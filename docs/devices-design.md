# Devices: five glyph families

The supplied `device-icons-moc.png` defines the silhouettes. These icons omit
its folder bodies and use only the hard disk platter and connector, SSD badge,
USB stick and trident, notched SD card, and optical disc. Both regular masters
use Home's cyan → blue → violet accent gradient. The 24 px master keeps a crisp
stroke; the 32 px master adds a faint stroke glow. SSD and SD labels are paths.

| Requested size | Master |
| --- | --- |
| 16, 20, 22, 24 | 24 monochrome semantic |
| 32, 48, 64, 96, 128, 256, 512 | 32 colorful |
| Every symbolic request | 24/symbolic monochrome |

This is the contract for replacement artwork. The current 24 px regular masters
are colorful; a separate artwork change must replace them. Verify ordinary and
`-symbolic` aliases with generated `index.theme` lookup at every advertised size,
scale 2, and through representative inheritance before claiming the small-size
result in Dolphin.

Every non-master size is a relative directory alias directly to its master.
Symbolic names use ColorScheme-Text/currentColor. Consumer palettes provide
selection and disabled states. `metadata/devices.json` declares the five names,
retained historical aliases, and explicit retirement of unrelated imported
Devices names. `metadata/migration.json` stays unchanged.

The ten regular masters are token templates. Canonical SVGs use Dark defaults;
the exporter freezes HoloNight light and HoloNight-Dark dark colors. The five
symbolic masters remain theme responsive. Retained historical names are
`drive-removable-media`, `media-flash-sd-mmc`, `media-optical-data` and
`media-optical-mixed-cd`, including their symbolic-directory spellings.

Visual review on 2026-09-25 covered both variants on light and dark backgrounds
at 16/22/24/32 px and 2×, plus selected surfaces and 45% disabled opacity.
The HDD platter, USB trident and disc stay distinct at small sizes. SSD and SD
lettering becomes legible at 22 px and above; the 16 px outline remains the
primary cue. Symbolic states keep their counters and respond to the selected
foreground. Regular selected artwork has lower contrast on blue surfaces because
the accent gradient is frozen; the consumer should choose a contrasting selection
surface. `task verify` passed all 40 tests, actual Qt rendering and lookup checks,
temporary-XDG installation checks and REUSE validation.
