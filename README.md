# HoloNight icons

**Naming migration: `HoloNight` is now the light variant. Existing users wanting
the dark variant must select `HoloNight-Dark` in their desktop or shell settings.**

| Theme | Default appearance | Declared inheritance |
| --- | --- | --- |
| HoloNight | Light | `Papirus,breeze,hicolor` |
| HoloNight-Dark | Dark | `Papirus-Dark,Papirus,breeze-dark,hicolor` |

Both themes declare `FollowsColorScheme=true`. Semantic SVGs respond to palettes
in KDE-aware consumers and HoloNight's own Qt renderer. No KDE Frameworks library
is required. Desktop settings or external integration select the variant; this
repository has no automatic switcher. GTK symbolic recoloring and cross-desktop
automatic switching are outside its contract.

Install your distribution's Papirus, Breeze and hicolor icon theme packages to
supply inherited icons. Inheritance is recursive: the declared list is not a
globally flattened lookup order. `hicolor` stays last in each declaration.

```sh
task build          # build/HoloNight and build/HoloNight-Dark
task validate       # rebuild and validate source + both variants
task install:local  # install both, then select the desired variant
```

Build and installation use Python 3.10+ and its standard library. Task is a
convenience wrapper; `python3 scripts/build.py`, `python3 scripts/validate_icons.py`
and `sh scripts/install-local.sh` are equivalent entry points.

### System packaging

Package both variants and the immutable recoloring bundle into an unused staging root:

```sh
python3 scripts/stage.py --destdir /tmp/holonight-icons-package
```

This builds and validates the payload before staging `usr/share/icons/HoloNight`,
`usr/share/icons/HoloNight-Dark` and `usr/share/holonight-icons`. Existing payload
destinations and symlinked parent directories are rejected. Relative icon aliases
and licensing metadata are preserved. Packaging does not run cache tools, create
backups, change user settings or require privilege. The umbrella installer owns
deployment, dependency checks, icon caches, upgrade cleanup and uninstall.

The system bundle's `/usr/share/holonight-icons/scripts/recolor.py` command still
targets an existing user-local theme under XDG_DATA_HOME; it does not modify the
system themes. Install a user-local copy first if recoloring is desired.

### User-local installation

Installation stages and validates both variants under
`${XDG_DATA_HOME:-$HOME/.local/share}/icons` before replacement. Each previous pair
is retained in a unique `.holonight-backup-*` directory there; failed replacement
rolls back both themes. To recover, move the current theme aside and restore the
corresponding backup directory under its original theme name. Available GTK icon
cache and KDE service cache tools are refreshed without a distribution-specific
menu prefix. `--no-cache` is available for isolated installation tests.

Canonical artwork lives in `icons/<context>/<native-size>/`. A `symbolic/`
subdirectory preserves separate representations with the same lookup name.
The shared generator lists only populated directories, with full-color lookup
precedence retained. SVG size ranges describe scalability, not independently
authored small-size designs. The migration inventory records every former master
and alias. Generated themes carry licensing and attribution alongside the icons.

```sh
task validate:icons
task test
task test:render
task preview:icons
task verify
```

Rendering and previews require CMake, a C++17 compiler, Qt 6 Core/Gui/Svg development
packages and a sibling `holonight-qt` checkout. Set `HOLONIGHT_QT_SOURCE` to use a
checkout elsewhere. Tests compile its actual `src/icons/iconrenderer.cpp`; they
add no dependency to the installed icon themes or Shell. CI pins a known renderer
revision. `task verify` also requires REUSE (`reuse lint`).

Family contact sheets are generated under `build/previews/` on light and dark
backgrounds at 16, 22, 24 and 32 pixels, each at 1× and 2×. Read the
[design contract](docs/icon-design-rules.md) and [verification guide](docs/sdd/icon-theme-compliance/VERIFICATION.md)
for palette and visual-review limits.

First-party material is GPL-3.0-or-later. Papirus-derived artwork remains
GPL-3.0-only; see [third-party notices](THIRD_PARTY_NOTICES.md), `REUSE.toml` and
`LICENSES/`.

[Places](docs/places-design.md) provides fourteen types: Home, generic folder,
Downloads, Documents, Desktop, Pictures, Music, Videos, Projects, Templates,
Public, Recent, empty Trash and full Trash. Two real SVG master directories hold
24 px colorful regular and monochrome symbolic artwork, and 32 px detailed
colorful artwork. Declared relative directory aliases reuse these masters.
Restored historical lookup names and deferred names are recorded explicitly in
`metadata/places.json`; the original migration inventory remains preserved.
Previews include both backgrounds, small sizes and enlarged gradient review.

### On-demand folder recoloring

`HoloNight` ships holonight-light; `HoloNight-Dark` ships holonight-dark.
All fourteen regular types support on-demand recoloring at both master sizes
(28 templates).
Presets are `holonight-light`, `holonight-dark`, `holonight-day` and `holonight-storm`.
Day/Storm remain explicit compatibility choices. The JSON contract still requires
all six tokens, even when an individual template uses fewer of them. Runtime monochrome
and status icons continue to follow consumer palettes independently.

After `task install:local`, run the installed command (Python standard library only):

```sh
python3 "${XDG_DATA_HOME:-$HOME/.local/share}/holonight-icons/scripts/recolor.py" HoloNight --preset holonight-light
python3 "${XDG_DATA_HOME:-$HOME/.local/share}/holonight-icons/scripts/recolor.py" HoloNight-Dark --palette /path/to/tokens.json
```

The JSON object must contain exactly `background`, `surface`, `textPrimary`,
`accentCyan`, `accentBlue`, and `accentViolet`, each an opaque `#RRGGBB` string.
For example, the Light input is:

```json
{"background":"#e7eef5","surface":"#f1f5fa","textPrimary":"#1b2533","accentCyan":"#00a8d8","accentBlue":"#3e7bdb","accentViolet":"#7566d4"}
```

A future Settings integration can pass this resolved token subset without adding
new presets here. Changing a palette never automatically rewrites icons.

The command regenerates from the immutable template bundle, stages and validates
all outputs, and replaces only manifest-listed artwork in the existing user-local
target theme. It preserves unrelated files and refreshes available GTK/KDE cache
tools. `--no-cache` is for isolated tests. Symlinked output paths are rejected.
A shared installation lock serializes installation and recoloring. Previous SVGs
and recovery.json remain in the printed `.holonight-recolor-backup-*` directory
under the user icon directory; the recorded output paths can be copied back to
the recorded theme to restore it. Replacement/cache failures restore prior SVGs.
