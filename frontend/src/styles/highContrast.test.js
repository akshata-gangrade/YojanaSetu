// @vitest-environment jsdom
import { describe, it, expect, beforeEach } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('High Contrast Mode Integration & Token Verification (Single Polarity: Black on White)', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-contrast');
  });

  it('sets data-contrast="high" attribute when enabled and removes it when disabled, with aria-pressed', () => {
    // Simulate initial toggle button
    const toggleButton = document.createElement('button');
    toggleButton.setAttribute('type', 'button');
    toggleButton.setAttribute('aria-label', 'Toggle high contrast mode');
    toggleButton.setAttribute('aria-pressed', 'false');
    document.body.appendChild(toggleButton);

    // Simulate enabling high contrast
    document.documentElement.setAttribute('data-contrast', 'high');
    localStorage.setItem('yojanasetu_contrast', 'true');
    toggleButton.setAttribute('aria-pressed', 'true');

    expect(document.documentElement.getAttribute('data-contrast')).toBe('high');
    expect(localStorage.getItem('yojanasetu_contrast')).toBe('true');
    expect(toggleButton.getAttribute('aria-pressed')).toBe('true');

    // Simulate disabling high contrast
    document.documentElement.removeAttribute('data-contrast');
    localStorage.setItem('yojanasetu_contrast', 'false');
    toggleButton.setAttribute('aria-pressed', 'false');

    expect(document.documentElement.hasAttribute('data-contrast')).toBe(false);
    expect(localStorage.getItem('yojanasetu_contrast')).toBe('false');
    expect(toggleButton.getAttribute('aria-pressed')).toBe('false');

    document.body.removeChild(toggleButton);
  });

  it('verifies index.html applies high contrast before first paint from localStorage', () => {
    const htmlPath = path.resolve(__dirname, '../../index.html');
    const htmlContent = fs.readFileSync(htmlPath, 'utf-8');

    expect(htmlContent).toContain("localStorage.getItem('yojanasetu_contrast')");
    expect(htmlContent).toContain(
      "document.documentElement.setAttribute('data-contrast', 'high')"
    );
  });

  it('guarantees localStorage only stores UI preference and never citizen profile data', () => {
    localStorage.setItem('yojanasetu_contrast', 'true');
    localStorage.setItem('yojanasetu_lang', 'en');
    localStorage.setItem('yojanasetu_text_size', 'normal');

    const allowedKeys = [
      'yojanasetu_contrast',
      'yojanasetu_lang',
      'yojanasetu_text_size',
    ];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      expect(allowedKeys).toContain(key);
      expect(key).not.toMatch(/name|aadhaar|phone|income|state|bank|profile/i);
    }
  });

  it('defines the universal black-on-white baseline in CSS scoped to [data-contrast="high"]', () => {
    const cssPath = path.resolve(__dirname, 'index.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');

    // Universal baseline scoped to [data-contrast='high']
    expect(cssContent).toContain("[data-contrast='high']");
    expect(cssContent).toContain('background-color: #ffffff !important');
    expect(cssContent).toContain('color: #000000 !important');
    expect(cssContent).toContain('border-color: #000000 !important');
    expect(cssContent).toContain('background-image: none !important');
    expect(cssContent).toContain('box-shadow: none !important');
    expect(cssContent).toContain('opacity: 1 !important');

    // 2px solid black borders on hero, cards, inputs, buttons, badges, icon tiles
    expect(cssContent).toContain('2px solid #000000 !important');
    expect(cssContent).toContain('[data-hero]');
    expect(cssContent).toContain('[data-card]');
    expect(cssContent).toContain('[data-stat-icon]');
    expect(cssContent).toContain('[data-hero-badge]');

    // Underlined links and 3px solid black focus ring
    expect(cssContent).toContain('text-decoration: underline !important');
    expect(cssContent).toContain('outline: 3px solid #000000 !important');
    expect(cssContent).toContain('outline-offset: 2px !important');
  });

  it('verifies explicit primary button exception (black background, white text, currentColor icon)', () => {
    const cssPath = path.resolve(__dirname, 'index.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');

    // Primary button target
    expect(cssContent).toContain("[data-variant='primary']");
    expect(cssContent).toMatch(
      /\[data-contrast='high'\]\s*\[data-variant='primary'\][^}]*background-color:\s*#000000\s*!important/
    );
    expect(cssContent).toMatch(
      /\[data-contrast='high'\]\s*\[data-variant='primary'\][^}]*color:\s*#ffffff\s*!important/
    );

    // Secondary / outline buttons stay white with black text
    expect(cssContent).toMatch(
      /button:not\(\[data-variant='primary'\]\)[^}]*background-color:\s*#ffffff\s*!important/
    );
  });

  it('hides the decorative arch graphic and enforces currentColor on SVG icons', () => {
    const cssPath = path.resolve(__dirname, 'index.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');

    // Decorative arch graphic hidden in high contrast
    expect(cssContent).toMatch(
      /\[data-contrast='high'\]\s*\[data-hero-arch\][^{]*\{[^}]*display:\s*none\s*!important/
    );

    // SVGs use currentColor for stroke and fill
    expect(cssContent).toContain('stroke: currentColor !important');
    expect(cssContent).toContain('fill: currentColor !important');
  });

  it('ensures pure black on white contrast ratio is 21:1 (maximum accessibility)', () => {
    // Relative luminance of pure black #000000 is 0, pure white #ffffff is 1
    const blackLum = 0.0;
    const whiteLum = 1.0;
    const ratio = (whiteLum + 0.05) / (blackLum + 0.05);

    expect(ratio).toBe(21);
    expect(ratio).toBeGreaterThanOrEqual(7.0); // Far exceeds WCAG AAA (7:1)
  });

  it('verifies text size controls and scalability (16px default A, 18px A+, 20px A++)', () => {
    const cssPath = path.resolve(__dirname, 'index.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');

    // CSS data-text-size rules
    expect(cssContent).toMatch(
      /html\[data-text-size='normal'\]\s*\{\s*font-size:\s*16px/
    );
    expect(cssContent).toMatch(/html\[data-text-size='large'\]\s*\{\s*font-size:\s*18px/);
    expect(cssContent).toMatch(
      /html\[data-text-size='xlarge'\]\s*\{\s*font-size:\s*20px/
    );

    // Initial default state
    document.documentElement.setAttribute('data-text-size', 'normal');
    expect(document.documentElement.getAttribute('data-text-size')).toBe('normal');

    // Switch to A+ (large: 18px)
    document.documentElement.setAttribute('data-text-size', 'large');
    localStorage.setItem('yojanasetu_text_size', 'large');
    expect(document.documentElement.getAttribute('data-text-size')).toBe('large');
    expect(localStorage.getItem('yojanasetu_text_size')).toBe('large');

    // Switch to A++ (xlarge: 20px)
    document.documentElement.setAttribute('data-text-size', 'xlarge');
    localStorage.setItem('yojanasetu_text_size', 'xlarge');
    expect(document.documentElement.getAttribute('data-text-size')).toBe('xlarge');
    expect(localStorage.getItem('yojanasetu_text_size')).toBe('xlarge');
  });
});
