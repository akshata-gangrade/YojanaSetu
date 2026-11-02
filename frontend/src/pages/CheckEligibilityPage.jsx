import { useTranslation } from 'react-i18next';
import { useEligibility } from '../context/EligibilityContext';
import { ConsentGate } from '../features/intake/components/ConsentGate';
import { IntakeChat } from '../features/intake/components/IntakeChat';
import { YourDetailsPanel } from '../features/intake/components/YourDetailsPanel';

export function CheckEligibilityPage() {
  const { t } = useTranslation();
  const { consentGiven, setConsentGiven } = useEligibility();

  return (
    <div className="mx-auto max-w-6xl space-y-6 py-6 sm:py-8" data-check-eligibility-page>
      {/* Header */}
      <div className="space-y-2">
        <div className="border-navy/20 bg-navy/10 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-bold text-navy">
          <span>
            {t(
              'common.independentBadge',
              'Independent informational project. Not an official Government of India website.'
            )}
          </span>
        </div>

        <h1 className="text-3xl font-black tracking-tight text-navy sm:text-4xl">
          {t('intake.pageTitle', 'Check Your Scheme Eligibility')}
        </h1>
        <p className="text-sm text-text-muted sm:text-base">
          {t(
            'intake.pageSubtitle',
            'Describe your situation in Hindi or English, or complete your details directly. Eligibility is decided by fixed rules, not by AI.'
          )}
        </p>
      </div>

      {/* Main View: Consent Gate OR Interactive Intake split view */}
      {!consentGiven ? (
        <div className="pt-4">
          <ConsentGate onConsent={() => setConsentGiven(true)} />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Conversational Assistant */}
          <div className="w-full">
            <IntakeChat />
          </div>

          {/* Source-of-truth Details Panel */}
          <div className="w-full">
            <YourDetailsPanel />
          </div>
        </div>
      )}
    </div>
  );
}

export default CheckEligibilityPage;
