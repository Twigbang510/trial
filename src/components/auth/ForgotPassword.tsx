import { Link } from '@tanstack/react-router';
import { ArrowLeft, ArrowRight, Facebook, Mail } from 'lucide-react';
import { AuthFormContainer } from './AuthFormContainer';
import { useNavigate } from '@tanstack/react-router';

export const ForgotPassword = () => {
  const navigate = useNavigate();
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate({ to: '/auth/verification' });
  };

  return (
    <AuthFormContainer title="Reset password">
      <div className='flex flex-col mt-4 mb-8 align-center justify-center gap-2'>
      <div className='flex flex-row items-center gap-2 align-center' >     
          <p className="text-gray-600">Go back to</p>
          <Link to="/auth/signin" className="text-sm text-[#46287C] flex items-center gap-2 hover:gap-3 transition-all ">
            Sign In   
          </Link>
        </div>
        {/* Create Account */}
        <div>
          <p className="text-sm text-gray-600 flex gap-2">
            Don't have an account?{' '}
            <Link to="/auth/signup" className="text-[#46287C] font-medium flex items-center gap-2 hover:gap-3 transition-all">
              Create Account
            </Link>
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email */}
        <div>
          <input
            type="email"
            name="email"
            placeholder="Email address"
            required
            className="w-full px-4 py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium"
          onClick={handleSubmit}  
        >
          Send Reset Instructions
          <span className="ml-2">→</span>
        </button>

        {/* Divider */}
        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or</span>
          </div>
        </div>

        {/* Social Sign In */}
        <div className="grid grid-cols-2 gap-4">
          <button
            type="button"
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Facebook className="h-5 w-5 text-[#1877F2]" />
            <span className="text-gray-700">Sign in with Facebook</span>
          </button>
          <button
            type="button"
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Mail className="h-5 w-5 text-[#DB4437]" />
            <span className="text-gray-700">Sign in with Google</span>
          </button>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 