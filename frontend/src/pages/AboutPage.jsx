import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent, Alert } from '../components/ui';

export function AboutPage() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto max-w-4xl space-y-8 py-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="border-navy/20 bg-navy/10 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-bold text-navy">
          <span>
            {t(
              'common.independentBadge',
              'Independent informational project. Not an official Government of India website.'
            )}
          </span>
        </div>
        <h1 className="text-3xl font-black tracking-tight text-navy sm:text-4xl">
          {t('pages.about.title', 'About YojanaSetu and Legal Disclaimer')}
        </h1>
        <p className="text-base leading-relaxed text-text-muted sm:text-lg">
          {t(
            'pages.about.subtitle',
            'Empowering citizens across India to access entitlements through transparent technology.'
          )}
        </p>
      </div>

      {/* Prominent Legal Disclaimer Alert */}
      <Alert variant="warning" title="Institutional Disclaimer">
        <p className="font-bold">
          {t(
            'common.officialDisclaimer',
            'Not an official Government of India website. YojanaSetu is an independent informational guide.'
          )}
        </p>
        <p className="mt-1 text-xs opacity-90">
          We do not process applications or disburse funds. Official applications must
          always be submitted through respective ministry websites ending in .gov.in or
          .nic.in.
        </p>
      </Alert>

      {/* Mission */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>{t('pages.about.missionTitle', 'Our Mission')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.about.missionText',
              'Millions of eligible citizens miss out on government welfare benefits due to fragmented information, complicated eligibility criteria, and lack of clear guidance. YojanaSetu ("Scheme Bridge") was built as an independent, transparent bridge connecting citizens directly to official schemes.'
            )}
          </p>
          <p>
            By translating intricate government circulars and scheme rules into clear,
            structured criteria, YojanaSetu allows citizens to easily determine where they
            qualify without sharing sensitive identity records.
          </p>
        </CardContent>
      </Card>

      {/* Independence & Architecture */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.about.independenceTitle', 'Independent Public Project')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.about.independenceText',
              'YojanaSetu is an independent project and is NOT affiliated with, sponsored by, or an official website of the Government of India or any state government. Official applications must always be completed on respective government portals ending in .gov.in or .nic.in.'
            )}
          </p>
          <div className="space-y-1 rounded-lg border border-border bg-surface-page p-4 text-xs text-text-muted sm:text-sm">
            <p className="font-bold text-navy">How to identify official portals:</p>
            <p>
              1. Always verify the domain name ends with <strong>.gov.in</strong> or{' '}
              <strong>.nic.in</strong>.
            </p>
            <p>
              2. Look for SSL certificates registered to the National Informatics Centre
              (NIC) or government bodies.
            </p>
            <p>
              3. YojanaSetu provides direct links to verified official endpoints for each
              scheme.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Information Accuracy & Source Guidelines */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>
            {t('pages.about.accuracyTitle', 'Information Accuracy and Sources')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 px-0 pb-0 text-sm leading-relaxed text-text-primary sm:text-base">
          <p>
            {t(
              'pages.about.accuracyText',
              'All scheme criteria and summaries on YojanaSetu are cross-referenced against published government gazettes, guidelines, and portal documentation. However, government policies and budget allotments change periodically. Always verify with official authorities before applying.'
            )}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export default AboutPage;
