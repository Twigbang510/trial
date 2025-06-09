import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { Eye, EyeOff, Facebook, Mail } from 'lucide-react';
import { AuthFormContainer } from './AuthFormContainer';

export const SignUp = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
  };

  return (
    <AuthFormContainer title="Create account.">
      <div className="mb-8">
        <p className="text-gray-600">
          Already have an account?{' '}
          <Link to="/auth/signin" className="text-[#46287C] font-medium">
            Log In
          </Link>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 ">
        <div className='grid grid-cols-2 gap-4'>
        {/* Full Name */}
        <div>
          <input
            type="text"
            name="fullName"
            placeholder="Full Name"
            required
            className="w-full px-4 py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500"
          />
        </div>

        {/* Username */}
        <div>
          <input
            type="text"
            name="username"
            placeholder="Username"
            required
            className="w-full px-4 py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500"
          />
        </div>
        </div>
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

        {/* Confirm Password */}
        <div className="relative">
          <input
            type={showConfirmPassword ? "text" : "password"}
            name="confirmPassword"
            placeholder="Confirm Password"
            required
            className="w-full px-4 py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
          >
            {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>

        {/* Terms and Conditions */}
        <div className="flex items-start mt-2 align-center">
          <input
            type="checkbox"
            id="terms"
            checked={acceptTerms}
            onChange={(e) => setAcceptTerms(e.target.checked)}
            className="mt-1 h-4 w-4 text-white focus:ring-white border-white rounded bg-transparent checked:bg-white checked:border-white"
          />
          <label htmlFor="terms" className="ml-2 text-sm text-gray-600">
            I've read and agree with your{' '}
            <Link to="/" className="text-[#332288]">
              Terms of Services
            </Link>
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium mt-6"
        >
          Create Account
          <span className="ml-2">→</span>
        </button>

        {/* Social Sign Up */}
        <div className="mt-4 text-center text-gray-600">
          <p className="mb-4">or</p>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Facebook className="h-5 w-5 text-[#1877F2]" />
            </button>
            <button
              type="button"
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors gap-1"
            >
              <Mail className="h-5 w-5 text-[#DB4437]" />
              <span>Sign up with Google</span>
            </button>
          </div>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 