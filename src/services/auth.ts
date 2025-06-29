import authApi from "@/lib/api/auth.api";
import { User, UserUpdate } from "@/types/user.type";

export interface AuthState {
  user: User | null;
  token: string | null;
}

const AUTH_STORAGE_KEY = 'auth_state';

export const authService = {
  init(): void {
    try {
      this.getAuthState();
    } catch (error) {
      console.error('Corrupted auth data detected, clearing localStorage:', error);
      this.logout();
    }
  },

  getAuthState(): AuthState {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    
    if (stored) {
      if (stored === "[object Object]" || stored === "undefined" || stored === "null") {
        console.warn('Detected corrupted auth data, clearing:', stored);
        localStorage.removeItem(AUTH_STORAGE_KEY);
        return { user: null, token: null };
      }
      
      try {
        const parsed = JSON.parse(stored);
        if (typeof parsed !== 'object' || parsed === null) {
          console.warn('Invalid auth state structure, clearing');
          localStorage.removeItem(AUTH_STORAGE_KEY);
          return { user: null, token: null };
        }
        
        return parsed;
      } catch (error) {
        console.error('Failed to parse auth state from localStorage:', error);
        console.log('Corrupted data:', stored);
        localStorage.removeItem(AUTH_STORAGE_KEY);
        return { user: null, token: null };
      }
    }
    
    return { user: null, token: null };
  },

  async login(email: string, password: string): Promise<AuthState> {
    const res = await authApi.login({ email, password });
    const token = res.data.access_token || "";
    const user = res.data.user || { email };
    const state = { user, token };
    
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Failed to save auth state:', error);
    }
    
    return state;
  },

  async refreshUserData(): Promise<User | null> {
    const currentState = this.getAuthState();
    
    if (!currentState.token) {
      return null;
    }
    
    try {
      const res = await authApi.getCurrentUser();
      const user = res.data;
      const newState = { ...currentState, user };
      
      try {
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(newState));
      } catch (error) {
        console.error('Failed to save updated user data:', error);
      }
      
      return user;
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      return null;
    }
  },

  async updateUser(updates: UserUpdate): Promise<User | null> {
    try {
      const res = await authApi.updateUser(updates);
      const user = res.data;
      const currentState = this.getAuthState();
      const newState = { ...currentState, user };
      
      try {
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(newState));
      } catch (error) {
        console.error('Failed to save updated user data:', error);
      }
      
      return user;
    } catch (error) {
      console.error('Failed to update user:', error);
      return null;
    }
  },

  logout(): void {
    localStorage.removeItem(AUTH_STORAGE_KEY);
  },

  // For debugging: clear all auth data (keeping for compatibility)
  clearAll(): void {
    try {
      localStorage.removeItem(AUTH_STORAGE_KEY);
      console.log('Auth data cleared successfully');
    } catch (error) {
      console.error('Failed to clear auth data:', error);
    }
  },

  isAuthenticated(): boolean {
    const state = this.getAuthState();
    return !!state.user && !!state.token;
  },

  getCurrentUser(): User | null {
    const state = this.getAuthState();
    return state.user;
  }
}; 