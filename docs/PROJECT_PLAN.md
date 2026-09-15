# XP Tower Defense — Project Plan

## 1. Project Goal

Build a polished 2D tower-defense game for modern browsers using WebGPU, with Apache Cordova included from the start as the native packaging layer for Android and iOS. The defining mechanic is that placed towers improve from combat experience instead of being manually upgraded. The player chooses where and what to build, while each tower's battlefield history determines how powerful and specialized it becomes.

The system must be fully functional and balanceable, with tower power growth constrained so veteran towers feel meaningfully stronger without making new towers irrelevant or allowing runaway snowballing.

## 2. Core Game Loop

1. Player selects a map.
2. Player starts with a fixed amount of credits.
3. Enemies follow one or more defined lanes toward the base.
4. Player spends credits to place towers on legal build cells or free-placement zones.
5. Towers automatically acquire targets and attack.
6. Towers earn experience from finite enemy XP budgets; only the portion of enemy threat actually neutralized unlocks XP for contribution-based distribution.
7. Towers level automatically when experience thresholds are reached.
8. Each level grants small stat growth; milestone levels unlock major traits such as multishot, piercing, splash, status effects, targeting improvements, or range behavior.
9. Destroying enemies grants credits for additional towers.
10. Waves escalate in health, speed, armor, resistance, density, and composition.
11. Victory occurs after the final wave; defeat occurs when base health reaches zero.

## 3. Design Rule: No Traditional Upgrade Button

Placed towers cannot be upgraded by spending currency. Their combat performance is the only progression path.

Player agency comes from:
- tower choice
- placement
- targeting priority
- selling/rebuilding strategy
- choosing when to add fresh towers versus relying on veteran towers
- map control and synergy

A tower's progression is earned, not purchased.

## 4. Experience System

### Experience Sources

Use contribution-based experience rather than kill-only experience.

Canonical model:
- every enemy has a finite authored XP budget tied to threat,
- effective damage, useful control, and attributable support create contribution weights,
- overkill contributes nothing,
- healing and shield regeneration cannot mint fresh XP,
- support attribution redistributes the existing enemy budget rather than creating extra XP,
- the finishing tower receives only a small weighting bonus,
- damage-over-time remains owned by its source tower,
- eligible underleveled late-built towers earn a bounded catch-up multiplier only while actively contributing and only until they reach the expected level band.

This prevents kill stealing, partial-damage leak farming, regeneration farming, support double-dipping, and permanent late-game underleveling. Exact formulas and invariants are defined in `BALANCE_SPEC.md`.

### XP Curve

Tower levels: 1–15 for the initial release.

Suggested total XP curve:
- L2: 40
- L3: 90
- L4: 160
- L5: 260
- L6: 390
- L7: 550
- L8: 750
- L9: 990
- L10: 1,280
- L11: 1,620
- L12: 2,020
- L13: 2,490
- L14: 3,030
- L15: 3,650

Exact values remain data-driven and will be tuned through simulations.

### Minor Level Growth

Normal levels should grant approximately 3–6% effective power depending on tower role, split between:
- damage
- fire rate
- range
- projectile speed
- status potency
- status duration
- accuracy/turn speed if applicable

Avoid multiplying all stats at once.

### Milestone Levels

Major upgrades at levels 3, 5, 8, 11, and 15.

Examples:
- extra projectile
- piercing
- explosive impact
- chain target
- execution bonus
- status spread
- armor break
- critical chance
- target retargeting enhancement
- projectile split

Major upgrades are predefined per tower to keep balance understandable and prevent random progression from deciding matches.

Level changes are resolved at the end of a simulation tick. If one XP settlement crosses multiple thresholds, all crossed levels are applied in order with no XP loss, and the new stats begin on the next tick. Existing projectiles/effect snapshots are not retroactively strengthened unless that effect is explicitly authored as dynamic. At level 15, XP stops accumulating; a max-level tower's contribution share is not redistributed to other towers.

## 5. Balance Framework

