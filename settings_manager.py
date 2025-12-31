# settings_manager.py

import tkinter as tk

from models import BedMeshSettings


class SettingsManager:
    """Manages bed mesh settings and UI variables."""

    def __init__(self):
        # Settings variables
        self.mesh_min_var = tk.StringVar()
        self.mesh_max_var = tk.StringVar()
        self.probe_count_var = tk.StringVar()

        # UI state variables
        self.show_probe_overlay = tk.BooleanVar(value=False)
        self.snap_var = tk.BooleanVar(value=False)

    def apply_loaded_settings(self, settings: BedMeshSettings) -> None:
        """Apply loaded settings to the UI variables."""
        self.mesh_min_var.set(settings.mesh_min)
        self.mesh_max_var.set(settings.mesh_max)
        self.probe_count_var.set(settings.probe_count)
