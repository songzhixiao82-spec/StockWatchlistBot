from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

POSITIONS_PATH = DATA_DIR / "positions.csv"
WATCHLIST_PATH = DATA_DIR / "watchlist.csv"
ALERT_LOG_PATH = DATA_DIR / "alert_log.csv"

load_dotenv(BASE_DIR / ".env")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "harry219@126.com")
