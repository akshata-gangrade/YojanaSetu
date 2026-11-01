import { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEligibility } from '../context/EligibilityContext';
import { ResultSchemeCard } from '../features/results/components/ResultSchemeCard';
import { ResultsTabs } from '../features/results/components/ResultsTabs';
import { Card, EmptyState, Button } from '../components/ui';

export function ResultsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { matchResults, hasAtLeastOneField } = useEligibility();

  const [activeTab, setActiveTab] = useState('eligible');
  const [selectedCategory, setSelectedCategory] = useState('');

  const eligibleList = useMemo(() => matchResults?.eligible || [], [matchResults]);
  const maybeList = useMemo(() => matchResults?.maybe || [], [matchResults]);
  const notEligibleList = useMemo(() => matchResults?.not_eligible || [], [matchResults]);

  // Active list based on active tab
  const currentList = useMemo(() => {
    if (activeTab === 'eligible') return eligibleList;
    if (activeTab === 'maybe') return maybeList;
    return notEligibleList;
  }, [activeTab, eligibleList, maybeList, notEligibleList]);

  // Extract all unique category tags across the 3 lists
  const allCategories = useMemo(() => {
    const set = new Set();
    [...eligibleList, ...maybeList, ...notEligibleList].forEach((s) => {
      if (Array.isArray(s.category_tags)) {
        s.category_tags.forEach((cat) => set.add(cat));
      }
    });
    return Array.from(set);
  }, [eligibleList, maybeList, notEligibleList]);

  // Filter current list by category tag if selected
  const filteredList = useMemo(() => {
    if (!selectedCategory) return currentList;
    return currentList.filter(
      (s) =>
        Array.isArray(s.category_tags) &&
        s.category_tags.some((tag) => tag.toLowerCase() === selectedCategory.toLowerCase())
    );
  }, [currentList, selectedCategory]);

  const handlePrint = () => {
    window.print();
  };

  // If page was refreshed or visited directly without profile in memory
  if (!matchResults || !hasAtLeastOneField) {
    return (
      <div className="mx-auto max-w-4xl py-12" data-no-results-guard>
        <Card className="p-6 text-center sm:p-12">
          <EmptyState
            title={t('results.noProfileTitle', 'No Profile in Memory')}
            description={t(
              'results.noProfileDesc',
              'For your privacy, citizen details are never stored on servers, in cookies, or in local storage. All temporary profile memory is erased on page refresh. Please check your eligibility again.'
            )}
            action={
              <Link to="/check-eligibility" className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy rounded">
                <Button variant="primary" size="md">
                  {t('results.startAgainBtn', 'Start Eligibility Check')} &rarr;
                </Button>
              </Link>
            }
          />
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 py-6 sm:py-8" data-results-page>
      {/* Top action row (hidden in print) */}
      <div className="flex flex-wrap items-center justify-between gap-3 print:hidden">
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/check-eligibility')}
        >
          &larr; {t('results.editDetailsBtn', 'Edit My Details')}
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handlePrint}
        >
          🖨 {t('results.printBtn', 'Print Results / PDF')}
        </Button>
      </div>

      {/* Mandatory Disclaimer Strip */}
      <div
        role="note"
        className="rounded-lg border border-saffron/40 bg-saffron/10 px-4 py-3 text-sm font-semibold text-navy"
        data-disclaimer-strip
      >
        <span className="mr-1.5 font-bold" aria-hidden="true">ℹ</span>
        <span>
          {t(
            'results.indicativeDisclaimer',
            'Indicative result. The concerned department makes the final decision.'
          )}
        </span>
      </div>

      {/* Page Title */}
      <div className="space-y-1">
        <h1 className="text-2xl font-black tracking-tight text-navy sm:text-3xl lg:text-4xl">
          {t('results.pageTitle', 'Your Scheme Eligibility Results')}
        </h1>
        <p className="text-sm text-text-muted">
          {t(
            'results.pageSubtitle',
            'Evaluated deterministically in pure Python against official government gazettes.'
          )}
        </p>
      </div>

      {/* Tabs (Eligible, Maybe, Not Eligible) */}
      <div className="print:hidden">
        <ResultsTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          eligibleCount={eligibleList.length}
          maybeCount={maybeList.length}
          notEligibleCount={notEligibleList.length}
        />
      </div>

      {/* Category filter pills (hidden in print) */}
      {allCategories.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-2 print:hidden" role="group" aria-label={t('results.categoryFilterAria', 'Filter by category')}>
          <span className="text-xs font-bold text-text-muted mr-1">
            {t('results.categoryLabel', 'Category')}:
          </span>
          <button
            type="button"
            onClick={() => setSelectedCategory('')}
            className={`rounded-full px-3 py-1 text-xs font-semibold transition-all ${
              selectedCategory === ''
                ? 'bg-navy text-white'
                : 'bg-surface-card border border-border-card text-text-muted hover:text-text-primary'
            }`}
          >
            {t('results.allCategories', 'All Categories')}
          </button>
          {allCategories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat)}
              className={`rounded-full px-3 py-1 text-xs font-semibold transition-all ${
                selectedCategory.toLowerCase() === cat.toLowerCase()
                  ? 'bg-navy text-white'
                  : 'bg-surface-card border border-border-card text-text-muted hover:text-text-primary'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Tab Panel Content */}
      <div
        id={`results-panel-${activeTab}`}
        role="tabpanel"
        aria-labelledby={`results-tab-${activeTab}`}
        className="space-y-6 pt-2"
      >
        {filteredList.length === 0 ? (
          <Card className="p-8 text-center">
            <EmptyState
              title={
                activeTab === 'eligible'
                  ? t('results.emptyEligibleTitle', 'No Eligible Schemes Found')
                  : activeTab === 'maybe'
                    ? t('results.emptyMaybeTitle', 'No Schemes Under Review')
                    : t('results.emptyNotEligibleTitle', 'No Disqualified Schemes')
              }
              description={
                selectedCategory
                  ? t('results.emptyCategoryDesc', 'No schemes match the selected category.')
                  : activeTab === 'eligible'
                    ? t('results.emptyEligibleDesc', 'Based on your entered details, you do not meet the verified criteria for any currently indexed schemes. Check the "Maybe eligible" tab for potential matches.')
                    : t('results.emptyGeneralDesc', 'No schemes found in this category.')
              }
              action={
                selectedCategory ? (
                  <Button variant="outline" size="sm" onClick={() => setSelectedCategory('')}>
                    {t('results.clearFilterBtn', 'Clear category filter')}
                  </Button>
                ) : null
              }
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {filteredList.map((scheme) => (
              <ResultSchemeCard key={scheme.slug} scheme={scheme} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsPage;
