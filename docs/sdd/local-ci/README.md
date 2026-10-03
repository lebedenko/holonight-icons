# Local CI rehearsal

Baseline: 402ed3a3cf858a3095941a75a7fceb2351fe6f9e. Umbrella package CI-008.

Preserve the existing single verification job, push/PR triggers and canonical Qt
provider 7c4fe3c9df0b9a15ed68ddad70b8d05a7312be1a. Local and remote invoke the same
launcher with isolated verification and REUSE 6.2.0 lanes. Verify theme generation,
SVG/alias validation, all Python regressions, actual Qt IconRenderer checks, actual
GTK 3/4 symbolic recoloring on private Xvfb displays, and full preview generation.
Lint repository, HoloNight, HoloNight-Dark and bundled holonight-icons roots.

Use immutable build and licensing images, checksum-pinned GTK/Xvfb supplements
in a disposable prefix, and fresh writable source/build trees from read-only
working-tree snapshots. Preserve modes/symlinks and report non-ignored new inputs.
Disposable passwd/group entries map the invoking UID/GID for private services.
Xvfb hard-codes /usr/bin/xkbcomp. Verification starts a small privileged container
bootstrap that extracts checksum-pinned tools and creates that isolated symlink,
then setpriv drops to the invoking UID/GID before copying or executing repository
code. Host input remains read-only; artifact files are written with host ownership.
The Xvfb wrapper includes server diagnostics in the complete lane log.
Save logs, revisions, dirty status, tool versions, image identities and results in
ignored build/ci. Export generated themes/previews there as host-owned artifacts;
only the existing remote workflow uploads them. No artwork edits, pushes or pins.

2026-10-03 acceptance: isolated verification passes in
`build/ci/20261003T141148Z-qe1s9emx/`; REUSE 6.2.0 passes all four roots in
`build/ci/20261003T140743Z-_m4g40lj/`. Verification covers 44 Python tests,
278 Qt masters at 12 sizes/scales and four palettes, temporary Places/Actions
fixtures at all 11 display sizes and 1x/2x, and 174 GTK symbolic cases per version
and theme. Full previews export 163 PNGs; all 2,013 exported files have host UID.
The source/development-build isolation comparison passes for 1,033 files.

Four launcher regressions cover current/deleted/new/ignored/space-containing
inputs, executable bits/symlinks, missing runtime, every failed lane/continuation,
Podman mapping, bootstrap UID/GID, read-only account files and host-owned artifact
collection. Actual provider compiler and GTK startup failures propagate nonzero.
Complete logs were reviewed. Missing optional Vulkan headers and DRI3 warnings
are expected for the private software-rendering display. The PNG preflight's
unclosed-loader warning was corrected with a format capability query; the narrow
query passes in the pinned environment without rerunning unaffected rendering.
Native documentation REUSE lint and final diff checks pass. Real Podman is unavailable; its argument/mapping behavior
is covered by launcher regression tests.

The existing workflow pin 27970cfe predates APIs used by the current renderer
checks (IconState, accent/background colors and resolveIconColors). The first
container run reproduced that compiler failure. Use published provider 7c4fe3c
which introduced those APIs; local and remote share this exact revision.
