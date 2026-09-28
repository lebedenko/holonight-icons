# Actions: four chevrons

The supplied drafts in `drafts/actions/` remain reference artwork. The 24 px
masters preserve their geometry and rounded caps/joins with a 1.7-unit stroke
and the complete semantic stylesheet. The 32-unit canvases scale the geometry
and stroke by 4/3 (effective stroke 2.266667 px). Both use only
ColorScheme-Text/currentColor.

`metadata/actions.json` declares real 24/32 masters and only the relative size
links 16 → 24, 20 → 24 and 22 → 24. Both generated themes advertise those five
exact sizes, including scale 2. Requests through 24 px select the 24 master;
32 px and larger select the 32 master with nearest-size scaling as needed.

At both master sizes, go-up → chevron-up, go-down → chevron-down,
go-next → chevron-right and go-previous → chevron-left are same-directory SVG
symlinks. The four go-*-symbolic aliases target the same monochrome artwork for
GTK recoloring. Original migrated navigation paths remain available. Endpoint
navigation aliases are deferred until they have distinct artwork.

Run `task verify` to check master canvases, semantic paints, aliases, exact
metadata, Qt lookup in both variants and through inheritance, larger fallback,
GTK 3/4 foreground recoloring and REUSE attribution. Inspect
`build/previews/outline-*-states.png` for light/dark backgrounds, selected and
disabled treatments at 16/20/22/24/32 px and 2×.
