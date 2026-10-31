import { useTranslation } from 'react-i18next';
import { useUiPreferences } from '../../context/useUiPreferences';

export function UtilityBar() {
  const { t } = useTranslation();
  const {
    language,
    setLanguage,
    textSize,
    setTextSize,
    highContrast,
    toggleHighContrast,
  } = useUiPreferences();

  return (
    <div
      className="border-b border-[#0B2A5B] bg-[#071C3D] px-4 py-1.5 text-xs text-white sm:px-6 sm:text-sm lg:px-8"
      role="region"
      aria-label="Accessibility and display settings"
    >
      {/* Skip to Main Content Link (Visible on focus) */}
      <a
        href="#main-content"
        className="focus:ring-3 sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded-md focus:bg-[#FF9933] focus:px-4 focus:py-2 focus:font-bold focus:text-[#0B2A5B] focus:shadow-lg focus:outline-none focus:ring-[#0B2A5B]"
      >
        {t('nav.skipToContent', 'Skip to main content')}
      </a>

      <div className="mx-auto flex max-w-[1200px] flex-col gap-2.5 sm:flex-row sm:items-center sm:justify-between">
        {/* Independence Notice Tag */}
        <div className="flex items-start gap-2 font-medium text-slate-300 sm:items-center">
          <span
            className="mt-1 inline-block h-2 w-2 shrink-0 rounded-full bg-[#FF9933] sm:mt-0"
            aria-hidden="true"
          />
          <span className="break-words text-[11px] leading-relaxed sm:text-xs">
            {t(
              'common.independentBadge',
              'Independent informational project. Not an official Government of India website.'
            )}
          </span>
        </div>

        {/* Accessibility & Language Controls */}
        <div className="flex shrink-0 flex-wrap items-center gap-2 sm:gap-4">
          {/* Text Size Controls: A (16px default), A+ (18px), A++ (20px) */}
          <div
            className="flex items-center gap-1 rounded border border-[#163B75] bg-[#0B2A5B]/80 p-0.5"
            role="group"
            aria-label={t('utility.textSize', 'Text size controls')}
          >
            <button
              type="button"
              onClick={() => setTextSize('normal')}
              aria-pressed={textSize === 'normal'}
              aria-label={t('utility.normalText', 'Standard text size (A, 16px)')}
              className={`min-h-[36px] min-w-[32px] rounded px-2.5 py-0.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933] ${
                textSize === 'normal'
                  ? 'shadow-xs bg-[#FF9933] font-bold text-[#0B2A5B]'
                  : 'text-slate-200 hover:bg-[#163B75]'
              }`}
            >
              A
            </button>
            <button
              type="button"
              onClick={() => setTextSize('large')}
              aria-pressed={textSize === 'large'}
              aria-label={t('utility.largeText', 'Large text size (A+, 18px)')}
              className={`min-h-[36px] min-w-[32px] rounded px-2.5 py-0.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933] ${
                textSize === 'large'
                  ? 'shadow-xs bg-[#FF9933] font-bold text-[#0B2A5B]'
                  : 'text-slate-200 hover:bg-[#163B75]'
              }`}
            >
              A+
            </button>
            <button
              type="button"
              onClick={() => setTextSize('xlarge')}
              aria-pressed={textSize === 'xlarge'}
              aria-label={t('utility.xlargeText', 'Extra large text size (A++, 20px)')}
              className={`min-h-[36px] min-w-[32px] rounded px-2.5 py-0.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933] ${
                textSize === 'xlarge'
                  ? 'shadow-xs bg-[#FF9933] font-bold text-[#0B2A5B]'
                  : 'text-slate-200 hover:bg-[#163B75]'
              }`}
            >
              A++
            </button>
          </div>

          {/* High Contrast Mode Toggle */}
          <button
            type="button"
            onClick={toggleHighContrast}
            aria-pressed={highContrast}
            aria-label={t('utility.toggleContrast', 'Toggle high contrast mode')}
            className={`flex min-h-[36px] items-center gap-1.5 rounded border px-2.5 py-1 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933] ${
              highContrast
                ? 'border-[#FF9933] bg-[#FF9933] font-bold text-[#0B2A5B]'
                : 'border-[#163B75] bg-[#0B2A5B]/80 text-slate-200 hover:bg-[#163B75]'
            }`}
          >
            <svg
              className="h-3.5 w-3.5"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 010-12v12z" />
            </svg>
            <span className="hidden sm:inline">
              {t('utility.highContrast', 'High Contrast')}
            </span>
          </button>

          {/* Language Toggle */}
          <div
            className="flex items-center rounded border border-[#163B75] bg-[#0B2A5B]/80 p-0.5"
            role="group"
            aria-label={t('utility.language', 'Language')}
          >
            <button
              type="button"
              onClick={() => setLanguage('en')}
              aria-pressed={language === 'en'}
              className={`min-h-[36px] rounded px-2.5 py-1 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933] ${
                language === 'en'
                  ? 'bg-[#138808] font-bold text-white'
                  : 'text-slate-200 hover:bg-[#163B75]'
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => setLanguage('hi')}
              aria-pressed={language === 'hi'}
              className={`min-h-[36px] rounded px-2.5 py-1 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933] ${
                language === 'hi'
                  ? 'bg-[#138808] font-bold text-white'
                  : 'text-slate-200 hover:bg-[#163B75]'
              }`}
            >
              हिन्दी
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UtilityBar;
