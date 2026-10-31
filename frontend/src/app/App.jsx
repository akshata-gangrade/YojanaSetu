import { useState, useEffect } from 'react';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { IntakeForm } from '../features/intake/components/IntakeForm';
import { ResultsList } from '../features/results/components/ResultsList';
import { checkBackendHealth } from '../lib/api';

export function App() {
  const [lang, setLang] = useState('en');
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkBackendHealth()
      .then((data) => setBackendStatus(data?.status || 'ok'))
      .catch(() => setBackendStatus('offline'));
  }, []);

  const toggleLang = () => {
    setLang((prev) => (prev === 'en' ? 'hi' : 'en'));
  };

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 font-sans">
      <DisclaimerBanner />
      <Header lang={lang} onToggleLang={toggleLang} />

      <main className="mx-auto w-full max-w-7xl flex-1 space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3">
          <span className="text-xs font-medium text-slate-600 sm:text-sm">
            System Connectivity Status:
          </span>
          <span
            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
              backendStatus === 'ok'
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-amber-100 text-amber-800'
            }`}
          >
            {backendStatus === 'ok' ? '● Backend Connected' : '○ Standalone / Connecting'}
          </span>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <IntakeForm />
          <ResultsList />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
