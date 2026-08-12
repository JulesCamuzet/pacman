# Gameplay Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the ghost AI, level timer, victory screen, and forced non-perfect maze tickets in one gameplay branch.

**Architecture:** Keep `GameState` as the owner of time and shared ghost modes. Keep pathfinding in the base `Ghost` model, while each colored subclass supplies its chase target. Reuse the existing score-entry modal with an explicit outcome instead of duplicating its input loop.

**Tech Stack:** Python 3.13, Pydantic 2, Pygame, pytest, mypy, flake8.

## Global Constraints

- Work only on `feat/gameplay-completion`.
- Keep the implementation small and compatible with the existing generated maze graph.
- Always pass `perfect=False` to `mazegenerator`.
- Add behavior tests before production changes.
- Do not push the branch.

---

### Task 1: Force Non-perfect Mazes

**Files:**
- Modify: `pacman/config.py`
- Modify: `pacman/maze.py`
- Modify: `pacman/ui/pages/maze_generator.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_game.py`
- Modify: `tests/test_maze_generator_page.py`

**Interfaces:**
- Consumes: `LevelConfig(width: int, height: int, seed: int)`
- Produces: `PacmanMazeGenerator.generate_maze(level)` always constructs the external generator with `perfect=False`.

- [ ] Write tests proving an input `perfect: true` is ignored, the maze adapter receives `False`, and the menu generates immediately without a mode toggle.
- [ ] Run the focused tests and confirm they fail because `perfect` is still configurable.
- [ ] Remove `perfect` from `LevelConfig` and normalization, force the adapter argument, and simplify the menu to one action.
- [ ] Run the focused tests and confirm they pass.
- [ ] Commit with `fix: always generate non-perfect mazes`.

### Task 2: Add Balanced Classic Ghost Personalities

**Files:**
- Modify: `pacman/constants.py`
- Modify: `pacman/game/ghosts/ghost.py`
- Modify: `pacman/game/ghosts/red.py`
- Modify: `pacman/game/ghosts/pink.py`
- Modify: `pacman/game/ghosts/blue.py`
- Modify: `pacman/game/ghosts/orange.py`
- Modify: `pacman/game/state.py`
- Modify: `tests/test_ghosts.py`

**Interfaces:**
- Produces: `Ghost.get_chase_target(state) -> tuple[int, int]`
- Produces: `Ghost.get_target(state) -> tuple[int, int]`
- Produces: `GameState.update_ghost_mode(now: float) -> None`
- Produces: `GameState.reset_after_life_loss(now: float) -> None`

- [ ] Write focused tests for Red, Pink, Blue, and Orange targets, scatter mode, no voluntary reversal, frightened choices, schedule changes, reduced speed, and life reset.
- [ ] Run the focused tests and confirm missing modes and target methods fail.
- [ ] Add `SCATTER`, target selection, classic corner mappings, legal-direction filtering, the schedule, 75 percent speed, and life reset.
- [ ] Run the ghost tests and confirm they pass.
- [ ] Commit with `feat: add balanced classic ghost AI`.

### Task 3: Enforce and Display the Level Timer

**Files:**
- Modify: `pacman/game/state.py`
- Modify: `pacman/ui/pages/game/dashboard.py`
- Modify: `pacman/ui/pages/game/game.py`
- Create: `tests/test_level_timer.py`

**Interfaces:**
- Produces: `GameState.remaining_time: int`
- Produces: `GameState.pause_timer(duration: float) -> None`
- `GameState.update(now)` returns `UpdateResult.LOSE` when no time remains.

- [ ] Write tests for initial time, countdown, timeout, next-level reset, and paused time.
- [ ] Run the timer tests and confirm the missing fields and behavior fail.
- [ ] Store a deadline, update the integer countdown, move the deadline after pause, and render `Time: Ns` in the dashboard.
- [ ] Run the timer and dashboard tests and confirm they pass.
- [ ] Commit with `feat: limit each level duration`.

### Task 4: Split Victory and Defeat Messages

**Files:**
- Modify: `pacman/ui/pages/game/highscore.py`
- Modify: `pacman/ui/pages/game/game.py`
- Create: `tests/test_game_outcome.py`

**Interfaces:**
- Produces: `GameOutcome` with `VICTORY` and `DEFEAT`.
- `DisplayHighscoreModal.outcome` controls only the recap copy; score entry remains shared.

- [ ] Write a rendering test that captures the modal text for each outcome.
- [ ] Run it and confirm victory currently renders `Game Over`.
- [ ] Add the outcome enum and pass the correct result from `GamePage`.
- [ ] Run the outcome tests and confirm both messages pass.
- [ ] Commit with `feat: show a distinct victory screen`.

### Task 5: Full Regression Verification

**Files:**
- Modify only files required by an observed regression.

**Interfaces:**
- Consumes: all four completed tickets.
- Produces: a branch ready for user review, without a push.

- [ ] Run all focused gameplay tests.
- [ ] Run `make lint`.
- [ ] Run the complete test suite with a finite timeout and report any pre-existing blocking tests accurately.
- [ ] Run `git diff --check` and inspect `git status` and the final diff.
- [ ] Do not push.
