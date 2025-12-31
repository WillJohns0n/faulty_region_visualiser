# parser_mesh.py

import re
from pathlib import Path
from typing import Optional

import numpy as np

from config import logger
from models import MeshData


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_latest_mesh(content: str) -> Optional[MeshData]:
    """
    Parse latest #*# [bed_mesh default] block from printer.cfg.
    Returns MeshData or None.
    """
    try:
        match = re.search(
            r"#\*# \[bed_mesh default\](.*?)(?=#\*# \[|$)",
            content,
            re.DOTALL,
        )
        if not match:
            logger.warning("No #*# [bed_mesh default] block found")
            return None

        block = match.group(1)

        # Extract parameters
        def get_param(name: str) -> float:
            m = re.search(rf"#\*# {re.escape(name)} = ([\d\.eE+-]+)", block)
            if not m:
                raise ValueError(f"Missing parameter {name} in bed_mesh block")
            return float(m.group(1))

        x_count = int(get_param("x_count"))
        y_count = int(get_param("y_count"))
        min_x = get_param("min_x")
        max_x = get_param("max_x")
        min_y = get_param("min_y")
        max_y = get_param("max_y")

        # Extract points
        points_lines = re.findall(r"#\*#\s+([-0-9\.,\s]+)", block)
        points_str = " ".join(points_lines).replace(",", " ")
        vals = [float(p) for p in points_str.split() if p.strip()]

        if len(vals) != x_count * y_count:
            raise ValueError(
                f"Mesh point count mismatch: got {len(vals)}, "
                f"expected {x_count * y_count}"
            )

        grid = np.array(vals, dtype=np.float64).reshape((y_count, x_count))
        x_coords = np.linspace(min_x, max_x, x_count)
        y_coords = np.linspace(min_y, max_y, y_count)

        logger.info(
            "Parsed mesh: %dx%d, X=[%.2f..%.2f], Y=[%.2f..%.2f]",
            x_count,
            y_count,
            min_x,
            max_x,
            min_y,
            max_y,
        )

        return MeshData(
            grid=grid,
            x_coords=x_coords,
            y_coords=y_coords,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
        )
    except Exception as e:
        logger.error(f"Failed to parse mesh: {e}")
        return None
