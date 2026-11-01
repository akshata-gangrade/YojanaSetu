import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from '../../../i18n';
import { SchemeAskBox } from './SchemeAskBox';

function renderAskBox(slug = 'pm-kisan') {
  return render(
    <I18nextProvider i18n={i18n}>
      <SchemeAskBox slug={slug} />
    </I18nextProvider>
  );
}

describe('SchemeAskBox', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders input with character limit of 500', () => {
    renderAskBox();

    const textarea = screen.getByLabelText(/Question about scheme guidelines|योजना दिशानिर्देशों के बारे में प्रश्न/i);
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveAttribute('maxLength', '500');
    expect(screen.getByText(/0\/500/)).toBeInTheDocument();
  });

  it('submits question and displays answer with citations when answerable is true', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        answer: 'Farmers with valid land records receive ₹6,000 annually in 3 installments.',
        citations: ['Section 3.1: Eligible Beneficiaries', 'Section 5.2: Installment Schedule'],
        answerable: true,
      }),
    });

    renderAskBox('pm-kisan');

    const textarea = screen.getByLabelText(/Question about scheme guidelines|योजना दिशानिर्देशों के बारे में प्रश्न/i);
    fireEvent.change(textarea, { target: { value: 'How much financial assistance is provided?' } });

    const submitBtn = screen.getByRole('button', { name: /Ask Question|प्रश्न पूछें/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Farmers with valid land records receive ₹6,000/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Section 3.1: Eligible Beneficiaries/i)).toBeInTheDocument();
    expect(screen.getByText(/Section 5.2: Installment Schedule/i)).toBeInTheDocument();
  });

  it('displays not-found message when answerable is false', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        answer: 'This question cannot be answered from the retrieved guidelines.',
        citations: [],
        answerable: false,
      }),
    });

    renderAskBox('pm-kisan');

    const textarea = screen.getByLabelText(/Question about scheme guidelines|योजना दिशानिर्देशों के बारे में प्रश्न/i);
    fireEvent.change(textarea, { target: { value: 'What is the exact bank IFSC code?' } });

    const submitBtn = screen.getByRole('button', { name: /Ask Question|प्रश्न पूछें/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Information Not Found|जानकारी नहीं मिली/i)).toBeInTheDocument();
    });
  });

  it('handles rate limits (429) with friendly advisory message', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({
        error: { code: 'RATE_LIMIT_EXCEEDED', message: 'Too many requests. Please slow down.' },
      }),
      headers: new Headers(),
    });

    renderAskBox('pm-kisan');

    const textarea = screen.getByLabelText(/Question about scheme guidelines|योजना दिशानिर्देशों के बारे में प्रश्न/i);
    fireEvent.change(textarea, { target: { value: 'Can I apply twice?' } });

    const submitBtn = screen.getByRole('button', { name: /Ask Question|प्रश्न पूछें/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/Too many requests, please wait a minute|बहुत अधिक अनुरोध/i)
      ).toBeInTheDocument();
    });
  });
});

