# Email & IP Validation API

A high-performance REST API that checks if email addresses are disposable and if IP addresses are on public blacklists.

## Features

- ✅ **Email Validation**: Checks against 4700+ disposable email domains
- ✅ **IP Blacklist Check**: Validates IPs against 180K+ entries from 2 public blacklists
- ✅ **Risk Scoring**: Comprehensive 0-100 risk assessment with multiple factors
- ✅ **Role-Based Detection**: Identifies admin@, info@, contact@, etc.
- ✅ **Typo Suggestions**: Catches common domain typos (gmal.com → gmail.com)
- ✅ **Rate Limiting**: 60 req/min per IP with automatic 429 responses
- ✅ **Metrics & Observability**: P50/P95/P99 latency tracking, error rates
- ✅ **IPv4 & IPv6 Support**: Full validation for both address types
- ✅ **Auto-Sync**: Lists update automatically every 24 hours
- ✅ **Fast Response**: Optimized for <100ms per request
- ✅ **Bulk Processing**: Upload CSV/JSON files (max 10MB, 10K rows)
- ✅ **Privacy-First**: No storage or logging of emails/IPs after processing

## Data Sources

All data sources are publicly available and permit commercial use.

- **Disposable Emails**: [disposable-email-domains/disposable-email-domains](https://github.com/disposable-email-domains/disposable-email-domains)
  - Count: 4,700+ domains
  - License: CC0 1.0 Universal (Public Domain)
  - Commercial use: ✅ Permitted
  
- **IP Blacklists**:
  - **[IPsum](https://github.com/stamparm/ipsum)** - Malicious IPs, botnets, attackers
    - Count: 188,000+ IPs (primarily IPv4)
    - License: Unlicense (Public Domain)
    - Commercial use: ✅ Permitted
    - Direct URL: `https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt`
  
  - **[BruteForceBlocker](https://danger.rulez.sk/projects/bruteforceblocker/)** - SSH/FTP brute force attackers
    - Count: 265+ IPs (IPv4 only)
    - License: Public blocklist
    - Commercial use: ✅ Permitted
    - Direct URL: `https://danger.rulez.sk/projects/bruteforceblocker/blist.php`

**IPv6 Support**: The API validates both IPv4 and IPv6 addresses. However, most public blacklists focus on IPv4. IPv6 addresses will be validated for format but may have limited blacklist coverage.

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
cd validation-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the API

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Endpoints

| Endpoint | Method | Rate Limit | Description |
|----------|--------|------------|-------------|
| `/` | GET | None | Health check |
| `/status` | GET | None | List statistics & sync times |
| `/metrics` | GET | None | Performance metrics & observability |
| `/validate` | POST | 60/min | Single email & IP validation |
| `/bulk-validate` | POST | 10/min | Batch validation (max 10k rows) |
| `/sync` | POST | None | Manual list update trigger |
| `/docs` | GET | None | Interactive API documentation |

### 1. Health Check

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "ok",
  "service": "Email & IP Validation API",
  "version": "1.0.0"
}
```

### 2. Status & List Information

```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "status": "ok",
  "email_domains_count": 4727,
  "email_last_updated": "2024-01-15T10:30:00Z",
  "ip_blacklists": {
    "ipsum": 188454,
    "bruteforceblocker": 265
  },
  "ip_last_updated": {
    "ipsum": "2024-01-15T10:30:05Z",
    "bruteforceblocker": "2024-01-15T10:30:12Z"
  }
}
```

### 3. Metrics & Performance

```bash
curl http://localhost:8000/metrics
```

**Response:**
```json
{
  "uptime_seconds": 3600,
  "total_requests": 1250,
  "error_count": 5,
  "error_rate": 0.004,
  "requests_per_second": 0.347,
  "latency_ms": {
    "p50": 45.2,
    "p95": 87.3,
    "p99": 120.5
  },
  "data_sources": {
    "disposable_domains": 4727,
    "ip_blacklists": {
      "ipsum": 188454,
      "bruteforceblocker": 265
    }
  }
}
```

### 4. Validate Email & IP

**POST** `/validate` (Rate limit: 60 requests/minute)

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@tempmail.com",
    "ip": "192.0.2.1"
  }'
```

**Request Body:**
```json
{
  "email": "test@tempmail.com",
  "ip": "192.0.2.1"
}
```

**Response:**
```json
{
  "email_disposable": true,
  "email_reason": "Domain 'tempmail.com' is in disposable email list",
  "email_role_based": false,
  "email_typo_suggestion": null,
  "ip_blacklisted": true,
  "ip_blacklist_hits": 2,
  "ip_blacklist_sources": ["ipsum", "bruteforceblocker"],
  "risk_score": 90,
  "blacklist_last_updated": {
    "ipsum": "2024-01-15T10:30:05Z",
    "bruteforceblocker": "2024-01-15T10:30:12Z"
  }
}
```

**Risk Score Breakdown:**
- Disposable email: +70
- Role-based address (admin@, contact@, etc.): +20
- Domain typo detected: +10
- IP blacklisted: +10 to +30 (based on hit count)
- Maximum score: 100

**Example with Clean Email & IP:**
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmail.com",
    "ip": "8.8.8.8"
  }'
```

**Response:**
```json
{
  "email_disposable": false,
  "email_reason": "Domain 'gmail.com' is not in disposable email list",
  "email_role_based": false,
  "email_typo_suggestion": null,
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "risk_score": 0,
  "blacklist_last_updated": {
    "ipsum": "2024-01-15T10:30:05Z",
    "bruteforceblocker": "2024-01-15T10:30:12Z"
  }
}
```

**Example with Role-Based Address:**
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "ip": "1.1.1.1"
  }'
```

