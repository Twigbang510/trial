import { createFileRoute } from '@tanstack/react-router';
import { LandingPage } from '../components/landing/LandingPage';
import { authService } from '../services/auth';
import { redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: LandingPage,
  beforeLoad: async () => {
    const isAuthenticated = authService.isAuthenticated();
    if (!isAuthenticated) {
      throw redirect({to: '/auth/signin'})
    }
  },
}); 