# Places: two SVG master directories

Places provides Home, the generic folder, Downloads, Documents, Desktop, Pictures,
Music, Videos, Projects, Templates, Public, Recent, empty Trash, full Trash and the generic open folder. Other historical artwork remains deferred.
Both real directories retain `.gitkeep` files. No new master directory is added.

| Display sizes | Master | Artwork |
| --- | --- | --- |
| 16, 20, 22, 24 | 24 | Simplified colorful regular folder |
| 32, 48, 64, 96, 128, 256, 512 | 32 | Detailed colorful regular folder |
| All symbolic requests | 24/symbolic | Monochrome rounded glyphs |

Every non-master size is a relative directory symlink directly to its master:
`16 → 24`, `20 → 24`, `22 → 24`, and `48/64/96/128/256/512 → 32`.
Additional optical masters require demonstrated visual need. Keep symbolic
subdirectories wherever full-color and symbolic artwork coexist.

Directory discovery advertises the masters and all nine aliases. Each Places
entry uses Scalable metadata with MinSize=MaxSize=Size. Scale=2 entries in
ScaledDirectories reference the same directories with a `/.` suffix; there are
no physical `@2x` directories. Regular names precede symbolic alternatives.
Larger symbolic requests reuse the 24 px glyph without a colorful fallback.

Both regular masters provide `folder-home.svg` and a `user-home.svg` alias.
`24/symbolic/folder-home-symbolic.svg` provides the glyph, with a
`user-home-symbolic.svg` alias. `metadata/places.json` authorizes the restored
historical user-home name and the generic folder replacements described below.
The entire
`metadata/migration.json` inventory remains unchanged.

## Home artwork and tokens

The visual reference is `drafts/folder-home/folder-home-dark-mod.svg` (preserved
unchanged, alongside the editor-resized draft). Canonical 32 px artwork retains
the revised silhouette, rounded house, open doorway, gradients and blue edge.
Low-opacity strokes duplicating the house path add soft cyan-to-blue/violet
glow beneath the crisp glyph. Gradient overlays duplicating the recessed face
concentrate light at its edges and fade toward the dark center. The folder has
no exterior halo; all new lighting stays within its existing silhouette. It scales uniformly, including strokes, to a 28 px painted width
on a 32×32 canvas. The [canvas rules](icon-canvas-rules.md) define safe bounds.

The 24 px regular master has a 20 px painted width, removes the fine edge and
roof highlights and house glow, and enlarges the house by 18% so
its doorway stays open at 16 px. Its opaque recessed face carries an 8% rim-gradient
tint and broad horizontal edge lighting: cyan at the left, blue at the center
and violet at the right, with opacities of 18%, 4.5%, 0%, 4.5% and 18% at
0%, 22%, 50%, 78% and 100%. Both overlays stay inside the recessed face,
beneath the crisp house, without an exterior halo or fine highlights. The symbolic master is a single rounded house
using ColorScheme-Text/currentColor, without gradients or folder geometry.

The generic `folder.svg` at each master size is an exact copy of Home with only
its house layers removed: `house` at 24 px; `house`, `house-glow-1` through
`house-glow-8`, and the roof highlight `path14` at 32 px. All remaining elements,
paints and geometry are identical. These approved bodies are shared by the folder
family: future folder types differ only in their interior glyph layers.
`inode-directory.svg` aliases `folder.svg` at both sizes.

`24/symbolic/folder-symbolic.svg` uses the closed outer folder path as a hollow
ColorScheme-Text outline, with no interior fill or gradients. Uniform scaling
centers its 18.3 px path width plus 1.7 px rounded stroke in the 20 px safe area.
The historical symbolic `folder.svg` aliases this outline; regular lookup retains
precedence. Larger symbolic requests reuse this 24 px master.

