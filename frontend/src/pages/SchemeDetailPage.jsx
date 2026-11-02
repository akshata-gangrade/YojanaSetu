import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getSchemeBySlug } from '../features/scheme/api/schemeApi';
import { SchemeDetail } from '../features/scheme/components/SchemeDetail';
import { Skeleton, ErrorState, EmptyState, Button, Alert } from '../components/ui';

export function SchemeDetailPage() {
  const { slug } = useParams();
  const { t } = useTranslation();

  const [scheme, setScheme] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSlow, setIsSlow] = useState(false);
  const [error, setError] = useState(null);
  const [isNotFound, setIsNotFound] = useState(false);

  const fetchScheme = useCallback(async () => {
    if (!slug) return;

    setIsLoading(true);
    setIsSlow(false);
    setError(null);
    setIsNotFound(false);

    try {
      const data = await getSchemeBySlug(slug, {
        onSlow: () => setIsSlow(true),
      });
      setScheme(data);
    } catch (err) {
      if (err?.status === 404) {
        setIsNotFound(true);
      } else if (err?.status === 429) {
        setError(t('apiErrors.rateLimit', 'Too many requests, please wait a minute.'));
      } else {
        setError(err.message || t('common.error', 'An error occurred'));
      }
    } finally {
      setIsLoading(false);
      setIsSlow(false);
    }
  }, [slug, t]);

  useEffect(() => {
    fetchScheme();
  }, [fetchScheme]);

  return (
    <div className="mx-auto max-w-4xl py-6 sm:py-8" data-scheme-detail-page>
      {/* Demo mode banner */}
      {scheme && scheme.is_verified === false && (
        <div className="mb-6">
          <Alert variant="warning" role="alert" data-demo-banner>
            {t(
              'schemes.demoModeBanner',
              'Demo mode: some schemes shown here have not been verified against official sources. Always confirm on the official website before applying.'
            )}
          </Alert>
        </div>
      )}

      {/* Slow server alert */}
      {isSlow && (
        <div className="mb-6">
          <Alert variant="warning" role="status">
            {t('apiErrors.slowServer', 'Waking up the server, this can take up to a minute')}
          </Alert>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-6" role="status" aria-label={t('common.loading', 'Loading scheme details')}>
          <Skeleton variant="title" width="60%" />
          <Skeleton variant="text" lines={3} />
          <Skeleton variant="card" />
          <Skeleton variant="card" />
        </div>
      ) : isNotFound ? (
        <div className="rounded-[12px] border border-border-card bg-surface-card p-6 shadow-soft" data-not-found>
          <EmptyState
            title={t('schemeDetail.notFoundTitle', 'Scheme Not Found')}
            description={t(
              'schemeDetail.notFoundDesc',
              'This scheme does not exist, has been archived, or is awaiting administrator verification against official gazettes.'
            )}
            action={
              <Link to="/schemes" className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy rounded">
                <Button variant="primary" size="md">
                  {t('schemeDetail.browseAllSchemes', 'Browse All Verified Schemes')}
                </Button>
              </Link>
            }
          />
        </div>
      ) : error ? (
        <div className="rounded-[12px] border border-border-card bg-surface-card p-6 shadow-soft" data-error-state>
          <ErrorState
            title={t('schemeDetail.errorTitle', 'Unable to Load Scheme Details')}
            message={error}
            onRetry={fetchScheme}
            retryLabel={t('common.retry', 'Try Again')}
          />
        </div>
      ) : (
        <SchemeDetail scheme={scheme} />
      )}
    </div>
  );
}

export default SchemeDetailPage;

