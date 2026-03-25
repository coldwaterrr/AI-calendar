import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = BACKEND_DIR / 'ai_calendar.db'
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
DATABASE_URL = os.getenv('DATABASE_URL', DEFAULT_DATABASE_URL)


def get_database_url() -> str:
    return os.getenv('DATABASE_URL', DEFAULT_DATABASE_URL)


def is_sqlite(url: str) -> bool:
    return url.startswith('sqlite')


connect_args = {'check_same_thread': False} if is_sqlite(DATABASE_URL) else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
