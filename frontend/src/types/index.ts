export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface Feed {
  id: number;
  url: string;
  title: string | null;
  description: string | null;
  country_code: string | null;
  last_fetched: string | null;
  is_active: boolean;
  user_id: number;
}

export interface Article {
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
}

export interface ArticleWithRecommendation extends Article {
  recommendation_score: number;
  recommendation_reason: string | null;
}

export interface ArticleLLMInsights {
  summary: string;
  key_points: string[];
  reliability_score: number | null;
  reliability_label: string | null;
  reliability_reason: string | null;
  tone: string | null;
  suggested_actions: string[];
}

export interface UserPreference {
  id: number;
  user_id: number;
  preferred_topics: string[];
  excluded_topics: string[];
  preferred_sources: string[];
  excluded_sources: string[];
  excluded_words: string[];
  enable_recommendations: boolean;
  min_relevance_score: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface FeedCreate {
  url: string;
  title?: string;
  description?: string;
  country_code?: string;
}
