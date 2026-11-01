/**
 * Helper to validate official Government of India web domains (.gov.in / .nic.in).
 * Rejects credentials, case variations, trailing dots, and lookalike domains.
 */

/**
 * Checks whether a given URL points strictly to an official .gov.in or .nic.in domain.
 *
 * Invariants:
 * - Protocol must be http: or https:
 * - Rejects URLs containing user credentials (e.g. user:pass@host)
 * - Hostnames are evaluated case-insensitively
 * - Trailing dots in hostname are stripped before evaluation
 * - Host must be exactly "gov.in", "nic.in" or end with ".gov.in", ".nic.in"
 *
 * @param {string} url - Target URL to evaluate
 * @returns {boolean} True if official allowlisted domain, false otherwise
 */
export function isOfficialGovDomain(url) {
  if (!url || typeof url !== 'string') return false;

  try {
    const parsed = new URL(url);

    // Reject non-web protocols
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return false;
    }

    // Reject URLs with embedded credentials (user:pass@host)
    if (parsed.username || parsed.password) {
      return false;
    }

    // Normalize hostname: lowercase and strip trailing dot
    let hostname = parsed.hostname.toLowerCase();
    if (hostname.endsWith('.')) {
      hostname = hostname.slice(0, -1);
    }

    // Hostname must be exactly or end with .gov.in or .nic.in
    const isGov = hostname === 'gov.in' || hostname.endsWith('.gov.in');
    const isNic = hostname === 'nic.in' || hostname.endsWith('.nic.in');

    return isGov || isNic;
  } catch {
    return false;
  }
}
