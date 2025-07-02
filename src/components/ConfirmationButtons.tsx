import React from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface ConfirmationButtonsProps {
  onConfirm: () => void;
  onCancel: () => void;
  className?: string;
  confirmText?: string;
  cancelText?: string;
}

const ConfirmationButtons: React.FC<ConfirmationButtonsProps> = ({
  onConfirm,
  onCancel,
  className = '',
  confirmText = 'Có',
  cancelText = 'Không'
}) => {
  return (
    <div className={`confirmation-buttons flex space-x-4 ${className}`}>
      {/* Yes Button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onConfirm}
        className="flex items-center space-x-2 px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg"
      >
        <CheckCircle className="w-5 h-5" />
        <span>{confirmText}</span>
      </motion.button>

      {/* No Button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onCancel}
        className="flex items-center space-x-2 px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg"
      >
        <XCircle className="w-5 h-5" />
        <span>{cancelText}</span>
      </motion.button>
    </div>
  );
};

export default ConfirmationButtons; 