# Project Documentation Design

## Goal

Replace the outdated root README and project-management document with an
accurate record of the two-person Pac-Man project that satisfies the subject's
documentation requirements.

## README

The root `README.md` will be written entirely in English. Its first line will
be italicized and will identify the two 42 logins `allasser` and `jcamuzet`.
It will contain the mandatory Description, Instructions, Resources,
Configuration, Highscore, Maze Generation, Implementation, General Software
Architecture, and Project Management sections.

The README will describe only behavior present in the repository. It will
explain installation through the Makefile, the JSON configuration contract,
the Pydantic validation layer, the assigned A-Maze-ing wheel, the game loop,
the four ghost personalities, the timer, the UI modules, testing commands,
known remaining mandatory work, and the team's use of AI. It will link to the
dedicated project-management directory.

## Project Management Document

`docs/project-management/README.md` will remain in French so both developers
can maintain it easily. It will be rebuilt from the repository history and
the user's confirmed division of work:

- Alexis (`allasser`) created the initial structure, configuration, JSON
  parsing, Pydantic validation, maze-generator adaptation and data extraction,
  then implemented the ghosts and their AI.
- Jules (`jcamuzet`) implemented the Pygame graphical layer, maze rendering,
  Pac-Man, sprites, menus, HUD, controls, animation and visual integration.
- Both developers integrate the two layers and fix the final bugs together.

The document will contain a team organization section, responsibility matrix,
planned-versus-actual timeline, current Kanban, progress log, technical
choices, risk register, blocking points and resolutions, acceptance-test plan,
Git workflow, and Definition of Done. Finished, partial and remaining items
will be distinguished explicitly instead of presenting planned work as done.

## Accuracy and Safety

Repository files, current tests and Git history are the evidence sources.
Unverified publication, packaging, cheat mode or highscore integration will be
marked as remaining work. Existing local changes in `TODO` and
`data/scores.json` will not be edited or included in documentation commits.

## Validation

The final check will verify the README's exact first line, all mandatory
headings, the project-management link, valid relative file links, Markdown
structure, `git diff --check`, and that `make test` and `make lint` still pass.
