import httpx
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, Set, Dict, List
import config

logger = logging.getLogger(__name__)

ROLE_BASED_ADDRESSES = {
    'admin', 'administrator', 'contact', 'info', 'support', 'sales', 
    'help', 'noreply', 'no-reply', 'postmaster', 'webmaster', 'hostmaster',
    'abuse', 'security', 'privacy', 'legal', 'billing', 'marketing'
}

COMMON_TYPOS = {
    'gmal.com': 'gmail.com',
    'gmial.com': 'gmail.com',
    'gmil.com': 'gmail.com',
    'yahooo.com': 'yahoo.com',
    'yaho.com': 'yahoo.com',
    'hotmial.com': 'hotmail.com',
    'hotmal.com': 'hotmail.com',
}


class EmailChecker:
    def __init__(self):
        self.disposable_domains: Set[str] = set()
        self.last_updated: datetime = None
        
    async def sync_disposable_list(self) -> bool:
        """Download and sync disposable email domain list."""
        try:
            logger.info("Syncing disposable email domain list...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(config.DISPOSABLE_EMAIL_LIST_URL)
                response.raise_for_status()
                
                domains = set()
                for line in response.text.strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        domains.add(line.lower())
                
                with open(config.DISPOSABLE_EMAIL_FILE, 'w') as f:
                    f.write('\n'.join(sorted(domains)))
                
                self.disposable_domains = domains
                self.last_updated = datetime.utcnow()
                logger.info(f"Synced {len(domains)} disposable email domains")
                return True
                
        except Exception as e:
            logger.error(f"Failed to sync disposable email list: {e}")
            self._load_from_cache()
            return False
    
    def _load_from_cache(self):
        """Load disposable domains from cached file."""
        if config.DISPOSABLE_EMAIL_FILE.exists():
            try:
                with open(config.DISPOSABLE_EMAIL_FILE, 'r') as f:
                    self.disposable_domains = {line.strip().lower() for line in f if line.strip()}
                logger.info(f"Loaded {len(self.disposable_domains)} domains from cache")
            except Exception as e:
                logger.error(f"Failed to load from cache: {e}")
    
    def check_email(self, email: str) -> Dict:
        """
        Check if email domain is disposable and analyze other attributes.
        Returns: dict with disposable status, reason, and additional flags
        """
        result = {
            'is_disposable': False,
            'reason': '',
            'is_role_based': False,
            'typo_suggestion': None,
            'risk_score': 0
        }
        
        if not email or '@' not in email:
            result['reason'] = "Invalid email format"
            return result
        
        try:
            local_part, domain = email.rsplit('@', 1)
            domain = domain.lower()
            local_part = local_part.lower()
            
            # Check for role-based address
            if local_part in ROLE_BASED_ADDRESSES:
                result['is_role_based'] = True
                result['risk_score'] += 20
            
            # Check for common typos
            if domain in COMMON_TYPOS:
                result['typo_suggestion'] = f"{local_part}@{COMMON_TYPOS[domain]}"
                result['risk_score'] += 10
            
            # Check if disposable
            if domain in self.disposable_domains:
                result['is_disposable'] = True
                result['reason'] = f"Domain '{domain}' is in disposable email list"
                result['risk_score'] += 70
                return result
            
            # Check parent domain for subdomains
            parts = domain.split('.')
            if len(parts) > 2:
                parent_domain = '.'.join(parts[-2:])
                if parent_domain in self.disposable_domains:
                    result['is_disposable'] = True
                    result['reason'] = f"Parent domain '{parent_domain}' is in disposable email list"
                    result['risk_score'] += 70
                    return result
            
            result['reason'] = f"Domain '{domain}' is not in disposable email list"
            return result
            
        except Exception as e:
            logger.error(f"Error checking email: {e}")
            result['reason'] = "Error checking email"
            return result


email_checker = EmailChecker()
