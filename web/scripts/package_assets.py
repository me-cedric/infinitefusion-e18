#!/usr/bin/env python3
# =============================================================================
# Pokemon Infinite Fusion — Web Asset Pipeline
#
# Processes game assets for efficient web delivery:
#   1. Compresses PNGs with pngquant (lossy, ~70% size reduction)
#   2. Converts audio to Opus/OGG (smaller than WAV/MP3)
#   3. Generates an asset manifest mapping game paths → CDN paths
#   4. Splits assets into tiers: boot (preloaded) vs lazy (on-demand)
#
# Usage:
#   python3 package_assets.py \
#       --game-dir /path/to/infinitefusion-e18 \
#       --output-dir /build/lazy-assets \
#       --manifest-out /build/manifest.json
# =============================================================================

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directories that are preloaded at boot (NOT processed here)
BOOT_TIER_DIRS = {
    "Graphics/Tilesets",
    "Graphics/Autotiles",
    "Graphics/Windowskins",
    "Graphics/Titles",
    "Graphics/Icons",
    "Graphics/Pictures",
}

# Lazy-load directories processed by this script
LAZY_GRAPHICS_DIRS = [
    "Graphics/Battlers",
    "Graphics/Characters",
    "Graphics/Animations",
    "Graphics/Battle animations",
    "Graphics/Battlebacks",
    "Graphics/Fogs",
    "Graphics/Panoramas",
    "Graphics/Pokemon",
    "Graphics/Trainers",
    "Graphics/Transitions",
    "Graphics/Weather",
    "Graphics/Items",
]

LAZY_AUDIO_DIRS = [
    "Audio/BGM",
    "Audio/BGS",
    "Audio/ME",
    "Audio/SE",
]

# pngquant quality range (min-max)
PNG_QUALITY = "45-80"
PNG_SPEED = "3"

# Audio conversion settings
AUDIO_BITRATE = "96k"
AUDIO_FORMAT = "ogg"  # Opus in OGG container — wide browser support

# Max parallel workers
MAX_WORKERS = os.cpu_count() or 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def content_hash(filepath: Path, length: int = 8) -> str:
    """Generate a short content hash for cache-busting."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:length]


def has_tool(name: str) -> bool:
    """Check if a CLI tool is available."""
    return shutil.which(name) is not None


def ensure_parent(path: Path):
    """Create parent directories if they don't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Image processing
# ---------------------------------------------------------------------------

def compress_png(src: Path, dst: Path) -> bool:
    """Compress a PNG with pngquant. Falls back to copy if pngquant unavailable."""
    ensure_parent(dst)

    if has_tool("pngquant"):
        try:
            subprocess.run(
                [
                    "pngquant",
                    "--quality", PNG_QUALITY,
                    "--speed", PNG_SPEED,
                    "--force",
                    "--output", str(dst),
                    "--strip",
                    str(src),
                ],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            # pngquant can fail on already-optimized or paletted PNGs
            pass

    # Fallback: straight copy
    shutil.copy2(src, dst)
    return False


def copy_image(src: Path, dst: Path):
    """Copy non-PNG images (BMP, JPG) directly."""
    ensure_parent(dst)
    shutil.copy2(src, dst)


# ---------------------------------------------------------------------------
# Audio processing
# ---------------------------------------------------------------------------

def convert_audio(src: Path, dst: Path) -> bool:
    """Convert audio to OGG/Opus via ffmpeg. Falls back to copy."""
    dst = dst.with_suffix(f".{AUDIO_FORMAT}")
    ensure_parent(dst)

    if has_tool("ffmpeg"):
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",                    # overwrite
                    "-i", str(src),
                    "-c:a", "libvorbis",     # vorbis in ogg — widest support
                    "-b:a", AUDIO_BITRATE,
                    "-map_metadata", "-1",   # strip metadata
                    str(dst),
                ],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            pass

    # Fallback: copy original
    dst_fallback = dst.with_suffix(src.suffix)
    shutil.copy2(src, dst_fallback)
    return False


# ---------------------------------------------------------------------------
# Asset processing dispatch
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".png", ".bmp", ".jpg", ".jpeg"}
AUDIO_EXTENSIONS = {".ogg", ".mp3", ".wav", ".mid", ".midi", ".wma", ".flac"}


