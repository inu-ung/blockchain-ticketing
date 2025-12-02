import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';

export function useRequestRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { ticket_id: string; reason?: string }) => {
      const response = await apiClient.post('/refunds/request', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      queryClient.invalidateQueries({ queryKey: ['refunds'] });
    },
  });
}

export function useGetRefunds() {
  return useQuery({
    queryKey: ['refunds'],
    queryFn: async () => {
      const response = await apiClient.get('/refunds');
      return response.data;
    },
  });
}

