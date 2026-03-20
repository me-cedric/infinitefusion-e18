# =============================================================================
# Pokemon Infinite Fusion - Web Build Environment
# Compiles mkxp-z + CRuby to WebAssembly via Emscripten
#
# mkxp-z uses Meson. Native deps must be cross-compiled for wasm32.
# Emscripten ports provide: SDL2, SDL2_image, SDL2_ttf, freetype, zlib, libpng
# We build from source: physfs, openal-soft, theora, vorbis, ogg, pixman,
#   SDL2_sound, libjpeg, uchardet, bzip2, Ruby (CRuby 3.1.x)
# =============================================================================

FROM emscripten/emsdk:3.1.51 AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV EMSDK=/emsdk
ENV EM_CACHE=/emsdk/upstream/emscripten/cache
ENV WASM_PREFIX=/build/wasm-sysroot
ENV PKG_CONFIG_PATH=${WASM_PREFIX}/lib/pkgconfig
ENV EM_PKG_CONFIG_PATH=${WASM_PREFIX}/lib/pkgconfig

# System build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    autoconf automake bison build-essential cmake curl git libtool \
    meson ninja-build pkg-config python3 python3-pip ruby wget xxd \
    pngquant ffmpeg \
    && pip3 install --no-cache-dir Pillow \
    && rm -rf /var/lib/apt/lists/*

# Pre-build Emscripten ports (cached in Docker layer)
RUN embuilder build sdl2 sdl2_image sdl2_ttf zlib libpng freetype harfbuzz

WORKDIR /build
RUN mkdir -p ${WASM_PREFIX}/lib ${WASM_PREFIX}/include ${WASM_PREFIX}/lib/pkgconfig

# Copy Meson cross-file early (needed by pixman and mkxp-z builds)
COPY emscripten-cross.ini /build/emscripten-cross.ini

# Create stub pkg-config .pc files for Emscripten port libraries.
# Emscripten provides SDL2, SDL2_image, SDL2_ttf, freetype, zlib, libpng as
# compiler ports (-sUSE_SDL=2 etc), but no .pc files. Meson needs them.
RUN PC=${WASM_PREFIX}/lib/pkgconfig && mkdir -p $PC \
    && printf 'Name: SDL2\nVersion: 2.0.0\nDescription: Emscripten SDL2 port\nCflags: -sUSE_SDL=2\nLibs: -sUSE_SDL=2\n' > $PC/sdl2.pc \
    && printf 'Name: SDL2_image\nVersion: 2.0.0\nDescription: Emscripten SDL2_image port\nRequires: sdl2\nCflags: -sUSE_SDL_IMAGE=2\nLibs: -sUSE_SDL_IMAGE=2\n' > $PC/SDL2_image.pc \
    && printf 'Name: SDL2_ttf\nVersion: 2.0.0\nDescription: Emscripten SDL2_ttf port\nRequires: sdl2\nCflags: -sUSE_SDL_TTF=2\nLibs: -sUSE_SDL_TTF=2\n' > $PC/SDL2_ttf.pc \
    && printf 'Name: freetype2\nVersion: 2.0.0\nDescription: Emscripten freetype port\nCflags: -sUSE_FREETYPE=1\nLibs: -sUSE_FREETYPE=1\n' > $PC/freetype2.pc \
    && printf 'Name: zlib\nVersion: 1.2.0\nDescription: Emscripten zlib port\nCflags: -sUSE_ZLIB=1\nLibs: -sUSE_ZLIB=1\n' > $PC/zlib.pc \
    && printf 'Name: libpng\nVersion: 1.6.0\nDescription: Emscripten libpng port\nRequires: zlib\nCflags: -sUSE_LIBPNG=1\nLibs: -sUSE_LIBPNG=1\n' > $PC/libpng.pc \
    && printf 'Name: libjpeg\nVersion: 3.0.0\nDescription: libjpeg-turbo\nCflags: -I${WASM_PREFIX}/include\nLibs: -L${WASM_PREFIX}/lib -ljpeg\n' | sed "s|\${WASM_PREFIX}|${WASM_PREFIX}|g" > $PC/libjpeg.pc \
    && ls -la $PC/

# Create empty stub static libraries for iconv and charset.
# On Emscripten, iconv functions are built into libc; charset is unused.
# mkxp-z's meson.build does find_library('iconv') and find_library('charset').
RUN cd ${WASM_PREFIX}/lib \
    && /emsdk/upstream/emscripten/emar rcs libiconv.a \
    && /emsdk/upstream/emscripten/emar rcs libcharset.a \
    && ls -la libiconv.a libcharset.a

# =============================================================================
# Stage 1: Build native dependencies for wasm32-emscripten
# =============================================================================

# Download modern config.sub/config.guess (old ones don't know wasm32)
RUN curl -sL 'https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' > /build/config.sub \
    && curl -sL 'https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' > /build/config.guess \
    && chmod +x /build/config.sub /build/config.guess

# ---- libogg ----
ARG OGG_VERSION=1.3.5
RUN curl -sL https://downloads.xiph.org/releases/ogg/libogg-${OGG_VERSION}.tar.xz | tar xJ \
    && cd libogg-${OGG_VERSION} \
    && cp /build/config.sub . && cp /build/config.guess . \
    && emconfigure ./configure --prefix=${WASM_PREFIX} --host=wasm32-unknown-emscripten --disable-shared --enable-static \
    && emmake make -j$(nproc) && emmake make install \
    && cd /build && rm -rf libogg-${OGG_VERSION}

# ---- libvorbis ----
ARG VORBIS_VERSION=1.3.7
RUN curl -sL https://downloads.xiph.org/releases/vorbis/libvorbis-${VORBIS_VERSION}.tar.xz | tar xJ \
    && cd libvorbis-${VORBIS_VERSION} \
    && cp /build/config.sub . && cp /build/config.guess . \
    && emconfigure ./configure --prefix=${WASM_PREFIX} --host=wasm32-unknown-emscripten --disable-shared --enable-static \
       --with-ogg=${WASM_PREFIX} \
    && emmake make -j$(nproc) && emmake make install \
    && cd /build && rm -rf libvorbis-${VORBIS_VERSION}

# ---- libtheora ----
ARG THEORA_VERSION=1.1.1
RUN curl -sL https://downloads.xiph.org/releases/theora/libtheora-${THEORA_VERSION}.tar.bz2 | tar xj \
    && cd libtheora-${THEORA_VERSION} \
    && cp /build/config.sub . && cp /build/config.guess . \
    && emconfigure ./configure --prefix=${WASM_PREFIX} --host=wasm32-unknown-emscripten \
       --disable-shared --enable-static \
       --with-ogg=${WASM_PREFIX} --disable-asm --disable-spec --disable-examples --disable-encode \
    && emmake make -j$(nproc) && emmake make install \
    && cd /build && rm -rf libtheora-${THEORA_VERSION}

# ---- bzip2 (no autoconf, manual build) ----
ARG BZ2_VERSION=1.0.8
RUN curl -sL https://sourceware.org/pub/bzip2/bzip2-${BZ2_VERSION}.tar.gz | tar xz \
    && cd bzip2-${BZ2_VERSION} \
    && emmake make CC=emcc AR=emar RANLIB=emranlib CFLAGS="-O2" libbz2.a \
    && cp libbz2.a ${WASM_PREFIX}/lib/ \
    && cp bzlib.h ${WASM_PREFIX}/include/ \
    && cd /build && rm -rf bzip2-${BZ2_VERSION}

# ---- libjpeg-turbo ----
ARG JPEGT_VERSION=3.0.1
RUN curl -sL https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/${JPEGT_VERSION}/libjpeg-turbo-${JPEGT_VERSION}.tar.gz | tar xz \
    && cd libjpeg-turbo-${JPEGT_VERSION} \
    && mkdir build-wasm && cd build-wasm \
    && emcmake cmake .. -G Ninja \
       -DCMAKE_INSTALL_PREFIX=${WASM_PREFIX} \
       -DCMAKE_BUILD_TYPE=Release \
       -DENABLE_SHARED=OFF -DWITH_SIMD=OFF -DWITH_TURBOJPEG=OFF \
    && ninja -j$(nproc) && ninja install \
    && cd /build && rm -rf libjpeg-turbo-${JPEGT_VERSION}

# ---- pixman ----
ARG PIXMAN_VERSION=0.42.2
RUN curl -sL https://cairographics.org/releases/pixman-${PIXMAN_VERSION}.tar.gz | tar xz \
    && cd pixman-${PIXMAN_VERSION} \
    && mkdir build-wasm && cd build-wasm \
    && meson setup --cross-file /build/emscripten-cross.ini \
       --prefix=${WASM_PREFIX} --default-library=static \
       -Dgtk=disabled -Dlibpng=disabled -Dopenmp=disabled .. \
    && ninja -j$(nproc) && ninja install \
    && cd /build && rm -rf pixman-${PIXMAN_VERSION}

# ---- uchardet ----
ARG UCHARDET_VERSION=0.0.8
RUN curl -sL https://www.freedesktop.org/software/uchardet/releases/uchardet-${UCHARDET_VERSION}.tar.xz | tar xJ \
    && cd uchardet-${UCHARDET_VERSION} \
    && mkdir build-wasm && cd build-wasm \
    && emcmake cmake .. -G Ninja \
       -DCMAKE_INSTALL_PREFIX=${WASM_PREFIX} \
       -DCMAKE_BUILD_TYPE=Release \
       -DBUILD_BINARY=OFF -DBUILD_SHARED_LIBS=OFF \
    && ninja -j$(nproc) && ninja install \
    && cd /build && rm -rf uchardet-${UCHARDET_VERSION}

# ---- PhysicsFS ----
ARG PHYSFS_VERSION=3.2.0
RUN curl -sL https://github.com/icculus/physfs/archive/refs/tags/release-${PHYSFS_VERSION}.tar.gz | tar xz \
    && cd physfs-release-${PHYSFS_VERSION} \
    && mkdir build-wasm && cd build-wasm \
    && emcmake cmake .. -G Ninja \
       -DCMAKE_INSTALL_PREFIX=${WASM_PREFIX} \
       -DCMAKE_BUILD_TYPE=Release \
       -DPHYSFS_BUILD_SHARED=OFF -DPHYSFS_BUILD_TEST=OFF \
    && ninja -j$(nproc) && ninja install \
    && cd /build && rm -rf physfs-release-${PHYSFS_VERSION}

# ---- OpenAL Soft (Emscripten backend) ----
ARG OPENAL_VERSION=1.23.1
RUN git clone --depth 1 --branch ${OPENAL_VERSION} \
      https://github.com/kcat/openal-soft.git /build/openal-soft \
    && cd /build/openal-soft && mkdir build-wasm && cd build-wasm \
    && emcmake cmake .. -G Ninja \
       -DCMAKE_INSTALL_PREFIX=${WASM_PREFIX} \
       -DCMAKE_BUILD_TYPE=Release \
       -DALSOFT_UTILS=OFF -DALSOFT_EXAMPLES=OFF -DALSOFT_TESTS=OFF \
       -DALSOFT_BACKEND_WAVE=OFF -DALSOFT_REQUIRE_SDL2=ON \
       -DLIBTYPE=STATIC \
    && ninja -j$(nproc) && ninja install \
    && cd /build && rm -rf openal-soft

# ---- SDL2_sound (pin to v2.0.4 — latest HEAD requires SDL3) ----
RUN git clone --depth 1 --branch v2.0.4 https://github.com/icculus/SDL_sound.git /build/SDL_sound \
    && cd /build/SDL_sound && mkdir build-wasm && cd build-wasm \
    && emcmake cmake .. -G Ninja \
       -DCMAKE_INSTALL_PREFIX=${WASM_PREFIX} \
       -DCMAKE_BUILD_TYPE=Release \
       -DSDLSOUND_BUILD_SHARED=OFF -DSDLSOUND_BUILD_TEST=OFF \
       -DSDL2_INCLUDE_DIR=${EM_CACHE}/sysroot/include/SDL2 \
    && ninja -j$(nproc) && ninja install \
    && cd /build && rm -rf SDL_sound

# =============================================================================
# Stage 2: Download pre-built CRuby for wasm32-emscripten
# Building Ruby from source for Emscripten requires extensive patches.
# The ruby/ruby.wasm project provides nightly pre-built binaries.
# =============================================================================

ARG RUBY_WASM_RELEASE=2026-03-12-a
ARG RUBY_WASM_VERSION=3.2

RUN curl -sL "https://github.com/ruby/ruby.wasm/releases/download/${RUBY_WASM_RELEASE}/ruby-${RUBY_WASM_VERSION}-wasm32-unknown-emscripten-full.tar.gz" \
    | tar xz -C /build \
    && mv /build/ruby-${RUBY_WASM_VERSION}-wasm32-unknown-emscripten-full /build/ruby-wasm-install \
    && echo "Ruby WASM installed:" \
    && ls -la /build/ruby-wasm-install/usr/local/lib/libruby-static.a \
    && ls /build/ruby-wasm-install/usr/local/include/ruby-*/ruby.h

