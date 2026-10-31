export function Skeleton({
  variant = 'text', // 'text' | 'title' | 'card' | 'circle' | 'button' | 'rectangle'
  lines = 1,
  className = '',
  width,
  height,
}) {
  const baseClasses = 'bg-[#EAEFF5] animate-pulse rounded';

  const style = {
    ...(width ? { width } : {}),
    ...(height ? { height } : {}),
  };

  if (variant === 'circle') {
    return (
      <div
        className={`${baseClasses} shrink-0 rounded-full ${className}`}
        style={{ width: width || '44px', height: height || '44px' }}
        aria-hidden="true"
      />
    );
  }

  if (variant === 'button') {
    return (
      <div
        className={`${baseClasses} h-11 w-32 rounded-lg ${className}`}
        style={style}
        aria-hidden="true"
      />
    );
  }

  if (variant === 'title') {
    return (
      <div
        className={`${baseClasses} mb-3 h-7 w-3/4 rounded-md ${className}`}
        style={style}
        aria-hidden="true"
      />
    );
  }

  if (variant === 'card') {
    return (
      <div
        className={`rounded-[12px] border border-[#D9E0EA] bg-white p-6 shadow-soft ${className}`}
        aria-hidden="true"
      >
        <div className="mb-4 flex items-center gap-3">
          <div className="h-10 w-10 animate-pulse rounded-full bg-[#EAEFF5]" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-1/2 animate-pulse rounded bg-[#EAEFF5]" />
            <div className="h-3 w-1/4 animate-pulse rounded bg-[#EAEFF5]" />
          </div>
        </div>
        <div className="mb-6 space-y-2.5">
          <div className="h-3.5 w-full animate-pulse rounded bg-[#EAEFF5]" />
          <div className="h-3.5 w-5/6 animate-pulse rounded bg-[#EAEFF5]" />
          <div className="h-3.5 w-2/3 animate-pulse rounded bg-[#EAEFF5]" />
        </div>
        <div className="flex items-center justify-between pt-2">
          <div className="h-6 w-24 animate-pulse rounded-full bg-[#EAEFF5]" />
          <div className="h-9 w-28 animate-pulse rounded-lg bg-[#EAEFF5]" />
        </div>
      </div>
    );
  }

  // Multi-line text
  if (lines > 1) {
    return (
      <div className={`space-y-2.5 ${className}`} aria-hidden="true">
        {Array.from({ length: lines }).map((_, idx) => (
          <div
            key={idx}
            className={`${baseClasses} h-4 ${idx === lines - 1 ? 'w-4/5' : 'w-full'}`}
            style={style}
          />
        ))}
      </div>
    );
  }

  // Single line text
  return (
    <div
      className={`${baseClasses} h-4 w-full ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
}

export default Skeleton;
