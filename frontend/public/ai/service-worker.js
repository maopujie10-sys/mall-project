// Friday AI PWA Service Worker v3
const CACHE_NAME = "friday-ai-v3"
const PRE_CACHE = ["/ai/", "/ai/friday", "/ai/dashboard", "/ai/chat"]

// Install: pre-cache key routes
self.addEventListener("install", (e) => {
  self.skipWaiting()
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRE_CACHE).catch(() => {}))
  )
})

// Activate: clean old caches
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  )
  e.waitUntil(clients.claim())
})

// Fetch: network-first for API, cache-first for static
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url)
  // Bypass cache for API calls
  if (url.pathname.includes("/api/") || url.pathname.includes("/agent/")) {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)))
    return
  }
  // Cache-first for static assets
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((res) => {
      if (res.ok && (url.pathname.endsWith(".js") || url.pathname.endsWith(".css") || url.pathname.endsWith(".svg"))) {
        const clone = res.clone()
        caches.open(CACHE_NAME).then((c) => c.put(e.request, clone))
      }
      return res
    }))
  )
})
