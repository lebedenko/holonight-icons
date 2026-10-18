# Generic notification artwork

The five `dialog-information`, `dialog-error`, `dialog-warning`, `dialog-question`
and `dialog-positive` Status glyphs show a circled i, cross, warning triangle,
question mark and check. `application-x-executable` provides the generic application
fallback as a window with a four-cell grid. Every name has an explicit `-symbolic`
alias, with identical monochrome Text artwork. Consumers supply urgency accents,
selection and disabled treatments; the shell retains its existing fallback selection.

Status uses original 24-unit masters, rounded 1.7-unit strokes and a 2-unit safe
area. Its existing 16–32 scalable ranges remain intact, including scale-2 entries;
larger requests scale the nearest local master. MIME types reuse their established
24/32 masters and directory aliases, with proportionally scaled executable geometry.
These monochrome names are exceptions to colorful large Places and Devices artwork.

`metadata/status.json` declares only this subset, leaving tray artwork independent.
Source and generated validation require real square semantic Text masters and exact
same-directory aliases. Qt compares all twelve names against local masters at every
advertised size, both scales and variants, directly and through inheritance. GTK 3/4
checks all six symbolic names for local resolution and visible foreground recoloring.
Outline contact sheets cover 16/20/22/24/32 at both scales on light/dark backgrounds
with normal, selected, disabled and notification-accent treatments under `build/previews`.
New artwork is first-party GPL-3.0-or-later; imported MIME provenance stays unchanged.
Notification bells and shell urgency mapping remain outside this design.
