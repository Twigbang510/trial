import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Phone, Mail, ArrowRight, Menu, X } from "lucide-react";
import { NavUser } from '../layout/NavUser';
import { useAuth } from "../../hooks/useAuth";
import { useState } from "react";

const NavLink = ({ children, href }: { children: React.ReactNode; href: string }) => (
  <Link
    to={href}
    className="transition-colors text-[#0E2A46] hover:text-primary [&.active]:text-[#009988] [&.active]:border [&.active]:border-[#009988] [&.active]:rounded-[200px] [&.active]:px-3 [&.active]:py-1 text-sm md:text-base"
  >
    {children}
  </Link>
);

export const Navbar = () => {
  const {user} = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <>
      {/* Top Contact Section */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 bg-[#332288] text-white"
      >
        <div className="w-full flex justify-center px-2 md:px-4">
          <div className="w-full max-w-[1200px] flex items-center justify-between h-10 md:h-12">
            {/* Contact Info */}
            <div className="flex items-center gap-4 md:gap-8">
              <div className="flex items-center gap-1 md:gap-2">
                <Phone className="w-3 h-3 md:w-4 md:h-4" />
                <span className="text-xs md:text-sm">(84) 348 962 536</span>
              </div>
              <div className="flex items-center gap-1 md:gap-2">
                <Mail className="w-3 h-3 md:w-4 md:h-4" />
                <span className="text-xs md:text-sm">trialdn@gmail.com</span>
              </div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Main Navigation */}
      <motion.nav
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="fixed top-10 md:top-12 left-0 right-0 z-40 bg-white shadow-sm"
      >
        <div className="w-full flex flex-row justify-center px-2 md:px-4 py-2 md:py-3">
          <div className="w-full max-w-[1200px] flex items-center justify-between h-14 md:h-16">
            {/* Logo */}
            <div className="hidden md:flex items-center gap-2"> 
              <Link to="/" className="text-xl md:text-2xl font-bold text-[#46287C]">
                Trial
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-[#332288]/10 transition-all duration-300 ease-in-out transform hover:scale-105 active:scale-95"
            >
              {isMenuOpen ? (
                <X className="w-6 h-6 text-[#0E2A46] transition-transform duration-300 rotate-180" />
              ) : (
                <Menu className="w-6 h-6 text-[#0E2A46] transition-transform duration-300" />
              )}
            </button>

            {/* Navigation Links */}
            <div className={`${isMenuOpen ? 'flex' : 'hidden'} md:flex flex-col md:flex-row absolute md:relative top-full md:top-auto left-0 right-0 md:left-auto md:right-auto bg-white md:bg-transparent shadow-md md:shadow-none p-4 md:p-0 items-center gap-4 md:gap-8 transition-all duration-300 ease-in-out transform origin-top`}>
              <NavLink href="/">Home</NavLink>
              <NavLink href="/about">About Us</NavLink>
              <NavLink href="/university">University</NavLink>
              <NavLink href="/consultant">Consultant</NavLink>
              <NavLink href="/appointment">Appointment</NavLink>
              <NavLink href="/contact">Contact</NavLink>
            </div>

            {/* Create Account Button */}
            {!user && (
              <button className="hidden md:flex bg-[#009988] text-white w-[180px] md:w-[223.3px] h-[45px] md:h-[58.5px] px-4 md:px-6 rounded-[200px] hover:bg-primary-dark transition-colors items-center justify-between text-sm md:text-[15px] font-normal">
                <span>Create Account</span>
                <ArrowRight className="w-3 h-3 md:w-4 md:h-4" />
              </button>
            )}
            <div className="flex items-center gap-2 md:gap-4">
              <NavUser />
            </div>
          </div>
        </div>
      </motion.nav>
    </>
  );
}; 