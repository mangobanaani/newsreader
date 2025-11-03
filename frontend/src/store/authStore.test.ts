import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from './authStore';
import { authApi } from '../api/auth';
import type { User } from '../types';

vi.mock('../api/auth', () => ({
  authApi: {
    isAuthenticated: vi.fn(),
    logout: vi.fn(),
  },
}));

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({ user: null, isAuthenticated: false });
    vi.clearAllMocks();
  });

  it('initializes with null user and checks authentication', () => {
    vi.mocked(authApi.isAuthenticated).mockReturnValue(false);

    const state = useAuthStore.getState();

    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('sets user and updates authentication status', () => {
    const mockUser: User = {
      id: 1,
      email: 'test@example.com',
      is_active: true,
      is_superuser: false,
    };

    const { setUser } = useAuthStore.getState();
    setUser(mockUser);

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });

  it('clears user when set to null', () => {
    const mockUser: User = {
      id: 1,
      email: 'test@example.com',
      is_active: true,
      is_superuser: false,
    };

    const { setUser } = useAuthStore.getState();
    setUser(mockUser);

    expect(useAuthStore.getState().isAuthenticated).toBe(true);

    setUser(null);

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('logs out user and calls authApi.logout', () => {
    const mockUser: User = {
      id: 1,
      email: 'test@example.com',
      is_active: true,
      is_superuser: false,
    };

    const { setUser, logout } = useAuthStore.getState();
    setUser(mockUser);

    expect(useAuthStore.getState().isAuthenticated).toBe(true);

    logout();

    expect(authApi.logout).toHaveBeenCalled();
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('maintains state across multiple operations', () => {
    const { setUser } = useAuthStore.getState();

    const user1: User = {
      id: 1,
      email: 'user1@example.com',
      is_active: true,
      is_superuser: false,
    };

    const user2: User = {
      id: 2,
      email: 'user2@example.com',
      is_active: true,
      is_superuser: false,
    };

    setUser(user1);
    expect(useAuthStore.getState().user?.id).toBe(1);

    setUser(user2);
    expect(useAuthStore.getState().user?.id).toBe(2);

    setUser(null);
    expect(useAuthStore.getState().user).toBeNull();
  });
});
