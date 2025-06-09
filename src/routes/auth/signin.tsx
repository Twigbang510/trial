import { createFileRoute } from '@tanstack/react-router'
import { SignIn } from '@/components/auth/SignIn'

export const Route = createFileRoute('/auth/signin')({
  component: SignIn,
})
