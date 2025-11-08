import apiClient from './client';
import type { HealthResponse, ProxyStatsResponse } from './types';

export const healthApi = {
  check: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  getProxyStats: async (): Promise<ProxyStatsResponse> => {
    const response = await apiClient.get<ProxyStatsResponse>('/health/proxies');
    return response.data;
  },
};

