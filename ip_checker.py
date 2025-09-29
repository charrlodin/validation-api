import httpx
import logging
import ipaddress
from datetime import datetime
from typing import Tuple, List, Dict, Set
import config

logger = logging.getLogger(__name__)


class IPChecker:
    def __init__(self):
        self.blacklists: Dict[str, Set[str]] = {}
        self.last_updated: Dict[str, datetime] = {}
        
    async def sync_blacklists(self) -> bool:
        """Download and sync all IP blacklists."""
        success = True
        for source_name, url in config.IP_BLACKLIST_SOURCES.items():
            try:
                logger.info(f"Syncing IP blacklist from {source_name}...")
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    ips = set()
                    for line in response.text.strip().split('\n'):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        parts = line.split()
                        ip_candidate = parts[0] if parts else line
                        
                        try:
                            ipaddress.ip_address(ip_candidate)
                            ips.add(ip_candidate)
                        except ValueError:
                            continue
                    
                    file_path = config.IP_BLACKLIST_DIR / f"{source_name}.txt"
                    with open(file_path, 'w') as f:
                        f.write('\n'.join(sorted(ips)))
                    
                    self.blacklists[source_name] = ips
                    self.last_updated[source_name] = datetime.utcnow()
                    logger.info(f"Synced {len(ips)} IPs from {source_name}")
                    
            except Exception as e:
                logger.error(f"Failed to sync {source_name}: {e}")
                self._load_from_cache(source_name)
                success = False
        
        return success
    
    def _load_from_cache(self, source_name: str):
        """Load IP blacklist from cached file."""
        file_path = config.IP_BLACKLIST_DIR / f"{source_name}.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    self.blacklists[source_name] = {line.strip() for line in f if line.strip()}
                logger.info(f"Loaded {len(self.blacklists[source_name])} IPs from {source_name} cache")
            except Exception as e:
                logger.error(f"Failed to load {source_name} from cache: {e}")
    
    def check_ip(self, ip_str: str) -> Tuple[bool, int, List[str]]:
        """
        Check if IP is in any blacklist.
        Returns: (is_blacklisted, hit_count, sources)
        """
        try:
            ip = ipaddress.ip_address(ip_str)
            ip_normalized = str(ip)
            
            hits = []
            for source_name, blacklist in self.blacklists.items():
                if ip_normalized in blacklist:
                    hits.append(source_name)
            
            is_blacklisted = len(hits) > 0
            return is_blacklisted, len(hits), hits
            
        except ValueError:
            logger.error(f"Invalid IP address: {ip_str}")
            return False, 0, []
        except Exception as e:
            logger.error(f"Error checking IP: {e}")
            return False, 0, []
    
    def get_last_updated(self) -> Dict[str, str]:
        """Get last updated timestamps for all sources."""
        return {
            source: timestamp.isoformat() + 'Z' if timestamp else None
            for source, timestamp in self.last_updated.items()
        }


ip_checker = IPChecker()
