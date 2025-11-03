import { apiClient } from './client';
import type { UserPreference } from '../types';

export interface UserPreferenceUpdate {
  preferred_topics?: string[];
  excluded_topics?: string[];
  preferred_sources?: string[];
  excluded_sources?: string[];
  enable_recommendations?: boolean;
  min_relevance_score?: number;
}

export const preferencesApi = {
  get: async (): Promise<UserPreference> => {
    const response = await apiClient.get<UserPreference>('/preferences/');
    return response.data;
  },

  update: async (data: UserPreferenceUpdate): Promise<UserPreference> => {
    const response = await apiClient.put<UserPreference>('/preferences/', data);
    return response.data;
  },
};
