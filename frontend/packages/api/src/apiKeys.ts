import apiClient from './client';
import type { ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse } from './types';

export const apiKeysApi = {
    /**
     * Create a new API key for the current user.
     * 
     * WARNING: The raw API key will only be returned once!
     * Make sure to save it securely before closing the response.
     */
    create: async (data: ApiKeyCreate): Promise<ApiKeyCreateResponse> => {
        const response = await apiClient.post<ApiKeyCreateResponse>('/api-keys', data);
        return response.data;
    },

    /**
     * List all API keys for the current user.
     * 
     * Note: The actual key values are never returned, only metadata.
     */
    list: async (): Promise<ApiKeyResponse[]> => {
        const response = await apiClient.get<ApiKeyResponse[]>('/api-keys');
        return response.data;
    },

    /**
     * Revoke (delete) an API key.
     * 
     * Users can only revoke their own API keys.
     */
    revoke: async (keyId: number): Promise<void> => {
        await apiClient.delete(`/api-keys/${keyId}`);
    },

    /**
     * List all API keys for a specific user (admin only).
     */
    listUserKeys: async (userId: number): Promise<ApiKeyResponse[]> => {
        const response = await apiClient.get<ApiKeyResponse[]>(`/api-keys/users/${userId}/api-keys`);
        return response.data;
    },
};
