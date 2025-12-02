from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.event import EventStatus


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_wei: int
    max_tickets: int
    start_time: datetime
    end_time: datetime
    event_date: datetime


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_wei: Optional[int] = None
    max_tickets: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_date: Optional[datetime] = None


class EventResponse(EventBase):
    id: str
    event_id_onchain: Optional[int] = None
    organizer_id: str
    ipfs_hash: Optional[str] = None
    sold_tickets: int
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

