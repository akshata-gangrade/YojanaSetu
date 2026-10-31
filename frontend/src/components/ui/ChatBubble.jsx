import { Logo } from './Logo';

export function ChatBubble({
  message,
  sender = 'assistant', // 'assistant' | 'user' | 'system'
  timestamp,
  isLoading = false,
  className = '',
  avatar,
  children,
}) {
  const isAssistant = sender === 'assistant';
  const isUser = sender === 'user';
  const isSystem = sender === 'system';

  if (isSystem) {
    return (
      <div
        className={`my-3 flex justify-center px-4 ${className}`}
        role="status"
        aria-live="polite"
      >
        <span className="rounded-full border border-[#D9E0EA] bg-[#E8EEF5] px-3.5 py-1.5 text-xs font-medium text-[#55627A]">
          {message || children}
        </span>
      </div>
    );
  }

  return (
    <div
      className={`my-3 flex max-w-2xl items-start gap-3 ${
        isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
      } ${className}`}
      role="article"
      aria-label={`${sender} message`}
    >
      {/* Avatar */}
      <div
        className={`shadow-2xs flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-full ${
          isAssistant
            ? 'bg-[#0B2A5B] text-white ring-2 ring-[#FF9933]/30'
            : 'bg-[#138808] text-white ring-2 ring-[#138808]/20'
        }`}
        aria-hidden="true"
      >
        {avatar ? (
          avatar
        ) : isAssistant ? (
          <Logo variant="mark" size="sm" className="scale-75 text-white" inverted />
        ) : (
          <span className="text-xs font-bold">YOU</span>
        )}
      </div>

      {/* Bubble Container */}
      <div
        className={`flex flex-col ${
          isUser ? 'items-end' : 'items-start'
        } max-w-[85%] sm:max-w-md`}
      >
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-soft sm:text-base ${
            isAssistant
              ? 'rounded-tl-sm border border-[#D9E0EA] bg-white text-[#1A2433]'
              : 'rounded-tr-sm bg-[#0B2A5B] text-white'
          }`}
          aria-live="polite"
        >
          {isLoading ? (
            <div
              className="flex items-center gap-1.5 px-2 py-1"
              aria-label="Assistant is thinking"
            >
              <span className="h-2 w-2 animate-bounce rounded-full bg-[#FF9933] [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-[#FF9933] [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-[#FF9933]" />
            </div>
          ) : (
            <div>{message || children}</div>
          )}
        </div>

        {/* Timestamp */}
        {timestamp && (
          <span
            className={`mt-1 select-none px-1 text-[11px] text-[#55627A]`}
            aria-label={`Sent at ${timestamp}`}
          >
            {timestamp}
          </span>
        )}
      </div>
    </div>
  );
}

export default ChatBubble;
