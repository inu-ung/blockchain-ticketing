import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import apiClient from '../services/api';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import { Link } from 'react-router-dom';
import { useRequestRefund } from '../hooks/useRefunds';

export default function MyTickets() {
  const { isAuthenticated } = useAuthStore();
  const [refundingTicketId, setRefundingTicketId] = useState<string | null>(null);
  const requestRefund = useRequestRefund();

  const { data: tickets, isLoading } = useQuery({
    queryKey: ['tickets'],
    queryFn: async () => {
      const response = await apiClient.get('/tickets');
      return response.data;
    },
    enabled: isAuthenticated,
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
  };

  const formatPrice = (priceWei: number | null | undefined) => {
    if (!priceWei) return 'N/A';
    return (priceWei / 1e18).toFixed(0) + ' USDC';
  };

  const handleRefund = async (ticketId: string) => {
    if (!confirm('정말 이 티켓을 환불하시겠습니까?')) {
      return;
    }

    setRefundingTicketId(ticketId);
    try {
      await requestRefund.mutateAsync({
        ticket_id: ticketId,
        reason: '사용자 요청 환불',
      });
      alert('환불 요청이 완료되었습니다. 주최자 승인 후 환불이 처리됩니다.');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || '환불 요청 중 오류가 발생했습니다.';
      alert(errorMessage);
    } finally {
      setRefundingTicketId(null);
    }
  };

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🔒</div>
          <p className="text-xl text-gray-600 mb-6">로그인이 필요합니다.</p>
          <Link to="/login" className="btn-primary inline-block">
            로그인하기
          </Link>
        </div>
      </Layout>
    );
  }

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
        <h1 className="text-3xl font-bold mb-2 text-gray-800">내 티켓</h1>
      </div>

      {tickets && tickets.length === 0 ? (
        <div className="text-center py-20 card">
          <div className="text-6xl mb-4">🎫</div>
          <p className="text-xl text-gray-600 mb-2">보유한 티켓이 없습니다</p>
          <p className="text-gray-500 mb-6">이벤트를 탐색하고 티켓을 구매해보세요!</p>
          <Link to="/events" className="btn-primary inline-block">
            이벤트 보러가기
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {tickets?.map((ticket: any, index: number) => (
            <div
              key={ticket.id}
              className="card-blue animate-slide-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h2 className="text-lg font-bold mb-1 text-gray-800">
                    {ticket.event_name || `이벤트 #${ticket.event_id}`}
                  </h2>
                  <p className="text-sm text-gray-600 mb-2">
                    {ticket.event_date ? formatDate(ticket.event_date) : formatDate(ticket.created_at)}
                  </p>
                  {ticket.status === 'refunded' && (
                    <p className="text-xs text-red-600 font-medium">환불 완료</p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-800 mb-1">
                    {formatPrice(ticket.purchase_price_wei)} / 1매
                  </p>
                  <p className="text-xs text-gray-500 mb-2">티켓 구매</p>
                  {ticket.status !== 'refunded' && (
                    <button
                      onClick={() => handleRefund(ticket.id)}
                      disabled={refundingTicketId === ticket.id}
                      className={`px-3 py-1 text-xs rounded-lg transition-all ${
                        refundingTicketId === ticket.id
                          ? 'bg-gray-400 text-white cursor-not-allowed'
                          : 'bg-red-500 text-white hover:bg-red-600'
                      }`}
                    >
                      {refundingTicketId === ticket.id ? '처리 중...' : '환불 요청'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}

