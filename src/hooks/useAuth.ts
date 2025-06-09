import { useState, useEffect } from 'react';
import { authService, User } from '../services/auth';

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const state = authService.getAuthState();
    setIsAuthenticated(!!state.user);
    setUser(state.user);
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const state = await authService.login(email, password);
      setIsAuthenticated(true);
      setUser(state.user);
      return state;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  return {
    isLoading,
    isAuthenticated,
    user,
    login,
    logout
  };
}; 