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
      const response = await apiClient.login(username, password);
      setUser(response.user);
      // Fetch full profile
      const profileData = await apiClient.getCurrentUser();
      setProfile(profileData);
    } catch (error) {
      console.error('[v0] Login error:', error);
      throw error instanceof Error ? error : new Error((error as any)?.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string, first_name?: string, last_name?: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.register(username, email, password, first_name, last_name);
      setUser(response.user);
      // Fetch full profile
      const profileData = await apiClient.getCurrentUser();
      setProfile(profileData);
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
