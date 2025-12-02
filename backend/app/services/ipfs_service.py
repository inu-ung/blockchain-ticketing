import requests
from app.core.config import settings
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class IPFSService:
    def __init__(self):
        self.api_key = settings.PINATA_API_KEY
        self.secret_key = settings.PINATA_SECRET_KEY
        self.base_url = "https://api.pinata.cloud"
        self.gateway_url = "https://gateway.pinata.cloud/ipfs"
        self.is_configured = bool(self.api_key and self.secret_key)
    
    def upload_json(self, data: dict, pinata_metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        JSON 데이터를 IPFS에 업로드
        
        Args:
            data: 업로드할 JSON 데이터
            pinata_metadata: Pinata 메타데이터 (name, keyvalues 등)
        
        Returns:
            IPFS 해시 (예: "Qm...") 또는 None
        """
        if not self.is_configured:
            logger.warning("Pinata API keys not configured. Using mock hash.")
            return "QmMockHash123456789"
        
        url = f"{self.base_url}/pinning/pinJSONToIPFS"
        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "pinataContent": data
        }
        
        if pinata_metadata:
            payload["pinataMetadata"] = pinata_metadata
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ipfs_hash = result.get("IpfsHash")
            
            if ipfs_hash:
                logger.info(f"Successfully uploaded JSON to IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                logger.error(f"IPFS upload succeeded but no hash returned: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"IPFS upload error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during IPFS upload: {e}")
            return None
    
    def upload_file(self, file_path: str, pinata_metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        파일을 IPFS에 업로드
        
        Args:
            file_path: 업로드할 파일 경로
            pinata_metadata: Pinata 메타데이터
        
        Returns:
            IPFS 해시 또는 None
        """
        if not self.is_configured:
            logger.warning("Pinata API keys not configured. Using mock hash.")
            return "QmMockHash123456789"
        
        url = f"{self.base_url}/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key
        }
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {}
                
                if pinata_metadata:
                    data['pinataMetadata'] = json.dumps(pinata_metadata)
                
                response = requests.post(url, files=files, headers=headers, data=data, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                ipfs_hash = result.get("IpfsHash")
                
                if ipfs_hash:
                    logger.info(f"Successfully uploaded file to IPFS: {ipfs_hash}")
                    return ipfs_hash
                else:
                    logger.error(f"IPFS upload succeeded but no hash returned: {result}")
                    return None
                    
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"IPFS file upload error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during IPFS file upload: {e}")
            return None
    
    def get_json(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        IPFS에서 JSON 데이터 조회
        
        Args:
            ipfs_hash: IPFS 해시 (ipfs:// 접두사 제거됨)
        
        Returns:
            JSON 데이터 또는 None
        """
        # ipfs:// 접두사 제거
        hash_clean = ipfs_hash.replace("ipfs://", "").strip()
        
        # 여러 IPFS 게이트웨이 시도
        gateways = [
            f"{self.gateway_url}/{hash_clean}",
            f"https://ipfs.io/ipfs/{hash_clean}",
            f"https://cloudflare-ipfs.com/ipfs/{hash_clean}",
        ]
        
        for gateway_url in gateways:
            try:
                response = requests.get(gateway_url, timeout=10)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully retrieved JSON from IPFS: {hash_clean}")
                return data
            except requests.exceptions.RequestException as e:
                logger.debug(f"Failed to fetch from {gateway_url}: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from IPFS: {e}")
                continue
        
        logger.error(f"Failed to retrieve JSON from IPFS: {hash_clean}")
        return None
    
    def get_file_url(self, ipfs_hash: str) -> str:
        """
        IPFS 파일 URL 생성
        
        Args:
            ipfs_hash: IPFS 해시
        
        Returns:
            IPFS 게이트웨이 URL
        """
        hash_clean = ipfs_hash.replace("ipfs://", "").strip()
        return f"{self.gateway_url}/{hash_clean}"
    
    def test_connection(self) -> bool:
        """
        Pinata 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        if not self.is_configured:
            logger.warning("Pinata API keys not configured")
            return False
        
        url = f"{self.base_url}/data/testAuthentication"
        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info("Pinata connection test successful")
            return True
        except Exception as e:
            logger.error(f"Pinata connection test failed: {e}")
            return False


ipfs_service = IPFSService()

