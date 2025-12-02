import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import WalletStatus from './WalletStatus';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-40 backdrop-blur-sm bg-white/95">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="text-2xl font-bold text-gradient">
              🎫 블록체인 티켓팅
            </Link>
            
            <div className="flex items-center space-x-2">
              <Link
                to="/events"
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  isActive('/events')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                이벤트
              </Link>
              <Link
                to="/marketplace"
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  isActive('/marketplace')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                마켓플레이스
              </Link>
              
              {isAuthenticated ? (
                <>
                  <Link
                    to="/tickets"
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      isActive('/tickets')
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    내 티켓
                  </Link>
                  {user?.role === 'organizer' && (
                    <Link
                      to="/create-event"
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        isActive('/create-event')
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      이벤트 생성
                    </Link>
                  )}
                  {user?.role === 'admin' && (
                    <Link
                      to="/admin"
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        isActive('/admin')
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      관리자
                    </Link>
                  )}
                  <WalletStatus />
                  <div className="ml-4 px-4 py-2 bg-gray-100 rounded-lg">
                    <span className="text-sm text-gray-700">{user?.email}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors"
                  >
                    로그아웃
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-4 py-2 text-sm text-blue-600 border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
                  >
                    로그인
                  </Link>
                  <Link
                    to="/register"
                    className="px-4 py-2 text-sm text-white bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium shadow-md"
                  >
                    회원가입
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 animate-fade-in">{children}</main>
    </div>
  );
}

