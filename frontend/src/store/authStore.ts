import { create } from 'zustand';
import { authApi } from '../api/auth';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: authApi.isAuthenticated(),
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => {
    authApi.logout();
    set({ user: null, isAuthenticated: false });
  },
  fetchUser: async () => {
    try {
      const user = await authApi.me();
      set({ user, isAuthenticated: true });
    } catch {
      authApi.logout();
      set({ user: null, isAuthenticated: false });
    }
  },
}));

// Hydrate user from token on startup
if (authApi.isAuthenticated()) {
  useAuthStore.getState().fetchUser();
}
