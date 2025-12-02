import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';

export function useEvents(status?: string) {
  return useQuery({
    queryKey: ['events', status],
    queryFn: async () => {
      try {
        const params = status ? { status_filter: status } : {};
        console.log('[useEvents] Fetching events with params:', params);
        const response = await apiClient.get('/events', { params });
        console.log('[useEvents] Events fetched:', response.data);
        return response.data;
      } catch (error: any) {
        console.error('[useEvents] Error fetching events:', error);
        console.error('[useEvents] Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
        });
        throw error;
      }
    },
    retry: 1, // 재시도 1회만
  });
}

export function useEvent(id: string) {
  return useQuery({
    queryKey: ['event', id],
    queryFn: async () => {
      const response = await apiClient.get(`/events/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/events', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });
}

export function usePurchaseTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { event_id: string; token_uri?: string }) => {
      const response = await apiClient.post('/tickets/purchase', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });
}

