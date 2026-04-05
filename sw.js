// TodayFortune Service Worker - Notification support + offline caching
const CACHE_NAME = 'todayfortune-v1';
const OFFLINE_URLS = ['/', '/ja/', '/ko/'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_URLS))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  // Network-first for HTML, cache-first for assets
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request).catch(() => caches.match(e.request).then(r => r || caches.match('/')))
    );
  }
});

// Handle notification click - open the site
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const lang = e.notification.data && e.notification.data.lang || 'en';
  const urlMap = { en: '/', ja: '/ja/', ko: '/ko/' };
  const url = 'https://todayfortune.net' + (urlMap[lang] || '/');
  e.waitUntil(
    clients.matchAll({ type: 'window' }).then(list => {
      for (const client of list) {
        if (client.url.includes('todayfortune.net') && 'focus' in client) return client.focus();
      }
      return clients.openWindow(url);
    })
  );
});
