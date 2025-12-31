# main.py

import tkinter as tk
from app_ui import MeshRegionApp
from config import logger


def main() -> None:
    try:
        root = tk.Tk()
        MeshRegionApp(root)
        logger.info("Application started")
        root.mainloop()
    except Exception:
        logger.exception("Fatal error")
        raise


if __name__ == "__main__":
    main()
