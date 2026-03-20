#!/usr/bin/env python3
"""Generate all remaining web shell files for the PIF web build."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
# scripts/ is inside web/, and web/ is inside the project root
PROJECT = os.path.dirname(os.path.dirname(BASE))

def write(path, content):
    full = os.path.join(PROJECT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"  wrote {path} ({len(content)} bytes)")

# ==========================================================================
# 1. shell/index.html
# ==========================================================================
write("web/shell/index.html", r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
    <meta name="description" content="Pokemon Infinite Fusion - Play in your browser">
    <meta name="theme-color" content="#1a1a2e">
    <meta http-equiv="Cross-Origin-Opener-Policy" content="same-origin">
    <meta http-equiv="Cross-Origin-Embedder-Policy" content="require-corp">
    <title>Pokemon Infinite Fusion</title>
    <link rel="stylesheet" href="shell.css">
    <link rel="preload" href="game.wasm" as="fetch" crossorigin>
    <link rel="preload" href="game.js" as="script">
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-overlay">
        <div id="loading-container">
            <h1 id="loading-title">Pokemon Infinite Fusion</h1>
            <div id="loading-subtitle">Web Edition</div>
            <div id="progress-container">
                <div id="progress-bar"><div id="progress-fill"></div></div>
                <div id="progress-text">Initializing...</div>
            </div>
            <div id="loading-details"></div>
            <div id="error-container" style="display:none">
                <div id="error-icon">&#x26A0;&#xFE0F;</div>
                <div id="error-title">Something went wrong</div>
                <div id="error-message"></div>
                <button id="error-retry" onclick="location.reload()">Retry</button>
            </div>
        </div>
        <div id="compat-warning" style="display:none">
            <p><strong>Browser not supported.</strong></p>
            <p>Requires WebAssembly and WebGL.<br>Use Chrome 90+, Firefox 90+, Safari 16+, or Edge 90+.</p>
        </div>
    </div>

    <!-- Game Canvas -->
    <div id="game-container">
        <canvas id="canvas" oncontextmenu="event.preventDefault()" tabindex="-1"></canvas>
    </div>

    <!-- Mobile Touch Controls -->
    <div id="controls-overlay" style="display:none">
        <div id="dpad">
            <button class="dpad-btn dpad-up" data-key="ArrowUp">&#9650;</button>
            <button class="dpad-btn dpad-left" data-key="ArrowLeft">&#9664;</button>
            <button class="dpad-btn dpad-right" data-key="ArrowRight">&#9654;</button>
            <button class="dpad-btn dpad-down" data-key="ArrowDown">&#9660;</button>
        </div>
        <div id="action-buttons">
            <button class="action-btn" data-key="z" id="btn-a">A</button>
            <button class="action-btn" data-key="x" id="btn-b">B</button>
            <button class="action-btn action-btn-small" data-key="Enter" id="btn-start">Start</button>
        </div>
    </div>

    <!-- Toolbar -->
    <div id="toolbar">
        <button id="btn-fullscreen" title="Toggle fullscreen">&#x26F6;</button>
        <button id="btn-mute" title="Toggle audio">&#x1F50A;</button>
        <button id="btn-save-reminder" title="Saves stored in browser">&#x1F4BE;</button>
    </div>

    <script src="game-data.js"></script>
    <script src="game.js"></script>
    <script src="shell.js"></script>
</body>
</html>
""")

