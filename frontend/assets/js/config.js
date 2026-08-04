/* Runtime API config — override via <meta name="find-api-base" content="..."> or localStorage */
(function () {
  const meta = document.querySelector('meta[name="find-api-base"]');
  const fromMeta = meta && meta.getAttribute('content');
  const fromStorage = localStorage.getItem('find_api_base');

  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const defaultHost = isLocal
    ? `${window.location.protocol}//${window.location.hostname}:8000/api/v1`
    : '/api/v1';

  window.FIND_API_BASE = fromMeta || fromStorage || defaultHost;
})();
