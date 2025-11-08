import { useQuery } from '@tanstack/react-query';
import { logsApi, type GetLogsParams } from '@proxy-manager/api';

export const useLogs = (params?: GetLogsParams) => {
  return useQuery({
    queryKey: ['logs', params],
    queryFn: () => logsApi.getMyLogs(params),
  });
};

export const useExportLogs = () => {
  return async (params?: GetLogsParams) => {
    const blob = await logsApi.exportMyLogs(params);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `logs-${new Date().toISOString()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };
};

