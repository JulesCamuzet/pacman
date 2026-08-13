# Final Project Documentation Implementation Plan

> **For the project team:** Execute this plan on `feat/gameplay-completion` and keep unrelated local changes untouched.

**Goal:** Replace the outdated project documentation with an accurate README and project-management record that satisfy the mandatory subject requirements.

**Documentation structure:** The root README is the public entry point for installation, configuration, architecture, resources, and current status. `docs/project-management/README.md` is the detailed evidence of planning, ownership, progress, risks, decisions, acceptance testing, and remaining work.

**Project stack:** Markdown, Git, Python 3.13, Pygame, Pydantic, pytest, flake8, mypy.

---

### Task 1: Rewrite the project-management record

**Files:**
- Modify: `docs/project-management/README.md`

1. Replace the obsolete forecast with the actual team organization and division of work.
2. Record the planned-versus-actual timeline and dated development history.
3. Add the current Kanban, decisions, risks, blockers, acceptance-test evidence, and Definition of Done.
4. Identify unfinished mandatory work honestly instead of presenting it as complete.

### Task 2: Rewrite the root README

**Files:**
- Modify: `README.md`

1. Add the exact mandatory 42 attribution as the first line using the confirmed logins `allasser` and `jcamuzet`.
2. Document installation, execution, controls, tests, and useful Make targets.
3. Explain configuration, highscore storage, maze generation, implementation, and architecture from the current code.
4. Add project-management ownership, technical resources, AI usage, and known remaining work.

### Task 3: Verify and commit documentation only

**Files:**
- Verify: `README.md`
- Verify: `docs/project-management/README.md`

1. Check mandatory headings, attribution, logins, links, and ownership wording.
2. Run the project test and lint commands to ensure documentation work did not disturb the codebase.
3. Review `git diff --check` and the final diff.
4. Commit only the two documentation files and this implementation plan; do not stage `TODO` or `data/scores.json`.
