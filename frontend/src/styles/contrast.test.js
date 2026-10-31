import { describe, it, expect } from 'vitest';

/**
 * Calculate relative luminance and contrast ratio according to WCAG 2.1 specifications:
 * https://www.w3.org/WAI/GL/wiki/Relative_luminance
 */
function hexToRgb(hex) {
  const cleanHex = hex.replace('#', '');
  const bigint = parseInt(cleanHex, 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255,
  };
}

function getChannelLuminance(channel255) {
  const c = channel255 / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function getLuminance(hex) {
  const { r, g, b } = hexToRgb(hex);
  return (
    0.2126 * getChannelLuminance(r) +
    0.7152 * getChannelLuminance(g) +
    0.0722 * getChannelLuminance(b)
  );
}

function getContrastRatio(hex1, hex2) {
  const lum1 = getLuminance(hex1);
  const lum2 = getLuminance(hex2);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}

describe('YojanaSetu Design System - WCAG 2.1 AA Contrast Compliance', () => {
  const MIN_AA_NORMAL_TEXT = 4.5;

  it('verifies Navy #0B2A5B on White #FFFFFF exceeds 4.5:1 (passes AAA)', () => {
    const ratio = getContrastRatio('#0B2A5B', '#FFFFFF');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(13.0);
  });

  it('verifies Dark Saffron #9A4A00 on White #FFFFFF exceeds 4.5:1 for small text', () => {
    const ratio = getContrastRatio('#9A4A00', '#FFFFFF');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(5.0);
  });

  it('verifies Maybe Eligible saffron text #9A4A00 on light tint #FFF4E5 exceeds 4.5:1', () => {
    const ratio = getContrastRatio('#9A4A00', '#FFF4E5');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(4.9);
  });

  it('verifies Saffron #FF9933 on Navy #0B2A5B exceeds 4.5:1 for accents and highlights', () => {
    const ratio = getContrastRatio('#FF9933', '#0B2A5B');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(6.5);
  });

  it('verifies Green #138808 on White #FFFFFF exceeds 4.5:1 (Eligible status)', () => {
    const ratio = getContrastRatio('#138808', '#FFFFFF');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(4.5);
  });

  it('verifies White #FFFFFF text on Green #138808 button exceeds 4.5:1', () => {
    const ratio = getContrastRatio('#FFFFFF', '#138808');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(4.5);
  });

  it('verifies Primary text #1A2433 on White #FFFFFF exceeds 4.5:1 (passes AAA)', () => {
    const ratio = getContrastRatio('#1A2433', '#FFFFFF');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(14.0);
  });

  it('verifies Primary text #1A2433 on Page BG #F7F9FC exceeds 4.5:1 (passes AAA)', () => {
    const ratio = getContrastRatio('#1A2433', '#F7F9FC');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(13.5);
  });

  it('verifies Muted text #55627A on White #FFFFFF exceeds 4.5:1', () => {
    const ratio = getContrastRatio('#55627A', '#FFFFFF');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(5.2);
  });

  it('verifies Muted text #55627A on Page BG #F7F9FC exceeds 4.5:1', () => {
    const ratio = getContrastRatio('#55627A', '#F7F9FC');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(5.0);
  });

  it('verifies Disqualification reason #B3261E on White #FFFFFF exceeds 4.5:1', () => {
    const ratio = getContrastRatio('#B3261E', '#FFFFFF');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(5.6);
  });

  it('verifies Disqualification reason #B3261E on Neutral Grey #F1F5F9 exceeds 4.5:1', () => {
    const ratio = getContrastRatio('#B3261E', '#F1F5F9');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(5.0);
  });

  it('verifies Eligible text #0E6606 on light green tint #EAF5EA exceeds 4.5:1', () => {
    const ratio = getContrastRatio('#0E6606', '#EAF5EA');
    expect(ratio).toBeGreaterThanOrEqual(MIN_AA_NORMAL_TEXT);
    expect(ratio).toBeGreaterThan(6.0);
  });
});
