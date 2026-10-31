import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent, Alert } from '../components/ui';

export function TermsPage() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto max-w-4xl space-y-8 py-8">
      {/* Title */}
      <div className="space-y-3">
        <div className="border-navy/20 bg-navy/10 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-bold text-navy">
          <span>Terms & Conditions</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight text-navy sm:text-4xl">
          {t('pages.terms.title', 'Terms of Service')}
        </h1>
        <p className="text-base leading-relaxed text-text-muted sm:text-lg">
          {t(
            'pages.terms.subtitle',
            'Conditions of use for the YojanaSetu citizen portal.'
          )}
        </p>
      </div>

      <Alert variant="info" title="Public Informational Resource">
        YojanaSetu is made available as a public interest informational tool to empower
        citizens with knowledge of central and state entitlement schemes.
      </Alert>

      {/* Section 1 */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.terms.infoTitle', '1. Informational Service Only')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.terms.infoText',
              'YojanaSetu is an informational directory and eligibility guidance tool. It does not disburse funds, grant approvals, or accept government applications. Submission of welfare applications must be done through sanctioned government offices or websites.'
            )}
          </p>
        </CardContent>
      </Card>

      {/* Section 2 */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.terms.liabilityTitle', '2. Limitation of Liability')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.terms.liabilityText',
              'While we strive for absolute accuracy based on official government documentation, YojanaSetu and its contributors are not liable for any discrepancies, policy changes, rejected applications, or outcomes resulting from use of this information.'
            )}
          </p>
        </CardContent>
      </Card>

      {/* Section 3 */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.terms.redirectTitle', '3. External Links to Government Portals')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.terms.redirectText',
              'Links leading to external government websites (.gov.in, .nic.in) are provided for convenience. We do not control or endorse external third-party software.'
            )}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export default TermsPage;