**Response:**
```json
{
  "email_disposable": false,
  "email_reason": "Domain 'example.com' is not in disposable email list",
  "email_role_based": true,
  "email_typo_suggestion": null,
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "risk_score": 20,
  "blacklist_last_updated": {...}
}
```

**Example with Typo Detection:**
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmal.com",
    "ip": "8.8.8.8"
  }'
```

**Response:**
```json
{
  "email_disposable": true,
  "email_reason": "Domain 'gmal.com' is in disposable email list",
  "email_role_based": false,
  "email_typo_suggestion": "user@gmail.com",
  "ip_blacklisted": false,
  "ip_blacklist_hits": 0,
  "ip_blacklist_sources": [],
  "risk_score": 80,
  "blacklist_last_updated": {...}
}
```

**Example with IPv6:**
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "ip": "2001:4860:4860::8888"
  }'
```

### 4. Bulk Validate (CSV)

**POST** `/bulk-validate`

Create a CSV file (`test.csv`):
```csv
email,ip
test@tempmail.com,192.0.2.1
user@gmail.com,8.8.8.8
admin@mailinator.com,1.2.3.4
```

Upload and validate:
```bash
curl -X POST http://localhost:8000/bulk-validate \
  -F "file=@test.csv" \
  -o results.csv
```

**Output (results.csv):**
```csv
email,ip,email_disposable,email_reason,ip_blacklisted,ip_blacklist_hits,ip_blacklist_sources
test@tempmail.com,192.0.2.1,true,Domain 'tempmail.com' is in disposable email list,true,2,ipsum;ipblocklist
user@gmail.com,8.8.8.8,false,Domain 'gmail.com' is not in disposable email list,false,0,
admin@mailinator.com,1.2.3.4,true,Domain 'mailinator.com' is in disposable email list,false,0,
```

### 5. Bulk Validate (JSON)

Create a JSON file (`test.json`):
```json
[
  {"email": "test@tempmail.com", "ip": "192.0.2.1"},
  {"email": "user@gmail.com", "ip": "8.8.8.8"},
  {"email": "admin@mailinator.com", "ip": "1.2.3.4"}
]
```

Upload and validate:
```bash
curl -X POST http://localhost:8000/bulk-validate \
  -F "file=@test.json" \
  -o results.csv
```

### 6. Manual Sync

Trigger an immediate update of all lists:
```bash
curl -X POST http://localhost:8000/sync
```

**Response:**
```json
{
  "status": "success",
  "message": "Lists synced successfully",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

## Error Handling

### Invalid Email Format
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-email", "ip": "8.8.8.8"}'
```

**Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

### Invalid IP Address
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "ip": "999.999.999.999"}'
```

**Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "ip"],
      "msg": "Invalid IP address format",
      "type": "value_error"
    }
  ]
}
```

## Configuration

Edit `config.py` to customize:

- **Sync Interval**: Change `SYNC_INTERVAL_HOURS` (default: 24)
- **Data Sources**: Modify `DISPOSABLE_EMAIL_LIST_URL` or `IP_BLACKLIST_SOURCES`
- **Data Directory**: Change `DATA_DIR` for list storage location

## How List Updates Work

1. **Initial Sync**: On startup, all lists are downloaded and cached locally
2. **Scheduled Updates**: APScheduler runs sync every 24 hours automatically
3. **Manual Sync**: Use `/sync` endpoint to trigger immediate update
4. **Fallback**: If sync fails, API uses cached lists from disk
5. **No Downtime**: Updates happen in background without interrupting requests

## Performance

- **Target Response Time**: <500ms per request
- **Optimization**: 
  - In-memory set lookups (O(1) complexity)
  - Async I/O for all network operations
  - No database queries during validation
  - Efficient caching mechanism

## Privacy & Security

- ✅ **No Data Retention**: Emails and IPs are not stored or logged
- ✅ **No External API Calls**: All checks are done against local cached lists
- ✅ **Open Source Lists**: Uses only public, transparent blocklists
- ✅ **No Tracking**: No analytics or monitoring of validated data

## Development

### Project Structure

```
validation-api/
├── main.py              # FastAPI application
├── email_checker.py     # Email validation logic
├── ip_checker.py        # IP blacklist checking
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── data/                # Cached lists (auto-generated)
    ├── disposable_domains.txt
    └── ip_blacklists/
        ├── ipsum.txt
        └── ipblocklist.txt
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run validation tests (example)
python -c "
import asyncio
from email_checker import email_checker
from ip_checker import ip_checker

async def test():
    await email_checker.sync_disposable_list()
    await ip_checker.sync_blacklists()
    
    print('Email check:', email_checker.check_email('test@tempmail.com'))
    print('IP check:', ip_checker.check_ip('192.0.2.1'))

asyncio.run(test())
"
```

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t validation-api .
docker run -p 8000:8000 validation-api
```

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Troubleshooting

### Lists Not Downloading

If initial sync fails (network issues, rate limiting):
1. Check logs for error messages
2. Try manual sync: `curl -X POST http://localhost:8000/sync`
3. Verify internet connectivity
4. Check if GitHub is accessible

### Slow Response Times

- Check list sizes in `/status` endpoint
- Consider using production server with workers
- Monitor system resources (CPU, RAM)
- Reduce sync frequency if needed

## License

MIT License - Feel free to use in your projects

## Contributing

Contributions welcome! To add more blacklist sources:
1. Add URL to `IP_BLACKLIST_SOURCES` in `config.py`
2. Ensure format is compatible (one IP per line)
3. Test sync and validation

## Support

For issues or questions, check:
- API logs for error details
- `/status` endpoint for list health
- GitHub issues for data source updates
