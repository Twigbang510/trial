import { createFileRoute, redirect } from '@tanstack/react-router';
import { ConsultantPage } from '../components/consultant/ConsultantPage';
import { authService } from '../services/auth';

export const Route = createFileRoute('/consultant')({
  beforeLoad: async () => {
    const isAuthenticated = authService.isAuthenticated();
    if (!isAuthenticated) {
      throw redirect({to: '/auth/signin'})
    }
  },
  component: ConsultantPage,
}); 