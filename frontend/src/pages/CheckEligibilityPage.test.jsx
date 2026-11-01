import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import { EligibilityProvider } from '../context/EligibilityContext';
import { CheckEligibilityPage } from './CheckEligibilityPage';

function renderCheckEligibility() {
  return render(
    <I18nextProvider i18n={i18n}>
      <EligibilityProvider>
        <MemoryRouter initialEntries={['/check-eligibility']}>
          <Routes>
            <Route path="/check-eligibility" element={<CheckEligibilityPage />} />
            <Route path="/check-eligibility/results" element={<div>Results Mock Page</div>} />
          </Routes>
        </MemoryRouter>
      </EligibilityProvider>
    </I18nextProvider>
  );
}

describe('CheckEligibilityPage Integration', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
    sessionStorage.clear();
    document.cookie = '';
  });

  it('initially gates user behind the consent card before showing chat', () => {
    renderCheckEligibility();

    expect(screen.getByText(/Before You Check Your Eligibility|पात्रता जांचने से पहले यह समझें/i)).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /Your Details|आपका विवरण/i })).not.toBeInTheDocument();

    // Click continue button
    const continueBtn = screen.getByRole('button', {
      name: /I understand, continue|मैं समझ गया\/गई, आगे बढ़ें/i,
    });
    fireEvent.click(continueBtn);

    // Chat and Your Details panel are now unlocked
    expect(screen.getByRole('heading', { name: /Your Details|आपका विवरण/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Conversational Eligibility Guide|संवादात्मक पात्रता मार्गदर्शक/i })).toBeInTheDocument();
  });

  it('performs a chat turn that merges extracted fields into the details panel', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        profile_updates: {
          age: 29,
          state: 'bihar',
          occupation: 'farmer',
        },
        missing_fields: ['gender'],
        next_question: 'What is your gender?',
        pii_notice: null,
      }),
    });

    renderCheckEligibility();

    // Unlock consent
    fireEvent.click(screen.getByRole('button', { name: /I understand, continue|मैं समझ गया\/गई, आगे बढ़ें/i }));

    const textarea = screen.getByLabelText(/Citizen situation description|नागरिक स्थिति का विवरण/i);
    fireEvent.change(textarea, { target: { value: 'I am a 29 year old farmer living in Bihar' } });

    const sendBtn = screen.getByRole('button', { name: /Send|भेजें/i });
    fireEvent.click(sendBtn);

    // Assert fetch was called with /intake/extract
    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/intake/extract'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('"message":"I am a 29 year old farmer living in Bihar"'),
        })
      );
    });

    // Assistant reply displayed in transcript
    await waitFor(() => {
      expect(screen.getByText(/What is your gender\?/i)).toBeInTheDocument();
    });

    // Details panel fields updated automatically
    const ageInput = screen.getByLabelText(/Age|आयु/i);
    expect(ageInput).toHaveValue(29);

    const stateSelect = screen.getByLabelText(/^State|^राज्य/i);
    expect(stateSelect).toHaveValue('bihar');

    const occupationSelect = screen.getByLabelText(/Occupation|व्यवसाय/i);
    expect(occupationSelect).toHaveValue('farmer');

    // Quick-reply chips rendered for missing field 'gender'
    expect(screen.getByRole('button', { name: /^Female$|^महिला$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Male$|^पुरुष$/i })).toBeInTheDocument();

    // Zero data written to storage
    expect(localStorage.getItem('profile')).toBeNull();
    expect(sessionStorage.getItem('profile')).toBeNull();
    expect(document.cookie).toBe('');
  });

  it('quick-reply chip sets field directly and chip value wins over model conflict', async () => {
    // Turn 1 returns missing_fields: ['gender']
    // Turn 2 returns conflicting model extraction { gender: 'male' }
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          profile_updates: {},
          missing_fields: ['gender'],
          next_question: 'Please select your gender',
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          profile_updates: { gender: 'male' }, // conflict from model
          missing_fields: [],
          next_question: 'Thank you for providing your gender.',
        }),
      });

    renderCheckEligibility();
    fireEvent.click(screen.getByRole('button', { name: /I understand, continue|मैं समझ गया\/गई, आगे बढ़ें/i }));

    // Pre-populate missing field gender via chat
    const textarea = screen.getByLabelText(/Citizen situation description|नागरिक स्थिति का विवरण/i);
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByRole('button', { name: /Send|भेजें/i }));

    // Wait for chips
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Female|महिला/i })).toBeInTheDocument();
    });

    // Click 'Female' chip
    const femaleChip = screen.getByRole('button', { name: /Female|महिला/i });
    fireEvent.click(femaleChip);

    // Chip value wins: gender in details panel MUST be female, not male!
    await waitFor(() => {
      const genderSelect = screen.getByLabelText(/Gender|लिंग/i);
      expect(genderSelect).toHaveValue('female');
    });
  });

  it('direct manual edits in the details panel update state and enable matching', async () => {
    renderCheckEligibility();
    fireEvent.click(screen.getByRole('button', { name: /I understand, continue|मैं समझ गया\/गई, आगे बढ़ें/i }));

    const matchBtn = screen.getByRole('button', { name: /See my matching schemes|मेरी पात्र योजनाएं देखें/i });
    expect(matchBtn).toBeDisabled();

    // Type age directly
    const ageInput = screen.getByLabelText(/Age|आयु/i);
    fireEvent.change(ageInput, { target: { value: '45' } });
    expect(ageInput).toHaveValue(45);

    // Match button is now enabled
    expect(matchBtn).not.toBeDisabled();

    // Select state directly
    const stateSelect = screen.getByLabelText(/^State|^राज्य/i);
    fireEvent.change(stateSelect, { target: { value: 'punjab' } });
    expect(stateSelect).toHaveValue('punjab');
  });

  it('"Clear my details" resets all fields, transcript, and ignores delayed responses', async () => {
    let delayedResolve;
    const pendingPromise = new Promise((resolve) => {
      delayedResolve = resolve;
    });

    globalThis.fetch = vi.fn().mockImplementation(() => pendingPromise);

    renderCheckEligibility();
    fireEvent.click(screen.getByRole('button', { name: /I understand, continue|मैं समझ गया\/गई, आगे बढ़ें/i }));

    // Send a message that is delayed
    const textarea = screen.getByLabelText(/Citizen situation description|नागरिक स्थिति का विवरण/i);
    fireEvent.change(textarea, { target: { value: 'I am 50 years old' } });
    fireEvent.click(screen.getByRole('button', { name: /Send|भेजें/i }));

    // Click "Clear my details" while request is in flight
    const clearBtn = screen.getByRole('button', { name: /Clear my details|मेरा विवरण साफ़ करें/i });
    fireEvent.click(clearBtn);

    // All fields are reset immediately
    const ageInput = screen.getByLabelText(/Age|आयु/i);
    expect(ageInput).toHaveValue(null);

    // Resolve the delayed response now
    delayedResolve({
      ok: true,
      status: 200,
      json: async () => ({
        profile_updates: { age: 50 },
        missing_fields: [],
        next_question: 'Next question',
      }),
    });

    // Wait a tick and verify delayed response was DISCARDED
    await new Promise((r) => setTimeout(r, 50));
    expect(ageInput).toHaveValue(null);
  });

  it('calls POST /match and navigates to results when clicking "See my matching schemes"', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        eligible: [],
        maybe: [],
        not_eligible: [],
      }),
    });

    renderCheckEligibility();
    fireEvent.click(screen.getByRole('button', { name: /I understand, continue|मैं समझ गया\/गई, आगे बढ़ें/i }));

    // Set age to enable match button
    const ageInput = screen.getByLabelText(/Age|आयु/i);
    fireEvent.change(ageInput, { target: { value: '30' } });

    const matchBtn = screen.getByRole('button', { name: /See my matching schemes|मेरी पात्र योजनाएं देखें/i });
    fireEvent.click(matchBtn);

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/match'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('"age":30'),
        })
      );
    });

    // Navigated to results mock page
    await waitFor(() => {
      expect(screen.getByText('Results Mock Page')).toBeInTheDocument();
    });
  });
});
