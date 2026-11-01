import { useTranslation } from 'react-i18next';
import { INDIAN_STATES, SCHEME_LEVELS } from '../constants';
import { Button } from '../../../components/ui';

export function SchemeFilters({
  level = '',
  state = '',
  category = '',
  onChange,
  onReset,
}) {
  const { t } = useTranslation();

  const handleLevelChange = (e) => {
    onChange({ level: e.target.value, state, category });
  };

  const handleStateChange = (e) => {
    onChange({ level, state: e.target.value, category });
  };

  const handleCategoryChange = (e) => {
    onChange({ level, state, category: e.target.value });
  };

  const hasActiveFilters = Boolean(level || state || category);

  return (
    <div
      role="search"
      aria-label={t('schemes.filters.ariaLabel', 'Filter government schemes')}
      className="rounded-[12px] border border-border-card bg-surface-card p-4 shadow-soft sm:p-5"
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {/* Level Filter */}
        <div className="space-y-1.5">
          <label
            htmlFor="scheme-level-select"
            className="block text-xs font-bold uppercase tracking-wider text-text-muted"
          >
            {t('schemes.filters.levelLabel', 'Administrative Level')}
          </label>
          <select
            id="scheme-level-select"
            value={level}
            onChange={handleLevelChange}
            className="h-11 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm text-text-primary focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            {SCHEME_LEVELS.map((lvl) => (
              <option key={lvl.value} value={lvl.value}>
                {lvl.value === ''
                  ? t('schemes.filters.allLevels', 'All Levels')
                  : lvl.value === 'central'
                    ? t('schemes.filters.centralOnly', 'Central Schemes')
                    : t('schemes.filters.stateOnly', 'State Schemes')}
              </option>
            ))}
          </select>
        </div>

        {/* State Filter */}
        <div className="space-y-1.5">
          <label
            htmlFor="scheme-state-select"
            className="block text-xs font-bold uppercase tracking-wider text-text-muted"
          >
            {t('schemes.filters.stateLabel', 'State / Union Territory')}
          </label>
          <select
            id="scheme-state-select"
            value={state}
            onChange={handleStateChange}
            className="h-11 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm text-text-primary focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('schemes.filters.allStates', 'All States & UTs')}</option>
            {INDIAN_STATES.map((st) => (
              <option key={st.value} value={st.value}>
                {st.label}
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div className="space-y-1.5">
          <label
            htmlFor="scheme-category-input"
            className="block text-xs font-bold uppercase tracking-wider text-text-muted"
          >
            {t('schemes.filters.categoryLabel', 'Category')}
          </label>
          <input
            id="scheme-category-input"
            type="text"
            value={category}
            onChange={handleCategoryChange}
            placeholder={t('schemes.filters.categoryPlaceholder', 'e.g. agriculture, education')}
            className="h-11 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm text-text-primary placeholder:text-text-muted focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          />
        </div>
      </div>

      {hasActiveFilters && (
        <div className="mt-4 flex justify-end border-t border-border-card pt-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="text-xs"
          >
            {t('schemes.filters.clearAll', 'Reset Filters')}
          </Button>
        </div>
      )}
    </div>
  );
}

export default SchemeFilters;

