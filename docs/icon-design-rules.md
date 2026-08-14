# HoloNight icon design rules

This document is the production brief for icons intended for the HoloNight icon theme. It is based on the icon usage
in the HoloNight shell, settings, AI, package-manager, greeter, and shared Qt repositories, together with the product
mockups in those repositories and in `holonight-docs`.

The theme inherits from Papirus Dark, Papirus, Breeze Dark, and hicolor. HoloNight does not need to redraw every
upstream icon. Add an override only when the HoloNight visual language, a product-specific concept, or a required
state cannot be supplied by an inherited theme.

## Visual character

HoloNight is a dark, futuristic desktop with restrained neon accents. Its icons should feel precise and technical,
not ornamental.

- Use simple silhouettes, thin rounded linework, and clear negative space.
- Prefer front or orthographic views. Use perspective only for illustrative application, weather, or place icons.
- Use cyan and blue as the normal accent, violet as a secondary accent, green for success, amber for attention, and
  red for destructive or error states.
- Keep routine interface icons monochrome. The application applies normal, muted, disabled, active, and semantic
  colors at runtime.
- Use gradients, glow, layered depth, and dark interior panels only in full-color icons. At small UI sizes these
  effects become blur and reduce recognition.
- Match optical weight and occupied area across a set. Equal numeric bounds do not necessarily look equally large.

The mockups show icons most often at 16, 20, 22, 24, 28, and 32 logical pixels. Weather artwork also appears at 64,
128, and approximately 220 pixels. Every theme icon must remain recognizable at its smallest declared size.

## Choose the icon family first

Do not apply one construction recipe to all icons.

| Family | Typical use | Master canvas | Color treatment |
| --- | --- | --- | --- |
| Symbolic UI | buttons, menus, navigation, settings, status, devices | `24 × 24` | semantic monochrome |
| Fixed panel/status | tray and panel states needing pixel tuning | exact target size | monochrome; restrained state accent |
| Full-color application | launchers, task switchers, alerts | `256 × 256` | HoloNight tile, gradients allowed |
| Full-color places/mimetypes | folders and content types | `24 × 24` or inherited contract | small flat palette |
| Illustrative/weather | weather conditions and large dashboard art | `512 × 512` | full color, layered artwork |
| Brand/provider/distro | third-party identity | original official canvas | preserve brand geometry and color rules |

Symbolic icons belong under `HoloNight/symbolic/<context>/`. Full-color scalable overrides belong under
`HoloNight/scalable/<context>/`. Put manually pixel-tuned panel icons under the matching fixed-size directory, such
as `HoloNight/24x24/panel/`.

## Symbolic UI construction

### Canvas and grid

- Author on a `24 × 24` viewport with `viewBox="0 0 24 24"`.
- Use a nominal `2` unit safe area on every side. Ordinary geometry should stay inside `x/y = 2…22`.
- Keep the main recognizable mass inside `3…21` when possible. Use the outer safe-area boundary only for long
  arrows, slashes, signal arcs, or shapes that otherwise look visibly undersized.
- Center by optical weight rather than only by mathematical bounds. Circular and diagonal forms may extend about
  `0.25` unit beyond the bounds of square forms to look equal in size.
- Prefer whole- or half-unit coordinates. Fractional coordinates are acceptable when required to align a stroke's
  centerline with the pixel grid at the target size.
- Do not crop strokes. The stroke, including round caps and joins, must remain inside the viewport.

### Stroke and shape

- The standard stroke on the 24-unit master is `1.7` units.
- A range of `1.5–2.0` is permitted only for optical correction or compatibility with an existing family. Do not
  mix weights arbitrarily within one set.
- Use `stroke-linecap="round"` and `stroke-linejoin="round"` by default.
- Use `fill="none"` for outline forms. Use solid fills for small dots, badges, compact indicators, and shapes that
  would collapse as outlines.
- Keep gaps at least `1.5` units wide on the master; target `2` units for critical interior counters.
- Keep short terminal segments at least `2` units long. Avoid decorative notches or isolated details smaller than
  `1.25` units.
- Use consistent corner language: approximately `1.5–2` unit radii for small rectangular UI forms.
- Avoid hairlines, miter spikes, overlapping translucent strokes, and doubled edges.

### Scaling targets

A scalable symbolic master must be previewed at all of these logical sizes:

| Render size | Expected use | Effective stroke from a 1.7-unit master |
| --- | --- | --- |
| 16 px | compact controls and menus | about 1.13 px |
| 20 px | notifications and dense rows | about 1.42 px |
| 22 px | headers and popup controls | about 1.56 px |
| 24 px | standard controls, sidebar tabs, devices | 1.7 px |
| 28 px | audio streams and compact app identity | about 1.98 px |
| 32 px | top bar, launcher results, notification apps | about 2.27 px |

If a symbol becomes muddy at 16 px, simplify it before increasing its global stroke. Remove the least important
detail, enlarge counters, or produce a fixed-size version when the silhouette genuinely needs pixel-specific work.

## Fixed panel and status icons

