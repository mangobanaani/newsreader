import type { Page, Route } from '@playwright/test';

const apiBase = 'http://localhost:8000/api/v1';

type Article = {
  id: number;
  feed_id: number;
  title: string;
  link: string;
  description: string | null;
  content: string | null;
  author: string | null;
  published_date: string | null;
  created_at: string;
  cluster_id: number | null;
  sentiment_score: number | null;
  topics: string[] | null;
  readability_score: number | null;
  readability_label: string | null;
  writing_style: string | null;
  is_read: boolean;
  is_bookmarked: boolean;
  user_rating: number | null;
};

type ArticleWithRecommendation = Article & {
  recommendation_score: number;
  recommendation_reason: string | null;
};

type Feed = {
  id: number;
  url: string;
  title: string | null;
  description: string | null;
  country_code: string | null;
  last_fetched: string | null;
  is_active: boolean;
  user_id: number;
};

type UserPreference = {
  id: number;
  user_id: number;
  preferred_topics: string[];
  excluded_topics: string[];
  preferred_sources: string[];
  excluded_sources: string[];
  excluded_words: string[];
  enable_recommendations: boolean;
  min_relevance_score: number;
};

interface MockContext {
  articles: Article[];
  recommendations: ArticleWithRecommendation[];
  feeds: Feed[];
  preferences: UserPreference;
  topics: Record<string, number>;
  sentimentAnalytics: {
    positive: number;
    slightly_positive: number;
    neutral: number;
    slightly_negative: number;
    negative: number;
    total: number;
    daily_trends: Record<string, { positive: number; neutral: number; negative: number }>;
  };
  topicTrends: {
    trending_topics: Array<{ topic: string; count: number; growth: number }>;
  };
  clusterAnalytics: {
    clusters: Array<{ cluster_id: number; article_count: number; article_ids: number[] }>;
  };
}

const now = new Date();
const iso = (date: Date) => date.toISOString();

