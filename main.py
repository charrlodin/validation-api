import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
import csv
import io
from collections import defaultdict
import time

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from email_checker import email_checker
from ip_checker import ip_checker
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

class Metrics:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.latencies = []
        self.start_time = datetime.utcnow()
        
    def record_request(self, latency_ms: float, is_error: bool = False):
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies = self.latencies[-1000:]
    
    def get_stats(self):
        if not self.latencies:
            return {}
        sorted_latencies = sorted(self.latencies)
        return {
            'p50': sorted_latencies[len(sorted_latencies) // 2],
            'p95': sorted_latencies[int(len(sorted_latencies) * 0.95)],
            'p99': sorted_latencies[int(len(sorted_latencies) * 0.99)],
        }

metrics = Metrics()


class ValidationRequest(BaseModel):
    email: str = Field(..., description="Email address to validate")
    ip: str = Field(..., description="IPv4 or IPv6 address to validate")
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        return v.strip().lower()
    
    @validator('ip')
    def validate_ip(cls, v):
        import ipaddress
        try:
            ipaddress.ip_address(v.strip())
            return v.strip()
        except ValueError:
            raise ValueError('Invalid IP address format')


class ValidationResponse(BaseModel):
    email_disposable: bool
    email_reason: str
    email_role_based: bool = False
    email_typo_suggestion: Optional[str] = None
    ip_blacklisted: bool
    ip_blacklist_hits: int
    ip_blacklist_sources: List[str]
    risk_score: int = Field(..., description="Overall risk score (0-100)")
    blacklist_last_updated: Optional[dict] = None


class BulkValidationItem(BaseModel):
    email: str
    ip: str


class BulkValidationRequest(BaseModel):
    items: List[BulkValidationItem]


async def sync_all_lists():
    """Sync all email and IP lists."""
    logger.info("Starting scheduled sync of all lists...")
    try:
        await email_checker.sync_disposable_list()
        await ip_checker.sync_blacklists()
        logger.info("Scheduled sync completed successfully")
    except Exception as e:
        logger.error(f"Error during scheduled sync: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting validation API...")
    
    await sync_all_lists()
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        sync_all_lists,
        'interval',
        hours=config.SYNC_INTERVAL_HOURS,
        id='sync_lists'
    )
    scheduler.start()
    logger.info(f"Scheduled sync every {config.SYNC_INTERVAL_HOURS} hours")
    
    yield
    
    scheduler.shutdown()
    logger.info("Shutting down validation API...")


app = FastAPI(
    title="Email & IP Validation API",
    description="API to check if emails are disposable and IPs are blacklisted",
    version="1.0.0",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Email & IP Validation API",
        "version": "1.0.0"
    }


@app.get("/status")
async def status():
    """Get API status and list update information."""
    return {
        "status": "ok",
        "email_domains_count": len(email_checker.disposable_domains),
        "email_last_updated": email_checker.last_updated.isoformat() + 'Z' if email_checker.last_updated else None,
        "ip_blacklists": {
            source: len(ips) for source, ips in ip_checker.blacklists.items()
        },
        "ip_last_updated": ip_checker.get_last_updated()
    }


@app.get("/metrics")
async def get_metrics():
    """
    Get API metrics and performance statistics.
    
    Returns request counts, error rates, and latency percentiles.
    """
    uptime = (datetime.utcnow() - metrics.start_time).total_seconds()
    latency_stats = metrics.get_stats()
    
    return {
        "uptime_seconds": uptime,
        "total_requests": metrics.request_count,
        "error_count": metrics.error_count,
        "error_rate": metrics.error_count / metrics.request_count if metrics.request_count > 0 else 0,
        "requests_per_second": metrics.request_count / uptime if uptime > 0 else 0,
        "latency_ms": latency_stats,
        "data_sources": {
            "disposable_domains": len(email_checker.disposable_domains),
            "ip_blacklists": {
                source: len(ips) for source, ips in ip_checker.blacklists.items()
            }
        }
    }


