import { createFileRoute } from '@tanstack/react-router';
import { ResetPassword } from '../../components/auth/ResetPassword';

export const Route = createFileRoute('/auth/reset-password')({
  component: ResetPassword,
}); 