import { useState, useEffect } from 'react';
import { getProvider, ensureSmartWallet, getNetworkInfo, getBalance } from '../services/web3';
import { useAuthStore } from '../store/authStore';

interface Web3State {
  isConnected: boolean;
  smartWalletAddress: string | null;
  balance: string | null;
  network: {
    chainId: number;
    name: string;
    blockNumber: number;
  } | null;
  loading: boolean;
  error: string | null;
}

export function useWeb3() {
  const { user, updateUser } = useAuthStore();
  const [state, setState] = useState<Web3State>({
    isConnected: false,
    smartWalletAddress: null,
    balance: null,
    network: null,
    loading: false, // 초기값을 false로 변경 (true면 무한 로딩)
    error: null,
  });

  // Smart Wallet 연결
  const connectWallet = async () => {
    try {
      console.log('[useWeb3] Starting wallet connection...');
      setState((prev) => ({ ...prev, loading: true, error: null }));

      // Provider 연결 확인
      console.log('[useWeb3] Checking provider connection...');
      const provider = getProvider();
      let isConnected = false;
      try {
        await Promise.race([
          provider.getNetwork(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))
        ]);
        isConnected = true;
        console.log('[useWeb3] Provider connected');
      } catch (error: any) {
        console.error('[useWeb3] Provider connection error:', error);
        throw new Error('Failed to connect to blockchain network. Please check if Hardhat node is running.');
      }
      
      if (!isConnected) {
        throw new Error('Failed to connect to blockchain network');
      }

      // Smart Wallet 주소 확인 및 생성
      console.log('[useWeb3] Creating smart wallet...');
      const smartWalletAddress = await ensureSmartWallet();
      console.log('[useWeb3] Smart wallet address:', smartWalletAddress);
      
      if (!smartWalletAddress) {
        throw new Error('Failed to get smart wallet address');
      }
      
      // 네트워크 정보 (에러가 발생해도 계속 진행)
      let network = null;
      let balance = '0.0';
      try {
        console.log('[useWeb3] Getting network info...');
        network = await Promise.race([
          getNetworkInfo(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))
        ]) as any;
        console.log('[useWeb3] Network info:', network);
      } catch (error) {
        console.warn('[useWeb3] Failed to get network info:', error);
      }
      
      // 잔액 조회 (에러가 발생해도 계속 진행)
      try {
        console.log('[useWeb3] Getting balance...');
        balance = await Promise.race([
          getBalance(smartWalletAddress),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))
        ]) as string;
        console.log('[useWeb3] Balance:', balance);
      } catch (error) {
        console.warn('[useWeb3] Failed to get balance:', error);
      }

      // 사용자 정보 업데이트
      console.log('[useWeb3] Updating user info...');
      updateUser({ smart_wallet_address: smartWalletAddress });

      console.log('[useWeb3] Wallet connection successful!');
      setState({
        isConnected: true,
        smartWalletAddress,
        balance,
        network,
        loading: false,
        error: null,
      });
    } catch (error: any) {
      console.error('[useWeb3] Wallet connection error:', error);
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error.message || 'Failed to connect wallet',
      }));
    }
  };

  // 초기 연결 (컴포넌트 마운트 시)
  useEffect(() => {
    console.log('[useWeb3] useEffect triggered', {
      hasUser: !!user,
      userEmail: user?.email,
      userId: user?.id,
      smartWalletAddress: state.smartWalletAddress,
      loading: state.loading,
    });
    
    // user가 있고, smartWalletAddress가 없고, 현재 로딩 중이 아닐 때만 실행
    if (user && !state.smartWalletAddress && !state.loading) {
      console.log('[useWeb3] Auto-connecting wallet for user:', user.email);
      // 약간의 지연을 두어 컴포넌트가 완전히 마운트된 후 실행
      const timer = setTimeout(() => {
        connectWallet();
      }, 500);
      return () => clearTimeout(timer);
    } else {
      const reason = !user 
        ? 'no user' 
        : state.smartWalletAddress 
          ? `has wallet: ${state.smartWalletAddress}` 
          : state.loading 
            ? 'loading' 
            : 'unknown';
      console.log('[useWeb3] Skipping auto-connect:', { reason });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, state.smartWalletAddress, state.loading]); // 의존성 명확히 지정

  // 주기적으로 잔액 업데이트
  useEffect(() => {
    if (!state.smartWalletAddress) return;

    const interval = setInterval(async () => {
      try {
        const balance = await getBalance(state.smartWalletAddress!);
        setState((prev) => ({ ...prev, balance }));
      } catch (error) {
        console.error('Failed to update balance:', error);
      }
    }, 10000); // 10초마다

    return () => clearInterval(interval);
  }, [state.smartWalletAddress]);

  return {
    ...state,
    connectWallet,
    refresh: connectWallet,
  };
}

