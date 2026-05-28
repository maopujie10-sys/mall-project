self.addEventListener("install", (e) => {
  self.skipWaiting()
  e.waitUntil(
    caches.open("friday-v1").then((c) => {
      return c.addAll(["/ai/", "/ai/friday", "/ai/dashboard", "/ai/chat"])
    })
  )
})
self.addEventListener("activate", (e) => {
  e.waitUntil(clients.claim())
})
self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request).catch(() => new Response("离线", { status: 503 })))
  )
})
