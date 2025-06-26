import { createFileRoute, redirect } from '@tanstack/react-router';
import { AppointmentPage } from '../components/appointment/AppointmentPage';
import { authService } from '../services/auth';

export const Route = createFileRoute('/appointment')({
  beforeLoad: async () => {
    const isAuthenticated = authService.isAuthenticated();
    if (!isAuthenticated) {
      throw redirect({to: '/auth/signin'})
    }
  },
  component: AppointmentPage,
}); 