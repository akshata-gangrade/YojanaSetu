export function Alert({
  variant = 'info',
  title,
  children,
  onDismiss,
  className = '',
  icon,
  role = 'alert',
}) {
  const variantConfig = {
    info: {
      container: 'bg-[#EBF1FA] border-[#0B2A5B]/30 text-[#0B2A5B]',
      iconColor: 'text-[#0B2A5B]',
      defaultIcon: (
        <svg
          className="h-5 w-5 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    warning: {
      container: 'bg-[#FFF4E5] border-[#FFD099] text-[#9A4A00]',
      iconColor: 'text-[#9A4A00]',
      defaultIcon: (
        <svg
          className="h-5 w-5 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      ),
    },
    error: {
      container: 'bg-[#FDF2F2] border-[#F8B4B4] text-[#B3261E]',
      iconColor: 'text-[#B3261E]',
      defaultIcon: (
        <svg
          className="h-5 w-5 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    success: {
      container: 'bg-[#EAF5EA] border-[#A3D9A3] text-[#0E6606]',
      iconColor: 'text-[#0E6606]',
      defaultIcon: (
        <svg
          className="h-5 w-5 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
  }[variant] || {
    container: 'bg-[#EBF1FA] border-[#0B2A5B]/30 text-[#0B2A5B]',
    iconColor: 'text-[#0B2A5B]',
  };

  return (
    <div
      role={role}
      aria-live="polite"
      className={`shadow-2xs flex items-start gap-3.5 rounded-lg border p-4 ${variantConfig.container} ${className}`}
    >
      <div className={`mt-0.5 ${variantConfig.iconColor}`} aria-hidden="true">
        {icon || variantConfig.defaultIcon}
      </div>

      <div className="flex-1 text-sm leading-relaxed">
        {title && <p className="mb-1 text-base font-bold tracking-tight">{title}</p>}
        <div>{children}</div>
      </div>

      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="flex min-h-[36px] min-w-[36px] shrink-0 items-center justify-center rounded-md p-1 opacity-75 hover:bg-black/5 hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-current"
          aria-label="Dismiss alert"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </div>
  );
}

export default Alert;
