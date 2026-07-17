import axios from 'axios';

// const apiBaseUrl =
//   process.env.VUE_APP_API_URL || 'http://localhost:9000/api'; // for development

 // const apiBaseUrl =
 // process.env.VUE_APP_API_URL || 'https://api.safepath.duckdns.org/api'; // for production
  //'http://172.28.0.10:9000/api'

const apiBaseUrl =  process.env.VUE_APP_API_URL

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: { 'Content-Type': 'application/json' },
});

export const placeService = {
  search: (query) => api.get('/places', { params: { query } }),
};

export const routeService = {
  safe: (payload) =>
    api.post('/routes/safe', payload),
};

export default api;