# ==========================================================================
# 2. shell/shell.css
# ==========================================================================
write("web/shell/shell.css", r"""/* ==========================================================================
   Pokemon Infinite Fusion — Web Shell Styles
   ========================================================================== */

:root {
    --bg-dark: #1a1a2e;
    --bg-darker: #16213e;
    --accent: #e94560;
    --accent-glow: #ff6b81;
    --text-primary: #eee;
    --text-secondary: #aaa;
    --progress-bg: #2a2a4a;
    --progress-fill: linear-gradient(90deg, #e94560, #ff6b81);
    --toolbar-bg: rgba(0, 0, 0, 0.6);
    --canvas-bg: #000;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: var(--canvas-bg);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--text-primary);
    touch-action: none;
    -webkit-tap-highlight-color: transparent;
}

/* ==========================================================================
   Loading Overlay
   ========================================================================== */

#loading-overlay {
    position: fixed;
    inset: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-dark);
    transition: opacity 0.6s ease, visibility 0.6s ease;
}

#loading-overlay.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
}

#loading-container {
    text-align: center;
    max-width: 480px;
    padding: 2rem;
}

#loading-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    background: linear-gradient(135deg, #e94560, #ff6b81, #ffd93d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

#loading-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* Progress bar */
#progress-container {
    margin: 1.5rem 0;
}

#progress-bar {
    width: 100%;
    height: 8px;
    background: var(--progress-bg);
    border-radius: 4px;
    overflow: hidden;
}

#progress-fill {
    width: 0%;
    height: 100%;
    background: var(--progress-fill);
    border-radius: 4px;
    transition: width 0.3s ease;
}

#progress-text {
    margin-top: 0.75rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

#loading-details {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: var(--text-secondary);
    opacity: 0.6;
    min-height: 1.2em;
}

/* Error display */
#error-container {
    margin-top: 2rem;
    padding: 1.5rem;
    background: rgba(233, 69, 96, 0.1);
    border: 1px solid rgba(233, 69, 96, 0.3);
    border-radius: 8px;
}

#error-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

#error-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--accent);
}

#error-message {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
    word-break: break-word;
}

#error-retry {
    padding: 0.6rem 1.5rem;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background 0.2s;
}

#error-retry:hover {
    background: var(--accent-glow);
}

/* Compatibility warning */
#compat-warning {
    position: absolute;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    font-size: 0.85rem;
    color: var(--text-secondary);
    max-width: 400px;
}

/* ==========================================================================
   Game Canvas
   ========================================================================== */

#game-container {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--canvas-bg);
}

#canvas {
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    outline: none;
    max-width: 100%;
    max-height: 100%;
}

/* ==========================================================================
   Toolbar
   ========================================================================== */

#toolbar {
    position: fixed;
    top: 0.5rem;
    right: 0.5rem;
    z-index: 50;
    display: flex;
    gap: 0.4rem;
    opacity: 0;
    transition: opacity 0.3s;
}

#game-container:hover ~ #toolbar,
#toolbar:hover {
    opacity: 1;
}

#toolbar button {
    width: 36px;
    height: 36px;
    background: var(--toolbar-bg);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    color: var(--text-primary);
    font-size: 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s, border-color 0.2s;
}

#toolbar button:hover {
    background: rgba(0, 0, 0, 0.8);
    border-color: rgba(255, 255, 255, 0.3);
}

/* ==========================================================================
   Mobile Touch Controls
   ========================================================================== */

#controls-overlay {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 40;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    pointer-events: none;
}

#controls-overlay > * {
    pointer-events: auto;
}

/* D-Pad */
#dpad {
    position: relative;
    width: 130px;
    height: 130px;
}

.dpad-btn {
    position: absolute;
    width: 44px;
    height: 44px;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    -webkit-user-select: none;
    user-select: none;
}

.dpad-btn:active {
    background: rgba(255, 255, 255, 0.3);
}

.dpad-up    { top: 0;   left: 50%; transform: translateX(-50%); }
.dpad-down  { bottom: 0; left: 50%; transform: translateX(-50%); }
.dpad-left  { left: 0;  top: 50%;  transform: translateY(-50%); }
.dpad-right { right: 0; top: 50%;  transform: translateY(-50%); }

/* Action buttons */
#action-buttons {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
}

.action-btn {
    width: 56px;
    height: 56px;
    background: rgba(233, 69, 96, 0.25);
    border: 2px solid rgba(233, 69, 96, 0.5);
    border-radius: 50%;
    color: #fff;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    -webkit-user-select: none;
    user-select: none;
}

.action-btn:active {
    background: rgba(233, 69, 96, 0.5);
}

.action-btn-small {
    width: 44px;
    height: 44px;
    font-size: 0.7rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* ==========================================================================
   Responsive
   ========================================================================== */

@media (max-width: 600px) {
    #loading-title { font-size: 1.5rem; }
    #loading-container { padding: 1rem; }
}

@media (min-width: 800px) {
    /* Hide touch controls on desktop */
    #controls-overlay { display: none !important; }
}

/* ==========================================================================
   Fullscreen
   ========================================================================== */

:fullscreen #toolbar { opacity: 1; }
:-webkit-full-screen #toolbar { opacity: 1; }
""")

