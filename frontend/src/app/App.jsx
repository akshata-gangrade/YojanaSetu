import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UiPreferencesProvider } from '../context/UiPreferencesContext';
import { ToastProvider } from '../components/ui/Toast';
import { AppShell } from '../components/layout/AppShell';

import { HomePage } from '../pages/HomePage';
import { AboutPage } from '../pages/AboutPage';
import { PrivacyPage } from '../pages/PrivacyPage';
import { TermsPage } from '../pages/TermsPage';
import { CheckEligibilityPage } from '../pages/CheckEligibilityPage';
import { BrowseSchemesPage } from '../pages/BrowseSchemesPage';
import { AdminPage } from '../pages/AdminPage';
import { DesignSystemPage } from '../pages/DesignSystemPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export function App() {
  return (
    <UiPreferencesProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/check-eligibility" element={<CheckEligibilityPage />} />
              <Route path="/schemes" element={<BrowseSchemesPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/privacy" element={<PrivacyPage />} />
              <Route path="/terms" element={<TermsPage />} />
              <Route path="/admin" element={<AdminPage />} />
              {import.meta.env.DEV && (
                <Route path="/design-system" element={<DesignSystemPage />} />
              )}
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </UiPreferencesProvider>
  );
}

export default App;
