import { useState } from 'react';
import { useRegister } from '../hooks/useAuth';
import { useToastStore } from '../components/ToastContainer';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const register = useRegister();
  const addToast = useToastStore((state) => state.addToast);

  const handleSendCode = () => {
    if (!email) {
      addToast('이메일을 입력해주세요.', 'error');
      return;
    }
    addToast('인증 코드가 전송되었습니다. (테스트 모드)', 'info');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      addToast('비밀번호가 일치하지 않습니다.', 'error');
      return;
    }
    register.mutate(
      { email, password, role: 'buyer' },
      {
        onError: () => {
          addToast('회원가입에 실패했습니다. 다시 시도해주세요.', 'error');
        },
        onSuccess: () => {
          addToast('회원가입이 완료되었습니다! 로그인해주세요.', 'success');
        },
      }
    );
  };

  return (
    <Layout>
      <div className="max-w-md mx-auto animate-slide-up">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 text-gray-800">회원가입</h1>
        </div>
        
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-lg">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              이름
            </label>
            <div className="input-field-with-icon">
              <span className="input-icon">👤</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="이름을 입력하세요"
                className="input-field"
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              E-mail
            </label>
            <div className="flex gap-2">
              <div className="input-field-with-icon flex-1">
                <span className="input-icon">📧</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="your@email.com"
                  className="input-field"
                />
              </div>
              <button
                type="button"
                onClick={handleSendCode}
                className="px-4 py-3 bg-gradient-to-r from-pink-400 to-yellow-400 text-white font-semibold rounded-lg shadow hover:shadow-md transition-all whitespace-nowrap"
              >
                코드 전송
              </button>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              인증 코드
            </label>
            <div className="input-field-with-icon">
              <span className="input-icon">📄</span>
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="인증 코드를 입력하세요"
                className="input-field"
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              비밀번호
            </label>
            <div className="input-field-with-icon">
              <span className="input-icon">🔒</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                placeholder="비밀번호를 입력하세요"
                className="input-field"
              />
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              비밀번호 (다시 입력)
            </label>
            <div className="input-field-with-icon">
              <span className="input-icon">🔒</span>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
                placeholder="비밀번호를 다시 입력하세요"
                className="input-field"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={register.isPending}
            className="btn-gradient-pink w-full"
          >
            {register.isPending ? (
              <span className="flex items-center justify-center gap-2">
                <LoadingSpinner size="sm" />
                가입 중...
              </span>
            ) : (
              '회원가입'
            )}
          </button>
        </form>
      </div>
    </Layout>
  );
}

