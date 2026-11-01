import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useEligibility } from '../../../context/EligibilityContext';
import { Card, Button, Alert } from '../../../components/ui';

export function IntakeChat() {
  const { t } = useTranslation();
  const {
    chatMessages,
    sendMessage,
    isLoading,
    isSlow,
    error,
  } = useEligibility();

  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);
  const MAX_MESSAGE_CHARS = 1000;

  useEffect(() => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = inputText.trim();
    if (!trimmed || isLoading) return;

    sendMessage(trimmed);
    setInputText('');
  };

  const handleChipClick = (chip) => {
    if (isLoading) return;
    sendMessage(chip.label, { field: chip.field, value: chip.value });
  };

  return (
    <Card className="flex h-[620px] flex-col p-4 shadow-soft sm:p-5" data-intake-chat>
      {/* Chat Header */}
      <div className="border-b border-border-card pb-3">
        <h3 className="text-base font-bold text-navy sm:text-lg">
          {t('intake.chat.title', 'Conversational Eligibility Guide')}
        </h3>
        <p className="text-xs text-text-muted">
          {t(
            'intake.chat.subtitle',
            'Describe your household in plain words. Extracted details update the panel on the right.'
          )}
        </p>
      </div>

      {/* Messages Transcript */}
      <div
        className="flex-1 space-y-4 overflow-y-auto py-4 pr-1 focus:outline-none"
        aria-live="polite"
        role="log"
        tabIndex={0}
      >
        {chatMessages.map((msg) => {
          const isUser = msg.sender === 'user';

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              {/* PII Warning Notice if stripped */}
              {msg.piiNotice && (
                <div className="mb-2 max-w-[85%]">
                  <Alert variant="warning" role="alert" className="text-xs">
                    {msg.piiNotice}
                  </Alert>
                </div>
              )}

              {/* Message Bubble */}
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  isUser
                    ? 'bg-navy text-white rounded-br-xs'
                    : 'bg-[#F1F5F9] text-text-primary border border-border-card rounded-bl-xs'
                }`}
              >
                <div className="font-semibold text-[11px] opacity-75 mb-0.5">
                  {isUser
                    ? t('intake.chat.you', 'You')
                    : t('intake.chat.assistant', 'YojanaSetu Guide')}
                </div>
                <p className="whitespace-pre-wrap break-words">{msg.text}</p>
              </div>

              {/* Quick-reply chips if present */}
              {!isUser && Array.isArray(msg.quickReplies) && msg.quickReplies.length > 0 && (
                <div
                  className="mt-2.5 flex max-w-[90%] flex-wrap items-center gap-1.5"
                  role="group"
                  aria-label={t('intake.chat.quickRepliesLabel', 'Suggested quick replies')}
                >
                  {msg.quickReplies.map((chip, idx) => (
                    <button
                      key={idx}
                      type="button"
                      disabled={isLoading}
                      onClick={() => handleChipClick(chip)}
                      className="rounded-full border border-navy/30 bg-surface-card px-3 py-1 text-xs font-semibold text-navy transition-all hover:bg-navy hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {/* Loading Bubble */}
        {isLoading && (
          <div className="flex flex-col items-start" aria-live="polite">
            <div className="rounded-2xl rounded-bl-xs border border-border-card bg-[#F1F5F9] px-4 py-3 text-sm text-text-muted">
              <div className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 animate-spin text-navy"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>
                  {t('intake.chat.thinking', 'Extracting criteria from your description...')}
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Cold Start Alert */}
      {isSlow && (
        <div className="mb-2">
          <Alert variant="warning" role="status">
            {t('apiErrors.slowServer', 'Waking up the server, this can take up to a minute')}
          </Alert>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="mb-2">
          <Alert variant="error" role="alert">
            {error}
          </Alert>
        </div>
      )}

      {/* Input Bar */}
      <form onSubmit={handleSubmit} className="border-t border-border-card pt-3 space-y-2">
        <div className="relative">
          <textarea
            id="chat-user-input"
            rows={2}
            value={inputText}
            onChange={(e) => setInputText(e.target.value.slice(0, MAX_MESSAGE_CHARS))}
            placeholder={t(
              'intake.chat.inputPlaceholder',
              'Type your situation here in English or Hindi (e.g. 35-year-old farmer in Bihar earning 80k/yr)...'
            )}
            aria-label={t('intake.chat.inputAriaLabel', 'Citizen situation description')}
            maxLength={MAX_MESSAGE_CHARS}
            disabled={isLoading}
            className="w-full resize-none rounded-lg border border-border-card bg-surface-card p-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy disabled:opacity-60"
          />

          <div className="flex items-center justify-between text-xs text-text-muted pt-1">
            <span className="text-[11px]">
              🔒 {t('intake.chat.privacyPill', 'Never type Aadhaar, phone, or bank details')}
            </span>
            <span className={inputText.length >= MAX_MESSAGE_CHARS ? 'font-bold text-[#B3261E]' : ''}>
              {inputText.length}/{MAX_MESSAGE_CHARS}
            </span>
          </div>
        </div>

        <div className="flex justify-end">
          <Button
            type="submit"
            variant="primary"
            size="sm"
            isLoading={isLoading}
            disabled={!inputText.trim() || isLoading}
          >
            {t('intake.chat.sendBtn', 'Send')} &uarr;
          </Button>
        </div>
      </form>
    </Card>
  );
}

export default IntakeChat;
