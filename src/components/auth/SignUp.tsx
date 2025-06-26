import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { Eye, EyeOff, Facebook, Mail } from 'lucide-react';
import { AuthFormContainer } from './AuthFormContainer';
import authApi from '@/lib/api/auth.api';

export const SignUp = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [form, setForm] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!acceptTerms) {
      setError('You must accept the terms.');
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    try {
      console.log("form", form);
      await authApi.registerAccount({
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        username: form.username,
      });
      setSuccess('Account created! You can now log in.');
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg).join(', '));
      } else {
        setError(detail || 'Registration failed');
      }
    }
  };

  return (
    <AuthFormContainer title="Create account.">
      <div className="mb-6 md:mb-8">
        <p className="text-sm md:text-base text-gray-600">
          Already have an account?{' '}
          <Link to="/auth/signin" className="text-[#46287C] font-medium hover:underline">
            Log In
          </Link>
        </p>
      </div>
      {error && (
        <div className="text-red-500 mb-2">
          {Array.isArray(error)
            ? error.map((e, idx) => (
                <div key={idx}>{e.msg || JSON.stringify(e)}</div>
              ))
            : error}
        </div>
      )}
      {success && <div className="text-green-600 mb-2">{success}</div>}
      <form onSubmit={handleSubmit} className="space-y-3 md:space-y-4">
        <div className='grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4'>
          {/* Full Name */}
          <div>
            <input
              type="text"
              name="full_name"
              placeholder="Full Name"
              required
              value={form.full_name}
              onChange={handleChange}
              className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
            />
          </div>
          {/* Username */}
          <div>
            <input
              type="text"
              name="username"
              placeholder="Username"
              required
              value={form.username}
              onChange={handleChange}
              className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
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
            value={form.email}
            onChange={handleChange}
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
            value={form.password}
            onChange={handleChange}
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
        {/* Confirm Password */}
        <div className="relative">
          <input
            type={showConfirmPassword ? "text" : "password"}
            name="confirmPassword"
            placeholder="Confirm Password"
            required
            value={form.confirmPassword}
            onChange={handleChange}
            className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
          >
            {showConfirmPassword ? <EyeOff className="w-4 h-4 md:w-5 md:h-5" /> : <Eye className="w-4 h-4 md:w-5 md:h-5" />}
          </button>
        </div>
        {/* Terms and Conditions */}
        <div className="flex items-start mt-2 items-center">
          <input
            type="checkbox"
            id="terms"
            checked={acceptTerms}
            onChange={(e) => setAcceptTerms(e.target.checked)}
            className="mt-1 h-4 w-4 text-white focus:ring-white border-white rounded bg-transparent checked:bg-white checked:border-white"
          />
          <label htmlFor="terms" className="ml-2 text-xs md:text-sm text-gray-600 text-bottom">
            I've read and agree with your{' '}
            <Link to="/" className="text-[#332288] hover:underline">
              Terms of Services
            </Link>
          </label>
        </div>
        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-2.5 md:py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium mt-4 md:mt-6 text-sm md:text-base"
        >
          Create Account
          <span className="ml-2">→</span>
        </button>
        {/* Social Sign Up */}
        <div className="mt-4 text-center text-gray-600">
          <p className="text-sm mb-3 md:mb-4">or</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
            <button
              type="button"
              className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Facebook className="h-4 w-4 md:h-5 md:w-5 text-[#1877F2]" />
              <span className="text-sm md:text-base text-gray-700">Sign up with Facebook</span>
            </button>
            <button
              type="button"
              className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Mail className="h-4 w-4 md:h-5 md:w-5 text-[#DB4437]" />
              <span className="text-sm md:text-base text-gray-700">Sign up with Google</span>
            </button>
          </div>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 