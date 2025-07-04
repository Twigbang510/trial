import axios from "axios";
import { API_URL } from "@/config/app";

const USER_API_URL = `${API_URL}/api/v1/users`;

export interface BookingLecturer {
  id: number
  name: string
  subject: string | null
  location: string | null
  notes: string | null
}

export interface Booking {
  id: number
  booking_date: string
  booking_time: string
  duration_minutes: number
  status: 'pending' | 'confirmed' | 'cancelled'
  subject: string | null
  notes: string | null
  created_at: string | null
  lecturer: BookingLecturer
}

export interface BookingsResponse {
  bookings: Booking[]
  total: number
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  try {
    const authStateStr = localStorage.getItem('auth_state');
    if (authStateStr) {
      const authState = JSON.parse(authStateStr);
      const token = authState.token;
      if (token) {
        return {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };
      }
    }
  } catch (error) {
    console.warn('Failed to get auth headers:', error);
  }
  return {
    'Content-Type': 'application/json'
  };
};

export const bookingApi = {
  // Get current user's bookings
  getMyBookings: async (params?: {
    status?: string
    limit?: number
  }): Promise<BookingsResponse> => {
    const response = await axios.get(`${USER_API_URL}/me/bookings`, { 
      params,
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Get booking by ID (for future use)
  getBooking: async (id: number): Promise<Booking> => {
    const response = await axios.get(`${API_URL}/api/v1/bookings/${id}`, {
      headers: getAuthHeaders()
    })
    return response.data
  }
} 