`metadata/templates.json` lists all 30 regular assets across the two master sizes. Each maps only its five
used tokens: background, surface, accentCyan, accentBlue and accentViolet.
The recoloring JSON input still requires all six tokens, including textPrimary.
Canonical templates use holonight-dark. HoloNight exports holonight-light and
HoloNight-Dark exports holonight-dark. Day/Storm remain explicitly selectable
compatibility presets. Semantic defaults are an offline holonight-qt snapshot.

Regular exports have frozen literal paints and an unused standard semantic
guard preventing runtime tinting. Symbolic artwork responds to runtime palettes
and never enters the on-demand recoloring manifest. The single installed bundle
lives outside icon lookup directories; recoloring stages and validates all 30
regular outputs, preserves backups and rolls back partial replacement failures.

## Verification

Run `task verify`. Tests cover the complete folder family and fixture lookup at all eleven
sizes and 1×/2×, alias identity, frozen regular colors, runtime symbolic colors,
exact palette defaults and temporary-XDG installation/recoloring recovery.
Inspect `build/previews/folder-home-states.png`, the symbolic state sheet and
`folder-home-gradients.png` on both backgrounds at 16/22/24/32 px and 2×.
The `folder-states.png`, `folder-symbolic-states.png` and `folder-gradients.png`
sheets cover the generic folder; `folder-family-*.png` places them alongside Home.
Selection and 45% disabled opacity are consumer-state simulations, not a claim
about Shell's event handling. Review the 24-to-32 transition and open doorway.

Visual review completed on 2026-09-23 for both variants and backgrounds, all
requested small sizes and 2×, selected surfaces and 45% disabled opacity. The
24 px master keeps the doorway open at 16 px; the transition to the detailed
32 px master preserves the family silhouette. Enlarged gradients are smooth,
and strokes stay unclipped. The 32 px house glow is soft, its doorway remains
open, and the inset edge lighting stays inside the unchanged folder boundary.
The separate lighting mockup was unavailable for this review; glow placement
follows the supplied plan. The smallest disabled folder rim is faint on a
matching background, while the house remains recognizable. Symbolic selection
and disabled presentations retain a clear glyph and open doorway.

The 24 px face-tint review on 2026-09-23 covers both themes on both backgrounds
at 16/22/24/32 px and 2×, enlarged gradients, selected surfaces and 45% disabled
opacity. The faint tint gives the face a visible surface on matching backgrounds;
broad edge shading softens the flat fill on contrasting backgrounds while strong
light/dark contrast remains. The house stays crisp without glow and its doorway
remains open. The smallest disabled rim remains faint on matching backgrounds.
All original SVG elements retain their attributes and geometry; the 32 px and
symbolic sources are unchanged. `task verify` passed with all 28 tests, actual Qt
renderer checks and REUSE licensing checks.

Generic folder review completed on 2026-09-23: both themes and backgrounds,
16/22/24/32 px and 2×, enlarged comparison with Home, selection and 45% disabled
opacity. The colorful bodies match Home with no residual house glow or roof
highlight. The hollow symbolic folder has a clear tab, transparent interior and
unclipped rounded outline in every state. As in Home, the smallest colorful
folder rim is faint when disabled on a matching background. Home sources remain
byte-identical. `task verify` passed all 29 tests, Qt rendering and lookup checks,
temporary-XDG installation/recoloring checks and REUSE licensing validation.

## Downloads artwork

`icons/places/24/folder-download.svg` and `icons/places/32/folder-download.svg`
reuse the approved generic folder bodies byte for byte, adding only interior
glyph layers. A centered downward arrow sits above an open rounded tray. Its stroke uses
Home’s cyan-to-blue-to-violet rim gradient.
The 24 px glyph is enlarged slightly to match Home's small-size weight, with no
glow. The 32 px glyph uses eight low-opacity expanded strokes following Home's
layered glow technique; lighting stays inside the folder silhouette.

The supplied Downloads mockup is referenced by the implementation plan as a
“downward arrow above an open tray.” No Downloads mockup file was present in the
workspace during implementation, so this description is the available reference.
`24/symbolic/folder-download-symbolic.svg` contains only the arrow and tray,
with rounded 1.7-unit ColorScheme-Text strokes and a 2-unit safe area.