# ==========================================================================
# 3. shell/shell.js — Boot loader
# ==========================================================================
write("web/shell/shell.js", r"""// ==========================================================================
// Pokemon Infinite Fusion — Web Boot Loader (shell.js)
//
// Responsibilities:
//   1. Check browser compatibility (WASM, WebGL)
//   2. Set up Emscripten filesystem mounts (MEMFS, IDBFS)
//   3. Initialize WASM module with progress reporting
//   4. Handle loading overlay transitions
//   5. Set up mobile touch controls
//   6. Register service worker
// ==========================================================================

(function () {
    'use strict';

    // -----------------------------------------------------------------------
    // DOM refs
    // -----------------------------------------------------------------------
    const overlay       = document.getElementById('loading-overlay');
    const progressFill  = document.getElementById('progress-fill');
    const progressText  = document.getElementById('progress-text');
    const loadingDetail = document.getElementById('loading-details');
    const errorContainer = document.getElementById('error-container');
    const errorMessage  = document.getElementById('error-message');
    const compatWarning = document.getElementById('compat-warning');
    const canvas        = document.getElementById('canvas');

    // -----------------------------------------------------------------------
    // Progress helpers
    // -----------------------------------------------------------------------
    function setProgress(pct, msg, detail) {
        if (progressFill) progressFill.style.width = Math.min(pct, 100) + '%';
        if (progressText && msg) progressText.textContent = msg;
        if (loadingDetail && detail !== undefined) loadingDetail.textContent = detail;
    }

    function showError(msg) {
        if (progressFill) progressFill.parentElement.style.display = 'none';
        if (progressText) progressText.style.display = 'none';
        if (errorContainer) {
            errorContainer.style.display = 'block';
            errorMessage.textContent = msg;
        }
        console.error('[shell] Fatal:', msg);
    }

    function hideOverlay() {
        if (overlay) {
            overlay.classList.add('hidden');
            // Remove from DOM after transition
            setTimeout(function () {
                overlay.style.display = 'none';
            }, 700);
        }
        // Focus canvas for keyboard input
        if (canvas) canvas.focus();
    }

    // -----------------------------------------------------------------------
    // Compatibility check
    // -----------------------------------------------------------------------
    function checkCompat() {
        var issues = [];
        if (typeof WebAssembly === 'undefined') issues.push('WebAssembly');
        try {
            var c = document.createElement('canvas');
            var gl = c.getContext('webgl2') || c.getContext('webgl') || c.getContext('experimental-webgl');
            if (!gl) issues.push('WebGL');
        } catch (e) {
            issues.push('WebGL');
        }
        if (typeof fetch === 'undefined') issues.push('Fetch API');
        if (typeof indexedDB === 'undefined') issues.push('IndexedDB');

        if (issues.length > 0) {
            if (compatWarning) compatWarning.style.display = 'block';
            showError('Missing browser features: ' + issues.join(', '));
            return false;
        }
        return true;
    }

    // -----------------------------------------------------------------------
    // IDBFS sync helper
    // -----------------------------------------------------------------------
    function syncIDBFS(Module, populate, callback) {
        Module.FS.syncfs(populate, function (err) {
            if (err) console.warn('[shell] IDBFS sync error:', err);
            if (callback) callback(err);
        });
    }

    // -----------------------------------------------------------------------
    // Module configuration
    // -----------------------------------------------------------------------
    function createModuleConfig() {
        return {
            canvas: canvas,

            // Emscripten progress callbacks
            setStatus: function (text) {
                if (!text) return;
                // Parse "Downloading data... (X/Y)" format
                var m = text.match(/([^(]+)\((\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)\)/);
                if (m) {
                    var pct = (parseFloat(m[2]) / parseFloat(m[3])) * 100;
                    setProgress(pct, m[1].trim(), Math.round(pct) + '%');
                } else {
                    setProgress(0, text, '');
                }
            },

            // Called before main()
            preRun: [function (Module) {
                setProgress(40, 'Mounting filesystems...', '');

                // Create mount points
                Module.FS.mkdir('/saves');
                Module.FS.mkdir('/cache');

                // Mount IDBFS for persistent saves
                Module.FS.mount(Module.FS.filesystems.IDBFS, {}, '/saves');
                Module.FS.mount(Module.FS.filesystems.IDBFS, {}, '/cache');

                // Sync from IndexedDB → MEMFS (populate=true reads stored data)
                Module.addRunDependency('idbfs-sync');
                syncIDBFS(Module, true, function () {
                    console.log('[shell] IDBFS synced from IndexedDB');
                    Module.removeRunDependency('idbfs-sync');
                });
            }],

            // Called when main() starts
            onRuntimeInitialized: function () {
                setProgress(90, 'Starting game engine...', '');
                console.log('[shell] WASM runtime initialized');
            },

            // Called when the game starts rendering
            postRun: [function () {
                setProgress(100, 'Ready!', '');
                setTimeout(hideOverlay, 300);

                // Periodic IDBFS sync (every 30s) to persist saves
                setInterval(function () {
                    syncIDBFS(window.Module, false);
                }, 30000);
            }],

            // Error handler
            onAbort: function (reason) {
                showError('Game engine aborted: ' + (reason || 'unknown error'));
            },

            // Print/printErr for console
            print: function (text) {
                console.log('[game]', text);
            },
            printErr: function (text) {
                // Filter noisy Emscripten warnings
                if (text.indexOf('warning: unsupported syscall') >= 0) return;
                console.warn('[game]', text);
            },

            // Prevent Emscripten from catching all errors
            ENVIRONMENT_IS_WEB: true,
        };
    }

    // -----------------------------------------------------------------------
    // Mobile touch controls
    // -----------------------------------------------------------------------
    function setupTouchControls() {
        // Only show on touch devices
        var isTouchDevice = ('ontouchstart' in window) ||
                            (navigator.maxTouchPoints > 0);
        if (!isTouchDevice) return;

        var controlsOverlay = document.getElementById('controls-overlay');
        if (controlsOverlay) controlsOverlay.style.display = 'flex';

        // Simulate keyboard events from touch buttons
        var allBtns = document.querySelectorAll('.dpad-btn, .action-btn');
        allBtns.forEach(function (btn) {
            var keyName = btn.getAttribute('data-key');
            if (!keyName) return;

            function dispatch(type) {
                var ev = new KeyboardEvent(type, {
                    key: keyName,
                    code: keyName,
                    bubbles: true,
                    cancelable: true,
                });
                canvas.dispatchEvent(ev);
            }

            btn.addEventListener('touchstart', function (e) {
                e.preventDefault();
                dispatch('keydown');
            }, { passive: false });

            btn.addEventListener('touchend', function (e) {
                e.preventDefault();
                dispatch('keyup');
            }, { passive: false });
        });
    }

    // -----------------------------------------------------------------------
    // Toolbar buttons
    // -----------------------------------------------------------------------
    function setupToolbar() {
        // Fullscreen
        var btnFS = document.getElementById('btn-fullscreen');
        if (btnFS) {
            btnFS.addEventListener('click', function () {
                var container = document.getElementById('game-container');
                if (!document.fullscreenElement) {
                    (container.requestFullscreen || container.webkitRequestFullscreen)
                        .call(container);
                } else {
                    (document.exitFullscreen || document.webkitExitFullscreen)
                        .call(document);
                }
            });
        }

        // Mute toggle
        var btnMute = document.getElementById('btn-mute');
        var muted = false;
        if (btnMute) {
            btnMute.addEventListener('click', function () {
                muted = !muted;
                // Emscripten SDL audio uses Web Audio API
                if (window.SDL && window.SDL.audioContext) {
                    if (muted) {
                        window.SDL.audioContext.suspend();
                    } else {
                        window.SDL.audioContext.resume();
                    }
                }
                btnMute.innerHTML = muted ? '&#x1F507;' : '&#x1F50A;';
            });
        }
    }

    // -----------------------------------------------------------------------
    // Service Worker registration
    // -----------------------------------------------------------------------
    function registerSW() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('sw.js').then(function (reg) {
                console.log('[shell] Service worker registered, scope:', reg.scope);
            }).catch(function (err) {
                console.warn('[shell] Service worker registration failed:', err);
            });
        }
    }

    // -----------------------------------------------------------------------
    // Boot sequence
    // -----------------------------------------------------------------------
    function boot() {
        console.log('[shell] Pokemon Infinite Fusion — Web Boot');
        setProgress(5, 'Checking browser...', '');

        if (!checkCompat()) return;

        setProgress(10, 'Loading game data...', '');

        // Register service worker early
        registerSW();

        // Set up UI
        setupTouchControls();
        setupToolbar();

        // Create Emscripten module config
        var moduleConfig = createModuleConfig();

        // createMkxpModule is defined in game.js (Emscripten MODULARIZE output)
        if (typeof createMkxpModule === 'function') {
            setProgress(20, 'Initializing WebAssembly...', '');
            createMkxpModule(moduleConfig).then(function (mod) {
                window.Module = mod;
                console.log('[shell] WASM module created');
            }).catch(function (err) {
                showError('Failed to initialize game engine: ' + err.message);
            });
        } else {
            // Fallback: non-modularized Emscripten output
            window.Module = moduleConfig;
        }
    }

    // Start boot when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

})();
""")

