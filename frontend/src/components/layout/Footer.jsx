import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Logo } from '../ui/Logo';

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer
      className="mt-auto border-t border-[#0B2A5B] bg-[#071C3D] pb-8 pt-12 text-white"
      role="contentinfo"
      aria-label="Site footer"
    >
      <div className="mx-auto max-w-[1200px] space-y-8 px-4 sm:px-6 lg:px-8">
        {/* Top Grid */}
        <div className="grid grid-cols-1 items-start gap-8 md:grid-cols-12">
          {/* Brand & Purpose */}
          <div className="space-y-4 md:col-span-5">
            <Logo variant="horizontal" size="md" inverted />
            <p className="max-w-sm text-sm leading-relaxed text-slate-300">
              {t(
                'common.allRightsReserved',
                'Independent public information portal. Scheme criteria verified against respective central and state ministry guidelines.'
              )}
            </p>
            <div
              data-footer-badge
              className="border-saffron/30 bg-saffron/15 inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-semibold text-saffron"
            >
              <span className="h-2 w-2 rounded-full bg-saffron" aria-hidden="true" />
              <span>
                {t(
                  'common.officialDisclaimer',
                  'Not an official Government of India website.'
                )}
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-3 md:col-span-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              {t('nav.browseSchemes', 'Navigation')}
            </h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>
                <Link
                  to="/"
                  className="inline-flex min-h-[36px] items-center rounded hover:text-white hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933]"
                >
                  {t('nav.home', 'Home')}
                </Link>
              </li>
              <li>
                <Link
                  to="/check-eligibility"
                  className="inline-flex min-h-[36px] items-center rounded hover:text-white hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933]"
                >
                  {t('nav.checkEligibility', 'Check Eligibility')}
                </Link>
              </li>
              <li>
                <Link
                  to="/schemes"
                  className="inline-flex min-h-[36px] items-center rounded hover:text-white hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933]"
                >
                  {t('nav.browseSchemes', 'Browse Schemes')}
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Trust */}
          <div className="space-y-3 md:col-span-4">
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              {t('nav.about', 'Legal & Disclaimer')}
            </h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>
                <Link
                  to="/about"
                  className="inline-flex min-h-[36px] items-center rounded hover:text-white hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933]"
                >
                  {t('nav.about', 'About & Legal Disclaimer')}
                </Link>
              </li>
              <li>
                <Link
                  to="/privacy"
                  className="inline-flex min-h-[36px] items-center rounded hover:text-white hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933]"
                >
                  {t('nav.privacy', 'Privacy Policy')}
                </Link>
              </li>
              <li>
                <Link
                  to="/terms"
                  className="inline-flex min-h-[36px] items-center rounded hover:text-white hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF9933]"
                >
                  {t('nav.terms', 'Terms of Service')}
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Privacy Highlight Banner in Footer */}
        <div
          data-footer-privacy
          className="flex items-start gap-3 rounded-[12px] border border-[#163B75] bg-[#0B2A5B]/70 p-4 text-xs text-slate-300 sm:text-sm"
        >
          <svg
            className="mt-0.5 h-5 w-5 shrink-0 text-saffron"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
            />
          </svg>
          <p className="leading-relaxed">
            <strong className="text-white">Privacy Guarantee: </strong>
            {t(
              'common.privacyGuarantee',
              'No personal data stored by us. We never ask for or store Aadhaar, PAN, phone number, email, or bank details.'
            )}
          </p>
        </div>

        {/* Bottom Bar: Disclaimer & Last Updated */}
        <div className="flex flex-col items-center justify-between gap-4 border-t border-[#163B75] pt-6 text-xs text-slate-400 sm:flex-row">
          <p>
            © {new Date().getFullYear()} YojanaSetu &mdash;{' '}
            <span className="font-medium text-slate-300">
              {t(
                'common.officialDisclaimer',
                'Not an official Government of India website.'
              )}
            </span>
          </p>
          <div className="flex items-center gap-2">
            <span>Checked against official sources:</span>
            <span className="rounded border border-[#163B75] bg-[#0B2A5B] px-2 py-0.5 font-semibold text-slate-200">
              {t('common.lastUpdated', 'October 2026')}
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
