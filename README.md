# Vantage: XP Tower Defense

Play the current build: https://syenar.github.io/vantage-xp-tower-defense/

A complete standalone 2D tower-defense game built around experience-driven tower progression. Towers never use a manual upgrade button: they earn finite contribution-based experience from combat and automatically advance through 15 levels with major milestone abilities at levels 3, 5, 8, 11, and 15.

## Game Content

- 10 mechanically distinct towers: Ranger, Repeater, Cannon, Railgun, Frost, Ember, Arc, Marksman, Hive, and Beacon
- 10 authored maps with generated map artwork
- 31 waves per map including boss waves
- Easy, Normal, and Hard difficulties
- 10 enemy archetypes including armor, shields, regeneration, stealth, splitters, swarms, elites, and bosses
- first/last/strongest/weakest/closest targeting priorities
- deterministic fixed-step simulation and seeded combat randomness
- contribution-aware XP, support XP, status effects, splash, pierce, chains, burn, freeze/slow, critical hits, detection, and support auras
- checkpoint saves, completion tracking, pause/restart, victory/defeat results, and persistent settings
- strategy-game camera: cursor-centered wheel zoom, pinch zoom, mouse/touch drag pan, WASD/arrow-key pan, +/− zoom, Home reset, bounded 1×–3× view
- explicit stealth-counter guidance: Marksman detection, Ranger detection/Adaptive Rounds, and Beacon reveal

## Presentation

The full generated asset library is integrated into the game shell: map art, tower and enemy sprites, title splash, tower cards, map selection, tutorial art, result art, branding, and battlefield overlays. WebGPU is the primary world renderer and a transparent 2D sprite layer displays generated tower/enemy art. A Canvas 2D fallback keeps the game playable on environments where WebGPU cannot initialize.

## Main Menu & Settings

The main menu contains Continue Defense, New Defense, How to Play, and Settings. The map screen supports all 10 battlefields and all three difficulties. Settings persist automatically and cover sound effects, ambient music, master/effects/music volume, reduced motion, high contrast, always-show-ranges, rendering quality, background auto-pause, sell confirmation, fullscreen, and progress reset.

## Running

Open `index.html` or `play.html` directly in a modern browser. `index.html` is the canonical web/native entry point.

For development with the pinned toolchain:

- `npm run build:web` — canonical TypeScript + Vite production build (requires restored npm dependencies)
- `python tools/build_standalone.py` — builds the self-contained `Vantage_XP_Tower_Defense_PLAYABLE.html`
- `python tools/build_static.py` — dependency-free static web build to `dist/`
- `node tools/sync-cordova.mjs` — synchronizes the already-built web assets into Cordova `www/`
- `npm run cordova:build:android` — Android native package (requires Android SDK/JDK)
- `npm run cordova:build:ios` — iOS native package (requires macOS/Xcode)

In the current verification container, TypeScript/static/standalone/Cordova-web synchronization are testable, but npm dependency restoration for the canonical Vite command times out. That gate is reported as unverified rather than treated as a pass.

## Verification

- `python tools/verify_build.py` checks syntax, geometry, asset wiring, packaging files, web-manifest files, and required graphics.
- `python tools/verify_runtime.py` uses a headless browser (when Python Playwright is available) to exercise all 10 towers, save/restore, sell cleanup, and all 10 maps through wave 31.
- Evidence is recorded under `release-evidence/` and summarized in `COMPLETION_EVIDENCE.md`.
