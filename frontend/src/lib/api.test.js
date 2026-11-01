import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  fetchApi,
  getSchemes,
  getSchemeBySlug,
  askSchemeQuestion,
  ApiError,
  getApiBaseUrl,
} from './api';

describe('Centralized API Client (lib/api.js)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('constructs base URL ending with /api/v1', () => {
    const url = getApiBaseUrl();
    expect(url).toMatch(/\/api\/v1$/);
  });

  it('handles successful JSON response', async () => {
    const mockData = { items: [], total: 0 };
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const result = await fetchApi('/schemes');
    expect(result).toEqual(mockData);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/schemes'),
      expect.objectContaining({
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      })
    );
  });

  it('triggers onSlow callback if server takes >= 6 seconds (Render cold start)', async () => {
    vi.useFakeTimers();
    const onSlowMock = vi.fn();

    // Pending promise simulating slow cold start
    let resolvePromise;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    globalThis.fetch = vi.fn().mockImplementation(() => pendingPromise);

    const apiCallPromise = fetchApi('/schemes', { onSlow: onSlowMock });

    // Advance time by 5.9 seconds -> should not trigger yet
    vi.advanceTimersByTime(5900);
    expect(onSlowMock).not.toHaveBeenCalled();

    // Advance time by 200ms (total 6.1s) -> should trigger onSlow
    vi.advanceTimersByTime(200);
    expect(onSlowMock).toHaveBeenCalledWith(
      expect.objectContaining({
        isSlow: true,
        message: expect.stringContaining('Waking up the server'),
      })
    );

    // Resolve the promise
    resolvePromise({
      ok: true,
      status: 200,
      json: async () => ({ success: true }),
    });

    const result = await apiCallPromise;
    expect(result).toEqual({ success: true });
  });

  it('maps network errors to friendly ApiError', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(fetchApi('/schemes')).rejects.toThrow(ApiError);
    await expect(fetchApi('/schemes')).rejects.toMatchObject({
      status: 0,
      code: 'NETWORK_ERROR',
      message: 'Network error. Please check your internet connection and try again.',
    });
  });

  it('maps 404 responses to friendly not found message', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({
        error: {
          code: 'NOT_FOUND',
          message: 'Scheme not found',
        },
      }),
      headers: new Headers(),
    });

    await expect(getSchemeBySlug('non-existent')).rejects.toMatchObject({
      status: 404,
      code: 'NOT_FOUND',
    });
  });

  it('maps 413 responses to payload too large', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 413,
      json: async () => ({
        error: {
          code: 'PAYLOAD_TOO_LARGE',
          message: 'Request payload exceeds allowed limit.',
        },
      }),
      headers: new Headers(),
    });

    await expect(fetchApi('/intake/extract', { method: 'POST' })).rejects.toMatchObject({
      status: 413,
      code: 'PAYLOAD_TOO_LARGE',
    });
  });

  it('maps 429 to friendly "too many requests, please wait a minute"', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({
        error: {
          code: 'RATE_LIMIT_EXCEEDED',
          message: 'Too many requests. Please slow down.',
        },
      }),
      headers: new Headers(),
    });

    await expect(fetchApi('/schemes')).rejects.toMatchObject({
      status: 429,
      code: 'RATE_LIMIT_EXCEEDED',
      message: 'Too many requests, please wait a minute.',
    });
  });

  it('maps 503 responses to server unavailable', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({}),
      headers: new Headers(),
    });

    await expect(fetchApi('/schemes')).rejects.toMatchObject({
      status: 503,
      message: 'The server is temporarily unavailable. Please try again shortly.',
    });
  });

  it('builds query parameters with exact backend names for getSchemes', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [], total: 0, skip: 20, limit: 10 }),
    });

    await getSchemes({
      skip: 20,
      limit: 10,
      state: 'Maharashtra',
      level: 'state',
      category: 'agriculture',
    });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining(
        '/api/v1/schemes?skip=20&limit=10&state=maharashtra&level=state&category=agriculture'
      ),
      expect.anything()
    );
  });

  it('sends question and language to askSchemeQuestion', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        answer: 'Financial support is ₹6,000 annually.',
        citations: ['Section 4.1'],
        answerable: true,
      }),
    });

    const res = await askSchemeQuestion('pm-kisan', {
      question: 'What is the benefit amount?',
      language: 'en',
    });

    expect(res.answerable).toBe(true);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/schemes/pm-kisan/ask'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          question: 'What is the benefit amount?',
          language: 'en',
        }),
      })
    );
  });
});

