import { apiClient } from './client';
import type { Article, ArticleLLMInsights, ArticleWithRecommendation } from '../types';

export const articlesApi = {
  list: async (params?: {
    skip?: number;
    limit?: number;
    unread_only?: boolean;
    bookmarked_only?: boolean;
    topic?: string;
    min_sentiment?: number;
    max_sentiment?: number;
    sort_by?: 'date' | 'sentiment';
  }): Promise<Article[]> => {
    const response = await apiClient.get<Article[]>('/articles/', { params });
    return response.data;
  },

  getTopics: async (): Promise<Record<string, number>> => {
    const response = await apiClient.get<Record<string, number>>('/articles/topics/all');
    return response.data;
  },

  processAll: async (): Promise<{ processed: number; total: number; message: string }> => {
    const response = await apiClient.post<{ processed: number; total: number; message: string }>('/articles/process-all');
    return response.data;
  },

  cluster: async (): Promise<{ clusters: number }> => {
    const response = await apiClient.post<{ clusters: number }>('/articles/cluster');
    return response.data;
  },

  get: async (id: number): Promise<Article> => {
    const response = await apiClient.get<Article>(`/articles/${id}`);
    return response.data;
  },

  getRecommendations: async (limit?: number): Promise<ArticleWithRecommendation[]> => {
    const response = await apiClient.get<ArticleWithRecommendation[]>('/articles/recommendations', {
      params: { limit },
    });
    return response.data;
  },

  markAsRead: async (id: number): Promise<Article> => {
    const response = await apiClient.post<Article>(`/articles/${id}/read`);
    return response.data;
  },

  toggleBookmark: async (id: number): Promise<Article> => {
    const response = await apiClient.post<Article>(`/articles/${id}/bookmark`);
    return response.data;
  },

  rate: async (id: number, rating: number): Promise<Article> => {
    const response = await apiClient.post<Article>(`/articles/${id}/rate`, null, {
      params: { rating },
    });
    return response.data;
  },

  getSimilar: async (id: number, limit?: number): Promise<Article[]> => {
    const response = await apiClient.get<Article[]>(`/articles/${id}/similar`, {
      params: { limit },
    });
    return response.data;
  },

  getLLMInsights: async (id: number): Promise<ArticleLLMInsights> => {
    const response = await apiClient.get<ArticleLLMInsights>(`/articles/${id}/llm-insights`);
    return response.data;
  },

  // Analytics
  getSentimentAnalytics: async (): Promise<{
    positive: number;
    slightly_positive: number;
    neutral: number;
    slightly_negative: number;
    negative: number;
    total: number;
    daily_trends: Record<string, { positive: number; neutral: number; negative: number }>;
  }> => {
    const response = await apiClient.get('/articles/analytics/sentiment');
    return response.data;
  },

  getTopicTrends: async (days: number = 7): Promise<{
    trending_topics: Array<{ topic: string; count: number; growth: number }>;
  }> => {
    const response = await apiClient.get('/articles/analytics/topics', {
      params: { days },
    });
    return response.data;
  },

  getClusterAnalytics: async (): Promise<{
    clusters: Array<{ cluster_id: number; article_count: number; article_ids: number[] }>;
  }> => {
    const response = await apiClient.get('/articles/analytics/clusters');
    return response.data;
  },

  // Export
  exportCsv: (params?: {
    topic?: string;
    min_sentiment?: number;
    max_sentiment?: number;
  }): string => {
    const queryParams = new URLSearchParams();
    if (params?.topic) queryParams.append('topic', params.topic);
    if (params?.min_sentiment !== undefined) queryParams.append('min_sentiment', params.min_sentiment.toString());
    if (params?.max_sentiment !== undefined) queryParams.append('max_sentiment', params.max_sentiment.toString());

    return `/articles/export/csv?${queryParams.toString()}`;
  },

  exportJson: (params?: {
    topic?: string;
    min_sentiment?: number;
    max_sentiment?: number;
  }): string => {
    const queryParams = new URLSearchParams();
    if (params?.topic) queryParams.append('topic', params.topic);
    if (params?.min_sentiment !== undefined) queryParams.append('min_sentiment', params.min_sentiment.toString());
    if (params?.max_sentiment !== undefined) queryParams.append('max_sentiment', params.max_sentiment.toString());

    return `/articles/export/json?${queryParams.toString()}`;
  },
};
