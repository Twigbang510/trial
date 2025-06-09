import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { Eye, EyeOff } from 'lucide-react';
import { AuthFormContainer } from './AuthFormContainer';

export const SignIn = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
  };

  return (
    <AuthFormContainer title="Sign in">
      <div className="mb-8">
        <p className="text-gray-600">
          Don't have account{' '}
          <Link to="/auth/signup" className="text-[#46287C]">
            Create Account
          </Link>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
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

        {/* Password */}
        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            name="password"
            placeholder="Password"
            required
            className="w-full px-4 py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>

        {/* Remember Me and Forgot Password */}
        <div className="flex items-center justify-between">
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
          <Link to="/auth/forgot-password" className="text-sm text-[#46287C]">
            Forget password
          </Link>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium mt-6"
        >
          Sign In
          <span className="ml-2">→</span>
        </button>

        {/* Social Sign In */}
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600 mb-4">or</p>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <img src="/facebook-icon.png" alt="Facebook" className="w-5 h-5" />
              <span className="text-gray-700">Sign in with Facebook</span>
            </button>
            <button
              type="button"
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <img src="/google-icon.png" alt="Google" className="w-5 h-5" />
              <span className="text-gray-700">Sign in with Google</span>
            </button>
          </div>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 