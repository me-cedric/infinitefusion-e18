#!/usr/bin/env bash
# =============================================================================
# Pokemon Infinite Fusion - Web Build Orchestrator
# Compiles mkxp-z + CRuby → WASM, packages assets, assembles dist/
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-/build}"
DIST_DIR="${SCRIPT_DIR}/dist"
GAME_DIR="${GAME_DIR:-$PROJECT_ROOT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${CYAN}[build]${NC} $*"; }
ok()   { echo -e "${GREEN}[  ok ]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn ]${NC} $*"; }
err()  { echo -e "${RED}[error]${NC} $*" >&2; }

# ---------------------------------------------------------------------------
# Step 0: Validate environment
# ---------------------------------------------------------------------------
step_validate() {
    log "Validating build environment..."

    local missing=0
    for cmd in emcc emcmake emmake python3 pngquant ffmpeg; do
        if ! command -v "$cmd" &>/dev/null; then
            err "Missing required tool: $cmd"
            missing=1
        fi
    done

    if [ ! -d "$GAME_DIR/Data" ]; then
        err "Game directory not found at $GAME_DIR (expected Data/ subdirectory)"
        exit 1
    fi

    if [ "$missing" -eq 1 ]; then
        err "Run this inside the Docker build environment: docker build -t pif-web web/"
        exit 1
    fi

    ok "Environment validated"
}

# ---------------------------------------------------------------------------
# Step 1: Build WASM binary (if not already built in Docker layer)
# ---------------------------------------------------------------------------
step_build_wasm() {
    log "Checking WASM binary..."

    local mkxp_build="$BUILD_DIR/mkxp-z/build-web"
    # Meson output name is 'mkxp-z' (project name), we rename to 'game'
    local wasm_bin="$mkxp_build/mkxp-z.wasm"
    local js_glue="$mkxp_build/mkxp-z.js"

    if [ -f "$wasm_bin" ] && [ -f "$js_glue" ]; then
        ok "WASM binary already built (from Docker layer)"
    else
        # Check if already renamed from a previous run
        if [ -f "$mkxp_build/game.wasm" ] && [ -f "$mkxp_build/game.js" ]; then
            ok "WASM binary already built and renamed"
            return 0
        fi
        log "Building mkxp-z WASM binary..."
        cd "$mkxp_build"
        ninja -j"$(nproc)"
        ok "WASM binary built"
    fi

    # Rename to game.wasm / game.js for the web shell
    if [ -f "$wasm_bin" ]; then
        cp "$wasm_bin" "$mkxp_build/game.wasm"
        cp "$js_glue" "$mkxp_build/game.js"
        ok "Renamed to game.wasm / game.js"
    fi
}

