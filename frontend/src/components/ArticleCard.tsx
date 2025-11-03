import React, { useEffect, useMemo, useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import clsx from 'clsx';
import {
  ChevronDownIcon,
  ChevronUpIcon,
  ArrowTopRightOnSquareIcon,
  ClockIcon,
  CheckIcon,
  GlobeAltIcon,
  ExclamationTriangleIcon,
  BookOpenIcon,
  PaintBrushIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import type { Article, ArticleLLMInsights, ArticleWithRecommendation } from '../types';
import { articlesApi } from '../api/articles';
import { ENABLE_LLM_FEATURES } from '../utils/featureFlags';

type ArticleCardViewMode = 'cards' | 'list' | 'focus';

interface ArticleCardProps {
  article: Article | ArticleWithRecommendation;
  onRead?: (id: number) => void;
  onBookmark?: (id: number) => void;
  showRecommendation?: boolean;
  defaultExpanded?: boolean;
  viewMode?: ArticleCardViewMode;
}

const stripHtml = (value: string) => value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

const getSummary = (article: Article) => {
  const source = article.content || article.description;
  if (!source) return null;
  const clean = stripHtml(source);
  if (!clean) return null;
  const sentenceMatch = clean.match(/(.+?[.!?])(\s|$)/);
  const snippet = sentenceMatch ? sentenceMatch[1] : clean.slice(0, 240);
  return snippet.length > 200 ? `${snippet.slice(0, 200)}...` : snippet;
};

const getSentimentInfo = (score: number | null) => {
  if (score === null) return null;

  if (score >= 0.5) {
    return { label: 'Positive', color: 'bg-green-500/20 text-green-400 border-green-500/50', icon: '😊' };
  } else if (score >= 0.05) {
    return { label: 'Slightly Positive', color: 'bg-green-500/10 text-green-300 border-green-500/30', icon: '🙂' };
  } else if (score <= -0.5) {
    return { label: 'Negative', color: 'bg-red-500/20 text-red-400 border-red-500/50', icon: '😢' };
  } else if (score <= -0.05) {
    return { label: 'Slightly Negative', color: 'bg-red-500/10 text-red-300 border-red-500/30', icon: '😟' };
  } else {
    return { label: 'Neutral', color: 'bg-gray-500/10 text-gray-300 border-gray-500/40', icon: '😐' };
  }
};

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onRead,
  onBookmark,
  showRecommendation = false,
  defaultExpanded = true,
  viewMode = 'cards',
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [showInsights, setShowInsights] = useState(false);
  const [isInsightsLoading, setIsInsightsLoading] = useState(false);
  const [insights, setInsights] = useState<ArticleLLMInsights | null>(null);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  useEffect(() => {
    setIsExpanded(defaultExpanded);
  }, [defaultExpanded]);

  const hasRecommendation = 'recommendation_score' in article;
  const recommendationArticle = hasRecommendation ? (article as ArticleWithRecommendation) : null;

  const timeAgo = article.published_date
    ? formatDistanceToNow(new Date(article.published_date), { addSuffix: true })
    : null;

  const sentimentInfo = getSentimentInfo(article.sentiment_score);

  const summary = useMemo(() => getSummary(article), [article]);

  const readingStats = useMemo(() => {
    const text = stripHtml(article.content || article.description || '');
    if (!text) return null;
    const words = text.split(/\s+/).filter(Boolean).length;
    if (!words) return null;
    const minutes = Math.max(1, Math.round(words / 220));
    return { words, minutes };
  }, [article.content, article.description]);

  const sourceDomain = useMemo(() => {
    try {
      return new URL(article.link).hostname.replace(/^www\./, '');
    } catch {
      return null;
    }
  }, [article.link]);

  const isCompact = viewMode === 'list';
  const isFocus = viewMode === 'focus';

  const insightBadges = [
    sourceDomain && {
      id: 'source',
      content: (
        <span className="inline-flex items-center space-x-1">
          <GlobeAltIcon className="w-4 h-4" />
          <span>{sourceDomain}</span>
        </span>
      ),
    },
    timeAgo && { id: 'time', content: timeAgo },
    readingStats && {
      id: 'reading',
      content: (
        <span className="inline-flex items-center space-x-1">
          <ClockIcon className="w-4 h-4" />
          <span>{readingStats.minutes} min read</span>
        </span>
      ),
    },
    article.is_bookmarked && { id: 'bookmark', content: '★ Saved' },
    article.cluster_id && {
      id: 'cluster',
      content: (
        <span className="inline-flex items-center space-x-1">
          <ExclamationTriangleIcon className="w-4 h-4" />
          <span>Duplicate watch</span>
        </span>
      ),
    },
    article.readability_label && article.readability_score !== null && {
      id: 'readability',
      content: (
        <span className="inline-flex items-center space-x-1">
          <BookOpenIcon className="w-4 h-4" />
          <span>
            {article.readability_label}
            <span className="text-dark-400"> ({Math.round(article.readability_score)})</span>
          </span>
        </span>
      ),
    },
    article.writing_style && {
      id: 'style',
      content: (
        <span className="inline-flex items-center space-x-1">
          <PaintBrushIcon className="w-4 h-4" />
          <span>{article.writing_style}</span>
        </span>
      ),
    },
  ].filter(Boolean) as Array<{ id: string; content: React.ReactNode }>;

  const fetchInsights = async () => {
    if (!ENABLE_LLM_FEATURES) return;

    if (insights || isInsightsLoading) {
      setShowInsights((prev) => !prev);
      return;
    }

    setIsInsightsLoading(true);
    setInsightsError(null);
    try {
      const data = await articlesApi.getLLMInsights(article.id);
      setInsights(data);
      setShowInsights(true);
    } catch {
      setInsightsError('Unable to generate AI insights right now.');
      setShowInsights(true);
    } finally {
      setIsInsightsLoading(false);
    }
  };

  return (
    <article
      className={clsx(
        'card relative group overflow-hidden transition-all duration-300',
        isCompact ? 'p-4' : 'p-6',
        isFocus && 'shadow-xl border border-dark-border/60',
        article.is_read ? 'opacity-60' : 'hover:shadow-lg hover:-translate-y-0.5'
      )}
    >
      {showRecommendation && recommendationArticle && (
        <div className="absolute top-4 right-4">
          <div className="flex items-center space-x-2 bg-primary-600/20 border border-primary-500/50 rounded-full px-3 py-1">
            <span className="text-primary-400 text-xs font-medium">
              {Math.round(recommendationArticle.recommendation_score * 100)}% match
            </span>
          </div>
        </div>
      )}

      <div className="absolute top-3 right-3 hidden md:flex items-center gap-2 rounded-full border border-dark-border/60 bg-dark-primary/90 px-3 py-1.5 text-xs text-dark-400 opacity-0 backdrop-blur transition-all group-hover:opacity-100 group-hover:-translate-y-1">
        <a
          href={article.link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1 hover:text-primary-400 transition-colors"
          title="Open original article"
        >
          <ArrowTopRightOnSquareIcon className="w-4 h-4" />
          <span>Open</span>
        </a>
        {onRead && !article.is_read && (
          <button
            onClick={() => onRead(article.id)}
            className="inline-flex items-center space-x-1 hover:text-primary-400 transition-colors"
            title="Mark as read"
          >
            <CheckIcon className="w-4 h-4" />
            <span>Read</span>
          </button>
        )}
        {onBookmark && (
          <button
            onClick={() => onBookmark(article.id)}
            className="inline-flex items-center space-x-1 hover:text-primary-400 transition-colors"
            title={article.is_bookmarked ? 'Remove bookmark' : 'Bookmark article'}
          >
            <BookmarkSolidIcon
              className={clsx('w-4 h-4', article.is_bookmarked ? 'text-primary-400' : 'text-dark-400')}
            />
            <span>{article.is_bookmarked ? 'Saved' : 'Save'}</span>
          </button>
        )}
      </div>

      <div className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 space-y-2">
            {insightBadges.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 text-xs text-dark-400">
                {insightBadges.map((badge) => (
                  <span key={badge.id} className="inline-flex items-center space-x-1 rounded-full bg-dark-tertiary px-3 py-1">
                    {badge.content}
                  </span>
                ))}
              </div>
            )}

            <h3
              className={clsx(
                'text-dark-700 font-semibold transition-colors',
                isCompact ? 'text-lg' : 'text-xl'
              )}
            >
              <a
                href={article.link}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
              >
                {article.title}
              </a>
            </h3>

            {summary && (
              <p
                className={clsx(
                  'text-dark-500',
                  isCompact ? 'text-sm line-clamp-2' : 'text-base leading-relaxed line-clamp-3'
                )}
              >
                {summary}
              </p>
            )}
          </div>
          <button
            onClick={() => setIsExpanded((prev) => !prev)}
            className="flex-shrink-0 p-1 text-dark-500 hover:text-dark-700 hover:bg-dark-tertiary rounded transition-colors"
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? <ChevronUpIcon className="w-5 h-5" /> : <ChevronDownIcon className="w-5 h-5" />}
          </button>
        </div>

        {isExpanded && (
          <div className="space-y-4 animate-fade-in">
            {article.description && (
              <p className={clsx('text-dark-500', isCompact ? 'text-sm leading-relaxed' : 'text-base leading-7')}>
                {stripHtml(article.description)}
              </p>
            )}

            {showRecommendation && recommendationArticle?.recommendation_reason && (
              <div className="bg-primary-900/20 border border-primary-800/30 rounded-lg p-3">
                <p className="text-sm text-primary-400">
                  <span className="font-medium">Why recommended:</span>{' '}
                  {recommendationArticle.recommendation_reason}
                </p>
              </div>
            )}

            <div className="flex flex-wrap items-center gap-3 text-sm text-dark-500">
              {article.author && <span>{article.author}</span>}
              {timeAgo && <span>• {timeAgo}</span>}
              {readingStats && <span>• {readingStats.words.toLocaleString()} words</span>}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {sentimentInfo && (
                <div
                  className={clsx(
                    'flex items-center space-x-2 border rounded-full px-3 py-1 text-xs font-medium',
                    sentimentInfo.color
                  )}
                >
                  <span>{sentimentInfo.icon}</span>
                  <span>
                    {sentimentInfo.label} ({(article.sentiment_score! * 100).toFixed(0)}%)
                  </span>
                </div>
              )}

              {article.topics && article.topics.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  {article.topics.slice(0, 6).map((topic, idx) => (
                    <span
                      key={idx}
                      className="bg-primary-900/20 border border-primary-800/30 px-2 py-1 rounded text-xs text-primary-400"
                    >
                      {topic}
                    </span>
                  ))}
                  {article.topics.length > 6 && (
                    <span className="text-xs text-dark-500">
                      +{article.topics.length - 6} more
                    </span>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center flex-wrap gap-4 pt-2">
              <a
                href={article.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary-500 hover:text-primary-400 transition-colors"
              >
              Read original
              </a>

              {onRead && (
                <button
                  onClick={() => onRead(article.id)}
                  className={clsx(
                    'text-sm transition-colors',
                    article.is_read ? 'text-primary-500' : 'text-dark-500 hover:text-primary-500'
                  )}
                >
                  {article.is_read ? 'Marked as read' : 'Mark as read'}
                </button>
              )}

              {onBookmark && (
                <button
                  onClick={() => onBookmark(article.id)}
                  className={clsx(
                    'text-sm transition-colors flex items-center space-x-1',
                    article.is_bookmarked
                      ? 'text-primary-500'
                      : 'text-dark-500 hover:text-primary-500'
                  )}
                >
                  <BookmarkSolidIcon className={clsx('w-4 h-4', article.is_bookmarked ? 'text-primary-500' : 'text-dark-400')} />
                  <span>{article.is_bookmarked ? 'Bookmarked' : 'Bookmark'}</span>
                </button>
              )}

              {ENABLE_LLM_FEATURES && (
                <button
                  onClick={fetchInsights}
                  disabled={isInsightsLoading}
                  className={clsx(
                    'text-sm inline-flex items-center space-x-1 rounded-full border px-3 py-1.5 transition-colors',
                    showInsights
                      ? 'border-primary-500/40 text-primary-400 bg-primary-500/10'
                      : 'border-dark-border text-dark-500 hover:text-primary-400 hover:border-primary-500/40'
                  )}
                >
                  <SparklesIcon className={clsx('w-4 h-4', isInsightsLoading && 'animate-pulse')} />
                  <span>{isInsightsLoading ? 'Fetching...' : showInsights ? 'Hide AI Insights' : 'AI Insights'}</span>
                </button>
              )}
            </div>

            {ENABLE_LLM_FEATURES && showInsights && (
              <div className="mt-4 rounded-lg border border-dark-border/70 bg-dark-secondary/60 p-4 space-y-3">
                {isInsightsLoading && (
                  <div className="flex items-center space-x-2 text-sm text-dark-500">
                    <div className="h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                    <span>Generating insights...</span>
                  </div>
                )}

                {!isInsightsLoading && insightsError && (
                  <p className="text-sm text-red-400">{insightsError}</p>
                )}

                {!isInsightsLoading && insights && (
                  <div className="space-y-3 text-sm text-dark-400">
                    <div>
                      <h4 className="text-dark-200 font-semibold mb-1">AI Summary</h4>
                      <p>{insights.summary}</p>
                    </div>

                    {insights.key_points.length > 0 && (
                      <div>
                        <h5 className="text-dark-200 font-semibold mb-1">Key Points</h5>
                        <ul className="list-disc list-inside space-y-1">
                          {insights.key_points.map((point, index) => (
                            <li key={index}>{point}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {(insights.reliability_label || insights.reliability_reason) && (
                      <div className="rounded-md bg-dark-tertiary/80 border border-dark-border/70 p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs uppercase tracking-wide text-dark-500">Reliability</span>
                          {insights.reliability_score !== null && (
                            <span className="text-xs text-dark-500">{Math.round(insights.reliability_score * 100)}%</span>
                          )}
                        </div>
                        {insights.reliability_label && (
                          <p className="text-sm font-semibold text-primary-300 mt-1">
                            {insights.reliability_label}
                          </p>
                        )}
                        {insights.reliability_reason && (
                          <p className="text-xs text-dark-400 mt-1">{insights.reliability_reason}</p>
                        )}
                      </div>
                    )}

                    {(insights.tone || insights.suggested_actions.length > 0) && (
                      <div className="flex flex-col gap-2">
                        {insights.tone && (
                          <div className="text-xs text-dark-500">
                            <span className="font-semibold text-dark-200">Tone:</span> {insights.tone}
                          </div>
                        )}
                        {insights.suggested_actions.length > 0 && (
                          <div>
                            <h5 className="text-xs font-semibold uppercase tracking-wide text-dark-500 mb-1">
                              Suggested Follow-ups
                            </h5>
                            <ul className="text-xs space-y-1">
                              {insights.suggested_actions.map((action, index) => (
                                <li key={index} className="flex items-start gap-2">
                                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-primary-400" />
                                  <span>{action}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </article>
  );
};
