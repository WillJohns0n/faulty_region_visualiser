# file_manager.py

from pathlib import Path
from tkinter import filedialog, messagebox

from config import logger
from parser_mesh import read_text as read_mesh_text, parse_latest_mesh
from parser_settings import (
    read_text as read_settings_text,
    parse_bed_mesh_settings,
    update_bed_mesh_section,
)


class FileManager:
    """Handles file operations for loading and saving configuration files."""

    def __init__(self, app):
        self.app = app

    def browse_mesh(self) -> None:
        """Browse for mesh configuration file."""
        path = filedialog.askopenfilename(
            title="Select mesh config file",
            filetypes=[("Config files", "*.cfg"), ("All files", "*.*")],
        )
        if path:
            self.app.mesh_path_var.set(path)

    def browse_settings(self) -> None:
        """Browse for settings configuration file."""
        path = filedialog.askopenfilename(
            title="Select settings config file",
            filetypes=[("Config files", "*.cfg"), ("All files", "*.*")],
        )
        if path:
            self.app.settings_path_var.set(path)

    def load_data(self) -> None:
        """Load mesh and settings data from selected files."""
        mesh_path = self.app.mesh_path_var.get().strip()
        settings_path = self.app.settings_path_var.get().strip()

        if not mesh_path or not settings_path:
            messagebox.showwarning(
                "Missing files", "Please select both printer.cfg and einsy-rambo.cfg."
            )
            return

        mesh_file = Path(mesh_path)
        settings_file = Path(settings_path)

        try:
            m_txt = read_mesh_text(mesh_file)
            mesh = parse_latest_mesh(m_txt)
            if not mesh:
                raise ValueError("Failed to parse bed mesh from printer.cfg")

            s_txt = read_settings_text(settings_file)
            settings = parse_bed_mesh_settings(s_txt)

            self.app.settings_manager.apply_loaded_settings(settings)
            self.app.region_manager.apply_loaded_data(mesh, settings)
            self.app._set_status("Loaded mesh and settings")

        except Exception as e:
            logger.exception("Error loading data")
            messagebox.showerror("Error", str(e))
            self.app._set_status("Load failed")

    def update_settings_cfg(self) -> None:
        """Update the settings configuration file with current regions."""
        if not self.app.settings_path_var.get().strip():
            messagebox.showwarning(
                "No settings file", "Please select einsy-rambo.cfg first."
            )
            return
        settings_path = Path(self.app.settings_path_var.get().strip())
        try:
            content = read_settings_text(settings_path)

            pairs = [(r.min_point, r.max_point) for r in self.app.regions]

            updated = update_bed_mesh_section(
                content,
                self.app.settings_manager.mesh_min_var.get().strip(),
                self.app.settings_manager.mesh_max_var.get().strip(),
                self.app.settings_manager.probe_count_var.get().strip(),
                pairs,
            )
            settings_path.write_text(updated, encoding="utf-8")
            messagebox.showinfo("Updated", f"Updated [bed_mesh] in:\n{settings_path}")
            self.app._set_status("Updated einsy-rambo.cfg")
        except Exception as e:
            logger.exception("Update failed")
            messagebox.showerror("Error", f"Failed to update:\n{e}")
            self.app._set_status("Update failed")
