interface Appointment {
  id: string;
  title: string;
  date: string;
  time: string;
}

interface AppointmentListProps {
  activeTab: 'upcoming' | 'history';
}

const mockAppointments: Appointment[] = [
  {
    id: '1',
    title: 'VN-UK Institute for Research and Executive Education',
    date: '18 August 2025',
    time: '5:30 PM - 6:00 PM',
  },
  {
    id: '2',
    title: 'University of Economics - The University of Danang',
    date: '20 August 2025',
    time: '2:00 PM - 2:30 PM',
  },
];

export const AppointmentList = ({ activeTab }: AppointmentListProps) => {
  return (
    <div className="flex-1 p-4 md:p-6 md:ml-4">
      <h2 className="text-xl md:text-2xl font-bold text-[#332288] mb-4 md:mb-6">
        {activeTab === 'upcoming' ? 'Upcoming Appointments' : 'Appointments History'}
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        {mockAppointments.map((appointment) => (
          <div
            key={appointment.id}
            className="border-2 border-[#332288] rounded-lg p-4 md:p-6 w-full"
          >
            <h3 className="text-base md:text-lg font-semibold text-[#332288] line-clamp-2">
              {appointment.title}
            </h3>
            <p className="text-[#332288] text-sm mb-4">
              {appointment.date}, {appointment.time}
            </p>
            <div className="flex flex-row w-full mt-4 justify-end"> 
              <button className="bg-[#332288] text-white px-4 md:px-6 py-2 rounded-xl hover:bg-opacity-90 transition-colors text-sm md:text-base">
                VIEW DETAILS
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 