from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.refund import RefundStatus


class RefundRequestCreate(BaseModel):
    ticket_id: str
    reason: Optional[str] = None


class RefundRequestResponse(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    reason: Optional[str] = None
    status: RefundStatus
    refund_amount_wei: Optional[int] = None
    refund_tx_hash: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

