import React from 'react';
import { Clock, MapPin, User, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import { BookingOption } from '@/types/conversation.type';

interface BookingOptionsProps {
  options: BookingOption[];
  onOptionSelect: (option: BookingOption) => void;
  className?: string;
}

const BookingOptions: React.FC<BookingOptionsProps> = ({ 
  options, 
  onOptionSelect, 
  className = '' 
}) => {
  console.log('🎯 BookingOptions component rendered!');
  console.log('Options received:', options);
  console.log('Options length:', options?.length);
  
  if (!options || options.length === 0) {
    console.log('❌ BookingOptions: No options provided, returning null');
    return null;
  }

  // Hiển thị tất cả options (không filter type)
  const allOptions = options;
  console.log('=== BOOKING OPTIONS ===');
  console.log(allOptions);

  const formatTime = (timeStr: string) => {
    try {
      const [hours, minutes] = timeStr.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeStr;
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('vi-VN', {
        weekday: 'short',
        day: 'numeric',
        month: 'short'
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className={`booking-options-external ${className} mt-4 p-4 bg-white border-2 border-blue-500 rounded-lg shadow-lg`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-blue-700 mb-3 flex items-center space-x-2">
          <Calendar className="w-5 h-5" />
          <span>Đây là các khung giờ phù hợp và available, vui lòng chọn bằng cách nhấn vào 1 trong các khung giờ dưới đây:</span>
        </h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {allOptions.map((option, index) => (
            <motion.button
              key={`${option.availability_id}-${option.time}-${index}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onOptionSelect(option)}
              className={`p-4 border-2 ${option.type === 'exact_match' ? 'border-green-500 bg-green-50 hover:bg-green-100' : 'border-yellow-400 bg-yellow-50 hover:bg-yellow-100'} rounded-lg text-left transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-300 shadow-sm hover:shadow-md`}
            >
              {/* Time Display */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-blue-600" />
                  <span className="text-xl font-bold text-blue-800">
                    {option.time}
                  </span>
                </div>
                <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">
                  {formatDate(option.date)}
                </span>
              </div>
              {/* Lecturer Info */}
              <div className="flex items-center space-x-2 mb-2">
                <User className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-800">
                  {option.lecturer_name}
                </span>
              </div>
              {/* Subject */}
              <div className="text-sm text-blue-700 font-medium mb-2 bg-blue-100 px-2 py-1 rounded">
                📚 {option.subject}
              </div>
              {/* Location */}
              <div className="flex items-center space-x-1 mb-1">
                <MapPin className="w-4 h-4 text-gray-500" />
                <span className="text-xs text-gray-600">{option.location}</span>
              </div>
              {/* Duration */}
              <div className="text-xs text-gray-500">
                ⏱️ Thời lượng: {option.duration_minutes} phút
              </div>
            </motion.button>
          ))}
        </div>
      </div>
      {/* Call to action */}
      <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-emerald-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800 text-center font-medium">
          💡 <strong>Nhấn vào khung giờ bạn muốn</strong> để tiến hành đặt lịch
        </p>
      </div>
    </div>
  );
};

export default BookingOptions; 