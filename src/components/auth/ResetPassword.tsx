import { Link } from '@tanstack/react-router';
import { AuthFormContainer } from './AuthFormContainer';
import { useNavigate } from '@tanstack/react-router';

export const ResetPassword = () => {
  const navigate = useNavigate();
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate({ to: '/auth/signin' });
  };

  return (
    <AuthFormContainer title="Reset password">
      <form onSubmit={handleSubmit} className="space-y-4 md:space-y-6">
        {/* New Password */}
        <div>
          <input
            type="password"
            name="newPassword"
            placeholder="New password"
            required
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
            className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-[#F4F4F4] rounded-lg outline-none text-gray-900 placeholder-gray-500 text-sm md:text-base"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-2.5 md:py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium text-sm md:text-base"
        >
          Reset Password
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