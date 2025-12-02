from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.db.database import Base


class EventStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    ENDED = "ended"


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id_onchain = Column(BigInteger, unique=True, nullable=True)  # 스마트 컨트랙트의 eventId
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    ipfs_hash = Column(String(255), nullable=True)
    price_wei = Column(BigInteger, nullable=False)
    max_tickets = Column(Integer, nullable=False)
    sold_tickets = Column(Integer, default=0, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    event_date = Column(DateTime, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organizer = relationship("User", back_populates="events")
    tickets = relationship("Ticket", back_populates="event")
    transactions = relationship("Transaction", back_populates="event")

