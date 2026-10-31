import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui';

export function NotFoundPage() {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col items-center justify-center space-y-6 px-4 py-20 text-center">
      <div
        data-404-badge
        className="shadow-2xs border-saffron-dark/20 flex h-24 w-24 items-center justify-center rounded-full border bg-saffron-light text-3xl font-black text-saffron-dark"
      >
        404
      </div>

      <div className="max-w-md space-y-2">
        <h1 className="text-3xl font-black text-navy">
          {t('pages.notFound.title', '404 - Page Not Found')}
        </h1>
        <p className="text-base text-text-muted">
          {t(
            'pages.notFound.subtitle',
            'The page you are looking for does not exist or has been moved.'
          )}
        </p>
      </div>

      <Link
        to="/"
        className="focus-visible:ring-3 rounded-lg focus-visible:outline-none focus-visible:ring-navy"
      >
        <Button variant="primary" size="md">
          {t('pages.notFound.cta', 'Return to Homepage')}
        </Button>
      </Link>
    </div>
  );
}

export default NotFoundPage;
