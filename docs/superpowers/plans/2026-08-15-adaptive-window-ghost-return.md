# Adaptive Window and Ghost Return Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the adaptive 1000×1500 interface and make active ghosts walk toward their corners for three seconds after Pacman loses a life.

**Architecture:** Shared display constants derive one uniform scale from the detected screen, so the window, fonts, content, and maze retain the same proportions. Life-loss handling reuses each ghost's existing `GOING_HOME` mode and shared BFS; coordinates are never assigned directly during that transition.

**Tech Stack:** Python 3.13, Pygame 2.6, Pydantic 2, pytest, flake8, mypy.

## Global Constraints

- Preserve the original 1000×1500 reference ratio and the 90% screen margin.
- Scale the window, shared fonts, content bounds, and `MAX_MAZE_SIZE` together.
- Keep the existing 3-second `GHOST_GOING_HOME_DURATION`.
- Do not change the `EATEN` ghost behavior.
- Do not change collision distance, scoring, lives, timers, cheats, or chase targets.
- Add regression tests before each production change.

---

### Task 1: Restore the adaptive display constants

**Files:**
- Modify: `tests/test_game_layout.py:1-52`
- Modify: `tests/test_game.py:295-323`
- Modify: `pacman/constants.py:7-46`

**Interfaces:**
- Consumes: `pygame.display.Info()` with `current_w: int` and `current_h: int`.
- Produces: `WINDOW_WIDTH`, `WINDOW_HEIGHT`, `CONTENT_START_X`, `CONTENT_END_X`, `CONTENT_START_Y`, `CONTENT_END_Y`, five `FONT_SIZE_*` constants, and `MAX_MAZE_SIZE` as scaled integers.

- [ ] **Step 1: Write the failing proportional-layout test**

Add the shared constants to the imports in `tests/test_game_layout.py` and add:

```python
def test_layout_uses_one_adaptive_1000_by_1500_scale() -> None:
    """Every shared layout value must follow the reference scale."""

    scale_x = WINDOW_WIDTH / 1000
    scale_y = WINDOW_HEIGHT / 1500
    font_scale = min(scale_x, scale_y)

    assert abs(scale_x - scale_y) < 0.002
    assert CONTENT_START_X == int(100 * scale_x)
    assert CONTENT_END_X == int(900 * scale_x)
    assert CONTENT_START_Y == int(300 * scale_y)
    assert CONTENT_END_Y == int(1400 * scale_y)
    assert FONT_SIZE_SMALL == max(1, int(14 * font_scale))
    assert FONT_SIZE_TEXT == max(1, int(18 * font_scale))
    assert FONT_SIZE_MEDIUM == max(1, int(24 * font_scale))
    assert FONT_SIZE_LARGE == max(1, int(32 * font_scale))
    assert FONT_SIZE_TITLE == max(1, int(36 * font_scale))
    assert MAX_MAZE_SIZE == int(800 * scale_x)
```

- [ ] **Step 2: Run the test and verify the fixed window fails it**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_game_layout.py::test_layout_uses_one_adaptive_1000_by_1500_scale -q
```

Expected: FAIL because `WINDOW_HEIGHT` is currently `900` while the unscaled
1000-pixel width implies the old 1500-pixel reference height.

- [ ] **Step 3: Restore the adaptive constants**

Replace the fixed window/layout block in `pacman/constants.py` with the former
screen fitting calculation:

```python
_BASE_WINDOW_WIDTH = 1000
_BASE_WINDOW_HEIGHT = 1500


def _compute_window_size() -> tuple[int, int]:
    """Fit the reference window inside 90% of the detected screen."""

    try:
        import pygame

        pygame.display.init()
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
    except Exception:
        return _BASE_WINDOW_WIDTH, _BASE_WINDOW_HEIGHT

    if screen_width <= 0 or screen_height <= 0:
        return _BASE_WINDOW_WIDTH, _BASE_WINDOW_HEIGHT

    scale = min(
        screen_width * 0.9 / _BASE_WINDOW_WIDTH,
        screen_height * 0.9 / _BASE_WINDOW_HEIGHT,
        1.0,
    )
    width = int(_BASE_WINDOW_WIDTH * scale)
    height = int(_BASE_WINDOW_HEIGHT * scale)
    return width, height


