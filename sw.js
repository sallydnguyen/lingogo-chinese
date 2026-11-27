const CACHE_NAME = 'lingogo-chinese-offline-v2';
const CORE_ASSETS = ['./', './index.html', './version.json', './data/zh.json'];
self.addEventListener('install', (e) => { self.skipWaiting(); e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(CORE_ASSETS).catch(() => {}))); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const req = e.request; if (req.method !== 'GET') return;
  if (new URL(req.url).origin !== self.location.origin) return;
  e.respondWith(caches.match(req, { ignoreSearch: true }).then((c) => c || fetch(req).then((r) => {
    if (r && r.status === 200) { const cp = r.clone(); caches.open(CACHE_NAME).then((ca) => ca.put(req, cp)).catch(() => {}); }
    return r;
  }).catch(() => c || new Response('', { status: 503 }))));
});
