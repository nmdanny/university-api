from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

assert isinstance(settings.SQLALCHEMY_DATABASE_URI, str) and str
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, future=True, echo=settings.ECHO_SQL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
