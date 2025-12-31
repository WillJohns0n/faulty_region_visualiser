# parser_settings.py

import re
from pathlib import Path
from typing import Tuple

from config import logger
from models import BedMeshSettings, Point


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_bed_mesh_settings(content: str) -> BedMeshSettings:
    """
    Parse [bed_mesh] settings from einsy-rambo.cfg:
    - mesh_min
    - mesh_max
    - probe_count
    - faulty_region_* pairs
    """
    section_match = re.search(r"(?m)^\[bed_mesh\](.*?)(?=^\[|\Z)", content, re.DOTALL)
    if not section_match:
        logger.warning("No [bed_mesh] section found")
        return BedMeshSettings("", "", "", [])

    body = section_match.group(1)

    def get_value(key: str) -> str:
        m = re.search(rf"{re.escape(key)}:\s*(.*)", body)
        return m.group(1).strip() if m else ""

    mesh_min = get_value("mesh_min")
    mesh_max = get_value("mesh_max")
    probe_count = get_value("probe_count")

    # faulty_region_N_min / _max
    region_pairs = re.findall(
        r"faulty_region_(\d+)_min:\s*(.*?)\s*$\s*faulty_region_\1_max:\s*(.*?)\s*$",
        body,
        re.MULTILINE,
    )

    regions: list[Tuple[Point, Point]] = []
    region_pairs.sort(key=lambda t: int(t[0]))
    for _, vmin, vmax in region_pairs:
        try:
            p1_vals = [float(x.strip()) for x in vmin.split(",")]
            p2_vals = [float(x.strip()) for x in vmax.split(",")]
            if len(p1_vals) == 2 and len(p2_vals) == 2:
                regions.append((Point(*p1_vals), Point(*p2_vals)))
        except Exception:
            continue

    logger.info(
        "Parsed bed_mesh: mesh_min=%r, mesh_max=%r, probe_count=%r, regions=%d",
        mesh_min,
        mesh_max,
        probe_count,
        len(regions),
    )

    return BedMeshSettings(mesh_min, mesh_max, probe_count, regions)


def update_bed_mesh_section(
    content: str,
    new_mesh_min: str,
    new_mesh_max: str,
    new_probe_count: str,
    regions: list[Tuple[Point, Point]],
) -> str:
    """
    Update [bed_mesh] section in einsy-rambo.cfg, preserving order and indentation.
    """

    # Find the section boundaries
    section_match = re.search(r"(?ms)^\[bed_mesh\]\s*\n(.*?)(?=^\[|\Z)", content)
    if not section_match:
        raise ValueError("No [bed_mesh] section found in settings file")

    body = section_match.group(1)
    start, end = section_match.span(1)

    lines = body.splitlines()

    # Detect indentation (first non-empty line)
    indent = ""
    for line in lines:
        if line.strip():
            indent = line[: len(line) - len(line.lstrip())]
            break

    # Build new region lines
    region_lines = []
    for idx, (p1, p2) in enumerate(regions, start=1):
        region_lines.append(f"{indent}faulty_region_{idx}_min: {p1.x:.3f}, {p1.y:.3f}")
        region_lines.append(f"{indent}faulty_region_{idx}_max: {p2.x:.3f}, {p2.y:.3f}")

    new_body_lines = []
    inserted_regions = False

    for line in lines:
        stripped = line.strip()

        # Replace keys in place
        if stripped.startswith("mesh_min:"):
            new_body_lines.append(f"{indent}mesh_min: {new_mesh_min}")
            continue

        if stripped.startswith("mesh_max:"):
            new_body_lines.append(f"{indent}mesh_max: {new_mesh_max}")
            continue

        if stripped.startswith("probe_count:"):
            new_body_lines.append(f"{indent}probe_count: {new_probe_count}")
            continue

        # Remove old region lines
        if stripped.startswith("faulty_region_"):
            continue

        # Insert new region lines immediately after fade_end or algorithm
        if not inserted_regions and stripped.startswith("horizontal_move_z:"):
            # Insert regions BEFORE horizontal_move_z
            new_body_lines.extend(region_lines)
            inserted_regions = True

        new_body_lines.append(line)

    # If no insertion point was found, append at end
    if not inserted_regions:
        new_body_lines.extend(region_lines)

    new_body = "\n".join(new_body_lines) + "\n"

    updated = content[:start] + new_body + content[end:]
    return updated
