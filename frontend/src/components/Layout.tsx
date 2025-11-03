import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useTheme } from '../contexts/ThemeContext';
import { useCommandPalette } from '../contexts/CommandPaletteContext';
import clsx from 'clsx';
import {
  NewspaperIcon,
  SparklesIcon,
  ChartBarIcon,
  BookmarkIcon,
  RssIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  Bars3Icon,
  PlusCircleIcon,
  ListBulletIcon,
} from '@heroicons/react/24/outline';
import { MagnifyingGlassIcon } from '@heroicons/react/24/solid';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isAuthenticated, logout } = useAuthStore();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { registerCommands, openPalette } = useCommandPalette();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMoreMenuOpen, setIsMoreMenuOpen] = useState(false);

  const navigationLinks = useMemo(
    () => [
      { id: 'feed', label: 'Feed', to: '/', icon: <NewspaperIcon className="w-5 h-5" /> },
      { id: 'recommendations', label: 'Recommendations', to: '/recommendations', icon: <SparklesIcon className="w-5 h-5" /> },
      { id: 'bookmarks', label: 'Bookmarks', to: '/bookmarks', icon: <BookmarkIcon className="w-5 h-5" /> },
      { id: 'analytics', label: 'Analytics', to: '/analytics', icon: <ChartBarIcon className="w-5 h-5" /> },
      { id: 'feeds', label: 'My Feeds', to: '/feeds', icon: <RssIcon className="w-5 h-5" /> },
      { id: 'preferences', label: 'Preferences', to: '/preferences', icon: <Cog6ToothIcon className="w-5 h-5" /> },
    ],
    []
  );

  const primaryLinks = navigationLinks.slice(0, 3);
  const secondaryLinks = navigationLinks.slice(3);

  const handleLogout = useCallback((): void => {
    logout();
    navigate('/login');
  }, [logout, navigate]);

  const handleAddFeed = useCallback(() => {
    navigate('/feeds?add=1');
  }, [navigate]);

  useEffect(() => {
    if (!isAuthenticated) return;

    const cleanup = registerCommands([
      ...navigationLinks.map((link) => ({
        id: `nav-${link.id}`,
        title: link.label,
        group: 'Navigation',
        keywords: [link.label.toLowerCase()],
        action: () => {
          navigate(link.to);
        },
        icon: link.icon,
      })),
      {
        id: 'action-add-feed',
        title: 'Add new feed',
        subtitle: 'Open feed library to add sources',
        group: 'Actions',
        keywords: ['feed', 'add', 'rss'],
        action: handleAddFeed,
        icon: <PlusCircleIcon className="w-5 h-5" />,
      },
      {
        id: 'action-toggle-theme',
        title: theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode',
        group: 'Actions',
        keywords: ['theme', 'dark', 'light', 'toggle'],
        action: toggleTheme,
        icon: theme === 'dark' ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />,
      },
      {
        id: 'action-logout',
        title: 'Log out',
        group: 'Account',
        keywords: ['logout', 'sign out', 'exit'],
        action: handleLogout,
        icon: <ArrowRightOnRectangleIcon className="w-5 h-5" />,
      },
      {
        id: 'action-open-command-palette',
        title: 'Open command palette',
        subtitle: 'Search feeds, topics, or actions',
        group: 'Actions',
        keywords: ['command', 'search', 'palette'],
        action: () => openPalette(),
        icon: <ListBulletIcon className="w-5 h-5" />,
      },
    ]);

    return cleanup;
  }, [handleAddFeed, handleLogout, isAuthenticated, navigate, navigationLinks, openPalette, registerCommands, theme, toggleTheme]);

  useEffect(() => {
    setIsMobileMenuOpen(false);
    setIsMoreMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!isMoreMenuOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (target.closest('[data-more-menu]')) {
        return;
      }
      setIsMoreMenuOpen(false);
    };

    window.addEventListener('click', handleClickOutside);
    return () => window.removeEventListener('click', handleClickOutside);
  }, [isMoreMenuOpen]);

  return (
    <div className="min-h-screen bg-dark-primary">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-dark-border/70 bg-gradient-to-r from-dark-primary/95 via-dark-secondary/90 to-dark-primary/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-lg shadow-primary-900/30 transition-transform group-hover:-translate-y-0.5">
              <span className="text-white font-bold text-xl">N</span>
            </div>
            <div>
              <span className="text-xl font-semibold text-dark-50">NewsReader</span>
              <p className="text-xs text-dark-400">Curate smarter. Read faster.</p>
            </div>
          </Link>

          {isAuthenticated && (
            <div className="flex items-center space-x-4">
              <nav className="hidden lg:flex items-center space-x-2 px-2 py-1.5 rounded-full border border-dark-border/60 bg-dark-secondary/60 backdrop-blur-sm shadow-inner shadow-black/20">
                {primaryLinks.map((link) => {
                  const isActive =
                    location.pathname === link.to ||
                    (link.to !== '/' && location.pathname.startsWith(link.to));
                  return (
                    <Link
                      key={link.id}
                      to={link.to}
                      className={clsx(
                        'relative flex items-center space-x-1 rounded-full px-3 py-1.5 text-sm transition-all',
                        isActive
                          ? 'bg-primary-500/20 text-primary-300 shadow-sm shadow-primary-900/20'
                          : 'text-dark-400 hover:text-primary-200 hover:bg-dark-tertiary/80'
                      )}
                    >
                      <span className={clsx('transition-transform', isActive && '-translate-y-0.5')}>
                        {link.icon}
                      </span>
                      <span className="font-medium">{link.label}</span>
                      {isActive && (
                        <span className="absolute -bottom-[5px] left-1/2 h-[2px] w-6 -translate-x-1/2 rounded-full bg-primary-400" />
                      )}
                    </Link>
                  );
                })}
                <div className="relative" data-more-menu>
                  <button
                    type="button"
                    onClick={() => setIsMoreMenuOpen((value) => !value)}
                    className={clsx(
                      'flex items-center space-x-1 rounded-full border px-3 py-1.5 text-sm transition-all',
                      isMoreMenuOpen
                        ? 'border-primary-500/40 text-primary-300 bg-primary-500/15 shadow-sm shadow-primary-900/30'
                        : 'border-dark-border/70 text-dark-400 hover:text-primary-200 hover:border-primary-400/50'
                    )}
                    aria-expanded={isMoreMenuOpen}
                  >
                    <span>More</span>
                    <Bars3Icon className="w-4 h-4" />
                  </button>

                  {isMoreMenuOpen && (
                    <div className="absolute right-0 mt-3 w-60 rounded-xl border border-dark-border/70 bg-dark-primary/95 shadow-2xl shadow-black/50 backdrop-blur-lg">
                      <div className="px-4 pt-4 pb-2 text-xs uppercase tracking-widest text-dark-500">
                        Explore more
                      </div>
                      <div className="py-2">
                        {secondaryLinks.map((link) => {
                          const isActive =
                            location.pathname === link.to ||
                            (location.pathname.startsWith(link.to) && link.to !== '/');
                          return (
                            <Link
                              key={link.id}
                              to={link.to}
                              className={clsx(
                                'flex items-center space-x-3 px-4 py-2 text-sm transition-all',
                                isActive
                                  ? 'bg-primary-500/15 text-primary-300'
                                  : 'text-dark-400 hover:text-primary-200 hover:bg-dark-secondary/80'
                              )}
                            >
                              <span className="w-8 h-8 rounded-lg bg-dark-tertiary/80 flex items-center justify-center">
                                {link.icon}
                              </span>
                              <span className="font-medium">{link.label}</span>
                            </Link>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </nav>

              <button
                type="button"
                onClick={() => openPalette()}
                className="hidden md:inline-flex items-center space-x-2 rounded-full border border-dark-border/60 px-3 py-2 text-sm text-dark-400 transition-all hover:border-primary-500/60 hover:text-primary-300 hover:bg-primary-500/10"
              >
                <MagnifyingGlassIcon className="w-5 h-5" />
                <span>Quick search</span>
                <span className="hidden lg:inline-flex items-center space-x-1 text-[11px] font-mono text-dark-500">
                  <span className="rounded bg-dark-secondary px-1.5 py-0.5">⌘/Ctrl</span>
                  <span className="rounded bg-dark-secondary px-1.5 py-0.5">K</span>
                </span>
              </button>

              <button
                type="button"
                onClick={handleAddFeed}
                className="hidden md:inline-flex items-center space-x-2 rounded-full bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-primary-900/30 transition-transform hover:-translate-y-0.5"
              >
                <PlusCircleIcon className="w-5 h-5" />
                <span>Add Feed</span>
              </button>

              <button
                onClick={toggleTheme}
                className="p-2 text-dark-600 hover:text-primary-500 transition-colors"
                title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              >
                {theme === 'dark' ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
              </button>

              <button
                onClick={handleLogout}
                className="hidden md:inline-flex items-center space-x-2 rounded-full border border-dark-border/50 px-3 py-2 text-sm text-dark-400 transition-all hover:text-primary-300 hover:border-primary-500/60"
              >
                <ArrowRightOnRectangleIcon className="w-5 h-5" />
                <span>Logout</span>
              </button>

              <button
                type="button"
                onClick={() => setIsMobileMenuOpen((value) => !value)}
                className="lg:hidden inline-flex items-center justify-center rounded-lg border border-dark-border p-2 text-dark-600 hover:text-primary-400"
                aria-expanded={isMobileMenuOpen}
              >
                <Bars3Icon className="w-6 h-6" />
              </button>
            </div>
          )}
        </div>

        {isAuthenticated && isMobileMenuOpen && (
          <div className="border-t border-dark-border bg-dark-primary lg:hidden">
            <div className="container mx-auto px-4 py-4 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {navigationLinks.map((link) => (
                  <Link
                    key={link.id}
                    to={link.to}
                    className="flex items-center space-x-2 rounded-lg border border-dark-border px-3 py-2 text-dark-600 hover:border-primary-500/50 hover:text-primary-400 transition-colors"
                  >
                    {link.icon}
                    <span>{link.label}</span>
                  </Link>
                ))}
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={() => openPalette()}
                  className="flex-1 min-w-[160px] rounded-lg border border-dark-border px-3 py-2 text-left text-dark-500 hover:border-primary-500/50 hover:text-primary-400"
                >
                  ⌘/Ctrl + K to search
                </button>
                <button
                  type="button"
                  onClick={handleAddFeed}
                  className="btn-primary flex-1 min-w-[160px] inline-flex items-center justify-center space-x-2"
                >
                  <PlusCircleIcon className="w-5 h-5" />
                  <span>Add Feed</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="btn-secondary flex-1 min-w-[160px] inline-flex items-center justify-center space-x-2"
                >
                  <ArrowRightOnRectangleIcon className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">{children}</main>

      {/* Footer */}
      <footer className="glass-effect border-t border-dark-border mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-dark-500 text-sm">
          <p>NewsReader - AI-Powered News Aggregator</p>
        </div>
      </footer>
    </div>
  );
};
