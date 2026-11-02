import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, Badge, Button } from '../../../components/ui';
import { formatDate } from '../../../lib/formatters';
import { useEligibility } from '../../../context/EligibilityContext';

function parseReasonSymbol(reasonText) {
  if (!reasonText || typeof reasonText !== 'string') {
    return { symbol: '•', type: 'note', text: '' };
  }
  let clean = reasonText.trim();
  let symbol = '✓';
  let type = 'passed';

  if (clean.endsWith('✓')) {
    symbol = '✓';
    type = 'passed';
    clean = clean.slice(0, -1).trim();
  } else if (clean.endsWith('✕') || clean.endsWith('✗') || clean.endsWith('X')) {
    symbol = '✕';
    type = 'failed';
    clean = clean.slice(0, -1).trim();
  } else if (clean.endsWith('?')) {
    symbol = '?';
    type = 'unknown';
    clean = clean.slice(0, -1).trim();
  }

  return { symbol, type, text: clean };
}

function extractMissingField(reasonText) {
  const lower = reasonText.toLowerCase();
  if (lower.includes('age') || lower.includes('आयु')) return 'age';
  if (lower.includes('income') || lower.includes('आय')) return 'annual_income';
  if (lower.includes('state') || lower.includes('राज्य')) return 'state';
  if (lower.includes('gender') || lower.includes('लिंग')) return 'gender';
  if (lower.includes('occupation') || lower.includes('व्यवसाय')) return 'occupation';
  if (lower.includes('category') || lower.includes('श्रेणी')) return 'social_category';
  if (lower.includes('education') || lower.includes('शिक्षा')) return 'education_level';
  if (lower.includes('residence') || lower.includes('निवास')) return 'residence_type';
  if (lower.includes('marital') || lower.includes('वैवाहिक')) return 'marital_status';
  if (lower.includes('disability') || lower.includes('दिव्यांग')) return 'disability_status';
  if (lower.includes('student') || lower.includes('छात्र')) return 'is_student';
  return null;
}

