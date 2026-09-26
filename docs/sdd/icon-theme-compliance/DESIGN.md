# Implementation design

`scripts/theme.py` defines directory ordering, size ranges and variant defaults.
`scripts/build.py` validates canonical sources and emits complete themes under
ignored `build/`. `metadata/migration.json` maps each original master/alias to its
new path and records resolved alias targets. Native canvas sizes replace fake
size-directory aliases. Places keeps regular and explicit symbolic names together at 24 px; Devices
retains a separate symbolic directory.

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
Two real master directories provide monochrome semantic 24 px and colorful 32 px
artwork. Fifteen Places types and 15 colorful token templates are shipped. Extra optical masters require demonstrated visual need.
See [Places design](../../places-design.md) for explicit migration dispositions,
exact size ranges and Scale=2 index references to the existing directories.

Template exports resolve semantic tokens to frozen paints with the standard stylesheet
guard. Other generated artwork changes stylesheet defaults only. The immutable shared
bundle stays outside icon lookup directories. System packaging and its validation
contract are described in the [umbrella packaging SDD](../umbrella-packaging/README.md).
