"""
App configuration.

Every setting here is read from an environment variable so the exact same
code can run locally, on Vercel, or anywhere else -- only the environment
variables change. See README.md, section "Working with the database" for
how to point this at SQLite, PostgreSQL, or MySQL.
"""
import os


def _normalize_db_url(url: str) -> str:
    """Some hosts (Heroku-style) hand out 'postgres://' which SQLAlchemy's
    modern driver name no longer accepts -- normalize it to 'postgresql://'."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = _normalize_db_url(
        os.environ.get("DATABASE_URL", "sqlite:///travelmate.db")
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
