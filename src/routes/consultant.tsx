import { createFileRoute } from '@tanstack/react-router';
import { ConsultantPage } from '../components/consultant/ConsultantPage';

export const Route = createFileRoute('/consultant')({
  component: ConsultantPage,
}); 