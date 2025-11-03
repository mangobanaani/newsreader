import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './store/authStore';
import { ThemeProvider } from './contexts/ThemeContext';
import { Login } from './pages/Login';
import { AuthCallback } from './pages/AuthCallback';
import { Home } from './pages/Home';
import { Recommendations } from './pages/Recommendations';
import { Analytics } from './pages/Analytics';
import { Bookmarks } from './pages/Bookmarks';
import { FeedManagement } from './pages/FeedManagement';
import { Preferences } from './pages/Preferences';
import { CommandPaletteProvider } from './contexts/CommandPaletteContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <CommandPaletteProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/auth/callback" element={<AuthCallback />} />
              <Route
                path="/"
                element={
                  <PrivateRoute>
                    <Home />
                  </PrivateRoute>
                }
              />
              <Route
                path="/recommendations"
                element={
                  <PrivateRoute>
                    <Recommendations />
                  </PrivateRoute>
                }
              />
              <Route
                path="/analytics"
                element={
                  <PrivateRoute>
                    <Analytics />
                  </PrivateRoute>
                }
              />
              <Route
                path="/bookmarks"
                element={
                  <PrivateRoute>
                    <Bookmarks />
                  </PrivateRoute>
                }
              />
              <Route
                path="/feeds"
                element={
                  <PrivateRoute>
                    <FeedManagement />
                  </PrivateRoute>
                }
              />
              <Route
                path="/preferences"
                element={
                  <PrivateRoute>
                    <Preferences />
                  </PrivateRoute>
                }
              />
            </Routes>
          </CommandPaletteProvider>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
