import { useTranslation } from 'react-i18next';

export function ResultsTabs({
  activeTab,
  onTabChange,
  eligibleCount = 0,
  maybeCount = 0,
  notEligibleCount = 0,
}) {
  const { t } = useTranslation();

  const tabs = [
    {
      id: 'eligible',
      label: t('status.eligible', 'Eligible'),
      count: eligibleCount,
      countBadgeClass: 'bg-[#EAF5EA] text-[#0E6606] border border-[#A3D9A3]',
      activeClass: 'border-[#138808] text-[#0E6606] font-bold',
    },
    {
      id: 'maybe',
      label: t('status.maybeEligible', 'Maybe eligible'),
      count: maybeCount,
      countBadgeClass: 'bg-[#FFF4E5] text-[#9A4A00] border border-[#FFD099]',
      activeClass: 'border-[#FF9933] text-[#9A4A00] font-bold',
    },
    {
      id: 'not_eligible',
      label: t('status.notEligible', 'Not eligible'),
      count: notEligibleCount,
      countBadgeClass: 'bg-[#F1F5F9] text-[#475569] border border-[#CBD5E1]',
      activeClass: 'border-slate-500 text-slate-700 font-bold',
    },
  ];

  const handleKeyDown = (e, index) => {
    let nextIndex = null;
    if (e.key === 'ArrowRight') {
      nextIndex = (index + 1) % tabs.length;
    } else if (e.key === 'ArrowLeft') {
      nextIndex = (index - 1 + tabs.length) % tabs.length;
    } else if (e.key === 'Home') {
      nextIndex = 0;
    } else if (e.key === 'End') {
      nextIndex = tabs.length - 1;
    }

    if (nextIndex !== null) {
      e.preventDefault();
      onTabChange(tabs[nextIndex].id);
      const nextBtn = document.getElementById(`results-tab-${tabs[nextIndex].id}`);
      nextBtn?.focus();
    }
  };

  return (
    <div className="border-b border-border-card" role="region" aria-label={t('results.tabsAria', 'Results category tabs')}>
      <div className="-mb-px flex flex-wrap gap-2 sm:gap-6" role="tablist">
        {tabs.map((tab, idx) => {
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              id={`results-tab-${tab.id}`}
              role="tab"
              type="button"
              aria-selected={isActive}
              aria-controls={`results-panel-${tab.id}`}
              tabIndex={isActive ? 0 : -1}
              onClick={() => onTabChange(tab.id)}
              onKeyDown={(e) => handleKeyDown(e, idx)}
              className={`inline-flex items-center gap-2 border-b-2 px-3 py-3 text-sm transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy ${
                isActive
                  ? tab.activeClass
                  : 'border-transparent text-text-muted hover:border-slate-300 hover:text-text-primary'
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`inline-flex h-5 min-w-[20px] items-center justify-center rounded-full px-1.5 text-xs font-bold ${tab.countBadgeClass}`}
              >
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default ResultsTabs;