Both regular masters have `folder-downloads.svg` aliases. The historical symbolic
`folder-download.svg` aliases the glyph-only symbol; regular name lookup retains
precedence. The distinct `folder-download-open.svg` remains deferred.
Both regular Downloads masters use the existing five folder token mappings and
Dark canonical defaults. Symbolic Downloads remains outside template generation.

Downloads has regular and symbolic state sheets (`folder-download-states.png`
and `folder-download-symbolic-states.png`), enlarged master comparisons
(`folder-download-gradients.png`) and entries in all `folder-family-*.png` sheets
under `build/previews/`. Tests cover lookup at all declared sizes and 1×/2×,
unchanged folder bodies, frozen exports, consumer palette response, installed
alias identity and rollback after a Downloads master has been replaced.

Downloads visual review completed on 2026-09-23: both themes on both backgrounds,
16/22/24/32 px and 2×, selected surfaces and 45% disabled opacity, plus enlarged
family/master comparisons. The arrow and open tray remain separated, rounded
strokes stay unclipped, and the unchanged bodies maintain the Home family
silhouette across the 24-to-32 transition. The small master stays crisp; the
larger master's soft cyan glow stays inside the folder. Symbolic selection and
disabled states remain recognizable. Regular disabled artwork is faint on
matching backgrounds, consistent with Home. The mockup image itself was not
available for direct comparison. `task verify` passed all 30 tests, actual Qt
rendering and lookup, temporary-XDG installation/recoloring recovery, and REUSE.

## Documents artwork

`icons/places/24/folder-documents.svg` and `icons/places/32/folder-documents.svg`
reuse the approved generic bodies exactly, adding only `documents` and (at 32)
`documents-glow-1` through `documents-glow-8`. The reference is the Documents
page in `places.png`: portrait outline, clipped upper-right corner and two
horizontal bars. The page and bars use Home’s cyan-to-blue-to-violet rim gradient, rounded joins and
transparent counters. Eight expanded, low-opacity strokes provide the 32 px
interior glow; the 24 px glyph stays crisp.

The path plus its 1.4-unit stroke measures 8.3 × 10.4 units before the existing
folder transform: 6.83 × 8.56 px at 24 and 9.50 × 11.91 px at 32, excluding
glow (width/height 0.798). It is centered horizontally at source x=16 and
vertically at y=17, below the tab, matching Home and Downloads' optical center.
The page is taller and narrower than Home's house.

`24/symbolic/folder-documents-symbolic.svg` is a page-only ColorScheme-Text
outline with rounded 1.7-unit strokes and at least a 2-unit canvas safe area.
Both regular masters use the existing five token mappings and Dark defaults;
the symbolic glyph responds to consumer palettes. The historical regular
`folder-documents.svg` is restored; `folder-documents-open.svg` stays deferred.
The migration inventory and existing size aliases are unchanged.

Documents is included in `folder-family-*.png` comparisons, with separate
`folder-documents-states.png`, `folder-documents-symbolic-states.png` and
`folder-documents-gradients.png` sheets. Tests cover exact body preservation,
all-size lookup, frozen exports, runtime symbolic recoloring, temporary-XDG
installation and rollback after the first new Desktop master has been replaced.

Documents visual review completed on 2026-09-24 using `places.png`, the regular
and symbolic state sheets and enlarged family comparisons: both themes on both
backgrounds at 16/22/24/32 px and 2×, selected surfaces and 45% disabled opacity.
The two bars remain distinct, the page counter stays open, and the rounded
clipped corner remains recognizable. The blue page feels taller and narrower
than Home with consistent optical placement; its 32 px glow stays inside the
unchanged folder silhouette. The smallest disabled regular icon is faint on a
matching background, consistent with the existing family. Symbolic states retain
clear separation. `task verify` passed all 31 tests, actual Qt rendering and
lookup checks, temporary-XDG recoloring/recovery and REUSE licensing validation.


