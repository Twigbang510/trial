import { createFileRoute } from '@tanstack/react-router'
import { SignUp } from '@/components/auth/SignUp'

export const Route = createFileRoute('/auth/signup')({
  component: SignUp,
})
