import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

const FloatingCard = ({ className = '', delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ 
      opacity: 1, 
      y: [0, -10, 0],
      transition: {
        y: {
          repeat: Infinity,
          duration: 3,
          ease: "easeInOut",
        },
        opacity: {
          duration: 0.5,
        }
      }
    }}
    transition={{ delay }}
    className={`absolute bg-gradient-card backdrop-blur-sm border border-white/10 rounded-lg shadow-lg ${className}`}
  >
    <div className="w-full h-full p-4">
      <div className="w-32 h-2 bg-primary/20 rounded-full mb-2" />
      <div className="w-24 h-2 bg-white/10 rounded-full" />
    </div>
  </motion.div>
);

const TagLine = () => (
  <motion.div
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay: 0.2 }}
    className="inline-flex items-center gap-2 bg-white backdrop-blur-sm border border-white/10 rounded-xl px-4 py-2 mb-7"
  >
    <span className="text-primary text-xl">✦</span>
    <span className="text-black">Generative Business Intelligence for Analysts</span>
  </motion.div>
);

export const Hero = () => {
  return (
    <section className="relative min-h-screen pt-28 pb-20 overflow-hidden">
      <div className="w-full max-w-[1200px] mx-auto px-4 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Content */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col"
        >
          <span className="text-[#46287C] mb-4">WELCOME TO TRIAL!</span>
          
          <h1 className="text-5xl font-bold text-[#46287C] leading-tight mb-6">
            Find Your Future,{" "}
            <span className="block">Build Your Life</span>
          </h1>
          
          <div className="space-y-4 mb-8">
            <p className="text-gray-600">24/7 answers to your admissions questions.</p>
            <p className="text-gray-600">Let our agent guide your journey.</p>
          </div>

          <button className="flex items-center gap-2 bg-[#46287C] text-white px-8 py-4 rounded-full w-fit hover:bg-[#46287C]/90 transition-all">
            Chat Now
            <ArrowRight className="w-5 h-5" />
          </button>
        </motion.div>

        {/* Right Image */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative"
        >
          <img
            src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80"
            alt="Students in library"
            className="w-full h-[600px] object-cover rounded-2xl"
          />
          
          {/* Decorative dots */}
          <div className="absolute -right-8 top-8 w-24 h-24 grid grid-cols-3 gap-2">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="w-2 h-2 rounded-full bg-[#46287C]/20" />
            ))}
          </div>
          <div className="absolute -left-8 bottom-8 w-24 h-24 grid grid-cols-3 gap-2">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="w-2 h-2 rounded-full bg-[#46287C]/20" />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}; 