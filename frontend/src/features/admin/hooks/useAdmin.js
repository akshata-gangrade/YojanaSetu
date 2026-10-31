import { useState } from 'react';

export function useAdmin() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  return { isAuthenticated, setIsAuthenticated };
}
