from fastapi import APIRouter
from app.api.v1 import auth, events, tickets, resales, refunds, admin, ipfs, user_operations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(resales.router, prefix="/resales", tags=["resales"])
api_router.include_router(refunds.router, prefix="/refunds", tags=["refunds"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ipfs.router, prefix="/ipfs", tags=["ipfs"])
api_router.include_router(user_operations.router, prefix="/user-operations", tags=["user-operations"])

