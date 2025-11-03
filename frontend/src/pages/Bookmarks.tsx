import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { articlesApi } from '../api/articles';
import { ArticleCard } from '../components/ArticleCard';
import { Layout } from '../components/Layout';
import { SkeletonLoader } from '../components/SkeletonLoader';
import { BookmarkIcon } from '@heroicons/react/24/outline';

export const Bookmarks: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles', 'bookmarked'],
    queryFn: () => articlesApi.list({
      limit: 100,
      bookmarked_only: true,
    }),
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

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <BookmarkIcon className="h-8 w-8 text-primary-500" />
            <h1 className="text-3xl font-bold text-dark-700">Bookmarked Articles</h1>
          </div>
          <div className="text-sm text-dark-500">
            {articles?.length || 0} bookmarked articles
          </div>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <SkeletonLoader key={i} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!isLoading && articles?.length === 0 && (
          <div className="text-center py-12">
            <BookmarkIcon className="h-16 w-16 text-dark-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-dark-600 mb-2">No bookmarked articles</h3>
            <p className="text-dark-500">Articles you bookmark will appear here</p>
          </div>
        )}

        {/* Articles list */}
        {!isLoading && articles && articles.length > 0 && (
          <div className="space-y-4">
            {articles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onRead={(id) => markReadMutation.mutate(id)}
                onBookmark={(id) => bookmarkMutation.mutate(id)}
              />
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};
