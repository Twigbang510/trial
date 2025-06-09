import { createFileRoute, redirect } from '@tanstack/react-router';
import { LandingPage } from '../components/landing/LandingPage';

export const Route = createFileRoute('/')({
  beforeLoad: async () => {
    const currentUser = false;
    if (!currentUser) {
      throw redirect({to: '/auth/signin'})
    }
  },
  component: LandingPage,
}); 