import os
from datetime import date, datetime

from sqlalchemy import create_engine, BigInteger, Text, Date, Float, DateTime, func, UniqueConstraint 
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


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)  # Keycloak sub
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)  # base64 data URL

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
    submitted_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

class LoginEvent(Base):
    __tablename__ = "login_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)              # "LOGIN" | "LOGIN_ERROR"
    user_id: Mapped[str | None] = mapped_column(Text, nullable=True)     # Keycloak sub
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    identity_provider: Mapped[str | None] = mapped_column(Text, nullable=True)  # Email/Google/…
    client_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)       # set on LOGIN_ERROR
    dedup_key: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (UniqueConstraint("dedup_key", name="uq_login_events_dedup"),)

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