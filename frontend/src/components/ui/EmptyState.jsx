import { Button } from './Button';

export function EmptyState({
  title = 'No records found',
  description = 'There is currently no data or match for your selected criteria.',
  icon,
  action,
  actionLabel,
  onAction,
  className = '',
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center sm:p-12 ${className}`}
      role="region"
      aria-label="Empty state"
    >
      <div
        className="shadow-2xs mb-4 flex h-16 w-16 items-center justify-center rounded-full border border-[#D9E0EA] bg-[#F7F9FC] text-[#55627A]"
        aria-hidden="true"
      >
        {icon || (
          <svg
            className="h-8 w-8 text-[#55627A]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.75"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        )}
      </div>

      <h3 className="mb-2 text-lg font-bold text-[#0B2A5B]">{title}</h3>
      <p className="mb-6 max-w-md text-sm leading-relaxed text-[#55627A]">
        {description}
      </p>

      {action ? (
        action
      ) : actionLabel && onAction ? (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}

export default EmptyState;
