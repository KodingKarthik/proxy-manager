import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi, type ListUsersParams, type GetLogsParams } from '@proxy-manager/api';

export const useAdminUsers = (params?: ListUsersParams) => {
  return useQuery({
    queryKey: ['admin', 'users', params],
    queryFn: () => adminApi.listUsers(params),
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => adminApi.deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
  });
};

export const usePromoteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => adminApi.promoteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
  });
};

export const useAdminLogs = (params?: GetLogsParams) => {
  return useQuery({
    queryKey: ['admin', 'logs', params],
    queryFn: () => adminApi.getAllLogs(params),
  });
};

export const useExportAdminLogs = () => {
  return async (params?: GetLogsParams) => {
    const blob = await adminApi.exportAllLogs(params);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `admin-logs-${new Date().toISOString()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };
};

