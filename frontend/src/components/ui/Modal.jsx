import { useEffect, useRef, useId } from 'react';

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = 'max-w-lg',
  className = '',
}) {
  const dialogRef = useRef(null);
  const titleId = useId();
  const descId = useId();

  // Control native dialog open/close states
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      if (!dialog.open) {
        dialog.showModal();
      }
    } else {
      if (dialog.open) {
        dialog.close();
      }
    }
  }, [isOpen]);

  // Handle native cancel event (ESC key press)
  const handleCancel = (e) => {
    e.preventDefault();
    onClose();
  };

  // Close on outside click (click on backdrop)
  const handleBackdropClick = (e) => {
    if (e.target === dialogRef.current) {
      onClose();
    }
  };

  return (
    <dialog
      ref={dialogRef}
      onCancel={handleCancel}
      onClick={handleBackdropClick}
      aria-labelledby={title ? titleId : undefined}
      aria-describedby={description ? descId : undefined}
      className={`w-[92vw] rounded-[12px] border border-[#D9E0EA] bg-white p-0 text-[#1A2433] shadow-soft-lg ${maxWidth} backdrop:backdrop-blur-xs open:animate-in open:fade-in open:zoom-in-95 m-auto duration-200 backdrop:bg-[#0B2A5B]/40 focus:outline-none ${className}`}
    >
      <div className="flex max-h-[90vh] flex-col">
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-[#E8EEF5] p-6">
          <div>
            {title && (
              <h2 id={titleId} className="text-xl font-bold text-[#0B2A5B]">
                {title}
              </h2>
            )}
            {description && (
              <p id={descId} className="mt-1 text-sm text-[#55627A]">
                {description}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="focus-visible:ring-3 -mr-1.5 -mt-1.5 flex min-h-[44px] min-w-[44px] items-center justify-center rounded-lg p-1.5 text-[#55627A] hover:bg-[#F1F5F9] hover:text-[#0B2A5B] focus-visible:outline-none focus-visible:ring-[#0B2A5B]"
            aria-label="Close dialog"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Modal Content */}
        <div className="overflow-y-auto p-6 text-sm leading-relaxed sm:text-base">
          {children}
        </div>

        {/* Modal Footer */}
        {footer && (
          <div className="flex items-center justify-end gap-3 rounded-b-[12px] border-t border-[#E8EEF5] bg-[#F7F9FC] p-4 px-6">
            {footer}
          </div>
        )}
      </div>
    </dialog>
  );
}

export default Modal;
