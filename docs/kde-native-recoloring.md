# Native KDE recoloring test

Run `task test:kde`. This optional task requires CMake, a C++23 compiler,
Qt 6.6+ (Core, Gui and Svg), and KDE Frameworks 6 IconThemes development files.
On Arch Linux the KDE dependency is `kiconthemes`. A version that understands
`ColorScheme-Accent` is required for the role checks to pass; the test records
its actual Qt and IconThemes versions rather than assuming Accent support.

The default input is the Papirus-derived XML prototype at
`tests/kde/application-xml.svg`. To test the working root prototype instead:

```sh
task test:kde -- application-xml.svg
```

The input must retain the prototype's Text paper and Accent glyph structure.
This is a focused recoloring test, not a validator for arbitrary artwork.
24 px output scales the supplied 32 px master; it does not test a separate
24 px optical master.

The runner creates a disposable icon theme with `FollowsColorScheme=true`,
configuration, data and cache directories. It invokes `KIconLoader` directly,
offscreen, without HoloNight's renderer or a Plasma platform plugin. It does
not install a theme or change the desktop configuration. The test remains
separate from `task verify`, so the existing workflow does not require KDE.

## Checks and output

- Independent Text, Highlight and Accent colors (magenta Accent, green Highlight).
- Light/dark palettes, normal/selected/disabled states, 24/32 px, 1x/2x.
- Selected Text and Highlight mapping, with Accent distinct from paper.
- Fixed translucent black/white shading and unchanged normal-state geometry/opacity.
- An SVG without the recognized stylesheet ID as a negative control.
- Resolution from the isolated theme, and physical output dimensions.
- Accent-only palette changes using the same loader and icon name, compared
  with a separate uncached icon name.

Results appear under `build/kde/results/`:

- `comparison.png`: six rows of native renders, plus enlarged samples.
- `report.txt`: versions, input path, assertions and overall result.
- Individual PNGs for each palette/state/size/scale combination.

The sheet and report are retained if the final palette-cache check fails.
A failure still returns a nonzero exit code; it is not silently skipped.
Earlier assertion failures print a diagnostic and do not publish a success
report. A new run removes the previous comparison and report first.

## Observed result: IconThemes 6.30.0 / Qt 6.11.2

The prototype passes the native recoloring and selected/disabled rendering
checks. Changing only `QPalette::Accent` via `setCustomPalette()` on the same
loader returns the previous Accent for an already loaded icon name. An uncached
icon name renders the new Accent correctly in the same loader. The test
reports this as a native palette-cache refresh failure. This concerns the
isolated API path; it does not establish whether Plasma's broader settings
change notifications and cache invalidation reproduce the issue in Dolphin.

A separate interactive check in Plasma/Dolphin is still needed to establish
live desktop palette propagation, application caching and visual contrast
with real user-selected color schemes. The synthetic palettes make role
mapping obvious; they are not a contrast guarantee for arbitrary palettes.
