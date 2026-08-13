import axios from 'axios';

// keycloak
import keycloak from './keycloak'; 

// error handling
import { showError } from './errorStore';

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

// Map common status codes to short titles.
const STATUS_TITLES = {
  400: 'Bad Request',
  401: 'Unauthorized',
  403: 'Forbidden',
  404: 'Not Found',
  408: 'Request Timeout',
  409: 'Conflict',
  422: 'Invalid Data',
  500: 'Server Error',
  502: 'Bad Gateway',
  503: 'Service Unavailable',
  504: 'Gateway Timeout',
};

api.interceptors.response.use(
  (response) => response, // success passes through untouched
  (error) => {
    const status = error.response?.status;
    // FastAPI returns { detail: "..." } — fall back to axios message.
    const detail =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Unknown error';

    // Don't dialog 401 — the request interceptor already sends the user to
    // keycloak.login(); showing an error on top would be noise.
    if (status !== 401) {
      showError({
        status,
        title: STATUS_TITLES[status] || 'Request Failed',
        message: detail,
      });
    }

    return Promise.reject(error); // still reject so callers can react if they want
  }
);

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
};