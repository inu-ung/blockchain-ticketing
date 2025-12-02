import { useState } from 'react';
import { ethers } from 'ethers';
import { connectMetaMask, chargeSmartWallet, getMetaMaskAddress, getBalance } from '../services/web3';
import { getSmartWalletAddress } from '../services/web3';
import { useToastStore } from '../components/ToastContainer';

interface PaymentState {
  isMetaMaskConnected: boolean;
  metaMaskAddress: string | null;
  smartWalletAddress: string | null;
  smartWalletBalance: string;
  loading: boolean;
  error: string | null;
}

export function usePayment() {
  const [state, setState] = useState<PaymentState>({
    isMetaMaskConnected: false,
    metaMaskAddress: null,
    smartWalletAddress: null,
    smartWalletBalance: '0',
    loading: false,
    error: null,
  });
  const addToast = useToastStore((state) => state.addToast);

  // MetaMask 연결
  const connectWallet = async () => {
    try {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      
      const signer = await connectMetaMask();
      const address = await signer.getAddress();
      
      // Smart Wallet 주소 가져오기
      const smartWalletAddress = await getSmartWalletAddress();
      
      // Smart Wallet 잔액 확인
      let balance = '0';
      if (smartWalletAddress) {
        balance = await getBalance(smartWalletAddress);
      }
      
      setState({
        isMetaMaskConnected: true,
        metaMaskAddress: address,
        smartWalletAddress,
        smartWalletBalance: balance,
        loading: false,
        error: null,
      });
      
      addToast('MetaMask 연결 완료', 'success');
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error.message || 'MetaMask 연결 실패',
      }));
      addToast(error.message || 'MetaMask 연결 실패', 'error');
      throw error;
    }
  };

  // Smart Wallet에 자금 충전
  const chargeWallet = async (amount: bigint) => {
    try {
      if (!state.smartWalletAddress) {
        throw new Error('Smart Wallet 주소가 없습니다.');
      }
      
      if (!state.isMetaMaskConnected) {
        await connectWallet();
      }
      
      setState((prev) => ({ ...prev, loading: true }));
      
      const txHash = await chargeSmartWallet(state.smartWalletAddress, amount);
      
      // 잔액 업데이트
      const balance = await getBalance(state.smartWalletAddress);
      
      setState((prev) => ({
        ...prev,
        smartWalletBalance: balance,
        loading: false,
      }));
      
      addToast('자금 충전 완료', 'success');
      return txHash;
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error.message || '자금 충전 실패',
      }));
      addToast(error.message || '자금 충전 실패', 'error');
      throw error;
    }
  };

  // 잔액 확인 및 업데이트
  const checkBalance = async () => {
    try {
      if (!state.smartWalletAddress) {
        const smartWalletAddress = await getSmartWalletAddress();
        if (!smartWalletAddress) return;
        
        setState((prev) => ({ ...prev, smartWalletAddress }));
      }
      
      const balance = await getBalance(state.smartWalletAddress!);
      setState((prev) => ({ ...prev, smartWalletBalance: balance }));
      
      return balance;
    } catch (error: any) {
      console.error('Failed to check balance:', error);
      return '0';
    }
  };

  return {
    ...state,
    connectWallet,
    chargeWallet,
    checkBalance,
  };
}

