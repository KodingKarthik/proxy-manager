import apiClient from './client';
import type { BlacklistCreate, BlacklistResponse } from './types';

export const blacklistApi = {
  list: async (): Promise<BlacklistResponse[]> => {
    const response = await apiClient.get<BlacklistResponse[]>('/blacklist');
    return response.data;
  },

  create: async (data: BlacklistCreate): Promise<BlacklistResponse> => {
    const response = await apiClient.post<BlacklistResponse>('/blacklist', data);
    return response.data;
  },

  delete: async (ruleId: number): Promise<void> => {
    await apiClient.delete(`/blacklist/${ruleId}`);
  },
};