# ==========================================================================
# 4. shell/sw.js — Service Worker for offline caching
# ==========================================================================
write("web/shell/sw.js", r"""// ==========================================================================
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
""")

# ==========================================================================
# 5. ci/web-build.yml — GitHub Actions CI workflow
# ==========================================================================
write("web/ci/web-build.yml", r"""# ==========================================================================
# Pokemon Infinite Fusion — Web Build CI
# GitHub Actions workflow
#
# Triggers:
#   - Push to develop/main branches (web/ directory changes)
#   - Manual dispatch
#
# Steps:
#   1. Build Docker image with mkxp-z + CRuby compiled to WASM
#   2. Run asset pipeline
#   3. Assemble dist/
#   4. Upload artifacts / deploy to Pages
# ==========================================================================

name: Web Build

on:
  push:
    branches: [develop, main]
    paths:
      - 'web/**'
      - 'Data/**'
      - 'Graphics/**'
      - 'Audio/**'
  workflow_dispatch:
    inputs:
      deploy:
        description: 'Deploy to GitHub Pages'
        required: false
        default: 'false'
        type: boolean

concurrency:
  group: web-build-${{ github.ref }}
  cancel-in-progress: true

env:
  DOCKER_IMAGE: pif-web-builder
  DIST_ARTIFACT: pif-web-dist

jobs:
  # -----------------------------------------------------------------------
  # Build WASM + Assets
  # -----------------------------------------------------------------------
  build:
    name: Build Web Distribution
    runs-on: ubuntu-latest
    timeout-minutes: 120

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          lfs: true

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Cache Docker layers
        uses: actions/cache@v4
        with:
          path: /tmp/.buildx-cache
          key: ${{ runner.os }}-buildx-${{ hashFiles('web/Dockerfile') }}
          restore-keys: |
            ${{ runner.os }}-buildx-

      - name: Build Docker image
        run: |
          docker buildx build \
            --cache-from type=local,src=/tmp/.buildx-cache \
            --cache-to type=local,dest=/tmp/.buildx-cache-new,mode=max \
            --load \
            -t ${{ env.DOCKER_IMAGE }} \
            web/

      - name: Run build pipeline
        run: |
          docker run --rm \
            -v "${{ github.workspace }}:/game:ro" \
            -v "${{ github.workspace }}/web/dist:/build/web/dist" \
            -e GAME_DIR=/game \
            ${{ env.DOCKER_IMAGE }}

      - name: Move Docker cache
        run: |
          rm -rf /tmp/.buildx-cache
          mv /tmp/.buildx-cache-new /tmp/.buildx-cache

      - name: List dist contents
        run: |
          echo "=== dist/ contents ==="
          ls -lhR web/dist/
          echo ""
          echo "=== Size summary ==="
          du -sh web/dist/
          du -sh web/dist/assets/ 2>/dev/null || true

      - name: Upload dist artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ env.DIST_ARTIFACT }}
          path: web/dist/
          retention-days: 14

  # -----------------------------------------------------------------------
  # Deploy to GitHub Pages (optional)
  # -----------------------------------------------------------------------
  deploy:
    name: Deploy to GitHub Pages
    needs: build
    runs-on: ubuntu-latest
    if: >-
      github.ref == 'refs/heads/main' ||
      (github.event_name == 'workflow_dispatch' && github.event.inputs.deploy == 'true')

    permissions:
      pages: write
      id-token: write

    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}

    steps:
      - name: Download dist artifact
        uses: actions/download-artifact@v4
        with:
          name: ${{ env.DIST_ARTIFACT }}
          path: dist/

      - name: Configure Pages
        uses: actions/configure-pages@v4

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist/

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

  # -----------------------------------------------------------------------
  # Validate build (smoke test)
  # -----------------------------------------------------------------------
  validate:
    name: Validate Build Output
    needs: build
    runs-on: ubuntu-latest

    steps:
      - name: Download dist artifact
        uses: actions/download-artifact@v4
        with:
          name: ${{ env.DIST_ARTIFACT }}
          path: dist/

      - name: Validate required files
        run: |
          echo "Checking required files..."
          required_files=(
            "dist/index.html"
            "dist/shell.css"
            "dist/shell.js"
            "dist/sw.js"
            "dist/game.js"
            "dist/game.wasm"
            "dist/game.data"
            "dist/game-data.js"
            "dist/manifest.json"
          )
          all_ok=true
          for f in "${required_files[@]}"; do
            if [ -f "$f" ]; then
              size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f")
              echo "  OK: $f ($size bytes)"
            else
              echo "  MISSING: $f"
              all_ok=false
            fi
          done
          if [ "$all_ok" != "true" ]; then
            echo "ERROR: Missing required files"
            exit 1
          fi

      - name: Validate HTML structure
        run: |
          # Basic check that index.html references required scripts
          grep -q 'game.js' dist/index.html && echo "OK: game.js referenced"
          grep -q 'shell.js' dist/index.html && echo "OK: shell.js referenced"
          grep -q 'canvas' dist/index.html && echo "OK: canvas element found"

      - name: Validate manifest
        run: |
          python3 -c "
          import json, sys
          with open('dist/manifest.json') as f:
              m = json.load(f)
          print(f'Manifest version: {m.get(\"version\", \"?\")}')
          print(f'Total assets: {m.get(\"total_files\", 0)}')
          size_mb = m.get('total_size', 0) / (1024*1024)
          print(f'Total size: {size_mb:.1f} MB')
          if m.get('total_files', 0) == 0:
              print('WARNING: No assets in manifest')
              sys.exit(1)
          "
""")

print("\nAll files generated successfully!")


