// ==========================================================================
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
