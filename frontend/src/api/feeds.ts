import { apiClient } from './client';
import type { Feed, FeedCreate } from '../types';

export const feedsApi = {
  list: async (): Promise<Feed[]> => {
    const response = await apiClient.get<Feed[]>('/feeds/');
    return response.data;
  },

  create: async (data: FeedCreate): Promise<Feed> => {
    const response = await apiClient.post<Feed>('/feeds/', data);
    return response.data;
  },

  get: async (id: number): Promise<Feed> => {
    const response = await apiClient.get<Feed>(`/feeds/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<FeedCreate>): Promise<Feed> => {
    const response = await apiClient.put<Feed>(`/feeds/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/feeds/${id}`);
  },

  refresh: async (id: number): Promise<{ new_articles: number }> => {
    const response = await apiClient.post<{ new_articles: number }>(`/feeds/${id}/refresh`);
    return response.data;
  },

  refreshAll: async (): Promise<{ new_articles: number; errors: number; feeds_updated: number }> => {
    const response = await apiClient.post<{ new_articles: number; errors: number; feeds_updated: number }>('/feeds/refresh-all');
    return response.data;
  },
};
