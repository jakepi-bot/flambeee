# Story 001: Game Hub / Launcher

**Priority:** 1
**Status:** Ready for development
**Author:** Quinn (BA) with Ember (PM)

## Description

As a player, I want a central page where I can see all available Flambeee games and choose which one to play, so I don't have to remember individual URLs or navigate manually.

## Acceptance Criteria (BDD)

### Scenario 1: Viewing the game hub
```gherkin
Given I navigate to the Flambeee game hub
Then I should see a title "🔥 Flambeee Games"
And I should see cards for each available game
And each card should show the game name, a brief description, and a "Play" button
```

### Scenario 2: Launching a game from the hub
```gherkin
Given I am on the game hub
When I click the "Play" button on a game card
Then I should be taken to that game's page
```

### Scenario 3: Returning from a game to the hub
```gherkin
Given I am playing a game
When I click the "Back to Games" link
Then I should return to the game hub
```

### Scenario 4: Hub shows available games accurately
```gherkin
Given the hub page is loaded
Then I should see Minesweeper listed
And I should see Simon listed
And each card should have an emoji icon representing the game
```

### Scenario 5: Mobile-friendly hub
```gherkin
Given I am on a mobile device
When I view the game hub
Then the game cards should stack vertically
And each card should be fully tappable
```

## Technical Notes

- Hub lives at `src/index.html` (replaces the current Minesweeper-only page)
- Minesweeper moves to `src/minesweeper.html`
- Simon lives at `src/simon.html`
- All three pages share the same dark theme (--bg, --surface, --accent)
- Hub links to games via relative paths
- Games link back to hub via a "Back to Games" link