@app.post("/validate", response_model=ValidationResponse)
@limiter.limit("60/minute")
async def validate(request: Request, validation_request: ValidationRequest):
    """
    Validate an email and IP address.
    
    Checks if the email domain is disposable and if the IP is on any public blacklists.
    Rate limit: 60 requests per minute per IP.
    """
    start_time = time.time()
    is_error = False
    
    try:
        email_result = email_checker.check_email(validation_request.email)
        
        is_blacklisted, hit_count, sources = ip_checker.check_ip(validation_request.ip)
        
        risk_score = email_result['risk_score']
        if is_blacklisted:
            risk_score += min(30, hit_count * 10)
        risk_score = min(100, risk_score)
        
        response = ValidationResponse(
            email_disposable=email_result['is_disposable'],
            email_reason=email_result['reason'],
            email_role_based=email_result['is_role_based'],
            email_typo_suggestion=email_result['typo_suggestion'],
            ip_blacklisted=is_blacklisted,
            ip_blacklist_hits=hit_count,
            ip_blacklist_sources=sources,
            risk_score=risk_score,
            blacklist_last_updated=ip_checker.get_last_updated()
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        logger.info(f"Validation completed in {elapsed_ms:.2f}ms, risk_score={risk_score}")
        
        return response
        
    except Exception as e:
        is_error = True
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@app.post("/bulk-validate")
@limiter.limit("10/minute")
async def bulk_validate(request: Request, file: UploadFile = File(...)):
    """
    Bulk validate emails and IPs from CSV or JSON file.
    
    CSV format: email,ip
    JSON format: [{"email": "...", "ip": "..."}, ...]
    
    Returns a CSV file with results.
    Maximum file size: 10MB, maximum 10,000 rows recommended.
    Rate limit: 10 requests per minute per IP.
    """
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
        
        content_str = content.decode('utf-8')
        
        results = []
        
        if file.filename.endswith('.json'):
            import json
            data = json.loads(content_str)
            if len(data) > 10000:
                raise HTTPException(status_code=413, detail="Too many items. Maximum 10,000 rows per file.")
            
            for item in data:
                email = item.get('email', '').strip().lower()
                ip = item.get('ip', '').strip()
                
                email_result = email_checker.check_email(email)
                is_blacklisted, hit_count, sources = ip_checker.check_ip(ip)
                
                risk_score = email_result['risk_score']
                if is_blacklisted:
                    risk_score += min(30, hit_count * 10)
                risk_score = min(100, risk_score)
                
                results.append({
                    'email': email,
                    'ip': ip,
                    'email_disposable': email_result['is_disposable'],
                    'email_reason': email_result['reason'],
                    'email_role_based': email_result['is_role_based'],
                    'email_typo_suggestion': email_result['typo_suggestion'] or '',
                    'ip_blacklisted': is_blacklisted,
                    'ip_blacklist_hits': hit_count,
                    'ip_blacklist_sources': ';'.join(sources),
                    'risk_score': risk_score
                })
        
        elif file.filename.endswith('.csv'):
            csv_reader = csv.DictReader(io.StringIO(content_str))
            rows = list(csv_reader)
            if len(rows) > 10000:
                raise HTTPException(status_code=413, detail="Too many rows. Maximum 10,000 rows per file.")
            
            for row in rows:
                email = row.get('email', '').strip().lower()
                ip = row.get('ip', '').strip()
                
                email_result = email_checker.check_email(email)
                is_blacklisted, hit_count, sources = ip_checker.check_ip(ip)
                
                risk_score = email_result['risk_score']
                if is_blacklisted:
                    risk_score += min(30, hit_count * 10)
                risk_score = min(100, risk_score)
                
                results.append({
                    'email': email,
                    'ip': ip,
                    'email_disposable': email_result['is_disposable'],
                    'email_reason': email_result['reason'],
                    'email_role_based': email_result['is_role_based'],
                    'email_typo_suggestion': email_result['typo_suggestion'] or '',
                    'ip_blacklisted': is_blacklisted,
                    'ip_blacklist_hits': hit_count,
                    'ip_blacklist_sources': ';'.join(sources),
                    'risk_score': risk_score
                })
        else:
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
        
        output = io.StringIO()
        if results:
            writer = csv.DictWriter(output, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=validation_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Bulk validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk validation error: {str(e)}")


@app.post("/sync")
async def manual_sync():
    """Manually trigger a sync of all lists."""
    try:
        await sync_all_lists()
        return {
            "status": "success",
            "message": "Lists synced successfully",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        logger.error(f"Manual sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")
