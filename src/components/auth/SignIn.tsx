import { Link, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import { Eye, EyeOff, Facebook, Mail } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { AuthFormContainer } from './AuthFormContainer';

export const SignIn = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await login(email, password);
      window.location.href = '/';
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <AuthFormContainer title="Sign in">
      <div className="mb-6 md:mb-8">
        <p className="text-sm md:text-base text-gray-600">
          Don't have account{' '}
          <Link to="/auth/signup" className="text-[#46287C] hover:underline">
            Create Account
          </Link>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3 md:space-y-4">
        {/* Email */}
        <div>
          <input
            type="email"
            name="email"
            placeholder="Email address"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
          />
        </div>

        {/* Password */}
        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            name="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
          >
            {showPassword ? <EyeOff className="w-4 h-4 md:w-5 md:h-5" /> : <Eye className="w-4 h-4 md:w-5 md:h-5" />}
          </button>
        </div>

        {/* Remember Me and Forgot Password */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="remember"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 text-[#46287C] focus:ring-[#46287C] border-gray-300 rounded"
            />
            <label htmlFor="remember" className="ml-2 text-sm text-gray-600">
              Remember Me
            </label>
          </div>
          <Link to="/auth/forgot-password" className="text-sm text-[#46287C] hover:underline">
            Forget password
          </Link>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center px-4 py-2.5 md:py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium mt-4 md:mt-6 disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
        >
          {isLoading ? 'Signing in...' : 'Sign In'}
          <span className="ml-2">→</span>
        </button>

        {/* Social Sign In */}
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600 mb-3 md:mb-4">or</p>
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
        </div>
      </form>
    </AuthFormContainer>
  );
}; 