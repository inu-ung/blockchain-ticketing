from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.resale import ResaleStatus


class ResaleCreate(BaseModel):
    ticket_id: str
    price_wei: int


class ResaleResponse(BaseModel):
    id: str
    ticket_id: str
    token_id: int
    seller_address: str
    price_wei: int
    status: ResaleStatus
    created_at: datetime
    sold_at: Optional[datetime] = None
    sale_tx_hash: Optional[str] = None

    class Config:
        from_attributes = True

