import { createFileRoute } from '@tanstack/react-router';
import { AppointmentPage } from '../components/appointment/AppointmentPage';

export const Route = createFileRoute('/appointment')({
  component: AppointmentPage,
}); 