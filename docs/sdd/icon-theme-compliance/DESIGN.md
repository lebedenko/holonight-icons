# Icon theme compliance design

## Validation

`scripts/validate_icons.py` uses Python's standard library for XML and manifest handling. It validates canvas
contracts, symbolic forbidden content and classes, editor metadata, exact exceptions, symlink containment, baseline
counts, and Inkscape-reported application/panel bounds. `scripts/icon-exceptions.json` is the only exception source.

## Preview pipeline

`scripts/generate_icon_previews.py` renders masters with Inkscape and composes stripped PNG contact sheets with
ImageMagick. Stable path sorting, fixed backgrounds, fixed tile geometry, and explicit render sizes keep output
reviewable. Application targets are 16, 24, 32, 48, 64, 128, and 256 px; symbolic targets are 16, 20, 22, 24, 28,
and 32 px. Panel and folder sheets cover their consumer scale.

## Artwork decisions

The folder family keeps its established filled geometry and gains only an explicit 24-unit viewport. The four
first-party tiles share one centered inset transform, preserving their silhouette and optical relationships. Kiro
keeps its official proportions and AWS VPN keeps the explicitly consumed 64-unit contract.

Insync uses one stable arc/device base with a lower-left marker region. Warning, offline, pause, success, and sync
states differ by shape, not color alone. Bluetooth artwork is unchanged. Teams is uniformly refit without changing
its mark. Symbolic masters retain upstream names and meanings; the compliance pass removes editor data and unused
semantic definitions while preserving their compact filled details.