### Baseline Metrics

Every tower is normalized around these metrics:
- DPS: sustained damage per second
- burst DPS
- damage per credit
- range coverage
- crowd control value
- effective targets hit per attack
- armor performance
- boss performance
- time to first meaningful milestone
- veteran scaling factor

### Power Budget

A level-1 tower should be fully useful.
A level-5 tower should feel clearly veteran.
A level-10 tower should be about 1.8–2.2x as effective as level 1 depending on role.
A level-15 tower should normally cap near 2.7–3.2x its level-1 effective combat value.

Milestone abilities are included in that power budget, not added on top of unconstrained stat growth.

### Anti-Snowball Rules

- XP is based mostly on contribution, not last-hit kills.
- Higher tower levels require increasingly more XP.
- Wave difficulty rises faster than one veteran tower can scale alone.
- Different enemy defenses force mixed tower compositions.
- Bosses and elites reduce single-strategy dominance.
- Towers cannot directly transfer XP.
- Selling a tower does not transfer its level to a replacement.

## 6. Economy

The economy has only two primary resources:
- Credits: global match currency for building towers.
- Tower XP: individual, non-transferable combat progression.

Standard-mode targets:
- starting credits: approximately 450, adjustable per map/difficulty,
- enemy defeat credits are global and independent of which tower lands the kill,
- leaked enemies grant no defeat reward,
- split/summoned enemy reward budgets are conserved,
- maps may use a modest authored wave-clear stipend,
- no passive interest for hoarding,
- sell refund: 70% of original build price,
- veteran level does not increase refund and XP never transfers.

Selling removes the tower and all of its owned projectiles, drones, damage-over-time, control, and support effects immediately so the player cannot fire, refund the tower, and retain its combat value. No currency can buy tower levels in the core mode.

## 7. Enemy System

Initial enemy archetypes:

1. Grunt — baseline health/speed.
2. Runner — low health, high speed.
3. Brute — high health, slow.
4. Armored — elevated percentage `armorResistance` against Kinetic/Explosive damage.
5. Swarm — many weak enemies packed tightly.
6. Regenerator — recovers health unless kept under pressure.
7. Shielded — regenerating outer shield with different resist profile.
8. Stealth — requires detection while cloaked, with multiple roster-accessible detection sources so it never creates a single mandatory tower.
9. Splitter — creates smaller enemies on death.
10. Boss — high health, resistance package, crowd-control resistance.

Later maps can combine lanes and spawn modifiers.

## 8. Wave Director

Waves are authored through data rather than hard-coded logic.

Each wave can define:
- enemy type
- count
- spawn interval
- spawn group
- lane
- health multiplier
- speed multiplier
- reward multiplier
- special modifier

Standard match cadence:
- the player places the opening defense and manually starts wave 1,
- after a cleared wave, an 8-second preparation countdown begins,
- the player may start the next wave early, but there is no early-start currency bonus in the initial mode,
- building, selling, and targeting changes are allowed during preparation and while a wave is active, but not while paused,
- only one authored wave is active at a time in the initial mode,
- a wave clears when all of its spawned enemies have been killed or have leaked/despawned through an authored terminal rule,
- the wave-clear stipend is paid once after resolution if the base is still alive,
- defeat resolves immediately when base lives reach zero,
- victory resolves when the final boss wave is fully resolved with base lives remaining.

Difficulty should be evaluated using an offline simulation harness so changes to tower stats can be tested against standardized waves.

## 9. Targeting

Each offensive tower supports selectable deterministic targeting priority:
- First — least remaining path distance to its own exit/base
- Last — greatest remaining path distance
- Strongest — highest current effective durability
- Weakest — lowest current effective durability
- Closest — shortest world-space distance to the tower

Some specialized towers may add:
- Highest armor
- Lowest health percentage
- Unaffected target

Stable entity ID resolves exact ties. Untargetable stealth units are excluded unless detected/revealed. Targeting can be changed by the player and is not considered a tower upgrade.

