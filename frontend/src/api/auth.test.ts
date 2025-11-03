import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { authApi } from './auth';
import { apiClient } from './client';

vi.mock('./client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('authApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('register', () => {
    it('registers a new user successfully', async () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        is_active: true,
        created_at: new Date(),
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockUser });

      const result = await authApi.register({
        email: 'test@example.com',
        password: 'password123',
      });

      expect(apiClient.post).toHaveBeenCalledWith('/auth/register', {
        email: 'test@example.com',
        password: 'password123',
      });
      expect(result).toEqual(mockUser);
    });

    it('throws error on registration failure', async () => {
      const mockError = new Error('Email already exists');
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      await expect(
        authApi.register({
          email: 'existing@example.com',
          password: 'password123',
        })
      ).rejects.toThrow('Email already exists');
    });
  });

  describe('login', () => {
    it('sends correct login request and stores token', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-token',
          token_type: 'bearer',
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await authApi.login({
        username: 'test@example.com',
        password: 'password123',
      });

      expect(apiClient.post).toHaveBeenCalledWith(
        '/auth/login',
        expect.any(URLSearchParams),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const callArgs = vi.mocked(apiClient.post).mock.calls[0];
      const formData = callArgs[1] as URLSearchParams;
      expect(formData.get('username')).toBe('test@example.com');
      expect(formData.get('password')).toBe('password123');

      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('access_token')).toBe('mock-token');
    });

    it('throws error on failed login', async () => {
      const mockError = new Error('Invalid credentials');
      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      await expect(
        authApi.login({
          username: 'wrong@example.com',
          password: 'wrongpass',
        })
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('removes access token from localStorage', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(localStorage.getItem('access_token')).toBe('test-token');

      authApi.logout();

      expect(localStorage.getItem('access_token')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('returns true when token exists', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(authApi.isAuthenticated()).toBe(true);
    });

    it('returns false when token does not exist', () => {
      expect(authApi.isAuthenticated()).toBe(false);
    });
  });
});