Fixed-size SVGs use a viewport equal to the directory size and are tuned at 100% zoom. Recommended starting values
are:

| Directory size | Safe padding | Nominal stroke |
| --- | --- | --- |
| 16 px | 1.5 px | 1.25 px |
| 22 px | 2 px | 1.5 px |
| 24 px | 2 px | 1.7 px |
| 32 px | 3 px | 2 px |
| 64 px | 6 px | 3–4 px |

- Preserve a stable silhouette between states. Enabling Bluetooth, muting audio, or losing network connectivity
  must not make the base glyph jump or change scale.
- Reserve one consistent region for a state marker. For a 24 px icon, a dot is normally `2–2.5` px in diameter and
  a slash uses the base stroke weight.
- State must be readable without color alone. Pair color with a dot, slash, pause mark, exclamation mark, or changed
  signal geometry.
- Keep warning and error badges above the base glyph and give them enough surrounding negative space to survive at
  16 px.
- Do not use an SVG blur filter for ordinary panel icons. The surrounding shell supplies glow and active treatments.

## Full-color application icons

HoloNight application icons use a `256 × 256` master.

- Keep all visible artwork within `20…236`, giving a 20-unit (`7.8%`) outer safe area.
- Keep the primary symbol within roughly `52…204`; adjust optically for wide or tall symbols.
- Use the established clipped-corner HoloNight tile silhouette for first-party applications. Keep the tile outline
  near `8` units and primary glyph strokes near `12–14` units.
- The tile should use a deep navy surface rather than pure black. Cyan-to-blue-to-violet is the preferred edge or
  glyph gradient.
- Use at most three visually dominant layers: tile/background, primary glyph, and a state or product accent.
- Ensure the central glyph reads in monochrome. Color may distinguish the product, but it must not carry the entire
  meaning.
- Preview at 16, 24, 32, 48, 64, 128, and 256 px. At 16 and 24 px the result may read mainly as tile plus silhouette;
  do not depend on small labels or texture.
- Do not place text, version numbers, or thin internal grids in an application icon.

Third-party brand icons are exceptions: preserve the official mark and its exclusion zone. Do not force a brand
logo into HoloNight linework, recolor it without permission, or add a glow that changes its identity. A neutral dark
tile may be used only when the brand's own guidance allows containment.

## Places, folders, and mimetypes

The existing folder family is a compact 24-unit, filled design and should remain visually compatible with inherited
Papirus icons.

- Use `viewBox="0 0 24 24"` and keep the outer folder silhouette in approximately `2…22` horizontally and `3…21`
  vertically.
- Reuse the established blue base and pale inset-paper structure. A folder-specific emblem may change, but its base
  folder must not.
- Keep emblems simple enough to read at 16 px and inside the folder's central clear area.
- Open, closed, synced, locked, favorite, and warning variants must keep the same apparent size and baseline.
- Do not add a new folder color solely for decoration. Color changes need a stable semantic meaning.
- Mimetype icons should emphasize file class through one strong emblem, not miniature application interfaces.

## Weather and illustrative icons

Weather icons are product artwork rather than symbolic theme icons. The shell currently uses square 512-unit art at
64, 128, and large-current-condition sizes.

- Use `viewBox="0 0 512 512"`; omit a visible background rectangle.
- Keep ordinary condition art inside approximately `64…448`. Extreme effects may extend to `40…472` but must not
  touch the canvas edge.
- Keep a common sun, moon, and cloud scale across the entire set. Day/night and intensity variants must align so a
  changing forecast does not appear to jump.
- Use a limited shared palette and consistent lighting direction. Separate rain, snow, hail, lightning, fog, and
  wind by shape as well as color.
- Design the primary weather mass to survive at 64 px. Details visible only at 220 px are secondary.
- Use blur or glow sparingly and keep it within the safe area. Check that transparent effects do not create a large,
  misleading rendered bounding box.
- Export deterministic, optimized SVG. Remove editor metadata, embedded rasters, and legacy doctypes when revising
  an asset.

## Color and runtime recoloring

