import { Link } from '@tanstack/react-router';
import { Facebook, Mail } from 'lucide-react';
import { AuthFormContainer } from './AuthFormContainer';
import { useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import authApi from '@/lib/api/auth.api';

export const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);
    try {
      await authApi.forgotPassword({ email });
      // Lưu email để dùng ở trang verification
      localStorage.setItem('reset_email', email);
      setSuccess('Verification code sent to your email.');
      setTimeout(() => {
        navigate({ to: '/auth/verification' });
      }, 2000);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(detail || 'Failed to send reset instructions');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthFormContainer title="Reset password">
      <div className='flex flex-col mt-4 mb-6 md:mb-8 align-center justify-center gap-2'>
        <div className='flex flex-row items-center gap-2 align-center' >     
          <p className="text-sm md:text-base text-gray-600">Go back to</p>
          <Link to="/auth/signin" className="text-sm text-[#46287C] flex items-center gap-2 hover:gap-3 transition-all hover:underline">
            Sign In   
          </Link>
        </div>
        {/* Create Account */}
        <div>
          <p className="text-sm text-gray-600 flex gap-2">
            Don't have an account?{' '}
            <Link to="/auth/signup" className="text-[#46287C] font-medium flex items-center gap-2 hover:gap-3 transition-all hover:underline">
              Create Account
            </Link>
          </p>
        </div>
      </div>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {success && <div className="text-green-600 mb-2">{success}</div>}
      <form onSubmit={handleSubmit} className="space-y-4 md:space-y-6">
        {/* Email */}
        <div>
          <input
            type="email"
            name="email"
            placeholder="Email address"
            required
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
          />
        </div>
        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-2.5 md:py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium text-sm md:text-base"
          disabled={isLoading}
        >
          {isLoading ? 'Sending...' : 'Send Reset Instructions'}
          <span className="ml-2">→</span>
        </button>
        {/* Divider */}
        <div className="relative my-6 md:my-8">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or</span>
          </div>
        </div>
        {/* Social Sign In */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
          <button
            type="button"
            className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Facebook className="h-4 w-4 md:h-5 md:w-5 text-[#1877F2]" />
            <span className="text-sm md:text-base text-gray-700">Sign in with Facebook</span>
          </button>
          <button
            type="button"
            className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Mail className="h-4 w-4 md:h-5 md:w-5 text-[#DB4437]" />
            <span className="text-sm md:text-base text-gray-700">Sign in with Google</span>
          </button>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 