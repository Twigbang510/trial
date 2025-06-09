import { motion } from 'framer-motion';

interface AuthFormContainerProps {
  children: React.ReactNode;
  title: string;
  rightImages?: boolean;
}

export const AuthFormContainer = ({ children, title, rightImages = true }: AuthFormContainerProps) => {
  return (
    <div className="min-h-screen w-screen bg-white flex">
      {/* Left Form Section */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-4xl font-bold text-[#46287C] mb-2">{title}</h2>
            {children}
          </motion.div>
        </div>
      </div>

      {/* Right Images Section */}
      {rightImages && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="hidden lg:flex lg:w-1/2 p-8 flex-wrap gap-4 content-center justify-center"
        >
          <div className="w-[280px] h-[280px] rounded-2xl overflow-hidden">
            <img
              src="https://images.unsplash.com/photo-1541339907198-e08756dedf3f"
              alt="University building"
              className="w-full h-full object-cover"
            />
          </div>
          <div className="w-[280px] h-[380px] rounded-2xl overflow-hidden -mt-20">
            <img
              src="https://images.unsplash.com/photo-1523050854058-8df90110c9f1"
              alt="Student studying"
              className="w-full h-full object-cover"
            />
          </div>
          <div className="w-[280px] h-[280px] rounded-2xl overflow-hidden -mt-20">
            <img
              src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f"
              alt="Students collaborating"
              className="w-full h-full object-cover"
            />
          </div>
        </motion.div>
      )}
    </div>
  );
}; 