const V = 'bikepark-v3';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'vendor/leaflet.js', 'vendor/leaflet.css',
  'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png', 'data/spots.json', 'data/theft.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL.map(u => new Request(u, {cache: 'reload'})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  e.respondWith(caches.open(V).then(async c => {
    const hit = await c.match(e.request, {ignoreSearch: true});
    const fresh = fetch(e.request, {cache: 'no-cache'}).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; });
    // The page itself: newest copy when there is signal, saved copy after 3 seconds or offline.
    if (e.request.mode === 'navigate') {
      const slow = new Promise(done => setTimeout(() => done(hit), 3000));
      e.waitUntil(fresh.catch(() => {}));
      return Promise.race([fresh.catch(() => hit), hit ? slow : fresh]).then(r => r || fresh);
    }
    // Everything else: saved copy straight away, refreshed in the background.
    e.waitUntil(fresh.catch(() => {}));
    return hit || fresh;
  }));
});
