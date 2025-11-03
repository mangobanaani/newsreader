import { create } from 'zustand';
import { authApi } from '../api/auth';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: authApi.isAuthenticated(),
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => {
    authApi.logout();
    set({ user: null, isAuthenticated: false });
  },
}));
