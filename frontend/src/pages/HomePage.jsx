import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button, Card } from '../components/ui';

export function HomePage() {
  const { t } = useTranslation();

  return (
    <div className="space-y-16 py-8">
      {/* 1. HERO SECTION */}
      <section
        data-hero
        aria-labelledby="hero-title"
        className="relative overflow-hidden rounded-[16px] bg-gradient-to-b from-[#0B2A5B] to-[#071C3D] p-8 text-white shadow-soft-lg sm:p-14"
      >
        {/* Subtle bridge backdrop graphic (hidden in high contrast) */}
        <div
          data-hero-arch
          className="pointer-events-none absolute -bottom-16 -right-12 opacity-10"
          aria-hidden="true"
        >
          <svg
            width="400"
            height="320"
            viewBox="0 0 80 64"
            fill="none"
            stroke="currentColor"
          >
            <path d="M10 48 A30 30 0 0 1 70 48" strokeWidth="5" />
            <path d="M21 48 A19 19 0 0 1 59 48" strokeWidth="5" />
            <path d="M4 53 H76" strokeWidth="5" />
          </svg>
        </div>

        <div className="relative z-10 max-w-3xl space-y-6">
          {/* Hero pill badge: 100% Free • Privacy First • No Login Required (no hyphens) */}
          <div
            data-hero-badge
            className="backdrop-blur-xs inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3.5 py-1.5 text-xs font-semibold tracking-wide text-[#FF9933] sm:text-sm"
          >
            <span className="h-2 w-2 rounded-full bg-[#FF9933]" aria-hidden="true" />
            <span>
              {t('hero.badge', '100% Free • Privacy First • No Login Required')}
            </span>
          </div>

          <h1
            id="hero-title"
            className="text-3xl font-black leading-tight tracking-tight text-white sm:text-4xl md:text-5xl"
          >
            {t('hero.title', 'Bridging You to Government Schemes You Deserve')}
          </h1>

          <p className="max-w-2xl text-base leading-relaxed text-slate-200 sm:text-lg">
            {t(
              'hero.subtitle',
              'Find the schemes you qualify for in minutes. We never ask for your name, Aadhaar, phone number, or bank details, and every scheme is checked against its official source.'
            )}
          </p>

          {/* Call to Actions: One clear primary call to action */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              to="/check-eligibility"
              className="focus-visible:ring-3 rounded-lg focus-visible:outline-none focus-visible:ring-[#FF9933]"
            >
              <Button
                variant="primary"
                size="lg"
                iconRight={
                  <svg
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2.5"
                      d="M14 5l7 7m0 0l-7 7m7-7H3"
                    />
                  </svg>
                }
              >
                {t('hero.ctaPrimary', 'Check Your Eligibility')}
              </Button>
            </Link>

            <Link
              to="/schemes"
              className="focus-visible:ring-3 rounded-lg focus-visible:outline-none focus-visible:ring-[#FF9933]"
            >
              <Button
                variant="outline"
                size="lg"
                className="border-white/40 bg-white/10 text-white hover:bg-white/20 hover:text-white"
              >
                {t('hero.ctaSecondary', 'Browse All Schemes')}
              </Button>
            </Link>
          </div>

          {/* Trust stat pills */}
          <div
            data-hero-trust-strip
            className="grid grid-cols-1 gap-4 border-t border-white/20 pt-6 sm:grid-cols-3"
          >
            <div data-hero-stat className="flex items-center gap-3">
              <div
                data-stat-icon
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-white/25 bg-white/10 text-white"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-bold text-white">
                  {t('hero.stat1Value', 'Hindi and English')}
                </p>
                <p className="text-xs text-slate-300">
                  {t('hero.stat1Label', 'Choose your language')}
                </p>
              </div>
            </div>

            <div data-hero-stat className="flex items-center gap-3">
              <div
                data-stat-icon
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-white/25 bg-white/10 text-white"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-bold text-white">
                  {t('hero.stat2Value', 'No personal data stored')}
                </p>
                <p className="text-xs text-slate-300">
                  {t('hero.stat2Label', 'We keep none of your details')}
                </p>
              </div>
            </div>

            <div data-hero-stat className="flex items-center gap-3">
              <div
                data-stat-icon
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-white/25 bg-white/10 text-white"
              >
                <svg
                  className="h-5 w-5"
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
              </div>
              <div>
                <p className="text-sm font-bold text-white">
                  {t('hero.stat3Value', 'Verified sources')}
                </p>
                <p className="text-xs text-slate-300">
                  {t('hero.stat3Label', 'Checked against official government sources')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. THREE-STEP "HOW IT WORKS" */}
      <section aria-labelledby="how-it-works-title" className="space-y-8">
        <div className="mx-auto max-w-2xl space-y-2 text-center">
          <h2
            id="how-it-works-title"
            className="text-2xl font-bold text-navy sm:text-3xl"
          >
            {t('howItWorks.title', 'How YojanaSetu Works')}
          </h2>
          <p className="text-sm text-text-muted sm:text-base">
            {t(
              'howItWorks.subtitle',
              'Three simple, transparent steps to discover government benefits without paperwork hurdles.'
            )}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {/* Step 1 */}
          <Card className="hover:border-navy/40 relative space-y-4 p-6">
            <div
              data-step-icon
              className="border-navy/20 bg-navy/10 flex h-12 w-12 items-center justify-center rounded-xl border text-xl font-black text-navy"
            >
              1
            </div>
            <h3 className="text-lg font-bold text-navy">
              {t('howItWorks.step1Title', '1. Answer Simple Questions')}
            </h3>
            <p className="text-sm leading-relaxed text-text-muted">
              {t(
                'howItWorks.step1Desc',
                'Tell us about your household, state, occupation, or category in plain language. No identity documents required.'
              )}
            </p>
          </Card>

          {/* Step 2 */}
          <Card className="hover:border-navy/40 relative space-y-4 p-6">
            <div
              data-step-icon
              className="border-saffron-dark/20 flex h-12 w-12 items-center justify-center rounded-xl border bg-saffron-light text-xl font-black text-saffron-dark"
            >
              2
            </div>
            <h3 className="text-lg font-bold text-navy">
              {t('howItWorks.step2Title', '2. Fixed-Rule Eligibility Matching')}
            </h3>
            <p className="text-sm leading-relaxed text-text-muted">
              {t(
                'howItWorks.step2Desc',
                'Our rule engine checks eligibility criteria and identifies schemes where you are eligible or may qualify.'
              )}
            </p>
          </Card>

          {/* Step 3 */}
          <Card className="hover:border-navy/40 relative space-y-4 p-6">
            <div
              data-step-icon
              className="border-govgreen/20 flex h-12 w-12 items-center justify-center rounded-xl border bg-govgreen-light text-xl font-black text-govgreen"
            >
              3
            </div>
            <h3 className="text-lg font-bold text-navy">
              {t('howItWorks.step3Title', '3. Direct Official Portal Application')}
            </h3>
            <p className="text-sm leading-relaxed text-text-muted">
              {t(
                'howItWorks.step3Desc',
                'Get verified links to official government portals (.gov.in / .nic.in) along with exact checklists of required documents.'
              )}
            </p>
          </Card>
        </div>
      </section>

      {/* 3. TRUST & PRIVACY SECTION */}
      <section aria-labelledby="trust-title" className="space-y-8">
        <div className="mx-auto max-w-2xl space-y-2 text-center">
          <h2 id="trust-title" className="text-2xl font-bold text-navy sm:text-3xl">
            {t('trust.title', 'Built on Trust, Privacy, and Verified Sources')}
          </h2>
          <p className="text-sm text-text-muted sm:text-base">
            {t(
              'trust.subtitle',
              'Why citizens and advisors rely on YojanaSetu for scheme discovery.'
            )}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <Card className="space-y-3 border-t-4 border-t-navy p-6">
            <div
              data-trust-icon
              className="bg-navy/10 flex h-10 w-10 items-center justify-center rounded-lg text-navy"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <h3 className="text-base font-bold text-navy">
              {t('trust.card1Title', 'Verified Sources')}
            </h3>
            <p className="text-sm leading-relaxed text-text-muted">
              {t(
                'trust.card1Desc',
                'Every scheme rule and criterion is checked directly against published central and state government gazettes and portals.'
              )}
            </p>
          </Card>

          <Card className="space-y-3 border-t-4 border-t-govgreen p-6">
            <div
              data-trust-icon
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-govgreen-light text-govgreen"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
            <h3 className="text-base font-bold text-navy">
              {t('trust.card2Title', 'Privacy Preserving')}
            </h3>
            <p className="text-sm leading-relaxed text-text-muted">
              {t(
                'trust.card2Desc',
                'We do not save your details on our servers or in your browser storage. They are held only in this page\'s memory and are cleared when you refresh or close the tab. We never ask for or store Aadhaar numbers, phone numbers, or bank accounts.'
              )}
            </p>
          </Card>

          <Card className="space-y-3 border-t-4 border-t-saffron-dark p-6">
            <div
              data-trust-icon
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-saffron-light text-saffron-dark"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <h3 className="text-base font-bold text-navy">
              {t('trust.card3Title', 'Clear Qualification Reasons')}
            </h3>
            <p className="text-sm leading-relaxed text-text-muted">
              {t(
                'trust.card3Desc',
                'We clearly distinguish between Eligible, Maybe Eligible, and Not Eligible with plain-language explanations for each criterion.'
              )}
            </p>
          </Card>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
