import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { User } from "@/types/user.type"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export const isJsonString = (str: string): boolean => {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
};

export const convertSecondToMinute = (seconds:number):string => {
  const minutes = Math.floor(seconds / 60);
  const resSecond = Math.ceil(seconds % 60);
  const paddedSeconds = resSecond.toString().padStart(2, '0');
  return `${minutes}:${paddedSeconds}`;
}

export function isUserSuspended(user: User | null): boolean {
  if (!user) return false;
  
  return !user.is_active || (user.violation_count !== undefined && user.violation_count >= 5);
}

export interface BookingDetails {
  lecturer_name: string;
  date: string;
  time: string;
  subject: string;
  location: string;
  duration_minutes: number;
}

export function parseAIBookingResponse(aiResponse: any): BookingDetails | null {
  try {
    // Check if AI response indicates a booking
    if (!aiResponse.ai_is_schedule || !aiResponse.ai_booking_details) {
      return null;
    }

    const bookingDetails = aiResponse.ai_booking_details;
    
    // Validate required fields
    if (!bookingDetails.date || !bookingDetails.time || !bookingDetails.lecturer_name) {
      console.warn('Missing required booking details:', bookingDetails);
      return null;
    }

    return {
      lecturer_name: bookingDetails.lecturer_name,
      date: bookingDetails.date,
      time: bookingDetails.time,
      subject: bookingDetails.subject || 'Career Consultation',
      location: bookingDetails.location || 'Online Meeting',
      duration_minutes: bookingDetails.duration_minutes || 30
    };
  } catch (error) {
    console.error('Error parsing AI booking response:', error);
    return null;
  }
}