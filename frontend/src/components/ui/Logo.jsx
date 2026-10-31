import { useTranslation } from 'react-i18next';

export function Logo({
  variant = 'horizontal',
  size = 'md',
  showTagline = true,
  className = '',
  taglineText,
  inverted = false,
}) {
  const { t } = useTranslation();
  const effectiveTagline =
    taglineText || t('common.appTagline', 'Bridging people to the schemes they deserve.');

  // Dimensions based on size
  const markDimensions =
    {
      sm: 'w-8 h-6',
      md: 'w-10 h-8',
      lg: 'w-14 h-11',
    }[size] || 'w-10 h-8';

  const markSvg = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 80 64"
      role="img"
      aria-label="YojanaSetu logo mark"
      className={`shrink-0 transition-transform ${markDimensions}`}
    >
      <path
        d="M10 48 A30 30 0 0 1 70 48"
        fill="none"
        stroke="#FF9933"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <path
        d="M21 48 A19 19 0 0 1 59 48"
        fill="none"
        stroke="#138808"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <path
        d="M33 42 L38 46.5 L47 36.5"
        fill="none"
        stroke={inverted ? '#FFFFFF' : '#0B2A5B'}
        strokeWidth="4.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M4 53 H76"
        fill="none"
        stroke={inverted ? '#FFFFFF' : '#0B2A5B'}
        strokeWidth="5"
        strokeLinecap="round"
      />
    </svg>
  );

  if (variant === 'mark') {
    return <div className={`inline-flex items-center ${className}`}>{markSvg}</div>;
  }

  // Horizontal variant
  return (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      {markSvg}
      <div className="flex flex-col text-left">
        <span className="font-sans text-xl font-black leading-none tracking-tight sm:text-2xl">
          <span className={inverted ? 'text-white' : 'text-navy'}>Yojana</span>
          <span className="text-govgreen">Setu</span>
        </span>
        {showTagline && (
          <span
            className={`mt-0.5 text-[11px] font-medium leading-tight tracking-normal sm:text-xs ${
              inverted ? 'text-slate-300' : 'text-text-muted'
            }`}
          >
            {effectiveTagline}
          </span>
        )}
      </div>
    </div>
  );
}

export default Logo;
