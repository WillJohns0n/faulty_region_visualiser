# models.py

from dataclasses import dataclass
from matplotlib.patches import Rectangle
import numpy.typing as npt
import numpy as np


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass
class Region:
    """Logical + visual region."""

    min_point: Point
    max_point: Point
    patch: Rectangle

    def format_klipper(self, index: int) -> list[str]:
        return [
            f"faulty_region_{index}_min: {self.min_point.x:.3f}, {self.min_point.y:.3f}",
            f"faulty_region_{index}_max: {self.max_point.x:.3f}, {self.max_point.y:.3f}",
        ]


@dataclass
class MeshData:
    grid: npt.NDArray[np.float64]
    x_coords: npt.NDArray[np.float64]
    y_coords: npt.NDArray[np.float64]
    min_x: float
    max_x: float
    min_y: float
    max_y: float


@dataclass
class BedMeshSettings:
    mesh_min: str
    mesh_max: str
    probe_count: str
    regions: list[tuple[Point, Point]]
