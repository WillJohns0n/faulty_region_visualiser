# config.py

import logging
import matplotlib

matplotlib.use("TkAgg")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bed_mesh_region_tool")


class Config:
    """Global configuration constants."""

    # Visuals
    COLORMAP = "viridis"
    FIGURE_SIZE = (7, 6)

    # Plot styling
    SCATTER_POINT_SIZE = 6
    SCATTER_ALPHA = 0.5
    RECT_COLOR = "red"
    RECT_STYLE = "--"
    RECT_LINEWIDTH = 1.5
    RECT_ZORDER = 6

    # GUI
    LISTBOX_WIDTH = 40
    LISTBOX_HEIGHT = 18

    # Undo/redo
    MAX_UNDO_STACK = 30

    # File
    SUPPORTED_EXTENSIONS = (".cfg",)
