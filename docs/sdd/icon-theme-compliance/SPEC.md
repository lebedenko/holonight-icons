# Icon theme compliance specification

Status: Implemented; manual desktop review pending

## Baseline and scope

The checked-in baseline contains 154 real SVG masters and 58 symlink aliases. The audit found 77 folder masters,
12 panel masters, and three power-profile masters without `viewBox` declarations; five assets contained Inkscape or
Sodipodi metadata. First-party application tiles extended to `16…240`, Teams exceeded the panel safe area, Insync
states did not share one construction, and the Kiro filename did not match its installed icon contract.

This SDD covers theme-owned SVG structure, panel artwork, application artwork, folders, symbolic masters, aliases,
repeatable previews, and contributor validation. It does not change Qt, QML, C++, desktop entries, or runtime APIs.

## Requirements

- Every real SVG parses, renders, and declares its intended canvas.
- Symbolic assets contain no embedded images, text, filters, masks, clipping paths, editor metadata, or unsupported
  semantic classes.
- Aliases resolve to masters within the theme.
- First-party application artwork fits `20…236` on a 256-unit canvas.
- Insync states share base bounds within 0.5 unit and retain shape-readable state markers.
- Teams fits the `2…22` safe area; Bluetooth dots and disabled slashes remain intact.
- Kiro resolves as `kiro`; AWS VPN continues to resolve as `acvc-64`.
- Exact, reviewed exceptions are machine readable; wildcard exceptions are invalid.

## Deferred work

The existing fixed-size panel directory aliases and `index.theme` declarations are intentionally unchanged. Dedicated
panel sizes or migration to `scalable/status` require a separate SDD.
