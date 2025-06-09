import { Link } from '@tanstack/react-router';
import { AuthFormContainer } from './AuthFormContainer';

export const ForgotPassword = () => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
  };

  return (
    <AuthFormContainer title="Reset password">
      <div className="mb-8">
        <p className="text-gray-600">
          Enter your email address and we'll send you instructions to reset your password.
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

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium mt-6"
        >
          Send Reset Instructions
          <span className="ml-2">→</span>
        </button>

        {/* Back to Sign In */}
        <div className="text-center mt-4">
          <Link to="/auth/signin" className="text-sm text-[#46287C]">
            Back to Sign In
          </Link>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 