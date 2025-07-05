import { AnimatePresence, motion } from "framer-motion";
import { useState, useEffect } from 'react';
import { bookingApi, type Booking } from '@/lib/api/booking.api';
import { useAuth } from '@/hooks/useAuth';
import { Calendar, Clock, MapPin, User, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import axios from 'axios';

interface AppointmentListProps {
  activeTab: 'upcoming' | 'history';
}

export const AppointmentList = ({ activeTab }: AppointmentListProps) => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();


  const fetchBookings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await bookingApi.getMyBookings();
      if (response && Array.isArray(response.bookings)) {
        setBookings(response.bookings);
      } else {
        setBookings([]);
      }
    } catch (err: any) {
      if (err instanceof Error) {
        console.error('Error name:', err.name);
      }
      if (axios.isAxiosError(err)) {
        setError('Cannot load booking list');
        setBookings([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchBookings();
    } else {
      setLoading(false);
      setBookings([]);
    }
  }, [isAuthenticated]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeStr: string, duration: number) => {
    const startTime = timeStr.slice(0, 5);
    const [hours, minutes] = timeStr.split(':').map(Number);
    const endDate = new Date(0, 0, 0, hours, minutes + duration);
    const endTime = endDate.toTimeString().slice(0, 5);
    return `${startTime} - ${endTime}`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'pending':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'Confirmed';
      case 'pending':
        return 'Pending';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'border-green-500 bg-green-50';
      case 'pending':
        return 'border-yellow-500 bg-yellow-50';
      case 'cancelled':
        return 'border-red-500 bg-red-50';
      default:
        return 'border-gray-500 bg-gray-50';
    }
  };

  // Filter bookings based on active tab
  const filteredBookings = (bookings || []).filter(booking => {
    const bookingDate = new Date(booking.booking_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (activeTab === 'upcoming') {
      return bookingDate >= today && booking.status !== 'cancelled';
    } else {
      return bookingDate < today || booking.status === 'cancelled';
    }
  });

  if (!isAuthenticated) {
    return null;
  }

  // Safety check for bookings state
  if (bookings === undefined || bookings === null) {
    return (
      <div className="flex-1 p-4 md:p-6 md:ml-4">
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 border-2 border-[#332288] border-t-transparent rounded-full animate-spin"></div>
            <span className="text-[#332288] font-medium">Initializing...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 md:p-6 md:ml-4">
      <div className="flex items-center justify-between mb-4 md:mb-6">
        <h2 className="text-xl md:text-2xl font-bold text-[#332288]">
          {activeTab === 'upcoming' ? 'Upcoming Appointments' : 'Appointments History'}
        </h2>
        {!loading && bookings && bookings.length > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-sm text-gray-600 bg-white px-3 py-1 rounded-full border border-[#332288]/20"
          >
            {filteredBookings.length} appointments
          </motion.div>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center justify-center py-12"
        >
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 border-2 border-[#332288] border-t-transparent rounded-full animate-spin"></div>
            <span className="text-[#332288] font-medium">Loading appointments...</span>
          </div>
        </motion.div>
      )}

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-red-50 border border-red-200 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2">
            <XCircle className="w-5 h-5 text-red-600" />
            <span className="text-red-800">{error}</span>
          </div>
        </motion.div>
      )}

      {/* Bookings List */}
      {!loading && !error && (
        <AnimatePresence mode="wait">
          {filteredBookings.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-12"
            >
              <div className="w-16 h-16 bg-[#332288]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="w-8 h-8 text-[#332288]" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {activeTab === 'upcoming' ? 'No upcoming appointments' : 'No appointment history'}
              </h3>
              <p className="text-gray-600">
                {activeTab === 'upcoming' 
                  ? 'You have no upcoming appointments. Please book an appointment now!' 
                  : 'You have no appointment history.'}
              </p>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6"
            >
              {filteredBookings.map((booking, index) => (
                <motion.div
                  key={booking.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className={`border-2 rounded-xl p-4 md:p-6 w-full transition-all duration-300 hover:shadow-lg hover:scale-[1.02] ${getStatusColor(booking.status)} border-[#332288] hover:border-[#332288]/60`}
                >
                  {/* Header with status */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <User className="w-5 h-5 text-[#332288]" />
                      <h3 className="text-base md:text-lg font-semibold text-[#332288] line-clamp-2">
                        {booking.lecturer.name}
                      </h3>
                    </div>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(booking.status)}
                    </div>
                  </div>

                  {/* Subject */}
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-700">
                      {booking.lecturer.subject || booking.subject || 'Consultation'}
                    </p>
                  </div>

                  {/* Date & Time */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-[#332288]" />
                      <p className="text-sm text-[#332288] font-medium">
                        {formatDate(booking.booking_date)}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-[#332288]" />
                      <p className="text-sm text-[#332288]">
                        {formatTime(booking.booking_time, booking.duration_minutes)}
                      </p>
                    </div>
                    {booking.lecturer.location && (
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4 text-[#332288]" />
                        <p className="text-sm text-[#332288]">
                          {booking.lecturer.location}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Status */}
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-xs font-medium px-3 py-1 rounded-full bg-white border border-[#332288]/30 text-[#332288]">
                      {getStatusText(booking.status)}
                    </span>
                    <button className="bg-[#332288] text-white px-4 md:px-6 py-2 rounded-xl hover:bg-[#2a1f70] transition-all duration-200 text-sm md:text-base hover:shadow-md">
                      VIEW DETAILS
                    </button>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      )}

    </div>
  );
}; 