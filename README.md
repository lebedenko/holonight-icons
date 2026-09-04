# HoloNight Icon Theme

HoloNight is a Linux icon theme that overrides selected icons from
`Papirus-Dark` while inheriting the rest from `Papirus-Dark`, `breeze-dark`,
and `hicolor`.

The theme is designed as a small override layer rather than a full icon set.
Icons not provided by HoloNight fall back through the inherited themes.

## Upstream

HoloNight is based on the Papirus icon theme project:
<https://github.com/PapirusDevelopmentTeam/papirus-icon-theme>

Use Papirus icon names and directory conventions when adding overrides. This
keeps HoloNight compatible with applications and desktop environments that
already resolve icons from Papirus.

## Structure

- `HoloNight/index.theme` defines the installable icon theme metadata.
- `HoloNight/scalable/*/` contains full-color SVG overrides grouped by icon context.
- `HoloNight/symbolic/{actions,status,devices,places}/` contains symbolic SVG overrides.
- `scripts/validate-theme.sh` checks the theme metadata and directory layout.
- `scripts/validate_icons.py` checks SVG structure, contracts, and aliases.
- `scripts/generate_icon_previews.py` renders repeatable family contact sheets.
- `scripts/install-local.sh` installs the theme into the current user's icon directory.

## Usage

Validate the scaffold:

```sh
task validate
task validate:icons
task verify
```

Install locally:

```sh
task install:local
```

Then select `HoloNight` in your desktop environment's appearance settings.

`task preview:icons` requires Inkscape and ImageMagick. It writes reviewed
contact sheets under `docs/sdd/icon-theme-compliance/previews/`. Structural
exceptions must be exact file entries in `scripts/icon-exceptions.json`; glob
and directory-wide exceptions are rejected.

## Adding Icons

Place SVG overrides in the matching context directory, for example:

- `HoloNight/scalable/apps/org.gnome.Terminal.svg`
- `HoloNight/scalable/places/folder-documents.svg`
- `HoloNight/scalable/mimetypes/text-x-python.svg`
- `HoloNight/symbolic/status/audio-volume-muted-symbolic.svg`

Use the same icon names as Papirus when replacing an existing icon.

## License

First-party project material is licensed under `GPL-3.0-or-later`. Papirus-derived icon families are retained under
`GPL-3.0-only`; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`LICENSES/`](LICENSES/).
