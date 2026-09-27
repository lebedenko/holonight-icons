# Places artwork and lookup

Places has two authored sizes. The 24 px directory supplies monochrome semantic
regular artwork for ordinary requests at 16, 20, 22, and 24 px. The 32 px
directory supplies colorful regular artwork at 32, 48, 64, 96, 128, 256, and
512 px. Each other size directory is a relative symlink to the corresponding
master. `index.theme` advertises every size and scale 2.

The eighteen 24 px regular masters are glyph-only semantic sources:
Home, folder, Downloads, Documents, Desktop, Pictures, Music, Videos, Projects,
Templates, Public, Build, Bookmark, Network, Recent, empty Trash, full Trash,
and open folder. They use
`ColorScheme-Text` and `currentColor`, with no fixed paint. Each explicit
`-symbolic.svg` name is a same-directory link to its regular master, so GTK can
recognize and recolor the symbolic name at every requested size. The same small
semantic master is used for symbolic requests larger than 24 px.

The colorful 32 px masters retain the shared folder body and interior glyphs.
Home has a rounded house and an open doorway. The generic folder removes the
house layers and roof highlight. Other folder types add their corresponding
glyphs. Soft interior glow, rim gradients, and folder shading remain at 32 px.
The 32 px sources are the eighteen Places entries in `metadata/templates.json`;
there are no 24 px Places token templates. Token recoloring applies only after
an explicit command, and the generated themes contain frozen colorful masters.

`metadata/places.json` declares regular and symbolic lookup aliases. Regular
aliases such as `user-home.svg`, `inode-directory.svg`, and `folder-downloads.svg`
resolve within each master size. Historical symbolic names such as
`user-home-symbolic.svg` and `folder-sound-symbolic.svg` live beside the 24 px
regular masters and link to the corresponding semantic artwork. The historical
`folder-sound.svg` also has a colorful 32 px alias. `folder-development`
links to Projects at both master sizes; its explicit symbolic name links to
the 24 px Projects glyph. Build, Bookmark, and Network have tool, ribbon,
and connected nodes glyphs without a folder body at 24 px. The migration
inventory in
`metadata/migration.json` records the flat 24 px paths; deferred historical
names stay deferred.

The 24 px safe area is x/y 2–22. Start new stroked symbols with rounded
1.7-unit strokes and gaps of at least 1.5 units; check their visible bounds at
16 px. The 32 px safe area is x/y 2–30. Preserve the visual family across the
24-to-32 transition while letting the large artwork show its color and detail.
See [canvas rules](icon-canvas-rules.md) and the
[artwork contract](icon-design-rules.md).

Run `task verify` after source or metadata changes. The validation, Qt lookup,
GTK symbolic recoloring, and preview checks cover both generated themes.
Inspect `build/previews/folder-family-*.png` and the folder state sheets at
16, 22, 24, and 32 px on light and dark backgrounds, at 1× and 2×.
