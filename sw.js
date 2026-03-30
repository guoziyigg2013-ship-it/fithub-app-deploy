const CACHE_NAME = "fithub-shell-v1";

function coreUrls() {
  const scope = self.registration.scope;
  return [
    scope,
    new URL("index.html", scope).href,
    new URL("styles.css", scope).href,
    new URL("app.js", scope).href,
    new URL("mobile.html", scope).href
  ];
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(coreUrls()))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request, { ignoreSearch: true });
  const networkPromise = fetch(request)
    .then((response) => {
      if (response && response.ok) {
        cache.put(request, response.clone());
      }
      return response;
    })
    .catch(() => null);

  return cached || networkPromise || fetch(request);
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.includes("/api/") || url.pathname === "/healthz") return;

  if (request.mode === "navigate") {
    const shellUrl = new URL("index.html", self.registration.scope).href;
    event.respondWith(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        const cachedShell = await cache.match(shellUrl, { ignoreSearch: true });
        const networkShell = fetch(request)
          .then((response) => {
            if (response && response.ok) {
              cache.put(shellUrl, response.clone());
            }
            return response;
          })
          .catch(() => null);
        return cachedShell || networkShell || fetch(request);
      })()
    );
    return;
  }

  if (/\.(?:js|css|html)$/i.test(url.pathname) || url.pathname.endsWith("/")) {
    event.respondWith(staleWhileRevalidate(request));
  }
});
