import { Facebook, Instagram, Linkedin, Twitter } from 'lucide-react';
import { Link } from '@tanstack/react-router';

const SocialLink = ({ href, children }: { href: string; children: React.ReactNode }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="w-[45px] h-[45px] rounded-[22.5px] bg-[#E9E2FF] flex items-center justify-center hover:bg-[#704FE6] group transition-colors"
  >
    <div className="text-[#704FE6] group-hover:text-white transition-colors">
      {children}
    </div>
  </a>
);

const QuickLink = ({ href, children, className }: { href: string; children: React.ReactNode; className?: string }) => (
  <Link
    to={href}
    className={`transition-colors flex items-center gap-2 ${className || 'text-text-secondary'} [&.active]:text-primary [&.active]:border [&.active]:border-primary [&.active]:rounded-[200px] [&.active]:px-3 [&.active]:py-1`}
  >
    <span className="text-text-primary">›</span>
    {children}
  </Link>
);

export const Footer = () => {
  const quickLinks = [
    { label: 'About Us', href: '/about' },
    { label: 'University', href: '/university' },
    { label: 'Consultant', href: '/consultant' },
    { label: 'Appoinment', href: '/appointment' },
    { label: 'Contact Us', href: '/contact' },
  ];

  return (
    <footer className="bg-background-lighter pt-16">
      <div className="w-full max-w-[1200px] mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-8 pb-12">
          {/* Logo and Social Links */}
          <div className="lg:col-span-5">
            <Link to="/" className="inline-block flex justify-center">
              <h2 className="text-3xl font-bold text-text-primary mb-6 text-center">Trial</h2>
            </Link>
            
            <div className="flex items-center gap-4 justify-center">
              <SocialLink href="https://facebook.com">
                <Facebook className="w-5 h-5" />
              </SocialLink>
              <SocialLink href="https://instagram.com">
                <Instagram className="w-5 h-5" />
              </SocialLink>
              <SocialLink href="https://linkedin.com">
                <Linkedin className="w-5 h-5" />
              </SocialLink>
              <SocialLink href="https://twitter.com">
                <Twitter className="w-5 h-5" />
              </SocialLink>
            </div>
          </div>

          {/* Quick Links */}
          <div className="lg:col-span-4 lg:col-start-9">
            <h3 className="text-text-primary text-xl font-semibold mb-6">Quick Links:</h3>
            <nav className="flex flex-col gap-4">
              {quickLinks.map((link) => (
                <QuickLink key={link.href} href={link.href} className="text-white">
                  {link.label}
                </QuickLink>
              ))}
            </nav>
          </div>
        </div>


      </div>
              {/* Copyright */}
        <div className="pt-6 border-t border-background bg-[#222222] w-full">
          <p className="text-text-secondary text-center">
            Copyright © 2025 <span className="px-2 text-[#FFD25D]">Trial</span> || All Rights Reserved
          </p>
        </div>
    </footer>
  );
}; 