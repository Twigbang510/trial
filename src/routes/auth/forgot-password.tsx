import { createFileRoute } from '@tanstack/react-router'
import { ResetPassword } from '@/components/auth/ResetPassword'

export const Route = createFileRoute('/auth/forgot-password')({
  component: ResetPassword,
})
