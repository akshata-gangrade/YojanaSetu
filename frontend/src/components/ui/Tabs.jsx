import { useRef } from 'react';

export function Tabs({ tabs = [], activeTab, onChange, className = '' }) {
  const tabListRef = useRef(null);

  const handleKeyDown = (e, index) => {
    let newIndex = index;

    if (e.key === 'ArrowRight') {
      newIndex = (index + 1) % tabs.length;
    } else if (e.key === 'ArrowLeft') {
      newIndex = (index - 1 + tabs.length) % tabs.length;
    } else if (e.key === 'Home') {
      newIndex = 0;
    } else if (e.key === 'End') {
      newIndex = tabs.length - 1;
    } else {
      return;
    }

    e.preventDefault();
    onChange(tabs[newIndex].id);
    const buttons = tabListRef.current?.querySelectorAll('button[role="tab"]');
    if (buttons && buttons[newIndex]) {
      buttons[newIndex].focus();
    }
  };

  const currentTab = tabs.find((t) => t.id === activeTab) || tabs[0];

  return (
    <div className={`w-full ${className}`}>
      {/* Tab Header list */}
      <div
        ref={tabListRef}
        role="tablist"
        aria-orientation="horizontal"
        className="scrollbar-none flex items-center gap-1 overflow-x-auto border-b border-[#D9E0EA] pb-px"
      >
        {tabs.map((tab, idx) => {
          const isActive = tab.id === currentTab?.id;
          return (
            <button
              key={tab.id}
              role="tab"
              id={`tab-${tab.id}`}
              type="button"
              aria-selected={isActive}
              aria-controls={`panel-${tab.id}`}
              tabIndex={isActive ? 0 : -1}
              onClick={() => onChange(tab.id)}
              onKeyDown={(e) => handleKeyDown(e, idx)}
              className={`focus-visible:ring-3 flex min-h-[44px] items-center gap-2 whitespace-nowrap rounded-t-md border-b-2 px-4 py-2.5 text-sm font-semibold transition-all duration-150 focus-visible:outline-none focus-visible:ring-[#0B2A5B] sm:text-base ${
                isActive
                  ? 'border-[#0B2A5B] bg-[#EBF1FA]/60 font-bold text-[#0B2A5B]'
                  : 'border-transparent text-[#55627A] hover:bg-[#F7F9FC] hover:text-[#0B2A5B]'
              }`}
            >
              {tab.icon && <span aria-hidden="true">{tab.icon}</span>}
              <span>{tab.label}</span>
              {typeof tab.count === 'number' && (
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-bold ${
                    isActive ? 'bg-[#0B2A5B] text-white' : 'bg-[#EAEFF5] text-[#55627A]'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Panel */}
      {currentTab && (
        <div
          role="tabpanel"
          id={`panel-${currentTab.id}`}
          aria-labelledby={`tab-${currentTab.id}`}
          tabIndex={0}
          className="rounded-lg pt-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0B2A5B]"
        >
          {currentTab.content}
        </div>
      )}
    </div>
  );
}

export default Tabs;
