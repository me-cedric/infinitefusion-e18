---
id: infinitefusion-outfit-workflow
trigger: "when adding new clothes, hats, or hairstyles to the game"
confidence: 0.9
domain: game-content
source: local-repo-analysis
analyzed_commits: 200
---

# Follow the Outfit Addition Workflow

## Action
When adding a new outfit/hat/hairstyle:
1. Create all required sprite variants in `Graphics/Characters/player/{type}/{name}/`
2. Register the ID in `Data/Scripts/050_Outfits/OutfitIds.rb` (if applicable)
3. Add the data entry to the corresponding JSON file in `Data/outfits/`
4. Clothes require 7 sprite variants: walk, run, bike, surf, dive, fish, trainer
5. Hats require 2 sprites: normal + trainer
6. Hair requires 4-5 color variants + trainer variants

## Evidence
- 31 "Adds" commits in 200 analyzed, majority adding customization content
- Consistent file co-change pattern: OutfitIds.rb + JSON data + sprite assets
- Missing sprite variants cause visual glitches (5+ bug fix commits related)

**Why:** The outfit system expects all variants to exist. Missing sprites cause crashes or visual glitches at runtime.

**How to apply:** Always verify all sprite variants are present before committing new outfit content.
