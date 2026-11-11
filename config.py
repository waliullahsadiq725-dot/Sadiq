import os
from pathlib import Path

APP_NAME = "Nangarhar University Digital Library API"
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE-THIS-SECRET-KEY-BEFORE-DEPLOYMENT")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nudl.db")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
FRONTEND_ORIGINS = [
    item.strip() for item in os.getenv("FRONTEND_ORIGINS", "*").split(",") if item.strip()
]
