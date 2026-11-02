# Devices: nine glyph families

The supplied `device-icons-moc.png` defines the silhouettes. These icons omit
its folder bodies and use only the hard disk platter and connector, SSD badge,
USB stick and trident, notched SD card, and optical disc. The sixth family, `input-mouse`, preserves the supplied
24 px rounded mouse outline and wheel mark without extra buttons or badges. The 24 px regular
master uses a crisp monochrome semantic stroke. The colorful 32 px master uses
Home's cyan → blue → violet accent gradient and a faint stroke glow. SSD and SD
labels are paths.

Keyboard, headphones and headset bring the set to nine families. The keyboard
keeps its 18×12 rounded frame with eight 1.5×1.5 keys and a separated spacebar.
Headphones and headset preserve the supplied earcups, headband and microphone.
Their 24 px masters use complete semantic stylesheets and 1.7-unit outlines.
Their 32 px templates share a user-coordinate diagonal cyan → blue → violet
gradient, 1.65-unit outlines and a faint 2.4-unit outline glow; filled details
remain filled without expanded glow. Virtual-keyboard names remain retired.

| Requested size | Master |
| --- | --- |
| 16, 20, 22, 24 | 24 monochrome semantic |
| 32, 48, 64, 96, 128, 256, 512 | 32 colorful |
| Every symbolic request | 24 monochrome via a same-directory `-symbolic` link |

The 24 px regular masters and explicit symbolic names share the same semantic
monochrome artwork. Historical `24/symbolic/` paths remain compatibility links. Verify ordinary and
`-symbolic` aliases with generated `index.theme` lookup at every advertised size,
scale 2, and through representative inheritance before claiming the small-size
result in Dolphin.

Every non-master size is a relative directory alias directly to its master.
Symbolic names use ColorScheme-Text/currentColor. Consumer palettes provide
selection and disabled states. `metadata/devices.json` declares the nine names,
retained historical aliases, and explicit retirement of unrelated imported
Devices names. `metadata/migration.json` stays unchanged.

The nine colorful 32 px regular masters are token templates. Canonical SVGs use Dark defaults;
the exporter freezes HoloNight light and HoloNight-Dark dark colors. The nine
symbolic masters remain theme responsive. Retained historical names are
`drive-removable-media`, `media-flash-sd-mmc`, `media-optical-data` and
`media-optical-mixed-cd`, including their symbolic-directory spellings.

Visual review on 2026-09-27 covered both variants on light and dark backgrounds
at 16/22/24/32 px and 2×, plus selected surfaces and 45% disabled opacity.
The HDD platter, USB trident and disc stay distinct at small sizes. SSD and SD
lettering becomes legible at 22 px and above; the 16 px outline remains the
primary cue. Symbolic states keep their counters and respond to the selected
foreground. Regular selected artwork has lower contrast on blue surfaces because
the accent gradient is frozen; the consumer should choose a contrasting selection
surface. `task verify` passed all 40 tests, actual Qt rendering and lookup checks,
temporary-XDG installation checks and REUSE validation.

Mouse review on 2026-11-02 covered Qt regular and symbolic state sheets at
16/22/24/32 px and 2× on light and dark backgrounds, selected surfaces and
45% disabled opacity. The rounded outline and wheel remain distinct with no
clipping. Symbolic artwork follows the consumer foreground in all states.
Ordinary semantic artwork rendered without palette support uses the theme's
default foreground, so a mismatched background can reduce contrast; the colorful
32 px master retains the shared Devices gradient and restrained glow.

Keyboard and audio review on 2026-11-02 covered actual Qt regular and symbolic
state sheets at 16/22/24/32 px and 2× in both variants on light and dark
backgrounds, selected surfaces and 45% disabled opacity. Keyboard keys and
spacebar remain separated from each other and the frame. The headset boom and
filled microphone remain visible at 16 px and distinguish it from headphones;
no outline clipping is visible. Symbolic selected and disabled states retain
the silhouettes and follow the foreground. Ordinary small artwork retains the
same default-foreground limitation documented for mouse on mismatched surfaces.
The colorful audio glyphs share one diagonal gradient across their filled and
outlined details, with glow confined to outlines.
