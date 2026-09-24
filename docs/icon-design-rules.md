# Artwork and recoloring contract

The canonical tree is `icons/<context>/<native-size>/`. Keep the original canvas
and proportions; the native size is the longer viewBox dimension (the 75×100 Kiro
mark belongs in `apps/100`). Panel artwork belongs in `status`. Full-color and
symbolic representations may coexist under `<size>/` and `<size>/symbolic/`.
Relative SVG aliases stay within the theme. Only the relative, same-context size-directory aliases declared in
`metadata/places.json` are permitted. They explicitly advertise scaled reuse;
Places has two real master directories: 24 for colorful regular and theme-responsive monochrome symbolic
artwork at 16–24 px, and 32 for colorful artwork at 32 px and above. Extra optical
masters require demonstrated visual need. Explicit `-symbolic` names stay
monochrome at every requested size, reusing the 24-unit master.

Use simple silhouettes, clear counters and consistent optical weight. For a new
24-unit UI symbol, start with a 2-unit safe area, rounded 1.7-unit strokes and at
least 1.5-unit gaps. Preserve existing application-requested status silhouettes.
New interaction treatments (selected, hovered, disabled) come from the consumer,
not separate assets. Domain status badges such as sync errors remain meaningful
artwork and must be legible without color alone.

Every responsive SVG contains exactly one stylesheet with
`id="current-color-scheme"` and `type="text/css"`. Use the complete definitions
in `metadata/palettes.json`. Shapes or ancestor groups assign a supported class,
and every effective visible fill/stroke is `currentColor` or `none`, except for
explicitly exempt fixed artwork. A class alone does not make a hard-coded fill
semantic. Inline `color` overrides and unclassified implicit black are prohibited.
The validator supports simple class color definitions, not arbitrary CSS selectors,
external resources, animation or indirect `<use>` references in responsive artwork.

| Role | Purpose | holonight-qt rendering |
| --- | --- | --- |
| ColorScheme-Text | Foreground | Supported |
| ColorScheme-Highlight | Accent / selection | Supported |
| ColorScheme-PositiveText | Success | Supported |
| ColorScheme-NeutralText | Warning | Supported |
| ColorScheme-NegativeText | Error | Supported |
| ColorScheme-Background | Surface | Reserved, fallback only |
| ColorScheme-HighlightedText | Selection text | Reserved, fallback only |

Background and HighlightedText are valid KDE roles, but the current HoloNight
renderer exposes only five colors. Keep their defaults declared; do not assign
these two classes to painted shapes until consumer support is added. Selection
and disabled tests pass resolved foreground colors to the renderer; this is not
a test of Shell's palette selection or event handling.

Light and dark defaults come from holonight-light and holonight-dark, with
provenance and role mapping in `metadata/palettes.json`. Runtime icon generation
replaces only stylesheet bodies; it never replaces arbitrary literal hex colors. Default
colors help renderers without palette recoloring. Recoloring itself is toolkit
specific; `FollowsColorScheme=true` does not implement recoloring or switching.

Fixed brands, full-color applications, folder illustrations, weather art and
intentional decorative shading retain their paint. Every exemption has an exact
asset path and rationale in `metadata/fixed-artwork.json`; globs are prohibited.
Mixed artwork exempts exact element IDs and keeps the responsive portion semantic.
Places contains fifteen folder types (30 regular token templates), including the seven
Desktop, Pictures, Music, Videos, Projects, Templates and Public additions plus Recent and both Trash states; see the [Places specification](places-design.md).
There is no weather artwork in the current inventory.

Fixed assets also include an unused semantic stylesheet. This is a compatibility
guard for holonight-qt's legacy literal-paint tinting fallback, which is bypassed
when semantic definitions are present. It does not assign roles to fixed shapes.
The real renderer regression test proves that their pixels stay unchanged across
light, dark, selected and disabled colors.

Full-color app tiles normally use a 256-unit canvas with 20-unit outer padding.
Preserve external brand canvases and exclusion zones. Small-size scalability does
not prove legibility: review previews at 16/22/24/32 and 2× on both backgrounds.
Check status badge separation, unclipped strokes, stable family silhouettes and
selected/disabled contrast in the actual consumer. A white brand may intentionally
need a contrasting surface; do not silently recolor its mark to solve that.

Run `task verify`. New source files automatically gain directory metadata, but
removing or retargeting migrated lookup names fails validation except for the exact
Places-only dispositions recorded in `metadata/places.json`. Update REUSE
attribution when adding artwork. Do not edit generated output.

References: [Breeze generation](https://github.com/KDE/breeze-icons/blob/master/icons/CMakeLists.txt),
[KDE stylesheet contract](https://github.com/KDE/kiconthemes/blob/master/src/kiconcolors.cpp),
[Icon Theme Specification](https://specifications.freedesktop.org/icon-theme/latest/).

Places visual review covers all fifteen folder types listed in the Places specification;
unrelated historical artwork remains deferred.

## Explicit token templates

`metadata/templates.json` is the only authority for on-demand artwork recoloring;
currently it lists all fifteen regular folder types at both master sizes. Author these assets in the canonical tree
using only the HoloNight classes actually used by that master, mapped explicitly to holonight-qt tokens, including every
gradient stop. Canonical defaults are Dark. Do not add fixed-artwork exemptions
for templates: validate their paints before exporting them as frozen artwork.
The exporter permits a small SVG subset, validates inherited roles, forbids literal
or implicit paints and unsupported CSS, and retains only the unused ColorScheme
guard in the export. Runtime semantic gradients require classified currentColor
stops. Existing runtime icons and fixed brands keep their separate contracts.

HoloNight ships holonight-light defaults; HoloNight-Dark ships holonight-dark.
`metadata/palettes.json` records the offline holonight-qt provenance and semantic
role mapping, superseding the earlier Breeze defaults. Rebuilds change standard
semantic stylesheets; only manifest-listed templates also resolve literal paints.

One template bundle installs under `$XDG_DATA_HOME/holonight-icons`, outside icon
lookup directories. Recolor only through an explicit command; palette changes
alone do nothing. Never recover token identity by matching generated hex values.
