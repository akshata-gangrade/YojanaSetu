import { useState } from 'react';

export function useIntake() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  return { profile, setProfile, loading, setLoading };
}
