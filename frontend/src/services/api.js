import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:9000/api',
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