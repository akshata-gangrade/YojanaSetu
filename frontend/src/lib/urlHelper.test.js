import { describe, it, expect } from 'vitest';
import { isOfficialGovDomain } from './urlHelper';

describe('Official Government Domain Validator (isOfficialGovDomain)', () => {
  it('accepts legitimate .gov.in and .nic.in domains', () => {
    expect(isOfficialGovDomain('https://myscheme.gov.in')).toBe(true);
    expect(isOfficialGovDomain('https://pib.gov.in/PressReleasePage.aspx')).toBe(true);
    expect(isOfficialGovDomain('https://agricoop.nic.in/en/schemes')).toBe(true);
    expect(isOfficialGovDomain('http://pmkisan.gov.in')).toBe(true);
    expect(isOfficialGovDomain('https://sub.portal.gov.in/scheme')).toBe(true);
    expect(isOfficialGovDomain('https://sub.portal.nic.in/scheme')).toBe(true);
    expect(isOfficialGovDomain('https://gov.in')).toBe(true);
    expect(isOfficialGovDomain('https://nic.in')).toBe(true);
  });

  it('evaluates hostnames case-insensitively', () => {
    expect(isOfficialGovDomain('https://MYSCHEME.GOV.IN')).toBe(true);
    expect(isOfficialGovDomain('https://Pib.Gov.In/docs')).toBe(true);
    expect(isOfficialGovDomain('https://AgriCoop.Nic.In')).toBe(true);
    expect(isOfficialGovDomain('HTTP://SCHEME.GOV.IN')).toBe(true);
  });

  it('ignores trailing dot in FQDN hostnames', () => {
    expect(isOfficialGovDomain('https://myscheme.gov.in./')).toBe(true);
    expect(isOfficialGovDomain('https://agricoop.nic.in./page')).toBe(true);
  });

  it('rejects URLs containing user credentials (user:pass@host)', () => {
    expect(isOfficialGovDomain('https://user:pass@myscheme.gov.in')).toBe(false);
    expect(isOfficialGovDomain('https://admin@myscheme.gov.in')).toBe(false);
    expect(isOfficialGovDomain('http://token:x@agricoop.nic.in')).toBe(false);
  });

  it('rejects lookalike and spoofing domains', () => {
    // Suffix spoofing
    expect(isOfficialGovDomain('https://evil-gov.in.com')).toBe(false);
    expect(isOfficialGovDomain('https://gov.in.evil.com')).toBe(false);
    expect(isOfficialGovDomain('https://nic.in.attacker.org')).toBe(false);
    expect(isOfficialGovDomain('https://myscheme.gov.in.co')).toBe(false);

    // Prefix lookalikes
    expect(isOfficialGovDomain('https://fakegov.in')).toBe(false);
    expect(isOfficialGovDomain('https://notgov.in')).toBe(false);
    expect(isOfficialGovDomain('https://fakenic.in')).toBe(false);
    expect(isOfficialGovDomain('https://mygov.in.fake')).toBe(false);
  });

  it('rejects non-http/https protocols', () => {
    expect(isOfficialGovDomain('ftp://myscheme.gov.in')).toBe(false);
    expect(isOfficialGovDomain('javascript:alert(1)')).toBe(false);
    expect(isOfficialGovDomain('data:text/html,test')).toBe(false);
    expect(isOfficialGovDomain('file:///etc/passwd')).toBe(false);
  });

  it('rejects empty, non-string, or malformed inputs', () => {
    expect(isOfficialGovDomain('')).toBe(false);
    expect(isOfficialGovDomain(null)).toBe(false);
    expect(isOfficialGovDomain(undefined)).toBe(false);
    expect(isOfficialGovDomain(12345)).toBe(false);
    expect(isOfficialGovDomain('not-a-valid-url')).toBe(false);
    expect(isOfficialGovDomain('http://')).toBe(false);
  });
});

