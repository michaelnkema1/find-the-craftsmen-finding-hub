/* Auth utilities for the Find platform */

// Relative-path helpers — work for both file:// and http://
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
    window.location.href = _pages('login.html');
  },

  requireAuth(redirectTo) {
    if (!Auth.isLoggedIn()) {
      window.location.href = redirectTo || _pages('login.html');
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
      navDash.href = user.role === 'provider'
        ? _pages('provider-dash.html')
        : _pages('homeowner-dash.html');
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
