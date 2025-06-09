import { Facebook, Instagram, Twitter } from 'lucide-react';
import { Link } from '@tanstack/react-router';

const SocialLink = ({ href, children }: { href: string; children: React.ReactNode }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="w-10 h-10 flex items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 transition-colors"
  >
    {children}
  </a>
);

const QuickLink = ({ href, children }: { href: string; children: React.ReactNode }) => (
  <Link
    to={href}
    className="text-white/80 hover:text-white transition-colors flex items-center gap-2"
  >
    <span className="text-white">›</span>
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
    <footer className="bg-[#1A1A1A] pt-16 pb-6">
      <div className="w-full max-w-[1200px] mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-8 pb-12">
          {/* Logo and Social Links */}
          <div className="lg:col-span-5">
            <Link to="/" className="inline-block">
              <h2 className="text-3xl font-bold text-white mb-6">Trial</h2>
            </Link>
            
            <div className="flex items-center gap-3">
              <SocialLink href="https://facebook.com">
                <Facebook className="w-5 h-5" />
              </SocialLink>
              <SocialLink href="https://instagram.com">
                <Instagram className="w-5 h-5" />
              </SocialLink>
              <SocialLink href="https://pinterest.com">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0a12 12 0 0 0-4.373 23.178c-.01-.937-.02-2.375.492-3.398.446-.861 2.882-5.574 2.882-5.574s-.738-1.476-.738-3.655c0-3.425 1.987-5.981 4.461-5.981 2.106 0 3.122 1.58 3.122 3.472 0 2.116-1.343 5.277-2.037 8.203-.577 2.447 1.226 4.44 3.638 4.44 4.367 0 7.728-4.587 7.728-11.22 0-5.863-4.207-9.97-10.236-9.97C6.757 0 2.873 4.723 2.873 9.802c0 1.94.738 4.047 1.894 5.193.178.165.246.307.178.563-.098.41-.318 1.338-.369 1.524-.066.246-.197.329-.492.197-1.845-.862-3.002-3.595-3.002-6.12C1.082 4.392 5.993 0 12.492 0 17.697 0 22 3.655 22 9.458c0 5.112-3.195 9.215-7.63 9.215-1.648 0-3.195-1.051-3.718-2.284 0 0-.82 3.1-.984 3.861-.369 1.415-1.353 3.182-2.008 4.264A11.49 11.49 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/>
                </svg>
              </SocialLink>
              <SocialLink href="https://twitter.com">
                <Twitter className="w-5 h-5" />
              </SocialLink>
            </div>
          </div>

          {/* Quick Links */}
          <div className="lg:col-span-4 lg:col-start-9">
            <h3 className="text-white text-xl font-semibold mb-6">Quick Links:</h3>
            <nav className="flex flex-col gap-4">
              {quickLinks.map((link) => (
                <QuickLink key={link.href} href={link.href}>
                  {link.label}
                </QuickLink>
              ))}
            </nav>
          </div>
        </div>

        {/* Copyright */}
        <div className="pt-6 border-t border-white/10">
          <p className="text-white/60 text-center">
            Copyright © 2025 <span className="text-[#FFD700]">Trial</span> || All Rights Reserved
          </p>
        </div>
      </div>
    </footer>
  );
}; 