import React, { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { authApi } from '../api/auth';

export const AuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setUser = useAuthStore((state) => state.setUser);
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const token = searchParams.get('token');

    if (token) {
      // Store the token
      localStorage.setItem('access_token', token);

      // Fetch real user data from the backend
      authApi.me().then((user) => {
        setUser(user);
        navigate('/');
      }).catch(() => {
        // Fallback if /me endpoint fails
        setUser({ id: 0, email: '', is_active: true, is_superuser: false });
        navigate('/');
      });
    } else {
      // No token, redirect to login with error
      navigate('/login?error=oauth_failed');
    }
  }, [searchParams, navigate, setUser]);

  return (
    <div className="min-h-screen bg-dark-primary flex items-center justify-center">
      <div className="card max-w-md w-full text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-dark-700">Completing sign in...</h2>
        <p className="text-dark-500 mt-2">Please wait while we redirect you.</p>
      </div>
    </div>
  );
};
