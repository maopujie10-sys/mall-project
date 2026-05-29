// Friday AI v2 — 只缓存静态页面，API 请求直通网络
const CACHE_NAME = "friday-v2"
const STATIC_ROUTES = ["/ai/", "/ai/friday", "/ai/dashboard", "/ai/chat"]

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
  // API 请求：只用网络，不缓存
  if (url.pathname.includes("/api/")) {
    e.respondWith(fetch(e.request))
    return
  }
  // 静态资源：缓存回退
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request))
  )
})
