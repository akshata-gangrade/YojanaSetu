import { createContext, useContext } from 'react';

export const UiPreferencesContext = createContext(null);

export function useUiPreferences() {
  const context = useContext(UiPreferencesContext);
  if (!context) {
    throw new Error('useUiPreferences must be used within a UiPreferencesProvider');
  }
  return context;
}

export default useUiPreferences;
