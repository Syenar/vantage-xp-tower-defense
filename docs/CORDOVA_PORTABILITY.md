# Cordova Portability Plan

## Goal

Keep one authoritative TypeScript/WebGPU game codebase while making Android and iOS packaging routine through Apache Cordova. Cordova is a native application shell and device bridge; it must not become a second gameplay implementation.

## Pinned Tooling Baseline

- Apache Cordova CLI: 13.0.0
- cordova-android: 15.0.0
- cordova-ios: 8.1.1
- Android application floor: Android 12 / API 31 for the initial WebGPU package
- Android target SDK: API 36
- iOS/iPadOS application floor: 26.0 for reliable default `WKWebView` WebGPU support

Platform versions are pinned so a clean checkout does not silently jump to a new native toolchain. Upgrade them deliberately after device regression testing.

## Source-of-Truth Rule

Never hand-edit generated files under `www/` or `platforms/`.

1. Source code lives in `src/`, `index.html`, assets, and data files.
2. `npm run build:web` creates `dist/`.
3. `npm run cordova:sync` recreates `www/` from `dist/` and injects `cordova.js`.
4. Cordova prepares/builds native projects from `www/`.
5. Native platform folders are disposable generated output.

This prevents browser and mobile editions from drifting apart.

## Runtime Boundary

All device-specific behavior goes behind `src/platform/`. Game systems must not directly call Cordova globals or plugins. The initial runtime layer owns:

- Cordova `deviceready` boot gating
- native pause/resume events
- Android back-button routing
- future haptics, filesystem, sharing, achievements, billing, and platform services

Browser builds use the same interface with browser-safe implementations.

## WebGPU Compatibility

Cordova embeds the web build in Android WebView or iOS `WKWebView`; it does not provide its own WebGPU implementation. Therefore startup always performs the normal WebGPU capability check before creating gameplay.

- Android requires a WebGPU-capable Chromium System WebView and supported GPU/driver.
- iOS/iPadOS native packaging targets version 26 or newer for default `WKWebView` WebGPU support.
- There is no silent WebGL fallback in the initial release.
- Capability failure must show a useful compatibility screen rather than crash or hang.

## Mobile UX Requirements

The web and Cordova builds share gameplay, but layout/input must be portable from the start:

- Pointer Events are authoritative so mouse, touch, and pen use the same placement path.
- No gameplay action may require hover.
- Touch targets should be at least 44 CSS pixels where practical.
- The game world may draw edge-to-edge; HUD panels respect CSS safe-area insets.
- Initial native orientation is landscape.
- Multi-touch gestures cannot accidentally place/sell towers.
- Backgrounding a Cordova app pauses deterministic simulation immediately.
- Resume never simulates elapsed real-world background time.
- Android back opens/closes menus or pauses before app exit.

## Persistence

Core saves continue through the versioned storage adapter. Initial Cordova builds may use WebView local storage because standard progress/settings are small, but gameplay code must call a storage abstraction so a Cordova filesystem/database plugin can replace it later without migration throughout the game.

## Build Verification Matrix

Every release candidate must pass:

- desktop browser WebGPU build
- Android Cordova debug build
- Android physical-device launch and WebGPU adapter creation
- Android pause/resume and back-button tests
- iOS Cordova build on macOS
- iPhone/iPad physical-device launch on iOS/iPadOS 26+
- iOS background/foreground lifecycle test
- safe-area/notch layout test
- touch placement, drag/cancel, targeting, sell confirmation, and speed controls
- deterministic simulation parity against browser fixtures

Native shell differences may change input/lifecycle presentation, never combat results.

## Future Portability

Adding a Cordova plugin must happen only through the platform adapter. Plugins are selected for a concrete need and pinned by version. The initial game does not require network connectivity or native plugins to run, keeping Android/iOS packaging as thin as possible.
