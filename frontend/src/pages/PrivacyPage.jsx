import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent, Alert } from '../components/ui';

export function PrivacyPage() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto max-w-4xl space-y-8 py-8">
      {/* Page Title */}
      <div className="space-y-3">
        <div className="border-govgreen/20 inline-flex items-center gap-2 rounded-full border bg-govgreen-light px-3 py-1 text-xs font-bold text-govgreen">
          <span>Privacy Preserving Architecture</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight text-navy sm:text-4xl">
          {t('pages.privacy.title', 'Privacy Policy')}
        </h1>
        <p className="text-base leading-relaxed text-text-muted sm:text-lg">
          {t(
            'pages.privacy.subtitle',
            'Your privacy is our foundational principle. We do not track, collect, or store personal identifiers.'
          )}
        </p>
      </div>

      {/* Main Guarantee Highlight */}
      <Alert variant="success" title="No Personal Data Stored by Us">
        <p className="text-sm">
          {t(
            'common.privacyGuarantee',
            'No personal data stored by us. We never ask for or store Aadhaar, PAN, phone number, email, or bank details.'
          )}
        </p>
      </Alert>

      {/* No PII Collection */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.privacy.noPiiTitle', 'No Personal Data Collection')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.privacy.noPiiText',
              'We never ask for, collect, or store Aadhaar numbers, PAN cards, voter IDs, phone numbers, email addresses, names, or bank account details. Any temporary input provided during an eligibility check is processed solely in transient browser memory.'
            )}
          </p>
          <div className="space-y-2 rounded-lg border border-border bg-surface-page p-4 text-xs text-text-muted sm:text-sm">
            <p className="font-bold text-navy">What we NEVER ask for or retain:</p>
            <ul className="list-disc space-y-1 pl-5">
              <li>Aadhaar numbers or biometric information</li>
              <li>PAN numbers or Tax ID numbers</li>
              <li>Phone numbers or contact details</li>
              <li>Email addresses or personal accounts</li>
              <li>Bank account numbers, IFSC codes, or UPI IDs</li>
              <li>Exact home addresses or GPS locations</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Local Storage Policy */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.privacy.storageTitle', 'What We Store Locally')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.privacy.storageText',
              "We only save your accessibility and interface preferences (selected language, text size preference, and high contrast toggle) in your browser's local storage. Your user queries and eligibility profiles are never saved to local storage or transmitted to analytics services."
            )}
          </p>
          <div className="grid grid-cols-1 gap-3 pt-2 sm:grid-cols-3">
            <div className="rounded-lg border border-border bg-surface-page p-3">
              <p className="text-xs font-bold text-navy">yojanasetu_lang</p>
              <p className="mt-1 text-xs text-text-muted">
                Saved language preference (&apos;en&apos; or &apos;hi&apos;)
              </p>
            </div>
            <div className="rounded-lg border border-border bg-surface-page p-3">
              <p className="text-xs font-bold text-navy">yojanasetu_text_size</p>
              <p className="mt-1 text-xs text-text-muted">
                Saved scale (&apos;normal&apos;, &apos;large&apos;, &apos;xlarge&apos;)
              </p>
            </div>
            <div className="rounded-lg border border-border bg-surface-page p-3">
              <p className="text-xs font-bold text-navy">yojanasetu_contrast</p>
              <p className="mt-1 text-xs text-text-muted">
                High contrast mode flag (&apos;true&apos; or &apos;false&apos;)
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* No Cookies / Tracking */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.privacy.cookiesTitle', 'No Advertising or Tracking Cookies')}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-0 pb-0 text-sm leading-relaxed text-[#1A2433]">
          <p>
            {t(
              'pages.privacy.cookiesText',
              'YojanaSetu uses no commercial tracking cookies, no third-party behavioral pixels, and no fingerprinting technologies.'
            )}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export default PrivacyPage;
