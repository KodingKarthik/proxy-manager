import apiClient from './client';
import type {
  ProxyCreate,
  ProxyResponse,
  ProxyTestResult,
} from './types';

export interface ListProxiesParams {
  working_only?: boolean;
  limit?: number;
  offset?: number;
}

export interface GetProxyParams {
  strategy?: 'random' | 'round_robin' | 'lru' | 'best' | 'health_score';
  target_url?: string | null;
}

export const proxiesApi = {
  list: async (params?: ListProxiesParams): Promise<ProxyResponse[]> => {
    const response = await apiClient.get<ProxyResponse[]>('/proxies', { params });
    return response.data;
  },

  create: async (data: ProxyCreate): Promise<ProxyResponse> => {
    const response = await apiClient.post<ProxyResponse>('/proxies', data);
    return response.data;
  },

  delete: async (proxyId: number): Promise<void> => {
    await apiClient.delete(`/proxies/${proxyId}`);
  },

  test: async (proxyId: number): Promise<ProxyTestResult> => {
    const response = await apiClient.post<ProxyTestResult>(`/proxies/${proxyId}/test`);
    return response.data;
  },

  getByStrategy: async (params?: GetProxyParams): Promise<ProxyResponse> => {
    const response = await apiClient.get<ProxyResponse>('/proxy', { params });
    return response.data;
  },

  getNext: async (targetUrl?: string | null): Promise<ProxyResponse> => {
    const response = await apiClient.get<ProxyResponse>('/proxy/next', {
      params: targetUrl ? { target_url: targetUrl } : undefined,
    });
    return response.data;
  },

  getRandom: async (targetUrl?: string | null): Promise<ProxyResponse> => {
    const response = await apiClient.get<ProxyResponse>('/proxy/random', {
      params: targetUrl ? { target_url: targetUrl } : undefined,
    });
    return response.data;
  },

  getBest: async (): Promise<ProxyResponse> => {
    const response = await apiClient.get<ProxyResponse>('/proxy/best');
    return response.data;
  },
};

