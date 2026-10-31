import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, EmptyState, Button, Alert } from '../components/ui';

export function CheckEligibilityPage() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto max-w-4xl space-y-8 py-8">
      {/* Title */}
      <div className="space-y-2">
        <div className="border-govgreen/20 inline-flex items-center gap-2 rounded-full border bg-govgreen-light px-3 py-1 text-xs font-bold text-govgreen">
          <span>{t('hero.badge', '100% Free • Privacy First • No Login Required')}</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight text-navy sm:text-4xl">
          {t('pages.eligibilityPlaceholder.title', 'Check Your Scheme Eligibility')}
        </h1>
        <p className="text-base text-text-muted">
          {t(
            'pages.eligibilityPlaceholder.subtitle',
            'Determine your qualification for central and state welfare benefits.'
          )}
        </p>
      </div>

      {/* Privacy Notice */}
      <Alert variant="info" title="Privacy Notice">
        {t(
          'common.privacyGuarantee',
          'No personal data stored by us. We never ask for or store Aadhaar, PAN, phone number, email, or bank details.'
        )}
      </Alert>

      {/* Placeholder EmptyState with Verified Data Notice */}
      <Card className="p-4 sm:p-8">
        <EmptyState
          title={t(
            'pages.eligibilityPlaceholder.emptyTitle',
            'Eligibility Questionnaire Arriving Soon'
          )}
          description={t(
            'pages.eligibilityPlaceholder.emptyDesc',
            'The deterministic citizen qualification questionnaire is currently being calibrated with official eligibility rules. It will launch with verified criteria from published guidelines without storing personal details.'
          )}
          action={
            <Link
              to="/"
              className="focus-visible:ring-3 rounded-lg focus-visible:outline-none focus-visible:ring-navy"
            >
              <Button variant="primary" size="md">
                {t('common.backToHome', 'Back to Home')}
              </Button>
            </Link>
          }
        />
      </Card>
    </div>
  );
}

export default CheckEligibilityPage;
