import { Outlet } from "@tanstack/react-router";
import { useAuth } from "@/hooks/useAuth";
import { isUserSuspended } from "@/lib/utils";
import AccountSuspended from "@/components/auth/AccountSuspended";

export default function RootLayout() {
  const { user, isAuthenticated } = useAuth();

  if (isAuthenticated && isUserSuspended(user)) {
    return <AccountSuspended user={user!} />;
  }

  return (
    <>
      <Outlet />
    </>
  );
}
