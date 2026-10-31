import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './en.json';
import hi from './hi.json';

const savedLang =
  typeof window !== 'undefined' ? localStorage.getItem('yojanasetu_lang') || 'en' : 'en';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    hi: { translation: hi },
  },
  lng: savedLang,
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false, // React already escapes values
  },
});

if (typeof document !== 'undefined') {
  document.documentElement.lang = savedLang;
}

i18n.on('languageChanged', (lng) => {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lng;
    try {
      localStorage.setItem('yojanasetu_lang', lng);
    } catch {
      // Storage unavailable or disabled
    }
  }
});

export default i18n;
