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

  listUsers: (params = {}) => api.get('/admin/users', { params }),
  createUser: (payload) => api.post('/admin/users', payload),
  updateUser: (id, payload) => api.put(`/admin/users/${id}`, payload),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),

  loginEvents: (params = {}) => api.get('/admin/login-events', { params }),
  syncLoginEvents: () => api.post('/admin/login-events/sync'),
};
export default api;

// Incident reports. create/recent are public; listAdmin/updateStatus require Admin.
export const incidentService = {
  create: (payload) => api.post('/incidents', payload),
  recent: (params = {}) => api.get('/incidents/recent', { params }),
  listAdmin: (params = {}) => api.get('/admin/incidents', { params }),
};

export const userService = {
  me: () => api.get('/me'),
  deleteMe: () => api.delete('/me'),
  getAvatar: () => api.get('/me/avatar'),
  updateAvatar: (avatar) => api.put('/me/avatar', { avatar }),
};