Glyph style alignment reviewed on 2026-09-24: Downloads and Documents now use
Home’s `rim` gradient for their crisp glyph strokes and all eight 32 px glow
layers. Existing glow widths, opacity falloff and glyph geometry are preserved;
the 24 px masters remain glow-free. Family previews were inspected in both
themes on both backgrounds at 16/22/24/32 px and 2×, including selection and
45% disabled opacity. The gradient and soft glow match Home; the arrow/tray gap
and document bars remain distinct. The smallest disabled icons remain faint on
matching backgrounds. `task verify` passed all 31 tests, actual Qt rendering,
temporary-XDG installation/recovery and REUSE checks.


## Seven additional folders

Desktop, Pictures, Music, Videos, Projects, Templates and Public each provide
`icons/places/24/folder-<name>.svg`, `icons/places/32/folder-<name>.svg` and
`icons/places/24/symbolic/folder-<name>-symbolic.svg`. These 21 first-party sources
follow the silhouettes in `places.png`:

| Name | Glyph |
| --- | --- |
| desktop | Monitor with stand |
| pictures | Two mountains and a separate sun |
| music | Paired musical notes |
| videos | Play triangle |
| projects | Code brackets |
| templates | Two overlapping pages |
| public | Three connected share nodes |

Every regular body is a byte-for-byte copy of the generic folder, with only the
interior glyph layers added. Each glyph is a single compound path so the shared
`rim` gradient spans the entire motif, including disconnected details. Filled
Pictures, Music and Videos silhouettes follow the reference; the other motifs
use rounded outlines. All use Home's cyan → blue → violet colors rather than the
reference's category colors. Glyphs sit below the tab around source (16, 17).
24 px masters have no glyph glow. 32 px masters reuse the existing eight stroke
widths and opacity falloff, entirely inside the recessed face.

Symbolic forms contain only the glyph with ColorScheme-Text/currentColor;
outlines have effective 1.7 px rounded strokes. Projects uses a slightly smaller
scale to keep its wide brackets inside the 2 px safe area. All symbolic artwork
remains outside the template manifest. The 14 new regular entries retain the five
folder token mappings, Dark defaults and frozen exports with the unused semantic
guard. There are no new palettes, commands, or size-directory aliases.

Regular aliases restore `user-desktop`, `folder-photo`, `folder-video` and
`folder-publicshare`. Historical symbolic Desktop, Pictures, Publicshare and
Sound names (including User Desktop, with and without `-symbolic`) resolve to the
corresponding glyphs. The migration inventory is unchanged; only their explicit
Places dispositions are restored. Category-specific open-folder and unrelated names remain deferred.

All fifteen folders receive individual regular/symbolic state sheets and enlarged
master comparisons in `build/previews/`. Numbered `folder-family-<page>-*.png`
comparisons show two folders per page at full resolution, keeping labels readable
as the family grows. `folder-family-overview-<panel>-states.png` and symbolic
counterparts compare all fifteen types in one sheet for each theme/background.
Qt lookup exercises every proof name and alias at eleven
sizes and both scales, including regular-name precedence and symbolic reuse.
Temporary-XDG installation tests recolor all 28 outputs and check all aliases,
then simulate failure on the second Recent master after the first was replaced.

Seven-folder visual review completed on 2026-09-24 against `places.png`: all
regular and symbolic state sheets were inspected on both themes/backgrounds at
16/22/24/32 px and 2×, including selection and 45% disabled opacity. Enlarged
master comparisons confirm a continuous gradient across each complete glyph,
contained glow, and stable placement across the 24-to-32 transition. The monitor
counter, mountain/sun gap, paired notes, separated brackets, overlapping pages
and share-node connections remain recognizable. At the smallest regular sizes,
Public's node counters and Templates' rear-page gap approach pixel scale; the
larger symbolic forms retain clearer detail. Disabled regular rims remain faint
on matching backgrounds, consistent with Home. `task verify` passes 32 Python
tests, actual Qt rendering/palette/lookup checks, temporary-XDG installation and
recoloring rollback, preview generation and REUSE licensing validation.


