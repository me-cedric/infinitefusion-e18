---
id: infinitefusion-cleanup-debug
trigger: "when committing code changes to Ruby scripts"
confidence: 0.75
domain: code-quality
source: local-repo-analysis
analyzed_commits: 200
---

# Remove Debug Logs Before Committing

## Action
Before committing Ruby script changes:
1. Search for `p `, `print`, `puts`, or `echoln` debug statements in modified files
2. Remove any debugging output that was added during development
3. Keep intentional game logging (e.g., error handling)

## Evidence
- "Removes debugging logs" appears 3 times in 200 commits
- "Removes some debugging logs" (commit 47876255)
- "Removes commented code" (commit d754fc45)
- Pattern: debug logs are added during feature work, then cleaned up in a separate commit

**Why:** Debug output left in game scripts can cause performance issues, leak internal state to players, and clutter the console.

**How to apply:** Do a final pass for debug statements before committing. Ideally clean them in the same commit as the feature, not as a follow-up.
