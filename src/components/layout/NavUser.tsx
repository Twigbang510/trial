import { Bell } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const NavUser = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  // Ưu tiên full_name > username > email > '?'
  const displayName = user.full_name || user.username || user.email || "?";
  const avatarChar = displayName.charAt(0).toUpperCase();

  return (
    <div className="flex items-center gap-4">
      {/* Notification Bell */}
      <button className="relative p-2 text-gray-600 hover:text-gray-900">
        <Bell className="w-6 h-6" />
        <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
      </button>

      {/* User Avatar */}
      <div className="relative group">
        <button className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-[#46287C] flex items-center justify-center text-white">
            {avatarChar}
          </div>
        </button>

        {/* Dropdown Menu */}
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 hidden group-hover:block">
          <div className="px-4 py-2 text-sm text-gray-700 border-b">
            <p className="font-medium">{displayName}</p>
            <p className="text-gray-500">{user.email}</p>
          </div>
          <button
            onClick={logout}
            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}; 