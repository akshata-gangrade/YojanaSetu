import { fetchApi } from '../../../lib/api';

export async function loginAdmin(username, password) {
  return fetchApi('/api/v1/admin/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}