## 10. Maps

Initial release target: 10 maps.

Map progression should introduce mechanics gradually:
1. Single lane tutorial
2. Longer winding lane
3. Tight corners favoring area damage
4. Split lanes
5. Fast route / slow route
6. Limited build zones
7. Crossing lanes
8. Multiple entrances
9. Elite-heavy route
10. Final multi-lane challenge

Maps will be represented as JSON data and rendered by WebGPU. Enemy lanes are immutable authored paths; this is not a maze-building tower defense. Towers use free placement inside authored buildable areas with path/base/spawn clearance and tower-overlap checks. Crossing lanes are intentionally spatial: area attacks may affect both lanes when enemies are physically within the effect radius.

## 11. WebGPU + Cordova Technical Architecture

### Rendering

The browser build and Cordova builds use the same renderer and gameplay bundle. Cordova hosts that bundle inside the native platform WebView; it does not fork or replace the WebGPU renderer.

Use one WebGPU canvas for the game world, with normal HTML/CSS interface elements layered around/over it for the text-heavy HUD, build tray, menus, tooltips, and selected-tower panel. This keeps WebGPU responsible for the high-volume visual scene while preserving crisp text, keyboard focus, accessibility, and simpler responsive layout.

WebGPU world rendering layers:
1. map background
2. terrain/path
3. build zones
4. enemies
5. towers
6. projectiles/effects
7. health/status bars
8. selection/range/world-space overlays

Use batched textured quads for sprites and simple procedural geometry where practical. Gameplay uses fixed logical world coordinates independent of canvas pixels or device-pixel ratio. Resize/DPI changes only alter the camera transform and render resolution; they never change ranges, paths, collision, targeting, or placement legality.

### Simulation

Fixed timestep simulation, recommended 60 Hz.

Separate update and render loops:
- deterministic game-state tick
- interpolated rendering

Combat calculations remain on CPU for clarity and determinism. WebGPU handles rendering rather than prematurely moving game logic onto GPU compute. All random combat behavior uses a seeded simulation-owned pseudo-random number generator; rendering cannot consume gameplay randomness. Game speed changes the number of fixed 60 Hz simulation ticks processed, never combat math. Pause freezes simulation time and gameplay randomness; standard mode allows inspection while paused but disallows placement, selling, or targeting changes until resumed.

When the browser tab becomes hidden, the match automatically pauses rather than accumulating a large wall-clock backlog. Simulation ticks are never intentionally dropped to catch up; under load, gameplay slows in wall-clock time before simulation correctness is sacrificed. If the WebGPU device is lost, simulation pauses while rendering resources are recreated, then resumes from unchanged game state.

### Main Modules

- GameLoop
- Renderer
- AssetManager
- InputManager
- MapSystem
- PathSystem
- WaveSystem
- EnemySystem
- TowerSystem
- TargetingSystem
- ProjectileSystem
- DamageSystem
- StatusEffectSystem
- ExperienceSystem
- EconomySystem
- UI/HUD
- Save/Settings
- BalanceTelemetry
- SeededRng
- ContributionLedger
- PlatformRuntime / CordovaBridge
- StorageAdapter

### Cordova Packaging and Platform Boundary

Apache Cordova is a required packaging target from the foundation phase. Native builds use the exact same Vite output as the browser build:

1. `npm run build:web` produces `dist/`.
2. `npm run cordova:sync` regenerates Cordova's `www/` payload from `dist/` and injects the Cordova bridge.
3. `cordova prepare/build` generates native platform projects.
4. `www/` and `platforms/` are generated artifacts and are never authoritative source code.

Pinned baseline: Cordova CLI 13.0.0, cordova-android 15.0.0, and cordova-ios 8.1.1. The initial WebGPU-native support policy is Android 12/API 31+ with a current WebGPU-capable System WebView, and iOS/iPadOS 26+ for default `WKWebView` WebGPU availability. Unsupported devices show an explicit compatibility screen; the initial release does not silently fall back to WebGL.

