# region_manager.py

import matplotlib.pyplot as plt
from tkinter import messagebox

from config import Config
from models import MeshData, BedMeshSettings, Region, Point
from undo_manager import UndoManager


class RegionManager:
    """Manages region creation, editing, and undo/redo operations."""

    def __init__(self, app):
        self.app = app
        self.undo_mgr = UndoManager()

        # Resizing state
        self._resizing = False
        self._resize_region = None
        self._resize_handle = None
        self._resize_start = None
        self._resize_tolerance = 0.02

    def apply_loaded_data(self, mesh: MeshData, settings: BedMeshSettings) -> None:
        """Apply loaded mesh and regions data."""
        self.app.mesh = mesh

        self._remove_all_patches()
        self.app.regions.clear()
        self.undo_mgr.undo_stack.clear()
        self.undo_mgr.redo_stack.clear()

        for p1, p2 in settings.regions:
            self._add_region_from_points(p1, p2)

        self._refresh_region_list()
        self.app.canvas_controller.redraw()

    def _refresh_region_list(self, update_overlay: bool = True) -> None:
        """Update the region listbox with current regions.

        Args:
            update_overlay: Whether to update the probe overlay after refreshing.
                           Set to False during drag operations for better performance.
        """
        self.app.region_list.delete(0, "end")
        for i, r in enumerate(self.app.regions, start=1):
            for line in r.format_klipper(i):
                self.app.region_list.insert("end", line)
        # Apply alternating background colors for each region block (2 lines per region)
        self._apply_region_colors()
        # Auto-update probe overlay to show which points are excluded
        if update_overlay:
            self.app.canvas_controller.update_probe_overlay()

    def _apply_region_colors(self) -> None:
        """Apply alternating background colors to region blocks in the listbox."""
        colors = ("#ffffff", "#f0f0f0")  # White and light gray
        num_items = self.app.region_list.size()
        for i in range(num_items):
            region_index = i // 2  # 2 lines per region
            bg_color = colors[region_index % 2]
            self.app.region_list.itemconfig(i, bg=bg_color)

    def delete_selected(self) -> None:
        """Delete the currently selected region."""
        sel = self.app.region_list.curselection()
        if not sel:
            self.app._set_status("No region selected")
            return
        line_index = sel[0]
        region_index = line_index // 2  # 2 lines per region (min, max)
        if region_index < 0 or region_index >= len(self.app.regions):
            return

        self._snapshot_for_undo()
        region = self.app.regions[region_index]
        try:
            region.patch.remove()
        except Exception:
            pass
        del self.app.regions[region_index]

        # Clear selection in canvas controller
        self.app.canvas_controller._selected_region = None

        self._refresh_region_list()
        self.app.canvas.draw()
        self.app._set_status(f"Deleted region {region_index + 1}")

    def clear_all_regions(self) -> None:
        """Clear all regions."""
        if not self.app.regions:
            return
        self._snapshot_for_undo()
        self._remove_all_patches()
        self.app.regions.clear()
        self.app.canvas_controller._selected_region = None
        self._refresh_region_list()
        self.app.canvas.draw()
        self.app._set_status("Cleared all regions")

    def _remove_all_patches(self) -> None:
        """Remove all region patches from the plot."""
        for r in self.app.regions:
            try:
                r.patch.remove()
            except Exception:
                pass

    def _snapshot_for_undo(self) -> None:
        """Create an undo snapshot of current regions."""
        pairs = [(r.min_point, r.max_point) for r in self.app.regions]
        self.undo_mgr.snapshot(pairs)

    def undo(self) -> None:
        """Undo the last operation."""
        if not self.undo_mgr.can_undo():
            self.app._set_status("Nothing to undo")
            return
        current_pairs = [(r.min_point, r.max_point) for r in self.app.regions]
        self.undo_mgr.push_redo(current_pairs)

        prev_state = self.undo_mgr.pop_undo()
        self._restore_state(prev_state)
        self.app._set_status("Undo")

    def redo(self) -> None:
        """Redo the last undone operation."""
        if not self.undo_mgr.can_redo():
            self.app._set_status("Nothing to redo")
            return
        current_pairs = [(r.min_point, r.max_point) for r in self.app.regions]
        self.undo_mgr.snapshot(current_pairs)

        next_state = self.undo_mgr.pop_redo()
        self._restore_state(next_state)
        self.app._set_status("Redo")

    def _restore_state(self, state) -> None:
        """Restore regions from a saved state."""
        self._remove_all_patches()
        self.app.regions.clear()
        self.app.canvas_controller._selected_region = None
        for s in state:
            p1, p2 = s.min_point, s.max_point
            self._add_region_from_points(p1, p2)
        self._refresh_region_list()
        self.app.canvas_controller.redraw()

    def _add_region_from_points(self, p1: Point, p2: Point) -> None:
        """Add a new region from two corner points."""
        x0, y0 = min(p1.x, p2.x), min(p1.y, p2.y)
        x1, y1 = max(p1.x, p2.x), max(p1.y, p2.y)
        patch = plt.Rectangle(
            (x0, y0),
            x1 - x0,
            y1 - y0,
            linewidth=Config.RECT_LINEWIDTH,
            edgecolor=Config.RECT_COLOR,
            facecolor="none",
            linestyle=Config.RECT_STYLE,
            zorder=Config.RECT_ZORDER,
        )
        self.app.ax.add_patch(patch)
        self.app.regions.append(Region(Point(x0, y0), Point(x1, y1), patch))

    def copy_to_clipboard(self) -> None:
        """Copy region definitions to clipboard."""
        if not self.app.regions:
            messagebox.showinfo("Clipboard", "No regions to copy.")
            return
        try:
            import pyperclip

            lines = []
            for i, r in enumerate(self.app.regions, start=1):
                lines.extend(r.format_klipper(i))
            pyperclip.copy("\n".join(lines))
            messagebox.showinfo(
                "Clipboard",
                f"Copied {len(self.app.regions)} faulty_region definitions to clipboard.",
            )
            self.app._set_status("Copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy:\n{e}")
            self.app._set_status("Copy failed")
