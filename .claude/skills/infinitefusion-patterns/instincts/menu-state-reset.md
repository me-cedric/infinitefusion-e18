---
id: infinitefusion-menu-state
trigger: "when modifying menu navigation or selection logic in UI scripts"
confidence: 0.8
domain: ui-bugfix
source: local-repo-analysis
analyzed_commits: 200
---

# Reset Menu State When Switching Between Menus

## Action
When implementing menu transitions (especially in the outfit shop):
1. Reset selection index when entering a new menu/sub-menu
2. Clear any cached visual state (sprites, overlays) when switching views
3. Handle the case where a menu opens on the currently equipped item
4. Test navigation between clothes menu, hats menu, and hair menu

## Evidence
- "Fixes hats menu navigation issue" (commit 03b832a)
- "Hats menu navigation improvements" (commit 36851c7)
- "Fixes swapping hats visual glitch when only wearing one hat" (commit 5343792)
- "Clothes and Hats selection menu now opens on current worn outfit" (commit added as feature)

**Why:** The outfit shop has multiple interconnected menus. Stale selection state causes visual glitches and navigation bugs that are frustrating for players.

**How to apply:** Any change to menu navigation should be tested by switching between all sub-menus multiple times, wearing and removing items in different orders.
