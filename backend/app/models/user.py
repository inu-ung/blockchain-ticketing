from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    BUYER = "buyer"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # 비밀번호 해시
    wallet_address = Column(String(42), unique=False, nullable=True, index=True)  # unique 제거 (여러 사용자가 같은 지갑 사용 가능)
    smart_wallet_address = Column(String(42), nullable=True)  # Account Abstraction 지갑
    role = Column(Enum(UserRole), default=UserRole.BUYER, nullable=False)
    kyc_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    events = relationship("Event", back_populates="organizer")
    # tickets는 owner_address로만 연결되므로 relationship 제거
    transactions = relationship("Transaction", back_populates="user")
    refund_requests = relationship("RefundRequest", back_populates="user")

