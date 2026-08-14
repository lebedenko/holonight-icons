#!/usr/bin/env python3
"""Render deterministic family contact sheets with Inkscape and ImageMagick."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "HoloNight"
OUTPUT = ROOT / "docs/sdd/icon-theme-compliance/previews"
FAMILIES = {
    "panel": (THEME / "24x24/panel", [24]),
    "applications": (THEME / "scalable/apps", [16, 24, 32, 48, 64, 128, 256]),
    "folders": (THEME / "scalable/places", [16, 24, 32]),
    "symbolic": (THEME / "symbolic", [16, 20, 22, 24, 28, 32]),
}


def require(program: str) -> str:
    found = shutil.which(program)
    if not found:
        raise SystemExit(f"required program not found: {program}")
    return found


def render_sheet(label: str, family: str, source: Path, sizes: list[int]) -> None:
    inkscape = require("inkscape")
    magick = require("magick")
    icons = sorted(path for path in source.rglob("*.svg") if not path.is_symlink())
    destination = OUTPUT / label
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="holonight-icons-") as temp_name:
        temp = Path(temp_name)
        tiles: list[str] = []
        for icon_index, icon in enumerate(icons):
            for size_index, size in enumerate(sizes):
                rendered = temp / f"{icon_index:03d}-{size_index:02d}.png"
                tile = temp / f"tile-{icon_index:03d}-{size_index:02d}.png"
                subprocess.run([
                    inkscape, str(icon), "--export-background=#111827",
                    f"--export-width={size}", f"--export-height={size}",
                    f"--export-filename={rendered}",
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run([
                    magick, str(rendered), "-strip", "-gravity", "center",
                    "-background", "#111827", "-extent", "288x288",
                    "-fill", "#e5e7eb", "-pointsize", "14",
                    "-gravity", "south", "-annotate", "+0+18",
                    f"{icon.stem} · {size}px", str(tile),
                ], check=True)
                tiles.append(str(tile))
        columns = len(sizes)
        output = destination / f"{family}.png"
        subprocess.run([
            magick, "montage", *tiles, "-strip", "-background", "#0b1020",
            "-geometry", "+2+2", "-tile", f"{columns}x", str(output),
        ], check=True)
        print(output.relative_to(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", choices=("before", "after"), default="after")
    parser.add_argument("--family", action="append", choices=tuple(FAMILIES))
    args = parser.parse_args()
    for family, (source, sizes) in FAMILIES.items():
        if args.family and family not in args.family:
            continue
        render_sheet(args.label, family, source, sizes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
