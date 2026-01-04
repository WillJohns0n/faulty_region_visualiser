from typing import Optional, Dict, Any, List, Callable

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable

from config import Config
from models import MeshData, Region, PlotBounds


class MeshVisualizer:
    """Handles all matplotlib drawing with external colour scale control."""

    def __init__(self, fig: Figure, ax: Axes):
        self.fig = fig
        self.ax = ax

        # Colorbar axis
        divider = make_axes_locatable(self.ax)
        self.cax = divider.append_axes("right", size="5%", pad=0.05)

        self._colorbar = None
        self._im = None  # store the imshow object

        # Store current mesh z-range for external access
        self.z_min = 0.0
        self.z_max = 1.0

        # Callback for when z-range is updated (set by UI)
        self.on_z_range_changed: Optional[Callable[[float, float], None]] = None

    def draw_mesh(
        self,
        mesh: MeshData,
        regions: List[Region],
        plot_bounds: Optional[PlotBounds] = None,
        probe_overlay: Optional[Dict[str, Any]] = None,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        show_mesh_grid: bool = False,
    ) -> None:
        self.ax.clear()
        self.cax.clear()

        # Default bounds
        if plot_bounds is None:
            plot_bounds = PlotBounds(
                min_x=mesh.min_x,
                max_x=mesh.max_x,
                min_y=mesh.min_y,
                max_y=mesh.max_y,
            )

        # Draw mesh
        self._im = self.ax.imshow(
            mesh.grid,
            origin="lower",
            cmap=Config.COLORMAP,
            extent=(mesh.min_x, mesh.max_x, mesh.min_y, mesh.max_y),
            interpolation="nearest",
            aspect="equal",
            vmin=vmin,
            vmax=vmax,
        )

        # Colorbar
        self._colorbar = self.fig.colorbar(
            self._im,
            cax=self.cax,
            orientation="vertical",
            label="Z offset (mm)",
        )

        # Draw probe points (black dots) if enabled
        if show_mesh_grid:
            self._draw_probe_points(mesh)

        if probe_overlay and probe_overlay.get("enabled"):
            self._draw_probe_overlay(probe_overlay, regions)

        for r in regions:
            self.ax.add_patch(r.patch)

        # Axes labels
        self.ax.set_xlim(plot_bounds.min_x, plot_bounds.max_x)
        self.ax.set_ylim(plot_bounds.min_y, plot_bounds.max_y)
        self.ax.set_xlabel("X (mm)")
        self.ax.set_ylabel("Y (mm)")
        self.ax.set_title("Bed Mesh with Faulty Regions")

        # Store z-range and notify callback
        self.z_min = float(np.nanmin(mesh.grid))
        self.z_max = float(np.nanmax(mesh.grid))

        if self.on_z_range_changed:
            self.on_z_range_changed(self.z_min, self.z_max)

    def update_clim(self, vmin: float, vmax: float) -> None:
        """Update colour limits from external controls."""
        if self._im is None:
            return

        # Prevent inverted ranges
        if vmin >= vmax:
            return

        self._im.set_clim(vmin, vmax)
        self.fig.canvas.draw_idle()

    # ----------------------------------------------------------------------
    # Existing probe drawing logic
    # ----------------------------------------------------------------------
    def _draw_probe_points(self, mesh: MeshData) -> None:
        xg, yg = np.meshgrid(mesh.x_coords, mesh.y_coords)
        pts = np.column_stack([xg.ravel(), yg.ravel()])
        self.ax.scatter(
            pts[:, 0],
            pts[:, 1],
            c="black",
            s=Config.SCATTER_POINT_SIZE,
            alpha=Config.SCATTER_ALPHA,
            zorder=2,
        )

    def _draw_probe_overlay(self, cfg: Dict[str, Any], regions: List[Region]) -> None:
        try:
            min_x = float(cfg["mesh_min_x"])
            min_y = float(cfg["mesh_min_y"])
            max_x = float(cfg["mesh_max_x"])
            max_y = float(cfg["mesh_max_y"])
            count_x = int(cfg["probe_count_x"])
            count_y = int(cfg["probe_count_y"])

            count_x = max(2, min(200, count_x))
            count_y = max(2, min(200, count_y))

            xs = np.linspace(min_x, max_x, count_x)
            ys = np.linspace(min_y, max_y, count_y)
            xv, yv = np.meshgrid(xs, ys)
            pts = np.column_stack([xv.ravel(), yv.ravel()])

            excluded = np.zeros(len(pts), dtype=bool)
            for r in regions:
                x0, y0 = r.min_point.x, r.min_point.y
                x1, y1 = r.max_point.x, r.max_point.y
                in_r = (
                    (pts[:, 0] >= x0)
                    & (pts[:, 0] <= x1)
                    & (pts[:, 1] >= y0)
                    & (pts[:, 1] <= y1)
                )
                excluded |= in_r

            valid_pts = pts[~excluded]
            excl_pts = pts[excluded]

            if len(valid_pts):
                self.ax.scatter(
                    valid_pts[:, 0],
                    valid_pts[:, 1],
                    c="red",
                    s=35,
                    marker="o",
                    edgecolors="darkred",
                    linewidths=1.0,
                    zorder=4,
                    alpha=0.8,
                )
            if len(excl_pts):
                self.ax.scatter(
                    excl_pts[:, 0],
                    excl_pts[:, 1],
                    c="red",
                    s=40,
                    marker="x",
                    linewidths=2.0,
                    zorder=5,
                    alpha=0.9,
                )

            rect = Rectangle(
                (min_x, min_y),
                max_x - min_x,
                max_y - min_y,
                facecolor="none",
                edgecolor="blue",
                linestyle=":",
                linewidth=2,
                zorder=1,
            )
            self.ax.add_patch(rect)

        except Exception:
            pass
