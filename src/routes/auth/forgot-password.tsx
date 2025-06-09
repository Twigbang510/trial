import { createFileRoute } from '@tanstack/react-router'
import { ForgotPassword } from '@/components/auth/ForgotPassword'

export const Route = createFileRoute('/auth/forgot-password')({
  component: ForgotPassword,
})
