from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_admin
from app.services.ipfs_service import ipfs_service
from typing import Dict, Any

router = APIRouter()


@router.get("/test")
async def test_ipfs_connection():
    """IPFS 연결 테스트 (Pinata)"""
    is_connected = ipfs_service.test_connection()
    
    if not is_connected:
        return {
            "status": "error",
            "message": "IPFS connection failed. Please check your Pinata API keys.",
            "configured": ipfs_service.is_configured
        }
    
    return {
        "status": "success",
        "message": "IPFS connection successful",
        "configured": True
    }


@router.post("/upload")
async def upload_test_data(
    data: Dict[str, Any],
    current_user = Depends(get_current_admin)
):
    """테스트용 JSON 데이터 업로드"""
    ipfs_hash = ipfs_service.upload_json(data)
    
    if not ipfs_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload to IPFS"
        )
    
    return {
        "ipfs_hash": ipfs_hash,
        "token_uri": f"ipfs://{ipfs_hash}",
        "ipfs_url": ipfs_service.get_file_url(ipfs_hash)
    }


@router.get("/retrieve/{ipfs_hash}")
async def retrieve_ipfs_data(ipfs_hash: str):
    """IPFS에서 데이터 조회"""
    data = ipfs_service.get_json(ipfs_hash)
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data not found on IPFS"
        )
    
    return {
        "ipfs_hash": ipfs_hash,
        "data": data,
        "ipfs_url": ipfs_service.get_file_url(ipfs_hash)
    }

