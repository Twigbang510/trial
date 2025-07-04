import React from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface ConfirmationButtonsProps {
  onConfirm: () => void;
  onCancel: () => void;
  className?: string;
  confirmText?: string;
  cancelText?: string;
  disabled?: boolean;
}

const ConfirmationButtons: React.FC<ConfirmationButtonsProps> = ({
  onConfirm,
  onCancel,
  className = '',
  confirmText = 'Có',
  cancelText = 'Không',
  disabled = false
}) => {
  return (
    <div className={`confirmation-buttons flex space-x-4 ${className}`}>
      {/* Confirm Button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        whileHover={!disabled ? { scale: 1.05 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
        onClick={onConfirm}
        disabled={disabled}
        className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-md ${
          disabled 
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
            : 'bg-green-500 hover:bg-green-600 text-white hover:shadow-lg'
        }`}
      >
        <CheckCircle className="w-5 h-5" />
        <span>{confirmText}</span>
      </motion.button>

      {/* Cancel Button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        whileHover={!disabled ? { scale: 1.05 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
        onClick={onCancel}
        disabled={disabled}
        className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-md ${
          disabled 
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
            : 'bg-red-500 hover:bg-red-600 text-white hover:shadow-lg'
        }`}
      >
        <XCircle className="w-5 h-5" />
        <span>{cancelText}</span>
      </motion.button>
    </div>
  );
};

export default ConfirmationButtons; 