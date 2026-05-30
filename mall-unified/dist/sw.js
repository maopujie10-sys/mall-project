// TikTokMall PWA Service Worker
const CACHE_NAME = 'mall-unified-v1'

// 安装时预缓存关键资源
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      cache.addAll([
        '/',
        '/m',
        '/manifest.json',
      ]).catch(() => {})
    )
  )
  self.skipWaiting()
})

// 激活时清理旧缓存
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  )
  self.clients.claim()
})

// 网络优先策略（动态内容）→ 离线回退到缓存
self.addEventListener('fetch', event => {
  // 跳过非 GET 和 API 请求
  if (event.request.method !== 'GET') return
  if (event.request.url.includes('/api/')) return

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // 缓存成功的响应
        if (response.status === 200) {
          const clone = response.clone()
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone))
        }
        return response
      })
      .catch(() =>
        // 离线：返回缓存
        caches.match(event.request).then(cached =>
          cached || caches.match('/')
        )
      )
  )
})

// 推送通知
self.addEventListener('push', event => {
  const data = event.data?.json() || { title: 'TikTokMall', body: '您有新的订单消息' }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/icons/icon-192.png',
      badge: '/icons/icon-72.png',
      tag: 'mall-notification',
      renotify: true,
      vibrate: [200, 100, 200]
    })
  )
})

self.addEventListener('notificationclick', event => {
  event.notification.close()
  event.waitUntil(clients.openWindow('/m/order'))
})