# ---------------------------------------------------------------------------
# Step 2: Package boot-tier assets (preloaded with WASM)
# ---------------------------------------------------------------------------
step_package_boot_assets() {
    log "Packaging boot-tier assets..."

    local boot_dir="$BUILD_DIR/boot-assets"
    rm -rf "$boot_dir"
    mkdir -p "$boot_dir"

    # Data files (scripts, maps, game data) — required at boot
    cp -r "$GAME_DIR/Data"/*.rxdata "$boot_dir/" 2>/dev/null || true
    cp -r "$GAME_DIR/Data"/*.dat "$boot_dir/" 2>/dev/null || true

    # Copy Ruby scripts
    if [ -d "$GAME_DIR/Data/Scripts" ]; then
        mkdir -p "$boot_dir/Data/Scripts"
        cp -r "$GAME_DIR/Data/Scripts"/* "$boot_dir/Data/Scripts/"
    fi

    # Game.ini
    cp "$GAME_DIR/Game.ini" "$boot_dir/"

    # Core graphics needed at boot
    local gfx_dirs=(
        "Tilesets" "Autotiles" "Windowskins" "Titles"
        "Icons" "Pictures" "UI"
    )
    for dir in "${gfx_dirs[@]}"; do
        if [ -d "$GAME_DIR/Graphics/$dir" ]; then
            mkdir -p "$boot_dir/Graphics/$dir"
            cp -r "$GAME_DIR/Graphics/$dir"/* "$boot_dir/Graphics/$dir/" 2>/dev/null || true
        fi
    done

    # Fonts
    if [ -d "$GAME_DIR/Fonts" ]; then
        mkdir -p "$boot_dir/Fonts"
        cp -r "$GAME_DIR/Fonts"/* "$boot_dir/Fonts/"
    fi

    # PBS data files
    if [ -d "$GAME_DIR/PBS" ]; then
        mkdir -p "$boot_dir/PBS"
        cp -r "$GAME_DIR/PBS"/* "$boot_dir/PBS/"
    fi

    # JSON data files
    for json_dir in outfits pokedex sprites; do
        if [ -d "$GAME_DIR/Data/$json_dir" ]; then
            mkdir -p "$boot_dir/Data/$json_dir"
            cp -r "$GAME_DIR/Data/$json_dir"/* "$boot_dir/Data/$json_dir/" 2>/dev/null || true
        fi
    done

    # Web overrides (injected before game scripts)
    if [ -f "$SCRIPT_DIR/scripts/web_overrides.rb" ]; then
        mkdir -p "$boot_dir/Data/Scripts/000_Web"
        cp "$SCRIPT_DIR/scripts/web_overrides.rb" "$boot_dir/Data/Scripts/000_Web/000_WebOverrides.rb"
    fi

    # Generate Emscripten preload data file
    python3 "$EMSDK/upstream/emscripten/tools/file_packager.py" \
        "$BUILD_DIR/game.data" \
        --preload "$boot_dir@/game" \
        --js-output="$BUILD_DIR/game-data.js" \
        --use-preload-cache \
        --no-node \
        2>/dev/null

    local boot_size
    boot_size=$(du -sh "$BUILD_DIR/game.data" 2>/dev/null | cut -f1)
    ok "Boot assets packaged ($boot_size)"
}

# ---------------------------------------------------------------------------
# Step 3: Process and compress lazy-load assets
# ---------------------------------------------------------------------------
step_process_lazy_assets() {
    log "Processing lazy-load assets..."

    python3 "$SCRIPT_DIR/scripts/package_assets.py" \
        --game-dir "$GAME_DIR" \
        --output-dir "$BUILD_DIR/lazy-assets" \
        --manifest-out "$BUILD_DIR/manifest.json"

    local lazy_size
    lazy_size=$(du -sh "$BUILD_DIR/lazy-assets" 2>/dev/null | cut -f1)
    ok "Lazy assets processed ($lazy_size)"
}

# ---------------------------------------------------------------------------
# Step 4: Assemble dist/
# ---------------------------------------------------------------------------
step_assemble_dist() {
    log "Assembling dist/ directory..."

    rm -rf "$DIST_DIR"
    mkdir -p "$DIST_DIR/assets"

    # WASM binary and glue
    cp "$BUILD_DIR/mkxp-z/build-web/game.wasm" "$DIST_DIR/"
    cp "$BUILD_DIR/mkxp-z/build-web/game.js" "$DIST_DIR/"

    # Boot asset data bundle
    cp "$BUILD_DIR/game.data" "$DIST_DIR/"
    cp "$BUILD_DIR/game-data.js" "$DIST_DIR/"

    # HTML shell
    cp "$SCRIPT_DIR/shell/index.html" "$DIST_DIR/"
    cp "$SCRIPT_DIR/shell/shell.css" "$DIST_DIR/"
    cp "$SCRIPT_DIR/shell/shell.js" "$DIST_DIR/"
    cp "$SCRIPT_DIR/shell/sw.js" "$DIST_DIR/"

    # Lazy-load assets
    if [ -d "$BUILD_DIR/lazy-assets" ]; then
        cp -r "$BUILD_DIR/lazy-assets"/* "$DIST_DIR/assets/"
    fi

    # Asset manifest
    cp "$BUILD_DIR/manifest.json" "$DIST_DIR/"

    local dist_size
    dist_size=$(du -sh "$DIST_DIR" 2>/dev/null | cut -f1)
    ok "Distribution assembled at $DIST_DIR ($dist_size)"
}

# ---------------------------------------------------------------------------
# Step 5: Report
# ---------------------------------------------------------------------------
step_report() {
    echo ""
    log "========================================"
    log " Build Complete"
    log "========================================"
    echo ""
    echo "  Output:  $DIST_DIR/"
    echo ""
    echo "  Files:"
    ls -lh "$DIST_DIR"/*.wasm "$DIST_DIR"/*.js "$DIST_DIR"/*.html "$DIST_DIR"/*.data 2>/dev/null | \
        awk '{printf "    %-30s %s\n", $NF, $5}'
    echo ""
    echo "  Assets:  $(find "$DIST_DIR/assets" -type f 2>/dev/null | wc -l | tr -d ' ') files"
    echo ""
    echo "  To test locally:"
    echo "    cd $DIST_DIR"
    echo "    python3 -m http.server 8080"
    echo "    open http://localhost:8080"
    echo ""
    echo "  Required HTTP headers for SharedArrayBuffer:"
    echo "    Cross-Origin-Opener-Policy: same-origin"
    echo "    Cross-Origin-Embedder-Policy: require-corp"
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    log "Pokemon Infinite Fusion - Web Build"
    log "Game directory: $GAME_DIR"
    echo ""

    step_validate
    step_build_wasm
    step_package_boot_assets
    step_process_lazy_assets
    step_assemble_dist
    step_report
}

main "$@"
