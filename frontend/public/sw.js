// Friday AI v2 — 只缓存静态页面，API 请求直通网络
self.addEventListener("install", () => self.skipWaiting())
self.addEventListener("activate", () => self.clients.claim())
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url)
  // API 请求：只用网络，不查缓存
  if (url.pathname.includes("/api/")) {
    e.respondWith(fetch(e.request))
    return
  }
  // 静态资源：缓存回退
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  )
})
