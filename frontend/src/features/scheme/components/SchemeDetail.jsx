import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, Badge, Button, Checklist, GovLink } from '../../../components/ui';
import { SchemeAskBox } from './SchemeAskBox';
import { formatDate, formatCurrencyINR } from '../../../lib/formatters';

function formatCriterionReadable(criterion, t) {
  if (!criterion || !criterion.field) return null;

  const fieldKey = `criteria.fields.${criterion.field}`;
  const fieldName = t(fieldKey, criterion.field.replace(/_/g, ' '));
  const op = criterion.op;
  const val = criterion.value;

  let valueText = String(val);
  if (criterion.field === 'annual_income') {
    if (Array.isArray(val)) {
      valueText = `${formatCurrencyINR(val[0])} - ${formatCurrencyINR(val[1])}`;
    } else if (typeof val === 'number') {
      valueText = formatCurrencyINR(val);
    }
  } else if (Array.isArray(val)) {
    valueText = val
      .map((v) =>
        t(`criteria.values.${v}`, String(v).replace(/_/g, ' '))
      )
      .join(', ');
  } else if (typeof val === 'string') {
    valueText = t(`criteria.values.${val}`, val.replace(/_/g, ' '));
  }

  let text = '';
  switch (op) {
    case 'eq':
      text = `${fieldName}: ${valueText}`;
      break;
    case 'in':
      text = `${fieldName} must be: ${valueText}`;
      break;
    case 'not_in':
      text = `${fieldName} must not be: ${valueText}`;
      break;
    case 'gte':
      text = `${fieldName} minimum: ${valueText}`;
      break;
    case 'lte':
      text = `${fieldName} maximum: ${valueText}`;
      break;
    case 'between':
      if (Array.isArray(val) && val.length === 2) {
        text = `${fieldName} between ${val[0]} and ${val[1]}`;
      } else {
        text = `${fieldName}: ${valueText}`;
      }
      break;
    default:
      text = `${fieldName}: ${valueText}`;
  }

  if (criterion.as_on) {
    text += ` (${t('criteria.asOn', 'as on')} ${criterion.as_on})`;
  }

  return text;
}

