// 스마트 컨트랙트 주소 (배포 후 업데이트 필요)
export const CONTRACT_ADDRESSES = {
  TICKET_ACCESS_CONTROL: import.meta.env.VITE_TICKET_ACCESS_CONTROL_ADDRESS || "",
  TICKET_NFT: import.meta.env.VITE_TICKET_NFT_ADDRESS || "",
  EVENT_MANAGER: import.meta.env.VITE_EVENT_MANAGER_ADDRESS || "",
  MARKETPLACE: import.meta.env.VITE_MARKETPLACE_ADDRESS || "",
  REFUND_MANAGER: import.meta.env.VITE_REFUND_MANAGER_ADDRESS || "",
};

// API URL
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Polygon 네트워크
export const POLYGON_MUMBAI_RPC = "https://rpc-mumbai.maticvigil.com";
export const POLYGON_MAINNET_RPC = "https://polygon-rpc.com";

// Chain ID
export const POLYGON_MUMBAI_CHAIN_ID = 80001;
export const POLYGON_MAINNET_CHAIN_ID = 137;

