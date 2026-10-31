import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, EmptyState, Button } from '../components/ui';

export function AdminPage() {
  const { t } = useTranslation();

  // Enforce noindex, nofollow meta tag on the Admin page
  useEffect(() => {
    let meta = document.querySelector('meta[name="robots"]');
    const existed = Boolean(meta);
    const previousContent = meta ? meta.getAttribute('content') : null;

    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('name', 'robots');
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', 'noindex, nofollow');

    return () => {
      if (existed && previousContent) {
        meta.setAttribute('content', previousContent);
      } else if (meta && meta.parentNode) {
        meta.parentNode.removeChild(meta);
      }
    };
  }, []);

  return (
    <div className="mx-auto max-w-2xl space-y-8 py-12">
      {/* Page Title */}
      <div className="space-y-3 text-center">
        <div className="border-navy/20 bg-navy/10 inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold text-navy">
          <span>Administrative Portal</span>
        </div>
        <h1 className="text-3xl font-black tracking-tight text-navy sm:text-4xl">
          {t('pages.adminPlaceholder.title', 'Admin sign-in (coming soon)')}
        </h1>
        <p className="text-base text-text-muted">
          {t(
            'pages.adminPlaceholder.subtitle',
            'Administrative governance access will be enabled in a future release.'
          )}
        </p>
      </div>

      {/* Placeholder Card (No status or system information) */}
      <Card className="p-6 sm:p-10">
        <EmptyState
          title="Sign-in Unavailable"
          description={t(
            'pages.adminPlaceholder.notice',
            'Administrative authentication and rule management will be available here. This page is not indexed by public search engines.'
          )}
          action={
            <Link
              to="/"
              className="focus-visible:ring-3 rounded-lg focus-visible:outline-none focus-visible:ring-navy"
            >
              <Button variant="secondary" size="md">
                {t('common.backToHome', 'Back to Home')}
              </Button>
            </Link>
          }
        />
      </Card>
    </div>
  );
}

export default AdminPage;
