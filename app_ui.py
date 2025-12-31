# app_ui.py

from typing import Optional, List
import tkinter as tk

from config import logger
from models import MeshData, Region

# Manager imports
from ui_canvas import CanvasController
from ui_builder import UIBuilder
from file_manager import FileManager
from settings_manager import SettingsManager
from region_manager import RegionManager


class MeshRegionApp:
    """Main GUI app."""

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Bed Mesh Region Tool")

        # File paths
        self.mesh_path_var = tk.StringVar()
        self.settings_path_var = tk.StringVar()

        # Data
        self.mesh: Optional[MeshData] = None
        self.regions: List[Region] = []

        # Managers
        self.settings_manager = SettingsManager()
        self.file_manager = FileManager(self)
        self.region_manager = RegionManager(self)
        self.ui_builder = UIBuilder(self)

        # Canvas controller
        self.canvas_controller = CanvasController(self)

        # Build UI
        self.ui_builder.build_ui()

    # --- Status ---

    def _set_status(self, msg: str) -> None:
        self.status_bar.config(text=msg)
        self.root.update_idletasks()
        logger.info(msg)
