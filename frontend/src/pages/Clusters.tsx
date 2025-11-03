import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { articlesApi } from '../api/articles';
import { Layout } from '../components/Layout';
import { ArticleCard } from '../components/ArticleCard';
import type { Article } from '../types';

export const Clusters: React.FC = () => {
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);

  const { data: clusterData, isLoading: clustersLoading } = useQuery({
    queryKey: ['cluster-analytics'],
    queryFn: articlesApi.getClusterAnalytics,
  });

  const { data: clusterArticles, isLoading: articlesLoading } = useQuery({
    queryKey: ['cluster-articles', selectedCluster],
    queryFn: async () => {
      if (!selectedCluster) return [];
      // Fetch all articles and filter by cluster
      const allArticles = await articlesApi.list({ limit: 500 });
      return allArticles.filter((a: Article) => a.cluster_id === selectedCluster);
    },
    enabled: selectedCluster !== null,
  });

  const sortedClusters = clusterData?.clusters || [];

  // Get sample topics from a cluster
  const getClusterTopics = (articleIds: number[], allArticles?: Article[]): string[] => {
    if (!allArticles) return [];
    const clusterArticles = allArticles.filter(a => articleIds.includes(a.id));
    const allTopics: string[] = [];
    clusterArticles.forEach(article => {
      if (article.topics) {
        allTopics.push(...article.topics);
      }
    });
    // Get most common topics
    const topicCounts = allTopics.reduce((acc, topic) => {
      acc[topic] = (acc[topic] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    return Object.entries(topicCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([topic]) => topic);
  };

  // Fetch all articles to get topics
  const { data: allArticles } = useQuery({
    queryKey: ['all-articles'],
    queryFn: () => articlesApi.list({ limit: 500 }),
  });

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-dark-700">Article Clusters</h1>
          <p className="text-dark-500 mt-2">
            Articles grouped by content similarity using NLP clustering
          </p>
        </div>

        {/* Loading state */}
        {clustersLoading && (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-dark-500 mt-4">Loading clusters...</p>
          </div>
        )}

        {/* Cluster Grid */}
        {!clustersLoading && sortedClusters.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedClusters.map((cluster) => (
              <button
                key={cluster.cluster_id}
                onClick={() => setSelectedCluster(cluster.cluster_id)}
                className={`card text-left transition-all hover:scale-105 ${
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
                <p className="text-sm text-dark-500">
                  {cluster.article_count} {cluster.article_count === 1 ? 'article' : 'articles'}
                </p>
                <div className="mt-3 flex flex-wrap gap-1">
                  {getClusterTopics(cluster.article_ids, allArticles).map((topic) => (
                    <span
                      key={topic}
                      className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400"
                    >
                      {topic}
                    </span>
                  ))}
                  {getClusterTopics(cluster.article_ids, allArticles).length === 0 && (
                    <span className="text-xs text-dark-500">No topics</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!clustersLoading && sortedClusters.length === 0 && (
          <div className="card text-center py-12">
            <div className="text-6xl mb-4">🔗</div>
            <p className="text-dark-500 text-lg">No clusters found</p>
            <p className="text-dark-400 mt-2">
              Run the clustering process to group similar articles together
            </p>
          </div>
        )}

        {/* Selected Cluster Articles */}
        {selectedCluster !== null && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-dark-700">
                Cluster {selectedCluster} Articles
              </h2>
              <button
                onClick={() => setSelectedCluster(null)}
                className="text-sm text-dark-500 hover:text-dark-700 transition-colors"
              >
                Clear selection
              </button>
            </div>

            {articlesLoading && (
              <div className="text-center py-8">
                <div className="inline-block w-6 h-6 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-dark-500 mt-2">Loading articles...</p>
              </div>
            )}

            {!articlesLoading && clusterArticles && clusterArticles.length > 0 && (
              <div className="space-y-4">
                {clusterArticles.map((article: Article) => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                    onRead={() => {}}
                    onBookmark={() => {}}
                  />
                ))}
              </div>
            )}

            {!articlesLoading && clusterArticles && clusterArticles.length === 0 && (
              <div className="card text-center py-8">
                <p className="text-dark-500">No articles found in this cluster</p>
              </div>
            )}
          </div>
        )}

        {/* Cluster Info */}
        {!clustersLoading && sortedClusters.length > 0 && (
          <div className="card">
            <h2 className="text-xl font-semibold text-dark-700 mb-4">About Clustering</h2>
            <div className="space-y-3 text-dark-600">
              <p>
                Articles are automatically grouped into clusters based on content similarity using
                natural language processing (NLP).
              </p>
              <p>
                Each cluster contains articles that share similar topics, themes, or subject matter.
                This helps you discover related content and identify trending stories.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="bg-dark-secondary rounded-lg p-4">
                  <div className="text-2xl font-bold text-primary-500">
                    {sortedClusters.length}
                  </div>
                  <div className="text-sm text-dark-500 mt-1">Total Clusters</div>
                </div>
                <div className="bg-dark-secondary rounded-lg p-4">
                  <div className="text-2xl font-bold text-primary-500">
                    {sortedClusters.reduce((sum, c) => sum + c.article_count, 0)}
                  </div>
                  <div className="text-sm text-dark-500 mt-1">Clustered Articles</div>
                </div>
                <div className="bg-dark-secondary rounded-lg p-4">
                  <div className="text-2xl font-bold text-primary-500">
                    {sortedClusters.length > 0
                      ? Math.round(
                          sortedClusters.reduce((sum, c) => sum + c.article_count, 0) /
                            sortedClusters.length
                        )
                      : 0}
                  </div>
                  <div className="text-sm text-dark-500 mt-1">Avg. Cluster Size</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
