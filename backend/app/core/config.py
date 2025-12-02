from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ticketing"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Polygon
    POLYGON_MUMBAI_RPC_URL: str = "https://rpc-mumbai.maticvigil.com"
    POLYGON_MAINNET_RPC_URL: str = "https://polygon-rpc.com"
    PRIVATE_KEY: str = ""

    # Contract Addresses
    TICKET_ACCESS_CONTROL_ADDRESS: str = ""
    TICKET_NFT_ADDRESS: str = ""
    EVENT_MANAGER_ADDRESS: str = ""
    MARKETPLACE_ADDRESS: str = ""
    REFUND_MANAGER_ADDRESS: str = ""

    # IPFS (Pinata)
    PINATA_API_KEY: str = ""
    PINATA_SECRET_KEY: str = ""

    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Account Abstraction
    BUNDLER_URL: str = ""
    PAYMASTER_URL: str = ""
    SMART_WALLET_FACTORY_ADDRESS: str = ""
    ENTRY_POINT_ADDRESS: str = "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

