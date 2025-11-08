import apiClient from './client';
import type { ActivityLogResponse } from './types';

export interface GetLogsParams {
  start_date?: string | null;
  end_date?: string | null;
  endpoint?: string | null;
  method?: string | null;
  status_code?: number | null;
  limit?: number;
  offset?: number;
}

export interface ExportLogsParams {
  start_date?: string | null;
  end_date?: string | null;
  endpoint?: string | null;
  method?: string | null;
  status_code?: number | null;
}

export const logsApi = {
  getMyLogs: async (params?: GetLogsParams): Promise<ActivityLogResponse[]> => {
    const response = await apiClient.get<ActivityLogResponse[]>('/logs', { params });
    return response.data;
  },

  exportMyLogs: async (params?: ExportLogsParams): Promise<Blob> => {
    const response = await apiClient.get('/logs/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

