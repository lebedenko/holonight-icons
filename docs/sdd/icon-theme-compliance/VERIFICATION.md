# Verification

Run `task verify` from the repository root. Python tests require only the standard
library. Rendering requires Qt 6 Core/Gui/Svg development files, CMake, C++17 and a
holonight-qt checkout (`HOLONIGHT_QT_SOURCE`, default sibling). REUSE is required for
licensing checks. No KDE Frameworks packages are required.

The regression fixtures cover stylesheet IDs/roles, hard-coded and implicit paints,
inline overrides, inherited group styling, fixed/mixed exemptions, missing classes,
broken/escaping/cyclic aliases, invalid metadata and duplicate-name precedence.
Build comparison detects artwork changes outside semantic stylesheet defaults.
Installation is exercised twice using temporary XDG data directories; tests retain
a marker in a recoverable backup, reject an invalid stage, and inject a replacement
failure to check rollback of both variants.

The C++ test compiles the real holonight-qt renderer. All generated masters are
rendered at 16/22/24/32 logical pixels, 1× and 2×, with light, dark, selected and
disabled foreground colors. It checks visible output, responsive color changes,
unchanged fixed artwork, status role colors, Qt theme lookup and temporary-fixture name precedence.
Selected/disabled inputs are resolved test colors, not simulated Shell UI states.
The renderer currently supports five roles; background and selection-text defaults
are reserved. CI pins renderer revision `27970cfe3ed3dc8bf0585dfee7927eae697979ac`.

Current previews are generated under `build/previews/HoloNight{,-Dark}/` as PNG
family sheets. Review at 100% scale on both backgrounds: fine geometry and text-free
silhouettes must stay clear. Pixel assertions prove recoloring, not aesthetic
quality or contrast in every application. Review actual Shell selection/disabled
behavior when changing artwork or consumer palette integration.

The old `previews/before` and `previews/after` images here are historical migration
artifacts, not current generated output or evidence for this implementation.

## Places artwork and system packaging

Follow [the Places acceptance criteria](../../places-design.md). Validate the two
real masters, nine exact relative directory links and all eleven advertised sizes,
including Scale=2 entries and temporary-XDG installation. Missing masters, wrong
links and undeclared directories must fail. Historical migration inventory remains
unchanged; restored aliases and deferred names follow the explicit Places dispositions.
The fourteen types include regular 24/32 px masters, monochrome symbolic artwork and
28 regular token templates. Temporary fixtures test Qt lookup at every display size
and 2× DPR, symbolic reuse and name precedence. Review current Places previews on both
backgrounds, including enlarged gradient sheets.

System packaging tests invoke `scripts/stage.py --destdir` in disposable roots, verify
both themes and the single shared bundle, reject occupied/symlinked destinations and
invalid artifacts, and check rollback and absence of host cache/user-install effects.
