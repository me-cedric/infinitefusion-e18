---
id: infinitefusion-mvp-ui
trigger: "when creating or modifying UI screens in Data/Scripts"
confidence: 0.8
domain: architecture
source: local-repo-analysis
analyzed_commits: 200
---

# Follow MVP Pattern for UI Screens

## Action
UI screens in this project follow a Model-View-Presenter pattern:
- **Presenter** (`*Presenter.rb`) — Controls UI logic, handles input, manages state
- **View** (`*View.rb`) — Renders sprites and UI elements
- **Adapter** (`*MartAdapter.rb`) — Provides data to the presenter (items, prices, availability)

When modifying UI:
1. Business logic changes go in the Presenter
2. Visual changes go in the View
3. Data source changes go in the Adapter
4. Presenter and View files typically change together

## Evidence
- ClothesShopPresenter.rb (18 changes) + ClothesShopView.rb always co-change
- Separate adapter classes: ClothesMartAdapter, HatsMartAdapter, HairMartAdapter
- Split presenters for sub-menus: ClothesShopPresenter_HatsMenu.rb

**Why:** The outfit shop UI is the most complex and frequently modified UI in the game. The MVP separation keeps changes localized and reduces regression risk.

**How to apply:** When building new UI screens, create matching Presenter/View/Adapter files. When fixing bugs, identify which layer the issue belongs to.
