# Story 002: Simon Memory Game

**Priority:** 2
**Status:** Ready for development
**Author:** Quinn (BA) with Ember (PM)

## Description

As a player, I want to play a Simon-style memory game where I repeat increasingly long sequences of colored button presses, so I can test and improve my memory skills.

## Acceptance Criteria (BDD)

### Scenario 1: Starting a new game
```gherkin
Given I am on the Simon game page
When I click the "Start" button
Then the game should begin
And a sequence of one colored pad should flash
```

### Scenario 2: Repeating the sequence correctly
```gherkin
Given the game has shown a sequence of N pads
When I press the pads in the same order
Then the game should accept my input
And the game should add one more pad to the sequence
And the new sequence should flash for me to repeat
```

### Scenario 3: Making a mistake
```gherkin
Given the game has shown a sequence
When I press the wrong pad or press in the wrong order
Then the game should indicate I made an error
And the game should show my score (rounds completed)
And a "Play Again" button should appear
```

### Scenario 4: Score display
```gherkin
Given I am playing Simon
Then I should see my current round number displayed
And I should see my best score (stored in localStorage)
```

### Scenario 5: Visual and audio feedback
```gherkin
Given I am playing Simon
When a pad flashes in the sequence
Then it should light up visually and play a distinct tone
When I press a pad
Then it should light up and play its tone
```

### Scenario 6: Mobile support
```gherkin
Given I am on a mobile device
When I view the Simon game
Then the pads should be sized for touch interaction
And the layout should work in portrait orientation
```

### Scenario 7: Returning to the game hub
```gherkin
Given I am on the Simon game page
When I click "Back to Games"
Then I should return to the game hub
```

## Technical Notes

- Single-file HTML/CSS/JS at `src/simon.html`
- 4 colored pads (red, blue, green, yellow) in a 2x2 grid
- Each pad has a unique tone (Web Audio API or oscillator-based)
- localStorage for best score persistence
- Dark theme matching the Flambeee visual identity
- Increasing sequence length by 1 each successful round
- "Start" button to begin, overlay for game over
- Back to Games link at the top