import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DISPOSABLE_EMAIL_LIST_URL = "https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/disposable_email_blocklist.conf"
DISPOSABLE_EMAIL_FILE = DATA_DIR / "disposable_domains.txt"

IP_BLACKLIST_SOURCES = {
    "ipsum": "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt",
    "bruteforceblocker": "https://danger.rulez.sk/projects/bruteforceblocker/blist.php"
}
IP_BLACKLIST_DIR = DATA_DIR / "ip_blacklists"
IP_BLACKLIST_DIR.mkdir(exist_ok=True)

SYNC_INTERVAL_HOURS = 24
MAX_RESPONSE_TIME_MS = 500
