import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useToastStore } from '../components/ToastContainer';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Marketplace() {
  const { isAuthenticated } = useAuthStore();
  const queryClient = useQueryClient();
  const addToast = useToastStore((state) => state.addToast);

  const { data: resales, isLoading } = useQuery({
    queryKey: ['resales'],
    queryFn: async () => {
      const response = await apiClient.get('/resales');
      return response.data;
    },
  });

  const buyMutation = useMutation({
    mutationFn: async (resaleId: string) => {
      const response = await apiClient.post(`/resales/${resaleId}/buy`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resales'] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      addToast('티켓 구매가 완료되었습니다!', 'success');
    },
    onError: (error: any) => {
      addToast(error.response?.data?.detail || '구매에 실패했습니다.', 'error');
    },
  });

  const formatPrice = (priceWei: number) => {
    return (priceWei / 1e18).toFixed(4) + ' MATIC';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR');
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="text-center py-20">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-2 text-gradient">재판매 마켓플레이스</h1>
        <p className="text-gray-600">2차 시장에서 티켓을 구매하거나 판매하세요</p>
      </div>

      {resales && resales.length === 0 ? (
        <div className="text-center py-20 card">
          <div className="text-6xl mb-4">🛒</div>
          <p className="text-xl text-gray-600 mb-2">등록된 재판매 티켓이 없습니다</p>
          <p className="text-gray-500">티켓을 등록하면 여기에 표시됩니다</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resales?.map((resale: any, index: number) => (
            <div
              key={resale.id}
              className="card p-6 animate-slide-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="mb-6">
                <div className="w-full h-32 bg-gradient-to-br from-green-400 to-blue-500 rounded-lg mb-4 flex items-center justify-center">
                  <span className="text-5xl">🎫</span>
                </div>
                <div className="text-center">
                  <span className="text-sm font-medium text-gray-500">Token ID</span>
                  <p className="text-2xl font-bold text-gray-800">#{resale.token_id}</p>
                </div>
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                  <span className="text-sm text-gray-600">가격</span>
                  <span className="font-bold text-xl text-blue-600">
                    {formatPrice(resale.price_wei)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">등록일</span>
                  <span className="text-sm font-medium">{formatDate(resale.created_at)}</span>
                </div>
              </div>

              {isAuthenticated ? (
                <button
                  onClick={() => buyMutation.mutate(resale.id)}
                  disabled={buyMutation.isPending}
                  className="btn-primary w-full"
                >
                  {buyMutation.isPending ? (
                    <span className="flex items-center justify-center gap-2">
                      <LoadingSpinner size="sm" />
                      구매 중...
                    </span>
                  ) : (
                    '구매하기'
                  )}
                </button>
              ) : (
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">로그인 후 구매 가능합니다</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
