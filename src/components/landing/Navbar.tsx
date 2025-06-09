import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Phone, Mail } from "lucide-react";

const NavLink = ({ children, href }: { children: React.ReactNode; href: string }) => (
  <a
    href={href}
    className="text-text-primary/80 hover:text-text-primary transition-colors"
  >
    {children}
  </a>
);

export const Navbar = () => {
  return (
    <>
      {/* Top Contact Section */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 bg-[#46287C] text-white"
      >
        <div className="w-full flex justify-center px-4">
          <div className="w-full max-w-[1200px] flex items-center justify-between h-12">
            {/* Contact Info */}
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                <span className="text-sm">(84) 348 962 536</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                <span className="text-sm">trialdn@gmail.com</span>
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
        className="fixed top-12 left-0 right-0 z-40 bg-white shadow-sm"
      >
        <div className="w-full flex justify-center px-4">
          <div className="w-full max-w-[1200px] flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="text-2xl font-bold text-[#46287C]">
              Trial
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-8">
              <NavLink href="/">Home</NavLink>
              <NavLink href="/about">About Us</NavLink>
              <NavLink href="/university">University</NavLink>
              <NavLink href="/consultant">Consultant</NavLink>
              <NavLink href="/appointment">Appointment</NavLink>
              <NavLink href="/contact">Contact</NavLink>
            </div>

            {/* Create Account Button */}
            <button className="bg-[#46287C] text-white px-6 py-2 rounded-lg hover:bg-[#46287C]/90 transition-colors">
              Create Account
            </button>
          </div>
        </div>
      </motion.nav>
    </>
  );
}; 