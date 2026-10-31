import { Outlet } from 'react-router-dom';
import { UtilityBar } from './UtilityBar';
import { Header } from './Header';
import { Footer } from './Footer';

export function AppShell() {
  return (
    <div
      data-contrast-root
      className="flex min-h-screen flex-col bg-surface-page text-text-primary selection:bg-[#FF9933]/30"
    >
      {/* Top Utility Bar (Skip link, Language toggle, Text-size controls, High-contrast toggle) */}
      <UtilityBar />

      {/* Main Header (Logo, Nav, Accent line) */}
      <Header />

      {/* Main Content Area */}
      <main
        id="main-content"
        tabIndex={-1}
        className="mx-auto w-full max-w-[1200px] flex-1 px-4 outline-none sm:px-6 lg:px-8"
      >
        <Outlet />
      </main>

      {/* Institutional Footer */}
      <Footer />
    </div>
  );
}

export default AppShell;
