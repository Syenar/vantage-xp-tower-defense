# Project State — Vantage XP Tower Defense

## Implementation Complete

- Full standalone game entry point in `index.html` and `play.html`
- WebGPU-first renderer with Canvas 2D fallback
- Hybrid sprite layer using generated tower/enemy art
- Generated artwork integrated for all 10 maps
- 10 towers, 15 levels each, 5 milestones each
- 10 enemies and 31 waves on every map
- deterministic combat, projectiles, splash, piercing, chaining, critical hits, burn, slow/freeze, shields, regeneration, stealth/detection, splitter children, support auras, support XP, targeting priorities, selling, economy, victory/defeat
- Complete main menu: Continue, New Defense, How to Play, Settings
- Complete map selection with Easy/Normal/Hard
- Persistent checkpoint save and map completion tracking
- Pause, restart, save-and-exit, result/replay flows
- Persistent audio, graphics, accessibility, gameplay, fullscreen, and progress-reset settings
- synthesized UI/SFX and optional ambient music
- mouse, touch/pointer, keyboard, visibility pause, and Cordova native lifecycle hooks
- PWA manifest and generated launcher/favicon assets
- Vite configuration and Cordova packaging pipeline repaired
- dependency-free standalone production build available for verification

## Verification Status

- JavaScript syntax: PASS
- TypeScript static check: PASS using globally available TypeScript 5.8.3
- Static/content/package verification: PASS
- Runtime simulation gauntlet: PASS — all 10 maps reach wave 31/victory in QA execution
- XP progression during runtime gauntlet: PASS
- deterministic replay sanity: PASS
- checkpoint save/restore round trip: PASS
- standalone production bundle: PASS
- Cordova `www/` synchronization/static bridge check: PASS
- prior balanced normal-strategy evidence: 10/10 maps complete with 14–16 towers

## External Release Gates

The canonical Vite package build cannot be executed in this container because `npm install` repeatedly times out while restoring dependencies. GPU-backed browser automation is additionally blocked by the environment's managed Chromium URL policy, so an interactive WebGPU hardware smoke test cannot be executed here. Android native compilation requires the Android SDK/JDK environment; iOS native compilation requires macOS/Xcode. These limitations are documented rather than reported as passed.

## 2026-09-13 Bug Review Pass

Fixed during the latest clean-pass review:

- restored missing web/PWA packaging pieces (`manifest.webmanifest`, 192/512 icons)
- added missing `tsconfig.json` and `vite.config.ts`
- added the missing Cordova sync implementation and dependency-free static web build
- added permanent build/runtime verifiers that match the files actually in the repository
- corrected Cordova product name and viewport preference
- rebuilt the self-contained playable and immediate gameplay-test HTML from current source
- fixed common landscape-phone clipping of Start Wave/top controls
- compacted the landscape main menu so Settings and the core actions are immediately reachable
- verified exact checkpoint round-trip and active-effect/projectile cleanup on sell
- verified every tower can attack and gain XP in the runtime harness
- verified all 10 maps can execute all 31 waves without a wave deadlock under the QA defense configuration

## 2026-09-14 Arc + Hive Clean Review

- Arc now uses the authored lightning VFX atlas as its primary shot effect, with true target-to-target chaining and a level-8+ fork topology.
- Hive now uses visible autonomous orbiting drones instead of generic multishot. Drone milestones are 1 -> 2 -> 3 permanent channels, level-8 Hunter Logic retargets independently, and level-15 Swarm Protocol is a separate bounded burst.
- Hive total firing cadence now matches the authored total `fireRate` rather than multiplying that value once per drone.
- Idle cooldown banking is prevented for Hive drone channels and Swarm Protocol.
- Three consecutive focused clean passes are recorded under `release-evidence/arc-hive-clean-passes/`.

## 2026-09-15 Roster Uniqueness + Camera + Map Geometry Review

- Ranger L11 is now **Adaptive Rounds**: full stealth detection plus bounded target-specific ammunition behavior for armor, speed, and stealth. L15 **Combat Mastery** enhances every fifth primary attack instead of being another generic critical-stat milestone.
- Hive L5 **Faster Recall** is now a literal drone mechanic: losing a live target triggers immediate reacquisition and refunds 65% of the remaining channel cooldown.
- Railgun L15 **Hypervelocity** now lets enemies killed by the beam stop consuming pierce capacity, making the capstone mechanically transformative.
- Tower inspection now shows the full accumulated milestone history plus the next milestone instead of only the most recent unlock.
- Stealth enemy inspection explicitly names the counters: Marksman, Ranger, and Beacon reveal.
- Added bounded 1×–3× strategy camera with cursor-centered wheel zoom, pinch zoom, mouse/touch drag pan, WASD/arrow pan, +/− zoom, Home reset, and on-screen controls. World-to-screen conversion is shared by map art, towers, enemies, projectiles, ranges, pads, selection and placement.
- Camera pointer capture is hardened for browser/WebView pointer-state differences and pan gestures cannot accidentally place towers.
- Full tower audit: **168/168 PASS**. Camera/input audit: **18/18 PASS**.
- All 10 current map overlays were regenerated from runtime geometry and visually re-reviewed against the authored roads. Enemy route centerlines are aligned. A real Convergence build-pad mismatch was found and corrected; the regenerated geometry/manifests now match the painted pads.
- `tools/validate_geometry.py` now cross-checks live HTML geometry, both map manifests, actual PNG dimensions, source parity, and camera/map-art transform requirements.
- Canonical `npm run build:web` remains an environment gate in this container because the local Vite dependency is absent and npm restoration attempts time out. Dependency-free static build, standalone build, TypeScript checking, runtime tests, and Cordova web synchronization remain available and are not substituted for that canonical Vite gate.