const defaultContext: MockContext = {
  articles: [
    {
      id: 1,
      feed_id: 1,
      title: 'AI Breakthrough in Helsinki',
      link: 'https://example.com/ai-helsinki',
      description: 'Researchers in Finland announce a major AI milestone.',
      content:
        '<p>Researchers at the University of Helsinki have unveiled a groundbreaking AI model that significantly improves energy efficiency in data centers.</p>',
      author: 'News Desk',
      published_date: iso(new Date(now.getTime() - 1000 * 60 * 60)),
      created_at: iso(new Date(now.getTime() - 1000 * 60 * 60)),
      cluster_id: 1,
      sentiment_score: 0.72,
      topics: ['AI', 'Technology', 'Finland'],
      readability_score: 68,
      readability_label: 'Accessible',
      writing_style: 'Analytical',
      is_read: false,
      is_bookmarked: true,
      user_rating: null,
    },
    {
      id: 2,
      feed_id: 2,
      title: 'Nordic Climate Summit Highlights',
      link: 'https://example.com/climate-summit',
      description: 'Leaders set new targets for sustainable energy adoption.',
      content:
        '<p>The Nordic Climate Summit concluded with ambitious goals for renewable energy adoption across the region.</p>',
      author: 'Climate Correspondent',
      published_date: iso(new Date(now.getTime() - 1000 * 60 * 60 * 6)),
      created_at: iso(new Date(now.getTime() - 1000 * 60 * 60 * 6)),
      cluster_id: 2,
      sentiment_score: 0.12,
      topics: ['Climate', 'Policy'],
      readability_score: 62,
      readability_label: 'Accessible',
      writing_style: 'Informative',
      is_read: true,
      is_bookmarked: false,
      user_rating: null,
    },
    {
      id: 3,
      feed_id: 1,
      title: 'Startup Ecosystem Thrives in Espoo',
      link: 'https://example.com/espoo-startups',
      description: 'Innovative companies attract international investment.',
      content:
        '<p>Espoo continues to cement its position as a leading hub for tech innovation, with startups securing record funding in Q1.</p>',
      author: 'Business Reporter',
      published_date: iso(new Date(now.getTime() - 1000 * 60 * 60 * 24)),
      created_at: iso(new Date(now.getTime() - 1000 * 60 * 60 * 24)),
      cluster_id: 1,
      sentiment_score: 0.45,
      topics: ['Business', 'Startups', 'Finland'],
      readability_score: 74,
      readability_label: 'Clear',
      writing_style: 'Optimistic',
      is_read: false,
      is_bookmarked: false,
      user_rating: 4.5,
    },
  ],
  recommendations: [
    {
      id: 4,
      feed_id: 3,
      title: 'AI Ethics Panel Releases New Guidelines',
      link: 'https://example.com/ai-ethics',
      description: 'Experts outline responsible AI deployment practices.',
      content:
        '<p>A coalition of Nordic universities has released a comprehensive set of guidelines to ensure responsible AI deployment.</p>',
      author: 'Tech Ethics Board',
      published_date: iso(new Date(now.getTime() - 1000 * 60 * 45)),
      created_at: iso(new Date(now.getTime() - 1000 * 60 * 45)),
      cluster_id: 3,
      sentiment_score: 0.33,
      topics: ['AI', 'Policy'],
      readability_score: 70,
      readability_label: 'Clear',
      writing_style: 'Objective',
      is_read: false,
      is_bookmarked: false,
      user_rating: null,
      recommendation_score: 0.92,
      recommendation_reason: 'Matches your interest in AI governance',
    },
  ],
  feeds: [
    {
      id: 1,
      url: 'https://yle.fi/rss/uutiset/tuoreimmat',
      title: 'Yle Uutiset',
      description: 'Latest Finnish news from Yle',
      country_code: 'FI',
      last_fetched: iso(new Date(now.getTime() - 1000 * 60 * 12)),
      is_active: true,
      user_id: 1,
    },
    {
      id: 2,
      url: 'https://www.hs.fi/rss/talous.xml',
      title: 'Helsingin Sanomat Talous',
      description: 'Business coverage from HS',
      country_code: 'FI',
      last_fetched: iso(new Date(now.getTime() - 1000 * 60 * 90)),
      is_active: false,
      user_id: 1,
    },
  ],
  preferences: {
    id: 1,
    user_id: 1,
    preferred_topics: ['AI', 'Technology'],
    excluded_topics: ['Politics'],
    preferred_sources: ['Yle Uutiset'],
    excluded_sources: [],
    excluded_words: [],
    enable_recommendations: true,
    min_relevance_score: 0.6,
  },
  topics: {
    AI: 12,
    Technology: 9,
    Finland: 7,
    Business: 5,
    Climate: 3,
  },
  sentimentAnalytics: {
    positive: 6,
    slightly_positive: 4,
    neutral: 3,
    slightly_negative: 1,
    negative: 0,
    total: 14,
    daily_trends: {
      [iso(new Date(now.getTime() - 1000 * 60 * 60 * 24)).slice(0, 10)]: { positive: 2, neutral: 1, negative: 0 },
      [iso(new Date(now.getTime() - 1000 * 60 * 60 * 12)).slice(0, 10)]: { positive: 3, neutral: 1, negative: 0 },
      [iso(new Date(now.getTime() - 1000 * 60 * 60 * 3)).slice(0, 10)]: { positive: 1, neutral: 1, negative: 0 },
    },
  },
  topicTrends: {
    trending_topics: [
      { topic: 'AI', count: 12, growth: 28 },
      { topic: 'Climate', count: 5, growth: 12 },
      { topic: 'Startups', count: 4, growth: 18 },
    ],
  },
  clusterAnalytics: {
    clusters: [
      { cluster_id: 1, article_count: 2, article_ids: [1, 3] },
      { cluster_id: 2, article_count: 1, article_ids: [2] },
    ],
  },
};

const fulfillJson = (route: Route, payload: unknown, status = 200) => {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(payload),
  });
};

