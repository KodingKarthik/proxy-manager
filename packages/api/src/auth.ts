import apiClient from './client';
import type { UserCreate, UserLogin, Token, UserResponse } from './types';

export const authApi = {
  register: async (data: UserCreate): Promise<UserResponse> => {
    const response = await apiClient.post<UserResponse>('/auth/register', data);
    return response.data;
  },

  login: async (data: UserLogin): Promise<Token> => {
    const response = await apiClient.post<Token>('/auth/login', data);
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<Token> => {
    const response = await apiClient.post<Token>(
      `/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`
    );
    return response.data;
  },

  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>('/auth/me');
    return response.data;
  },
};

