import { Link } from '@tanstack/react-router';
import { AuthFormContainer } from './AuthFormContainer';
import { useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import authApi from '@/lib/api/auth.api';

export const ResetPassword = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (form.newPassword !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (form.newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);
    try {
      const email = localStorage.getItem('reset_email') || '';
      if (!email) {
        setError('Email not found. Please try forgot password again.');
        setIsLoading(false);
        return;
      }

      await authApi.resetPassword({ email, code: '', new_password: form.newPassword });
      setSuccess('Password reset successfully!');
      // Xóa email khỏi localStorage
      localStorage.removeItem('reset_email');
      setTimeout(() => {
        navigate({ to: '/auth/signin' });
      }, 2000);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(detail || 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthFormContainer title="Reset password">
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {success && <div className="text-green-600 mb-2">{success}</div>}
      <form onSubmit={handleSubmit} className="space-y-4 md:space-y-6">
        {/* New Password */}
        <div>
          <input
            type="password"
            name="newPassword"
            placeholder="New password"
            required
            value={form.newPassword}
            onChange={handleChange}
            className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
          />
        </div>

        {/* Confirm Password */}
        <div>
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm password"
            required
            value={form.confirmPassword}
            onChange={handleChange}
            className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-2.5 md:py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium text-sm md:text-base"
          disabled={isLoading}
        >
          {isLoading ? 'Resetting...' : 'Reset Password'}
          <span className="ml-2">→</span>
        </button>

        <div className="text-center">
          <Link to="/auth/signin" className="text-sm text-[#46287C] hover:underline">
            Back to Sign In
          </Link>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 