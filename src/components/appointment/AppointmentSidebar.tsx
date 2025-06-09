interface AppointmentSidebarProps {
  activeTab: 'upcoming' | 'history';
  onTabChange: (tab: 'upcoming' | 'history') => void;
}

export const AppointmentSidebar = ({ activeTab, onTabChange }: AppointmentSidebarProps) => {
  return (
    <div className="w-80 p-4">
      <div className="space-y-2">
        <button
          onClick={() => onTabChange('upcoming')}
          className={`w-full h-16 rounded-lg flex items-center justify-center text-lg font-medium transition-colors ${
            activeTab === 'upcoming'
              ? 'bg-[#332288] text-white'
              : 'bg-white text-[#332288] hover:bg-gray-50'
          }`}
        >
          Upcoming Appointments
        </button>
        <button
          onClick={() => onTabChange('history')}
          className={`w-full h-16 rounded-lg flex items-center justify-center text-lg font-medium transition-colors ${
            activeTab === 'history'
              ? 'bg-[#332288] text-white'
              : 'bg-white text-[#332288] hover:bg-gray-50'
          }`}
        >
          Appointments History
        </button>
      </div>
    </div>
  );
}; 