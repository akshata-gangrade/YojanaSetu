export function Checklist({
  items = [],
  onToggle,
  title,
  subtitle,
  className = '',
  readOnly = false,
}) {
  return (
    <div
      className={`rounded-[12px] border border-[#D9E0EA] bg-white p-5 shadow-soft ${className}`}
      role="group"
      aria-label={title || 'Requirements checklist'}
    >
      {title && (
        <h4 className="mb-1 flex items-center justify-between text-base font-bold text-[#0B2A5B]">
          <span>{title}</span>
          <span className="text-xs font-normal text-[#55627A]">
            {items.filter((i) => i.checked || i.status === 'eligible').length} /{' '}
            {items.length}
          </span>
        </h4>
      )}
      {subtitle && <p className="mb-3 text-xs text-[#55627A]">{subtitle}</p>}

      <ul className="mt-3 space-y-2.5" role="list">
        {items.map((item, idx) => {
          const itemId = `check-item-${item.id || idx}`;
          const isChecked = Boolean(item.checked);
          const status = item.status; // 'eligible' | 'warning' | 'error' | undefined

          return (
            <li
              key={item.id || idx}
              className={`flex items-start gap-3 rounded-lg border p-3 transition-colors ${
                isChecked || status === 'eligible'
                  ? 'border-[#A3D9A3] bg-[#EAF5EA]/50'
                  : status === 'error'
                    ? 'border-[#F8B4B4] bg-[#FDF2F2]/60'
                    : status === 'warning'
                      ? 'border-[#FFD099] bg-[#FFF4E5]/50'
                      : 'border-[#E8EEF5] bg-[#F7F9FC]'
              }`}
            >
              {readOnly ? (
                <div
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-xs font-bold ${
                    status === 'eligible' || isChecked
                      ? 'bg-[#138808] text-white'
                      : status === 'error'
                        ? 'bg-[#B3261E] text-white'
                        : status === 'warning'
                          ? 'bg-[#9A4A00] text-white'
                          : 'border-2 border-[#D9E0EA] bg-white text-[#55627A]'
                  }`}
                  aria-hidden="true"
                >
                  {status === 'eligible' || isChecked
                    ? '✓'
                    : status === 'error'
                      ? '✕'
                      : status === 'warning'
                        ? '!'
                        : ''}
                </div>
              ) : (
                <input
                  id={itemId}
                  type="checkbox"
                  checked={isChecked}
                  onChange={(e) => onToggle && onToggle(item.id || idx, e.target.checked)}
                  className="focus:ring-3 mt-0.5 h-5 min-h-[24px] w-5 min-w-[24px] cursor-pointer rounded border-[#D9E0EA] text-[#138808] focus:ring-[#0B2A5B] focus:ring-offset-1"
                />
              )}

              <div className="flex-1 text-sm">
                <label
                  htmlFor={readOnly ? undefined : itemId}
                  className={`block font-semibold ${
                    isChecked || status === 'eligible'
                      ? 'text-[#0E6606]'
                      : status === 'error'
                        ? 'text-[#B3261E]'
                        : 'text-[#1A2433]'
                  } ${readOnly ? '' : 'cursor-pointer'}`}
                >
                  {item.label || item.title}
                </label>
                {item.description && (
                  <p className="mt-0.5 text-xs leading-relaxed text-[#55627A]">
                    {item.description}
                  </p>
                )}
                {item.note && (
                  <p className="mt-1 inline-block rounded bg-[#FFF4E5] px-2 py-0.5 text-xs font-medium text-[#9A4A00]">
                    {item.note}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default Checklist;
