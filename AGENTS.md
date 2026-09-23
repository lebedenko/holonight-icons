# Contributor contract

Read `docs/icon-design-rules.md` before editing artwork. Edit only canonical
`icons/<context>/<native-size>/` sources; `build/` is generated and ignored.
Keep `symbolic/` subdirectories where names have both full-color and symbolic
representations. Preserve the historical `metadata/migration.json` inventory. The explicit Places-only
dispositions in `metadata/places.json` authorize deferred names and replacement
targets; every other migrated name and alias remains required. See
`docs/places-design.md` for the two masters (24 colorful regular and monochrome symbolic, 32 colorful regular) and declared size-directory aliases.
Additional optical masters require demonstrated visual need.

Theme-responsive artwork must have exactly one `<style id="current-color-scheme"
type="text/css">`, the supported role definitions from `metadata/palettes.json`,
and effective `currentColor` fills/strokes classified with `ColorScheme-*` roles.
Inherited group styling is supported. Literal foreground paints, implicit black,
inline color overrides, unsupported CSS and missing roles are errors.
Use Text for foreground, Background for surface, Highlight for accent/selection,
HighlightedText for selection text, PositiveText for success, NeutralText for warning,
and NegativeText for error. The current holonight-qt renderer supports Text,
Highlight, PositiveText, NeutralText and NegativeText; do not use Background or
HighlightedText on painted elements until its API and rendering tests support them.
Interaction states belong to consumer palettes, not newly duplicated artwork.
Existing application-requested status names and geometry must remain available.

Preserve fixed brands, application artwork, weather illustrations and intentional
shading. Record exact asset paths and a rationale in `metadata/fixed-artwork.json`.
Mixed artwork uses exact element IDs for fixed portions; its other paints must be
semantic. Whole-asset exemptions must never conceal semantic paints. Fixed assets
include an unused semantic stylesheet guard because holonight-qt otherwise tints
literal paints; keep that guard. Generated variants change stylesheet defaults only.

Update licensing and attribution when moving or adding artwork. Do not introduce
KDE Frameworks dependencies: render checks compile the actual holonight-qt renderer
against Qt. Run `task verify` for changes to this contract, tooling or artwork.
Inspect family previews on both backgrounds at 16/22/24/32 px and 2x. Automated
pixel checks do not replace visual review of small details, selection and disabled
contrast. Installation tests must use temporary XDG data directories.

Token templates are the explicit exception to stylesheet-only generation:
`metadata/templates.json` lists canonical sources, outputs and HoloNight class to
holonight-qt token mappings. Validate currentColor fills, strokes and gradient stops
before resolving to frozen literal artwork. Canonical templates use Dark defaults;
ship holonight-light for HoloNight and holonight-dark for HoloNight-Dark. Keep the unused standard
semantic guard in exports. Templates must not be hidden by fixed-artwork exemptions.
Keep the single installed template bundle outside icon lookup directories and
recolor only on explicit request, with staged validation and recoverable backups.
