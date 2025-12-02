import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateEvent } from '../hooks/useEvents';
import { useAuthStore } from '../store/authStore';
import { useToastStore } from '../components/ToastContainer';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function CreateEvent() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();
  const createEvent = useCreateEvent();
  const addToast = useToastStore((state) => state.addToast);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price_wei: '',
    max_tickets: '',
    start_time: '',
    end_time: '',
    event_date: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!isAuthenticated || (user?.role !== 'organizer' && user?.role !== 'admin')) {
      addToast('주최자 권한이 필요합니다.', 'error');
      return;
    }

    const eventData = {
      ...formData,
      price_wei: parseInt(formData.price_wei) * 1e18, // MATIC to wei
      max_tickets: parseInt(formData.max_tickets),
    };

    createEvent.mutate(eventData, {
      onSuccess: () => {
        addToast('이벤트가 생성되었습니다. 관리자 승인을 기다려주세요.', 'success');
        navigate('/events');
      },
      onError: (error: any) => {
        addToast(error.response?.data?.detail || '이벤트 생성에 실패했습니다.', 'error');
      },
    });
  };

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">로그인이 필요합니다.</p>
        </div>
      </Layout>
    );
  }

  if (user?.role !== 'organizer' && user?.role !== 'admin') {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">주최자 권한이 필요합니다.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto animate-fade-in">
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">✨</div>
          <h1 className="text-4xl font-bold mb-2 text-gradient">이벤트 생성</h1>
          <p className="text-gray-600">새로운 이벤트를 만들어보세요</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                이벤트 이름 *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                설명
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                className="input-field"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  티켓 가격 (MATIC) *
                </label>
                <input
                  type="number"
                  name="price_wei"
                  value={formData.price_wei}
                  onChange={handleChange}
                  step="0.0001"
                  min="0"
                  required
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  최대 티켓 수 *
                </label>
                <input
                  type="number"
                  name="max_tickets"
                  value={formData.max_tickets}
                  onChange={handleChange}
                  min="1"
                  required
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                판매 시작 시간 *
              </label>
              <input
                type="datetime-local"
                name="start_time"
                value={formData.start_time}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                판매 종료 시간 *
              </label>
              <input
                type="datetime-local"
                name="end_time"
                value={formData.end_time}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                이벤트 날짜 *
              </label>
              <input
                type="datetime-local"
                name="event_date"
                value={formData.event_date}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              type="submit"
              disabled={createEvent.isPending}
              className="btn-primary flex-1"
            >
              {createEvent.isPending ? (
                <span className="flex items-center justify-center gap-2">
                  <LoadingSpinner size="sm" />
                  생성 중...
                </span>
              ) : (
                '이벤트 생성'
              )}
            </button>
            <button
              type="button"
              onClick={() => navigate('/events')}
              className="btn-secondary px-6"
            >
              취소
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
