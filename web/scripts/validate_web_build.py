#!/usr/bin/env python3
"""Validate all web shell files locally."""
import html.parser
import json
import os
import re
import sys

# Script is at web/scripts/validate_web_build.py
# Go up: scripts/ -> web/ -> project root
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # web/scripts/
_WEB_DIR = os.path.dirname(_SCRIPT_DIR)                    # web/
BASE = os.path.dirname(_WEB_DIR)                           # project root
SHELL = os.path.join(_WEB_DIR, "shell")
SCRIPTS = os.path.join(_WEB_DIR, "scripts")
CI = os.path.join(_WEB_DIR, "ci")

errors = 0

def ok(msg):
    print(f"  \033[32m✓\033[0m {msg}")

def fail(msg):
    global errors
    errors += 1
    print(f"  \033[31m✗\033[0m {msg}")

def section(title):
    print(f"\n\033[1;36m{'='*60}\033[0m")
    print(f"\033[1;36m  {title}\033[0m")
    print(f"\033[1;36m{'='*60}\033[0m")


# =========================================================================
# 1. Check all expected files exist
# =========================================================================
section("File existence check")

expected_files = [
    "web/Dockerfile",
    "web/build.sh",
    "web/CMakeLists.web.cmake",
    "web/patches/mkxp-z-emscripten.patch",
    "web/scripts/web_overrides.rb",
    "web/scripts/package_assets.py",
    "web/shell/index.html",
    "web/shell/shell.css",
    "web/shell/shell.js",
    "web/shell/sw.js",
    "web/ci/web-build.yml",
    ".github/workflows/web-build.yml",
]

for relpath in expected_files:
    full = os.path.join(BASE, relpath)
    if os.path.isfile(full):
        size = os.path.getsize(full)
        if size > 0:
            ok(f"{relpath} ({size} bytes)")
        else:
            fail(f"{relpath} EXISTS BUT EMPTY")
    else:
        fail(f"{relpath} MISSING")


# =========================================================================
# 2. Validate HTML
# =========================================================================
section("HTML validation: index.html")

