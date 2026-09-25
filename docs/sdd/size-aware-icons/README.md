# Size-aware Places and Devices contract

Baseline: `a8ee0fda299fddaef0d1ea67709d8ed90e499ffd`.

Document ordinary name lookup at 16–24 px as monochrome semantic, at 32 px and above as colorful, and explicit `-symbolic` lookup as monochrome at every size. Require generated `index.theme`, alias, inheritance, scale 2, GTK 3 recoloring, and GTK 4 recognition checks for the later artwork change. This work changes documentation only; current 24 px regular masters remain colorful.

Implementation: `AGENTS.md`, `docs/icon-design-rules.md`, `docs/places-design.md`, and `docs/devices-design.md`. Local verification (2026-09-25): `task verify` passed (40 Python tests and generated-theme checks); GTK 3 foreground recoloring of installed Home and hard-disk symbolic icons passed with two colors, and GTK 4 recognized both as symbolic. Generated fixtures must be rechecked when the replacement artwork is authored.
