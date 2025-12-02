import { Link } from 'react-router-dom';
import Layout from '../components/Layout';

export default function Home() {
  return (
    <Layout>
      <div className="text-center py-20 animate-fade-in">
        <div className="mb-8">
          <h1 className="text-6xl font-bold mb-6 text-gradient">
            블록체인 티켓팅 시스템
          </h1>
          <p className="text-2xl text-gray-600 mb-4">
            Polygon 기반 NFT 티켓팅 플랫폼
          </p>
          <p className="text-gray-500">
            위조 방지, 투명한 재판매, 스마트 컨트랙트 기반 자동 환불
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
          <Link
            to="/events"
            className="card p-8 text-left group"
          >
            <div className="text-4xl mb-4">🎵</div>
            <h2 className="text-2xl font-bold mb-3 text-gray-800 group-hover:text-blue-600 transition-colors">
              이벤트 탐색
            </h2>
            <p className="text-gray-600 mb-4 leading-relaxed">
              다양한 이벤트를 탐색하고 NFT 티켓을 구매하세요. 모든 티켓은 블록체인에 안전하게 저장됩니다.
            </p>
            <span className="text-blue-600 font-semibold group-hover:underline inline-flex items-center">
              이벤트 보기
              <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
            </span>
          </Link>

          <Link
            to="/tickets"
            className="card p-8 text-left group"
          >
            <div className="text-4xl mb-4">🎫</div>
            <h2 className="text-2xl font-bold mb-3 text-gray-800 group-hover:text-blue-600 transition-colors">
              내 티켓
            </h2>
            <p className="text-gray-600 mb-4 leading-relaxed">
              구매한 티켓을 확인하고 관리하세요. 언제든지 재판매하거나 환불할 수 있습니다.
            </p>
            <span className="text-blue-600 font-semibold group-hover:underline inline-flex items-center">
              티켓 보기
              <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
            </span>
          </Link>

          <Link
            to="/marketplace"
            className="card p-8 text-left group"
          >
            <div className="text-4xl mb-4">🛒</div>
            <h2 className="text-2xl font-bold mb-3 text-gray-800 group-hover:text-blue-600 transition-colors">
              재판매 마켓
            </h2>
            <p className="text-gray-600 mb-4 leading-relaxed">
              2차 시장에서 티켓을 구매하거나 판매하세요. 모든 거래는 투명하게 블록체인에 기록됩니다.
            </p>
            <span className="text-blue-600 font-semibold group-hover:underline inline-flex items-center">
              마켓플레이스
              <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
            </span>
          </Link>
        </div>

        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white shadow-2xl">
          <h3 className="text-3xl font-bold mb-4">왜 블록체인 티켓팅인가요?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div>
              <div className="text-3xl mb-2">🔒</div>
              <h4 className="font-semibold mb-2">위조 방지</h4>
              <p className="text-blue-100 text-sm">각 티켓이 고유한 NFT로 발행되어 위조가 불가능합니다</p>
            </div>
            <div>
              <div className="text-3xl mb-2">📊</div>
              <h4 className="font-semibold mb-2">투명한 거래</h4>
              <p className="text-blue-100 text-sm">모든 거래가 블록체인에 기록되어 투명하게 추적 가능합니다</p>
            </div>
            <div>
              <div className="text-3xl mb-2">⚡</div>
              <h4 className="font-semibold mb-2">자동 환불</h4>
              <p className="text-blue-100 text-sm">스마트 컨트랙트로 환불이 자동으로 처리됩니다</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

