from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.ticket import TicketStatus


class TicketResponse(BaseModel):
    id: str
    token_id: int
    event_id: str
    owner_address: str
    ipfs_hash: Optional[str] = None
    status: TicketStatus
    purchase_price_wei: Optional[int] = None
    purchase_tx_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketPurchase(BaseModel):
    event_id: str
    token_uri: Optional[str] = None

