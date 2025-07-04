interface AppointmentSidebarProps {
  activeTab: 'upcoming' | 'history';
  onTabChange: (tab: 'upcoming' | 'history') => void;
}

export const AppointmentSidebar = ({ activeTab, onTabChange }: AppointmentSidebarProps) => {
  return (
    <div className="w-full md:w-80 p-2 md:p-4">
      <div className="flex md:flex-col gap-2 md:space-y-2">
        <button
          onClick={() => onTabChange('upcoming')}
          className={`w-full h-12 md:h-16 rounded-lg flex items-center justify-center text-base md:text-lg font-medium transition-colors ${
            activeTab === 'upcoming'
              ? 'bg-[#332288] text-white shadow-md'
              : 'bg-white text-[#332288] hover:bg-gray-50 border border-[#332288]/20'
          }`}
        >
          Upcoming
        </button>
        <button
          onClick={() => onTabChange('history')}
          className={`w-full h-12 md:h-16 rounded-lg flex items-center justify-center text-base md:text-lg font-medium transition-colors ${
            activeTab === 'history'
              ? 'bg-[#332288] text-white shadow-md'
              : 'bg-white text-[#332288] hover:bg-gray-50 border border-[#332288]/20'
          }`}
        >
          History
        </button>
      </div>
    </div>
  );
}; 