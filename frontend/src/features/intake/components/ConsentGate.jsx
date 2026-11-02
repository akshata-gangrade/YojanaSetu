import { useTranslation } from 'react-i18next';
import { Card, Button } from '../../../components/ui';

export function ConsentGate({ onConsent }) {
  const { t } = useTranslation();

  return (
    <Card className="mx-auto max-w-2xl border-navy/20 p-6 shadow-md sm:p-8" data-consent-gate>
      <div className="space-y-6">
        {/* Header Badge & Title */}
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-navy/30 bg-[#EBF1FA] px-3 py-1 text-xs font-bold text-navy">
            <span>🔒 {t('intake.consent.badge', 'No data saved • Privacy First')}</span>
          </div>

          <h2 className="text-2xl font-black tracking-tight text-navy sm:text-3xl">
            {t('intake.consent.title', 'Before You Check Your Eligibility')}
          </h2>

          <p className="text-sm leading-relaxed text-text-muted">
            {t(
              'intake.consent.intro',
              'Please review how your information is handled before continuing. YojanaSetu is designed from the ground up to preserve your confidentiality.'
            )}
          </p>
        </div>

        {/* Informational Points */}
        <div className="space-y-3.5 border-y border-border-card py-5 text-sm leading-relaxed text-text-primary">
          <div className="flex items-start gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#EAF5EA] text-xs font-bold text-[#0E6606]">
              ✓
            </span>
            <div>
              <strong className="block text-navy font-bold">
                {t('intake.consent.point1Title', 'What is asked')}
              </strong>
              <span className="text-text-muted">
                {t(
                  'intake.consent.point1Desc',
                  'Basic criteria such as your age, state, occupation, and household income bracket to evaluate eligibility.'
                )}
              </span>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#EAF5EA] text-xs font-bold text-[#0E6606]">
              ✓
            </span>
            <div>
              <strong className="block text-navy font-bold">
                {t('intake.consent.point2Title', 'No personal data stored')}
              </strong>
              <span className="text-text-muted">
                {t(
                  'intake.consent.point2Desc',
                  'We do not save your details on our servers or in your browser storage. They are held only in this page\'s memory and are cleared when you refresh or close the tab.'
                )}
              </span>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#EBF1FA] text-xs font-bold text-navy">
              ℹ
            </span>
            <div>
              <strong className="block text-navy font-bold">
                {t('intake.consent.point3Title', 'Processed by an AI service')}
              </strong>
              <span className="text-text-muted">
                {t(
                  'intake.consent.point3Desc',
                  'What you type is sent to our server and to an AI service so it can understand your situation. We do not save it, and the AI service has its own privacy policy. The AI never decides eligibility. Fixed rules do.'
                )}
              </span>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#FDF2F2] text-xs font-bold text-[#B3261E]">
              ✕
            </span>
            <div>
              <strong className="block text-[#B3261E] font-bold">
                {t('intake.consent.point4Title', 'Never enter identity or banking details')}
              </strong>
              <span className="text-text-muted">
                {t(
                  'intake.consent.point4Desc',
                  'Never type your Aadhaar number, PAN card, phone number, email address, physical address, or bank account numbers.'
                )}
              </span>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#FFF4E5] text-xs font-bold text-[#9A4A00]">
              !
            </span>
            <div>
              <strong className="block text-[#9A4A00] font-bold">
                {t('intake.consent.point5Title', 'Sensitive fields are strictly optional')}
              </strong>
              <span className="text-text-muted">
                {t(
                  'intake.consent.point5Desc',
                  'Social category and disability status are completely optional and always offer "Prefer not to say".'
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Confirmation Button */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-text-muted">
            {t(
              'intake.consent.footerNote',
              'By continuing, you agree to temporary in-memory processing of your situation.'
            )}
          </p>

          <Button
            variant="primary"
            size="md"
            onClick={onConsent}
            className="w-full sm:w-auto"
          >
            {t('intake.consent.continueBtn', 'I understand, continue')} &rarr;
          </Button>
        </div>
      </div>
    </Card>
  );
}

export default ConsentGate;

