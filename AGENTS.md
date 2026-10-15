# HoloNight Icons

Use Conventional Commits for every new commit: `type(scope): imperative summary`, or `type: imperative summary` when a scope adds no clarity.

This repository owns source artwork, aliases, theme metadata, and generated icon themes.
Read `docs/icon-design-rules.md` and the relevant Places or Devices specification before editing artwork.

Ordinary Places and Devices icon names must resolve to monochrome semantic artwork at 16, 20, 22, and 24 px and colorful artwork at 32 px and above. Explicit `-symbolic` names must stay monochrome and GTK-recolorable at every size. Keep aliases within the theme and verify lookup through `index.theme` at every advertised size, including inherited themes and scale 2 entries.

Do not edit generated themes directly. Run `task check` after source, metadata, or generator changes. Keep artwork and documentation changes in this repository; shared Qt rendering belongs to `holonight-qt`.



## Development and documentation

Use `task build` and `task test` for incremental native CMake/CTest work. Native builds
consume installed packages; use `CMAKE_PREFIX_PATH` for an explicit development prefix.
Use `task format` for the pinned formatter and `task check` for container acceptance.
Run `task check:integration` for installation/runtime changes. Container builds use
fresh build/prefix directories, separate from `build/dev` and `build/release`.
clangd reads `build/dev/compile_commands.json` directly.

Routine changes need tests and a commit explanation; update user documentation when
behavior changes. Substantial designs need one local SDD describing intent, decisions,
interfaces and acceptance. Cross-project changes need one umbrella note linking local
designs and stating contracts, dependency order and integration checks. Historical SDDs
remain historical. No separate planning, readiness, handoff or closure commits are required.
Keep routine logs and generated evidence in ignored build directories or CI artifacts.
Provider and consumer implementation may proceed together; publish providers before
consumer commits that reference them. Update umbrella pins per coherent milestone.
