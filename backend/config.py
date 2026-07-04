import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/data/vpn_panel.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-use-openssl-rand-hex-32")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# AmneziaWG defaults
DEFAULT_PORT = 51820
DEFAULT_DNS = "1.1.1.1, 8.8.8.8"
DEFAULT_ALLOWED_IPS = "0.0.0.0/0, ::/0"

# Server config keys
CONFIG_KEYS = {
    "listen_port": str(DEFAULT_PORT),
    "dns": DEFAULT_DNS,
    "jc": "0",
    "jmin": "0",
    "jmax": "0",
    "s1": "0",
    "s2": "0",
    "h1": "0",
    "h2": "0",
    "h3": "0",
    "h4": "0",
}
