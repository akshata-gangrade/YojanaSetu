import { fetchApi } from '../../../lib/api';

export async function getScheme(slug) {
  return fetchApi(`/api/v1/schemes/${slug}`);
}
