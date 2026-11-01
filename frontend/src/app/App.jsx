import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UiPreferencesProvider } from '../context/UiPreferencesContext';
import { EligibilityProvider } from '../context/EligibilityContext';
import { ToastProvider } from '../components/ui/Toast';
import { AppShell } from '../components/layout/AppShell';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { Skeleton } from '../components/ui/Skeleton';

// Lazy-loaded routes for code splitting
const HomePage = lazy(() =>
  import('../pages/HomePage').then((m) => ({ default: m.HomePage }))
);
const AboutPage = lazy(() =>
  import('../pages/AboutPage').then((m) => ({ default: m.AboutPage }))
);
const PrivacyPage = lazy(() =>
  import('../pages/PrivacyPage').then((m) => ({ default: m.PrivacyPage }))
);
const TermsPage = lazy(() =>
  import('../pages/TermsPage').then((m) => ({ default: m.TermsPage }))
);
const CheckEligibilityPage = lazy(() =>
  import('../pages/CheckEligibilityPage').then((m) => ({
    default: m.CheckEligibilityPage,
  }))
);
const ResultsPage = lazy(() =>
  import('../pages/ResultsPage').then((m) => ({
    default: m.ResultsPage,
  }))
);
const BrowseSchemesPage = lazy(() =>
  import('../pages/BrowseSchemesPage').then((m) => ({
    default: m.BrowseSchemesPage,
  }))
);
const SchemeDetailPage = lazy(() =>
  import('../pages/SchemeDetailPage').then((m) => ({
    default: m.SchemeDetailPage,
  }))
);
const AdminPage = lazy(() =>
  import('../pages/AdminPage').then((m) => ({ default: m.AdminPage }))
);
const DesignSystemPage = lazy(() =>
  import('../pages/DesignSystemPage').then((m) => ({
    default: m.DesignSystemPage,
  }))
);
const NotFoundPage = lazy(() =>
  import('../pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage }))
);

function PageFallback() {
  return (
    <div
      className="mx-auto max-w-4xl space-y-6 py-12"
      role="status"
      aria-label="Loading page"
    >
      <Skeleton variant="title" width="50%" />
      <Skeleton variant="text" lines={3} />
      <Skeleton variant="card" />
    </div>
  );
}

export function App() {
  return (
    <ErrorBoundary>
      <UiPreferencesProvider>
        <EligibilityProvider>
          <ToastProvider>
            <BrowserRouter>
              <Routes>
                <Route element={<AppShell />}>
                  <Route
                    path="/"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <HomePage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/check-eligibility"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <CheckEligibilityPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/check-eligibility/results"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <ResultsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/schemes"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <BrowseSchemesPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/schemes/:slug"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <SchemeDetailPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/about"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <AboutPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/privacy"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <PrivacyPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/terms"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <TermsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/admin"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <AdminPage />
                      </Suspense>
                    }
                  />
                  {import.meta.env.DEV && (
                    <Route
                      path="/design-system"
                      element={
                        <Suspense fallback={<PageFallback />}>
                          <DesignSystemPage />
                        </Suspense>
                      }
                    />
                  )}
                  <Route
                    path="*"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <NotFoundPage />
                      </Suspense>
                    }
                  />
                </Route>
              </Routes>
            </BrowserRouter>
          </ToastProvider>
        </EligibilityProvider>
      </UiPreferencesProvider>
    </ErrorBoundary>
  );
}

export default App;
