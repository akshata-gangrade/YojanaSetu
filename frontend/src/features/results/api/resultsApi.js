import { fetchApi } from '../../../lib/api';

export async function matchSchemes(profile) {
  return fetchApi('/api/v1/match', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}