def process_file(src: Path, game_dir: Path, output_dir: Path) -> Optional[dict]:
    """Process a single asset file. Returns manifest entry or None."""
    rel = src.relative_to(game_dir)
    dst = output_dir / rel
    ext = src.suffix.lower()

    if ext == ".png":
        compress_png(src, dst)
    elif ext in IMAGE_EXTENSIONS:
        copy_image(src, dst)
    elif ext in AUDIO_EXTENSIONS:
        converted_dst = dst.with_suffix(f".{AUDIO_FORMAT}")
        success = convert_audio(src, converted_dst)
        if success:
            dst = converted_dst
        else:
            dst = dst.with_suffix(src.suffix)
    else:
        # Unknown file type — copy as-is
        ensure_parent(dst)
        shutil.copy2(src, dst)

    if not dst.exists():
        return None

    # Build manifest entry
    final_rel = dst.relative_to(output_dir)
    chash = content_hash(dst)
    size = dst.stat().st_size

    return {
        "game_path": str(rel),
        "cdn_path": f"assets/{final_rel}",
        "hash": chash,
        "size": size,
    }


# ---------------------------------------------------------------------------
# Directory scanner
# ---------------------------------------------------------------------------

def scan_lazy_assets(game_dir: Path) -> List[Path]:
    """Find all files in lazy-load directories."""
    files = []

    all_lazy_dirs = LAZY_GRAPHICS_DIRS + LAZY_AUDIO_DIRS
    for subdir in all_lazy_dirs:
        full = game_dir / subdir
        if not full.is_dir():
            continue
        for root, _dirs, filenames in os.walk(full):
            for fname in filenames:
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()
                # Include images, audio, and data files alongside assets
                if ext in IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | {".json", ".txt", ".csv"}:
                    files.append(fpath)

    return files


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Package Pokemon Infinite Fusion assets for web delivery"
    )
    parser.add_argument(
        "--game-dir",
        required=True,
        type=Path,
        help="Root game directory (contains Data/, Graphics/, Audio/)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Output directory for processed lazy-load assets",
    )
    parser.add_argument(
        "--manifest-out",
        required=True,
        type=Path,
        help="Path to write the asset manifest JSON",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Parallel workers (default: {MAX_WORKERS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List assets without processing",
    )
    args = parser.parse_args()

    game_dir = args.game_dir.resolve()
    output_dir = args.output_dir.resolve()
    manifest_path = args.manifest_out.resolve()

    if not game_dir.is_dir():
        print(f"Error: game directory not found: {game_dir}", file=sys.stderr)
        sys.exit(1)

    # Scan for assets
    files = scan_lazy_assets(game_dir)
    print(f"[assets] Found {len(files)} lazy-load assets to process")

    if args.dry_run:
        for f in sorted(files):
            print(f"  {f.relative_to(game_dir)}")
        return

    # Clean and create output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Process files in parallel
    manifest_entries = []
    errors = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_file, f, game_dir, output_dir): f
            for f in files
        }

        done = 0
        total = len(futures)
        for future in as_completed(futures):
            done += 1
            src = futures[future]
            try:
                entry = future.result()
                if entry:
                    manifest_entries.append(entry)
            except Exception as e:
                print(f"  [error] {src.relative_to(game_dir)}: {e}", file=sys.stderr)
                errors += 1

            if done % 100 == 0 or done == total:
                print(f"  [{done}/{total}] processed")

    # Sort manifest for deterministic output
    manifest_entries.sort(key=lambda e: e["game_path"])

    # Build manifest
    manifest = {
        "version": 1,
        "generated": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "total_files": len(manifest_entries),
        "total_size": sum(e["size"] for e in manifest_entries),
        "assets": {e["game_path"]: e for e in manifest_entries},
    }

    # Write manifest
    ensure_parent(manifest_path)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Summary
    total_size_mb = manifest["total_size"] / (1024 * 1024)
    print(f"[assets] Complete: {len(manifest_entries)} assets, {total_size_mb:.1f} MB")
    print(f"[assets] Manifest written to {manifest_path}")
    if errors:
        print(f"[assets] {errors} errors encountered", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

