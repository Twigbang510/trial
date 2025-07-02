import { useRef, useState } from 'react';
import { AuthFormContainer } from './AuthFormContainer';
import { useNavigate } from '@tanstack/react-router';
import authApi from '@/lib/api/auth.api';

export const EmailVerification = () => {
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const navigate = useNavigate();

  const handleChange = (index: number, value: string) => {
    if (value.length > 1) return; // Only allow single digit

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    // Handle backspace
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    const verificationCode = code.join('');
    if (verificationCode.length !== 6) {
      setError('Please enter the complete 6-digit code');
      setIsLoading(false);
      return;
    }

    try {
      // Lấy email từ localStorage (đã lưu khi gửi forgot password)
      const email = localStorage.getItem('reset_email') || '';
      if (!email) {
        setError('Email not found. Please try forgot password again.');
        setIsLoading(false);
        return;
      }

      await authApi.verifyCode({ email, code: verificationCode });
      navigate({ to: '/auth/reset-password' });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(detail || 'Invalid verification code');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthFormContainer title="Verify email">
      <div className="mb-6 md:mb-8">
        <p className="text-sm md:text-base text-gray-600 text-center md:text-left">
          We've sent a verification code to your email address. Please enter the code below to verify your account.
        </p>
      </div>
      {error && <div className="text-red-500 mb-2 text-center">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4 md:space-y-6">
        <div className="flex gap-2 md:gap-3 justify-center">
          {code.map((digit, index) => (
            <input
              key={index}
              type="text"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              ref={(el) => (inputRefs.current[index] = el)}
              className="w-10 h-10 md:w-12 md:h-12 text-center text-lg md:text-xl font-semibold bg-[#F4F4F4] rounded-lg outline-none text-gray-900"
              required
            />
          ))}
        </div>

        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-2.5 md:py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium text-sm md:text-base"
          disabled={isLoading}
        >
          {isLoading ? 'Verifying...' : 'Verify Email'}
          <span className="ml-2">→</span>
        </button>

        <div className="text-center">
          <button
            type="button"
            className="text-sm text-[#46287C] hover:underline"
          >
            Resend Code
          </button>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 