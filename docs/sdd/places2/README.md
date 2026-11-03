# Places2 adoption

Adopt the sixteen first-party SVGs from `iconset/places2/32` without changing their geometry, cutouts or open-folder paper. Folder material uses Accent; glyphs and paper use Text. Replace shading CSS with the exact `front-shading` black element at 35% opacity and register element exemptions only. Use existing palette defaults.

Extract the filled glyphs into 24 px masters, uniformly fitting their geometry into the 2–22 safe area. Preserve the plain/open semantic outlines. Build, Bookmark, Recent and full Trash retain their existing 24 px motifs, scaled into the supplied body at 32 px. Empty/full Trash remain distinct. All twenty designs keep ordinary small monochrome and large colorful lookup; explicit symbolic names always reuse 24 px.

Places is no longer a frozen token template: KDE can independently recolor Accent and Text. Explicit token recoloring applies only to Devices and must leave Places bytes unchanged. Aliases remain local; generated themes are rebuilt, never hand-edited. No external source edits or desktop installation.

Acceptance: focused Places/template regressions, task check, native KDE generated 24/32 px tests, task check:integration, direct/inherited lookup and GTK symbolic checks, visual review at 16/20/22/24/32 and both scales on light/dark/checkerboard. Preserve the known failing KDE Accent-only cache-refresh assertion and report it separately; desktop refresh is not proven.

## Import mapping and SHA-256

Source: `/home/andrii/Projects/graphics/iconset/places2/32`. First-party artwork uses the repository copyright and GPL-3.0-or-later license.

| Source | Canonical name | SHA-256 |
| --- | --- | --- |
| folder-archive.svg | folder-archive | `9602c6e9770f8e3c7f47bee1b7bb0dfb9efb0e39438877423db15803fc92716b` |
| folder-desktop.svg | folder-desktop | `6559be2ecb80a47359db362c1bef81aed534f4604c4579be3ee801596d631866` |
| folder-development.svg | folder-projects | `8f5b046c651eb0da7b2c3418f1f2db4ec9ac34c0b3dcc9752938040a8093a821` |
| folder-documents.svg | folder-documents | `db7b7265e99add5bd28961091456066eeabcc80a7904e09c7f26a3a47eb7fd9f` |
| folder-download.svg | folder-download | `ae0b2c55bcf33603b33b18b9eefc9eeabc84ed2c3b8f14cc8c463d2b1cd1e1b2` |
| folder-home.svg | folder-home | `8d9f086c82196d34512537ae09621877579dcb93c6a4c51d7600f2f6cfd9c11c` |
| folder-network.svg | folder-network | `481b2acaa2b25f87961c5462e3f6b50c985156fea5ce59afd318e045f309ea37` |
| folder-open.svg | folder-open | `783c8003cf9a6a22f08281f06f6c8d4430184de9815d7ba6acf6dd5d803262ee` |
| folder-pictures.svg | folder-pictures | `558ed2e8785f22073ebfa8e463458f0088b8c53299ae0aa260f8db54ef138bbd` |
| folder-publicshare.svg | folder-public | `33ab6cca28f5c58fafe3a07445ffc75f7554dfee8db27c9721f82ae54cbd9e16` |
| folder-remote.svg | folder-remote | `220a2cd7d6ca2ff591bfd0e873842f67059e900aacd204d6b9368851fe648861` |
| folder-sound.svg | folder-music | `d5fcd88da77e1e7cf036ca31cbfcd7a790e88b7a1900d6a128571dd7befbe74e` |
| folder-templates.svg | folder-templates | `1861414c5e20b613fb939829bb4e7a41d321ded2667f00ff098b442a9096f2a7` |
| folder-videos.svg | folder-videos | `afe3d22f839c54df5b69ff5553f919889df639350bde34478a11cb80a913e592` |
| folder.svg | folder | `c3b6d40962fcb4e3b981883d39605a0f15d1ef3c695dc9ec632b3dde4452c0cc` |
| user-trash.svg | folder-trash | `fe2756da34666451b15e208c58a363807a364c3d487ea4cfda88daa150b4ce6b` |

## Visual review

Reviewed all twenty designs at 16/20/22/24/32 px and both scales on light, dark
and checkerboard backgrounds. Filled cutouts remain open, the open folder retains
its paper insert, and full Trash is visibly distinct from empty Trash. Projects
uses the supplied rounded strokes; its 24 px glyph is fitted using painted bounds
including joins, which extend beyond Qt's reported element bounds.

The default light Text color has relatively low contrast against the shaded blue
folder face. The requested palette defaults are preserved. Small semantic artwork
requires a matching theme or consumer recoloring on the opposite background;
these static fallback-color previews do not imply palette adaptation.
