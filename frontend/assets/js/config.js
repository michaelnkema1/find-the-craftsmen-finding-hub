/* Runtime API config — override via <meta name="find-api-base" content="..."> */
(function () {
  const meta = document.querySelector('meta[name="find-api-base"]');
  const fromMeta = meta && meta.getAttribute('content');
  const fromHost = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
  window.FIND_API_BASE = fromMeta || fromHost;
})();
