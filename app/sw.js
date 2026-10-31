// Offline layer. build.py fills in the version and the file list, so each build gets its own cache.
const VERSION = '__VERSION__';
const FILES = __FILES__;
const CACHE = `trip-${VERSION}`;

// Install downloads the whole site into one cache. The worker takes over only once everything is stored.
self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) if (name !== CACHE) await caches.delete(name);
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
  event.respondWith((async () => {
    const cached = await (await caches.open(CACHE)).match(request, { ignoreSearch: true });
    if (!cached) return fetch(request);
    return request.headers.has('range') ? partial(cached, request.headers.get('range')) : cached;
  })());
});

// Audio elements ask for byte ranges and Safari will not play without a 206 answer. The cache holds whole files, so slice one.
async function partial(response, range) {
  const blob = await response.blob();
  const size = blob.size;
  const [, start = '', end = ''] = /bytes=(\d*)-(\d*)/.exec(range) || [];
  const from = start === '' ? Math.max(0, size - Number(end)) : Number(start);
  const to = start === '' || end === '' ? size - 1 : Math.min(Number(end), size - 1);
  if (Number.isNaN(from) || from > to) return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${size}` } });
  return new Response(blob.slice(from, to + 1), {
    status: 206,
    headers: {
      'Content-Type': response.headers.get('Content-Type') || 'application/octet-stream',
      'Content-Range': `bytes ${from}-${to}/${size}`,
      'Content-Length': String(to - from + 1),
      'Accept-Ranges': 'bytes',
    },
  });
}
