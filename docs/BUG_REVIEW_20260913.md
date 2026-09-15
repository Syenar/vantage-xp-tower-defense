# Bug Review — 2026-09-13

## Fixed in this cycle

1. **Missing PWA/web packaging files** — `index.html` referenced a web manifest that did not exist. Added `manifest.webmanifest` and generated 192/512 launcher icons.
2. **Broken TypeScript/Vite project path** — `package.json` referenced a TypeScript/Vite build while `tsconfig.json` and `vite.config.ts` were absent. Added both.
3. **Broken Cordova sync path** — `tools/sync-cordova.mjs` was referenced but missing. Added deterministic `dist/ -> www/` sync with `cordova.js` and a local Cordova build marker.
4. **Obsolete verification documentation** — README named verifier files that did not exist. Added current build/runtime verifiers and corrected commands.
5. **Stale gameplay-test build** — rebuilt `Vantage_GAMEPLAY_TEST.html` from the latest standalone source and current assets.
6. **Landscape mobile control clipping** — Start Wave and top controls could extend outside common 844×390 landscape viewports. Added a compact <=1000 px header breakpoint.
7. **Landscape menu ergonomics** — core menu actions could require immediate scrolling on short landscape screens. Added a short-height layout that keeps Settings and the primary actions visible.
8. **Cordova configuration drift** — corrected the product name and enabled viewport scaling; removed the obsolete local access entry.
9. **Standalone external dependency** — the standalone build still linked the external PWA manifest. The builder now strips the manifest link so the playable HTML is genuinely self-contained.

## Runtime regression coverage

The permanent runtime verifier now checks:

- startup without page errors
- exactly 10 towers and 10 maps
- 31 waves on every map
- every tower attacks and gains XP
- checkpoint save/restore round trip
- selling removes tower projectiles, burns, and slows
- all 10 maps can run through wave 31 without a wave deadlock under the QA full-defense configuration

## Final clean passes

Three consecutive passes completed with no intervening code changes. Each pass ran TypeScript checking, static/package verification, map geometry validation, asset validation, headless-browser runtime tests, standalone rebuilding, dependency-free web building, Cordova synchronization, source parity, XML/manifest parsing, and standalone self-containment checks.

See `release-evidence/clean-passes-20260913/`.
