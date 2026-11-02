export function Badge({
  children,
  variant = 'neutral',
  status, // 'eligible' | 'maybe' | 'not-eligible'
  reason,
  size = 'md',
  icon,
  className = '',
}) {
  const effectiveVariant = status || variant;

  const sizeClasses =
    {
      sm: 'text-xs px-2.5 py-0.5 gap-1',
      md: 'text-sm px-3 py-1 gap-1.5',
      lg: 'text-base px-3.5 py-1.5 gap-2 font-semibold',
    }[size] || 'text-sm px-3 py-1 gap-1.5';

  const variantStyles = {
    eligible: {
      container: 'bg-[#EAF5EA] text-[#0E6606] border border-[#A3D9A3]',
      icon: '✓',
    },
    maybe: {
      container: 'bg-[#FFF4E5] text-[#9A4A00] border border-[#FFD099]',
      icon: '?',
    },
    'not-eligible': {
      container: 'bg-[#F1F5F9] text-[#475569] border border-[#CBD5E1]',
      icon: '✕',
    },
    warning: {
      container: 'bg-[#FFF4E5] text-[#9A4A00] border border-[#FFD099]',
      icon: '⚠',
    },
    navy: {
      container: 'bg-[#EBF1FA] text-[#0B2A5B] border border-[#C2D6EE]',
      dot: 'bg-[#0B2A5B]',
    },
    neutral: {
      container: 'bg-[#F7F9FC] text-[#1A2433] border border-[#D9E0EA]',
      dot: 'bg-[#55627A]',
    },
  }[effectiveVariant] || {
    container: 'bg-[#F7F9FC] text-[#1A2433] border border-[#D9E0EA]',
    dot: 'bg-[#55627A]',
  };

  const badgeIcon = icon || variantStyles.icon;

  return (
    <div
      data-badge={effectiveVariant}
      className={`inline-flex flex-wrap items-center gap-1.5 ${className}`}
    >
      <span
        className={`shadow-2xs inline-flex items-center rounded-full font-semibold ${variantStyles.container} ${sizeClasses}`}
      >
        {badgeIcon ? (
          <span className="shrink-0 font-bold" aria-hidden="true">
            {badgeIcon}
          </span>
        ) : (
          <span
            className={`h-2 w-2 shrink-0 rounded-full ${variantStyles.dot}`}
            aria-hidden="true"
          />
        )}
        <span>{children}</span>
      </span>

      {reason && (
        <span
          data-badge-reason
          className="ml-1 rounded-md border border-[#F8B4B4] bg-[#FDF2F2] px-2 py-0.5 text-xs font-semibold text-[#B3261E]"
          role="note"
        >
          {reason}
        </span>
      )}
    </div>
  );
}

export default Badge;
