import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ArticleCard } from './ArticleCard';
import { Article } from '../types';

const mockArticle: Article = {
  id: 1,
  title: 'Test Article Title',
  link: 'https://example.com/article',
  description: 'This is a test article description',
  content: 'Full article content here',
  author: 'Test Author',
  published_date: new Date('2025-01-01T12:00:00Z'),
  feed_id: 1,
  created_at: new Date('2025-01-01T12:00:00Z'),
  cluster_id: null,
  sentiment_score: 0.5,
  topics: ['technology', 'ai'],
  readability_score: 60,
  readability_label: 'Standard',
  writing_style: 'Formal',
  is_read: false,
  is_bookmarked: false,
  user_rating: null,
};

describe('ArticleCard', () => {
  it('renders article title', () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.getByText('Test Article Title')).toBeInTheDocument();
  });

  it('renders article description when provided', () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.getByText('This is a test article description')).toBeInTheDocument();
  });

  it('renders article author when provided', () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.getByText(/Test Author/i)).toBeInTheDocument();
  });

  it('renders topics when provided', () => {
    render(<ArticleCard article={mockArticle} />);
    expect(screen.getByText('technology')).toBeInTheDocument();
    expect(screen.getByText('ai')).toBeInTheDocument();
  });

  it('handles article without description', () => {
    const articleWithoutDesc = { ...mockArticle, description: null };
    render(<ArticleCard article={articleWithoutDesc} />);
    expect(screen.getByText('Test Article Title')).toBeInTheDocument();
  });

  it('handles article without author', () => {
    const articleWithoutAuthor = { ...mockArticle, author: null };
    render(<ArticleCard article={articleWithoutAuthor} />);
    expect(screen.getByText('Test Article Title')).toBeInTheDocument();
  });

  it('handles article without topics', () => {
    const articleWithoutTopics = { ...mockArticle, topics: null };
    render(<ArticleCard article={articleWithoutTopics} />);
    expect(screen.getByText('Test Article Title')).toBeInTheDocument();
  });
});