# =============================================================================
# Stage 3: Build mkxp-z for wasm32-emscripten (Meson)
# =============================================================================

ARG MKXPZ_VERSION=v2.4.0

RUN git clone --depth 1 --branch ${MKXPZ_VERSION} \
    https://gitlab.com/mkxp-z/mkxp-z.git /build/mkxp-z

# Copy and apply patches
COPY patches/ /build/patches/
RUN cd /build/mkxp-z \
    && for patch in /build/patches/mkxp-z-*.patch; do \
         [ -f "$patch" ] && git apply --check "$patch" 2>/dev/null && git apply "$patch" && echo "Applied: $patch" || echo "Skip: $patch"; \
       done

# Configure and build mkxp-z via Meson
RUN cd /build/mkxp-z \
    && meson setup build-web --cross-file /build/emscripten-cross.ini \
       --prefix=/build/mkxp-z-install \
       --default-library=static \
       -Dgfx_backend=gles \
       -Denable-https=false \
       -Duse_miniffi=false \
       -Dsteamworks_path='' \
       -Dshared_fluid=false \
       -Dmri_version=3.2 \
       -Dmri_includes=/build/ruby-wasm-install/usr/local/include/ruby-3.2.0 \
       -Dmri_library=ruby-static \
       -Dmri_libpath=/build/ruby-wasm-install/usr/local/lib \
    && cd build-web \
    && ninja -j$(nproc)

# =============================================================================
# Stage 4: Final assembly container
# =============================================================================

COPY scripts/ /build/scripts/
COPY shell/ /build/shell/
COPY build.sh /build/build.sh
RUN chmod +x /build/build.sh

RUN mkdir -p /build/dist

ENTRYPOINT ["/build/build.sh"]
