import { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Logo } from '../ui/Logo';

export function Header() {
  const { t } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { to: '/', label: t('nav.home', 'Home'), end: true },
    { to: '/check-eligibility', label: t('nav.checkEligibility', 'Check Eligibility') },
    { to: '/schemes', label: t('nav.browseSchemes', 'Browse Schemes') },
    { to: '/about', label: t('nav.about', 'About & Disclaimer') },
  ];

  return (
    <header className="shadow-2xs sticky top-0 z-40 border-b border-border bg-surface-card">
      <div className="mx-auto max-w-[1200px] px-4 sm:px-6 lg:px-8">
        <div className="flex h-20 items-center justify-between gap-4">
          {/* Logo Brand */}
          <Link
            to="/"
            className="focus-visible:ring-3 -ml-1 flex items-center rounded-lg p-1 focus-visible:outline-none focus-visible:ring-navy"
            aria-label="YojanaSetu Homepage"
          >
            <Logo variant="horizontal" size="md" />
          </Link>

          {/* Desktop Navigation */}
          <nav
            aria-label="Primary navigation"
            className="hidden items-center gap-1 md:flex lg:gap-2"
          >
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `focus-visible:ring-3 inline-flex min-h-[44px] items-center justify-center rounded-lg px-3.5 py-2 text-sm font-semibold transition-all duration-150 focus-visible:outline-none focus-visible:ring-navy ${
                    isActive
                      ? 'bg-navy/10 border-b-2 border-navy font-bold text-navy'
                      : 'text-text-primary hover:bg-surface-page hover:text-navy'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex items-center md:hidden">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="focus-visible:ring-3 flex min-h-[44px] min-w-[44px] items-center justify-center rounded-lg p-2 text-navy hover:bg-surface-page focus-visible:outline-none focus-visible:ring-navy"
              aria-expanded={mobileMenuOpen}
              aria-label={
                mobileMenuOpen
                  ? t('nav.closeMenu', 'Close navigation menu')
                  : t('nav.openMenu', 'Open navigation menu')
              }
            >
              {mobileMenuOpen ? (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <nav
          aria-label="Mobile navigation"
          className="space-y-1 border-t border-border bg-surface-page px-4 pb-4 pt-2 shadow-inner md:hidden"
        >
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                `focus-visible:ring-3 block flex min-h-[44px] items-center rounded-lg px-4 py-3 text-base font-semibold focus-visible:outline-none focus-visible:ring-navy ${
                  isActive
                    ? 'bg-navy font-bold text-white'
                    : 'hover:bg-navy/10 text-text-primary hover:text-navy'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      )}

      {/* Thin Saffron / White / Green Accent Line under Header */}
      <div data-header-accent className="flex h-1.5 w-full" aria-hidden="true">
        <div className="flex-1 bg-[#FF9933]" />
        <div className="w-12 border-y border-border bg-surface-card sm:w-20" />
        <div className="flex-1 bg-[#138808]" />
      </div>
    </header>
  );
}

export default Header;
