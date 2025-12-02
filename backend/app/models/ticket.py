from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.db.database import Base


class TicketStatus(str, enum.Enum):
    ACTIVE = "active"
    REFUNDED = "refunded"
    TRANSFERRED = "transferred"
    CANCELLED = "cancelled"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_id = Column(BigInteger, unique=True, nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    owner_address = Column(String(42), nullable=False, index=True)
    ipfs_hash = Column(String(255), nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.ACTIVE, nullable=False)
    purchase_price_wei = Column(BigInteger, nullable=True)
    purchase_tx_hash = Column(String(66), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="tickets")
    resales = relationship("Resale", back_populates="ticket")
    transactions = relationship("Transaction", back_populates="ticket")
    refund_requests = relationship("RefundRequest", back_populates="ticket")

