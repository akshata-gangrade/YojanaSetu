import { useState } from 'react';

export function useScheme() {
  const [scheme, setScheme] = useState(null);
  return { scheme, setScheme };
}
