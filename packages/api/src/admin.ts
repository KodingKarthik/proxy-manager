import apiClient from './client';
import type { UserResponse, ActivityLogResponse } from './types';
import type { GetLogsParams, ExportLogsParams } from './logs';

export interface ListUsersParams {
  limit?: number;
  offset?: number;
}

export const adminApi = {
  listUsers: async (params?: ListUsersParams): Promise<UserResponse[]> => {
    const response = await apiClient.get<UserResponse[]>('/admin/users', { params });
    return response.data;
  },

  deleteUser: async (userId: number): Promise<void> => {
    await apiClient.delete(`/admin/users/${userId}`);
  },

  promoteUser: async (userId: number): Promise<UserResponse> => {
    const response = await apiClient.patch<UserResponse>(`/admin/users/${userId}/promote`);
    return response.data;
  },

  getAllLogs: async (params?: GetLogsParams): Promise<ActivityLogResponse[]> => {
    const response = await apiClient.get<ActivityLogResponse[]>('/admin/logs', { params });
    return response.data;
  },

  exportAllLogs: async (params?: ExportLogsParams): Promise<Blob> => {
    const response = await apiClient.get('/admin/logs/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

