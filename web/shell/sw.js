// ==========================================================================
// Pokemon Infinite Fusion — Service Worker
//
// Caching strategy:
//   - Shell files (HTML, CSS, JS): Cache-first, update in background
//   - WASM/data bundles: Cache-first (versioned by hash)
//   - Lazy game assets: Cache-first after first fetch
//   - API/external: Network-only (no caching)
// ==========================================================================

const CACHE_VERSION = 'pif-web-v1';

// Shell files to precache on install
const PRECACHE_URLS = [
    './',
    'index.html',
    'shell.css',
    'shell.js',
    'game.js',
    'game.wasm',
    'game.data',
    'game-data.js',
    'manifest.json',
];

// URL patterns that should NOT be cached
const NO_CACHE_PATTERNS = [
    /\/api\//,
    /google-analytics/,
    /firebase/,
];

// ---------------------------------------------------------------------------
// Install: precache shell files
// ---------------------------------------------------------------------------
self.addEventListener('install', function (event) {
    console.log('[sw] Installing service worker:', CACHE_VERSION);
    event.waitUntil(
        caches.open(CACHE_VERSION)
            .then(function (cache) {
                console.log('[sw] Precaching shell files');
                return cache.addAll(PRECACHE_URLS);
            })
            .then(function () {
                // Skip waiting to activate immediately
                return self.skipWaiting();
            })
            .catch(function (err) {
                console.warn('[sw] Precache failed (non-fatal):', err);
                return self.skipWaiting();
            })
    );
});

// ---------------------------------------------------------------------------
// Activate: clean old caches
// ---------------------------------------------------------------------------
self.addEventListener('activate', function (event) {
    console.log('[sw] Activating service worker:', CACHE_VERSION);
    event.waitUntil(
        caches.keys()
            .then(function (cacheNames) {
                return Promise.all(
                    cacheNames
                        .filter(function (name) { return name !== CACHE_VERSION; })
                        .map(function (name) {
                            console.log('[sw] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(function () {
                return self.clients.claim();
            })
    );
});

// ---------------------------------------------------------------------------
// Fetch: cache-first for game assets, network-first for shell
// ---------------------------------------------------------------------------
self.addEventListener('fetch', function (event) {
    var url = new URL(event.request.url);

    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Skip cross-origin requests (CORS issues)
    if (url.origin !== self.location.origin) return;

    // Skip no-cache patterns
    for (var i = 0; i < NO_CACHE_PATTERNS.length; i++) {
        if (NO_CACHE_PATTERNS[i].test(url.pathname)) return;
    }

    // Large binary files (.wasm, .data): cache-first
    if (/\.(wasm|data)$/.test(url.pathname)) {
        event.respondWith(cacheFirst(event.request));
        return;
    }

    // Game assets: cache-first after first fetch
    if (url.pathname.indexOf('/assets/') >= 0) {
        event.respondWith(cacheFirst(event.request));
        return;
    }

    // Shell files: stale-while-revalidate
    event.respondWith(staleWhileRevalidate(event.request));
});

// ---------------------------------------------------------------------------
// Strategies
// ---------------------------------------------------------------------------

function cacheFirst(request) {
    return caches.open(CACHE_VERSION).then(function (cache) {
        return cache.match(request).then(function (cached) {
            if (cached) return cached;

            return fetch(request).then(function (response) {
                if (response.ok) {
                    cache.put(request, response.clone());
                }
                return response;
            });
        });
    });
}

function staleWhileRevalidate(request) {
    return caches.open(CACHE_VERSION).then(function (cache) {
        return cache.match(request).then(function (cached) {
            var networkFetch = fetch(request).then(function (response) {
                if (response.ok) {
                    cache.put(request, response.clone());
                }
                return response;
            }).catch(function () {
                // Network failed — return cached if available
                return cached;
            });

            // Return cached immediately, update in background
            return cached || networkFetch;
        });
    });
}

// ---------------------------------------------------------------------------
// Message handling (for manual cache control)
// ---------------------------------------------------------------------------
self.addEventListener('message', function (event) {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }

    if (event.data === 'clearCache') {
        caches.delete(CACHE_VERSION).then(function () {
            console.log('[sw] Cache cleared');
        });
    }
});
