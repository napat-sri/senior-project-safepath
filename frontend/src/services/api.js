import axios from 'axios';

// keycloak
import keycloak from './keycloak'; 

const apiBaseUrl =  process.env.VUE_APP_API_URL
const api = axios.create({
  baseURL: apiBaseUrl,
  headers: { 'Content-Type': 'application/json' },
});
// Add a fresh Keycloak token to every request when the user is logged in.
api.interceptors.request.use(async (config) => {
  if (keycloak.authenticated) {
    try {
      await keycloak.updateToken(30);
      config.headers.Authorization = `Bearer ${keycloak.token}`;
    } catch (err) {
      keycloak.login();
    }
  }
  return config;
});

export const placeService = {
  search: (query) => api.get('/places', { params: { query } }),
};
export const routeService = {
  safe: (payload) =>
    api.post('/routes/safe', payload),
};
// Admin: user route-search logs, sourced from Langfuse traces.
// params: { minutes, limit } — both optional (backend defaults 1440 / 100).
export const adminService = {
  searchLogs: (params = {}) => api.get('/admin/search-logs', { params }),
};
export default api;