# Size-aware Places and Devices contract

Baseline: `a8ee0fda299fddaef0d1ea67709d8ed90e499ffd`.

Ordinary name lookup at 16–24 px must use monochrome semantic artwork, and at 32 px and above colorful artwork. Explicit `-symbolic` names and aliases must use monochrome artwork and recolor from the GTK foreground at every size. Generated `index.theme` lookup must cover aliases, inheritance and scale 2. The current 24 px regular masters remain colorful pending a separate artwork change.

Acceptance: `task verify` must run isolated GTK 3 and GTK 4 processes against temporary installations of both generated variants. Each process must resolve and recognize all 20 canonical Places and Devices symbolic names and their explicit aliases at 24 and 32 px, then render each with two distinct GTK foreground colors and confirm visible pixel recoloring. Home and hard disk must also pass at every advertised size and at scale 2.

Historical local verification (2026-09-25): `task verify` passed (40 Python tests and generated-theme checks); GTK 3 foreground recoloring of installed Home and hard-disk symbolic icons passed with two colors, and GTK 4 recognized both as symbolic. That result predates the automated GTK acceptance check and does not establish GTK 4 recoloring. Generated fixtures must be rechecked when the replacement artwork is authored.
