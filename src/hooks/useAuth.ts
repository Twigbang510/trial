import { useState, useEffect, useCallback } from 'react';
import { authService } from '../services/auth';
import { User } from '@/types/user.type';

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  // Function to sync auth state
  const syncAuthState = useCallback(() => {
    const state = authService.getAuthState();
    const newIsAuthenticated = !!state.user && !!state.token;
    
    setIsAuthenticated(newIsAuthenticated);
    setUser(state.user);
  }, []);

  useEffect(() => {
    // Initial sync
    syncAuthState();
    setIsLoading(false);

    // Listen for localStorage changes (for cross-tab sync)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_state') {
        syncAuthState();
      }
    };

    // Listen for custom auth events (for same-tab sync)
    const handleAuthChange = () => {
      syncAuthState();
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth-change', handleAuthChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-change', handleAuthChange);
    };
  }, [syncAuthState]);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const state = await authService.login(email, password);
      setIsAuthenticated(true);
      setUser(state.user);
      // Trigger auth change event
      window.dispatchEvent(new Event('auth-change'));
      return state;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshUserData = useCallback(async () => {
    try {
      const updatedUser = await authService.refreshUserData();
      if (updatedUser) {
        setUser(updatedUser);
        setIsAuthenticated(true);
        // Trigger auth change event
        window.dispatchEvent(new Event('auth-change'));
      }
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  }, []);

  const updateUserStatus = useCallback(async (status: "PENDING" | "PROCESSING" | "SCHEDULED") => {
    try {
      const updatedUser = await authService.updateUser({ status });
      if (updatedUser) {
        setUser(updatedUser);
        // Trigger auth change event
        window.dispatchEvent(new Event('auth-change'));
      }
      return updatedUser;
    } catch (error) {
      console.error('Failed to update user status:', error);
      return null;
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setIsAuthenticated(false);
    setUser(null);
    // Trigger auth change event
    window.dispatchEvent(new Event('auth-change'));
  }, []);

  return {
    isLoading,
    isAuthenticated,
    user,
    login,
    logout,
    refreshUserData,
    updateUserStatus
  };
}; 