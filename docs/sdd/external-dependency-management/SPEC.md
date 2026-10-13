# External dependency management — holonight-icons

Work package: EDM-008
Audit baseline: `a8debec1399b59c218b2faa8f54047e5d3bc7984`
Umbrella audit: `38146d8f474317f3f8d72699f60e6d16a71dd165`
Implementation baseline: `7684b021a5b74c7d4e34b7dd05bb3bdd02456473`
Status: Locally verified; canonical bundle 2.0.0 and qualified Arch image accepted.

## Requirements

- Configuration and normal build commands shall never acquire dependencies or prepare source providers.
- `task deps` shall explicitly prepare supplied local providers and check installed external prerequisites.
- Internal providers shall resolve only from approved prefixes; external packages shall resolve from an explicit
  external prefix or normal system locations.
- Enabled dependency-dependent features shall require their dependencies; minimal profiles shall disable them explicitly.
- Where production components use Qt, discovery shall require >=6.11; private Qt components shall match
  the selected public version exactly.
- Where tests use GTest, consumers shall require installed GTest >=1.14 CONFIG and any GMock targets they use.
- Existing public APIs, component switches, install-tree consumers and acceptance coverage shall be preserved.

## Design

Adopt canonical `tooling/modules/holonight-icons.json` and `.cmake`, then synchronize bundle 2.0.0 into this repository.
The copied metadata is owned by this standalone checkout. CMake performs authoritative discovery; shared probes
provide prerequisite diagnostics and record resolved versions/paths. Incompatible caches and local provider install
trees are archived before reuse. Package acquisition occurs only in explicit environment preparation. CI switches
build/runtime/release lanes together to qualified immutable images and runs acceptance offline after preparation.

Preserve all Qt/GTK renderer and inheritance acceptance, including optional KDE verification, font, licensing and package tests. No artwork changes.

## Implementation and verification tasks

- [x] Confirm the exact baseline and canonical handoff before implementation.
- [x] Adopt declarations, prefix helpers, explicit preparation and compatibility signatures.
- [x] Apply the repository-specific discovery changes above.
- [x] Update Task, CI preparation/entrypoints, Dockerfiles, release lanes and contributor instructions.
- [x] Run declaration/CMake/profile consistency checks and offline missing-package regressions.
- [x] Run narrow regressions, clean acceptance, installed-package consumers and required quality checks.
- [x] Inspect complete logs; record commands, versions, features, warnings and manual checks.
- [x] Make a repository-local commit only after local verification; publish only when authorized.

## Icons contract

Generation, staging, installation and recoloring remain Python-only. No GTest is required.
Test-only Qt/GTK/introspection/loaders/Xvfb/font declarations are controlled by
`VERIFY_RENDERERS` (default ON); native `VERIFY_KDE` defaults OFF and requires
Qt >=6.11 plus `KF6::IconThemes`. Production package profiles contain Python and
hicolor only. Both C++ tools retain C++23 and authoritative version/target discovery.

`task deps` validates installed prerequisites and copies only the hash-verified actual
IconRenderer cpp/header from explicit `HOLONIGHT_QT_SOURCE`. The source content contract
is revision `7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`; normal rendering uses
`build/deps/renderer` and performs no preparation or acquisition. The exact file hashes
are in `scripts/renderer-fixture.json`. Stale/incompatible prepared trees and renderer
build caches are archived. Missing preparation preserves existing cache contents.

CI `--prepare` pulls the immutable build image
`ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`
and the separate existing REUSE image, exports the exact renderer revision from a
supplied checkout or explicit canonical acquisition, and invokes `task deps`. Acceptance
validates hashed preparation identities before launching containers, then runs offline
with read-only prepared inputs, caller accounts and private runtime directories.
Verification and licensing names/uploads are preserved; minimal, release and static
lanes add isolation, production packaging and canonical strict quality checks.
Supplementary package downloads and root bootstrap are retired.

Artwork, aliases, metadata, payload inventory, recovery and existing assertions are
unchanged. Behavior-preserving C++ formatting/tidy cleanup is committed separately. Canonical tidy
configuration stays byte-identical to bundle 2.0.0, with warnings treated as errors.
Eight exhaustive test/preview matrix functions retain narrowly documented cognitive
complexity exemptions to preserve original assertion order; no other checks are disabled.
The enabled tool database filters only the same unsupported GCC flags as the bundle;
KDE database coverage is conditional on its explicitly enabled prerequisite.

