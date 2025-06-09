import { createFileRoute, redirect } from '@tanstack/react-router';
import { LandingPage } from '../components/landing/LandingPage';
import { authService } from '../services/auth';

export const Route = createFileRoute('/')({
  beforeLoad: async () => {
    const isAuthenticated = authService.isAuthenticated();
    if (!isAuthenticated) {
      throw redirect({to: '/auth/signin'})
    }
  },
  component: LandingPage,
}); 