# Umbrella packaging

Work package: III-001. Baseline: 7342a0947b960191b3e0c32cfd4f4c49ad2e973f.

## Contract

`python3 scripts/stage.py --destdir <absolute-root>` builds and validates both themes
and the immutable template bundle, then stages the three payloads below `usr/share`.
Theme names and locations are stable: `icons/HoloNight`, `icons/HoloNight-Dark`, and
`holonight-icons` for the shared bundle. Relative icon aliases and attribution are preserved.
Existing payload destinations, parent symlinks and paths containing `..` are rejected.
This entry point uses Python 3.10+ standard library only, with no caches, backups,
privileged commands or changes to user configuration. An installation failure removes
payloads already placed by this invocation; empty parent directories may remain.

## Implementation

`scripts/stage.py` reuses the canonical builder, theme validator and bundle inventory.
Bundle validation is shared with `scripts/install.py`; user-local installation behavior
is preserved. All copies are validated in a temporary directory on the destination
filesystem before placement. The umbrella owns deployment, cache generation, manifests,
safe obsolete-file cleanup and uninstall. Template recoloring continues to target only
explicitly requested user-local themes.

The license-check task generates its artifacts before checking them. Current Places
design/verification documentation describes the shipped masters and templates.

## Acceptance

- CLI packaging includes both valid variants, relative aliases and the exact bundle.
- Invalid artifacts and occupied or symlinked destinations cannot expose partial payloads.
- Placement failure rolls back this invocation's payloads.
- No user data, caches or installation backups are created by packaging.
- `task verify` passes with the umbrella-pinned Qt renderer and previews are inspected.

## Verification — 2026-09-24

Clean `task verify` passed: 39 Python tests, source and generated-theme validation,
206 rendered masters across 12 size/scale combinations and four palettes, all eleven
Places lookup sizes at 1x/2x, preview generation, and REUSE for source, both themes and
the bundle. The complete build log contained no actionable warnings. Renderer source:
umbrella-pinned holonight-qt 863af4183bdf09ce05199b37e8f5dfb46a311ba1 (Qt 6.11 toolchain).
Inspected generated regular/symbolic family overview sheets in both matching variants,
Home normal/selected/disabled sheets on both backgrounds at 16/22/24/32 px and 2x,
and enlarged Home gradients. Geometry is unclipped; small disabled regular rims remain
faint as already documented. No artwork was changed. `git diff --check` passed.
