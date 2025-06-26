import authApi from "@/lib/api/auth.api";

export interface User {
  id: string;
  email: string;
  username?: string;
  full_name?: string;
  is_active?: boolean;
  is_verified?: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

const AUTH_STORAGE_KEY = 'auth_state';

export const authService = {
  getAuthState(): AuthState {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
    return { user: null, token: null };
  },

  async login(email: string, password: string): Promise<AuthState> {
    const res = await authApi.login({ email, password });
    const token = res.data.access_token || res.data.accessToken || "";
    const user = res.data.user || { email };
    const state = { user, token };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(state));
    return state;
  },

  logout(): void {
    localStorage.removeItem(AUTH_STORAGE_KEY);
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