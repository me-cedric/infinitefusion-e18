---
id: infinitefusion-nil-check
trigger: "when modifying Ruby scripts that access hashes, maps, or game variables"
confidence: 0.85
domain: ruby-bugfix
source: local-repo-analysis
analyzed_commits: 200
---

# Always Initialize and Nil-Check Data Structures

## Action
Before accessing hashes, maps, or player data in Ruby scripts:
1. Initialize the data structure if it might not exist yet (`||= {}`, `||= []`)
2. Check for nil before accessing nested values
3. Pay special attention to outfit-related maps (dyed items, equipped items)

## Evidence
- "Fixes issue with possible uninitialized dyed items map" (commit 7358d67)
- "clothes menu crash fix" (commit 701ea9a)
- "Fixes new game crash" (commit 0c06b7a)
- Multiple crash fixes traced to uninitialized variables

**Why:** RPG Maker XP's Ruby runtime doesn't provide helpful error messages. Uninitialized variable access causes cryptic crashes that are hard to diagnose in-game.

**How to apply:** When touching any code that reads from player state, game variables, or outfit data, defensively initialize before use.
