# Implementation design

`scripts/theme.py` defines directory ordering, size ranges and variant defaults.
`scripts/build.py` validates canonical sources and emits complete themes under
ignored `build/`. `metadata/migration.json` maps each original master/alias to its
new path and records resolved alias targets. Native canvas sizes replace fake
size-directory aliases. Full-color directories precede symbolic directories;
both representations retain their original lookup names.

`scripts/validate_icons.py` checks XML, the restricted semantic CSS grammar,
inherited fill/stroke/color, exact exemptions, aliases and metadata. Generated
artwork is compared against the source with only the allowed stylesheet change.
`scripts/install.py` serializes concurrent installs, stages both themes on the
destination filesystem, validates, retains old themes and rolls back failures.

Rendering checks compile holonight-qt's IconRenderer directly with Qt Core/Gui/Svg.
No KDE dependency or replacement recoloring implementation is introduced. The
consumer's five supported roles are exercised; reserved background/selection-text
roles are not used by current artwork. Fixed-color assets carry a stylesheet guard
to avoid the consumer's legacy tinting fallback. See the [design contract](../../icon-design-rules.md).

Places permits only the relative size links declared in `metadata/places.json`.
Two empty real master directories, 24 and 32, reserve monochrome and colorful
artwork respectively. Extra optical masters require demonstrated visual need.
See [Places design](../../places-design.md) for pending migration dispositions,
exact size ranges and Scale=2 index references to the existing directories.
