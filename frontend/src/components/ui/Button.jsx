export function Button({
  children,
  variant = 'primary',
  size = 'md',
  type = 'button',
  isLoading = false,
  loadingText,
  disabled = false,
  iconLeft,
  iconRight,
  className = '',
  onClick,
  ...props
}) {
  const baseClasses =
    'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-150 select-none min-h-[44px] min-w-[44px] focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-[#0B2A5B] focus-visible:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed disabled:pointer-events-none active:scale-[0.98]';

  const sizeClasses =
    {
      sm: 'text-sm px-3.5 py-1.5 gap-1.5',
      md: 'text-base px-5 py-2.5 gap-2',
      lg: 'text-lg px-7 py-3.5 gap-2.5 font-bold',
    }[size] || 'text-base px-5 py-2.5 gap-2';

  const variantClasses =
    {
      primary:
        'bg-[#138808] text-white hover:bg-[#0E6606] shadow-sm hover:shadow active:bg-[#0A4D05] border border-transparent',
      secondary:
        'bg-[#0B2A5B] text-white hover:bg-[#071C3D] shadow-sm hover:shadow active:bg-[#05142B] border border-transparent',
      outline:
        'bg-white text-[#0B2A5B] border-2 border-[#0B2A5B] hover:bg-[#F7F9FC] active:bg-[#EAEFF5]',
      ghost:
        'bg-transparent text-[#0B2A5B] hover:bg-[#D9E0EA]/30 active:bg-[#D9E0EA]/60 border border-transparent',
      danger:
        'bg-[#B3261E] text-white hover:bg-[#8F100A] shadow-sm active:bg-[#6D0803] border border-transparent',
    }[variant] || 'bg-[#138808] text-white hover:bg-[#0E6606]';

  return (
    <button
      type={type}
      data-button
      data-variant={variant}
      className={`${baseClasses} ${sizeClasses} ${variantClasses} ${className}`}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      onClick={onClick}
      {...props}
    >
      {isLoading ? (
        <>
          <svg
            className="-ml-1 mr-2 h-4 w-4 animate-spin text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>{loadingText || children}</span>
        </>
      ) : (
        <>
          {iconLeft && (
            <span className="shrink-0" aria-hidden="true">
              {iconLeft}
            </span>
          )}
          <span>{children}</span>
          {iconRight && (
            <span className="shrink-0" aria-hidden="true">
              {iconRight}
            </span>
          )}
        </>
      )}
    </button>
  );
}

export default Button;
