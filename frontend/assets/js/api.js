/* API client for the Find platform */
const API_BASE = window.FIND_API_BASE || 'http://localhost:8000/api/v1';

const api = {
  _headers(auth = true) {
    const h = { 'Content-Type': 'application/json' };
    if (auth) {
      const token = localStorage.getItem('find_token');
      if (token) h['Authorization'] = `Bearer ${token}`;
    }
    return h;
  },

  async request(method, path, body = null, auth = true) {
    const opts = { method, headers: this._headers(auth) };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(`${API_BASE}${path}`, opts);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      return data;
    } catch (e) {
      throw e;
    }
  },

  get:    (path, auth)        => api.request('GET',    path, null, auth),
  post:   (path, body, auth)  => api.request('POST',   path, body, auth),
  patch:  (path, body)        => api.request('PATCH',  path, body),
  delete: (path)              => api.request('DELETE', path),

  /* Auth */
  register: (body) => api.post('/auth/register', body, false),
  login:    (body) => api.post('/auth/login',    body, false),
  getMe:    ()     => api.get('/users/me'),
  updateMe: (body) => api.patch('/users/me', body),

  /* Providers */
  searchProviders: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/providers${qs ? '?' + qs : ''}`);
  },
  getProvider:    (id, params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/providers/${id}${qs ? '?' + qs : ''}`);
  },
  updateProvider: (id, body) => api.patch(`/providers/${id}`, body),

  /* Bookings */
  createBooking:       (body)         => api.post('/bookings', body),
  listBookings:        ()             => api.get('/bookings'),
  updateBookingStatus: (id, status)   => api.patch(`/bookings/${id}/status`, { status }),

  /* Reviews */
  createReview:        (body)    => api.post('/reviews', body),
  getProviderReviews:  (id)      => api.get(`/reviews/provider/${id}`),
};

/* Toast helper */
function showToast(msg, type = 'success') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    document.body.appendChild(el);
  }
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const colors = {
    success: 'background: rgba(16,185,129,.15); border: 1px solid rgba(16,185,129,.3); color: #10B981;',
    error:   'background: rgba(239,68,68,.15);  border: 1px solid rgba(239,68,68,.3);  color: #EF4444;',
    info:    'background: rgba(245,158,11,.12); border: 1px solid rgba(245,158,11,.3); color: #F59E0B;',
  };
  el.style.cssText = colors[type] || colors.success;
  el.innerHTML = `<span>${icons[type] || ''}</span> ${msg}`;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 3500);
}

/* Stars renderer */
function renderStars(rating, max = 5) {
  return Array.from({ length: max }, (_, i) =>
    `<span class="star ${i < Math.round(rating) ? 'filled' : ''}">★</span>`
  ).join('');
}

/* Avatar initials */
function avatarInitials(name = '') {
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase();
}

/* Skills array from comma string */
function skillTags(skills = '') {
  return skills.split(',').filter(Boolean).map(s =>
    `<span class="skill-tag">${s.trim()}</span>`
  ).join('');
}

function statusBadge(status) {
  const labels = {
    pending: 'Pending', confirmed: 'Confirmed', in_progress: 'In Progress',
    provider_done: 'Awaiting Your Confirmation', completed: 'Completed', cancelled: 'Cancelled'
  };
  const map = {
    pending: 'badge-pending', confirmed: 'badge-confirmed',
    in_progress: 'badge-progress', provider_done: 'badge-progress',
    completed: 'badge-completed', cancelled: 'badge-cancelled'
  };
  return `<span class="badge ${map[status] || ''}">${labels[status] || status}</span>`;
}

/* Format date */
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}
