self.addEventListener('install', (e) => {
  self.skipWaiting()
  e.waitUntil(
    caches.open('tiktokmall-v1').then((c) => c.addAll(['/pwa/', '/wap/', '/www/']))
  )
})
self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim())
})
self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request).catch(() => new Response('离线模式', { status: 503 })))
  )
})