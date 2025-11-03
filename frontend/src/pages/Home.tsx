import React, { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import clsx from 'clsx';
import { useNavigate } from 'react-router-dom';
import { articlesApi } from '../api/articles';
import { feedsApi } from '../api/feeds';
import { ArticleCard } from '../components/ArticleCard';
import { Layout } from '../components/Layout';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { usePersistentState } from '../hooks/usePersistentState';
import type { CommandPaletteItem } from '../contexts/CommandPaletteContext';
import { useCommandPalette } from '../contexts/CommandPaletteContext';
import {
  FunnelIcon,
  ArrowPathIcon,
  ViewColumnsIcon,
  QueueListIcon,
  ArrowsPointingInIcon,
  PlusCircleIcon,
} from '@heroicons/react/24/outline';

type ViewMode = 'cards' | 'list' | 'focus';

export const Home: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { registerCommands, openPalette } = useCommandPalette();

  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [sentimentRange, setSentimentRange] = useState<[number, number]>([-1, 1]);
  const [sortBy, setSortBy] = useState<'date' | 'sentiment'>('date');
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = usePersistentState<ViewMode>('newsreader:view-mode', 'cards');
  const [allExpanded, setAllExpanded] = useState<boolean>(viewMode !== 'list');

  useEffect(() => {
    setAllExpanded(viewMode !== 'list');
  }, [viewMode]);

  const getSentimentParams = () => {
    const [min, max] = sentimentRange;
    const params: { min_sentiment?: number; max_sentiment?: number } = {};

    if (min > -1) params.min_sentiment = min;
    if (max < 1) params.max_sentiment = max;

    return params;
  };

  const hasActiveFilters = selectedTopic || sentimentRange[0] > -1 || sentimentRange[1] < 1 || sortBy !== 'date';
  const activeFilterCount = [
    selectedTopic ? 1 : 0,
    sentimentRange[0] > -1 || sentimentRange[1] < 1 ? 1 : 0,
    sortBy !== 'date' ? 1 : 0,
  ].reduce((acc, curr) => acc + curr, 0);

  const viewOptions: Array<{ id: ViewMode; label: string; Icon: React.ElementType }> = [
    { id: 'cards', label: 'Grid', Icon: ViewColumnsIcon },
    { id: 'list', label: 'List', Icon: QueueListIcon },
    { id: 'focus', label: 'Focus', Icon: ArrowsPointingInIcon },
  ];

  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles', selectedTopic, sentimentRange, sortBy],
    queryFn: () =>
      articlesApi.list({
        limit: 50,
        topic: selectedTopic || undefined,
        sort_by: sortBy,
        ...getSentimentParams(),
      }),
  });

  const { data: topics } = useQuery({
    queryKey: ['topics'],
    queryFn: articlesApi.getTopics,
  });

  const refreshMutation = useMutation({
    mutationFn: feedsApi.refreshAll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
    },
  });

  const markReadMutation = useMutation({
    mutationFn: articlesApi.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
    },
  });

  const bookmarkMutation = useMutation({
    mutationFn: articlesApi.toggleBookmark,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
    },
  });

  const topTopics = useMemo(() => {
    if (!topics) return [];
    return Object.entries(topics)
      .map(([topic, count]) => ({ topic, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [topics]);

  const resetFilters = () => {
    setSelectedTopic('');
    setSentimentRange([-1, 1]);
    setSortBy('date');
    setShowFilters(false);
  };

  const filterCommands = useMemo(() => {
    const commandItems: CommandPaletteItem[] = [];

    topTopics.slice(0, 8).forEach(({ topic, count }) => {
      commandItems.push({
        id: `topic-${topic}`,
        title: `Filter by topic: ${topic}`,
        subtitle: `${count} articles`,
        group: 'Topics',
        keywords: [topic],
        action: () => {
          setSelectedTopic(topic);
          setShowFilters(false);
        },
      });
    });

    (articles || []).slice(0, 15).forEach((article) => {
      let subtitle = 'Open article';
      try {
        subtitle = new URL(article.link).hostname;
      } catch {
        // Ignore malformed URLs
      }

      commandItems.push({
        id: `article-${article.id}`,
        title: article.title,
        subtitle,
        group: 'Articles',
        keywords: [article.title, ...(article.topics || []), article.author || ''].filter(Boolean),
        action: () => {
          window.open(article.link, '_blank', 'noopener,noreferrer');
        },
      });
    });

    return commandItems;
  }, [articles, topTopics]);

  useEffect(() => {
    if (filterCommands.length === 0) return;
    return registerCommands(filterCommands);
  }, [filterCommands, registerCommands]);

  const FiltersCard = () => (
    <div className="card space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-dark-700">Filter Articles</h2>
          <p className="text-sm text-dark-500">Quickly jump to the stories that matter.</p>
        </div>
        {hasActiveFilters && (
          <button onClick={resetFilters} className="text-sm text-primary-500 hover:text-primary-400 transition-colors">
            Clear all
          </button>
        )}
      </div>

      {topTopics.length > 0 && (
        <div>
          <div className="flex items-center justify-between text-sm text-dark-500 mb-2">
            <span>Trending topics</span>
            {selectedTopic && (
              <button onClick={() => setSelectedTopic('')} className="text-xs text-primary-500 hover:text-primary-400">
                Reset topic
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {topTopics.map(({ topic, count }) => (
              <button
                key={topic}
                onClick={() => {
                  setSelectedTopic((current) => (current === topic ? '' : topic));
                  setShowFilters(false);
                }}
                className={clsx(
                  'rounded-full border px-3 py-1.5 text-sm transition-colors',
                  selectedTopic === topic
                    ? 'border-primary-500 bg-primary-500/10 text-primary-400'
                    : 'border-dark-border text-dark-500 hover:border-primary-500/50 hover:text-primary-400'
                )}
              >
                {topic}{' '}
                <span className="text-xs text-dark-400">
                  ({count})
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-dark-600 mb-2">Topic</label>
          <select
            value={selectedTopic}
            onChange={(e) => {
              setSelectedTopic(e.target.value);
              setShowFilters(false);
            }}
            className="w-full bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Topics</option>
            {topics &&
              Object.entries(topics)
                .slice(0, 50)
                .map(([topic, count]) => (
                  <option key={topic} value={topic}>
                    {topic} ({count})
                  </option>
                ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-600 mb-2">Sort By</label>
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value as 'date' | 'sentiment');
              setShowFilters(false);
            }}
            className="w-full bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="date">Date (Newest First)</option>
            <option value="sentiment">Sentiment (Most Positive First)</option>
          </select>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-dark-600">Sentiment Range</label>
          <span className="text-sm text-dark-500">
            {sentimentRange[0].toFixed(2)} to {sentimentRange[1].toFixed(2)}
          </span>
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between text-xs text-dark-500 mb-1">
              <span>Min: {sentimentRange[0].toFixed(2)}</span>
              <span className="text-dark-400">
                {sentimentRange[0] >= 0.5
                  ? '😊 Very Positive'
                  : sentimentRange[0] >= 0.05
                  ? '🙂 Positive'
                  : sentimentRange[0] <= -0.5
                  ? '😢 Very Negative'
                  : sentimentRange[0] <= -0.05
                  ? '😟 Negative'
                  : '😐 Neutral'}
              </span>
            </div>
            <input
              type="range"
              min="-1"
              max="1"
              step="0.05"
              value={sentimentRange[0]}
              onChange={(e) => {
                const newMin = parseFloat(e.target.value);
                setSentimentRange([newMin, Math.max(newMin, sentimentRange[1])]);
              }}
              className="w-full h-2 bg-dark-tertiary rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between text-xs text-dark-500 mb-1">
              <span>Max: {sentimentRange[1].toFixed(2)}</span>
              <span className="text-dark-400">
                {sentimentRange[1] >= 0.5
                  ? '😊 Very Positive'
                  : sentimentRange[1] >= 0.05
                  ? '🙂 Positive'
                  : sentimentRange[1] <= -0.5
                  ? '😢 Very Negative'
                  : sentimentRange[1] <= -0.05
                  ? '😟 Negative'
                  : '😐 Neutral'}
              </span>
            </div>
            <input
              type="range"
              min="-1"
              max="1"
              step="0.05"
              value={sentimentRange[1]}
              onChange={(e) => {
                const newMax = parseFloat(e.target.value);
                setSentimentRange([Math.min(newMax, sentimentRange[0]), newMax]);
              }}
              className="w-full h-2 bg-dark-tertiary rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
          </div>

          <div className="relative h-8 bg-gradient-to-r from-red-500 via-gray-400 to-green-500 rounded-lg overflow-hidden">
            <div
              className="absolute top-0 bottom-0 bg-dark-primary/80 backdrop-blur-sm"
              style={{ left: 0, right: `${((1 - sentimentRange[0]) / 2) * 100}%` }}
            />
            <div
              className="absolute top-0 bottom-0 bg-dark-primary/80 backdrop-blur-sm"
              style={{ left: `${((sentimentRange[1] + 1) / 2) * 100}%`, right: 0 }}
            />
            <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
              {sentimentRange[0] === -1 && sentimentRange[1] === 1 ? 'All Sentiments' : 'Selected Range'}
            </div>
          </div>
        </div>
      </div>

    </div>
  );

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-dark-700">Your Feed</h1>
            <p className="text-dark-500 mt-2">Stay on top of every story with tailored filters and quick actions.</p>
          </div>
          <div className="flex items-center flex-wrap gap-3">
            <div className="flex items-center rounded-lg border border-dark-border p-1">
              {viewOptions.map(({ id, label, Icon }) => (
                <button
                  key={id}
                  onClick={() => setViewMode(id)}
                  className={clsx(
                    'flex items-center space-x-2 rounded-md px-3 py-2 text-sm transition-colors',
                    viewMode === id ? 'bg-primary-500/10 text-primary-400' : 'text-dark-500 hover:text-primary-400 hover:bg-dark-tertiary'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span>{label}</span>
                </button>
              ))}
            </div>

            <button
              onClick={() => setAllExpanded(!allExpanded)}
              className="px-4 py-2 rounded-lg transition-all flex items-center space-x-2 bg-dark-tertiary hover:bg-dark-secondary text-dark-700"
              title={allExpanded ? 'Switch to condensed view' : 'Expand all summaries'}
            >
              {allExpanded ? (
                <>
                  <QueueListIcon className="h-5 w-5" />
                  <span>Headlines</span>
                </>
              ) : (
                <>
                  <ViewColumnsIcon className="h-5 w-5" />
                  <span>Expand all</span>
                </>
              )}
            </button>

            <button
              onClick={() => setShowFilters((value) => !value)}
              className={clsx(
                'px-4 py-2 rounded-lg transition-all flex items-center space-x-2',
                hasActiveFilters
                  ? 'bg-primary-600/20 border border-primary-500/50 text-primary-400'
                  : 'bg-dark-tertiary hover:bg-dark-secondary text-dark-700'
              )}
            >
              <FunnelIcon className="h-5 w-5" />
              <span>
                Filters
                {activeFilterCount > 0 && ` (${activeFilterCount})`}
              </span>
            </button>

            <button
              onClick={() => refreshMutation.mutate()}
              disabled={refreshMutation.isPending}
              className="btn-primary flex items-center space-x-2"
            >
              <ArrowPathIcon className={clsx('w-5 h-5', refreshMutation.isPending && 'animate-spin')} />
              <span>{refreshMutation.isPending ? 'Refreshing...' : 'Refresh All Feeds'}</span>
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {showFilters && (
            <div className="max-w-3xl animate-fade-in">
              <FiltersCard />
            </div>
          )}

          {hasActiveFilters && (
            <div className="card flex flex-wrap items-center gap-3 text-sm text-dark-500">
              {selectedTopic && (
                <span className="inline-flex items-center space-x-1 rounded-full bg-primary-500/10 px-3 py-1 text-primary-400">
                  <span>Topic:</span>
                  <span className="font-medium">{selectedTopic}</span>
                </span>
              )}
              {(sentimentRange[0] > -1 || sentimentRange[1] < 1) && (
                <span className="inline-flex items-center space-x-1 rounded-full bg-dark-tertiary px-3 py-1">
                  <span>Sentiment:</span>
                  <span className="font-medium">
                    {sentimentRange[0].toFixed(2)} to {sentimentRange[1].toFixed(2)}
                  </span>
                </span>
              )}
              {sortBy !== 'date' && (
                <span className="inline-flex items-center space-x-1 rounded-full bg-dark-tertiary px-3 py-1">
                  <span>Sorted by</span>
                  <span className="font-medium">sentiment</span>
                </span>
              )}
              <button onClick={resetFilters} className="ml-auto text-primary-500 hover:text-primary-400 text-sm">
                Clear
              </button>
            </div>
          )}

          {isLoading && (
            <div className="space-y-4">
              <SkeletonLoader type="article" count={5} />
            </div>
          )}

          {articles && articles.length > 0 && (
            <div
              className={clsx(
                'gap-4',
                viewMode === 'cards' && 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3',
                viewMode === 'list' && 'space-y-2',
                viewMode === 'focus' && 'space-y-4 max-w-3xl mx-auto'
              )}
            >
              {articles.map((article, index) => (
                <div
                  key={article.id}
                  className={clsx('animate-fade-in', viewMode === 'cards' ? '' : 'col-span-full')}
                  style={{ animationDelay: `${index * 40}ms` }}
                >
                  <ArticleCard
                    article={article}
                    onRead={(id) => markReadMutation.mutate(id)}
                    onBookmark={(id) => bookmarkMutation.mutate(id)}
                    defaultExpanded={viewMode === 'list' ? false : allExpanded}
                    viewMode={viewMode}
                  />
                </div>
              ))}
            </div>
          )}

          {articles && articles.length === 0 && !isLoading && (
            <div className="card text-center py-12 space-y-4">
              <h2 className="text-xl font-semibold text-dark-600">No articles match your view yet</h2>
              <p className="text-dark-400">Try widening your filters or add new feeds to bring in fresh stories.</p>
              <div className="flex flex-wrap justify-center gap-3 pt-2">
                <button onClick={() => setShowFilters(true)} className="btn-secondary">
                  Adjust filters
                </button>
                <button onClick={() => navigate('/feeds?add=1')} className="btn-primary flex items-center space-x-2">
                  <PlusCircleIcon className="w-5 h-5" />
                  <span>Add a feed</span>
                </button>
                <button
                  onClick={() => openPalette({ query: 'topic' })}
                  className="px-4 py-2 rounded-lg text-sm text-primary-400 hover:text-primary-300 transition-colors"
                >
                  Open command palette (⌘/Ctrl + K)
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};
