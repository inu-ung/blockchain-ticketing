import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  role: string;
  wallet_address?: string;
  smart_wallet_address?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  initialized: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  initialized: false,
  setAuth: (user, token) => {
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  updateUser: (updates) =>
    set((state) => ({
      user: state.user ? { ...state.user, ...updates } : null,
    })),
  initialize: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      set({ initialized: true, isAuthenticated: false });
      return;
    }

    try {
      // 동적 import로 순환 참조 방지
      const apiClient = (await import('../services/api')).default;
      apiClient.defaults.headers.Authorization = `Bearer ${token}`;
      
      const response = await apiClient.get('/auth/me');
      const user = response.data;
      
      set({
        user,
        token,
        isAuthenticated: true,
        initialized: true,
      });
      
      console.log('[authStore] User initialized:', user);
    } catch (error: any) {
      console.error('[authStore] Failed to initialize user:', error);
      // 토큰이 유효하지 않으면 제거
      localStorage.removeItem('token');
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        initialized: true,
      });
    }
  },
}));

