/* Auth utilities for the Find platform */

const _inPages = () => window.location.pathname.includes('/pages/') || window.location.href.includes('/pages/');
const _pages   = (p) => _inPages() ? p : 'pages/' + p;
const _root    = (p) => _inPages() ? '../' + p : p;

const Auth = {
  getToken:    () => localStorage.getItem('find_token'),
  getUser:     () => { try { return JSON.parse(localStorage.getItem('find_user')); } catch { return null; } },
  isLoggedIn:  () => !!Auth.getToken(),
  isProvider:  () => Auth.getUser()?.role === 'provider',
  isHomeowner: () => Auth.getUser()?.role === 'homeowner',

  save(token, user) {
    localStorage.setItem('find_token', token);
    localStorage.setItem('find_user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('find_token');
    localStorage.removeItem('find_user');
    sessionStorage.removeItem('find_redirect');
    window.location.href = _pages('login.html');
  },

  dashboardUrl(user = Auth.getUser()) {
    return user?.role === 'provider'
      ? _pages('provider-dash.html')
      : _pages('homeowner-dash.html');
  },

  loginUrl(returnTo) {
    const base = _pages('login.html');
    if (!returnTo) return base;
    return `${base}?redirect=${encodeURIComponent(returnTo)}`;
  },

  /** Path to return to after login (same-origin relative URL). */
  currentReturnPath() {
    return window.location.pathname + window.location.search;
  },

  saveRedirect(path) {
    sessionStorage.setItem('find_redirect', path || Auth.currentReturnPath());
  },

  consumeRedirect(fallback) {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get('redirect');
    const fromSession = sessionStorage.getItem('find_redirect');
    sessionStorage.removeItem('find_redirect');

    const candidate = fromQuery || fromSession;
    if (!candidate) return fallback;

    // Block open redirects — only allow relative in-app paths
    if (candidate.includes('://') || candidate.startsWith('//')) return fallback;
    const path = candidate.startsWith('/') ? candidate : candidate.replace(/^\.\//, '');
    if (path.includes('..')) return fallback;
    return path.startsWith('/') ? path : path;
  },

  requireAuth(redirectTo) {
    if (!Auth.isLoggedIn()) {
      Auth.saveRedirect(typeof redirectTo === 'string' ? redirectTo : Auth.currentReturnPath());
      window.location.href = Auth.loginUrl(Auth.currentReturnPath());
      return false;
    }
    return true;
  },

  requireHomeowner() {
    if (!Auth.requireAuth()) return false;
    if (!Auth.isHomeowner()) {
      window.location.href = _pages('provider-dash.html');
      return false;
    }
    return true;
  },

  requireProvider() {
    if (!Auth.requireAuth()) return false;
    if (!Auth.isProvider()) {
      window.location.href = _pages('homeowner-dash.html');
      return false;
    }
    return true;
  },

  requireRole(role) {
    const user = Auth.getUser();
    if (!user || user.role !== role) {
      window.location.href = _root('index.html');
      return false;
    }
    return true;
  },

  /** Use after login/register to land on the intended page. */
  redirectAfterAuth(user) {
    const fallback = user.role === 'provider'
      ? _pages('provider-dash.html')
      : _pages('homeowner-dash.html');
    window.location.href = Auth.consumeRedirect(fallback);
  },
};

/* Populate nav user info if element exists */
function initNavUser() {
  const user = Auth.getUser();
  const navUser   = document.getElementById('nav-user');
  const navLogin  = document.getElementById('nav-login');
  const navLogout = document.getElementById('nav-logout');
  const navDash   = document.getElementById('nav-dash');

  if (user) {
    if (navUser)   { navUser.textContent = user.name; navUser.style.display = 'block'; }
    if (navLogin)  navLogin.style.display = 'none';
    if (navLogout) { navLogout.style.display = 'inline-flex'; navLogout.onclick = Auth.logout; }
    if (navDash) {
      navDash.style.display = 'inline-flex';
      navDash.href = Auth.dashboardUrl(user);
    }
  } else {
    if (navUser)   navUser.style.display = 'none';
    if (navLogout) navLogout.style.display = 'none';
    if (navDash)   navDash.style.display = 'none';
  }
}

/* Scroll-aware navbar */
function initScrollNav() {
  const nb = document.querySelector('.navbar');
  if (!nb) return;
  window.addEventListener('scroll', () => {
    nb.classList.toggle('scrolled', window.scrollY > 40);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initNavUser();
  initScrollNav();
});
