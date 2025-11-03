import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { preferencesApi } from '../api/preferences';
import { articlesApi } from '../api/articles';
import { Layout } from '../components/Layout';
import { useTheme } from '../contexts/ThemeContext';

export const Preferences: React.FC = () => {
  const queryClient = useQueryClient();
  const { theme, toggleTheme } = useTheme();

  const [preferredTopics, setPreferredTopics] = useState<string[]>([]);
  const [excludedTopics, setExcludedTopics] = useState<string[]>([]);
  const [preferredSources, setPreferredSources] = useState<string[]>([]);
  const [excludedSources, setExcludedSources] = useState<string[]>([]);
  const [enableRecommendations, setEnableRecommendations] = useState(true);
  const [minRelevanceScore, setMinRelevanceScore] = useState(0.5);

  const [newPreferredTopic, setNewPreferredTopic] = useState('');
  const [newExcludedTopic, setNewExcludedTopic] = useState('');
  const [newPreferredSource, setNewPreferredSource] = useState('');
  const [newExcludedSource, setNewExcludedSource] = useState('');

  const { data: preferences, isLoading } = useQuery({
    queryKey: ['preferences'],
    queryFn: preferencesApi.get,
  });

  const { data: allTopics } = useQuery({
    queryKey: ['topics'],
    queryFn: articlesApi.getTopics,
  });

  useEffect(() => {
    if (preferences) {
      setPreferredTopics(preferences.preferred_topics || []);
      setExcludedTopics(preferences.excluded_topics || []);
      setPreferredSources(preferences.preferred_sources || []);
      setExcludedSources(preferences.excluded_sources || []);
      setEnableRecommendations(preferences.enable_recommendations);
      setMinRelevanceScore(preferences.min_relevance_score);
    }
  }, [preferences]);

  const updateMutation = useMutation({
    mutationFn: preferencesApi.update,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['preferences'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });

  const handleSave = () => {
    updateMutation.mutate({
      preferred_topics: preferredTopics,
      excluded_topics: excludedTopics,
      preferred_sources: preferredSources,
      excluded_sources: excludedSources,
      enable_recommendations: enableRecommendations,
      min_relevance_score: minRelevanceScore,
    });
  };

  const addPreferredTopic = () => {
    if (newPreferredTopic.trim() && !preferredTopics.includes(newPreferredTopic.trim())) {
      setPreferredTopics([...preferredTopics, newPreferredTopic.trim()]);
      setNewPreferredTopic('');
    }
  };

  const addExcludedTopic = () => {
    if (newExcludedTopic.trim() && !excludedTopics.includes(newExcludedTopic.trim())) {
      setExcludedTopics([...excludedTopics, newExcludedTopic.trim()]);
      setNewExcludedTopic('');
    }
  };

  const addPreferredSource = () => {
    if (newPreferredSource.trim() && !preferredSources.includes(newPreferredSource.trim())) {
      setPreferredSources([...preferredSources, newPreferredSource.trim()]);
      setNewPreferredSource('');
    }
  };

  const addExcludedSource = () => {
    if (newExcludedSource.trim() && !excludedSources.includes(newExcludedSource.trim())) {
      setExcludedSources([...excludedSources, newExcludedSource.trim()]);
      setNewExcludedSource('');
    }
  };

  const topTopics = allTopics ? Object.keys(allTopics).slice(0, 20) : [];

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-dark-700">Preferences & Settings</h1>
            <p className="text-dark-500 mt-2">Customize your news reading experience</p>
          </div>
          <button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="btn-primary"
          >
            {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        {updateMutation.isSuccess && (
          <div className="card bg-green-500/10 border border-green-500/50">
            <p className="text-green-400">Preferences saved successfully!</p>
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-dark-500 mt-4">Loading preferences...</p>
          </div>
        )}

        {!isLoading && (
          <div className="space-y-6">
            {/* Appearance Settings */}
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-700 mb-4">Appearance</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-dark-700">Theme</div>
                    <div className="text-sm text-dark-500 mt-1">
                      Choose between dark and light mode
                    </div>
                  </div>
                  <button
                    onClick={toggleTheme}
                    className="relative inline-flex items-center h-10 w-20 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 bg-dark-tertiary"
                  >
                    <span
                      className={`inline-block w-8 h-8 transform transition-transform rounded-full bg-primary-500 flex items-center justify-center ${
                        theme === 'dark' ? 'translate-x-1' : 'translate-x-11'
                      }`}
                    >
                      {theme === 'dark' ? '🌙' : '☀️'}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            {/* Recommendation Settings */}
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-700 mb-4">Recommendations</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-dark-700">Enable Recommendations</div>
                    <div className="text-sm text-dark-500 mt-1">
                      Get personalized article suggestions
                    </div>
                  </div>
                  <button
                    onClick={() => setEnableRecommendations(!enableRecommendations)}
                    className={`relative inline-flex items-center h-10 w-20 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                      enableRecommendations ? 'bg-primary-500' : 'bg-dark-tertiary'
                    }`}
                  >
                    <span
                      className={`inline-block w-8 h-8 transform transition-transform rounded-full bg-white ${
                        enableRecommendations ? 'translate-x-11' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="font-medium text-dark-700">
                      Minimum Relevance Score
                    </label>
                    <span className="text-sm text-dark-500">{minRelevanceScore.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={minRelevanceScore}
                    onChange={(e) => setMinRelevanceScore(parseFloat(e.target.value))}
                    disabled={!enableRecommendations}
                    className="w-full h-2 bg-dark-tertiary rounded-lg appearance-none cursor-pointer accent-primary-500 disabled:opacity-50"
                  />
                  <div className="flex justify-between text-xs text-dark-500 mt-1">
                    <span>Show all</span>
                    <span>Highly relevant only</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Preferred Topics */}
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-700 mb-4">Preferred Topics</h2>
              <p className="text-sm text-dark-500 mb-4">
                Articles about these topics will be prioritized in your feed
              </p>
              <div className="space-y-3">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newPreferredTopic}
                    onChange={(e) => setNewPreferredTopic(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addPreferredTopic()}
                    placeholder="Add a topic..."
                    className="flex-1 bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button onClick={addPreferredTopic} className="btn-primary">
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {preferredTopics.map((topic) => (
                    <span
                      key={topic}
                      className="px-3 py-1 bg-green-500/20 text-green-400 border border-green-500/50 rounded-full text-sm flex items-center space-x-2"
                    >
                      <span>{topic}</span>
                      <button
                        onClick={() =>
                          setPreferredTopics(preferredTopics.filter((t) => t !== topic))
                        }
                        className="hover:text-green-300"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                {topTopics.length > 0 && (
                  <div>
                    <p className="text-xs text-dark-500 mb-2">Quick add from your articles:</p>
                    <div className="flex flex-wrap gap-2">
                      {topTopics.map((topic) => (
                        <button
                          key={topic}
                          onClick={() => {
                            if (!preferredTopics.includes(topic)) {
                              setPreferredTopics([...preferredTopics, topic]);
                            }
                          }}
                          disabled={preferredTopics.includes(topic)}
                          className="text-xs px-2 py-1 bg-dark-tertiary hover:bg-dark-secondary text-dark-600 rounded disabled:opacity-50"
                        >
                          + {topic}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Excluded Topics */}
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-700 mb-4">Excluded Topics</h2>
              <p className="text-sm text-dark-500 mb-4">
                Articles about these topics will be filtered out
              </p>
              <div className="space-y-3">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newExcludedTopic}
                    onChange={(e) => setNewExcludedTopic(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addExcludedTopic()}
                    placeholder="Add a topic to exclude..."
                    className="flex-1 bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button onClick={addExcludedTopic} className="btn-primary">
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {excludedTopics.map((topic) => (
                    <span
                      key={topic}
                      className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/50 rounded-full text-sm flex items-center space-x-2"
                    >
                      <span>{topic}</span>
                      <button
                        onClick={() =>
                          setExcludedTopics(excludedTopics.filter((t) => t !== topic))
                        }
                        className="hover:text-red-300"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Preferred Sources */}
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-700 mb-4">Preferred Sources</h2>
              <p className="text-sm text-dark-500 mb-4">
                Prioritize articles from these sources (feed URLs or domains)
              </p>
              <div className="space-y-3">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newPreferredSource}
                    onChange={(e) => setNewPreferredSource(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addPreferredSource()}
                    placeholder="example.com or full feed URL..."
                    className="flex-1 bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button onClick={addPreferredSource} className="btn-primary">
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {preferredSources.map((source) => (
                    <span
                      key={source}
                      className="px-3 py-1 bg-primary-500/20 text-primary-400 border border-primary-500/50 rounded-full text-sm flex items-center space-x-2"
                    >
                      <span>{source}</span>
                      <button
                        onClick={() =>
                          setPreferredSources(preferredSources.filter((s) => s !== source))
                        }
                        className="hover:text-primary-300"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Excluded Sources */}
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-700 mb-4">Excluded Sources</h2>
              <p className="text-sm text-dark-500 mb-4">
                Block articles from these sources (feed URLs or domains)
              </p>
              <div className="space-y-3">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newExcludedSource}
                    onChange={(e) => setNewExcludedSource(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addExcludedSource()}
                    placeholder="example.com or full feed URL..."
                    className="flex-1 bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button onClick={addExcludedSource} className="btn-primary">
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {excludedSources.map((source) => (
                    <span
                      key={source}
                      className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/50 rounded-full text-sm flex items-center space-x-2"
                    >
                      <span>{source}</span>
                      <button
                        onClick={() =>
                          setExcludedSources(excludedSources.filter((s) => s !== source))
                        }
                        className="hover:text-red-300"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
