import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, EmptyState, Button } from '../components/ui';

export function BrowseSchemesPage() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto max-w-4xl space-y-8 py-8">
      {/* Page Title */}
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
          {t('pages.schemesPlaceholder.title', 'Browse Government Schemes')}
        </h1>
        <p className="text-base text-text-muted">
          {t(
            'pages.schemesPlaceholder.subtitle',
            'Comprehensive directory of central and state citizen welfare programs.'
          )}
        </p>
      </div>

      {/* Placeholder EmptyState with Verified Data Notice */}
      <Card className="p-4 sm:p-8">
        <EmptyState
          title={t(
            'pages.schemesPlaceholder.emptyTitle',
            'Scheme Directory Arriving Soon'
          )}
          description={t(
            'pages.schemesPlaceholder.emptyDesc',
            'The scheme directory is being indexed with verified guidelines and criteria checked against official government gazettes. Direct links to official portals will be available here.'
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

export default BrowseSchemesPage;
