import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, tokenStorage, type UserResponse } from '@proxy-manager/api';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  user: UserResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const refreshUser = async () => {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (error) {
      // If getting user fails, clear tokens
      tokenStorage.clearAccessToken();
      tokenStorage.clearRefreshToken();
      setUser(null);
    }
  };

  useEffect(() => {
    // Check if user is authenticated on mount
    const initAuth = async () => {
      const token = tokenStorage.getAccessToken();
      if (token) {
        try {
          await refreshUser();
        } catch (error) {
          // Token is invalid, clear it
          tokenStorage.clearAccessToken();
          tokenStorage.clearRefreshToken();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    const tokens = await authApi.login({ username, password });
    tokenStorage.setAccessToken(tokens.access_token);
    tokenStorage.setRefreshToken(tokens.refresh_token);
    await refreshUser();
    navigate('/app/proxies');
  };

  const register = async (username: string, email: string, password: string) => {
    await authApi.register({ username, email, password });
    // After registration, login automatically
    await login(username, password);
  };

  const logout = () => {
    tokenStorage.clearAccessToken();
    tokenStorage.clearRefreshToken();
    setUser(null);
    navigate('/login');
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