All native behavior is isolated under `src/platform/`. Gameplay, towers, balance, simulation, maps, and rendering must never depend directly on Cordova globals/plugins. Cordova `deviceready`, pause/resume, Android back behavior, safe-area handling, and any future native plugins are routed through the platform adapter. Backgrounding always pauses simulation immediately and resuming never fast-forwards elapsed wall-clock time.

See `CORDOVA_PORTABILITY.md` for the complete native packaging contract.

## 12. Data-Driven Content

Keep towers, enemies, waves, maps, status effects, XP curves, and balance coefficients in TypeScript data definitions or JSON-like modules.

This lets balance changes happen without rewriting combat code.

## 13. User Interface

Responsive HTML/CSS HUD around the WebGPU world canvas. Desktop remains the primary tuning surface, but all controls are designed from the start for mouse and touch so the Cordova build does not require a second interface:
- top bar: lives, credits, wave, game speed
- bottom/side build tray: 10 towers with price and concise role
- selected tower panel: level, XP bar, current stats, milestone history, next milestone preview, targeting priority, sell
- no upgrade button
- range preview on hover/selection
- clear invalid placement feedback
- pause, 1x, 2x, 3x speed
- Pointer Events for mouse/touch/pen through one input path
- no required hover-only action
- safe-area-aware native HUD margins and large touch targets

The visual design should be clean, modern, legible, and uncluttered.

## 14. Experience Feedback

Tower progression must feel highly visible.

When a tower levels:
- short ring pulse
- level-up text
- brief stat-change indicator

At milestone levels:
- stronger visual effect
- milestone name
- ability description

The selected-tower panel always shows:
- current level
- XP / next XP
- current combat stats
- next milestone and level requirement

## 15. Audio

Initial audio set:
- tower placement
- tower sell
- 10 distinct attack families
- impacts/explosions
- enemy death variants
- level-up
- milestone unlock
- wave start
- boss alert
- victory/defeat

Audio can ship after core gameplay is stable.

## 16. Persistence

Initial release should save through a versioned storage adapter so browser local storage can later be replaced by a Cordova-native storage backend without touching gameplay systems:
- settings
- map completion
- best score/wave
- optional gameplay statistics

Individual tower XP resets between matches in the standard mode so each match has its own progression arc. Initial persistence uses versioned local browser storage for settings/completion/statistics; corrupt or older data must fail safely through schema defaults/migration rather than preventing game launch.

A persistent tower-progression mode can be added later, but should not complicate initial balance.

## 17. Testing Strategy

### Unit Tests
- XP thresholds
- damage math
- armor/resistance
- status stacking
- targeting priorities
- sell values
- wave spawning
- milestone unlocks

### Simulation Tests
Run thousands of seeded deterministic no-render simulations and enforce automated balance gates defined in `BALANCE_SPEC.md` to compare:
- cost efficiency
- tower solo performance
- mixed compositions
- early/mid/late wave survival
- armor counters
- swarm counters
- boss counters
- level progression speed
- XP-budget conservation / anti-farming
- support and status stacking abuse
- late-build viability
- identical outcomes at 1x/2x/3x speed

The balance harness uses two layers: isolated authored fixtures for tower-role measurements, and map-level build-search/scripted-agent runs for economy/opening validation. Balance candidates are tested over a fixed seed set plus randomized deterministic seeds; map validation must discover at least two materially different successful opening concepts rather than merely replaying one hand-authored solution.

### Browser Tests
- Chrome/Edge WebGPU
- resize behavior
- high-DPI rendering
- pointer placement
- pause/resume
- tab visibility changes
- lost WebGPU device recovery
- graceful unsupported-WebGPU message with no silent WebGL behavior change

