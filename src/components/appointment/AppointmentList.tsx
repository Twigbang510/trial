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
    <div className="flex-1 ml-4 p-6">
      <h2 className="text-2xl font-bold text-[#332288] mb-6">
        {activeTab === 'upcoming' ? 'Upcoming Appointments' : 'Appointments History'}
      </h2>
      <div className=" flex flex-row gap-4 flex-wrap items-center">
        {mockAppointments.map((appointment) => (
          <div
            key={appointment.id}
            className="border-2 border-[#332288] rounded-lg p-6 max-w-[342px]"
          >
            <h3 className="text-lg font-semibold text-[#332288]">
              {appointment.title}
            </h3>
            <p className="text-[#332288] text-sm mb-4">
              {appointment.date}, {appointment.time}
            </p>
            <div className="flex flex-row w-full mt-4 justify-end"> 
              <button className="bg-[#332288] text-white px-6 py-2 rounded-xl hover:bg-opacity-90 transition-colors">
                VIEW DETAILS
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 