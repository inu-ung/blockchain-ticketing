from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.db.database import Base


class ResaleStatus(str, enum.Enum):
    LISTED = "listed"
    SOLD = "sold"
    CANCELLED = "cancelled"


class Resale(Base):
    __tablename__ = "resales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    token_id = Column(BigInteger, nullable=False, index=True)
    seller_address = Column(String(42), nullable=False, index=True)
    price_wei = Column(BigInteger, nullable=False)
    status = Column(Enum(ResaleStatus), default=ResaleStatus.LISTED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sold_at = Column(DateTime, nullable=True)
    sale_tx_hash = Column(String(66), nullable=True)

    # Relationships
    ticket = relationship("Ticket", back_populates="resales")

