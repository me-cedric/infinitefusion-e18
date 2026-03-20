# =============================================================================
# NOTE: This file is UNUSED — mkxp-z uses Meson, not CMake.
# Kept for reference. The actual build config is in emscripten-cross.ini
# and the Meson options passed in the Dockerfile.
#
# The Emscripten link flags below are applied via emscripten-cross.ini
# and/or the final linking step in build.sh
# =============================================================================
#
# Key Emscripten flags for the final link:
#
#   -sASYNCIFY                              Yield to browser event loop
#   -sASYNCIFY_STACK_SIZE=65536             Stack for async unwinding
#   -sASYNCIFY_IMPORTS=[...]                Functions that may yield
#   -sUSE_SDL=2                             SDL2 port
#   -sUSE_SDL_IMAGE=2                       SDL2_image port
#   -sUSE_SDL_TTF=2                         SDL2_ttf port
#   -sINITIAL_MEMORY=268435456              256 MB initial heap
#   -sMAXIMUM_MEMORY=536870912              512 MB max heap
#   -sALLOW_MEMORY_GROWTH=1                 Heap grows as needed
#   -sSTACK_SIZE=1048576                    1 MB stack
#   -sFORCE_FILESYSTEM=1                    Enable Emscripten VFS
#   -lidbfs.js                              IDBFS for persistent storage
#   -sFETCH                                 Fetch API for HTTP
#   -sEXPORTED_RUNTIME_METHODS=[...]        JS-accessible runtime methods
#   -sEXPORTED_FUNCTIONS=[...]              Exported C functions
#   -sMODULARIZE=1                          Module factory function
#   -sEXPORT_NAME='createMkxpModule'        Module factory name
#   -sWASM=1                                Output WebAssembly
#   -O2 -flto                               Optimization
#
# These flags are now specified in:
#   - emscripten-cross.ini  (compile flags)
#   - Dockerfile            (link flags via Meson setup)
# =============================================================================
