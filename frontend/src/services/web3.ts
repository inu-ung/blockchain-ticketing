import { ethers } from 'ethers';
import apiClient from './api';

// 로컬 Hardhat 노드 또는 Polygon RPC
const RPC_URL = import.meta.env.VITE_RPC_URL || 'http://localhost:8545';

// Provider 인스턴스
let provider: ethers.JsonRpcProvider | null = null;
let browserProvider: ethers.BrowserProvider | null = null;
let userSigner: ethers.JsonRpcSigner | null = null;

/**
 * MetaMask Provider 가져오기
 */
export function getBrowserProvider(): ethers.BrowserProvider | null {
  if (typeof window !== 'undefined' && window.ethereum) {
    if (!browserProvider) {
      browserProvider = new ethers.BrowserProvider(window.ethereum);
    }
    return browserProvider;
  }
  return null;
}

/**
 * MetaMask 연결
 */
export async function connectMetaMask(): Promise<ethers.JsonRpcSigner> {
  const browserProvider = getBrowserProvider();
  if (!browserProvider) {
    throw new Error('MetaMask not installed. Please install MetaMask extension.');
  }
  
  // 계정 요청
  await browserProvider.send('eth_requestAccounts', []);
  
  // Signer 가져오기
  const signer = await browserProvider.getSigner();
  userSigner = signer;
  
  return signer;
}

/**
 * 연결된 MetaMask 주소 가져오기
 */
export async function getMetaMaskAddress(): Promise<string | null> {
  try {
    const browserProvider = getBrowserProvider();
    if (!browserProvider) return null;
    
    const signer = await browserProvider.getSigner();
    return await signer.getAddress();
  } catch (error) {
    console.error('Failed to get MetaMask address:', error);
    return null;
  }
}

/**
 * Smart Wallet에 이더 충전
 */
export async function chargeSmartWallet(
  smartWalletAddress: string,
  amount: bigint
): Promise<string> {
  const browserProvider = getBrowserProvider();
  if (!browserProvider) {
    throw new Error('MetaMask not installed');
  }
  
  const signer = await browserProvider.getSigner();
  
  // Smart Wallet 주소로 이더 전송
  const tx = await signer.sendTransaction({
    to: smartWalletAddress,
    value: amount
  });
  
  // 트랜잭션 완료 대기
  await tx.wait();
  
  return tx.hash;
}

/**
 * Web3 Provider 초기화 (RPC용)
 */
export function getProvider(): ethers.JsonRpcProvider {
  if (!provider) {
    provider = new ethers.JsonRpcProvider(RPC_URL);
  }
  return provider;
}

/**
 * Smart Wallet 주소 가져오기 (백엔드에서 생성)
 */
export async function getSmartWalletAddress(): Promise<string | null> {
  try {
    console.log('[web3] Getting smart wallet address from /auth/me...');
    const response = await apiClient.get('/auth/me', { timeout: 5000 });
    console.log('[web3] Response:', response.data);
    const address = response.data.smart_wallet_address || null;
    console.log('[web3] Smart wallet address:', address);
    return address;
  } catch (error: any) {
    console.error('[web3] Failed to get smart wallet address:', error);
    console.error('[web3] Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    });
    return null;
  }
}

/**
 * Smart Wallet 생성 요청 (백엔드)
 */
export async function createSmartWallet(): Promise<string> {
  try {
    console.log('[web3] Requesting smart wallet creation...');
    const response = await apiClient.post('/auth/wallet/create', {}, { timeout: 30000 });
    console.log('[web3] Smart wallet created:', response.data);
    const address = response.data.smart_wallet_address;
    if (!address) {
      throw new Error('Smart wallet address not returned from server');
    }
    return address;
  } catch (error: any) {
    console.error('[web3] Smart wallet creation error:', error);
    console.error('[web3] Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    });
    // 이미 생성된 경우 주소 반환
    if (error.response?.status === 400 || error.response?.status === 409) {
      console.log('[web3] Smart wallet already exists, fetching address...');
      const address = await getSmartWalletAddress();
      if (address) return address;
    }
    throw error;
  }
}

/**
 * Smart Wallet 주소 확인 및 생성
 */
export async function ensureSmartWallet(): Promise<string> {
  console.log('[web3] Ensuring smart wallet...');
  try {
    let address = await getSmartWalletAddress();
    console.log('[web3] Current smart wallet address:', address);
    
    if (!address) {
      console.log('[web3] No smart wallet found, creating new one...');
      // Smart Wallet 생성
      address = await createSmartWallet();
      console.log('[web3] New smart wallet address:', address);
    } else {
      console.log('[web3] Smart wallet already exists:', address);
    }
    
    if (!address) {
      throw new Error('Failed to get or create smart wallet address');
    }
    
    return address;
  } catch (error: any) {
    console.error('[web3] ensureSmartWallet error:', error);
    throw error;
  }
}

/**
 * 컨트랙트 인스턴스 생성
 */
export function getContract(address: string, abi: any[]): ethers.Contract {
  const provider = getProvider();
  return new ethers.Contract(address, abi, provider);
}

/**
 * 블록체인 네트워크 정보 가져오기
 */
export async function getNetworkInfo() {
  try {
    const provider = getProvider();
    const network = await provider.getNetwork();
    let blockNumber = 0;
    try {
      blockNumber = await provider.getBlockNumber();
    } catch (error) {
      console.warn('Failed to get block number:', error);
    }
    
    // 네트워크 이름이 없거나 "unknown"인 경우 chainId로 판단
    let networkName = network.name;
    if (!networkName || networkName === 'unknown') {
      const chainId = Number(network.chainId);
      if (chainId === 31337 || chainId === 1337) {
        networkName = 'Hardhat Local';
      } else if (chainId === 80001) {
        networkName = 'Polygon Mumbai';
      } else if (chainId === 137) {
        networkName = 'Polygon Mainnet';
      } else {
        networkName = `Chain ${chainId}`;
      }
    }
    
    return {
      chainId: Number(network.chainId),
      name: networkName,
      blockNumber,
    };
  } catch (error) {
    console.error('Failed to get network info:', error);
    // 기본값 반환
    return {
      chainId: 31337, // Hardhat 기본 chainId
      name: 'Hardhat Local',
      blockNumber: 0,
    };
  }
}

/**
 * 잔액 조회
 */
export async function getBalance(address: string): Promise<string> {
  try {
    const provider = getProvider();
    const balance = await provider.getBalance(address);
    return ethers.formatEther(balance);
  } catch (error) {
    console.error('Failed to get balance:', error);
    return '0.0'; // 기본값 반환
  }
}

