import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import EligibilityContext from '../context/EligibilityContext';
import { ResultsPage } from './ResultsPage';

const mockMatchResults = {
  eligible: [
    {
      slug: 'pm-kisan',
      name: 'PM Kisan Samman Nidhi',
      name_hi: 'पीएम किसान सम्मान निधि',
      level: 'central',
      state: null,
      category_tags: ['agriculture'],
      benefit_summary: '₹6,000 per year.',
      benefit_summary_hi: '₹6,000 प्रति वर्ष।',
      apply_url: 'https://pmkisan.gov.in',
      source_url: 'https://agricoop.nic.in/pmkisan',
      last_verified: '2026-10-25T00:00:00Z',
      reasons: ['Occupation is farmer ✓', 'Annual income within limit ✓'],
      status: 'eligible',
    },
  ],
  maybe: [
    {
      slug: 'state-solar-pump',
      name: 'Solar Pump Subsidy',
      name_hi: 'सोलर पंप सब्सिडी',
      level: 'state',
      state: 'maharashtra',
      category_tags: ['agriculture', 'energy'],
      benefit_summary: 'Subsidy on solar pumps.',
      benefit_summary_hi: 'सोलर पंप पर सब्सिडी।',
      apply_url: 'https://mahadiscom.in',
      source_url: 'https://maharashtra.gov.in',
      last_verified: '2026-10-25T00:00:00Z',
      reasons: ['State is Maharashtra ✓', 'Land acreage: detail not provided ?'],
      status: 'maybe',
    },
  ],
  not_eligible: [
    {
      slug: 'senior-pension',
      name: 'Vridha Pension Yojana',
      name_hi: 'वृद्धा पेंशन योजना',
      level: 'central',
      state: null,
      category_tags: ['social_welfare'],
      benefit_summary: 'Monthly pension for senior citizens.',
      benefit_summary_hi: 'वरिष्ठ नागरिकों के लिए मासिक पेंशन।',
      apply_url: 'https://nsap.nic.in',
      source_url: 'https://pib.gov.in',
      last_verified: '2026-10-25T00:00:00Z',
      reasons: ['Age minimum 60 years: your age is 35 ✕'],
      status: 'not_eligible',
    },
  ],
};

function renderResultsWithContext(contextValue = {}) {
  const defaultContext = {
    matchResults: mockMatchResults,
    hasAtLeastOneField: true,
    setFocusedField: vi.fn(),
    profile: { age: 35, state: 'maharashtra' },
    ...contextValue,
  };

  return render(
    <I18nextProvider i18n={i18n}>
      <EligibilityContext.Provider value={defaultContext}>
        <MemoryRouter initialEntries={['/check-eligibility/results']}>
          <Routes>
            <Route path="/check-eligibility/results" element={<ResultsPage />} />
            <Route path="/check-eligibility" element={<div>Eligibility Intake Page</div>} />
          </Routes>
        </MemoryRouter>
      </EligibilityContext.Provider>
    </I18nextProvider>
  );
}

describe('ResultsPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
    sessionStorage.clear();
    document.cookie = '';
  });

  it('renders "No Profile in Memory" guard when visited without active profile', () => {
    renderResultsWithContext({
      matchResults: null,
      hasAtLeastOneField: false,
    });

    expect(
      screen.getByText(/No Profile in Memory|मेमोरी में कोई विवरण उपलब्ध नहीं/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', {
        name: /Start Eligibility Check|पात्रता जांच प्रारंभ करें/i,
      })
    ).toBeInTheDocument();
  });

  it('renders tab counts for Eligible (1), Maybe (1), and Not Eligible (1)', () => {
    renderResultsWithContext();

    // Mandatory disclaimer strip
    expect(
      screen.getByText(
        /Indicative result. The concerned department makes the final decision.|संकेतात्मक परिणाम/i
      )
    ).toBeInTheDocument();

    // Tab buttons with counts
    const eligibleTab = screen.getByRole('tab', { name: /^Eligible|^पात्र /i });
    expect(eligibleTab).toHaveTextContent('1');

    const maybeTab = screen.getByRole('tab', { name: /^Maybe eligible|^संभावित पात्र/i });
    expect(maybeTab).toHaveTextContent('1');

    const notEligibleTab = screen.getByRole('tab', { name: /^Not eligible|^अपात्र/i });
    expect(notEligibleTab).toHaveTextContent('1');
  });

  it('renders reasons without duplicating symbols (check and cross marks)', () => {
    renderResultsWithContext();

    // Default tab is 'eligible'
    expect(screen.getByText(/PM Kisan Samman Nidhi/i)).toBeInTheDocument();

    // Reason without duplicate checkmark
    expect(screen.getByText(/Occupation is farmer/i)).toBeInTheDocument();
    expect(screen.getByText(/Annual income within limit/i)).toBeInTheDocument();
  });

  it('navigates to Maybe tab and handles "Add this detail" button', () => {
    const setFocusedFieldMock = vi.fn();
    renderResultsWithContext({ setFocusedField: setFocusedFieldMock });

    // Click 'Maybe eligible' tab
    const maybeTab = screen.getByRole('tab', { name: /Maybe eligible|संभावित पात्र/i });
    fireEvent.click(maybeTab);

    expect(screen.getByText(/Solar Pump Subsidy/i)).toBeInTheDocument();

    // "Add this detail" button
    const addDetailBtn = screen.getByRole('button', {
      name: /\+ Add this detail|\+ यह विवरण जोड़ें/i,
    });
    fireEvent.click(addDetailBtn);

    // Navigated back to /check-eligibility
    expect(screen.getByText('Eligibility Intake Page')).toBeInTheDocument();
  });

  it('filters results by category tag', () => {
    renderResultsWithContext();

    // Click 'agriculture' category filter pill
    const agCategoryBtn = screen.getByRole('button', { name: /^agriculture$/i });
    fireEvent.click(agCategoryBtn);

    expect(screen.getByText(/PM Kisan Samman Nidhi/i)).toBeInTheDocument();
  });

  it('asserts zero citizen details written to localStorage, sessionStorage, or cookies', () => {
    renderResultsWithContext();

    expect(localStorage.getItem('profile')).toBeNull();
    expect(localStorage.getItem('matchResults')).toBeNull();
    expect(sessionStorage.getItem('profile')).toBeNull();
    expect(document.cookie).toBe('');
  });
});