WINDOW_WIDTH, WINDOW_HEIGHT = _compute_window_size()
_SCALE_X = WINDOW_WIDTH / _BASE_WINDOW_WIDTH
_SCALE_Y = WINDOW_HEIGHT / _BASE_WINDOW_HEIGHT

CONTENT_START_X = int(100 * _SCALE_X)
CONTENT_END_X = int(900 * _SCALE_X)
CONTENT_START_Y = int(300 * _SCALE_Y)
CONTENT_END_Y = int(1400 * _SCALE_Y)

_FONT_SCALE = min(_SCALE_X, _SCALE_Y)
FONT_SIZE_SMALL = max(1, int(14 * _FONT_SCALE))
FONT_SIZE_TEXT = max(1, int(18 * _FONT_SCALE))
FONT_SIZE_MEDIUM = max(1, int(24 * _FONT_SCALE))
FONT_SIZE_LARGE = max(1, int(32 * _FONT_SCALE))
FONT_SIZE_TITLE = max(1, int(36 * _FONT_SCALE))
```

Set the maze constant to:

```python
MAX_MAZE_SIZE = int(800 * _SCALE_X)
```

- [ ] **Step 4: Make the UI-size test consume the adaptive values**

Rename `test_ui_requests_a_centered_fixed_window` to
`test_ui_requests_the_centered_adaptive_window`, update its docstring, and use:

```python
assert created_sizes == [(WINDOW_WIDTH, WINDOW_HEIGHT)]
```

Import `WINDOW_WIDTH` and `WINDOW_HEIGHT` from `pacman.constants` in
`tests/test_game.py`. Also create the layout-test surface with
`pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)` instead of a
literal width.

- [ ] **Step 5: Run the focused layout and UI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_game_layout.py tests/test_game.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit the adaptive display change**

```bash
git add pacman/constants.py tests/test_game_layout.py tests/test_game.py
git commit -m "fix: restore adaptive game window"
```

---

### Task 2: Return ghosts by BFS after a lost life

**Files:**
- Modify: `tests/test_ghosts.py:364-389`
- Modify: `pacman/game/state.py:318-328,461-510`

**Interfaces:**
- Consumes: `Ghost.send_home(now: float) -> None`, `Ghost.update(state: GameState, now: float | None = None) -> None`, and `GhostMode.GOING_HOME`.
- Produces: life-loss behavior that preserves ghost coordinates, sets every non-`EATEN` ghost to `GOING_HOME`, and lets those ghosts move while Pacman is dying.

- [ ] **Step 1: Replace the teleport expectation with a walking expectation**

In `test_normal_collision_removes_one_life_only`, keep the ghost stationary for
the collision and replace the position/mode assertions with:

```python
ghost = state.ghosts[0]
assert (ghost.x, ghost.y) == (15, 15)
assert_ghost_mode(ghost, GhostMode.GOING_HOME)
assert ghost.frightened_until == 13.0

