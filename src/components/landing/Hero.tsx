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
    <div className="w-full h-full p-3 md:p-4">
      <div className="w-24 md:w-32 h-1.5 md:h-2 bg-primary/20 rounded-full mb-1.5 md:mb-2" />
      <div className="w-16 md:w-24 h-1.5 md:h-2 bg-white/10 rounded-full" />
    </div>
  </motion.div>
);

const TagLine = () => (
  <motion.div
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay: 0.2 }}
    className="inline-flex items-center gap-2 bg-white backdrop-blur-sm border border-white/10 rounded-xl px-3 md:px-4 py-1.5 md:py-2 mb-5 md:mb-7"
  >
    <span className="text-primary text-lg md:text-xl">✦</span>
    <span className="text-black text-sm md:text-base">Generative Business Intelligence for Analysts</span>
  </motion.div>
);

export const Hero = () => {
  return (
    <section className="relative min-h-screen pt-20 md:pt-28 pb-10 md:pb-20 overflow-hidden">
      <div className="w-full max-w-[1200px] mx-auto px-2 md:px-4 grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-12 items-center">
        {/* Left Content */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="md:flex md:flex-col items-center md:items-start justify-center"
        >
          <span className="text-[#46287C] text-sm md:text-base mb-3 md:mb-4">WELCOME TO TRIAL!</span>
          
          <h1 className="text-3xl md:text-5xl font-bold text-[#46287C] leading-tight mb-4 md:mb-6">
            Find Your Future,{" "}
            <span className="block">Build Your Life</span>
          </h1>
          
          <div className="space-y-2 md:space-y-4 mb-6 md:mb-8">
            <p className="text-gray-600 text-sm md:text-base">24/7 answers to your admissions questions.</p>
            <p className="text-gray-600 text-sm md:text-base">Let our agent guide your journey.</p>
          </div>

          <button className="flex items-center gap-2 bg-[#46287C] text-white px-6 md:px-8 py-3 md:py-4 rounded-full w-fit hover:bg-[#46287C]/90 transition-all text-sm md:text-base">
            Chat Now
            <ArrowRight className="w-4 h-4 md:w-5 md:h-5" />
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
            className="w-full h-[400px] md:h-[600px] object-cover rounded-xl md:rounded-2xl relative z-10"
          />
          
          {/* Decorative dots */}
          <div className="absolute -left-8 md:-left-14 bottom-4 md:bottom-8 w-16 md:w-24 h-16 md:h-24 grid grid-cols-3 gap-1 md:gap-2 -z-9">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="w-1.5 md:w-2 h-1.5 md:h-2 rounded-full bg-[#46287C]/20" />
            ))}
          </div>
          <div className="absolute -left-8 md:-left-14 bottom-[calc(4rem+4px)] md:bottom-[calc(8rem+8px)] w-16 md:w-24 h-16 md:h-24 grid grid-cols-3 gap-1 md:gap-2 -z-9">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="w-1.5 md:w-2 h-1.5 md:h-2 rounded-full bg-[#46287C]/20" />
            ))}
          </div>
          <div className="absolute -left-8 md:-left-14 bottom-[calc(7rem+6px)] md:bottom-[calc(14rem+12px)] w-16 md:w-24 h-16 md:h-24 grid grid-cols-3 gap-1 md:gap-2 -z-9">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="w-1.5 md:w-2 h-1.5 md:h-2 rounded-full bg-[#46287C]/20" />
            ))}
          </div>
          <div className="absolute -left-8 md:-left-14 bottom-[calc(10rem+8px)] md:bottom-[calc(20rem+16px)] w-16 md:w-24 h-16 md:h-24 grid grid-cols-3 gap-1 md:gap-2 -z-9">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="w-1.5 md:w-2 h-1.5 md:h-2 rounded-full bg-[#46287C]/20" />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}; 