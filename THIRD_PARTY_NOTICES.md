# Third-party notices and provenance

Artwork in `icons/status/24/symbolic/` retains the previous scalable/symbolic families'
Papirus provenance. It is licensed GPL-3.0-only and attributed to the Papirus
Development Team and 2026 Andrii L <lebeden@gmail.com>. The remaining independently
authored status artwork, tooling, metadata and documentation are GPL-3.0-or-later.
See REUSE.toml for the exact path annotations. In generated/installed themes the
same paths appear without the `icons/` prefix and carry equivalent REUSE metadata
and both license texts. Aliases refer to the same licensed artwork.

Upstream: [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme).
Migration retains existing silhouettes, brand colors and decorative shading;
semantic defaults now vary by light/dark theme. Full-color SVGs include an unused
stylesheet guard to preserve their paints through holonight-qt's renderer.

Light, Dark, Day and Storm colors are an offline snapshot of holonight-qt's
`palette/palette.cpp` (`holoNightLightTokens`, `holoNightDarkTokens`, `tokyoNightDayTokens`,
`tokyoNightStormTokens`) and matching
`data/holonight-{light,dark,day,storm}.colors`, recorded 2026-09-23. The metadata records
semantic role mapping. The independently authored Home artwork at
`icons/places/32/folder-home.svg`, `icons/places/24/folder-home.svg` and
`icons/places/24/folder-home-symbolic.svg`, including their user-home
aliases, refines the supplied HoloNight mockup and revised draft, with house glow
and inset folder lighting in the 32 px master; copyright 2026 Andrii L <lebeden@gmail.com>,
GPL-3.0-or-later. Its canonical source and generated literal variants share that
attribution. The generic folder derivatives at `icons/places/24/folder.svg`,
`icons/places/32/folder.svg` and `icons/places/24/folder-symbolic.svg`,
including their inode-directory and symbolic folder aliases, share this first-party
copyright and GPL-3.0-or-later license. The Downloads derivatives at
`icons/places/24/folder-download.svg`, `icons/places/32/folder-download.svg` and
`icons/places/24/folder-download-symbolic.svg`, with their folder-downloads
and historical symbolic folder-download aliases, share this first-party copyright
and GPL-3.0-or-later license. Their arrow-and-tray motif follows the supplied
mockup description in the implementation plan; the mockup image was unavailable.
The installed template bundle includes REUSE metadata and licenses.
No KDE source code or library is shipped in the theme. Rendering tests compile the
GPL-3.0-or-later IconRenderer from a separate holonight-qt checkout without copying
or distributing it as part of the installed themes.

The HDD, SSD, USB drive, SD card and optical drive glyphs at
`icons/devices/{24,32}/` and `icons/devices/24/symbolic/` are first-party
artwork by Andrii L (2026), licensed GPL-3.0-or-later. They follow the supplied
Devices mockup silhouettes and Home accent gradient. Historical lookup aliases,
generated exports and installed canonical templates carry the same attribution.

Names and marks represented by provider, distribution, product and application
icons belong to their respective owners. Their use identifies compatible software
and does not imply sponsorship, endorsement or ownership of those trademarks.

Documents artwork at `icons/places/24/folder-documents.svg`,
`icons/places/32/folder-documents.svg` and
`icons/places/24/folder-documents-symbolic.svg` adapts the page glyph
from the first-party `places.png` reference onto the approved folder bodies.
Copyright 2026 Andrii L; GPL-3.0-or-later.

Desktop, Pictures, Music, Videos, Projects, Templates and Public artwork at
`icons/places/{24,32}/folder-{desktop,pictures,music,videos,projects,templates,public}.svg`
and `icons/places/24/folder-{desktop,pictures,music,videos,projects,templates,public}-symbolic.svg`
uses the first-party `places.png` silhouettes with the approved Home folder bodies
and shared gradient. Copyright 2026 Andrii L <lebeden@gmail.com>;
GPL-3.0-or-later. REUSE.toml enumerates all 21 canonical paths explicitly.
The restored regular and symbolic aliases, generated exports and installed
canonical template bundle carry the same attribution.


Recent and Trash artwork at
`icons/places/{24,32}/folder-{recent,trash,trash-full}.svg` and
`icons/places/24/folder-{recent,trash,trash-full}-symbolic.svg` is first-party
artwork by Andrii L (2026), licensed GPL-3.0-or-later. Recent's clock and empty
Trash's bin adapt the first-party `places.png` reference; the raised lid and paper
shapes of full Trash are original additions. Regular versions reuse the approved
Home-derived generic folder body. Alias files resolve to these same artworks.

The chevrons at `icons/actions/{24,32}/chevron-{up,down,left,right}.svg`
adapt the supplied first-party drafts. Their regular and symbolic go-up,
go-down, go-next and go-previous aliases, generated exports and installed
artwork share copyright 2026 Andrii L <lebeden@gmail.com> and GPL-3.0-or-later.

## MIME-type import

The 32 MIME-type designs at `icons/mimetypes/{24,32}/` and their aliases
are derived from Papirus icon theme, installed package version `20260801-1`,
imported on 2026-09-29. Copyright Papirus Development Team; GPL-3.0-only.
Upstream: https://github.com/PapirusDevelopmentTeam/papirus-icon-theme.
Modifications by Andrii L (2026-09-29): add explicit viewBox metadata where
absent and an unused semantic stylesheet guard for HoloNight rendering.
Original geometry, layers, colors and opacity are preserved.
`metadata/mimetypes.json` records source checksums and flattened internal aliases.
These imports retain fixed paints pending a separate semantic recoloring pass.

`tests/kde/application-xml.svg` is a Papirus-derived 32 px XML prototype,
GPL-3.0-only, modified by Andrii L on 2026-09-30: paper and fold use Text,
the glyph uses Accent, and translucent black shadows are explicit.
Original path geometry, layer order and white edge lighting remain intact.

Reviewed EPUB and JSON 32 px masters were adapted by Andrii L on 2026-09-30
as semantic Text paper/fold and Accent glyph artwork, preserving Papirus paths,
layer order, opacity, stroke attributes and decorative black/white paints.
Their 24 px masters remain unchanged apart from the unused Accent declaration.

## Applications refresh

The seven HoloNight and Strata application masters in `icons/apps/170/` and
their filename aliases are supplied first-party artwork, copyright 2026 Andrii L
<lebeden@gmail.com>, GPL-3.0-or-later. Imported canvases, geometry, gradients,
transparency and colors are preserved; only an unused semantic stylesheet guard
is added. `metadata/apps.json` records source checksums, aliases and historical
replacement targets. Kiro and AWS VPN Client (acvc-64) remain retired pending
verified redistribution permission.
