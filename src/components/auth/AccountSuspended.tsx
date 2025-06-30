import React from 'react';
import { AlertTriangle, Mail, Phone, Clock } from 'lucide-react';
import { User } from '@/types/user.type';

interface AccountSuspendedProps {
  user: User;
}

const AccountSuspended: React.FC<AccountSuspendedProps> = ({ user }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-red-200">
        {/* Header */}
        <div className="bg-red-500 text-white p-6 rounded-t-2xl text-center">
          <AlertTriangle className="w-16 h-16 mx-auto mb-4" />
          <h1 className="text-2xl font-bold">Account Suspended</h1>
          <p className="text-red-100 mt-2">Your account has been temporarily suspended</p>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Account Details</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Username:</span>
                <span className="font-medium text-red-600">{user.username || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Email:</span>
                <span className="font-medium text-red-600">{user.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Account Status:</span>
                <span className="font-medium text-red-600">
                  {!user.is_active ? 'Suspended' : 'Violation Limit Reached'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Violation Count:</span>
                <span className="font-medium text-red-600">
                  {user.violation_count !== undefined ? `${user.violation_count}/5` : 'Unknown'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-orange-800 mb-2">Why was my account suspended?</h3>
            <p className="text-sm text-orange-700">
              Your account has been suspended due to repeated violations of our community guidelines. 
              This includes inappropriate content, spam, or other policy violations.
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold text-gray-800">What can I do?</h3>
            
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <Mail className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-blue-800">Contact Support</p>
                  <p className="text-sm text-blue-600">Email us at support@trial-webapp.com</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                <Phone className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-green-800">Call Support</p>
                  <p className="text-sm text-green-600">Phone: +1 (555) 123-4567</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                <Clock className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-purple-800">Appeal Process</p>
                  <p className="text-sm text-purple-600">Appeals are typically reviewed within 24-48 hours</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Please ensure you understand our community guidelines before appealing. 
              Repeated violations may result in permanent account suspension.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 rounded-b-2xl">
          <button
            onClick={() => {
              // Clear auth state and redirect to login
              localStorage.removeItem('auth_state');
              window.location.href = '/auth/signin';
            }}
            className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountSuspended; 