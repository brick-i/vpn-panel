const BASE = '/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.hash = '#/login';
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }

  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res;
}

export const api = {
  // Auth
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  setup: (username, password) =>
    request('/auth/setup', { method: 'POST', body: JSON.stringify({ username, password }) }),
  getMe: () => request('/auth/me'),
  getSetupStatus: () => request('/auth/setup-status'),

  // Server
  getServerStatus: () => request('/server/status'),
  startServer: () => request('/server/start', { method: 'POST' }),
  stopServer: () => request('/server/stop', { method: 'POST' }),
  restartServer: () => request('/server/restart', { method: 'POST' }),
  getServerConfig: () => request('/server/config'),
  updateServerConfig: (data) =>
    request('/server/config', { method: 'PUT', body: JSON.stringify(data) }),
  installServer: () => request('/server/install', { method: 'POST' }),
  getInstallProgress: () => request('/server/install/progress'),

  // Clients
  getClients: () => request('/clients'),
  createClient: (data) =>
    request('/clients', { method: 'POST', body: JSON.stringify(data) }),
  updateClient: (id, data) =>
    request(`/clients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteClient: (id) => request(`/clients/${id}`, { method: 'DELETE' }),

  // Stats
  getStatsOverview: () => request('/stats/overview'),
  getTrafficStats: () => request('/stats/traffic'),
  getClientStats: () => request('/stats/clients'),
  getSystemInfo: () => request('/stats/system'),
};
