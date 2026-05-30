const CACHE = "tiktokmall-pwa-v1";
const PRECACHE = [
  "/landing/pwa/",
  "/landing/pwa/manifest.json",
  "/landing/pwa/icons/icon-192.svg",
  "/landing/pwa/icons/icon-512.svg",
  "/landing/index.html",
  "/landing/rotation-engine.js",
  "/landing/domain-config.json"
];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(PRECACHE))
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.url.indexOf("/ai/api/") > -1) {
    return; // API
  }
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request).catch(() => caches.match("/landing/pwa/offline.html")))
  );
});
