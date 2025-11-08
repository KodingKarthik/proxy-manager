import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { proxiesApi, type ProxyCreate, type ListProxiesParams, type GetProxyParams } from '@proxy-manager/api';

export const useProxies = (params?: ListProxiesParams) => {
  return useQuery({
    queryKey: ['proxies', params],
    queryFn: () => proxiesApi.list(params),
  });
};

export const useProxy = (proxyId: number) => {
  return useQuery({
    queryKey: ['proxy', proxyId],
    queryFn: async () => {
      const proxies = await proxiesApi.list();
      return proxies.find((p) => p.id === proxyId);
    },
    enabled: !!proxyId,
  });
};

export const useCreateProxy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ProxyCreate) => proxiesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proxies'] });
    },
  });
};

export const useDeleteProxy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (proxyId: number) => proxiesApi.delete(proxyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proxies'] });
    },
  });
};

export const useTestProxy = () => {
  return useMutation({
    mutationFn: (proxyId: number) => proxiesApi.test(proxyId),
  });
};

export const useGetProxyByStrategy = () => {
  return useMutation({
    mutationFn: (params: { strategy?: GetProxyParams['strategy']; target_url?: string | null }) =>
      proxiesApi.getByStrategy(params as GetProxyParams),
  });
};

export const useGetNextProxy = () => {
  return useMutation({
    mutationFn: (targetUrl?: string | null) => proxiesApi.getNext(targetUrl),
  });
};

export const useGetRandomProxy = () => {
  return useMutation({
    mutationFn: (targetUrl?: string | null) => proxiesApi.getRandom(targetUrl),
  });
};

export const useGetBestProxy = () => {
  return useQuery({
    queryKey: ['proxy', 'best'],
    queryFn: () => proxiesApi.getBest(),
  });
};

