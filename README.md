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
repository has no automatic switcher. Explicit Places, Devices and navigation `-symbolic`
names recolor from the GTK foreground color in GTK 3 and GTK 4. The
[size-aware contract](docs/sdd/size-aware-icons/README.md) defines their lookup
and the separate ordinary-name artwork behavior. Cross-desktop automatic
switching is outside this repository's contract.

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
task test:gtk
task preview:icons
task verify
```

Rendering and previews require CMake, a C++23 compiler, Qt 6 Core/Gui/Svg development
packages and a sibling `holonight-qt` checkout. Set `HOLONIGHT_QT_SOURCE` to use a
checkout elsewhere. Tests compile its actual `src/icons/iconrenderer.cpp`; they
add no dependency to the installed icon themes or Shell. CI pins a known renderer
revision. `task verify` also requires REUSE (`reuse lint`).
The GTK check requires Python GObject introspection, GTK 3 and GTK 4
introspection typelibs, Xvfb and `xvfb-run`. On Ubuntu, install `python3-gi`,
`gir1.2-gtk-3.0`, `gir1.2-gtk-4.0`, `librsvg2-common` and `xvfb`.

Family contact sheets are generated under `build/previews/` on light and dark
backgrounds at 16, 22, 24 and 32 pixels, each at 1× and 2×. Read the
[design contract](docs/icon-design-rules.md) and [verification guide](docs/sdd/icon-theme-compliance/VERIFICATION.md)
for palette and visual-review limits.

Optional native KDE recoloring checks run with `task test:kde` (requires
KF6 IconThemes). See [the KDE test guide](docs/kde-native-recoloring.md) for
dependencies, prototype inputs, comparison images and known results.

MIME types include 32 Papirus designs with 24 and 32 px masters and 327
filename aliases per size. Smaller sizes reuse 24 px; larger sizes reuse 32 px.
This import preserves upstream colors and layers; semantic recoloring is pending.
See `metadata/mimetypes.json` for the inventory and source provenance.

First-party material is GPL-3.0-or-later. Papirus-derived artwork remains
GPL-3.0-only; see [third-party notices](THIRD_PARTY_NOTICES.md), `REUSE.toml` and
`LICENSES/`.

[Places](docs/places-design.md) provides eighteen types: Home, generic folder,
Downloads, Documents, Desktop, Pictures, Music, Videos, Projects, Templates,
Public, Build, Bookmark, Network, Recent, empty Trash, full Trash and open
folder. Two real SVG master directories hold
24 px monochrome semantic artwork for regular and explicit symbolic names, and
32 px detailed colorful artwork. Declared relative directory aliases reuse these masters.
Restored historical lookup names and deferred names are recorded explicitly in
`metadata/places.json`; the migration inventory keeps its historical names with updated flat 24 px paths.
Previews include both backgrounds, small sizes and enlarged gradient review.

[Devices](docs/devices-design.md) provides five glyph-only families with 24 px
monochrome semantic regular and symbolic names, a 32 px colorful master, and declared size aliases.
`metadata/devices.json` records retained historical aliases and retired imported
names without changing the migration inventory.

Applications use seven supplied 170 px HoloNight and Strata masters, scalable
from 16–512 logical pixels at scales 1 and 2. Files and Viewer expose their
`org.holonight.*` names; `holonight-pkg-manager` aliases Store. Additional native
canvas sizes are supported without directory aliases. See the
[application import workflow](docs/icon-design-rules.md#application-imports).
`metadata/apps.json` records artwork, filename aliases, replacements and retirements.
Kiro and AWS VPN Client are retired pending verified redistribution rights;
the historical migration inventory remains unchanged.

### On-demand template recoloring

`HoloNight` ships holonight-light; `HoloNight-Dark` ships holonight-dark.
All eighteen colorful 32 px Places types and five colorful 32 px Devices types
support on-demand recoloring (23 templates).
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

Chevron Actions have monochrome 24/32 px masters and navigation aliases;
see the [Actions artwork and lookup contract](docs/actions-design.md).
All 24 px families use an effective 1.7 px primary outline, preserving fine
lettering, filled edges and silhouettes.

## Standalone developer tooling

See [tooling/README.md](tooling/README.md) for presets, local dependency overrides, editor refresh,
`task tooling:doctor`, and the independent Serena project.


## Local CI rehearsal

Prepare explicitly before acceptance:

```sh
python3 scripts/ci/run.py --prepare --qt-source /path/to/holonight-qt
task ci
```

Preparation pulls immutable images and exports renderer revision
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`. Omit `--qt-source` to acquire that
revision from canonical GitHub during preparation. Supplied paths may contain spaces;
the checkout must contain that Git revision. Preparation invokes `task deps`, validates
installed Qt >=6.11 Core/Gui/Svg, GTK3/GTK4 and introspection, Cairo, SVG/PNG loaders,
DejaVu font and Xvfb, and records source hashes, package/toolchain versions, feature
selection and image identity. No supplementary packages are downloaded or installed.

Acceptance requires compatible prepared inputs, uses `--pull=never --network=none`,
and mounts its inputs read-only. Each lane has a fresh disposable source/build tree,
isolated XDG directories and the calling user's account. Git, Python 3 and an accessible
Docker daemon (Podman fallback) are required; images target linux/amd64.
Preparation needs registry/GitHub network access; acceptance works offline.

The `verification` lane retains Python regressions, generation/validation, actual Qt
renderer assertions, GTK3/GTK4 symbolic recoloring, inheritance/scale coverage and
previews. `minimal` runs generation, validation and Python installation/package tests
with renderers disabled. `release` stages the validated Python-only production payload
and rejects compiled test artifacts. `static` checks canonical formatting for both C++
tools and strict tidy for the enabled Qt renderer tool. `licensing` checks all four
existing REUSE roots in its separate pinned image.

Current tracked edits and non-ignored new files enter the snapshot. Complete logs,
revision/dirty state and results are saved below `build/ci/`; themes and previews remain
in `artifacts/verification/`, and the release payload in `artifacts/release/`.
Incompatible prepared artifacts are archived as `build/ci-prepared.previous-N`.
Existing developer builds and unrelated files are preserved.

For local rendering outside CI, supply the approved renderer checkout explicitly:

```sh
HOLONIGHT_QT_SOURCE=/path/to/holonight-qt task deps
task test:render
```

There is no sibling fallback. Ordinary rendering commands consume the validated fixture
in `build/deps/renderer`, never the live checkout, and never prepare or acquire dependencies.
`VERIFY_RENDERERS=OFF VERIFY_KDE=OFF task deps` selects Python-only preparation without
probing renderer prerequisites. Generation/staging/install/recolor remain Python-only.
`HOLONIGHT_EXTERNAL_PREFIX` selects installed external packages.

`VERIFY_KDE` defaults to `OFF`. Explicit `task test:kde` requires Qt >=6.11 and
`KF6::IconThemes` and fails if discovery is unavailable. `VERIFY_KDE=ON` also enables
KDE discovery during preparation and conditional native compilation/tidy/execution in
CI static acceptance. Native KDE execution is deferred in the qualified image, which
has no qualified KF6IconThemes prerequisite. Debian qualification, manual ecosystem
acceptance and final integration remain deferred.

Run focused regressions with `python3 scripts/ci/test_launcher.py` and
`python3 scripts/ci/test_dependencies.py`.
