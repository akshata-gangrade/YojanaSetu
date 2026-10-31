import { describe, it, expect } from 'vitest';
import en from './en.json';
import hi from './hi.json';

function getNestedKeys(obj, prefix = '') {
  return Object.keys(obj).reduce((res, el) => {
    if (Array.isArray(obj[el])) {
      return res;
    }
    if (typeof obj[el] === 'object' && obj[el] !== null) {
      return [...res, ...getNestedKeys(obj[el], prefix + el + '.')];
    }
    return [...res, prefix + el];
  }, []);
}

describe('Internationalization (i18n) Parity', () => {
  const enKeys = getNestedKeys(en);
  const hiKeys = getNestedKeys(hi);

  it('ensures every key in en.json exists in hi.json', () => {
    const missingInHi = enKeys.filter((k) => !hiKeys.includes(k));
    expect(missingInHi).toEqual([]);
  });

  it('ensures every key in hi.json exists in en.json', () => {
    const missingInEn = hiKeys.filter((k) => !enKeys.includes(k));
    expect(missingInEn).toEqual([]);
  });

  it('contains critical accessibility keys in both languages', () => {
    expect(en.nav.skipToContent).toBeDefined();
    expect(hi.nav.skipToContent).toBeDefined();
    expect(en.utility.textSize).toBeDefined();
    expect(hi.utility.textSize).toBeDefined();
    expect(en.utility.highContrast).toBeDefined();
    expect(hi.utility.highContrast).toBeDefined();
  });

  it('contains the non-government official disclaimer in both languages', () => {
    expect(en.common.officialDisclaimer).toContain(
      'Not an official Government of India website'
    );
    expect(hi.common.officialDisclaimer).toContain('भारत सरकार की आधिकारिक वेबसाइट नहीं');
  });

  it('contains the privacy guarantee in both languages', () => {
    expect(en.common.privacyGuarantee).toContain('No personal data stored by us');
    expect(hi.common.privacyGuarantee).toContain('कोई व्यक्तिगत डेटा');
  });
});
