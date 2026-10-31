import { fetchApi } from '../../../lib/api';

export async function submitIntakeText(text) {
  return fetchApi('/api/v1/intake', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}
