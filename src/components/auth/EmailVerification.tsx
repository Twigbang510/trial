import { useRef, useState } from 'react';
import { AuthFormContainer } from './AuthFormContainer';

export const EmailVerification = () => {
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle verification code submission
  };

  return (
    <AuthFormContainer title="Verify email">
      <div className="mb-8">
        <p className="text-gray-600">
          We've sent a verification code to your email address. Please enter the code below to verify your account.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex gap-3 justify-center">
          {code.map((digit, index) => (
            <input
              key={index}
              type="text"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              ref={(el) => (inputRefs.current[index] = el)}
              className="w-12 h-12 text-center text-xl font-semibold bg-[#F4F4F4] rounded-lg outline-none text-gray-900"
              required
            />
          ))}
        </div>

        <button
          type="submit"
          className="w-full flex items-center justify-center px-4 py-3 bg-[#46287C] text-white rounded-lg hover:bg-[#46287C]/90 transition-colors font-medium"
        >
          Verify Email
          <span className="ml-2">→</span>
        </button>

        <div className="text-center">
          <button
            type="button"
            className="text-sm text-[#46287C]"
          >
            Resend Code
          </button>
        </div>
      </form>
    </AuthFormContainer>
  );
}; 