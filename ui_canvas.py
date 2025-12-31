# ui_canvas.py

from typing import Optional
import numpy as np
from matplotlib.patches import Rectangle

from models import Region, Point
from config import Config


class CanvasController:
    """
    Handles all canvas drawing, probe overlay, mouse interaction,
    and resize-handle logic for the MeshRegionApp.
    """

    def __init__(self, app):
        self.app = app  # reference to MeshRegionApp

        # Drawing state
        self._dragging = False
        self._drag_start = None
        self._current_patch = None
        self._selected_region = None

    # --- Drawing ---

    def redraw(self) -> None:
        """Full redraw of mesh, regions, and optional probe overlay."""
        if not self.app.mesh:
            self.app.ax.clear()
            self.app.canvas.draw_idle()
            return

        overlay = None
        if self.app.settings_manager.show_probe_overlay.get():
            try:
                mesh_min = self._parse_pair(
                    self.app.settings_manager.mesh_min_var.get()
                )
                mesh_max = self._parse_pair(
                    self.app.settings_manager.mesh_max_var.get()
                )
                probe_count = self._parse_pair(
                    self.app.settings_manager.probe_count_var.get()
                )

                overlay = {
                    "enabled": True,
                    "mesh_min_x": mesh_min[0],
                    "mesh_min_y": mesh_min[1],
                    "mesh_max_x": mesh_max[0],
                    "mesh_max_y": mesh_max[1],
                    "probe_count_x": probe_count[0],
                    "probe_count_y": probe_count[1],
                }
            except Exception:
                overlay = None

        self.app.visualizer.draw_mesh(self.app.mesh, self.app.regions, overlay)
        self.app.canvas.draw_idle()

    def update_probe_overlay(self) -> None:
        """Redraw only the probe points overlay based on bed mesh settings."""
        if not self.app.mesh:
            return

        overlay = None
        if self.app.settings_manager.show_probe_overlay.get():
            try:
                mesh_min = self._parse_pair(
                    self.app.settings_manager.mesh_min_var.get()
                )
                mesh_max = self._parse_pair(
                    self.app.settings_manager.mesh_max_var.get()
                )
                probe_count = self._parse_pair(
                    self.app.settings_manager.probe_count_var.get()
                )

                overlay = {
                    "enabled": True,
                    "mesh_min_x": mesh_min[0],
                    "mesh_min_y": mesh_min[1],
                    "mesh_max_x": mesh_max[0],
                    "mesh_max_y": mesh_max[1],
                    "probe_count_x": probe_count[0],
                    "probe_count_y": probe_count[1],
                }
            except Exception:
                overlay = None

        # Redraw mesh with new overlay settings (clears old overlay)
        self.app.visualizer.draw_mesh(self.app.mesh, self.app.regions, overlay)
        self.app.canvas.draw_idle()

    def _parse_pair(self, text: str) -> tuple[float, float]:
        x_str, y_str = text.split(",")
        return float(x_str.strip()), float(y_str.strip())

    def _nearest_grid_value(self, val: float, grid: np.ndarray) -> float:
        idx = np.abs(grid - val).argmin()
        return float(grid[idx])

    # --- Resize handle helpers ---

    def _get_resize_handle(self, x: float, y: float, region: Region) -> Optional[str]:
        if not self.app.mesh:
            return None

        x_range = self.app.mesh.max_x - self.app.mesh.min_x
        y_range = self.app.mesh.max_y - self.app.mesh.min_y
        tol_x = x_range * self.app.region_manager._resize_tolerance
        tol_y = y_range * self.app.region_manager._resize_tolerance

        min_x, min_y = region.min_point.x, region.min_point.y
        max_x, max_y = region.max_point.x, region.max_point.y

        # Corners
        if abs(x - min_x) < tol_x and abs(y - min_y) < tol_y:
            return "sw"
        if abs(x - max_x) < tol_x and abs(y - min_y) < tol_y:
            return "se"
        if abs(x - min_x) < tol_x and abs(y - max_y) < tol_y:
            return "nw"
        if abs(x - max_x) < tol_x and abs(y - max_y) < tol_y:
            return "ne"

        # Edges
        if abs(x - min_x) < tol_x and min_y < y < max_y:
            return "w"
        if abs(x - max_x) < tol_x and min_y < y < max_y:
            return "e"
        if abs(y - min_y) < tol_y and min_x < x < max_x:
            return "s"
        if abs(y - max_y) < tol_y and min_x < x < max_x:
            return "n"

        return None

    def _update_cursor(self, x: float, y: float) -> None:
        widget = self.app.canvas.get_tk_widget()
        if not self.app.mesh:
            widget.config(cursor="cross")
            return

        for region in self.app.regions:
            handle = self._get_resize_handle(x, y, region)
            if handle:
                cursor_map = {
                    "nw": "top_left_corner",
                    "ne": "top_right_corner",
                    "sw": "bottom_left_corner",
                    "se": "bottom_right_corner",
                    "n": "top_side",
                    "s": "bottom_side",
                    "e": "right_side",
                    "w": "left_side",
                }
                widget.config(cursor=cursor_map.get(handle, "cross"))
                return

        widget.config(cursor="cross")

    def _select_region(self, region_index: int) -> None:
        """Select a region by index and highlight it."""
        if region_index < 0 or region_index >= len(self.app.regions):
            return

        # Deselect previous selection
        if self._selected_region is not None:
            old_idx = self._selected_region
            if old_idx < len(self.app.regions):
                region = self.app.regions[old_idx]
                region.patch.set_edgecolor(Config.RECT_COLOR)
                region.patch.set_linewidth(Config.RECT_LINEWIDTH)

        # Select new region
        self._selected_region = region_index
        region = self.app.regions[region_index]
        region.patch.set_edgecolor("yellow")
        region.patch.set_linewidth(2.5)

        # Update listbox selection
        self.app.region_list.selection_clear(0, "end")
        line_index = region_index * 3  # 3 lines per region (min, max, blank)
        self.app.region_list.selection_set(line_index)
        self.app.region_list.see(line_index)

        self.app.canvas.draw()
        self.app._set_status(f"Selected region {region_index + 1}")

    def _deselect_region(self) -> None:
        """Deselect the currently selected region."""
        if self._selected_region is not None:
            region = self.app.regions[self._selected_region]
            region.patch.set_edgecolor(Config.RECT_COLOR)
            region.patch.set_linewidth(Config.RECT_LINEWIDTH)
            self._selected_region = None
            self.app.region_list.selection_clear(0, "end")
            self.app.canvas.draw()

    def _is_point_in_region(self, x: float, y: float, region: Region) -> bool:
        """Check if point (x, y) is inside or near the region (with tolerance padding)."""
        if not self.app.mesh:
            return False

        min_x, min_y = region.min_point.x, region.min_point.y
        max_x, max_y = region.max_point.x, region.max_point.y

        # Calculate tolerance padding (same as used for resize handles)
        x_range = self.app.mesh.max_x - self.app.mesh.min_x
        y_range = self.app.mesh.max_y - self.app.mesh.min_y
        tol_x = x_range * self.app.region_manager._resize_tolerance
        tol_y = y_range * self.app.region_manager._resize_tolerance

        # Check if point is within region bounds plus tolerance
        return (min_x - tol_x) <= x <= (max_x + tol_x) and (min_y - tol_y) <= y <= (
            max_y + tol_y
        )

    # --- Mouse interaction ---

    def on_mouse_press(self, event) -> None:
        if not self.app.mesh or event.inaxes != self.app.ax:
            return

        x, y = event.xdata, event.ydata

        # Check for resize handles first (priority)
        for region in self.app.regions:
            handle = self._get_resize_handle(x, y, region)
            if handle:
                self.app.region_manager._resizing = True
                self.app.region_manager._resize_region = region
                self.app.region_manager._resize_handle = handle
                self.app.region_manager._resize_start = (x, y)
                self.app.region_manager._snapshot_for_undo()
                self.app._set_status("Resizing region")
                return

        # Check for clicks on region interiors (for selection)
        # Include tolerance padding around the edges
        for i, region in enumerate(self.app.regions):
            if self._is_point_in_region(x, y, region):
                self._select_region(i)
                return

        # Deselect if clicking on empty space
        self._deselect_region()

        # Start drawing a new rectangle
        self._dragging = True
        self._drag_start = (x, y)

        self._current_patch = Rectangle(
            (x, y),
            0,
            0,
            linewidth=Config.RECT_LINEWIDTH,
            edgecolor=Config.RECT_COLOR,
            facecolor="none",
            linestyle=Config.RECT_STYLE,
            zorder=Config.RECT_ZORDER,
        )
        self.app.ax.add_patch(self._current_patch)
        self.app.canvas.draw()

    def on_mouse_move(self, event) -> None:
        if not self.app.mesh or event.inaxes != self.app.ax:
            return

        x, y = event.xdata, event.ydata

        # Resizing
        if (
            self.app.region_manager._resizing
            and self.app.region_manager._resize_region is not None
        ):
            self._handle_resize(x, y)
            return

        # Drawing
        if self._dragging and self._current_patch is not None:
            x0, y0 = self._drag_start
            x1, y1 = x, y

            xmin, xmax = min(x0, x1), max(x0, x1)
            ymin, ymax = min(y0, y1), max(y0, y1)

            if self.app.settings_manager.snap_var.get():
                xmin = self._nearest_grid_value(xmin, self.app.mesh.x_coords)
                xmax = self._nearest_grid_value(xmax, self.app.mesh.x_coords)
                ymin = self._nearest_grid_value(ymin, self.app.mesh.y_coords)
                ymax = self._nearest_grid_value(ymax, self.app.mesh.y_coords)

            self._current_patch.set_xy((xmin, ymin))
            self._current_patch.set_width(max(0.0, xmax - xmin))
            self._current_patch.set_height(max(0.0, ymax - ymin))
            self.app.canvas.draw()
            return

        # Cursor update
        self._update_cursor(x, y)

    def _handle_resize(self, x: float, y: float) -> None:
        region = self.app.region_manager._resize_region
        handle = self.app.region_manager._resize_handle
        if not self.app.mesh or region is None or handle is None:
            return

        min_x, min_y = region.min_point.x, region.min_point.y
        max_x, max_y = region.max_point.x, region.max_point.y

        if self.app.settings_manager.snap_var.get():
            x = self._nearest_grid_value(x, self.app.mesh.x_coords)
            y = self._nearest_grid_value(y, self.app.mesh.y_coords)

        # Horizontal
        if "w" in handle:
            min_x = min(x, max_x - 0.001)
        if "e" in handle:
            max_x = max(x, min_x + 0.001)

        # Vertical
        if "s" in handle:
            min_y = min(y, max_y - 0.001)
        if "n" in handle:
            max_y = max(y, min_y + 0.001)

        region.min_point = Point(min_x, min_y)
        region.max_point = Point(max_x, max_y)

        region.patch.set_xy((min_x, min_y))
        region.patch.set_width(max_x - min_x)
        region.patch.set_height(max_y - min_y)

        self.app.region_manager._refresh_region_list()
        self.app.canvas.draw()

    def on_mouse_release(self, event) -> None:
        # Finish resizing
        if self.app.region_manager._resizing:
            self.app.region_manager._resizing = False
            self.app.region_manager._resize_region = None
            self.app.region_manager._resize_handle = None
            self.app.region_manager._resize_start = None
            self.app._set_status("Resize complete")
            return

        # Finish drawing
        if not self._dragging:
            return
        self._dragging = False

        if not self._current_patch:
            return

        x, y = self._current_patch.get_xy()
        w = self._current_patch.get_width()
        h = self._current_patch.get_height()

        if w <= 0.0 or h <= 0.0:
            self._current_patch.remove()
            self._current_patch = None
            self.app.canvas.draw_idle()
            return

        p1 = Point(x, y)
        p2 = Point(x + w, y + h)

        region = Region(p1, p2, self._current_patch)
        self.app.regions.append(region)
        self._current_patch = None

        self.app.region_manager._snapshot_for_undo()
        self.app.region_manager._refresh_region_list()
        self.app.canvas.draw_idle()
        self.app._set_status(f"Added region {len(self.app.regions)}")
