import { useState } from 'react';
import { AppointmentSidebar } from './AppointmentSidebar';
import { AppointmentList } from './AppointmentList';
import { Navbar } from '../landing/Navbar';

type TabType = 'upcoming' | 'history';

export const AppointmentPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('upcoming');

  return (
    <div className="min-h-screen w-screen bg-white text-text-primary overflow-auto">
        <Navbar />  
      <div className="flex mt-[148px] h-[calc(100vh-148px)] px-4">
        <AppointmentSidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <AppointmentList activeTab={activeTab} />
      </div>
    </div>
  );
}; 