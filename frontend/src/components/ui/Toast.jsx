import { useState, useCallback } from 'react';
import { ToastContext } from './useToast';

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    ({ title, message, variant = 'info', duration = 4000 }) => {
      const id = Date.now().toString() + Math.random().toString(36).substring(2, 5);
      const newToast = { id, title, message, variant };

      setToasts((prev) => [...prev, newToast]);

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
      return id;
    },
    [removeToast]
  );

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      {/* Toast Region */}
      <div
        role="region"
        aria-label="Notifications"
        className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-full max-w-sm flex-col gap-2.5 px-4 sm:px-0"
      >
        <div aria-live="polite" className="flex w-full flex-col gap-2.5">
          {toasts.map((toast) => (
            <ToastItem
              key={toast.id}
              toast={toast}
              onClose={() => removeToast(toast.id)}
            />
          ))}
        </div>
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onClose }) {
  const styles =
    {
      info: 'bg-[#0B2A5B] text-white border-[#163B75]',
      success: 'bg-[#138808] text-white border-[#0E6606]',
      warning: 'bg-[#9A4A00] text-white border-[#6E3200]',
      error: 'bg-[#B3261E] text-white border-[#8F100A]',
    }[toast.variant] || 'bg-[#0B2A5B] text-white';

  return (
    <div
      role="status"
      className={`animate-in slide-in-from-bottom-2 pointer-events-auto flex items-start gap-3 rounded-[12px] border p-4 shadow-soft-lg transition-all ${styles}`}
    >
      <div className="flex-1 text-sm">
        {toast.title && <p className="mb-0.5 font-bold">{toast.title}</p>}
        <p className="leading-snug">{toast.message}</p>
      </div>
      <button
        type="button"
        onClick={onClose}
        className="flex min-h-[36px] min-w-[36px] items-center justify-center rounded p-1 text-white/80 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
        aria-label="Dismiss notification"
      >
        ✕
      </button>
    </div>
  );
}

export default ToastProvider;
