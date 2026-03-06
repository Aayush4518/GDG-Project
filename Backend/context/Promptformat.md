This will be the format of the prompts that im gonna feed you, make sure you adhere to ths format 

# Prompt-format template — a reusable structure you can copy/paste

here’s a compact, practical template you can reuse whenever you want a clear engineering-style prompt (like the UNO one). I’ll give you: 1) a short explanation of each section, 2) the literal template you can paste and fill, and 3) a tiny example showing how it looks when filled. Use this for code changes, documentation updates, tests, or any task that must modify files.

---

## Why this structure works (quick)

Each prompt has:

* **Goal** — one-sentence outcome (what success looks like).
* **Context** — short background so the worker understands why it matters.
* **Objective** — exact scope of the task (what to change).
* **Detailed Instructions** — step-by-step actionable edits, with file paths, functions, code snippets, and edge cases.
* **Final deliverable** — exactly what you want returned (files, full updated code, diff, tests, checklist).
  This minimizes back-and-forth and ambiguity.

---

## Copy-paste template

```
TITLE: <short title of the task>

GOAL:
- <One-line statement of the desired outcome / success criteria.>

CONTEXT:
- <Two–four lines giving relevant background, constraints, or why this change is needed.>

SCOPE / OBJECTIVE:
- Target files:
  - <path/to/FileA.ext>
  - <path/to/FileB.ext>
- High-level objective:
  - <What should be implemented or changed — brief bullets.>

DETAILED INSTRUCTIONS:
Part A: <Description of part A>
1. File: <path/to/fileA>
   - Function/area: <functionName or line ref>
   - Changes:
     - <Step 1: exactly what to add/modify/delete>
     - <Step 2: code example or conditional to include>
   - Edge cases / safety:
     - <List checks, when to clear variables, concurrency notes>

Part B: <Description of part B>
1. File: <path/to/fileB>
   - Function/area: <functionName or utility>
   - Changes:
     - <Exact properties to add to returned objects / shape changes>
   - Backward compat:
     - <How to default undefined fields, etc.>

TESTING / VERIFICATION:
- <Unit tests to add or manual steps to validate>
- <Example inputs and expected outputs>

ASSUMPTIONS:
- <List any assumptions you made (versions, runtime env, expected existing APIs)>

FINAL DELIVERABLE:
- <Exactly what you want returned: updated file contents, diffs, tests, where to insert, or any sample output.>
```

---

## Minimal example (using placeholders)

```
TITLE: Add "X" flag propagation in game engine

GOAL:
- Backend should detect when a player enters X-state and broadcast that state.

CONTEXT:
- Game engine currently updates player hands and broadcasts general gameUpdate but lacks X-state info.

SCOPE / OBJECTIVE:
- Target files:
  - /game-logic/GameEngine.js
  - server.js
- High-level objective:
  - Detect X-state in GameEngine functions and include it in getRoomStateForClient.

DETAILED INSTRUCTIONS:
Part A: GameEngine.js
1. File: /game-logic/GameEngine.js
   - Function: playCard(playerId, card)
   - Changes:
     - After removing the card from the hand, add:
       if (newState.players[newState.currentPlayerIndex].hand.length === 1) {
         newState.xPlayerId = playerId;
       }
     - Before applying effects, add safe-clear logic:
       if (gameState.xPlayerId && gameState.xPlayerId !== playerId) {
         newState.xPlayerId = null;
       }
   - Also apply same clearing logic to drawCard, playDrawnCard, passDrawnCard.

Part B: server.js
1. File: server.js
   - Function: getRoomStateForClient(roomId, clientId)
   - Changes:
     - Ensure the returned state includes: unoPlayerId: gameState.unoPlayerId || null

TESTING / VERIFICATION:
- Unit test: simulate a player playing to 1 card -> expect newState.xPlayerId === playerId
- Simulate next player's action -> expect xPlayerId === null

ASSUMPTIONS:
- gameState and newState structures exist and follow current codebase conventions.

FINAL DELIVERABLE:
- Provide full updated contents of GameEngine.js and server.js.
```

---

## Quick checklist / best practices when authoring prompts of this style

* Always include **file paths** and **function names** (not just vague “update backend”).
* Add **exact code snippets** or exact condition checks you want inserted (copy/pasteable).
* State **edge cases** (nulls, clearing flags, concurrency).
* Specify **output format** you want returned (full files, diffs, or line-by-line patch).
* Include **tests or verification steps** so the implementer can validate changes.
* Add **assumptions** to avoid questions. If you prefer they make a safe guess, say so explicitly.
* If compatibility matters, say which branches or versions to target.
* Use numbered steps for sequences of changes — it prevents missed steps.

---

