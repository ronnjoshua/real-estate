'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, UserRole } from '../types/user';

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  isAdmin: boolean;
  isClient: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Token storage utilities (using sessionStorage for security)
const TOKEN_KEY = 'auth_tokens';
const USER_KEY = 'user_data';

const setTokens = (tokens: AuthTokens) => {
  try {
    sessionStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  } catch (error) {
    console.error('Error storing tokens:', error);
  }
};

const getTokens = (): AuthTokens | null => {
  try {
    const tokens = sessionStorage.getItem(TOKEN_KEY);
    return tokens ? JSON.parse(tokens) : null;
  } catch (error) {
    console.error('Error retrieving tokens:', error);
    return null;
  }
};

const removeTokens = () => {
  try {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  } catch (error) {
    console.error('Error removing tokens:', error);
  }
};

const setUserData = (user: User) => {
  try {
    sessionStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (error) {
    console.error('Error storing user data:', error);
  }
};

const getUserData = (): User | null => {
  try {
    const userData = sessionStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error('Error retrieving user data:', error);
    return null;
  }
};

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Refresh token function
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const tokens = getTokens();
      if (!tokens?.refresh_token) {
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: tokens.refresh_token,
        }),
      });

      if (!response.ok) {
        console.error('Token refresh failed');
        return false;
      }

      const newTokens: AuthTokens = await response.json();
      setTokens(newTokens);
      return true;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return false;
    }
  }, []);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const tokens = getTokens();
        const userData = getUserData();

        if (!tokens || !userData) {
          setLoading(false);
          return;
        }

        // Check if access token is expired (with 5 minute buffer)
        const tokenExpiry = Date.now() + (tokens.expires_in * 1000);
        const isExpiringSoon = tokenExpiry - Date.now() < 5 * 60 * 1000; // 5 minutes

        if (isExpiringSoon) {
          const refreshSuccess = await refreshToken();
          if (!refreshSuccess) {
            removeTokens();
            setUser(null);
            setLoading(false);
            return;
          }
        }

        setUser(userData);
      } catch (error) {
        console.error('Error checking authentication:', error);
        removeTokens();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [refreshToken]);

  // Set up token refresh interval
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(async () => {
      const tokens = getTokens();
      if (!tokens) return;

      const tokenExpiry = Date.now() + (tokens.expires_in * 1000);
      const isExpiringSoon = tokenExpiry - Date.now() < 10 * 60 * 1000; // 10 minutes

      if (isExpiringSoon) {
        const refreshSuccess = await refreshToken();
        if (!refreshSuccess) {
          logout();
        }
      }
    }, 5 * 60 * 1000); // Check every 5 minutes

    return () => clearInterval(interval);
  }, [user, refreshToken]);

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Login failed');
      }

      const loginData = await response.json();
      
      // Store tokens
      const tokens: AuthTokens = {
        access_token: loginData.access_token,
        refresh_token: loginData.refresh_token,
        token_type: loginData.token_type,
        expires_in: loginData.expires_in,
      };
      
      setTokens(tokens);
      
      // Store user data
      const userData: User = loginData.user;
      setUserData(userData);
      setUser(userData);
      
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      const tokens = getTokens();
      
      // Call logout endpoint if we have a token
      if (tokens?.access_token) {
        try {
          await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${tokens.access_token}`,
            },
          });
        } catch (error) {
          console.error('Error calling logout endpoint:', error);
          // Continue with local logout even if server logout fails
        }
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local state
      removeTokens();
      setUser(null);
    }
  };

  const isAdmin = user?.role === UserRole.ADMIN;
  const isClient = user?.role === UserRole.CLIENT;
  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      login, 
      logout, 
      refreshToken,
      isAdmin, 
      isClient,
      isAuthenticated 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 