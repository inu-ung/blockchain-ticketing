import { useState } from 'react';
import { ethers } from 'ethers';
import apiClient from '../services/api';
import { useToastStore } from './ToastContainer';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  eventPrice: bigint;
  eventName: string;
}

export default function PaymentModal({
  isOpen,
  onClose,
  onSuccess,
  eventPrice,
  eventName,
}: PaymentModalProps) {
  const addToast = useToastStore((state) => state.addToast);
  const [loading, setLoading] = useState(false);
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvc, setCardCvc] = useState('');
  const [cardName, setCardName] = useState('');

  const priceEth = ethers.formatEther(eventPrice);

  const handleCardPayment = async () => {
    if (!cardNumber || !cardExpiry || !cardCvc || !cardName) {
      addToast('카드 정보를 모두 입력해주세요.', 'error');
      return;
    }

    try {
      setLoading(true);
      
      // 카드 결제 처리 (백엔드 API 호출)
      const response = await apiClient.post('/payments/process-card', {
        amount_wei: eventPrice.toString(),
        card_number: cardNumber,
        card_expiry: cardExpiry,
        card_cvc: cardCvc,
        card_name: cardName,
      });

      if (response.data.success) {
        addToast('결제 완료! 티켓을 구매합니다.', 'success');
        // 결제 완료 후 티켓 구매 진행
        onSuccess();
      }
    } catch (error: any) {
      addToast(error.response?.data?.detail || '결제에 실패했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
        <h2 className="text-2xl font-bold mb-6">티켓 구매</h2>
        
        <div className="mb-6">
          <p className="text-gray-700 mb-2">이벤트: <strong>{eventName}</strong></p>
          <p className="text-gray-700 mb-4">가격: <strong>{priceEth} MATIC</strong></p>
          <p className="text-sm text-gray-500 mb-4">
            💡 카드로 결제하면 자동으로 티켓이 발행됩니다. MetaMask가 필요 없습니다!
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              카드 번호
            </label>
            <input
              type="text"
              placeholder="1234 5678 9012 3456"
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                만료일
              </label>
              <input
                type="text"
                placeholder="MM/YY"
                value={cardExpiry}
                onChange={(e) => setCardExpiry(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CVC
              </label>
              <input
                type="text"
                placeholder="123"
                value={cardCvc}
                onChange={(e) => setCardCvc(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              카드 소유자 이름
            </label>
            <input
              type="text"
              placeholder="홍길동"
              value={cardName}
              onChange={(e) => setCardName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              ✅ 가스비는 무료입니다! Paymaster가 자동으로 처리합니다.
            </p>
          </div>

          <button
            onClick={handleCardPayment}
            disabled={loading}
            className="w-full btn-primary"
          >
            {loading ? '결제 처리 중...' : `${priceEth} MATIC 결제하기`}
          </button>
        </div>

        <button
          onClick={onClose}
          className="mt-4 w-full text-gray-600 hover:text-gray-800"
        >
          취소
        </button>
      </div>
    </div>
  );
}

