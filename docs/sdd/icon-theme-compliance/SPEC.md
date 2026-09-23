# Theme specification

The maintained production contract is [icon-design-rules.md](../../icon-design-rules.md).
This replaces the previous dark-only layout and fixed asset-count requirements.

Produce HoloNight (light) and HoloNight-Dark (dark), each with complete artwork,
internal aliases, scalable directory metadata and explicit recursive inheritance.
Preserve every lookup and alias in `metadata/migration.json`. Build offline from
one context-first source tree; change semantic defaults only. Validate inherited
paints, CSS, metadata, aliases and exemptions. Install with staging, backups and
rollback. Test the actual holonight-qt renderer without KDE Frameworks dependencies.
GTK recoloring and automated theme selection are outside scope.
