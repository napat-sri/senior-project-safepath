import os
from datetime import date, datetime

from sqlalchemy import create_engine, BigInteger, Text, Date, Float, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column

# Reads from .env (loaded by the backend). Host is the compose service name
# "postgres"; the DB is the new "safepath" database created in Part A2.
DATABASE_URL = os.getenv(
    "SAFEPATH_DATABASE_URL",
    "postgresql+psycopg://langflow:langflow@postgres:5432/safepath",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reporter_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    incident_type: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    incident_date: Mapped[date] = mapped_column(Date, nullable=False)
    incident_time: Mapped[str] = mapped_column(Text, nullable=False)   # "HH:MM"
    details: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # list of filenames
    submitted_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


def init_db() -> None:
    """Create tables if they don't exist (runs on backend startup)."""
    Base.metadata.create_all(engine)


def get_db():
    """FastAPI dependency: one session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()