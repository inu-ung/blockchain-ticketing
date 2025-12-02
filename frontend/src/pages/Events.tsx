import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useEvents } from '../hooks/useEvents';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Events() {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { data: events, isLoading, error } = useEvents(statusFilter || undefined);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
  };

  const formatPrice = (priceWei: number) => {
    return (priceWei / 1e18).toFixed(0) + ' USDC';
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="text-center py-20">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">이벤트를 불러오는 중...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    console.error('[Events] Error loading events:', error);
    const errorMessage = (error as any)?.response?.data?.detail || (error as any)?.message || '알 수 없는 오류';
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="text-5xl mb-4">😕</div>
          <p className="text-red-600 text-lg mb-2">이벤트를 불러오는 중 오류가 발생했습니다.</p>
          <p className="text-gray-500 text-sm">{errorMessage}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            새로고침
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-10 animate-fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 text-gray-800">티켓 구입</h1>
        </div>
        
        <div className="flex flex-wrap gap-3 mb-8">
          <button
            onClick={() => setStatusFilter('')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              statusFilter === ''
                ? 'bg-gray-800 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            전체
          </button>
          <button
            onClick={() => setStatusFilter('approved')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              statusFilter === 'approved'
                ? 'bg-gray-800 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            승인됨
          </button>
          <button
            onClick={() => setStatusFilter('active')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              statusFilter === 'active'
                ? 'bg-gray-800 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            판매 중
          </button>
        </div>
      </div>

      {events && events.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl shadow">
          <div className="text-6xl mb-4">🎭</div>
          <p className="text-xl text-gray-600 mb-2">등록된 이벤트가 없습니다</p>
          <p className="text-gray-500">첫 번째 이벤트를 만들어보세요!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {events?.map((event: any, index: number) => (
            <Link
              key={event.id}
              to={`/events/${event.id}`}
              className="card-pink block animate-slide-up hover:shadow-md transition-shadow"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h2 className="text-lg font-bold mb-1 text-gray-800">
                    {event.name}
                  </h2>
                  <p className="text-sm text-gray-600 mb-2">
                    {formatDate(event.event_date)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-800 mb-1">
                    {formatPrice(event.price_wei)} / 1매
                  </p>
                  <p className="text-xs text-gray-500">1인 2매 제한</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
