# Map Path and Build-Pad Review — 2026-09-15

## Scope

All ten authored battlefield images were re-reviewed against the exact `MAP_GEOMETRY` used by the live runtime. The overlays in this directory were regenerated from the current geometry rather than copied from older evidence.

The review covers both:

- enemy route centerlines versus the painted road network; and
- tower build-pad coordinates versus the painted circular build locations.

## Result

**PASS — no remaining known route-centerline or build-pad/artwork mismatch.**

The current authoritative geometry is synchronized across:

- `index.html` / `play.html` (`MAP_GEOMETRY`)
- `release-evidence/manifests/map-geometry.json`
- `release-evidence/manifests/map-manifest.json`
- the actual 1672×941 map PNG dimensions

`tools/validate_geometry.py` now fails if those sources drift apart, if `index.html` and `play.html` disagree, or if the runtime map/camera transform stops using the exact stretched world plane required by the authored geometry.

## Per-map visual review

| Map | Routes | Pads | Review result |
| --- | ---: | ---: | --- |
| Meadow Circuit | 2 | 13 | PASS — both loop routes remain centered on the painted upper/lower road network. |
| Switchback | 2 | 13 | PASS — both winding routes follow the painted switchback corridors. |
| Crucible Bend | 2 | 14 | PASS — upper/lower routes track the road around the central crucible. |
| Twin Fork | 3 | 13 | PASS — all three lanes converge through the painted central roundabout correctly. |
| Velocity Divide | 2 | 14 | PASS — upper/lower routes track the divided road network. |
| Build Islands | 1 | 13 | PASS — the single winding route follows the painted island roadway. |
| Crossing Fire | 2 | 13 | PASS — horizontal/vertical crossing topology matches the artwork. |
| Convergence | 3 | 13 | PASS after correction — all three routes converge through the central road; the stale grass build pad was replaced with the omitted painted upper-left pad. |
| Elite Bastion | 2 | 14 | PASS — upper/lower routes correctly wrap the bastion. |
| Nexus Siege | 3 | 16 | PASS — all three routes converge on the painted nexus approach. |

## Corrected finding

During this review, **Convergence** contained one real build-pad/art mismatch: a runtime pad sat on grass while a visible authored pad in the upper-left was absent from geometry. The runtime geometry and both manifests were corrected and the overlays were regenerated afterward. Because that was a production geometry change, the final clean-pass count was reset.

## Evidence

- `all_maps_overlay_contact_sheet.jpg` — current all-map route/pad review sheet
- `<map>_overlay.png` — current per-map overlays
- `tools/render_map_path_overlays.py` — overlay generator
- `tools/validate_geometry.py` — synchronization and geometry validator

The route artwork review is visual evidence; the validator separately proves the runtime, manifests, image dimensions, and camera/map transform remain synchronized.
