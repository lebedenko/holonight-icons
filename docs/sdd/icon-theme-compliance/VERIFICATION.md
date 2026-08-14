# Icon theme compliance verification

## Automated verification

Verification date: 2026-08-14

Run from the `holonight-icons` repository:

```sh
task validate
task validate:icons
task verify
```

The aggregate gate parses theme metadata and every real SVG, validates structural and upstream contracts, checks all
aliases, queries application/Insync/Teams bounds with Inkscape, renders every master at reviewed sizes, and composes
the tracked contact sheets.

Results:

- `task validate`: passed; theme metadata is valid.
- `task validate:icons`: passed; 154 SVG masters and 58 aliases validated.
- `task verify`: passed; all four after contact sheets regenerated.
- `task install:local`: passed; installed to `~/.local/share/icons/HoloNight` and refreshed the KDE service cache.

## Exceptions

- `HoloNight/scalable/apps/kiro.svg`: official 75 × 100 brand canvas; reviewed at every application target size.
- `HoloNight/scalable/apps/acvc-64.svg`: AWS VPN's explicit `acvc-64` 64-unit contract; reviewed at every application
  target size.

The authoritative structured details are in `scripts/icon-exceptions.json`.

## Visual evidence

Before and after contact sheets are tracked in `previews/before/` and `previews/after/` for applications, folders,
panel icons, and symbolic masters.

## Manual verification

Reviewer: pending developer review

`task install:local` and the desktop inspection checklist remain pending because they mutate the user's installed icon
theme and require manual, focus-dependent interaction. After review, record the reviewer, date, command result, and
observations here before changing the SDD status to complete.