## Recent and Trash artwork

Recent, empty Trash and full Trash add six regular templates (28 total), using
exact copies of the approved generic bodies at 24 and 32 px. Recent follows
`places.png`: a round clock with hands pointing up and down-right. Empty Trash
uses a rounded bin, separate lid, handle and two vertical slots. Full Trash keeps
the bin and slots, raises the lid and exposes two paper shapes so the state is
recognizable without color. These new full-state details are original artwork.
All three use the shared cyan–blue–violet rim gradient, crisp 24 px strokes and
eight contained glow layers at 32 px. Dark canonical defaults and the five-token
mapping are unchanged.

The three `24/symbolic/folder-{recent,trash,trash-full}-symbolic.svg` sources
contain glyphs alone, with rounded effective 1.7 px ColorScheme-Text strokes
and the standard semantic stylesheet. Regular `user-trash` and `user-trash-full`
aliases exist at both masters. Historical symbolic User Trash names, with and
without `-symbolic`, resolve to the matching glyph. Only the Recent and Trash
migration dispositions change; the historical inventory and size aliases remain
unchanged.

Family tests check exact body preservation, matching glow paths, template
registration and aliases. Manifest-driven Qt checks and individual/family previews
include all three additions; temporary-XDG recoloring tests cover all 28 exports
and recover from a failure after the first Recent master has been replaced.

Recent/Trash visual review completed on 2026-09-24: individual regular and
symbolic state sheets, enlarged masters and family comparisons cover both themes
and backgrounds at 16/22/24/32 px and 2×, including selection and 45% disabled
opacity. Clock hands remain separated from the round outline; bin slots and
raised-lid/paper silhouettes distinguish the Trash states without relying on
color. Full Trash's widest glow stays within the folder boundary. Symbolic bins
and slots are identical between states. At 16 px, paper details are compact and
disabled regular artwork remains faint on matching backgrounds, consistent with
the family. `task verify` passed all 32 Python tests, Qt rendering and all-size
lookup checks, temporary-XDG installation/recoloring recovery and REUSE licensing.

## Generic open folder

`folder-open.svg` has separate 24 and 32 px colorful masters. A rounded, tabbed
back pocket exposes a dark interior above the lowered diagonal front flap. The
24 px master uses broad shapes and a faint interior tint so the opening stays visible when scaled to 16 px;
the 32 px master adds restrained shading inside the pocket and on the flap. Both
stay within the family's 20 and 28 px painted widths, with no exterior glow.
The 24 px `folder-open-symbolic.svg` uses a rounded 1.7-unit
ColorScheme-Text outline for the back and tilted flap, with a 2-unit safe area.
The historical symbolic `folder-open.svg` aliases that master.

The two regular masters bring the token-template inventory to 30. They use the
existing five folder tokens and Dark canonical defaults; exports are frozen
literal artwork with the unused semantic guard. Only the three generic
`folder-open` historical dispositions are restored. Category-specific open
folder names remain deferred; the migration inventory and size aliases are
unchanged. Manifest-driven lookup, rendering, preview, and temporary-XDG
recoloring checks include the new folder.

Open-folder visual review completed on 2026-09-24 using the individual regular
and symbolic sheets and enlarged masters. Both themes were checked on light and
dark backgrounds at 16/22/24/32 px and 2×, including selected and 45% disabled
states. The flap stays separate from the back pocket at 16 px, and the diagonal
front edge remains legible. The faint 24 px interior tint helps distinguish the
opening in the light theme. The 32 px shading stays within the folder, and the
symbolic strokes and gaps remain clear. As elsewhere in the family, disabled
regular art is faint on a matching background. `task verify` passed all 39 Python
tests, Qt rendering and lookup, temporary-XDG recoloring recovery and REUSE.
