import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, Badge, Button } from '../../../components/ui';
import { formatDate } from '../../../lib/formatters';

export function SchemeCard({ scheme }) {
  const { t, i18n } = useTranslation();
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

  return (
    <Card className="flex flex-col justify-between p-5 transition-shadow hover:shadow-md sm:p-6">
      <div className="space-y-3">
        {/* Badges row */}
        <div className="flex flex-wrap items-center gap-2">
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

          {Array.isArray(scheme.category_tags) &&
            scheme.category_tags.map((tag) => (
              <span
                key={tag}
                className="inline-block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700"
              >
                {tag}
              </span>
            ))}
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
      </div>

      {/* Footer Info & Action */}
      <div className="mt-6 flex flex-col gap-3 border-t border-border-card pt-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-xs text-text-muted">
          <span>{t('schemes.card.verifiedOn', 'Verified on')}: </span>
          <span className="font-semibold text-text-primary">
            {formatDate(scheme.last_verified)}
          </span>
        </div>

        <Link
          to={`/schemes/${scheme.slug}`}
          className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy rounded-lg"
          tabIndex={-1}
        >
          <Button variant="outline" size="sm" className="w-full sm:w-auto">
            {t('schemes.card.viewDetails', 'View details')}
          </Button>
        </Link>
      </div>
    </Card>
  );
}

export default SchemeCard;

