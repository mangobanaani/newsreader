import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { articlesApi } from '../api/articles';
import { ArticleCard } from '../components/ArticleCard';
import { Layout } from '../components/Layout';

export const Recommendations: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: recommendations, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => articlesApi.getRecommendations(20),
  });

  const markReadMutation = useMutation({
    mutationFn: articlesApi.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });

  const bookmarkMutation = useMutation({
    mutationFn: articlesApi.toggleBookmark,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-dark-700">AI Recommendations</h1>
          <p className="text-dark-500 mt-2">
            Articles curated just for you based on your reading preferences
          </p>
        </div>

        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-dark-500 mt-4">Generating recommendations...</p>
          </div>
        )}

        {recommendations && recommendations.length > 0 && (
          <div className="space-y-4">
            {recommendations.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onRead={(id) => markReadMutation.mutate(id)}
                onBookmark={(id) => bookmarkMutation.mutate(id)}
                showRecommendation
              />
            ))}
          </div>
        )}

        {recommendations && recommendations.length === 0 && (
          <div className="card text-center py-12">
            <p className="text-dark-500 text-lg">No recommendations available</p>
            <p className="text-dark-400 mt-2">
              Read and rate some articles to get personalized recommendations
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};
