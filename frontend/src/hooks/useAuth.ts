import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  role?: string;
}

export function useLogin() {
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (data: LoginData) => {
      const response = await apiClient.post('/auth/login', data);
      return response.data;
    },
    onSuccess: async (data) => {
      // 백엔드 응답 형식에 맞게 수정
      const token = data.access_token || data.token?.access_token;
      console.log('[useAuth] Login response:', data);
      
      if (token) {
        // 사용자 정보를 별도로 가져오기
        try {
          const apiClient = (await import('../services/api')).default;
          apiClient.defaults.headers.Authorization = `Bearer ${token}`;
          const userResponse = await apiClient.get('/auth/me');
          const user = userResponse.data;
          console.log('[useAuth] User info:', user);
          
          if (user) {
            setAuth(user, token);
            navigate('/');
          } else {
            console.error('[useAuth] User info not found');
          }
        } catch (error) {
          console.error('[useAuth] Failed to get user info:', error);
          // 토큰만으로 진행 (나중에 사용자 정보 가져올 수 있음)
          if (data.user) {
            setAuth(data.user, token);
            navigate('/');
          }
        }
      } else {
        console.error('[useAuth] Token not found in response');
      }
    },
  });
}

export function useRegister() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await apiClient.post('/auth/register', data);
      return response.data;
    },
    onSuccess: () => {
      navigate('/login');
    },
  });
}

export function useMe() {
  const { token } = useAuthStore();
  
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const response = await apiClient.get('/auth/me');
      return response.data;
    },
    enabled: !!token,
  });
}

