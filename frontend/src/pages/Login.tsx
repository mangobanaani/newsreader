import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/authStore';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const setUser = useAuthStore((state) => state.setUser);

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: () => {
      setUser({ id: 0, email, is_active: true, is_superuser: false });
      navigate('/');
    },
    onError: () => {
      setError('Invalid email or password');
    },
  });

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    setError('');
    loginMutation.mutate({ username: email, password });
  };

  return (
    <div className="min-h-screen bg-dark-primary flex items-center justify-center px-4">
      <div className="card max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl items-center justify-center mb-4">
            <span className="text-white font-bold text-3xl">N</span>
          </div>
          <h1 className="text-3xl font-bold text-dark-700">Welcome Back</h1>
          <p className="text-dark-500 mt-2">Sign in to continue to NewsReader</p>
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-3 mb-6">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-dark-600 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input w-full"
              required
              autoComplete="email"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-dark-600 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input w-full"
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="btn-primary w-full"
          >
            {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-dark-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-dark-100 text-dark-500">Or continue with</span>
          </div>
        </div>

        <a
          href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/google/login`}
          className="flex items-center justify-center gap-3 w-full px-4 py-3 border border-dark-300 rounded-lg hover:bg-dark-200 transition-colors"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span className="text-dark-700 font-medium">Continue with Google</span>
        </a>

        <div className="mt-6 text-center">
          <p className="text-dark-500 text-sm">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-500 hover:text-primary-400">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
