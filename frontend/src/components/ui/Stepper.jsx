export function Stepper({ steps = [], currentStep = 0, onStepClick, className = '' }) {
  return (
    <nav aria-label="Progress steps" className={`w-full py-4 ${className}`}>
      <ol className="relative mx-auto flex w-full max-w-2xl items-center justify-between">
        {steps.map((step, idx) => {
          const isCompleted = idx < currentStep;
          const isCurrent = idx === currentStep;
          const isClickable = Boolean(onStepClick && isCompleted);

          return (
            <li
              key={step.id || idx}
              className="group relative flex flex-1 flex-col items-center"
              aria-current={isCurrent ? 'step' : undefined}
            >
              {/* Connector line behind circles */}
              {idx > 0 && (
                <div
                  className={`absolute -left-1/2 top-5 z-0 h-1 w-full -translate-y-1/2 ${
                    idx <= currentStep ? 'bg-[#138808]' : 'bg-[#D9E0EA]'
                  }`}
                  aria-hidden="true"
                />
              )}

              {/* Step indicator circle */}
              <button
                type="button"
                disabled={!isClickable}
                onClick={() => isClickable && onStepClick(idx)}
                className={`focus-visible:ring-3 relative z-10 flex h-10 min-h-[44px] w-10 min-w-[44px] select-none items-center justify-center rounded-full text-sm font-bold transition-all duration-200 focus-visible:outline-none focus-visible:ring-[#0B2A5B] ${
                  isCompleted
                    ? 'bg-[#138808] text-white shadow-sm hover:scale-105'
                    : isCurrent
                      ? 'bg-[#0B2A5B] text-white shadow ring-4 ring-[#FF9933]/40'
                      : 'border-2 border-[#D9E0EA] bg-[#F7F9FC] text-[#55627A]'
                } ${isClickable ? 'cursor-pointer' : 'cursor-default'}`}
                aria-label={`Step ${idx + 1}: ${step.title || step.label} - ${
                  isCompleted ? 'Completed' : isCurrent ? 'Current step' : 'Upcoming'
                }`}
              >
                {isCompleted ? (
                  <svg
                    className="h-5 w-5 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2.5"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : (
                  <span>{idx + 1}</span>
                )}
              </button>

              {/* Step text */}
              <div className="mt-2 px-1 text-center">
                <span
                  className={`block text-xs font-semibold tracking-tight sm:text-sm ${
                    isCurrent
                      ? 'text-[#0B2A5B]'
                      : isCompleted
                        ? 'text-[#138808]'
                        : 'text-[#55627A]'
                  }`}
                >
                  {step.title || step.label}
                </span>
                {step.description && (
                  <span className="mx-auto mt-0.5 hidden max-w-[120px] truncate text-[11px] text-[#55627A] sm:block">
                    {step.description}
                  </span>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export default Stepper;
