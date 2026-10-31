import { Skeleton } from './Skeleton';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';

export function Card({
  children,
  className = '',
  as: Component = 'div',
  isLoading = false,
  isError = false,
  isEmpty = false,
  errorMessage,
  onRetry,
  emptyTitle,
  emptyDescription,
  emptyAction,
  ...props
}) {
  if (isLoading) {
    return (
      <div
        data-card
        className={`rounded-[12px] border border-[#D9E0EA] bg-white p-6 shadow-soft ${className}`}
        aria-busy="true"
        aria-label="Loading content"
      >
        <Skeleton variant="title" className="mb-4 w-1/3" />
        <Skeleton variant="text" lines={3} className="mb-4" />
        <Skeleton variant="button" className="w-28" />
      </div>
    );
  }

  if (isError) {
    return (
      <div
        data-card
        className={`rounded-[12px] border border-[#F8B4B4] bg-white p-6 shadow-soft ${className}`}
      >
        <ErrorState
          title="Could not load details"
          message={errorMessage || 'An error occurred while displaying this card.'}
          onRetry={onRetry}
        />
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div
        data-card
        className={`rounded-[12px] border border-[#D9E0EA] bg-white p-6 shadow-soft ${className}`}
      >
        <EmptyState
          title={emptyTitle || 'No content available'}
          description={emptyDescription || 'There are no items or details to display.'}
          action={emptyAction}
        />
      </div>
    );
  }

  return (
    <Component
      data-card
      className={`rounded-[12px] border border-[#D9E0EA] bg-white shadow-soft transition-shadow hover:shadow-soft-md ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}

export function CardHeader({ children, className = '', ...props }) {
  return (
    <div
      className={`flex flex-col gap-1 border-b border-[#E8EEF5] px-6 py-5 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '', as: Component = 'h3', ...props }) {
  return (
    <Component
      className={`text-lg font-bold tracking-tight text-[#0B2A5B] sm:text-xl ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}

export function CardDescription({ children, className = '', ...props }) {
  return (
    <p className={`text-sm leading-relaxed text-[#55627A] ${className}`} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ children, className = '', ...props }) {
  return (
    <div className={`p-6 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ children, className = '', ...props }) {
  return (
    <div
      className={`flex items-center justify-between gap-4 rounded-b-[12px] border-t border-[#E8EEF5] bg-[#F7F9FC]/60 px-6 py-4 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export default Card;