export function ResultSchemeCard({ scheme }) {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { setFocusedField } = useEligibility();

  if (!scheme) return null;

  const isHindi = i18n.language === 'hi';
  const title = (isHindi && scheme.name_hi) ? scheme.name_hi : scheme.name;
  const benefit = (isHindi && scheme.benefit_summary_hi)
    ? scheme.benefit_summary_hi
    : scheme.benefit_summary;

  const levelText = scheme.level === 'central'
    ? t('schemes.card.centralLevel', 'Central Scheme')
    : t('schemes.card.stateLevel', 'State Scheme');

  const stateFormatted = scheme.state
    ? scheme.state
        .split('_')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ')
    : null;

  // Find any missing reason for 'maybe' cards
  const missingReason = (scheme.reasons || []).find((r) => r.includes('?'));
  const missingField = missingReason ? extractMissingField(missingReason) : null;

  const handleAddMissingDetail = () => {
    if (missingField) {
      setFocusedField(missingField);
    }
    navigate('/check-eligibility');
  };

  return (
    <Card className="flex flex-col justify-between p-5 transition-shadow hover:shadow-md sm:p-6" data-result-scheme-card>
      <div className="space-y-4">
        {/* Badges row */}
        <div className="flex flex-wrap items-center gap-2">
          {scheme.status === 'eligible' && (
            <Badge status="eligible" size="sm">
              {t('status.eligible', 'Eligible')}
            </Badge>
          )}
          {scheme.status === 'maybe' && (
            <Badge status="maybe" size="sm">
              {t('status.maybeEligible', 'Maybe Eligible')}
            </Badge>
          )}
          {scheme.status === 'not_eligible' && (
            <Badge status="not-eligible" size="sm">
              {t('status.notEligible', 'Not Eligible')}
            </Badge>
          )}

          <Badge variant="navy" size="sm">
            {levelText}
          </Badge>

          {stateFormatted && (
            <Badge variant="neutral" size="sm">
              {stateFormatted}
            </Badge>
          )}

          {scheme.is_sample && (
            <Badge
              variant="maybe"
              size="sm"
              reason={t('schemes.card.sampleBadge', 'Sample data')}
            >
              {t('schemes.card.sampleData', 'Sample')}
            </Badge>
          )}

          {scheme.is_verified === false && (
            <Badge
              variant="warning"
              size="sm"
              icon={
                <svg
                  className="h-3.5 w-3.5 shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              }
            >
              {t('schemes.card.unverifiedBadge', 'Unverified demo data')}
            </Badge>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-navy sm:text-xl line-clamp-2">
          <Link
            to={`/schemes/${scheme.slug}`}
            className="hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy rounded"
          >
            {title}
          </Link>
        </h3>

        {/* Benefit Summary */}
        <p className="text-sm leading-relaxed text-text-muted line-clamp-3">
          {benefit}
        </p>

        {/* Qualification Reasons Breakdown (No duplicated symbols, text + icon) */}
        {Array.isArray(scheme.reasons) && scheme.reasons.length > 0 && (
          <div className="rounded-lg border border-border-card bg-surface-page p-3.5 space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-text-muted">
              {t('results.reasonsTitle', 'Eligibility Evaluation Reasons')}:
            </div>

            <ul className="space-y-2 text-xs leading-relaxed" role="list">
              {scheme.reasons.map((r, idx) => {
                const { symbol, type, text } = parseReasonSymbol(r);
                const badgeStyle =
                  type === 'passed'
                    ? 'text-[#0E6606] bg-[#EAF5EA] border-[#A3D9A3]'
                    : type === 'failed'
                      ? 'text-[#B3261E] bg-[#FDF2F2] border-[#F8B4B4]'
                      : 'text-[#9A4A00] bg-[#FFF4E5] border-[#FFD099]';

                const textLabel =
                  type === 'passed'
                    ? t('results.conditionPassed', 'Passed')
                    : type === 'failed'
                      ? t('results.conditionFailed', 'Failed')
                      : t('results.conditionMissing', 'Detail needed');

                return (
                  <li key={idx} className="flex items-start gap-2.5">
                    <span
                      aria-hidden="true"
                      className={`inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full border text-[10px] font-bold ${badgeStyle}`}
                    >
                      {symbol}
                    </span>
                    <span className="flex-1 text-text-primary">
                      <span className="sr-only">[{textLabel}] </span>
                      {text}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {/* Missing detail callout for Maybe Eligible */}
        {scheme.status === 'maybe' && (
          <div className="rounded-lg border border-[#FFD099] bg-[#FFF4E5] p-3 text-xs text-[#9A4A00] space-y-2">
            <div className="font-bold flex items-center gap-1.5">
              <span>?</span>
              <span>{t('results.missingDetailPrompt', 'A required detail is missing to confirm qualification.')}</span>
            </div>
            <div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleAddMissingDetail}
                className="text-xs bg-white text-[#9A4A00] border-[#9A4A00] hover:bg-[#FFF4E5]"
              >
                + {t('results.addMissingDetailBtn', 'Add this detail')}
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info & View Details */}
      <div className="mt-6 flex flex-col gap-3 border-t border-border-card pt-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-xs text-text-muted">
          {scheme.is_verified === false ? (
            <span className="font-semibold text-[#9A4A00]">
              {t(
                'schemes.card.notYetVerified',
                'Not yet verified against the official source'
              )}
            </span>
          ) : (
            <>
              <span>{t('schemes.card.verifiedOn', 'Verified on')}: </span>
              <span className="font-semibold text-text-primary">
                {formatDate(scheme.last_verified)}
              </span>
            </>
          )}
        </div>

        <Link
          to={`/schemes/${scheme.slug}`}
          className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy rounded-lg"
        >
          <Button variant="primary" size="sm" className="w-full sm:w-auto">
            {t('schemes.card.viewDetails', 'View details')} &rarr;
          </Button>
        </Link>
      </div>
    </Card>
  );
}

export default ResultSchemeCard;
