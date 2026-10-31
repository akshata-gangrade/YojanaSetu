import { describe, it, expect } from 'vitest';
import { containsPii } from './validators';

describe('PII detection baseline', () => {
  it('detects 10-digit phone numbers', () => {
    expect(containsPii('Call me at 9876543210')).toBe(true);
  });

  it('detects email addresses', () => {
    expect(containsPii('Contact citizen@example.com for info')).toBe(true);
  });

  it('detects PAN format', () => {
    expect(containsPii('My PAN is ABCDE1234F')).toBe(true);
  });

  it('returns false for generic demographic input without PII', () => {
    expect(containsPii('I am a small farmer in Uttar Pradesh aged 42')).toBe(false);
  });
});
