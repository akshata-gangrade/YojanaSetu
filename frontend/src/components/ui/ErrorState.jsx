import { Button } from './Button';

export function ErrorState({
  title = 'Something went wrong',
  message = 'An error occurred while loading this section. Please try again.',
  onRetry,
  retryLabel = 'Try Again',
  icon,
  className = '',
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center sm:p-12 ${className}`}
      role="alert"
    >
      <div
        className="shadow-2xs mb-4 flex h-16 w-16 items-center justify-center rounded-full border border-[#F8B4B4] bg-[#FDF2F2] text-[#B3261E]"
        aria-hidden="true"
      >
        {icon || (
          <svg
            className="h-8 w-8 text-[#B3261E]"
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
        )}
      </div>

      <h3 className="mb-2 text-lg font-bold text-[#B3261E]">{title}</h3>
      <p className="mb-6 max-w-md text-sm leading-relaxed text-[#55627A]">{message}</p>

      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          {retryLabel}
        </Button>
      )}
    </div>
  );
}

export default ErrorState;
