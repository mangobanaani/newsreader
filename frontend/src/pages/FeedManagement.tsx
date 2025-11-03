import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { feedsApi } from '../api/feeds';
import { Layout } from '../components/Layout';
import { FeedLibrary } from '../components/FeedLibrary';
import { EditFeedModal } from '../components/EditFeedModal';
import type { Feed, FeedCreate } from '../types';

export const FeedManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const [editingFeed, setEditingFeed] = useState<Feed | null>(null);

  const { data: feeds, isLoading } = useQuery({
    queryKey: ['feeds'],
    queryFn: feedsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: (data: FeedCreate) => feedsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<FeedCreate> }) => feedsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
      setEditingFeed(null);
    },
  });

  const refreshMutation = useMutation({
    mutationFn: (id: number) => feedsApi.refresh(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'], refetchType: 'active' });
      queryClient.invalidateQueries({ queryKey: ['articles'], refetchType: 'active' });
    },
  });

  const refreshAllMutation = useMutation({
    mutationFn: feedsApi.refreshAll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'], refetchType: 'active' });
      queryClient.invalidateQueries({ queryKey: ['articles'], refetchType: 'active' });
    },
  });

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-dark-700">Feed Library</h1>
            <p className="text-dark-500 mt-2">Browse and manage your RSS feeds</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => refreshAllMutation.mutate()}
              disabled={refreshAllMutation.isPending}
              className="btn-secondary"
            >
              {refreshAllMutation.isPending ? 'Refreshing...' : 'Refresh All'}
            </button>
          </div>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-dark-500 mt-4">Loading feeds...</p>
          </div>
        )}

        {/* Feed Library - Main View */}
        {!isLoading && (
          <FeedLibrary
            feeds={feeds}
            onSelectFeed={(feed) => {
              // Directly add the feed instead of showing the form
              createMutation.mutate({
                url: feed.url,
                title: feed.name,
                description: feed.description,
                country_code: feed.country,
              });
            }}
            activeFeedUrls={feeds?.filter(f => f.is_active).map(f => f.url) || []}
            inactiveFeedUrls={feeds?.filter(f => !f.is_active).map(f => f.url) || []}
            onRemoveFeed={(url) => {
              const feedToDeactivate = feeds?.find(f => f.url === url);
              if (feedToDeactivate && window.confirm(`Deactivate feed "${feedToDeactivate.title || url}"?\n\nThis will stop fetching new articles but keep existing ones.`)) {
                updateMutation.mutate({ id: feedToDeactivate.id, data: { title: feedToDeactivate.title || undefined } });
              }
            }}
            onReactivate={(url) => {
              const feedToReactivate = feeds?.find(f => f.url === url);
              if (feedToReactivate) {
                updateMutation.mutate({ id: feedToReactivate.id, data: { title: feedToReactivate.title || undefined } });
              }
            }}
            onEdit={(feed) => setEditingFeed(feed)}
            onRefresh={(feedId) => refreshMutation.mutate(feedId)}
            isAdding={createMutation.isPending}
            isRefreshing={refreshMutation.isPending}
          />
        )}

        {/* Edit Feed Modal */}
        {editingFeed && (
          <EditFeedModal
            feed={editingFeed}
            isOpen={true}
            onClose={() => setEditingFeed(null)}
            onSave={(id, updates) => updateMutation.mutate({ id, data: updates })}
            isSaving={updateMutation.isPending}
          />
        )}
      </div>
    </Layout>
  );
};
