/**
 * Client-side input validation and PII detection.
 */
export const PII_PATTERNS = {
  aadhaar: /\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b/,
  pan: /\b[A-Z]{5}[0-9]{4}[A-Z]\b/,
  phone: /\b(?:\+91|0)?[6-9]\d{9}\b/,
  email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
};

export function containsPii(text) {
  if (!text || typeof text !== 'string') return false;
  return Object.values(PII_PATTERNS).some((pattern) => pattern.test(text));
}
