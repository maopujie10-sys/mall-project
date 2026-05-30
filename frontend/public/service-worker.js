// Friday AI v2 — API 
const CACHE_NAME = "friday-v2"
const STATIC_ROUTES = ["/ai/friday", "/ai/friday", "/ai/dashboard", "/ai/chat"]

self.addEventListener("install", (e) => {
  self.skipWaiting()
  e.waitUntil(
    caches.open(CACHE_NAME).then((c) => c.addAll(STATIC_ROUTES))
  )
})

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
  )
  e.waitUntil(clients.claim())
})

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url)
  // API 
  if (url.pathname.includes("/api/")) {
    e.respondWith(fetch(e.request))
    return
  }
  // 
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request))
  )
})
