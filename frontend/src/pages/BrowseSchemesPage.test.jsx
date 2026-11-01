import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import { BrowseSchemesPage } from './BrowseSchemesPage';

function renderWithProviders(ui) {
  return render(
    <I18nextProvider i18n={i18n}>
      <MemoryRouter>{ui}</MemoryRouter>
    </I18nextProvider>
  );
}

describe('BrowseSchemesPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading skeletons on mount', () => {
    // Hang fetch so it stays in loading state
    globalThis.fetch = vi.fn().mockImplementation(() => new Promise(() => {}));

    renderWithProviders(<BrowseSchemesPage />);

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /Browse Government Schemes|सरकारी योजनाएं खोजें/i
    );
    expect(document.querySelector('[data-loading-skeletons]')).toBeInTheDocument();
  });

  it('renders scheme cards on successful API response', async () => {
    const mockSchemes = [
      {
        slug: 'pm-kisan',
        name: 'PM Kisan Samman Nidhi',
        name_hi: 'पीएम किसान सम्मान निधि',
        level: 'central',
        state: null,
        category_tags: ['agriculture'],
        benefit_summary: 'Income support of ₹6,000 per year to all farmer families.',
        benefit_summary_hi: 'सभी किसान परिवारों को ₹6,000 प्रति वर्ष की आय सहायता।',
        apply_url: 'https://pmkisan.gov.in',
        source_url: 'https://agricoop.nic.in/pmkisan',
        last_verified: '2026-10-15T00:00:00Z',
        is_sample: false,
      },
    ];

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        items: mockSchemes,
        total: 1,
        skip: 0,
        limit: 12,
      }),
    });

    renderWithProviders(<BrowseSchemesPage />);

    await waitFor(() => {
      expect(screen.getByText(/PM Kisan Samman Nidhi/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Income support of ₹6,000/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Central Scheme|केंद्रीय योजना/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/View details|विवरण देखें/i)).toBeInTheDocument();
  });

  it('renders "Sample data" badge when is_sample is true', async () => {
    const mockSchemes = [
      {
        slug: 'sample-scheme',
        name: 'Sample Youth Scheme',
        name_hi: 'नमूना युवा योजना',
        level: 'central',
        benefit_summary: 'Financial support for youth.',
        benefit_summary_hi: 'युवाओं के लिए वित्तीय सहायता।',
        apply_url: 'https://myscheme.gov.in',
        source_url: 'https://pib.gov.in',
        last_verified: '2026-10-15T00:00:00Z',
        is_sample: true,
      },
    ];

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        items: mockSchemes,
        total: 1,
        skip: 0,
        limit: 12,
      }),
    });

    renderWithProviders(<BrowseSchemesPage />);

    await waitFor(() => {
      expect(screen.getByText(/Sample Youth Scheme/i)).toBeInTheDocument();
    });

    expect(screen.getAllByText(/Sample|नमूना/i).length).toBeGreaterThan(0);
  });

  it('renders empty state when zero schemes match', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        items: [],
        total: 0,
        skip: 0,
        limit: 12,
      }),
    });

    renderWithProviders(<BrowseSchemesPage />);

    await waitFor(() => {
      expect(document.querySelector('[data-empty-state]')).toBeInTheDocument();
    });

    expect(
      screen.getByText(/Verified Schemes Will Appear Here|सत्यापित योजनाएं यहाँ प्रदर्शित होंगी/i)
    ).toBeInTheDocument();
  });

  it('renders error state and retries on button click', async () => {
    // First call fails, second call succeeds
    globalThis.fetch = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          items: [
            {
              slug: 'pm-kisan',
              name: 'PM Kisan Samman Nidhi',
              level: 'central',
              benefit_summary: 'Income support.',
              apply_url: 'https://pmkisan.gov.in',
              source_url: 'https://pib.gov.in',
              last_verified: '2026-10-15T00:00:00Z',
            },
          ],
          total: 1,
          skip: 0,
          limit: 12,
        }),
      });

    renderWithProviders(<BrowseSchemesPage />);

    await waitFor(() => {
      expect(document.querySelector('[data-error-state]')).toBeInTheDocument();
    });

    const retryBtn = screen.getByRole('button', { name: /Try Again|पुनः प्रयास करें/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText(/PM Kisan Samman Nidhi/i)).toBeInTheDocument();
    });
  });
});

