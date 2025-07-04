import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Mail, X, Calendar, Clock, MapPin, User, Book } from 'lucide-react';

interface BookingDetails {
  lecturer_name: string;
  date: string;
  time: string;
  subject: string;
  location: string;
  duration_minutes: number;
}

interface BookingSuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  bookingDetails: BookingDetails;
  emailSent: boolean;
}

const BookingSuccessModal: React.FC<BookingSuccessModalProps> = ({
  isOpen,
  onClose,
  bookingDetails,
  emailSent
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.7, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.7, opacity: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-[#332288] to-[#4a3199] text-white p-6 rounded-t-2xl relative">
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-white hover:text-gray-200 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="bg-green-500 rounded-full p-2">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Booking Confirmed!</h2>
                <p className="text-purple-100">Your appointment has been scheduled</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Email Status */}
            <div className={`flex items-center space-x-3 p-4 rounded-lg mb-6 ${
              emailSent 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-yellow-50 border border-yellow-200'
            }`}>
              <Mail className={`w-5 h-5 ${emailSent ? 'text-green-600' : 'text-yellow-600'}`} />
              <div className="flex-1">
                <p className={`font-medium text-sm ${emailSent ? 'text-green-800' : 'text-yellow-800'}`}>
                  {emailSent ? '✅ Email Confirmation Sent!' : '📧 Email Confirmation Pending'}
                </p>
                <p className={`text-xs ${emailSent ? 'text-green-600' : 'text-yellow-600'}`}>
                  {emailSent 
                    ? 'Check your inbox for detailed booking information'
                    : 'Email will be sent shortly'
                  }
                </p>
              </div>
            </div>

            {/* Booking Details */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-[#332288] mb-4">📅 Appointment Details</h3>
              
              <div className="space-y-3">
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <User className="w-5 h-5 text-[#332288]" />
                  <div>
                    <p className="text-xs text-gray-500">Lecturer</p>
                    <p className="font-medium text-[#332288]">{bookingDetails.lecturer_name}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Calendar className="w-5 h-5 text-[#332288]" />
                  <div>
                    <p className="text-xs text-gray-500">Date</p>
                    <p className="font-medium text-[#332288]">{bookingDetails.date}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Clock className="w-5 h-5 text-[#332288]" />
                  <div>
                    <p className="text-xs text-gray-500">Time & Duration</p>
                    <p className="font-medium text-[#332288]">
                      {bookingDetails.time} ({bookingDetails.duration_minutes} minutes)
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Book className="w-5 h-5 text-[#332288]" />
                  <div>
                    <p className="text-xs text-gray-500">Subject</p>
                    <p className="font-medium text-[#332288]">{bookingDetails.subject}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <MapPin className="w-5 h-5 text-[#332288]" />
                  <div>
                    <p className="text-xs text-gray-500">Location</p>
                    <p className="font-medium text-[#332288]">{bookingDetails.location}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <div className="mt-6 flex justify-center">
              <button
                onClick={onClose}
                className="bg-[#332288] text-white px-8 py-3 rounded-lg font-medium hover:bg-[#2a1a70] transition-all duration-200 transform hover:scale-105"
              >
                Got it, thanks! 🎉
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default BookingSuccessModal; 