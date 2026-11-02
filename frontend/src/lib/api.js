import i18n from '../i18n';

/**
 * Custom error class for API failures with structured details.
 */
export class ApiError extends Error {
  constructor(message, status = 0, code = 'UNKNOWN_ERROR', details = null, requestId = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
    this.requestId = requestId;
  }
}

/**
 * Resolves base API URL from VITE_API_BASE_URL (client appends /api/v1).
 */
export function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  // Strip trailing slashes and redundant /api/v1 suffix if accidentally provided
  const sanitized = envUrl.replace(/\/+$/, '').replace(/\/api\/v1$/, '');
  return `${sanitized}/api/v1`;
}

/**
 * Core HTTP fetch wrapper with Render cold-start detection, structured error parsing,
 * and friendly error messages for 404, 413, 429, 503, and network errors.
 *
 * @param {string} endpoint - Path relative to /api/v1 (e.g. '/schemes' or '/schemes/pm-kisan')
 * @param {object} options - Fetch options with custom onSlow callback and headers
 * @returns {Promise<any>}
 */
export async function fetchApi(endpoint, options = {}) {
  const { onSlow, ...fetchOptions } = options;
  const baseUrl = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${cleanEndpoint}`;

  const headers = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers || {}),
  };

  // Render cold-start detector: fire onSlow after 6000ms if request is still pending
  let slowTimer = null;
  if (typeof onSlow === 'function') {
    slowTimer = setTimeout(() => {
      onSlow({
        isSlow: true,
        message: 'Waking up the server, this can take up to a minute',
      });
    }, 6000);
  }

  let response;
  try {
    response = await fetch(url, { ...fetchOptions, headers });
  } catch (networkError) {
    throw new ApiError(
      'Network error. Please check your internet connection and try again.',
      0,
      'NETWORK_ERROR',
      networkError.message
    );
  } finally {
    if (slowTimer) {
      clearTimeout(slowTimer);
    }
  }

  // Handle successful response
  if (response.ok) {
    // Some endpoints may return empty body on 204
    if (response.status === 204) return null;
    return response.json();
  }

  // Parse structured error envelope if available
  let errorData = null;
  try {
    errorData = await response.json();
  } catch {
    // Non-JSON response body
  }

  const envelopeError = errorData?.error;
  const status = response.status;
  const code = envelopeError?.code || `HTTP_${status}`;
  const requestId = envelopeError?.request_id || response.headers.get('x-request-id');
  const details = envelopeError?.details || null;

  // Friendly status-specific fallbacks
  let message = envelopeError?.message;
  if (!message) {
    if (status === 404) {
      message = 'The requested scheme or resource could not be found.';
    } else if (status === 413) {
      message = 'The request payload is too large.';
    } else if (status === 429) {
      message = 'Too many requests, please wait a minute.';
    } else if (status === 503) {
      message = 'The server is temporarily unavailable. Please try again shortly.';
    } else {
      message = `Request failed with status ${status}.`;
    }
  }

  // Guarantee friendly 429 copy even if backend returned a generic phrase
  if (status === 429 && !message.toLowerCase().includes('wait a minute')) {
    message = 'Too many requests, please wait a minute.';
  }

  throw new ApiError(message, status, code, details, requestId);
}

/**
 * Fetch verified schemes list with pagination and filters.
 * Exact backend query parameters: skip, limit, state, level, category.
 */
export async function getSchemes({
  skip = 0,
  limit = 20,
  state = null,
  level = null,
  category = null,
  onSlow = null,
  signal = null,
} = {}) {
  const params = new URLSearchParams();

  if (typeof skip === 'number' && skip >= 0) {
    params.set('skip', skip.toString());
  }
  if (typeof limit === 'number' && limit >= 1) {
    params.set('limit', limit.toString());
  }
  if (state && typeof state === 'string' && state.trim()) {
    params.set('state', state.trim().toLowerCase());
  }
  if (level && (level === 'central' || level === 'state')) {
    params.set('level', level);
  }
  if (category && typeof category === 'string' && category.trim()) {
    params.set('category', category.trim());
  }

  const query = params.toString();
  const endpoint = query ? `/schemes?${query}` : '/schemes';

  return fetchApi(endpoint, {
    method: 'GET',
    onSlow,
    signal,
  });
}

/**
 * Fetch a single scheme by its unique slug.
 */
export async function getSchemeBySlug(slug, { onSlow = null, signal = null } = {}) {
  if (!slug || typeof slug !== 'string') {
    throw new ApiError('Scheme slug is required.', 400, 'INVALID_SLUG');
  }
  return fetchApi(`/schemes/${encodeURIComponent(slug)}`, {
    method: 'GET',
    onSlow,
    signal,
  });
}

/**
 * Ask a grounded question about official scheme guidelines.
 */
export async function askSchemeQuestion(
  slug,
  { question, language = null, onSlow = null, signal = null } = {}
) {
  if (!slug || typeof slug !== 'string') {
    throw new ApiError('Scheme slug is required.', 400, 'INVALID_SLUG');
  }
  if (!question || typeof question !== 'string') {
    throw new ApiError('Question is required.', 400, 'INVALID_QUESTION');
  }

  const lang = language || i18n.language || 'en';

  return fetchApi(`/schemes/${encodeURIComponent(slug)}/ask`, {
    method: 'POST',
    body: JSON.stringify({
      question: question.trim(),
      language: lang,
    }),
    onSlow,
    signal,
  });
}

/**
 * Sanitizes citizen profile object so only non-null valid UserProfile fields are sent,
 * conforming strictly to backend Pydantic model_config extra="forbid".
 */
export function sanitizeProfileForApi(profile) {
  if (!profile || typeof profile !== 'object') return null;
  const clean = {};
  const allowed = [
    'age',
    'gender',
    'state',
    'annual_income',
    'social_category',
    'occupation',
    'education_level',
    'residence_type',
    'marital_status',
    'disability_status',
    'is_student',
  ];
  for (const key of allowed) {
    if (profile[key] !== undefined && profile[key] !== null && profile[key] !== '') {
      clean[key] = profile[key];
    }
  }
  return Object.keys(clean).length > 0 ? clean : null;
}

/**
 * Extract demographic criteria from citizen message via Groq LLM (POST /api/v1/intake/extract).
 */
export async function extractIntake({
  message,
  currentProfile = null,
  language = null,
  onSlow = null,
  signal = null,
} = {}) {
  if (!message || typeof message !== 'string') {
    throw new ApiError('Message is required.', 400, 'INVALID_MESSAGE');
  }

  const lang = language || i18n.language || 'en';

  return fetchApi('/intake/extract', {
    method: 'POST',
    body: JSON.stringify({
      message: message.trim(),
      language: lang,
      current_profile: sanitizeProfileForApi(currentProfile),
    }),
    onSlow,
    signal,
  });
}

/**
 * Match citizen profile against verified schemes in Python rule engine using fixed rules (POST /api/v1/match).
 */
export async function matchSchemes({
  profile,
  language = null,
  onSlow = null,
  signal = null,
} = {}) {
  const lang = language || i18n.language || 'en';

  return fetchApi('/match', {
    method: 'POST',
    body: JSON.stringify({
      profile: sanitizeProfileForApi(profile) || {},
      language: lang,
    }),
    onSlow,
    signal,
  });
}

/**
 * Health check endpoint for backend readiness verification.
 */
export async function checkBackendHealth({ onSlow = null, signal = null } = {}) {
  return fetchApi('/health', {
    method: 'GET',
    onSlow,
    signal,
  });
}
