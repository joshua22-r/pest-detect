'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient, UserProfile, AuthResponse } from '@/lib/api-client';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, first_name?: string, last_name?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  requestPasswordReset: (email: string) => Promise<void>;
  confirmPasswordReset: (token: string, newPassword: string) => Promise<void>;
  socialLogin: (provider: 'google' | 'facebook', accessToken: string, tokenType?: 'access_token' | 'id_token' | 'credential') => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore session on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
        if (token) {
          // Verify token by fetching current user
          const userData = await apiClient.getCurrentUser();
          setProfile(userData);
          setUser(userData.user);

          // Redirect admin users to admin dashboard
          if (userData.user_type === 'admin' && window.location.pathname !== '/admin/dashboard') {
            // Small delay to ensure state is updated before navigation
            setTimeout(() => {
              window.location.href = '/admin/dashboard';
            }, 100);
            return;
          }
        }
      } catch (error) {
        console.error('[v0] Failed to restore session:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      console.log('[AuthContext] Initiating login for:', username);
      const response = await apiClient.login(username, password);
      console.log('[AuthContext] Login response received:', response);
      setUser(response.user);
      
      // Fetch full profile
      const profileData = await apiClient.getCurrentUser();
      console.log('[AuthContext] Profile data fetched:', profileData);
      setProfile(profileData);

      // Redirect based on user type
      if (profileData.user_type === 'admin') {
        console.log('[AuthContext] User is admin, redirecting to dashboard');
        setTimeout(() => {
          if (window) {
            window.location.href = '/admin/dashboard';
          }
        }, 100);
        return;
      } else {
        console.log('[AuthContext] User is regular user, redirecting to predict');
        setTimeout(() => {
          if (window) {
            window.location.href = '/predict';
          }
        }, 100);
        return;
      }
    } catch (error) {
      console.error('[AuthContext] Login failed:', error);
      // Clear any partially set tokens on error
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
      setUser(null);
      setProfile(null);
      throw error instanceof Error ? error : new Error((error as any)?.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string, first_name?: string, last_name?: string) => {
    setIsLoading(true);
    try {
      await apiClient.register(username, email, password, first_name, last_name, false);
    } catch (error) {
      console.error('[v0] Registration error:', error);
      throw error instanceof Error ? error : new Error((error as any)?.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('[v0] Logout error:', error);
    } finally {
      setUser(null);
      setProfile(null);
    }
  };

  const refreshUser = async () => {
    try {
      const profileData = await apiClient.getCurrentUser();
      setProfile(profileData);
      setUser(profileData.user);
    } catch (error) {
      console.error('[v0] Failed to refresh user:', error);
    }
  };

  const requestPasswordReset = async (email: string) => {
    try {
      await apiClient.requestPasswordReset(email);
    } catch (error) {
      console.error('[Auth] Password reset request error:', error);
      throw error instanceof Error ? error : new Error((error as any)?.message || 'Password reset request failed');
    }
  };

  const confirmPasswordReset = async (token: string, newPassword: string) => {
    try {
      await apiClient.confirmPasswordReset(token, newPassword);
    } catch (error) {
      console.error('[Auth] Password reset confirmation error:', error);
      throw error instanceof Error ? error : new Error((error as any)?.message || 'Password reset confirmation failed');
    }
  };

  const socialLogin = async (provider: 'google' | 'facebook', accessToken: string, tokenType?: 'access_token' | 'id_token' | 'credential') => {
    setIsLoading(true);
    try {
      const response = await apiClient.socialLogin(provider, accessToken, tokenType);
      setUser(response.user);

      // Fetch full profile
      const profileData = await apiClient.getCurrentUser();
      setProfile(profileData);

      // Redirect based on user type
      if (profileData.user_type === 'admin') {
        setTimeout(() => {
          window.location.href = '/admin/dashboard';
        }, 100);
      } else {
        setTimeout(() => {
          window.location.href = '/predict';
        }, 100);
      }
    } catch (error) {
      console.error('[Auth] Social login error:', error);
      throw error instanceof Error ? error : new Error((error as any)?.message || 'Social login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
        requestPasswordReset,
        confirmPasswordReset,
        socialLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