export function SchemeDetail({ scheme }) {
  const { t, i18n } = useTranslation();

  // In-memory document checklist tick state (NEVER persisted to storage/backend)
  const [checkedDocs, setCheckedDocs] = useState({});

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

  // Toggle document checklist in memory
  const handleDocToggle = (docIndex, isChecked) => {
    setCheckedDocs((prev) => ({
      ...prev,
      [docIndex]: isChecked,
    }));
  };

  const docItems = (scheme.required_documents || []).map((doc, idx) => ({
    id: idx,
    label: doc,
    checked: Boolean(checkedDocs[idx]),
  }));

  const allCriteria = [
    ...(scheme.eligibility_criteria?.all_of || []),
    ...(scheme.eligibility_criteria?.any_of || []),
  ];

  const handlePrint = () => {
    window.print();
  };

  return (
    <article className="space-y-8" data-scheme-detail>
      {/* Back to schemes & Print button (hidden in print) */}
      <div className="flex flex-wrap items-center justify-between gap-3 print:hidden">
        <Link
          to="/schemes"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-navy hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy rounded"
        >
          <span aria-hidden="true">&larr;</span>
          <span>{t('schemeDetail.backToDirectory', 'Back to Browse Schemes')}</span>
        </Link>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handlePrint}
          className="print:hidden"
        >
          <span>🖨 {t('schemeDetail.printButton', 'Print this page / PDF')}</span>
        </Button>
      </div>

      {/* Mandatory Indicative Information Strip */}
      <div
        role="note"
        className="rounded-lg border border-saffron/40 bg-saffron/10 px-4 py-3 text-sm font-semibold text-navy"
        data-disclaimer-strip
      >
        <span className="mr-1.5 font-bold" aria-hidden="true">ℹ</span>
        <span>
          {t(
            'schemeDetail.indicativeNotice',
            'Indicative information. The concerned department makes the final decision.'
          )}
        </span>
      </div>

      {/* Header section with badges */}
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="navy" size="md">
            {levelText}
          </Badge>

          {stateFormatted && (
            <Badge variant="neutral" size="md">
              {stateFormatted}
            </Badge>
          )}

          {scheme.is_sample && (
            <Badge
              variant="maybe"
              size="md"
              reason={t('schemes.card.sampleBadge', 'Sample data')}
            >
              {t('schemes.card.sampleData', 'Sample')}
            </Badge>
          )}

          {scheme.is_verified === false && (
            <Badge
              variant="warning"
              size="md"
              icon={
                <svg
                  className="h-4 w-4 shrink-0"
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

          {Array.isArray(scheme.category_tags) &&
            scheme.category_tags.map((tag) => (
              <span
                key={tag}
                className="inline-block rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700"
              >
                {tag}
              </span>
            ))}
        </div>

        <h1 className="text-2xl font-black tracking-tight text-navy sm:text-3xl lg:text-4xl">
          {title}
        </h1>

        <div className="flex flex-wrap items-center gap-4 text-xs text-text-muted sm:text-sm">
          {scheme.is_verified === false ? (
            <div>
              <span className="font-semibold text-[#9A4A00]">
                {t(
                  'schemes.card.notYetVerified',
                  'Not yet verified against the official source'
                )}
              </span>
            </div>
          ) : (
            <>
              <div>
                <span>{t('schemes.card.verifiedOn', 'Verified on')}: </span>
                <span className="font-semibold text-text-primary">
                  {formatDate(scheme.last_verified)}
                </span>
              </div>

              {scheme.verified_by && (
                <div>
                  <span>{t('schemeDetail.verifiedBy', 'Verified by administrator')}: </span>
                  <span className="font-semibold text-text-primary">{scheme.verified_by}</span>
                </div>
              )}
            </>
          )}
        </div>
      </header>

      {/* Benefits Callout */}
      <Card className="border-green/30 bg-[#EAF5EA]/30 p-5 sm:p-6">
        <h2 className="text-base font-bold text-[#0E6606] sm:text-lg">
          {t('schemeDetail.benefitTitle', 'Benefits & Support')}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-text-primary sm:text-base">
          {benefit}
        </p>
      </Card>

      {/* Eligibility Criteria */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold text-navy sm:text-2xl">
          {t('schemeDetail.eligibilityTitle', 'Eligibility Criteria')}
        </h2>

        {allCriteria.length > 0 ? (
          <Card className="divide-y divide-border-card p-0 overflow-hidden">
            {allCriteria.map((crit, idx) => {
              const readable = formatCriterionReadable(crit, t);
              return (
                <div key={idx} className="flex items-start gap-3 p-4">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#EAF5EA] text-xs font-bold text-[#0E6606]">
                    ✓
                  </span>
                  <div className="text-sm font-medium text-text-primary">
                    {readable}
                  </div>
                </div>
              );
            })}
          </Card>
        ) : (
          <p className="text-sm text-text-muted">
            {t('schemeDetail.noCriteriaListed', 'Criteria are evaluated against published guidelines.')}
          </p>
        )}
      </section>

      {/* Required Documents Checklist */}
      <section className="space-y-4">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-navy sm:text-2xl">
            {t('schemeDetail.documentsTitle', 'Required Documents Checklist')}
          </h2>
          <p className="text-xs text-text-muted sm:text-sm">
            {t(
              'schemeDetail.documentsSubtitle',
              'Check off documents as you prepare them. This checklist is kept only in your current browser session and is never stored.'
            )}
          </p>
        </div>

        {docItems.length > 0 ? (
          <Checklist
            items={docItems}
            onToggle={handleDocToggle}
            title={t('schemeDetail.documentsChecklistTitle', 'Application Documents')}
            subtitle={t('schemeDetail.checklistSubtitle', 'Mark documents you have ready')}
          />
        ) : (
          <Card className="p-4 text-sm text-text-muted">
            {t('schemeDetail.noDocumentsListed', 'No specific documents specified in the indexed guideline.')}
          </Card>
        )}
      </section>

      {/* Step-by-step Application Procedure */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold text-navy sm:text-2xl">
          {t('schemeDetail.applicationStepsTitle', 'How to Apply (Step-by-Step)')}
        </h2>

        {Array.isArray(scheme.application_steps) && scheme.application_steps.length > 0 ? (
          <ol className="space-y-3">
            {scheme.application_steps.map((step, idx) => (
              <li
                key={idx}
                className="flex items-start gap-3.5 rounded-[12px] border border-border-card bg-surface-card p-4 shadow-soft"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-navy text-xs font-bold text-white">
                  {idx + 1}
                </span>
                <span className="pt-0.5 text-sm leading-relaxed text-text-primary">
                  {step}
                </span>
              </li>
            ))}
          </ol>
        ) : (
          <Card className="p-4 text-sm text-text-muted">
            {t('schemeDetail.noStepsListed', 'Application steps will be followed on the official portal.')}
          </Card>
        )}
      </section>

      {/* Application Deadline & Official Links */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold text-navy sm:text-2xl">
          {t('schemeDetail.officialLinksTitle', 'Official Application & Source Portals')}
        </h2>

        <Card className="space-y-4 p-5 sm:p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-border-card pb-4">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-text-muted">
                {t('schemeDetail.deadlineLabel', 'Application Deadline')}
              </div>
              <div className="text-sm font-semibold text-text-primary">
                {t('schemeDetail.openOngoing', 'Open / Ongoing under active budget allocation')}
              </div>
            </div>
          </div>

          {/* Official Apply Link */}
          <div className="space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-text-muted">
              {t('schemeDetail.applyPortalLabel', 'Official Application Portal')}
            </div>
            <GovLink
              href={scheme.apply_url}
              className="inline-flex items-center text-sm font-bold text-[#0E6606] hover:underline"
              plainTextClassName="text-sm font-medium text-text-muted"
            >
              {scheme.apply_url}
            </GovLink>
          </div>

          {/* Official Source Link */}
          <div className="space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-text-muted">
              {t('schemeDetail.sourceDocLabel', 'Official Ministry Gazette / Source')}
            </div>
            <GovLink
              href={scheme.source_url}
              className="inline-flex items-center text-sm font-bold text-navy hover:underline"
              plainTextClassName="text-sm font-medium text-text-muted"
            >
              {scheme.source_url}
            </GovLink>
          </div>
        </Card>
      </section>

      {/* Ask About This Scheme (hidden in print, gated by VITE_ENABLE_ASK) */}
      {import.meta.env.VITE_ENABLE_ASK === 'true' && (
        <section className="pt-4 print:hidden">
          <SchemeAskBox slug={scheme.slug} />
        </section>
      )}
    </article>
  );
}

export default SchemeDetail;