class HTMLValidator(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.validation_errors = []

    def handle_starttag(self, tag, attrs):
        void_tags = {
            "area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr"
        }
        if tag not in void_tags:
            self.tags.append(tag)

    def handle_endtag(self, tag):
        if self.tags and self.tags[-1] == tag:
            self.tags.pop()
        elif tag in self.tags:
            self.validation_errors.append(f"Mismatched closing tag: </{tag}>")

html_path = os.path.join(SHELL, "index.html")
with open(html_path) as f:
    html_content = f.read()

v = HTMLValidator()
v.feed(html_content)

if v.validation_errors:
    for e in v.validation_errors:
        fail(e)
elif v.tags:
    fail(f"Unclosed tags: {v.tags}")
else:
    ok("All HTML tags balanced")

required_in_html = [
    ("canvas", "Canvas element"),
    ("loading-overlay", "Loading overlay"),
    ("progress-fill", "Progress bar"),
    ("error-container", "Error display"),
    ("controls-overlay", "Mobile controls"),
    ("game-data.js", "Game data script ref"),
    ("game.js", "WASM glue script ref"),
    ("shell.js", "Boot loader script ref"),
    ("shell.css", "Stylesheet ref"),
    ("Cross-Origin-Opener-Policy", "COOP header"),
    ("Cross-Origin-Embedder-Policy", "COEP header"),
]

for needle, desc in required_in_html:
    if needle in html_content:
        ok(f"Found: {desc}")
    else:
        fail(f"Missing: {desc}")


# =========================================================================
# 3. Validate CSS
# =========================================================================
section("CSS validation: shell.css")

css_path = os.path.join(SHELL, "shell.css")
with open(css_path) as f:
    css_content = f.read()

css_selectors = [
    "#loading-overlay", "#progress-fill", "#canvas",
    "#game-container", "#controls-overlay", "#toolbar",
    ".dpad-btn", ".action-btn", "#error-container",
]

for sel in css_selectors:
    if sel in css_content:
        ok(f"Selector found: {sel}")
    else:
        fail(f"Selector missing: {sel}")

# Check for responsive rules
if "@media" in css_content:
    ok("Responsive media queries present")
else:
    fail("No responsive media queries")


# =========================================================================
# 4. Validate shell.js
# =========================================================================
section("JavaScript validation: shell.js")

js_path = os.path.join(SHELL, "shell.js")
with open(js_path) as f:
    js_content = f.read()

js_features = [
    ("WebAssembly", "WASM compatibility check"),
    ("webgl", "WebGL compatibility check"),
    ("IDBFS", "IDBFS mount"),
    ("/saves", "Save directory mount"),
    ("/cache", "Cache directory mount"),
    ("createMkxpModule", "Emscripten module init"),
    ("serviceWorker", "Service worker registration"),
    ("sw.js", "SW file reference"),
    ("setProgress", "Progress reporting"),
    ("showError", "Error handling"),
    ("hideOverlay", "Loading overlay dismissal"),
    ("touchstart", "Touch controls"),
    ("fullscreen", "Fullscreen support"),
    ("syncfs", "IDBFS sync"),
]

for needle, desc in js_features:
    if needle.lower() in js_content.lower():
        ok(f"Feature: {desc}")
    else:
        fail(f"Missing feature: {desc}")

# Check IIFE wrapper
if "(function" in js_content and "'use strict'" in js_content:
    ok("Proper IIFE wrapper with strict mode")
else:
    fail("Missing IIFE wrapper or strict mode")


# =========================================================================
# 5. Validate service worker
# =========================================================================
section("Service Worker validation: sw.js")

sw_path = os.path.join(SHELL, "sw.js")
with open(sw_path) as f:
    sw_content = f.read()

sw_features = [
    ("install", "Install event handler"),
    ("activate", "Activate event handler"),
    ("fetch", "Fetch event handler"),
    ("caches.open", "Cache API usage"),
    ("skipWaiting", "Skip waiting"),
    ("clients.claim", "Clients claim"),
    ("game.wasm", "WASM in precache"),
    ("game.data", "Data bundle in precache"),
]

for needle, desc in sw_features:
    if needle in sw_content:
        ok(f"Feature: {desc}")
    else:
        fail(f"Missing feature: {desc}")


# =========================================================================
# 6. Validate CI workflow
# =========================================================================
section("CI Workflow validation: web-build.yml")

ci_path = os.path.join(CI, "web-build.yml")
with open(ci_path) as f:
    ci_content = f.read()

ci_features = [
    ("workflow_dispatch", "Manual trigger"),
    ("docker", "Docker build step"),
    ("upload-artifact", "Artifact upload"),
    ("pages", "GitHub Pages deployment"),
    ("game.wasm", "WASM file validation"),
]

for needle, desc in ci_features:
    if needle.lower() in ci_content.lower():
        ok(f"Feature: {desc}")
    else:
        fail(f"Missing feature: {desc}")


# =========================================================================
# 7. Cross-reference: build.sh references
# =========================================================================
section("Cross-reference: build.sh ↔ shell files")

build_path = os.path.join(_WEB_DIR, "build.sh")
with open(build_path) as f:
    build_content = f.read()

build_refs = [
    ("shell/index.html", "References index.html"),
    ("shell/shell.css", "References shell.css"),
    ("shell/shell.js", "References shell.js"),
    ("shell/sw.js", "References sw.js"),
    ("scripts/package_assets.py", "References package_assets.py"),
    ("scripts/web_overrides.rb", "References web_overrides.rb"),
    ("manifest.json", "References manifest.json"),
]

for needle, desc in build_refs:
    if needle in build_content:
        ok(desc)
    else:
        fail(desc)


# =========================================================================
# Summary
# =========================================================================
print(f"\n{'='*60}")
if errors == 0:
    print(f"\033[1;32m  ALL CHECKS PASSED\033[0m")
else:
    print(f"\033[1;31m  {errors} CHECK(S) FAILED\033[0m")
print(f"{'='*60}\n")

sys.exit(1 if errors else 0)




