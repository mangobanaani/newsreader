import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  AreaChart,
  Area,
  Legend,
} from 'recharts';
import { format, subDays } from 'date-fns';
import { articlesApi } from '../api/articles';
import { feedsApi } from '../api/feeds';
import { Layout } from '../components/Layout';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { ArticleCard } from '../components/ArticleCard';
import type { Article, Feed } from '../types';

type TimeRange = '7' | '30' | '90' | 'all';

interface DailyActivityPoint {
  dateKey: string;
  label: string;
  read: number;
  unread: number;
  total: number;
}

const timeRangeOptions: Array<{ value: TimeRange; label: string }> = [
  { value: '7', label: '7d' },
  { value: '30', label: '30d' },
  { value: '90', label: '90d' },
  { value: 'all', label: 'All' },
];

const parseArticleDate = (article: Article): Date | null => {
  const raw = article.published_date || article.created_at;
  if (!raw) {
    return null;
  }
  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

export const Analytics: React.FC = () => {
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('30');

  const { data: articles, isLoading: articlesLoading } = useQuery({
    queryKey: ['all-articles'],
    queryFn: () => articlesApi.list({ limit: 500 }),
  });

  const { data: feeds, isLoading: feedsLoading } = useQuery({
    queryKey: ['feeds'],
    queryFn: feedsApi.list,
  });

  const { data: sentimentAnalytics, isLoading: sentimentAnalyticsLoading } = useQuery({
    queryKey: ['sentiment-analytics'],
    queryFn: articlesApi.getSentimentAnalytics,
  });

  const topicTrendDays = timeRange === 'all' ? 90 : Number.parseInt(timeRange, 10);
  const { data: topicTrends } = useQuery({
    queryKey: ['topic-trends', topicTrendDays],
    queryFn: () => articlesApi.getTopicTrends(topicTrendDays),
  });

  const { data: clusterData } = useQuery({
    queryKey: ['cluster-analytics'],
    queryFn: articlesApi.getClusterAnalytics,
  });

  const { data: clusterArticles, isLoading: clusterArticlesLoading } = useQuery({
    queryKey: ['cluster-articles', selectedCluster],
    queryFn: async () => {
      if (!selectedCluster || !articles) return [];
      return articles.filter((article: Article) => article.cluster_id === selectedCluster);
    },
    enabled: selectedCluster !== null,
  });

  const timeRangeDays = timeRange === 'all' ? null : Number.parseInt(timeRange, 10);
  const cutoffDate = useMemo(() => {
    if (timeRangeDays === null) {
      return null;
    }
    const now = new Date();
    const endOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
    return subDays(endOfToday, timeRangeDays - 1);
  }, [timeRangeDays]);

  const filteredArticles = useMemo(() => {
    if (!articles) return [];
    return articles.filter((article) => {
      if (!cutoffDate) return true;
      const articleDate = parseArticleDate(article);
      if (!articleDate) return false;
      return articleDate >= cutoffDate;
    });
  }, [articles, cutoffDate]);

  const feedsById = useMemo(() => {
    if (!feeds) return new Map<number, Feed>();
    return new Map<number, Feed>(feeds.map((feed) => [feed.id, feed]));
  }, [feeds]);

  const engagement = useMemo(() => {
    if (!feeds || !articles) return null;

    let readCount = 0;
    let bookmarkCount = 0;
    let unreadCount = 0;
    const uniqueDaySet = new Set<string>();
    const topicCounts = new Map<string, number>();
    const feedTotals = new Map<number, { total: number; read: number; unread: number }>();
    const sentimentBuckets = {
      positive: 0,
      slightlyPositive: 0,
      neutral: 0,
      slightlyNegative: 0,
      negative: 0,
    };

    filteredArticles.forEach((article) => {
      if (article.is_read) {
        readCount += 1;
      } else {
        unreadCount += 1;
      }

      if (article.is_bookmarked) {
        bookmarkCount += 1;
      }

      const articleDate = parseArticleDate(article);
      if (articleDate) {
        uniqueDaySet.add(format(articleDate, 'yyyy-MM-dd'));
      }

      if (article.topics) {
        article.topics.forEach((topic) => {
          topicCounts.set(topic, (topicCounts.get(topic) || 0) + 1);
        });
      }

      const feedEntry = feedTotals.get(article.feed_id) || { total: 0, read: 0, unread: 0 };
      feedEntry.total += 1;
      if (article.is_read) {
        feedEntry.read += 1;
      } else {
        feedEntry.unread += 1;
      }
      feedTotals.set(article.feed_id, feedEntry);

      if (article.sentiment_score !== null && article.sentiment_score !== undefined) {
        const score = article.sentiment_score;
        if (score >= 0.5) {
          sentimentBuckets.positive += 1;
        } else if (score >= 0.05) {
          sentimentBuckets.slightlyPositive += 1;
        } else if (score <= -0.5) {
          sentimentBuckets.negative += 1;
        } else if (score <= -0.05) {
          sentimentBuckets.slightlyNegative += 1;
        } else {
          sentimentBuckets.neutral += 1;
        }
      }
    });

    const feedPerformance = Array.from(feedTotals.entries())
      .map(([feedId, stats]) => {
        const feed = feedsById.get(feedId);
        return {
          feedId,
          name: feed?.title || 'Untitled',
          active: feed?.is_active ?? false,
          total: stats.total,
          read: stats.read,
          unread: stats.unread,
          readRate: stats.total > 0 ? Math.round((stats.read / stats.total) * 100) : 0,
        };
      })
      .filter((item) => item.total > 0)
      .sort((a, b) => b.total - a.total)
      .slice(0, 10);

    const activeFeeds = feeds.filter((feed) => feed.is_active).length;
    const total = filteredArticles.length;
    const uniqueDays = uniqueDaySet.size || (timeRangeDays ?? 0);
    const averagePerDay = uniqueDays > 0 ? Math.round(total / uniqueDays) : total;

    const topTopics = Array.from(topicCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15)
      .map(([topic, count]) => ({ topic, count }));

    return {
      total,
      readCount,
      unreadCount,
      bookmarkCount,
      readRate: total > 0 ? Math.round((readCount / total) * 100) : 0,
      averagePerDay,
      activeFeeds,
      uniqueDays,
      topTopics,
      feedPerformance,
      fallbackSentiments: sentimentBuckets,
    };
  }, [articles, filteredArticles, feeds, feedsById, timeRangeDays]);

  const dailyActivity: DailyActivityPoint[] = useMemo(() => {
    if (!articles) return [];

    const countsMap = new Map<string, { read: number; unread: number; total: number }>();

    filteredArticles.forEach((article) => {
      const articleDate = parseArticleDate(article);
      if (!articleDate) return;
      const dateKey = format(articleDate, 'yyyy-MM-dd');
      const entry = countsMap.get(dateKey) || { read: 0, unread: 0, total: 0 };
      entry.total += 1;
      if (article.is_read) {
        entry.read += 1;
      } else {
        entry.unread += 1;
      }
      countsMap.set(dateKey, entry);
    });

    const points: DailyActivityPoint[] = [];

    if (timeRangeDays !== null) {
      for (let offset = timeRangeDays - 1; offset >= 0; offset -= 1) {
        const date = subDays(new Date(), offset);
        const dateKey = format(date, 'yyyy-MM-dd');
        const entry = countsMap.get(dateKey) || { read: 0, unread: 0, total: 0 };
        points.push({
          dateKey,
          label: timeRangeDays <= 30 ? format(date, 'MMM d') : format(date, 'MMM d'),
          read: entry.read,
          unread: entry.unread,
          total: entry.total,
        });
      }
    } else {
      const sortedKeys = Array.from(countsMap.keys()).sort();
      sortedKeys.forEach((key) => {
        const entry = countsMap.get(key)!;
        const date = new Date(`${key}T00:00:00`);
        points.push({
          dateKey: key,
          label: format(date, 'MMM d, yyyy'),
          read: entry.read,
          unread: entry.unread,
          total: entry.total,
        });
      });
    }

    return points;
  }, [articles, filteredArticles, timeRangeDays]);

  const longestReadStreak = useMemo(() => {
    if (dailyActivity.length === 0) return 0;
    let best = 0;
    let current = 0;
    let prevDate: Date | null = null;

    dailyActivity.forEach((day) => {
      const date = new Date(`${day.dateKey}T00:00:00`);
      if (prevDate) {
        const diff = Math.round((date.getTime() - prevDate.getTime()) / (1000 * 60 * 60 * 24));
        if (diff > 1) {
          current = 0;
        }
      }
      if (day.read > 0) {
        current += 1;
        best = Math.max(best, current);
      } else {
        current = 0;
      }
      prevDate = date;
    });

    return best;
  }, [dailyActivity]);

  const sentimentBuckets = useMemo(() => {
    const totals =
      sentimentAnalytics?.total ?? Object.values(engagement?.fallbackSentiments ?? {}).reduce((sum, value) => sum + value, 0);

    if (sentimentAnalytics && sentimentAnalytics.total > 0) {
      return [
        {
          id: 'positive',
          label: 'Positive',
          value: sentimentAnalytics.positive,
          description: 'Score ≥ 0.5',
          className: 'bg-green-500/20 border-green-500/40 text-green-400',
        },
        {
          id: 'slightlyPositive',
          label: 'Slightly Positive',
          value: sentimentAnalytics.slightly_positive,
          description: '0.05 — 0.49',
          className: 'bg-green-500/10 border-green-500/20 text-green-300',
        },
        {
          id: 'neutral',
          label: 'Neutral',
          value: sentimentAnalytics.neutral,
          description: 'Between -0.04 and 0.04',
          className: 'bg-gray-500/10 border-gray-500/20 text-gray-300',
        },
        {
          id: 'slightlyNegative',
          label: 'Slightly Negative',
          value: sentimentAnalytics.slightly_negative,
          description: '-0.49 — -0.06',
          className: 'bg-red-500/10 border-red-500/20 text-red-300',
        },
        {
          id: 'negative',
          label: 'Negative',
          value: sentimentAnalytics.negative,
          description: 'Score ≤ -0.5',
          className: 'bg-red-500/20 border-red-500/40 text-red-400',
        },
      ].map((bucket) => ({
        ...bucket,
        percent: totals > 0 ? Math.round((bucket.value / totals) * 100) : 0,
      }));
    }

    const fallback = engagement?.fallbackSentiments;
    if (!fallback) return [];

    return [
      {
        id: 'positive',
        label: 'Positive',
        value: fallback.positive,
        description: 'Score ≥ 0.5',
        className: 'bg-green-500/20 border-green-500/40 text-green-400',
      },
      {
        id: 'slightlyPositive',
        label: 'Slightly Positive',
        value: fallback.slightlyPositive,
        description: '0.05 — 0.49',
        className: 'bg-green-500/10 border-green-500/20 text-green-300',
      },
      {
        id: 'neutral',
        label: 'Neutral',
        value: fallback.neutral,
        description: 'Between -0.04 and 0.04',
        className: 'bg-gray-500/10 border-gray-500/20 text-gray-300',
      },
      {
        id: 'slightlyNegative',
        label: 'Slightly Negative',
        value: fallback.slightlyNegative,
        description: '-0.49 — -0.06',
        className: 'bg-red-500/10 border-red-500/20 text-red-300',
      },
      {
        id: 'negative',
        label: 'Negative',
        value: fallback.negative,
        description: 'Score ≤ -0.5',
        className: 'bg-red-500/20 border-red-500/40 text-red-400',
      },
    ].map((bucket) => ({
      ...bucket,
      percent: totals > 0 ? Math.round((bucket.value / totals) * 100) : 0,
    }));
  }, [engagement, sentimentAnalytics]);

  const sentimentTrendData = useMemo(() => {
    if (!sentimentAnalytics?.daily_trends) return [];
    const entries = Object.entries(sentimentAnalytics.daily_trends)
      .map(([dateKey, counts]) => {
        const date = new Date(dateKey);
        if (Number.isNaN(date.getTime())) return null;
        if (cutoffDate && date < cutoffDate) return null;
        return {
          fullDate: date,
          dateLabel: format(date, 'MMM d'),
          positive: counts.positive,
          neutral: counts.neutral,
          negative: counts.negative,
        };
      })
      .filter((item): item is { fullDate: Date; dateLabel: string; positive: number; neutral: number; negative: number } => !!item)
      .sort((a, b) => a.fullDate.getTime() - b.fullDate.getTime());

    return entries;
  }, [cutoffDate, sentimentAnalytics]);

  const trendingTopics = useMemo(() => {
    if (topicTrends?.trending_topics?.length) {
      return topicTrends.trending_topics.map((item) => ({
        topic: item.topic,
        count: item.count,
        growth: item.growth,
      }));
    }

    return engagement?.topTopics.slice(0, 8).map((item) => ({
      topic: item.topic,
      count: item.count,
      growth: null as number | null,
    })) ?? [];
  }, [engagement, topicTrends]);

  const topFeedsForChart = engagement?.feedPerformance.slice(0, 8) ?? [];

  const isLoading = articlesLoading || feedsLoading || sentimentAnalyticsLoading;
  const rangeLabel =
    timeRange === 'all'
      ? 'All-time trends'
      : `Last ${Number.parseInt(timeRange, 10)} days`;

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold text-dark-700">Analytics</h1>
            <p className="text-dark-500">
              {rangeLabel} across {engagement?.activeFeeds ?? 0} active feeds
            </p>
          </div>
          <div className="flex items-center gap-1 rounded-lg border border-dark-border bg-dark-secondary p-1">
            {timeRangeOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setTimeRange(option.value)}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  timeRange === option.value
                    ? 'bg-primary-600/20 text-primary-300 border border-primary-500/40'
                    : 'text-dark-500 hover:text-primary-300 hover:bg-dark-tertiary'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {isLoading && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <SkeletonLoader type="card" count={4} />
            </div>
            <SkeletonLoader type="chart" count={1} />
          </div>
        )}

        {!isLoading && engagement && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in">
              <div className="card">
                <div className="text-sm text-dark-500">Articles in view</div>
                <div className="text-3xl font-bold text-dark-700 mt-1">{engagement.total}</div>
                <div className="text-xs text-dark-500 mt-2">{rangeLabel}</div>
              </div>
              <div className="card">
                <div className="text-sm text-dark-500">Read rate</div>
                <div className="text-3xl font-bold text-primary-500 mt-1">
                  {engagement.readRate}%
                </div>
                <div className="text-xs text-dark-500 mt-2">
                  {engagement.readCount} read · {engagement.unreadCount} unread
                </div>
              </div>
              <div className="card">
                <div className="text-sm text-dark-500">Bookmarks</div>
                <div className="text-3xl font-bold text-yellow-400 mt-1">
                  {engagement.bookmarkCount}
                </div>
                <div className="text-xs text-dark-500 mt-2">Saved for later</div>
              </div>
              <div className="card">
                <div className="text-sm text-dark-500">Average / day</div>
                <div className="text-3xl font-bold text-dark-700 mt-1">
                  {engagement.averagePerDay}
                </div>
                <div className="text-xs text-dark-500 mt-2">
                  Longest read streak: {longestReadStreak} days
                </div>
              </div>
            </div>

            {dailyActivity.length > 0 && (
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-semibold text-dark-700">Reading activity</h2>
                    <p className="text-sm text-dark-500">
                      Daily read vs. unread articles
                    </p>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={320}>
                  <AreaChart data={dailyActivity}>
                    <defs>
                      <linearGradient id="readGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="unreadGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="label" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" allowDecimals={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937' }}
                      labelStyle={{ color: '#e5e7eb' }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="total"
                      stackId="1"
                      stroke="#10b981"
                      fillOpacity={0.2}
                      fill="#10b981"
                      name="Total"
                    />
                    <Area
                      type="monotone"
                      dataKey="read"
                      stackId="2"
                      stroke="#3b82f6"
                      fill="url(#readGradient)"
                      name="Read"
                    />
                    <Area
                      type="monotone"
                      dataKey="unread"
                      stackId="2"
                      stroke="#6366f1"
                      fill="url(#unreadGradient)"
                      name="Unread"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {sentimentBuckets.length > 0 && (
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-semibold text-dark-700">Sentiment overview</h2>
                    <p className="text-sm text-dark-500">
                      Tone of coverage across your feeds
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
                  {sentimentBuckets.map((bucket) => (
                    <div
                      key={bucket.id}
                      className={`rounded-lg border px-4 py-3 transition-colors ${bucket.className}`}
                    >
                      <div className="text-sm font-medium">{bucket.label}</div>
                      <div className="text-2xl font-semibold mt-1">{bucket.value}</div>
                      <div className="text-xs mt-1 opacity-80">{bucket.description}</div>
                      <div className="text-xs mt-2">
                        {bucket.percent}% of analysed articles
                      </div>
                    </div>
                  ))}
                </div>

                {sentimentTrendData.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-dark-500 mb-3">
                      Sentiment per day
                    </h3>
                    <ResponsiveContainer width="100%" height={260}>
                      <AreaChart data={sentimentTrendData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                        <XAxis dataKey="dateLabel" stroke="#9ca3af" />
                        <YAxis stroke="#9ca3af" allowDecimals={false} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937' }}
                          labelStyle={{ color: '#e5e7eb' }}
                        />
                        <Legend />
                        <Area
                          type="monotone"
                          dataKey="positive"
                          stackId="sentiment"
                          stroke="#22c55e"
                          fill="#22c55e40"
                          name="Positive"
                        />
                        <Area
                          type="monotone"
                          dataKey="neutral"
                          stackId="sentiment"
                          stroke="#6b7280"
                          fill="#6b728040"
                          name="Neutral"
                        />
                        <Area
                          type="monotone"
                          dataKey="negative"
                          stackId="sentiment"
                          stroke="#f87171"
                          fill="#f8717140"
                          name="Negative"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {topFeedsForChart.length > 0 && (
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-semibold text-dark-700">Feed performance</h2>
                      <p className="text-sm text-dark-500">Top sources by volume</p>
                    </div>
                  </div>
                  <ResponsiveContainer width="100%" height={320}>
                    <BarChart data={topFeedsForChart}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis
                        dataKey="name"
                        stroke="#9ca3af"
                        tickFormatter={(value: string) =>
                          value.length > 16 ? `${value.slice(0, 16)}...` : value
                        }
                      />
                      <YAxis stroke="#9ca3af" allowDecimals={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937' }}
                        labelStyle={{ color: '#e5e7eb' }}
                      />
                      <Legend />
                      <Bar dataKey="read" stackId="feed" fill="#3b82f6" name="Read" />
                      <Bar dataKey="unread" stackId="feed" fill="#6366f1" name="Unread" />
                    </BarChart>
                  </ResponsiveContainer>
                  <div className="mt-4 space-y-2 text-sm text-dark-500">
                    {topFeedsForChart.map((feed) => (
                      <div key={feed.feedId} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-dark-600">{feed.name}</span>
                          {!feed.active && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-dark-tertiary">
                              inactive
                            </span>
                          )}
                        </div>
                        <div>
                          {feed.total} articles · {feed.readRate}% read
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {trendingTopics.length > 0 && (
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-semibold text-dark-700">
                        Trending topics
                      </h2>
                      <p className="text-sm text-dark-500">
                        Subjects gaining momentum across your feeds
                      </p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    {trendingTopics.map((topic) => (
                      <div
                        key={topic.topic}
                        className="flex items-center justify-between rounded-lg border border-dark-border px-4 py-3 hover:border-primary-500/50 transition-colors"
                      >
                        <div>
                          <div className="font-medium text-dark-600">{topic.topic}</div>
                          <div className="text-xs text-dark-500">
                            {topic.count} mentions
                          </div>
                        </div>
                        <div
                          className={`text-sm font-medium ${
                            topic.growth === null
                              ? 'text-dark-500'
                              : topic.growth >= 0
                              ? 'text-green-400'
                              : 'text-red-400'
                          }`}
                        >
                          {topic.growth === null
                            ? '—'
                            : `${topic.growth >= 0 ? '+' : ''}${topic.growth}%`}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {engagement.topTopics.length > 0 && (
              <div className="card">
                <h2 className="text-xl font-semibold text-dark-700 mb-4">Top topics</h2>
                <div className="flex flex-wrap gap-3">
                  {engagement.topTopics.map((item) => (
                    <div
                      key={item.topic}
                      className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-dark-secondary border border-dark-tertiary hover:border-primary-500/50 transition-colors"
                    >
                      <span className="text-dark-700 font-medium">{item.topic}</span>
                      <span className="text-sm px-2 py-0.5 rounded-full bg-primary-600/20 text-primary-400">
                        {item.count}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {clusterData?.clusters?.length ? (
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-dark-700">Article clusters</h2>
                <p className="text-sm text-dark-500">
                  Similar stories grouped by semantic analysis
                </p>
              </div>
              <div className="flex items-center gap-6 text-sm text-dark-500">
                <div>
                  <span className="font-semibold text-dark-600">
                    {clusterData.clusters.length}
                  </span>{' '}
                  clusters
                </div>
                <div>
                  <span className="font-semibold text-dark-600">
                    {clusterData.clusters.reduce((sum, cluster) => sum + cluster.article_count, 0)}
                  </span>{' '}
                  articles
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {clusterData.clusters
                .slice()
                .sort((a, b) => b.article_count - a.article_count)
                .map((cluster) => {
                  const topics = getClusterTopics(cluster.article_ids, articles);
                  return (
                    <button
                      key={cluster.cluster_id}
                      type="button"
                      onClick={() =>
                        setSelectedCluster(
                          selectedCluster === cluster.cluster_id ? null : cluster.cluster_id
                        )
                      }
                      className={`card text-left transition-all hover:scale-[1.01] ${
                        selectedCluster === cluster.cluster_id
                          ? 'ring-2 ring-primary-500 bg-primary-600/10'
                          : 'hover:bg-dark-secondary'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold text-dark-700">
                          Cluster {cluster.cluster_id}
                        </h3>
                        <div className="w-10 h-10 rounded-full bg-primary-600/20 flex items-center justify-center">
                          <span className="text-primary-400 font-bold">
                            {cluster.article_count}
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {topics.length > 0 ? (
                          topics.map((topic) => (
                            <span
                              key={topic}
                              className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400"
                            >
                              {topic}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-dark-500">No topics yet</span>
                        )}
                      </div>
                    </button>
                  );
                })}
            </div>

            {selectedCluster !== null && (
              <div className="mt-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-dark-700">
                    Cluster {selectedCluster} articles
                  </h3>
                  <button
                    type="button"
                    onClick={() => setSelectedCluster(null)}
                    className="text-sm px-3 py-1.5 bg-dark-secondary hover:bg-dark-tertiary text-dark-700 rounded-lg transition-colors"
                  >
                    Close
                  </button>
                </div>

                {clusterArticlesLoading && (
                  <div className="text-center py-8">
                    <div className="inline-block w-6 h-6 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                    <p className="text-dark-500 mt-2">Loading articles...</p>
                  </div>
                )}

                {!clusterArticlesLoading && clusterArticles?.length ? (
                  <div className="space-y-4">
                    {clusterArticles.map((article) => (
                      <ArticleCard
                        key={article.id}
                        article={article}
                        defaultExpanded
                        viewMode="focus"
                      />
                    ))}
                  </div>
                ) : null}

                {!clusterArticlesLoading && clusterArticles?.length === 0 && (
                  <div className="text-center py-8 text-dark-500">
                    No articles found in this cluster
                  </div>
                )}
              </div>
            )}
          </div>
        ) : null}
      </div>
    </Layout>
  );
};

function getClusterTopics(articleIds: number[], articles: Article[] | undefined): string[] {
  if (!articles) return [];
  const topics: string[] = [];

  articleIds.forEach((articleId) => {
    const article = articles.find((item) => item.id === articleId);
    if (article?.topics) {
      topics.push(...article.topics);
    }
  });

  const topicCounts = topics.reduce((acc, topic) => {
    acc[topic] = (acc[topic] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return Object.entries(topicCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([topic]) => topic);
}
