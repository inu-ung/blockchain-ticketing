import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import apiClient from '../services/api';

/**
 * 앱 초기화 시 토큰이 있으면 사용자 정보를 복원하는 컴포넌트
 */
export default function AuthInitializer() {
  const { token, initialize, initialized } = useAuthStore();

  useEffect(() => {
    if (!initialized && token) {
      console.log('[AuthInitializer] Initializing auth...');
      initialize();
    } else if (!initialized) {
      // 토큰이 없으면 초기화 완료로 표시
      useAuthStore.setState({ initialized: true });
    }
  }, [token, initialize, initialized]);

  // 토큰이 있으면 API 요청에 항상 포함
  useEffect(() => {
    if (token) {
      apiClient.defaults.headers.Authorization = `Bearer ${token}`;
    } else {
      delete apiClient.defaults.headers.Authorization;
    }
  }, [token]);

  return null; // UI 렌더링 없음
}

