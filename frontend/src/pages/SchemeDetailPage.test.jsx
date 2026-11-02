import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import { SchemeDetailPage } from './SchemeDetailPage';

const mockScheme = {
  slug: 'pm-kisan',
  name: 'PM Kisan Samman Nidhi',
  name_hi: 'पीएम किसान सम्मान निधि',
  level: 'central',
  state: null,
  category_tags: ['agriculture'],
  benefit_summary: 'Direct income support of ₹6,000 per year.',
  benefit_summary_hi: '₹6,000 प्रति वर्ष की प्रत्यक्ष आय सहायता।',
  eligibility_criteria: {
    all_of: [
      { field: 'occupation', op: 'eq', value: 'farmer' },
      { field: 'annual_income', op: 'lte', value: 250000 },
    ],
    any_of: [],
  },
  required_documents: ['Aadhaar Card copy', 'Land ownership proof', 'Bank passbook'],
  application_steps: [
    'Visit the official PM-KISAN portal',
    'Click on New Farmer Registration',
    'Enter state and land details',
  ],
  apply_url: 'https://pmkisan.gov.in',
  source_url: 'https://agricoop.nic.in/pmkisan',
  last_verified: '2026-10-20T00:00:00Z',
  is_sample: false,
};

function renderDetail(slug = 'pm-kisan') {
  return render(
    <I18nextProvider i18n={i18n}>
      <MemoryRouter initialEntries={[`/schemes/${slug}`]}>
        <Routes>
          <Route path="/schemes/:slug" element={<SchemeDetailPage />} />
          <Route path="/schemes" element={<div>Browse Directory Page</div>} />
        </Routes>
      </MemoryRouter>
    </I18nextProvider>
  );
}

describe('SchemeDetailPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading skeleton initially', () => {
    globalThis.fetch = vi.fn().mockImplementation(() => new Promise(() => {}));
    renderDetail('pm-kisan');

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders scheme detail with all sections on successful fetch', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockScheme,
    });

    renderDetail('pm-kisan');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/PM Kisan Samman Nidhi/i);
    });

    // Mandatory Disclaimer Strip
    expect(document.querySelector('[data-disclaimer-strip]')).toHaveTextContent(
      /Indicative information. The concerned department makes the final decision.|संकेतात्मक जानकारी/i
    );

    // Benefits Callout
    expect(screen.getByText(/Direct income support of ₹6,000/i)).toBeInTheDocument();

    // Eligibility Criteria
    expect(screen.getByText(/Occupation: Farmer|व्यवसाय: किसान/i)).toBeInTheDocument();

    // Required Documents Checklist
    expect(screen.getByText(/Aadhaar Card copy/i)).toBeInTheDocument();
    expect(screen.getByText(/Land ownership proof/i)).toBeInTheDocument();

    // Application Steps
    expect(screen.getByText(/Visit the official PM-KISAN portal/i)).toBeInTheDocument();

    // Official .gov.in links
    const applyLink = screen.getByRole('link', { name: /https:\/\/pmkisan\.gov\.in/i });
    expect(applyLink).toHaveAttribute('href', 'https://pmkisan.gov.in');
    expect(applyLink).toHaveAttribute('target', '_blank');
    expect(applyLink).toHaveAttribute('rel', 'noopener noreferrer');

    // Print button
    expect(screen.getByRole('button', { name: /Print this page \/ PDF|यह पृष्ठ प्रिंट करें/i })).toBeInTheDocument();
  });

  it('toggles checklist items in React state without modifying storage', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockScheme,
    });

    renderDetail('pm-kisan');

    await waitFor(() => {
      expect(screen.getByLabelText(/Aadhaar Card copy/i)).toBeInTheDocument();
    });

    const checkbox = screen.getByLabelText(/Aadhaar Card copy/i);
    expect(checkbox.checked).toBe(false);

    fireEvent.click(checkbox);
    expect(checkbox.checked).toBe(true);

    // Confirm nothing was stored in localStorage or sessionStorage
    expect(localStorage.getItem('checkedDocs')).toBeNull();
    expect(sessionStorage.getItem('checkedDocs')).toBeNull();
  });

  it('renders 404 Not Found state when scheme does not exist', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({
        error: { code: 'NOT_FOUND', message: 'Scheme not found' },
      }),
      headers: new Headers(),
    });

    renderDetail('invalid-slug');

    await waitFor(() => {
      expect(document.querySelector('[data-not-found]')).toBeInTheDocument();
    });

    expect(screen.getByText(/Scheme Not Found|योजना नहीं मिली/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Browse All Verified Schemes|सभी सत्यापित योजनाएं देखें/i })).toBeInTheDocument();
  });

  it('renders error state with retry on network failure', async () => {
    globalThis.fetch = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('Network Error'))
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockScheme,
      });

    renderDetail('pm-kisan');

    await waitFor(() => {
      expect(document.querySelector('[data-error-state]')).toBeInTheDocument();
    });

    const retryBtn = screen.getByRole('button', { name: /Try Again|पुनः प्रयास करें/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/PM Kisan Samman Nidhi/i);
    });
  });

  it('renders demo mode banner, unverified badge, and replaces verified on line when is_verified is false', async () => {
    const unverifiedScheme = {
      ...mockScheme,
      slug: 'demo-unverified',
      name: 'Demo Unverified Scheme',
      is_verified: false,
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => unverifiedScheme,
      headers: new Headers(),
    });

    renderDetail('demo-unverified');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/Demo Unverified Scheme/i);
    });

    // Top banner is shown
    expect(
      screen.getByText(/Demo mode: some schemes shown here have not been verified against official sources/i)
    ).toBeInTheDocument();

    // Badge "Unverified demo data" is shown
    expect(screen.getByText(/Unverified demo data|असत्यापित डेमो डेटा/i)).toBeInTheDocument();

    // "Verified on" is replaced with "Not yet verified against the official source"
    expect(
      screen.getByText(/Not yet verified against the official source|आधिकारिक स्रोत से अभी तक सत्यापित नहीं/i)
    ).toBeInTheDocument();
    expect(screen.queryByText(/Verified on:/i)).not.toBeInTheDocument();
  });
});

