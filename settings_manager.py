# settings_manager.py

import tkinter as tk

from config import Config
from models import BedMeshSettings


class SettingsManager:
    """Manages bed mesh settings and UI variables."""

    def __init__(self):
        # Settings variables
        self.mesh_min_var = tk.StringVar()
        self.mesh_max_var = tk.StringVar()
        self.probe_count_var = tk.StringVar()

        # Plot area variables (in mm)
        self.plot_area_x_var = tk.StringVar(value=str(Config.DEFAULT_PLOT_AREA_X))
        self.plot_area_y_var = tk.StringVar(value=str(Config.DEFAULT_PLOT_AREA_Y))

        # UI state variables
        self.show_probe_overlay = tk.BooleanVar(value=True)
        self.snap_var = tk.BooleanVar(value=False)
        self.show_mesh_grid = tk.BooleanVar(value=False)  # Black dots, default off

        # File configuration - when True, [bed_mesh] is in printer.cfg instead of separate file
        self.bed_mesh_in_printer_cfg = tk.BooleanVar(value=False)

        # Z-scale (colormap) variables
        self.z_scale_min_var = tk.DoubleVar(value=0.0)
        self.z_scale_max_var = tk.DoubleVar(value=1.0)
        self._z_range_min = 0.0  # Actual data range
        self._z_range_max = 1.0

    def update_z_range(self, z_min: float, z_max: float) -> None:
        """Update the z-range from loaded mesh data."""
        self._z_range_min = z_min
        self._z_range_max = z_max
        self.z_scale_min_var.set(z_min)
        self.z_scale_max_var.set(z_max)

    def get_z_range(self) -> tuple[float, float]:
        """Get the actual data z-range."""
        return (self._z_range_min, self._z_range_max)

    def apply_loaded_settings(self, settings: BedMeshSettings) -> None:
        """Apply loaded settings to the UI variables."""
        self.mesh_min_var.set(settings.mesh_min)
        self.mesh_max_var.set(settings.mesh_max)
        self.probe_count_var.set(settings.probe_count)

    def get_plot_area(self) -> tuple[float, float]:
        """Get current plot area dimensions as (x, y) tuple."""
        try:
            x = float(self.plot_area_x_var.get())
            y = float(self.plot_area_y_var.get())
            return (max(x, 1), max(y, 1))  # Ensure positive values
        except (ValueError, tk.TclError):
            return (Config.DEFAULT_PLOT_AREA_X, Config.DEFAULT_PLOT_AREA_Y)
