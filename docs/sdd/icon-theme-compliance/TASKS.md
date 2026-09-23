# Maintained entry points

| Command | Result |
| --- | --- |
| `task build` | Both complete variants in `build/` |
| `task validate` / `task validate:icons` | Build, source/inventory/alias/metadata validation |
| `task test` | SVG fixtures, deterministic builds, staged/repeat/rollback installation |
| `task test:render` | Real holonight-qt renderer plus Qt lookup |
| `task preview:icons` | Light/dark family PNG sheets, 1× and 2× |
| `task license-check` | REUSE attribution checks |
| `task verify` | All checks and previews |
| `task install:local` | Staged user installation with recoverable backups |

Python and shell equivalents are in the root README. The old asset-count checklist
and legacy layout tasks are superseded by the migration inventory and automated
regression suite. Manual consumer UI review remains useful for new artwork.
