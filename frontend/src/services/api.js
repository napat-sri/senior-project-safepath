import axios from 'axios';

const apiBaseUrl =
  process.env.VUE_APP_API_URL || 'http://localhost:9000/api';

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: { 'Content-Type': 'application/json' },
});

export const placeService = {
  search: (query) => api.get('/places', { params: { query } }),
};

export const routeService = {
  analyze: (origin, destination) =>
    api.post('/routes', { origin, destination }),
};

export default api;