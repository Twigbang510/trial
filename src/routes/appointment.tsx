import { createFileRoute } from '@tanstack/react-router';
import { useAuth } from '@/hooks/useAuth';
import { Navigate } from '@tanstack/react-router';
import { AppointmentPage } from '@/components/appointment/AppointmentPage';
import AccountSuspended from '@/components/auth/AccountSuspended';
import { isUserSuspended } from '@/lib/utils';

export const Route = createFileRoute('/appointment')({
  component: AppointmentPageRoute,
});

function AppointmentPageRoute() {
  const { user, isAuthenticated, isLoading } = useAuth();

  // Show loading spinner while checking auth state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 border-2 border-[#332288] border-t-transparent rounded-full animate-spin"></div>
          <span className="text-[#332288] font-medium">Loading...</span>
        </div>
      </div>
    );
  }

  // Only redirect to signin after loading is complete
  if (!isAuthenticated) {
    return <Navigate to="/auth/signin" />;
  }

  // Check if account is suspended (inactive OR violation count >= 5)
  if (isUserSuspended(user)) {
    return <AccountSuspended user={user!} />;
  }

  return <AppointmentPage />;
} 