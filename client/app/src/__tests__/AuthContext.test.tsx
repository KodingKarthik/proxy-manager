import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { authApi } from '@proxy-manager/api';
import { tokenStorage } from '@proxy-manager/api';
import { ReactNode } from 'react';

vi.mock('@proxy-manager/api', () => ({
  authApi: {
    getMe: vi.fn(),
    login: vi.fn(),
    register: vi.fn(),
  },
  tokenStorage: {
    getAccessToken: vi.fn(),
    setAccessToken: vi.fn(),
    clearAccessToken: vi.fn(),
    getRefreshToken: vi.fn(),
    setRefreshToken: vi.fn(),
    clearRefreshToken: vi.fn(),
  },
}));

vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  BrowserRouter: ({ children }: { children: ReactNode }) => children,
}));

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should provide auth context', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      is_active: true,
      created_at: new Date().toISOString(),
    };

    vi.mocked(tokenStorage.getAccessToken).mockReturnValue('test-token');
    vi.mocked(authApi.getMe).mockResolvedValue(mockUser);

    const wrapper = ({ children }: { children: ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('should handle login', async () => {
    const mockTokens = {
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
    };

    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      is_active: true,
      created_at: new Date().toISOString(),
    };

    vi.mocked(authApi.login).mockResolvedValue(mockTokens);
    vi.mocked(authApi.getMe).mockResolvedValue(mockUser);

    const wrapper = ({ children }: { children: ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await result.current.login('testuser', 'password');

    expect(authApi.login).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password',
    });
    expect(tokenStorage.setAccessToken).toHaveBeenCalledWith('access-token');
    expect(tokenStorage.setRefreshToken).toHaveBeenCalledWith('refresh-token');
  });
});

