import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import apiClient from '../services/api';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Admin() {
  const { user } = useAuthStore();

  const { data: stats } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/stats');
      return response.data;
    },
  });

  const { data: pendingEvents } = useQuery({
    queryKey: ['admin', 'pending-events'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/events/pending');
      return response.data;
    },
  });

  if (user?.role !== 'admin') {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-red-600">관리자 권한이 필요합니다.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-2 text-gradient">관리자 페이지</h1>
        <p className="text-gray-600">시스템을 관리하고 이벤트를 승인하세요</p>
      </div>

      {/* 통계 */}
      {stats ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card p-6 bg-gradient-to-br from-blue-50 to-blue-100">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">전체 이벤트</h3>
            <p className="text-4xl font-bold text-blue-600">{stats.total_events}</p>
          </div>
          <div className="card p-6 bg-gradient-to-br from-green-50 to-green-100">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">전체 티켓</h3>
            <p className="text-4xl font-bold text-green-600">{stats.total_tickets}</p>
          </div>
          <div className="card p-6 bg-gradient-to-br from-purple-50 to-purple-100">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">전체 사용자</h3>
            <p className="text-4xl font-bold text-purple-600">{stats.total_users}</p>
          </div>
          <div className="card p-6 bg-gradient-to-br from-yellow-50 to-yellow-100">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">승인 대기</h3>
            <p className="text-4xl font-bold text-yellow-600">{stats.pending_events}</p>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {/* 승인 대기 이벤트 */}
      <div className="card p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">승인 대기 이벤트</h2>
        {pendingEvents && pendingEvents.length === 0 ? (
          <p className="text-gray-600">승인 대기 중인 이벤트가 없습니다.</p>
        ) : (
          <div className="space-y-4">
            {pendingEvents?.map((event: any) => (
              <div key={event.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="text-lg font-semibold mb-2">{event.name}</h3>
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">{event.description || '설명 없음'}</p>
                <button className="btn-primary">
                  승인하기
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
