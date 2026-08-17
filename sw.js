const CACHE_NAME = 'ignis-cache-v1';

// Install the service worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(['./index.html', './manifest.json']);
        })
    );
});

// Fetch from network, fallback to cache
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});
