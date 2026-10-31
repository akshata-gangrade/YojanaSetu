import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { UiPreferencesContext } from './useUiPreferences';

export function UiPreferencesProvider({ children }) {
  const { i18n } = useTranslation();

  // 1. Language Preference
  const [language, setLanguageState] = useState(() => {
    try {
      return localStorage.getItem('yojanasetu_lang') || 'en';
    } catch {
      return 'en';
    }
  });

  // 2. Text Size Preference ('normal' = 16px, 'large' = 18px, 'xlarge' = 20px)
  const [textSize, setTextSizeState] = useState(() => {
    try {
      return localStorage.getItem('yojanasetu_text_size') || 'normal';
    } catch {
      return 'normal';
    }
  });

  // 3. High Contrast Mode Preference
  const [highContrast, setHighContrastState] = useState(() => {
    try {
      return localStorage.getItem('yojanasetu_contrast') === 'true';
    } catch {
      return false;
    }
  });

  // Apply Language
  const setLanguage = (newLang) => {
    setLanguageState(newLang);
    i18n.changeLanguage(newLang);
    if (typeof document !== 'undefined') {
      document.documentElement.lang = newLang;
    }
    try {
      localStorage.setItem('yojanasetu_lang', newLang);
    } catch {
      // storage unavailable
    }
  };

  // Apply Text Size
  const setTextSize = (size) => {
    setTextSizeState(size);
    try {
      localStorage.setItem('yojanasetu_text_size', size);
    } catch {
      // storage unavailable
    }
  };

  // Toggle Contrast
  const toggleHighContrast = () => {
    setHighContrastState((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('yojanasetu_contrast', String(next));
      } catch {
        // storage unavailable
      }
      if (typeof document !== 'undefined') {
        if (next) {
          document.documentElement.setAttribute('data-contrast', 'high');
        } else {
          document.documentElement.removeAttribute('data-contrast');
        }
      }
      return next;
    });
  };

  // Synchronize DOM attributes with current preferences
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-text-size', textSize);
      if (highContrast) {
        document.documentElement.setAttribute('data-contrast', 'high');
      } else {
        document.documentElement.removeAttribute('data-contrast');
      }
    }
  }, [textSize, highContrast]);

  return (
    <UiPreferencesContext.Provider
      value={{
        language,
        setLanguage,
        textSize,
        setTextSize,
        highContrast,
        toggleHighContrast,
      }}
    >
      {children}
    </UiPreferencesContext.Provider>
  );
}

export default UiPreferencesProvider;
