# Reviewed EPUB and JSON semantic masters

The 32 px EPUB and JSON masters use Text paper/fold and independent Accent glyphs.
JSON retains fill:none and its original rounded 1 px stroke. Seven stable layer
IDs preserve order; only the four black/white decorative layers are exempt.
All path data, opacity and non-color stroke attributes match the imported Papirus
masters, recorded in `tests/fixtures/mimetype-geometry.json`. The original 24 px
masters retain fixed paint. Other MIME types remain at their import baseline.

Accent maps to primary with the same default as Highlight, but is a distinct role.
Unused Accent declarations on other sources and fixtures maintain compatibility;
they do not change painted artwork. Template custom declarations are preserved.

## Verification and visual review (2026-09-30)

- Source/build validation and 44 regression tests passed, including Accent fill,
  Accent stroke, missing/unknown/duplicate roles, literal paints, stale element
  exemptions and imported geometry/layer order.
- Shared renderer probes explicitly supply all eight colors, with distinct Accent
  and Highlight. Accent-only changes update the 32 px glyph and preserve paper
  pixels and all authored bytes after the stylesheet, including decorative paint.
- Shared state resolution checks normal, selected and disabled artwork; selected
  paper and glyph remain distinct. Disabled uses the existing background blending
  policy without KDE's whole-image effect.
- Authored 24 and 32 px masters have comparison sheets at 1x and 2x, in both themes:
  `build/previews/semantic-mimetypes/`. Columns are Normal, Selected and Disabled;
  selected cells use the selection background. Small antialiased strokes retain
  coverage; native 32 px JSON braces and EPUB counters remain open.
- Native KDE 6.30.0 / Qt 6.11.2 passed 24 artwork renders per edited master: both
  palettes, normal/selected/disabled, 24/32 px, 1x/2x. Geometry/alpha, literal shading,
  independent roles, selected separation and isolated lookup passed. Native 24 px
  samples scale the supplied 32 px master; the shared sheets separately review
  the authored 24 px master.
- Both native runs reproduced the known Accent-only cached-name refresh failure;
  uncached names use the new Accent. This is an isolated KIconLoader API result,
  not an assertion about Plasma/Dolphin notifications or an artwork failure.

Native reports and sheets are saved independently in `build/kde/epub/` and
`build/kde/json/`. Reproduce with:

```sh
python3 scripts/check-kde.py icons/mimetypes/32/application-epub+zip.svg --output build/kde/epub
python3 scripts/check-kde.py icons/mimetypes/32/application-json.svg --output build/kde/json
```

Both commands currently return 1 for the documented native palette cache refresh
failure after saving successful artwork comparisons. Standard verification retains
both theme variants, advertised size and scale 2 lookup, aliases and inheritance.
Palette contrast remediation is proposed in the sibling repository's
[selection color consistency tasks](../../holonight-qt/docs/sdd/selection-color-consistency/TASKS.md).

Final `task verify` passed: both themes generated and validated, 44 regression
tests, 278 shared-renderer masters, GTK 3/4 symbolic checks, preview generation
and REUSE checks for sources, both themes and template bundle. The GTK checks
required running outside the sandbox for Xvfb display access. `git diff --check`
also passed. Full verification output: `build/reports/mimetype-verify.log`.
