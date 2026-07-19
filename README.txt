TERMINAL BLOCKAGE
=================

A falling-block roguelike presented as a surreal early-1990s computer game.
Clear lines to damage enemies, collect temporary upgrades, and survive an
escalating ten-floor campaign split into two five-encounter cycles.


PLAYABLE BUILD
--------------

Open dist/index.html in a modern desktop browser.

The distributable is a single self-contained HTML file with the JavaScript,
CSS, fonts, audio, and artwork embedded. The source files are not required to
play the built version.


GAMEPLAY
--------

- Lock tetrominoes and clear lines to damage the current foe.
- Enemy attacks use a shared countdown, windup, impact, and result language.
- Build Fury through active play to trigger a temporary Overdrive state.
- Earn experience and choose blessings during the post-fight sequence.
- Every defeated foe awards 5 fragments for the current run.
- Spend fragments at the Upgrade Terminal to raise damage or armor. Each
  purchase increases the price of that upgrade.
- Extract an artifact after normal fights or an Impossible Relic after bosses.
- Unspent fragments are lost when the run ends. Best Floor is the persistent
  record.


SPECIAL PIECES
--------------

Bomb
  Appears after roughly 7-8 pieces and may be held. Locking it clears the
  bottom three rows and deals double damage to the enemy.

Sealed Tetromino
  A rare non-O tetromino that cannot be rotated.

Impossible Piece
  An irregular piece created by The Monument. It can be rotated but is more
  difficult to place than a standard tetromino.

Ghost Tetromino
  An outlined false piece injected by Silicon Cortex. It moves, rotates,
  collides, and may be held normally, but dissipates on landing without locking
  or clearing lines. Disposing of it still advances the enemy attack clock.


ENEMY ROUTE
-----------

Cycle I ends at The Monument. Cycle II rearranges the returning foes, adds a
hardened elite, and ends at Silicon Cortex. The campaign repeats with continued
floor scaling after floor 10. Each boss also changes the playfield atmosphere.

Chrome Strider
  Uses Orbital Strike to deal direct HP damage.

Memory Pool
  Adds liquid-memory garbage. Clearing lines while it is alive causes feedback
  damage to the player.

Chaos Jester
  Obscures the next-piece and Hold displays with animated static. Grand Shuffle
  scrambles the stack and deals chaos damage.

Elite Encounter
  A returning enemy with either an accelerated attack clock or a hardened HP
  shell, depending on its campaign position.

The Monument
  A route boss that alternates between raising garbage walls and dealing heavy
  damage while throwing an irregular Impossible Piece.

Silicon Cortex
  The Cycle II boss. Null Geometry visibly constructs one Ghost Tetromino in
  the queue.


IMPOSSIBLE RELICS
-----------------

Open Window
  Reveals a second upcoming piece.

Empty Frame
  Adds a second Hold slot. Press C to cycle stored pieces.

Short Fuse
  Bombs arrive 1-2 pieces sooner, but the normal floor-based falling-speed
  acceleration is doubled.


CONTROLS
--------

Left / Right       Move
Down               Soft drop
Space              Hard drop
Up or X            Rotate clockwise
Z                   Rotate counterclockwise
C                   Hold or cycle stored pieces
P                   Pause / resume
F2                  Open / close the development debug terminal


DEBUG TERMINAL
--------------

Press F2 to pause the run and open the development terminal. It can jump to a
specific floor or encounter, trigger enemy attacks, alter player and foe state,
force special pieces, prepare a danger stack, and grant blessings or relics.
Closing it restores the pause state that was active before it opened.


SOURCE TREE
-----------

src/index.html             Page structure
src/css/style.css          Layout, presentation, and interface animation
src/js/game.js             Gameplay, rendering, audio, and game state
src/assets/                Fonts, audio, portraits, and sprite atlases
tools/build.py             Creates the standalone distributable
tools/build_enemy_rigs.py  Rebuilds the animated foe atlases
tools/build_strider_rig.py Rebuilds the Chrome Strider atlas
dist/index.html            Generated standalone build


DEVELOPMENT
-----------

JavaScript syntax check:

  node --check src/js/game.js

Build the standalone version:

  .venv/bin/python tools/build.py

If the virtual environment is unavailable, the build script only uses the
Python standard library and can also be run with:

  python3 tools/build.py

Treat src/ as the source of truth. Do not edit dist/index.html directly.


REPOSITORY
----------

https://github.com/Rishik28/terminal-blockage
