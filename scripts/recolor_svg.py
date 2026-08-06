#!/usr/bin/env python3
"""
Recolor SVG files for the HoloNight icon theme.

This script is intentionally conservative:
- exact hex replacements
- preserves gradients and structure
- avoids raster/image content
- optionally normalizes common inline styles

It works best on SVG themes such as Papirus/Tela where colors are explicit hex values.

Usage:

    python recolor_svg.py --input icon.svg --output icon.svg --palette holonight-palette.json

"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")


def normalize_hex(value: str) -> str:
    value = value.lower()
    if len(value) == 4:
        return "#" + "".join(ch * 2 for ch in value[1:])
    return value


def load_replacements(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    replacements = data.get("replacements", {})
    return {normalize_hex(k): v.lower() for k, v in replacements.items()}


def recolor_svg_text(text: str, replacements: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        original = match.group(0)
        normalized = normalize_hex(original)
        return replacements.get(normalized, original)

    return HEX_RE.sub(replace, text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--palette", required=True, type=Path)
    args = parser.parse_args()

    replacements = load_replacements(args.palette)
    text = args.input.read_text(encoding="utf-8", errors="ignore")
    recolored = recolor_svg_text(text, replacements)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(recolored, encoding="utf-8")


if __name__ == "__main__":
    main()
