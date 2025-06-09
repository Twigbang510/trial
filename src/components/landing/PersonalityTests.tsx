import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

const TestButton = ({ children }: { children: React.ReactNode }) => (
  <button className="flex items-center gap-2 bg-[#46287C] text-white px-8 py-4 rounded-full hover:bg-[#46287C]/90 transition-all">
    {children}
    <ArrowRight className="w-5 h-5" />
  </button>
);

export const PersonalityTests = () => {
  return (
    <section className="py-20">
      <div className="w-full max-w-[1200px] mx-auto px-4 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Images Grid */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="relative grid grid-cols-2 gap-4"
        >
          {/* Decorative Element */}
          <div className="absolute -left-8 -top-8">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <path d="M20 0L24.4903 15.5097L40 20L24.4903 24.4903L20 40L15.5097 24.4903L0 20L15.5097 15.5097L20 0Z" fill="#4ADE80"/>
            </svg>
          </div>
          
          {/* Images */}
          <div className="space-y-4">
            <img
              src="https://images.unsplash.com/photo-1541339907198-e08756dedf3f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80"
              alt="University building"
              className="w-full h-48 object-cover rounded-lg"
            />
            <img
              src="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80"
              alt="Students studying"
              className="w-full h-64 object-cover rounded-lg"
            />
          </div>
          <div className="pt-8">
            <img
              src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1471&q=80"
              alt="Students collaborating"
              className="w-full h-72 object-cover rounded-lg"
            />
          </div>
        </motion.div>

        {/* Right Content */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col"
        >
          <h2 className="text-4xl font-bold text-[#46287C] leading-tight mb-6">
            Discover Your Strengths
            <span className="block">With MBTI, Holland</span>
            <span className="block">Understand Yourself Better</span>
          </h2>

          <p className="text-gray-600 mb-8">
            These tests help you explore your traits, improve your career choices, and communicate more effectively. It's the first step to finding the learning and career path that truly fits you.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <TestButton>MBTI Test</TestButton>
            <TestButton>Holland Test</TestButton>
          </div>
        </motion.div>
      </div>
    </section>
  );
}; 