## Verification evidence

Clean acceptance on 2026-10-13 passed in all five lanes. Full local logs are retained
at `build/ci/20261013T081036Z-qqve3cdb`; structured evidence, fixture hashes, preparation
identities and installed packages/toolchain versions are checked in under
[verification](verification/acceptance.json). Acceptance tested the complete implementation
working tree at the implementation baseline (dirty snapshot); subsequent changes add
documentation/evidence, CI artifact uploads and the focused GTK regression described below.

Commands and results:

- `python3 scripts/ci/test_launcher.py`: 8/8 pass, including missing/incompatible/tampered
  preparation, zero acceptance containers on missing preparation, rootless/offline
  command contracts, read-only mounts, spaces, failed-lane propagation and archival.
- `python3 scripts/ci/test_dependencies.py`: 11/11 pass, including old/missing Qt,
  missing Qt/KDE targets/packages and both GTK pkg-config packages,
  Cairo/GTK introspection/loaders/font/Xvfb failures,
  Python-only isolation, production profiles, explicit fixture sources and stale caches.
- `python3 scripts/ci/run.py --prepare --qt-source ../holonight-qt`: pass, approved
  provider export and explicit `task deps` in the immutable qualified environment.
- `python3 scripts/ci/run.py`: verification, licensing, minimal, release, static pass.
  Verification and minimal each pass all 47 existing Python regressions. Verification
  renders 282 masters at 12 sizes/scales and four palettes; temporary Places/Actions
  inherited lookups pass all 11 sizes at 1x/2x. GTK3 and GTK4 each pass 174 symbolic
  lookups/two-color renders per theme. Preview generation passes.
- Release staging validates both themes and the template bundle with no compiled test
  artifacts. Existing installation, rollback, recoloring and recovery tests pass.
- Canonical formatting passes for both owned C++ tools. Enabled Qt renderer strict tidy
  passes with the canonical warnings-as-errors configuration. Native KDE compile/tidy
  is conditional, not claimed in this environment.
- All four REUSE roots pass using REUSE 6.2.0 in the separate licensing image.
- Umbrella `python3 tooling/sync.py --check --module holonight-icons`,
  `python3 tooling/generate-install-profile.py --check`, declaration validation and
  `git diff --check`: pass. Local/canonical module JSON and CMake are identical.
  Production profiles exclude all renderer/test requirements; no GTest is declared.

Qualified toolchain: GCC 16.2.1, CMake 4.4.3, Clang 22.1.8, Python 3.14.7,
Qt Core/Gui/Svg 6.11.2, GTK3 3.24.52 and GTK4 4.22.5. REUSE image Python is 3.12.12.
Complete package versions are in `verification/packages.txt`.
After full acceptance, an additional explicit missing-GTK-package regression was added;
all 11 dependency tests passed again on the host and in the same immutable image with
`--pull=never --network=none`, caller UID and read-only source. Unchanged rendering,
build, staging and static acceptance results remain valid. Documentation/evidence and
artifact-upload closure passed workflow YAML validation and a focused four-root licensing
rerun at `build/ci/20261013T081504Z-5_8m0v4t`. All 56 original renderer assertion
texts were confirmed unchanged and in the same order.

All complete acceptance logs were inspected. The unsupported GCC flag was removed only
from the Clang database, matching the bundle adapter. No owned compiler/tidy warnings
remain. Qt's optional Vulkan-header discovery message is irrelevant to these CPU SVG
checks. Xvfb lacks DRI3; software Cairo rendering is intentionally selected. Glycin's
unsandboxed-loader notice reflects the isolated offline container environment. GTK4's
existing `is_symbolic()` assertion is retained for coverage and older GTK compatibility;
[it is deprecated since GTK 4.20](https://docs.gtk.org/gtk4/method.IconPaintable.is_symbolic.html).
No warning was hidden by changing runtime warning filters or weakening assertions.

Native KDE execution, Debian qualification, manual ecosystem acceptance and final
umbrella integration remain deferred. Publication follows verified separate local commits;
the umbrella checkpoint remains unpublished.