### Cordova / Device Tests
- Cordova web payload is regenerated from the current Vite build
- Android debug package builds with pinned cordova-android
- Android physical-device WebGPU adapter/device creation
- Android touch placement, pause/resume, and back-button behavior
- iOS package builds with pinned cordova-ios on macOS/Xcode
- iPhone/iPad WebGPU startup on iOS/iPadOS 26+
- safe-area/notch layout and orientation
- background/foreground produces no simulation catch-up
- browser and native seeded simulation fixtures produce identical outcomes

## 18. Performance Targets

Primary performance target:
- 60 FPS normal play on desktop and supported modern mobile hardware
- at least 500 simultaneous moving combat entities (enemies + projectiles + drones) without visible hitching on a modern discrete GPU
- low draw-call count through batching
- pooled projectiles/effects where useful
- no allocations in hot combat loops where avoidable

## 19. Development Phases

### Phase 1 — Foundation
- Cordova project/configuration and browser/native platform adapter
- WebGPU initialization
- resize-safe canvas
- game loop
- sprite/quad rendering
- input
- simple debug map

### Phase 2 — Playable Combat
- path following
- enemy spawning
- one tower
- targeting
- projectiles
- damage
- lives/economy

### Phase 3 — XP Progression
- contribution tracking
- XP gain
- level curve
- stat growth
- milestone unlock system
- level-up UI/effects

### Phase 4 — Full Tower Roster
Implement all 10 towers and their progression trees.

### Phase 5 — Enemy Roster + Status System
Implement all core enemy archetypes, armor/resistance, crowd control, shields, regeneration, stealth, splitting.

### Phase 6 — Maps + Waves
Build 10 maps and full wave sets.

### Phase 7 — Balance Gauntlet
Automated simulation passes, human playtests, power-curve tuning, economy tuning.

### Phase 8 — Polish
UI, particles, animation, audio, accessibility, onboarding, settings.

### Phase 9 — Verification
Regression tests, multi-browser testing, Android/iOS Cordova build and physical-device validation, browser/native deterministic parity, performance profiling, clean build validation.

## 20. Rules That Must Be Resolved Before Content Lock

The following are now design requirements rather than deferred questions:

- Damage uses four readable attack tags (Kinetic, Explosive, Energy, Elemental) with bounded resistances.
- Ordinary enemies are never completely immune to an attack family.
- Slow, vulnerability, armor break, and hard-control stacking have global caps.
- Regeneration, shields, splitters, and summons obey finite XP-budget conservation.
- Leaked enemies award only the XP portion already unlocked by real threat reduction; partial damage cannot normalize into a full enemy budget.
- Late-build catch-up is per eligible underleveled tower, capped at 1.40x, and expires at the expected level floor or after five waves.
- Overlapping support auras use diminishing returns and cannot recursively amplify support towers.
- Stealth has three defined base-access routes: reduced-range Ranger detection, full-range Marksman detection, and Beacon aura reveal.
- Game-speed settings produce identical gameplay outcomes.
- Level growth is explicit per tower rather than one generic multiplier.
- Each map must pass with at least two materially different opening strategies.
- A specialist purchased in the final third with at least five normal waves remaining must be able to reach a useful early milestone if placed well and kept active.

## 21. Definition of Done

The initial game is complete when:
- all 10 towers are distinct and functional
- every tower levels through combat XP only
- every tower has multiple milestone abilities
- XP contribution logic conserves base enemy XP, handles leaks correctly, and is fair across damage/control/support roles
- no manual upgrade button exists
- enemy counters encourage mixed tower strategy without hard-locking a map behind one mandatory tower
- at least 10 maps are playable
- waves progress to a final victory condition
- economy, selling, deterministic multi-lane targeting, placement, stealth detection, pausing, speed controls, save data work
- automated balance gates pass and simulation shows no tower dominating the scenario suite
- WebGPU rendering is stable in supported browsers and supported Cordova WebViews
- Android and iOS Cordova packages are generated from the same Vite gameplay build without source forks
- native lifecycle/backgrounding cannot advance deterministic simulation
- automated tests pass
- the game can be run locally with a simple dev command, packaged for static hosting, and packaged through Cordova for Android/iOS
