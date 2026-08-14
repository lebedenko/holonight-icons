#!/usr/bin/env python3
"""Validate HoloNight SVG structure and alias integrity using the standard library."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "HoloNight"
EXCEPTIONS_FILE = ROOT / "scripts/icon-exceptions.json"
SVG_NS = "{http://www.w3.org/2000/svg}"
FORBIDDEN_SYMBOLIC = {"image", "text", "filter", "mask", "clipPath"}
EDITOR_MARKERS = ("inkscape", "sodipodi")
SUPPORTED_CLASSES = {
    "ColorScheme-Text",
    "ColorScheme-Highlight",
    "ColorScheme-NeutralText",
    "ColorScheme-PositiveText",
    "ColorScheme-NegativeText",
}
APP_SIZES = {16, 24, 32, 48, 64, 128, 256}
FIRST_PARTY_APPS = {
    "holonight-ai.svg", "holonight-pkg-manager.svg",
    "holonight-settings.svg", "holonight-shell.svg",
}


def load_exceptions() -> tuple[dict[tuple[str, str], dict], list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(EXCEPTIONS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"{EXCEPTIONS_FILE.relative_to(ROOT)}: invalid manifest: {exc}"]
    entries: dict[tuple[str, str], dict] = {}
    required = {"path", "rule", "upstream_contract", "rationale", "reviewed_sizes"}
    for index, item in enumerate(data.get("exceptions", [])):
        missing = required - item.keys()
        if missing:
            errors.append(f"exception {index}: missing {', '.join(sorted(missing))}")
            continue
        if any(token in item["path"] for token in ("*", "?", "[")):
            errors.append(f"exception {index}: wildcard paths are prohibited")
        path = ROOT / item["path"]
        if not path.is_file() or path.is_symlink():
            errors.append(f"exception {index}: path is not a real file: {item['path']}")
        key = (item["path"], item["rule"])
        if key in entries:
            errors.append(f"exception {index}: duplicate path/rule entry")
        entries[key] = item
    return entries, errors


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_viewbox(value: str) -> tuple[float, float, float, float] | None:
    try:
        numbers = tuple(float(part) for part in re.split(r"[ ,]+", value.strip()))
    except ValueError:
        return None
    return numbers if len(numbers) == 4 else None


def inkscape_bounds(path: Path, element_id: str | None = None) -> tuple[float, float, float, float]:
    command = ["inkscape", str(path)]
    if element_id:
        command.append(f"--query-id={element_id}")
    command.extend(("--query-x", "--query-y", "--query-width", "--query-height"))
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    values = tuple(float(value) for value in result.stdout.splitlines())
    if len(values) != 4:
        raise ValueError(f"unexpected Inkscape query result: {result.stdout!r}")
    return values


def validate() -> list[str]:
    exceptions, errors = load_exceptions()
    used_exceptions: set[tuple[str, str]] = set()
    real_files = sorted(path for path in THEME.rglob("*.svg") if not path.is_symlink())
    aliases = sorted(path for path in THEME.rglob("*.svg") if path.is_symlink())

    for alias in aliases:
        try:
            target = alias.resolve(strict=True)
        except FileNotFoundError:
            errors.append(f"{alias.relative_to(ROOT)}: broken alias")
            continue
        if not target.is_file() or THEME not in target.parents:
            errors.append(f"{alias.relative_to(ROOT)}: alias escapes the icon theme")

    for path in real_files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
            root = ET.fromstring(text)
        except (OSError, UnicodeDecodeError, ET.ParseError) as exc:
            errors.append(f"{rel}: invalid XML: {exc}")
            continue
        if local_name(root.tag) != "svg":
            errors.append(f"{rel}: root element is not svg")
            continue
        viewbox = parse_viewbox(root.get("viewBox", ""))
        if viewbox is None or viewbox[2] <= 0 or viewbox[3] <= 0:
            errors.append(f"{rel}: missing or invalid viewBox")
            continue

        expected = None
        if "/symbolic/" in rel or "/scalable/places/" in rel or "/24x24/panel/" in rel:
            expected = (0.0, 0.0, 24.0, 24.0)
        elif rel.startswith("HoloNight/scalable/apps/"):
            expected = (0.0, 0.0, 256.0, 256.0)
        if expected and viewbox != expected:
            key = (rel, "canvas")
            if key in exceptions:
                used_exceptions.add(key)
            else:
                errors.append(f"{rel}: expected viewBox {' '.join(map(str, expected))}")

        if any(marker in text for marker in EDITOR_MARKERS):
            errors.append(f"{rel}: editor metadata is prohibited")

        if "/symbolic/" in rel:
            for element in root.iter():
                name = local_name(element.tag)
                if name in FORBIDDEN_SYMBOLIC:
                    errors.append(f"{rel}: forbidden symbolic element <{name}>")
                classes = element.get("class", "").split()
                unsupported = sorted(set(classes) - SUPPORTED_CLASSES)
                if unsupported:
                    errors.append(f"{rel}: unsupported semantic class {', '.join(unsupported)}")

    inkscape = shutil.which("inkscape")
    if not inkscape:
        errors.append("Inkscape is required for geometry validation")
    else:
        for name in sorted(FIRST_PARTY_APPS):
            path = THEME / "scalable/apps" / name
            try:
                x, y, width, height = inkscape_bounds(path)
            except (OSError, ValueError, subprocess.CalledProcessError) as exc:
                errors.append(f"{path.relative_to(ROOT)}: cannot query visible bounds: {exc}")
                continue
            if x < 19.99 or y < 19.99 or x + width > 236.01 or y + height > 236.01:
                errors.append(f"{path.relative_to(ROOT)}: visible artwork exceeds 20…236 safe area")

        insync_bounds = []
        for path in sorted((THEME / "24x24/panel").glob("insync-*.svg")):
            try:
                insync_bounds.append((path, inkscape_bounds(path, "insync-base")))
            except (OSError, ValueError, subprocess.CalledProcessError) as exc:
                errors.append(f"{path.relative_to(ROOT)}: cannot query Insync base: {exc}")
        if insync_bounds:
            reference_path, reference = insync_bounds[0]
            for path, bounds in insync_bounds[1:]:
                if any(abs(left - right) > 0.5 for left, right in zip(reference, bounds)):
                    errors.append(
                        f"{path.relative_to(ROOT)}: Insync base differs from "
                        f"{reference_path.name} by more than 0.5 unit"
                    )

        teams = THEME / "24x24/panel/teams-tray.svg"
        try:
            x, y, width, height = inkscape_bounds(teams)
            if x < 1.99 or y < 1.99 or x + width > 22.01 or y + height > 22.01:
                errors.append(f"{teams.relative_to(ROOT)}: visible artwork exceeds 2…22 safe area")
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            errors.append(f"{teams.relative_to(ROOT)}: cannot query visible bounds: {exc}")

    for key, item in exceptions.items():
        if key not in used_exceptions:
            errors.append(f"{item['path']}: unused exception for rule {item['rule']}")
        if set(item["reviewed_sizes"]) != APP_SIZES:
            errors.append(f"{item['path']}: canvas exception must review all application sizes")

    if len(real_files) != 154:
        errors.append(f"HoloNight: expected 154 real SVGs, found {len(real_files)}")
    if len(aliases) != 58:
        errors.append(f"HoloNight: expected 58 SVG aliases, found {len(aliases)}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Icon validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Icon validation passed: 154 SVG masters and 58 aliases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
