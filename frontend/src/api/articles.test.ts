import { describe, it, expect, vi, beforeEach } from 'vitest';
import { articlesApi } from './articles';
import { apiClient } from './client';

vi.mock('./client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

describe('articlesApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('list', () => {
    it('fetches articles with default parameters', async () => {
      const mockArticles = [
        {
          id: 1,
          title: 'Test Article 1',
          link: 'https://example.com/1',
          is_read: false,
        },
        {
          id: 2,
          title: 'Test Article 2',
          link: 'https://example.com/2',
          is_read: true,
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockArticles });

      const result = await articlesApi.list();

      expect(apiClient.get).toHaveBeenCalledWith('/articles/', {
        params: undefined,
      });
      expect(result).toEqual(mockArticles);
    });

    it('fetches articles with custom parameters', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      await articlesApi.list({
        skip: 10,
        limit: 20,
        unread_only: true,
        bookmarked_only: false,
        topic: 'technology',
      });

      expect(apiClient.get).toHaveBeenCalledWith('/articles/', {
        params: {
          skip: 10,
          limit: 20,
          unread_only: true,
          bookmarked_only: false,
          topic: 'technology',
        },
      });
    });

    it('handles errors when fetching articles', async () => {
      const error = new Error('Network error');
      vi.mocked(apiClient.get).mockRejectedValue(error);

      await expect(articlesApi.list()).rejects.toThrow('Network error');
    });
  });

  describe('get', () => {
    it('fetches single article by ID', async () => {
      const mockArticle = {
        id: 1,
        title: 'Test Article',
        link: 'https://example.com/article',
        description: 'Test description',
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockArticle });

      const result = await articlesApi.get(1);

      expect(apiClient.get).toHaveBeenCalledWith('/articles/1');
      expect(result).toEqual(mockArticle);
    });

    it('handles not found error', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Not found'));

      await expect(articlesApi.get(999)).rejects.toThrow('Not found');
    });
  });

  describe('markAsRead', () => {
    it('marks article as read', async () => {
      const mockArticle = {
        id: 1,
        title: 'Test',
        is_read: true,
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockArticle });

      const result = await articlesApi.markAsRead(1);

      expect(apiClient.post).toHaveBeenCalledWith('/articles/1/read');
      expect(result.is_read).toBe(true);
    });
  });

  describe('toggleBookmark', () => {
    it('toggles bookmark on an article', async () => {
      const mockArticle = {
        id: 1,
        title: 'Test',
        is_bookmarked: true,
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockArticle });

      const result = await articlesApi.toggleBookmark(1);

      expect(apiClient.post).toHaveBeenCalledWith('/articles/1/bookmark');
      expect(result.is_bookmarked).toBe(true);
    });
  });

  describe('getTopics', () => {
    it('fetches all available topics', async () => {
      const mockTopics = { technology: 10, ai: 5, science: 8, politics: 3 };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockTopics });

      const result = await articlesApi.getTopics();

      expect(apiClient.get).toHaveBeenCalledWith('/articles/topics/all');
      expect(result).toEqual(mockTopics);
    });

    it('handles empty topics list', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: {} });

      const result = await articlesApi.getTopics();

      expect(result).toEqual({});
    });
  });

  describe('getLLMInsights', () => {
    it('fetches AI insights for an article', async () => {
      const mockInsights = {
        summary: 'AI-generated summary',
        key_points: ['Point 1', 'Point 2', 'Point 3'],
        reliability_score: 0.85,
        reliability_label: 'Highly Reliable',
        tone: 'Neutral/Informational',
        suggested_actions: ['Read more', 'Check sources'],
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockInsights });

      const result = await articlesApi.getLLMInsights(1);

      expect(apiClient.get).toHaveBeenCalledWith('/articles/1/llm-insights');
      expect(result).toEqual(mockInsights);
      expect(result.key_points.length).toBe(3);
    });

    it('handles insights generation failure', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(
        new Error('LLM features disabled')
      );

      await expect(articlesApi.getLLMInsights(1)).rejects.toThrow(
        'LLM features disabled'
      );
    });
  });

  describe('getRecommendations', () => {
    it('fetches personalized recommendations', async () => {
      const mockRecommendations = [
        {
          id: 1,
          title: 'Recommended Article 1',
          recommendation_score: 0.95,
        },
        {
          id: 2,
          title: 'Recommended Article 2',
          recommendation_score: 0.87,
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockRecommendations });

      const result = await articlesApi.getRecommendations(10);

      expect(apiClient.get).toHaveBeenCalledWith('/articles/recommendations', {
        params: { limit: 10 },
      });
      expect(result).toEqual(mockRecommendations);
      expect(result.length).toBe(2);
    });

    it('uses default limit when not specified', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      await articlesApi.getRecommendations();

      expect(apiClient.get).toHaveBeenCalledWith('/articles/recommendations', {
        params: { limit: undefined },
      });
    });
  });
});
