import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useEvent, usePurchaseTicket } from '../hooks/useEvents';
import { useAuthStore } from '../store/authStore';
import { useToastStore } from '../components/ToastContainer';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import PaymentModal from '../components/PaymentModal';

export default function EventDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: event, isLoading } = useEvent(id || '');
  const { isAuthenticated } = useAuthStore();
  const purchaseTicket = usePurchaseTicket();
  const addToast = useToastStore((state) => state.addToast);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatPrice = (priceWei: number) => {
    return (priceWei / 1e18).toFixed(4) + ' MATIC';
  };

  const handlePurchase = () => {
    if (!isAuthenticated) {
      addToast('로그인이 필요합니다.', 'info');
      navigate('/login');
      return;
    }

    if (!id || !event) return;

    // 결제 모달 표시
    setShowPaymentModal(true);
  };

  const handlePurchaseConfirm = () => {
    if (!id) return;

    purchaseTicket.mutate(
      { event_id: id },
      {
        onSuccess: () => {
          addToast('티켓 구매가 완료되었습니다!', 'success');
          setShowPaymentModal(false);
          navigate('/tickets');
        },
        onError: (error: any) => {
          const errorDetail = error.response?.data?.detail;
          
          // 잔액 부족 에러 처리
          if (error.response?.status === 402 || (errorDetail && typeof errorDetail === 'object' && errorDetail.error === 'Insufficient balance')) {
            addToast('Smart Wallet 잔액이 부족합니다. 충전 후 다시 시도해주세요.', 'error');
            // 모달은 유지 (충전 가능하도록)
          } else {
            addToast(errorDetail?.message || errorDetail || '구매에 실패했습니다.', 'error');
            setShowPaymentModal(false);
          }
        },
      }
    );
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

  if (!event) {
    return (
      <Layout>
        <div className="text-center py-20">
          <div className="text-5xl mb-4">😕</div>
          <p className="text-red-600 text-lg">이벤트를 찾을 수 없습니다.</p>
        </div>
      </Layout>
    );
  }

  const isAvailable = event.status === 'approved' || event.status === 'active';
  const isSoldOut = event.sold_tickets >= event.max_tickets;
  const progress = (event.sold_tickets / event.max_tickets) * 100;

  return (
    <Layout>
      <div className="max-w-5xl mx-auto animate-fade-in">
        <button
          onClick={() => navigate(-1)}
          className="mb-6 text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-2"
        >
          <span>←</span> 뒤로가기
        </button>

        <div className="card overflow-hidden">
          {/* Hero Image */}
          <div className="w-full h-64 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center">
            <span className="text-8xl">🎵</span>
          </div>

          <div className="p-8">
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <h1 className="text-4xl font-bold mb-3 text-gray-800">{event.name}</h1>
                <span
                  className={`badge ${
                    event.status === 'approved'
                      ? 'badge-success'
                      : event.status === 'active'
                      ? 'badge-info'
                      : 'badge-gray'
                  }`}
                >
                  {event.status === 'approved' ? '✓ 승인됨' : 
                   event.status === 'active' ? '🔥 판매 중' : 
                   event.status === 'pending' ? '⏳ 대기 중' : event.status}
                </span>
              </div>
            </div>

            {event.description && (
              <div className="mb-8 p-6 bg-gray-50 rounded-lg">
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {event.description}
                </p>
              </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl">
                <div className="text-sm font-medium text-gray-600 mb-2">가격</div>
                <div className="text-3xl font-bold text-blue-600">{formatPrice(event.price_wei)}</div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl">
                <div className="text-sm font-medium text-gray-600 mb-2">판매 현황</div>
                <div className="text-3xl font-bold text-green-600">
                  {event.sold_tickets} / {event.max_tickets}
                </div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl">
                <div className="text-sm font-medium text-gray-600 mb-2">판매 시작</div>
                <div className="text-sm font-semibold text-purple-600">{formatDate(event.start_time)}</div>
              </div>
              <div className="bg-gradient-to-br from-pink-50 to-pink-100 p-6 rounded-xl">
                <div className="text-sm font-medium text-gray-600 mb-2">이벤트 날짜</div>
                <div className="text-sm font-semibold text-pink-600">{formatDate(event.event_date)}</div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-8">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>판매 진행률</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>

            {/* Purchase Button */}
            <div className="border-t pt-6">
              {isSoldOut ? (
                <button
                  disabled
                  className="w-full py-4 px-6 bg-gray-300 text-gray-600 rounded-xl cursor-not-allowed font-semibold text-lg"
                >
                  🎫 매진
                </button>
              ) : !isAvailable ? (
                <button
                  disabled
                  className="w-full py-4 px-6 bg-gray-300 text-gray-600 rounded-xl cursor-not-allowed font-semibold text-lg"
                >
                  ⏳ 판매 준비 중
                </button>
              ) : (
                <button
                  onClick={handlePurchase}
                  disabled={purchaseTicket.isPending}
                  className="btn-primary w-full text-lg py-4"
                >
                  {purchaseTicket.isPending ? (
                    <span className="flex items-center justify-center gap-2">
                      <LoadingSpinner size="sm" />
                      구매 중...
                    </span>
                  ) : (
                    '🎫 티켓 구매하기'
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 결제 모달 */}
      {event && (
        <PaymentModal
          isOpen={showPaymentModal}
          onClose={() => setShowPaymentModal(false)}
          onSuccess={handlePurchaseConfirm}
          eventPrice={BigInt(event.price_wei)}
          eventName={event.name}
        />
      )}
    </Layout>
  );
}
