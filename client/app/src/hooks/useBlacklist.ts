import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { blacklistApi, type BlacklistCreate } from '@proxy-manager/api';

export const useBlacklist = () => {
  return useQuery({
    queryKey: ['blacklist'],
    queryFn: () => blacklistApi.list(),
  });
};

export const useCreateBlacklistRule = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BlacklistCreate) => blacklistApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blacklist'] });
    },
  });
};

export const useDeleteBlacklistRule = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ruleId: number) => blacklistApi.delete(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blacklist'] });
    },
  });
};

