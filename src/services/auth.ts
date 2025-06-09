export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'university' | 'admin';
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

// Mock user data
const MOCK_USER: User = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'student'
};

const MOCK_TOKEN = 'mock-jwt-token';

const AUTH_STORAGE_KEY = 'auth_state';

export const authService = {
  getAuthState(): AuthState {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
    return { user: null, token: null };
  },

  login(email: string, password: string): Promise<AuthState> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const state = { user: MOCK_USER, token: MOCK_TOKEN };
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(state));
        resolve(state);
      }, 1000);
    });
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