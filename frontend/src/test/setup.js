// Setup file for Vitest with React Testing Library jest-dom matchers
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// JSDOM polyfills for window/element methods
if (typeof window !== 'undefined') {
  window.HTMLElement.prototype.scrollIntoView = vi.fn();
  window.scrollTo = vi.fn();
}
