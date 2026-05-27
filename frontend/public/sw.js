const CACHE = 'friday-ai-v1';
const PRE_CACHE = ['/ai/','/ai/assets/'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRE_CACHE).catch(()=>{})).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x!==CACHE).map(x => caches.delete(x)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('/ai/api/')) return;
  e.respondWith(
    caches.match(e.request).then(c => c || fetch(e.request).then(r => {
      if (r.ok) { const clone = r.clone(); caches.open(CACHE).then(cache => cache.put(e.request, clone)); }
      return r;
    }))
  );
});