export async function setupApiMocks(page: Page, overrides?: Partial<MockContext>) {
  const context: MockContext = {
    ...defaultContext,
    ...overrides,
  };

  const articleState = new Map<number, Article>(
    context.articles.map((article) => [article.id, { ...article }]),
  );

  const recommendationState = context.recommendations.map((article) => ({ ...article }));

  const feedState = new Map<number, Feed>(context.feeds.map((feed) => [feed.id, { ...feed }]));
  let preferencesState: UserPreference = { ...context.preferences };

  const getArticlesList = (searchParams: URLSearchParams) => {
    let articles = Array.from(articleState.values());
    if (searchParams.get('bookmarked_only') === 'true') {
      articles = articles.filter((article) => article.is_bookmarked);
    }
    if (searchParams.get('unread_only') === 'true') {
      articles = articles.filter((article) => !article.is_read);
    }
    const topic = searchParams.get('topic');
    if (topic) {
      articles = articles.filter((article) => article.topics?.includes(topic));
    }
    return articles;
  };

  await page.route(`${apiBase}/**`, (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const pathname = url.pathname.replace('/api/v1', '');
    const method = request.method();

    if (pathname === '/articles/' && method === 'GET') {
      return fulfillJson(route, getArticlesList(url.searchParams));
    }

    if (pathname === '/articles/recommendations' && method === 'GET') {
      return fulfillJson(route, recommendationState);
    }

    if (pathname === '/articles/topics/all' && method === 'GET') {
      return fulfillJson(route, context.topics);
    }

    if (pathname === '/articles/analytics/sentiment' && method === 'GET') {
      return fulfillJson(route, context.sentimentAnalytics);
    }

    if (pathname === '/articles/analytics/topics' && method === 'GET') {
      return fulfillJson(route, context.topicTrends);
    }

    if (pathname === '/articles/analytics/clusters' && method === 'GET') {
      return fulfillJson(route, context.clusterAnalytics);
    }

    if (/^\/articles\/\d+\/read$/.test(pathname) && method === 'POST') {
      const id = Number.parseInt(pathname.match(/\/articles\/(\d+)\/read$/)?.[1] ?? '', 10);
      const article = articleState.get(id);
      if (!article) {
        return fulfillJson(route, { detail: 'Article not found' }, 404);
      }
      article.is_read = true;
      articleState.set(article.id, { ...article });
      return fulfillJson(route, article);
    }

    if (/^\/articles\/\d+\/bookmark$/.test(pathname) && method === 'POST') {
      const id = Number.parseInt(pathname.match(/\/articles\/(\d+)\/bookmark$/)?.[1] ?? '', 10);
      const article = articleState.get(id);
      if (!article) {
        return fulfillJson(route, { detail: 'Article not found' }, 404);
      }
      article.is_bookmarked = !article.is_bookmarked;
      articleState.set(article.id, { ...article });
      return fulfillJson(route, article);
    }

    if (pathname === '/feeds/' && method === 'GET') {
      return fulfillJson(route, Array.from(feedState.values()));
    }

    if (pathname === '/feeds/' && method === 'POST') {
      const body = request.postDataJSON() as Partial<Feed>;
      const nextId = feedState.size
        ? Math.max(...Array.from(feedState.keys())) + 1
        : 1;
      const newFeed: Feed = {
        id: nextId,
        url: body.url ?? `https://example.com/feed-${nextId}`,
        title: (body.title as string | undefined) ?? `Feed ${nextId}`,
        description: (body.description as string | undefined) ?? null,
        country_code: (body.country_code as string | undefined) ?? null,
        last_fetched: iso(now),
        is_active: true,
        user_id: 1,
      };
      feedState.set(nextId, newFeed);
      return fulfillJson(route, newFeed, 201);
    }

    if (/^\/feeds\/\d+$/.test(pathname) && method === 'PUT') {
      const id = Number.parseInt(pathname.match(/\/feeds\/(\d+)$/)?.[1] ?? '', 10);
      const feed = feedState.get(id);
      if (!feed) {
        return fulfillJson(route, { detail: 'Feed not found' }, 404);
      }
      const body = request.postDataJSON() as Partial<Feed>;
      const updated: Feed = { ...feed, ...body };
      feedState.set(id, updated);
      return fulfillJson(route, updated);
    }

    if (/^\/feeds\/\d+$/.test(pathname) && method === 'DELETE') {
      const id = Number.parseInt(pathname.match(/\/feeds\/(\d+)$/)?.[1] ?? '', 10);
      feedState.delete(id);
      return fulfillJson(route, {});
    }

    if (/^\/feeds\/\d+\/refresh$/.test(pathname) && method === 'POST') {
      return fulfillJson(route, { new_articles: 4 });
    }

    if (pathname === '/feeds/refresh-all' && method === 'POST') {
      return fulfillJson(route, { new_articles: 9, errors: 0, feeds_updated: 2 });
    }

    if (pathname === '/preferences/' && method === 'GET') {
      return fulfillJson(route, preferencesState);
    }

    if (pathname === '/preferences/' && method === 'PUT') {
      const body = request.postDataJSON() as Partial<UserPreference>;
      preferencesState = { ...preferencesState, ...body };
      return fulfillJson(route, preferencesState);
    }

    if (pathname === '/auth/login' && method === 'POST') {
      return fulfillJson(route, { access_token: 'test-token', token_type: 'bearer' });
    }

    return route.continue();
  });

  return {
    articleState,
    feedState,
    recommendationState,
    preferencesState,
  };
}
