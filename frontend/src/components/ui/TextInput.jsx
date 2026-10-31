import { useId } from 'react';

export function TextInput({
  label,
  id,
  helperText,
  errorText,
  required = false,
  disabled = false,
  iconLeft,
  iconRight,
  className = '',
  inputClassName = '',
  type = 'text',
  value,
  onChange,
  placeholder,
  ...props
}) {
  const generatedId = useId();
  const inputId = id || generatedId;
  const helperId = `${inputId}-helper`;
  const errorId = `${inputId}-error`;

  const hasError = Boolean(errorText);

  const describedBy = [hasError ? errorId : null, helperText ? helperId : null]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={`flex w-full flex-col gap-1.5 text-left ${className}`}>
      {label && (
        <label
          htmlFor={inputId}
          className="flex items-center justify-between text-sm font-semibold text-[#0B2A5B]"
        >
          <span>
            {label}
            {required && (
              <span className="ml-1 text-[#B3261E]" aria-hidden="true">
                *
              </span>
            )}
          </span>
          {required && <span className="sr-only">(required)</span>}
        </label>
      )}

      <div className="relative flex items-center">
        {iconLeft && (
          <span
            className="pointer-events-none absolute left-3.5 flex items-center justify-center text-[#55627A]"
            aria-hidden="true"
          >
            {iconLeft}
          </span>
        )}

        <input
          id={inputId}
          data-text-input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          aria-invalid={hasError ? 'true' : 'false'}
          aria-describedby={describedBy || undefined}
          className={`shadow-2xs focus:ring-3 min-h-[44px] w-full rounded-lg border bg-white px-3.5 py-2.5 text-base text-[#1A2433] transition-colors duration-150 placeholder:text-[#55627A]/70 focus:border-transparent focus:outline-none focus:ring-[#0B2A5B] disabled:cursor-not-allowed disabled:bg-[#F1F5F9] disabled:text-[#55627A] ${
            hasError
              ? 'border-[#B3261E] focus:ring-[#B3261E]'
              : 'border-[#D9E0EA] hover:border-[#0B2A5B]/40'
          } ${iconLeft ? 'pl-11' : ''} ${iconRight ? 'pr-11' : ''} ${inputClassName}`}
          {...props}
        />

        {iconRight && (
          <span
            className="pointer-events-none absolute right-3.5 flex items-center justify-center text-[#55627A]"
            aria-hidden="true"
          >
            {iconRight}
          </span>
        )}
      </div>

      {hasError ? (
        <p
          id={errorId}
          className="mt-0.5 flex items-center gap-1 text-xs font-semibold text-[#B3261E]"
          role="alert"
        >
          <svg
            className="h-3.5 w-3.5 shrink-0"
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
          <span>{errorText}</span>
        </p>
      ) : helperText ? (
        <p id={helperId} className="mt-0.5 text-xs text-[#55627A]">
          {helperText}
        </p>
      ) : null}
    </div>
  );
}

export default TextInput;
