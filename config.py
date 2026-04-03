"""
ShopHub Configuration
"""
import os
from datetime import timedelta

class Config:
    # ── Core ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "shophub-secret-change-in-production")
    DEBUG = os.environ.get("DEBUG", "True") == "True"

    # ── Database (SQLite for dev, swap URI for Postgres/MySQL) ──
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'shophub.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT ───────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-in-prod")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # ── File uploads ──────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5 MB

    # ── Emotion engine ────────────────────────────────────
    EMOTION_CONFIDENCE_THRESHOLD = 0.40     # min confidence to act on emotion
    EMOTION_RECOMMENDATION_LIMIT = 8        # products per emotion response

    # ── Pagination ────────────────────────────────────────
    PRODUCTS_PER_PAGE = 12
