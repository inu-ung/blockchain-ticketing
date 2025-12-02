import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useLogin } from '../hooks/useAuth';
import { useToastStore } from '../components/ToastContainer';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const login = useLogin();
  const addToast = useToastStore((state) => state.addToast);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login.mutate(
      { email, password },
      {
        onError: () => {
          addToast('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.', 'error');
        },
      }
    );
  };

  return (
    <Layout>
      <div className="max-w-md mx-auto animate-slide-up">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 text-gray-800">로그인</h1>
        </div>
        
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-lg">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              E-mail
            </label>
            <div className="input-field-with-icon">
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
          </div>

          <div className="mb-6">
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
                placeholder="비밀번호를 입력하세요"
                className="input-field"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={login.isPending}
            className="btn-gradient-pink w-full mb-4"
          >
            {login.isPending ? (
              <span className="flex items-center justify-center gap-2">
                <LoadingSpinner size="sm" />
                로그인 중...
              </span>
            ) : (
              '로그인'
            )}
          </button>

          <Link
            to="/register"
            className="btn-gradient-yellow w-full block text-center"
          >
            회원가입
          </Link>
        </form>
      </div>
    </Layout>
  );
}

