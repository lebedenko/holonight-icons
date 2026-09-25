# HoloNight Icons

This repository owns source artwork, aliases, theme metadata, and generated icon themes.
Read `docs/icon-design-rules.md` and the relevant Places or Devices specification before editing artwork.

Ordinary Places and Devices icon names must resolve to monochrome semantic artwork at 16, 20, 22, and 24 px and colorful artwork at 32 px and above. Explicit `-symbolic` names must stay monochrome and GTK-recolorable at every size. Keep aliases within the theme and verify lookup through `index.theme` at every advertised size, including inherited themes and scale 2 entries.

Do not edit generated themes directly. Run `task verify` after source, metadata, or generator changes. Keep artwork and documentation changes in this repository; shared Qt rendering belongs to `holonight-qt`.
