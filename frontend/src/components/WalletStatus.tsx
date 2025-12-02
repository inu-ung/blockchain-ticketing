import { useWeb3 } from '../hooks/useWeb3';
import { useAuthStore } from '../store/authStore';

export default function WalletStatus() {
  const { user } = useAuthStore();
  const { isConnected, smartWalletAddress, balance, network, loading, error, connectWallet } = useWeb3();

  console.log('[WalletStatus] Render:', {
    hasUser: !!user,
    userEmail: user?.email,
    smartWalletAddress,
    loading,
    error,
  });

  if (!user) {
    console.log('[WalletStatus] No user, returning null');
    return null;
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <span>지갑 연결 중...</span>
        <button
          onClick={() => {
            console.log('취소 버튼 클릭 - 상태 초기화');
            // 로딩 상태를 강제로 해제할 수 없으므로, 에러로 처리
          }}
          className="ml-2 text-xs text-gray-500 hover:text-gray-700"
        >
          취소
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2">
        <div className="text-sm text-red-600">{error}</div>
        <button
          onClick={connectWallet}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          재시도
        </button>
      </div>
    );
  }

  if (!isConnected || !smartWalletAddress) {
    return (
      <button
        onClick={connectWallet}
        className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
      >
        지갑 연결
      </button>
    );
  }

  return (
    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span className="text-gray-700">연결됨</span>
      </div>
      
      <div className="flex flex-col">
        <div className="text-xs text-gray-500">Smart Wallet</div>
        <div className="font-mono text-xs text-gray-800">
          {smartWalletAddress.slice(0, 6)}...{smartWalletAddress.slice(-4)}
        </div>
      </div>
      
      {balance && (
        <div className="flex flex-col">
          <div className="text-xs text-gray-500">잔액</div>
          <div className="font-semibold text-gray-800">
            {parseFloat(balance).toFixed(4)} ETH
          </div>
        </div>
      )}
      
      {network && (
        <div className="flex flex-col">
          <div className="text-xs text-gray-500">네트워크</div>
          <div className="text-gray-800">{network.name}</div>
        </div>
      )}
    </div>
  );
}

