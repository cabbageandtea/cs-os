import os
import logging
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "cs_os.db"
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

# Connection pooling configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite: use NullPool (no connection pooling for SQLite)
    connect_args = {"check_same_thread": False}
    poolclass = NullPool
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        poolclass=poolclass,
        echo=False,
    )
else:
    # PostgreSQL/MySQL: use QueuePool for connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,  # Number of connections to keep in pool
        max_overflow=10,  # Overflow connections beyond pool_size
        pool_pre_ping=True,  # Test connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Get database session with proper error handling and cleanup."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.exception("Database error: %s", e)
        db.rollback()
        raise
    finally:
        db.close()
