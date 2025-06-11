import { motion } from 'framer-motion';
import { MessageCircle, Users, Clock, ShieldCheck } from 'lucide-react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeatureCard = ({ icon, title, description }: FeatureCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    className="bg-[#F3F1FF] rounded-lg p-4 md:p-6"
  >
    <div className="flex items-start gap-2 md:gap-3">
      <div className="text-[#46287C]">
        {icon}
      </div>
      <div>
        <h3 className="text-[#46287C] font-semibold mb-1 md:mb-2 text-sm md:text-base">{title}</h3>
        <p className="text-gray-600 text-xs md:text-sm">{description}</p>
      </div>
    </div>
  </motion.div>
);

export const WhyChooseUs = () => {
  const features = [
    {
      icon: <Users className="w-5 h-5 md:w-6 md:h-6" />,
      title: "Personalized Guidance",
      description: "Receive tailored university and program suggestions based on your goals and interests."
    },
    {
      icon: <Clock className="w-5 h-5 md:w-6 md:h-6" />,
      title: "24/7 Chatbot Support",
      description: "Instantly get answers to your admissions questions anytime, anywhere."
    },
    {
      icon: <MessageCircle className="w-5 h-5 md:w-6 md:h-6" />,
      title: "Flexible Consultation",
      description: "Book one-on-one sessions with university reps at your convenience."
    },
    {
      icon: <ShieldCheck className="w-5 h-5 md:w-6 md:h-6" />,
      title: "Trusted Information",
      description: "Access up-to-date details from verified universities and official sources."
    }
  ];

  return (
    <section className="py-10 md:py-20 relative overflow-hidden">
      {/* Decorative Wave */}
      <div className="absolute right-0 top-10 md:top-20">
        <svg width="80" height="30" viewBox="0 0 120 40" fill="none" className="md:w-[120px] md:h-[40px]">
          <path d="M0 20C20 5 40 35 60 20C80 5 100 35 120 20" stroke="#E0E7FF" strokeWidth="2"/>
        </svg>
      </div>

      {/* Decorative Dots */}
      <div className="absolute right-0 top-0 grid grid-cols-4 md:grid-cols-6 gap-2 md:gap-4 opacity-20">
        {[...Array(24)].map((_, i) => (
          <div key={i} className="w-1.5 md:w-2 h-1.5 md:h-2 rounded-full bg-[#46287C]" />
        ))}
      </div>

      <div className="w-full max-w-[1200px] mx-auto px-2 md:px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-12 items-center">
          {/* Left Content */}
          <div>
            <motion.span
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-block bg-[#F3F1FF] text-[#46287C] px-3 md:px-4 py-1 rounded-full text-xs md:text-sm mb-4 md:mb-6"
            >
              WHY CHOOSE US
            </motion.span>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-2xl md:text-4xl font-bold text-[#46287C] leading-tight mb-4 md:mb-6"
            >
              Empowering Your<br />
              University Journey
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-gray-600 text-sm md:text-base mb-6 md:mb-8"
            >
              We help students confidently choose the right university and major through personalized advice, smart chatbot support, and trusted information from top institutions in Danang.
            </motion.p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
              {features.map((feature, index) => (
                <FeatureCard
                  key={index}
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                />
              ))}
            </div>
          </div>

          {/* Right Image */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="relative"
          >
            <img
              src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?ixlib=rb-4.0.3"
              alt="Students collaborating"
              className="w-full rounded-xl md:rounded-2xl"
            />
          </motion.div>
        </div>
      </div>
    </section>
  );
}; 