import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { askSchemeQuestion } from '../api/schemeApi';
import { Button, Alert, Card } from '../../../components/ui';

export function SchemeAskBox({ slug }) {
  const { t, i18n } = useTranslation();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSlow, setIsSlow] = useState(false);
  const [error, setError] = useState(null);

  const MAX_CHARS = 500;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setIsSlow(false);
    setError(null);
    setResult(null);

    try {
      const response = await askSchemeQuestion(slug, {
        question: trimmed,
        language: i18n.language || 'en',
        onSlow: () => setIsSlow(true),
      });
      setResult(response);
    } catch (err) {
      if (err?.status === 429) {
        setError(t('ask.rateLimit', 'Too many requests, please wait a minute before asking again.'));
      } else {
        setError(err.message || t('common.error', 'An error occurred'));
      }
    } finally {
      setIsLoading(false);
      setIsSlow(false);
    }
  };

  const handleClear = () => {
    setQuestion('');
    setResult(null);
    setError(null);
    setIsSlow(false);
  };

  return (
    <Card className="p-5 sm:p-6" data-ask-box>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold text-navy sm:text-xl">
            {t('ask.title', 'Ask About This Scheme')}
          </h3>
          <p className="mt-1 text-xs text-text-muted sm:text-sm">
            {t(
              'ask.subtitle',
              'Get direct answers grounded in official scheme guidelines. Answers cite retrieved sections.'
            )}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="relative">
            <textarea
              id="scheme-ask-input"
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value.slice(0, MAX_CHARS))}
              placeholder={t(
                'ask.placeholder',
                'e.g. What documents are needed? Who is eligible? What is the subsidy percentage?'
              )}
              aria-label={t('ask.inputLabel', 'Question about scheme guidelines')}
              maxLength={MAX_CHARS}
              disabled={isLoading}
              className="w-full resize-none rounded-lg border border-border-card bg-surface-card p-3 text-sm text-text-primary placeholder:text-text-muted focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy disabled:opacity-60"
            />
            <div
              className="mt-1 flex justify-between text-xs text-text-muted"
              aria-live="polite"
            >
              <span>
                {t('ask.disclaimer', 'Answers are generated strictly from retrieved official guidelines.')}
              </span>
              <span className={question.length >= MAX_CHARS ? 'font-bold text-[#B3261E]' : ''}>
                {question.length}/{MAX_CHARS}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              isLoading={isLoading}
              disabled={!question.trim() || isLoading}
            >
              {t('ask.submit', 'Ask Question')}
            </Button>

            {(result || error || question) && !isLoading && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleClear}
              >
                {t('ask.clear', 'Clear')}
              </Button>
            )}
          </div>
        </form>

        {/* Slow Server Warning */}
        {isSlow && (
          <Alert variant="warning">
            {t(
              'apiErrors.slowServer',
              'Waking up the server, this can take up to a minute'
            )}
          </Alert>
        )}

        {/* Error Alert */}
        {error && (
          <Alert variant="error" role="alert">
            {error}
          </Alert>
        )}

        {/* Result Area */}
        {result && (
          <div
            className="rounded-lg border border-border-card bg-surface-page p-4"
            aria-live="polite"
            data-ask-result
          >
            {result.answerable ? (
              <div className="space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-[#0E6606]">
                  ✓ {t('ask.answerTitle', 'Official Guideline Answer')}
                </div>
                <p className="text-sm leading-relaxed text-text-primary">
                  {result.answer}
                </p>

                {Array.isArray(result.citations) && result.citations.length > 0 && (
                  <div className="border-t border-border-card pt-3">
                    <div className="text-xs font-bold text-text-muted">
                      {t('ask.citationsTitle', 'Retrieved Official Citations')}:
                    </div>
                    <ul className="mt-1 space-y-1 text-xs text-text-muted">
                      {result.citations.map((cite, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="font-semibold text-navy">•</span>
                          <span>{cite}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-xs font-bold uppercase tracking-wider text-saffron">
                  ℹ {t('ask.notFoundTitle', 'Information Not Found')}
                </div>
                <p className="text-sm leading-relaxed text-text-muted">
                  {result.answer ||
                    t(
                      'ask.notFoundMessage',
                      'This question cannot be answered from the retrieved official scheme guidelines. Please check the official ministry portal or gazette.'
                    )}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

export default SchemeAskBox;

