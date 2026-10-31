import { useState } from 'react';

export function useResults() {
  const [results, setResults] = useState([]);
  return { results, setResults };
}
