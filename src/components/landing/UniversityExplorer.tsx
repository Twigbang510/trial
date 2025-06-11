import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

interface UniversityCardProps {
  name: string;
  type: string;
  programs: string[];
  address: string;
}

const UniversityCard = ({ name, type, programs, address }: UniversityCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    className="bg-gray-50 rounded-xl md:rounded-2xl overflow-hidden"
  >
    <div className="relative">
      <img
        src="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3"
        alt={name}
        className="w-full h-40 md:h-48 object-cover"
      />
      <span className="absolute top-3 md:top-4 left-3 md:left-4 bg-[#FF7F50] text-white px-2 py-1 rounded-md text-xs md:text-sm">
        Top Rated
      </span>
    </div>
    
    <div className="p-4 md:p-6">
      <h3 className="text-lg md:text-xl font-bold text-[#46287C] mb-1 line-clamp-2">{name}</h3>
      
      <div className="space-y-3 md:space-y-4">
        <div>
          <p className="text-sm md:text-base text-gray-600">• Type: {type}</p>
        </div>
        
        <div>
          <p className="text-sm md:text-base text-gray-600">• Programs Offered:</p>
          <p className="text-sm md:text-base text-gray-600 mt-1 line-clamp-2">
            {programs.join(' - ')}
          </p>
        </div>
        
        <div>
          <p className="text-sm md:text-base text-gray-600">• Address: {address}</p>
        </div>
      </div>

      <button className="flex items-center gap-2 text-[#46287C] mt-4 md:mt-6 hover:gap-3 transition-all ml-auto bg-[#332288] text-white px-3 md:px-4 py-1.5 md:py-2 rounded-full text-sm md:text-base">
        More
        <ArrowRight className="w-4 h-4 md:w-5 md:h-5" />
      </button>
    </div>
  </motion.div>
);

export const UniversityExplorer = () => {
  const universities = [
    {
      name: "University Of Economics The University Of Danang (DUE)",
      type: "Public University",
      programs: ["Undergraduate", "Postgraduate", "Continuing Education", "International Joint Programs", "Transfer Programs"],
      address: "71 Ngu Hanh Son Street, Danang"
    },
    {
      name: "University Of Economics The University Of Danang (DUE)",
      type: "Public University",
      programs: ["Undergraduate", "Postgraduate", "Continuing Education", "International Joint Programs", "Transfer Programs"],
      address: "71 Ngu Hanh Son Street, Danang"
    },
    {
      name: "University Of Economics The University Of Danang (DUE)",
      type: "Public University",
      programs: ["Undergraduate", "Postgraduate", "Continuing Education", "International Joint Programs", "Transfer Programs"],
      address: "71 Ngu Hanh Son Street, Danang"
    }
  ];

  return (
    <section className="py-10 md:py-20">
      <div className="w-full max-w-[1200px] mx-auto px-2 md:px-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 md:gap-0 mb-8 md:mb-12">
          <h2 className="text-2xl md:text-4xl font-bold text-[#46287C]">
            Explore Universities In<br />
            Danang
          </h2>
          
          <button className="flex items-center gap-2 bg-[#46287C] text-white px-4 md:px-6 py-2 md:py-3 rounded-full hover:gap-3 transition-all text-sm md:text-base">
            Explore Universities
            <ArrowRight className="w-4 h-4 md:w-5 md:h-5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          {universities.map((university, index) => (
            <UniversityCard key={index} {...university} />
          ))}
        </div>
      </div>
    </section>
  );
}; 