ghost.speed = 1
distance_before = abs(ghost.x - ghost.start_x) + abs(
    ghost.y - ghost.start_y
)
assert state.update(now=10.1) == UpdateResult.CONTINUE
distance_after = abs(ghost.x - ghost.start_x) + abs(
    ghost.y - ghost.start_y
)
assert distance_after < distance_before
assert state.lives == 2
```

- [ ] **Step 2: Add a regression test for an already eaten ghost**

Add to `tests/test_ghosts.py`:

```python
def test_life_loss_does_not_reset_an_eaten_ghost() -> None:
    """An eaten ghost keeps its own delayed respawn state."""

    state = make_open_state()
    state.lives = 3
    state.pacman.x = 15
    state.pacman.y = 15
    state.pacman.speed = 0
    attacker = RedGhost(
        x=15,
        y=15,
        start_x=5,
        start_y=5,
        speed=0,
        mode=GhostMode.CHASE,
    )
    eaten = BlueGhost(
        x=25,
        y=25,
        start_x=5,
        start_y=25,
        speed=0,
    )
    eaten.be_eaten(now=8.0)
    state.ghosts = [attacker, eaten]

    state.update(now=10.0)

    assert_ghost_mode(attacker, GhostMode.GOING_HOME)
    assert_ghost_mode(eaten, GhostMode.EATEN)
    assert (eaten.x, eaten.y) == (25, 25)
    assert eaten.respawn_at == 13.0
```

- [ ] **Step 3: Run both tests and verify the teleporting code fails**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_ghosts.py::test_normal_collision_removes_one_life_only \
  tests/test_ghosts.py::test_life_loss_does_not_reset_an_eaten_ghost -q
```

Expected: FAIL because `reset_after_life_loss()` currently assigns every ghost
directly to `start_x` and `start_y`.

- [ ] **Step 4: Replace the teleport with `send_home`**

Remove `reset_after_life_loss()` and change the dangerous-collision branch in
`GameState.__resolve_ghost_collisions()` to:

```python
self.lives -= 1
self.pacman.is_dying = True
self.__reset_ghost_cycle(now)
for other_ghost in self.ghosts:
    if other_ghost.mode != GhostMode.EATEN:
        other_ghost.send_home(now)
if self.lives <= 0:
    return UpdateResult.LOSE
return UpdateResult.CONTINUE
```

- [ ] **Step 5: Allow only returning ghosts to move during death**

Replace the early death return in `GameState.update()` with:

```python
if self.pacman.is_dying:
    if not self.cheat_ghosts_frozen:
        for ghost in self.ghosts:
            if ghost.mode == GhostMode.GOING_HOME:
                ghost.update(self, current_time)
    return UpdateResult.CONTINUE
```

This keeps collision resolution disabled and leaves an `EATEN` ghost's delayed
respawn state untouched.

- [ ] **Step 6: Run the complete ghost test file**

Run:

```bash
.venv/bin/python -m pytest tests/test_ghosts.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit the ghost-return change**

```bash
git add pacman/game/state.py tests/test_ghosts.py
git commit -m "fix: make ghosts walk home after life loss"
```

---

### Task 3: Align documentation and validate the complete project

**Files:**
- Modify: `README.md`
- Modify: `docs/project-management/README.md`

**Interfaces:**
- Consumes: final adaptive constants and `GOING_HOME` life-loss behavior.
- Produces: user-facing documentation matching the tested implementation.

- [ ] **Step 1: Update the README behavior descriptions**

Replace the fixed-window statement with a description of the adaptive
1000×1500 reference. In the ghost AI and level-outcome sections, state that a
lost life sends every active ghost toward its corner by BFS for three seconds;
do not describe this as an immediate reset.

- [ ] **Step 2: Update project-management evidence**

In `docs/project-management/README.md`, change the window mitigation from a
fixed `1000×900` layout to proportional 1000×1500 scaling and record the
non-teleporting three-second BFS return in the completed work, decisions, and
acceptance criteria.

- [ ] **Step 3: Run all automated verification**

Run:

```bash
make test
make lint
make lint-strict
make config-check
make maze-check
git diff --check
```

Expected: every command exits with status 0.

- [ ] **Step 4: Build and smoke-test the package**

Run:

```bash
make package
```

Launch `dist/pac-man/pac-man` without arguments, verify it remains running and
that `README.txt`, `_internal/config.json`, and both assets are present.

- [ ] **Step 5: Commit documentation and verification evidence**

```bash
git add README.md docs/project-management/README.md
git commit -m "docs: describe adaptive layout and ghost return"
```
