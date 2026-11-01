import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { getSchemes } from '../features/scheme/api/schemeApi';
import { SchemeCard } from '../features/scheme/components/SchemeCard';
import { SchemeFilters } from '../features/scheme/components/SchemeFilters';
import { Skeleton, ErrorState, EmptyState, Button, Alert } from '../components/ui';

export function BrowseSchemesPage() {
  const { t } = useTranslation();

  const [schemes, setSchemes] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const limit = 12; // 12 schemes per page

  const [level, setLevel] = useState('');
  const [state, setState] = useState('');
  const [category, setCategory] = useState('');

  const [isLoading, setIsLoading] = useState(true);
  const [isSlow, setIsSlow] = useState(false);
  const [error, setError] = useState(null);

  const fetchSchemesList = useCallback(async () => {
    setIsLoading(true);
    setIsSlow(false);
    setError(null);

    try {
      const response = await getSchemes({
        skip,
        limit,
        level: level || null,
        state: state || null,
        category: category || null,
        onSlow: () => setIsSlow(true),
      });

      setSchemes(response?.items || []);
      setTotal(response?.total || 0);
    } catch (err) {
      if (err?.status === 429) {
        setError(t('apiErrors.rateLimit', 'Too many requests, please wait a minute.'));
      } else {
        setError(err.message || t('common.error', 'An error occurred'));
      }
    } finally {
      setIsLoading(false);
      setIsSlow(false);
    }
  }, [skip, limit, level, state, category, t]);

  useEffect(() => {
    fetchSchemesList();
  }, [fetchSchemesList]);

  // Handle filter changes (resets pagination to first page)
  const handleFilterChange = ({ level: newLevel, state: newState, category: newCategory }) => {
    setLevel(newLevel);
    setState(newState);
    setCategory(newCategory);
    setSkip(0);
  };

  const handleResetFilters = () => {
    setLevel('');
    setState('');
    setCategory('');
    setSkip(0);
  };

  const handleNextPage = () => {
    if (skip + limit < total) {
      setSkip((prev) => prev + limit);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePrevPage = () => {
    if (skip > 0) {
      setSkip((prev) => Math.max(0, prev - limit));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit) || 1;
  const startItem = total > 0 ? skip + 1 : 0;
  const endItem = Math.min(skip + limit, total);

  return (
    <div className="mx-auto max-w-5xl space-y-8 py-6 sm:py-8" data-browse-schemes>
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
          {t('schemes.directoryTitle', 'Browse Government Schemes')}
        </h1>
        <p className="text-sm text-text-muted sm:text-base">
          {t(
            'schemes.directorySubtitle',
            'Directory of verified central and state welfare programs. Checked against official government sources.'
          )}
        </p>
      </div>

      {/* Filter Toolbar */}
      <SchemeFilters
        level={level}
        state={state}
        category={category}
        onChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {/* Cold Start Slow Server Alert */}
      {isSlow && (
        <Alert variant="warning" role="status">
          {t('apiErrors.slowServer', 'Waking up the server, this can take up to a minute')}
        </Alert>
      )}

      {/* Main Content Area */}
      {isLoading ? (
        <div
          className="grid grid-cols-1 gap-6 sm:grid-cols-2"
          role="status"
          aria-label={t('common.loading', 'Loading schemes')}
          data-loading-skeletons
        >
          {Array.from({ length: 4 }).map((_, idx) => (
            <Skeleton key={idx} variant="card" />
          ))}
        </div>
      ) : error ? (
        <div className="rounded-[12px] border border-border-card bg-surface-card p-6 shadow-soft" data-error-state>
          <ErrorState
            title={t('schemes.errorTitle', 'Unable to Load Schemes')}
            message={error}
            onRetry={fetchSchemesList}
            retryLabel={t('common.retry', 'Try Again')}
          />
        </div>
      ) : schemes.length === 0 ? (
        <div className="rounded-[12px] border border-border-card bg-surface-card p-6 shadow-soft" data-empty-state>
          <EmptyState
            title={t('schemes.emptyTitle', 'Verified Schemes Will Appear Here')}
            description={
              level || state || category
                ? t(
                    'schemes.emptyFilteredDesc',
                    'No verified schemes match your current filter criteria. Try clearing or broadening your filters.'
                  )
                : t(
                    'schemes.emptyDesc',
                    'All schemes in YojanaSetu are reviewed by an administrator against official government gazettes before appearing here.'
                  )
            }
            action={
              (level || state || category) ? (
                <Button variant="outline" size="sm" onClick={handleResetFilters}>
                  {t('schemes.filters.clearAll', 'Reset Filters')}
                </Button>
              ) : null
            }
          />
        </div>
      ) : (
        <div className="space-y-6" data-schemes-list>
          {/* Results Count Summary */}
          <div className="flex items-center justify-between text-xs font-semibold text-text-muted sm:text-sm">
            <span>
              {t('schemes.showingCount', 'Showing {{start}}-{{end}} of {{total}} verified schemes', {
                start: startItem,
                end: endItem,
                total,
              })}
            </span>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {schemes.map((scheme) => (
              <SchemeCard key={scheme.slug || scheme.id} scheme={scheme} />
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <nav
              aria-label={t('schemes.paginationAria', 'Schemes pagination')}
              className="flex items-center justify-between border-t border-border-card pt-6"
            >
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrevPage}
                disabled={skip === 0}
                aria-label={t('schemes.prevPage', 'Previous Page')}
              >
                &larr; {t('schemes.prevPage', 'Previous')}
              </Button>

              <div className="text-xs font-medium text-text-muted sm:text-sm">
                {t('schemes.pageIndicator', 'Page {{current}} of {{total}}', {
                  current: currentPage,
                  total: totalPages,
                })}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleNextPage}
                disabled={skip + limit >= total}
                aria-label={t('schemes.nextPage', 'Next Page')}
              >
                {t('schemes.nextPage', 'Next')} &rarr;
              </Button>
            </nav>
          )}
        </div>
      )}
    </div>
  );
}

export default BrowseSchemesPage;
