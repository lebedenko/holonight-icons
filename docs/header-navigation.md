# Design: window-close Actions artwork

Actions supplies window-close at 24 and 32 px, monochrome semantic Text in both
theme variants. window-close-symbolic aliases the corresponding local master.
Existing 16/20/22 size-directory aliases reuse 24; larger requests follow existing
Actions lookup metadata. No new application-owned artwork is needed.

Viewer’s crossed diagonals retain their 24-unit endpoints at (6,6), (18,18),
(18,6), (6,18). The family 1.7-unit rounded stroke is represented by filled capsule
outlines because GTK 3 symbolic conversion drops straight open paths. The 32 px
master scales geometry and optical weight by 4/3. All paint uses currentColor and
the complete semantic stylesheet; applications supply interaction colors.

Actions proof_names and lookup_aliases extend existing rendering, direct/inherited
Qt lookup and GTK 3/4 recoloring checks. Generate themes through task build; run
validation, task check and isolated staging acceptance. Install the theme provider
before publishing applications that use its new icon. See actions-design.md and
the umbrella header-navigation contract. Native light/dark fractional-scale visual
parity remains a manual acceptance step.
