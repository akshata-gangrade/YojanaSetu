import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from '../../../i18n';
import { ConsentGate } from './ConsentGate';

describe('ConsentGate Component', () => {
  it('renders consent disclosure with all security and privacy points', () => {
    const onConsentMock = vi.fn();
    render(
      <I18nextProvider i18n={i18n}>
        <ConsentGate onConsent={onConsentMock} />
      </I18nextProvider>
    );

    // Header & Badge
    expect(screen.getByText(/Zero Data Storage • Privacy First|कोई डेटा संग्रह नहीं/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(
      /Before You Check Your Eligibility|पात्रता जांचने से पहले यह समझें/i
    );

    // Mandatory privacy points
    expect(screen.getByText(/What is asked|क्या पूछा जाता है/i)).toBeInTheDocument();
    expect(screen.getByText(/No personal data stored|कोई व्यक्तिगत डेटा संगृहीत नहीं/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Processed by an AI service|एआई \(AI\) सेवा द्वारा संसाधित/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Never enter identity or banking details|पहचान या बैंक विवरण कभी दर्ज न करें/i)).toBeInTheDocument();
    expect(screen.getByText(/Sensitive fields are strictly optional|संवेदनशील विवरण पूरी तरह वैकल्पिक हैं/i)).toBeInTheDocument();
  });

  it('triggers onConsent when clicking continue button', () => {
    const onConsentMock = vi.fn();
    render(
      <I18nextProvider i18n={i18n}>
        <ConsentGate onConsent={onConsentMock} />
      </I18nextProvider>
    );

    const continueBtn = screen.getByRole('button', {
      name: /I understand, continue|मैं समझ गया\/गई, आगे बढ़ें/i,
    });
    fireEvent.click(continueBtn);

    expect(onConsentMock).toHaveBeenCalledTimes(1);
  });
});
