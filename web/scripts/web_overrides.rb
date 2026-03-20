# =============================================================================
# Pokemon Infinite Fusion — Web Platform Overrides
# Loaded as 000_Web/000_WebOverrides.rb (before all game scripts)
#
# Patches Ruby-side code for browser compatibility:
#   - Save path → IDBFS mount (/saves/)
#   - Disable desktop-only file operations
#   - Route HTTP through Emscripten fetch
#   - Skip sprite folder management
# =============================================================================

module WebPlatform
  RUNNING_ON_WEB = true
  SAVES_DIR = "/saves"
  CACHE_DIR = "/cache"
  CDN_BASE_URL = "" # Set at build time via shell.js injection

  def self.web?
    true
  end

  # Sync IDBFS to IndexedDB (persists saves across sessions)
  # Called from C++ side after Marshal.dump, but also available from Ruby
  def self.sync_filesystem
    # Implemented in C++ via EM_ASM:
    #   FS.syncfs(false, function(err) { if(err) console.error('syncfs:', err); });
  end
end

# =============================================================================
# Override: Save file path → IDBFS
# =============================================================================
module SaveData
  remove_const(:FILE_PATH) if const_defined?(:FILE_PATH)
  FILE_PATH = "/saves/Game.rxdata"

  # Disable Windows save migration (not applicable on web)
  def self.move_old_windows_save
    # no-op on web
  end
end

# =============================================================================
# Override: System.data_directory → /saves/
# =============================================================================
module System
  class << self
    alias_method :_original_data_directory, :data_directory if method_defined?(:data_directory)

    def data_directory
      "/saves"
    end
  end
end

# =============================================================================
# Override: Disable desktop-only sprite folder operations
# =============================================================================

# Skip sprite sorting (requires local filesystem writes)
def sortCustomBattlers
  $game_temp.nb_imported_sprites = 0 if $game_temp
  # no-op on web — sprites loaded from CDN
end

# Skip custom folder creation
def createCustomSpriteFolders
  # no-op on web
end

# Skip temp folder clearing
def clearTempFolder
  # no-op on web
end

# Skip sprite replacement dialog
def handleReplaceExistingSprites
  # no-op on web
end

# =============================================================================
# Override: File operations safety layer
# =============================================================================
module WebFileGuard
  WRITABLE_PREFIXES = ["/saves/", "/cache/"].freeze

  def self.writable?(path)
    WRITABLE_PREFIXES.any? { |prefix| path.start_with?(prefix) }
  end
end

# Wrap File.rename to only work in writable paths
class << File
  alias_method :_original_rename, :rename

  def rename(old_path, new_path)
    if WebFileGuard.writable?(old_path) && WebFileGuard.writable?(new_path)
      _original_rename(old_path, new_path)
    end
  end
end

# Wrap File.delete to only work in writable paths
class << File
  alias_method :_original_delete, :delete

  def delete(*paths)
    safe_paths = paths.select { |p| WebFileGuard.writable?(p) }
    _original_delete(*safe_paths) unless safe_paths.empty?
  end
end

# Wrap Dir.mkdir to only work in writable paths
class << Dir
  alias_method :_original_mkdir, :mkdir

  def mkdir(path, *args)
    if WebFileGuard.writable?(path)
      _original_mkdir(path, *args)
    end
  end
end

# =============================================================================
# Override: HTTP downloads → web-compatible
# =============================================================================

# Downloads are allowed on web (routed through Emscripten fetch / CDN)
def downloadAllowed?
  true
end

# =============================================================================
# Override: Graphics — disable desktop window management
# =============================================================================

def pbSetResizeFactor(factor)
  if !$ResizeInitialized
    Graphics.resize_screen(Settings::SCREEN_WIDTH, Settings::SCREEN_HEIGHT)
    $ResizeInitialized = true
  end
  # Skip fullscreen/scale changes — CSS handles canvas scaling on web
end

# =============================================================================
# Override: Window title (no-op on web, but harmless)
# =============================================================================

def pbSetWindowText(string)
  # Could set document.title via EM_ASM, but not critical
end

# =============================================================================
# Override: showLoadingScreen — web version shows progress in HTML overlay
# =============================================================================

# The HTML shell handles the loading UI. The Ruby-side loading screen
# still works but is secondary to the HTML progress bar.

echo "[web] Web platform overrides loaded\n" if $DEBUG