Symbolic icons must cooperate with HoloNight's semantic recoloring pipeline. Use this pattern:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <style>
    .ColorScheme-Text { color: #444; }
    .ColorScheme-Highlight { color: #4285f4; }
    .ColorScheme-PositiveText { color: #9ece6a; }
    .ColorScheme-NeutralText { color: #ff9e64; }
    .ColorScheme-NegativeText { color: #f7768e; }
  </style>
  <g class="ColorScheme-Text" fill="none" stroke="currentColor"
     stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
    <!-- geometry -->
  </g>
</svg>
```

- Use `ColorScheme-Text` for the normal glyph.
- Use `ColorScheme-Highlight` only for an intrinsically active/selected portion.
- Use `ColorScheme-PositiveText`, `ColorScheme-NeutralText`, and `ColorScheme-NegativeText` for success, warning, and
  error meaning respectively.
- The literal fallback colors make previews usable; the runtime palette replaces their semantic meaning.
- Do not use literal white, black, cyan, or violet in a symbolic icon that is expected to tint.
- Do not encode hover, pressed, muted, or disabled variants as separate colors. Those are control states applied by
  HoloNight.
- Never use color alone to distinguish active, disabled, warning, and error assets.

Full-color icons may use HoloNight palette colors directly. Recommended starting colors, already represented in the
product assets, are deep navy `#090e1b`/`#0c1425`, primary text `#c0caf5`, cyan `#5debff`/`#7dcfff`, blue `#7aa2f7`,
violet `#bb9af7`, success `#9ece6a`, warning `#ff9e64`, and error `#f7768e`. Check colors against the current product
palette before creating a new family; these values describe existing artwork, not a replacement palette contract.

## Naming, contexts, and variants

- Use the standard freedesktop or upstream icon name whenever one exists, for example
  `audio-volume-high-symbolic.svg`, `network-wired-symbolic.svg`, or `folder-documents.svg`.
- Symbolic filenames end in `-symbolic.svg`. Do not add that suffix to full-color application or place icons.
- Use lowercase kebab-case except when an upstream application ID or icon name has required capitalization.
- Put icons in the semantic context that consumers search: `actions`, `apps`, `categories`, `devices`, `mimetypes`,
  `places`, or `status`.
- Prefer the standard base/state vocabulary: `-active`, `-disabled`, `-offline`, `-paused`, `-syncing`, `-synced`,
  `-warning`, and `-error`. Follow an upstream application's exact names when overriding its tray icons.
- Keep aliases as symlinks where packaging permits rather than exporting divergent duplicate drawings.
- Do not rename an existing icon or change its state semantics while restyling it.

Before drawing a new name, search all product repositories and inherited themes. Product code uses theme names from
desktop files, StatusNotifierItem services, audio services, and notification senders; exact compatibility is more
important than an internally tidy rename.

## SVG production requirements

- SVG is the source and delivery format unless a raster asset is explicitly required.
- Always include a `viewBox`. Width and height may be included for preview convenience but must agree with the
  intended canvas.
- Use standard SVG elements and attributes supported by Qt SVG.
- Expand text to paths. Do not reference external fonts, stylesheets, images, or files.
- Do not embed base64 rasters in an SVG.
- Remove editor-specific namespaces, guides, hidden layers, unused definitions, and metadata.
- Give gradients and filters stable descriptive IDs. Remove autogenerated ID churn.
- Keep transforms simple; bake nested transforms when this improves reviewability without damaging geometry.
- Avoid masks, clipping paths, filters, and blend modes in symbolic icons. Use them only when essential in
  full-color artwork and verify Qt rendering.
- Use lowercase six-digit hex colors in new hand-authored files. Preserve established formatting when making a
  focused edit to an existing family.
- Keep source ordering logical: definitions, background/base, primary glyph, then badges and highlights.
- Ensure the file has no opaque canvas-sized background unless the background is intentionally part of an
  application tile.

## Accessibility and meaning

- A symbol must be identifiable by silhouette at the smallest supported size.
- Do not rely on a red/green distinction. Change geometry or add a badge as well.
- Use familiar platform metaphors for universal actions. Avoid inventing a novel glyph when search, close, add,
  settings, lock, network, or volume already has a standard form.
- Directional icons must have matched geometry and weight. Mirror only when meaning permits; playback and text
  direction may require locale-aware handling by the application.
- Destructive icons should look destructive through their metaphor, not only their red color.
- Decorative glow must not be required to perceive the shape.

## Review and delivery checklist

For every icon or coherent icon set:

1. Confirm the exact consumer name, context, states, and smallest rendered size.
2. Compare against inherited Papirus/Breeze artwork and justify the override.
3. Check canvas, safe area, stroke, cap/join, optical centering, and occupied bounds.
4. Render symbolic icons at 16, 20, 22, 24, 28, and 32 px; render app icons at 16 through 256 px; render weather
   icons at 64, 128, and 220 px.
5. Inspect on HoloNight's dark surface in normal, muted, disabled, active, success, warning, and error colors where
   applicable.
6. Compare all states side by side. The base silhouette must not shift, shrink, or change weight.
7. Check color-blind-independent state cues and recognition without glow.
8. Validate XML and render with Qt SVG or Inkscape. Inkscape example:

   ```sh
   inkscape path/to/icon.svg --export-width=24 --export-height=24 \
     --export-filename=/tmp/icon-24.png
   ```

9. Run `task validate` from `holonight-icons`.
10. Install with `task install:local` for a real desktop preview when icon assets changed. Inspect the actual shell,
    settings navigation, launcher, tray, and notification surfaces that consume the icon. Manual UI interaction must
    be performed by the developer; automated pointer or focus interaction is not permitted.
11. Include before/after previews for visual changes and record any intentional exception to these rules.

## When an exception is justified

These rules are defaults, not a reason to damage an established external contract. Brand marks, upstream tray icon
names, inherited folder geometry, and an existing coherent state family may require a different canvas or stroke.
Document the exception in the change description, keep it scoped to that family, and verify it beside standard
HoloNight icons at the same rendered size.
