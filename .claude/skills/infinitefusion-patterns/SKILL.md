---
name: infinitefusion-patterns
description: Coding patterns extracted from the infinitefusion-e18 RPG Maker XP project (Ruby, Pokemon fangame)
version: 1.0.0
source: local-git-analysis
analyzed_commits: 200
---

# Infinite Fusion Patterns

## Project Overview

This is a **Pokemon Infinite Fusion** fangame built on **RPG Maker XP** (RGSS/Ruby). The codebase consists of 427+ Ruby scripts, binary `.rxdata` map/game data files, and extensive sprite/graphics assets.

## Commit Conventions

This project uses **informal, descriptive commit messages** (not conventional commits):
- `Fixes ...` — Bug fixes (most common, ~35% of commits)
- `Adds ...` — New features or content
- `Updates ...` — Modifications to existing content
- `Removes ...` — Cleanup (debugging logs, commented code)
- `Merge pull request #N` — GitHub PR merges

Commits are typically **sentence-case** without a type prefix. No co-author attribution is used.

## Code Architecture

```
Data/
├── Scripts/                      # Ruby source code (427+ files)
│   ├── 001_Settings.rb           # Global game settings
│   ├── 001_Technical/            # Core engine utilities
│   ├── 005_Sprites/              # Sprite rendering system
│   ├── 011_Battle/               # Battle system (phases, scenes, commands)
│   ├── 012_Overworld/            # Overworld mechanics
│   ├── 014_Pokemon/              # Pokemon data and logic
│   ├── 016_UI/                   # UI screens (Pokedex, menus)
│   ├── 048_Fusion/               # Fusion-specific logic & sprite extraction
│   ├── 050_Outfits/              # Character customization (most active)
│   │   ├── 001_OutfitsMain/      # Core outfit system
│   │   ├── OutfitIds.rb          # Outfit identifier constants
│   │   ├── ItemSets.rb           # Item set definitions
│   │   ├── UI/                   # Outfit UI (clothes shop, hat shop)
│   │   ├── utils/                # Outfit utility functions
│   │   └── wrappers/             # Wrapper classes
│   ├── 051_Wrappers/             # General wrapper classes
│   └── 052_AddOns/               # Add-on features (MultiSaves, GameplayUtils)
├── outfits/                      # JSON data for outfits
│   ├── clothes_data.json
│   ├── hairstyles_data.json
│   └── hats_data.json
├── pokedex/                      # Pokedex entry data (JSON)
├── sprites/                      # Sprite cache & rate limit logs
├── *.rxdata                      # Binary RPG Maker data (maps, events, items)
└── messages.dat                  # Game text/messages

Graphics/
├── Battlers/                     # Battle sprites
├── Characters/                   # Overworld character sprites
│   └── player/                   # Player customization sprites
│       ├── clothes/{name}/       # Outfit sprites (7 per set: walk, run, bike, surf, dive, fish, trainer)
│       ├── hair/{name}/          # Hairstyle sprites (4-5 color variants + trainer variants)
│       └── hat/{name}/           # Hat sprites (normal + trainer variants)
├── Items/                        # Item icons
├── Pictures/                     # UI pictures
└── Tilesets/                     # Map tilesets

PBS/                              # Pokemon Essentials PBS data
├── items.txt                     # Item definitions
└── trainers.txt                  # Trainer definitions

Audio/
└── SE/                           # Sound effects
```

## Key Modules & Hotspots

### 050_Outfits (Most Active Module)
The character customization system is the most actively developed area:
- **ClothesShopPresenter.rb** — Main controller for the clothes shop UI (18 changes in 200 commits)
- **HatsMartAdapter.rb** — Hat shop data adapter (15 changes)
- **OutfitIds.rb** — Outfit ID constants (12 changes)
- **ClothesShopPresenter_HatsMenu.rb** — Hats sub-menu presenter
- **0_OutfitsMartAdapter.rb** — Base adapter class for outfit shops

Pattern: Uses **MVP architecture** (Presenter/View/Adapter) for the outfit shop UI.

### Files That Change Together
These files almost always change in the same commit:
1. `Data/System.rxdata` + `Data/sprites/updated_spritesheets_cache` (always together)
2. `ClothesShopPresenter.rb` + `ClothesShopView.rb` (UI changes)
3. `OutfitIds.rb` + outfit JSON data files (adding new outfits)
4. `Data/Actors.rxdata` + `Data/Items.rxdata` + other `.rxdata` files (bulk game data updates)

### 052_AddOns
- **GameplayUtils.rb** — Utility functions modified in 20 commits
- **MultiSaves.rb** — Multiple save system
- **New Items effects.rb** — Custom item effect implementations

## Workflows

### Adding a New Outfit
1. Create sprite PNGs in `Graphics/Characters/player/clothes/{name}/` (7 variants: walk, run, bike, surf, dive, fish, trainer)
2. Add outfit ID to `Data/Scripts/050_Outfits/OutfitIds.rb`
3. Add outfit data entry to `Data/outfits/clothes_data.json`
4. Update `Data/System.rxdata` (RPG Maker project metadata)
5. Sprite cache gets regenerated (`Data/sprites/updated_spritesheets_cache`)

### Adding a New Hat
1. Create sprite PNGs in `Graphics/Characters/player/hat/{name}/` (normal + trainer variant)
2. Add hat data to `Data/outfits/hats_data.json`
3. Optionally add hat ID to `OutfitIds.rb`
4. Update `Data/System.rxdata`

### Adding a New Hairstyle
1. Create sprite PNGs in `Graphics/Characters/player/hair/{name}/` (4-5 color variants + trainer variants)
2. Add hairstyle data to `Data/outfits/hairstyles_data.json`
3. Update `Data/System.rxdata`

### Fixing a Bug
1. Identify the script file in `Data/Scripts/`
2. Fix the Ruby code
3. Commits typically include just the script file + `Data/System.rxdata`
4. Common pattern: remove debugging logs in a follow-up commit

## Sprite Naming Conventions

### Clothes
`clothes_{action}_{name}.png` where action is: `walk`, `run`, `bike`, `surf`, `dive`, `fish`, `trainer`

### Hair
`hair_{colorIndex}_{name}.png` (colors 1-5) + `hair_trainer_{colorIndex}_{name}.png`

### Hats
`hat_{name}.png` + `hat_trainer_{name}.png`

## Testing Patterns

This project has **no automated tests**. Quality assurance is done through manual playtesting. Bug fixes are common and typically address:
- UI crashes and navigation issues
- Visual glitches (sprites, animations)
- Uninitialized variable errors
- Game state corruption

## Common Bug Patterns

Based on commit history:
1. **Uninitialized variables** — Maps/hashes not initialized before first access
2. **Menu navigation issues** — Selection state not properly reset between menus
3. **Visual glitches** — Sprite rendering issues when switching outfits/hats
4. **Crash on missing data** — Code assumes data exists without nil checks

## Binary Data Files

Many `.rxdata` files are binary RPG Maker serialized data. These change frequently but cannot be meaningfully diffed:
- `Data/System.rxdata` — Changes in 107/200 commits (project metadata, always updated)
- `Data/MapInfos.rxdata` — Map listing (69 changes)
- `Data/CommonEvents.rxdata` — Shared game events (40 changes)
- Individual `Data/MapNNN.rxdata` files — Per-map data

## External Contributions

The project accepts pull requests from external contributors (e.g., KamilaBorowska, GLugia, fellow-dev-simon). Merges are done via GitHub's merge commit strategy.
