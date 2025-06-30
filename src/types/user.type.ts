export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  status: "PENDING" | "PROCESSING" | "SCHEDULED";
  violation_count: number;
  created_at: string;
  updated_at?: string;
}

export interface UserStatus {
  PENDING: "PENDING";
  PROCESSING: "PROCESSING";
  SCHEDULED: "SCHEDULED";
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignUpData {
  email: string;
  username: string;
  full_name?: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

export interface UserUpdate {
  username?: string;
  full_name?: string;
  status?: "PENDING" | "PROCESSING" | "SCHEDULED";
}

export interface UserType {
  id: string;
  email: string;
  username?: string;
  fullName?: string;
  isActive?: boolean;
  isVerified?: boolean;
  status?: "PENDING" | "PROCESSING" | "SCHEDULED";
  createdAt?: string;
  updatedAt?: string;
}
