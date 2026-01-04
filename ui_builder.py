# ui_builder.py

import tkinter as tk
from tkinter import ttk

from config import Config
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from visualizer import MeshVisualizer


class ToolTip:
    """Simple tooltip for tkinter widgets."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show_tip)
        widget.bind("<Leave>", self._hide_tip)

    def _show_tip(self, event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("TkDefaultFont", 9),
            padx=4,
            pady=2,
        )
        label.pack()

    def _hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class CollapsibleFrame(ttk.Frame):
    """A frame that can be collapsed/expanded with a toggle button."""

    def __init__(self, parent, text="", collapsed=False, **kwargs):
        super().__init__(parent, **kwargs)

        self._collapsed = tk.BooleanVar(value=collapsed)

        # Header frame with toggle button
        self.header = ttk.Frame(self)
        self.header.pack(fill="x")

        self.toggle_btn = ttk.Button(
            self.header,
            text="▼ " + text if not collapsed else "▶ " + text,
            command=self._toggle,
            style="Toolbutton",
        )
        self.toggle_btn.pack(fill="x")

        # Content frame
        self.content = ttk.Frame(self, padding=(4, 4))
        if not collapsed:
            self.content.pack(fill="both", expand=True)

        self._text = text

    def _toggle(self):
        if self._collapsed.get():
            self.content.pack(fill="both", expand=True)
            self.toggle_btn.config(text="▼ " + self._text)
            self._collapsed.set(False)
        else:
            self.content.forget()
            self.toggle_btn.config(text="▶ " + self._text)
            self._collapsed.set(True)

    def get_content_frame(self) -> ttk.Frame:
        """Return the content frame for adding widgets."""
        return self.content


class UIBuilder:
    """Handles construction of the GUI components."""

    def __init__(self, app):
        self.app = app

    def build_ui(self) -> None:
        """Build the complete UI structure."""
        self._build_status_bar()
        self._build_main_layout()
        self._setup_keybindings()

    def _build_main_layout(self) -> None:
        left = ttk.Frame(self.app.root, padding=(6, 6))
        left.pack(side="left", fill="y")

        right = ttk.Frame(self.app.root)
        right.pack(side="right", fill="both", expand=True)

        self._build_toolbar(left)
        self._build_file_selection(left)
        self._build_visualisation_settings(left)
        self._build_bed_mesh_settings(left)
        self._build_region_list(left)

        # Matplotlib figure
        self.app.fig, self.app.ax = plt.subplots(figsize=Config.FIGURE_SIZE)
        self.app.visualizer = MeshVisualizer(self.app.fig, self.app.ax)

        # Connect visualizer callback to update z-scale when mesh data changes
        self.app.visualizer.on_z_range_changed = self.update_z_scale_range

        self.app.canvas = FigureCanvasTkAgg(self.app.fig, master=right)
        self.app.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Mouse events now routed to controller
        self.app.canvas.mpl_connect(
            "button_press_event", self.app.canvas_controller.on_mouse_press
        )
        self.app.canvas.mpl_connect(
            "motion_notify_event", self.app.canvas_controller.on_mouse_move
        )
        self.app.canvas.mpl_connect(
            "button_release_event", self.app.canvas_controller.on_mouse_release
        )

    def _build_file_selection(self, parent: ttk.Frame) -> None:
        section = CollapsibleFrame(parent, text="Files", collapsed=False)
        section.pack(fill="x", pady=(0, 6))
        frame = section.get_content_frame()

        mesh_label = ttk.Label(frame, text="Mesh source:")
        mesh_label.grid(row=0, column=0, sticky="w")
        ToolTip(mesh_label, "Select printer.cfg to load [bed_mesh default] mesh data")

        ttk.Entry(frame, textvariable=self.app.mesh_path_var, width=24).grid(
            row=0, column=1, padx=4
        )
        ttk.Button(
            frame,
            text="...",
            width=3,
            command=lambda: self.app.file_manager.browse_mesh(),
        ).grid(row=0, column=2, padx=2)

        # Checkbox for [bed_mesh] in printer.cfg
        bed_mesh_checkbox = ttk.Checkbutton(
            frame,
            text="[bed_mesh] is in printer.cfg",
            variable=self.app.settings_manager.bed_mesh_in_printer_cfg,
            command=self._toggle_settings_row,
        )
        bed_mesh_checkbox.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 4))
        ToolTip(
            bed_mesh_checkbox,
            "Tick if [bed_mesh] config is in printer.cfg.\nUntick if it's in a separate file (e.g. einsy-rambo.cfg for Prusa MK3)",
        )

        # Settings file row (can be hidden)
        self.settings_label = ttk.Label(frame, text="Mesh settings:")
        self.settings_label.grid(row=2, column=0, sticky="w")
        ToolTip(
            self.settings_label,
            "Select the file containing [bed_mesh] configuration\n(mesh_min, mesh_max, probe_count etc.)",
        )

        self.settings_entry = ttk.Entry(
            frame, textvariable=self.app.settings_path_var, width=24
        )
        self.settings_entry.grid(row=2, column=1, padx=4)
        self.settings_browse_btn = ttk.Button(
            frame,
            text="...",
            width=3,
            command=lambda: self.app.file_manager.browse_settings(),
        )
        self.settings_browse_btn.grid(row=2, column=2, padx=2)

        load_btn = ttk.Button(
            frame, text="Load data", command=self.app.file_manager.load_data
        )
        load_btn.grid(row=3, column=1, pady=6)
        self.app.load_button = load_btn
        ToolTip(load_btn, "Load mesh data from selected files")

    def _toggle_settings_row(self) -> None:
        """Show or hide the settings file row based on checkbox state."""
        if self.app.settings_manager.bed_mesh_in_printer_cfg.get():
            self.settings_label.grid_remove()
            self.settings_entry.grid_remove()
            self.settings_browse_btn.grid_remove()
        else:
            self.settings_label.grid()
            self.settings_entry.grid()
            self.settings_browse_btn.grid()

    def _build_visualisation_settings(self, parent: ttk.Frame) -> None:
        """Build the visualisation settings section (formerly height map settings)."""
        section = CollapsibleFrame(
            parent, text="Visualisation settings", collapsed=True
        )
        section.pack(fill="x", pady=(0, 6))
        frame = section.get_content_frame()

        # --- Print area settings ---
        ttk.Label(frame, text="Print area X max (mm):").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(
            frame, textvariable=self.app.settings_manager.plot_area_x_var, width=12
        ).grid(row=0, column=1, padx=4, sticky="w")

        ttk.Label(frame, text="Print area Y max (mm):").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Entry(
            frame, textvariable=self.app.settings_manager.plot_area_y_var, width=12
        ).grid(row=1, column=1, padx=4, sticky="w")

        # Separator
        ttk.Separator(frame, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=6
        )

        # --- Z-scale controls ---
        ttk.Label(frame, text="Z-scale (colour range):").grid(
            row=3, column=0, columnspan=3, sticky="w"
        )

        # Min slider
        ttk.Label(frame, text="Min:").grid(row=4, column=0, sticky="w")
        self.z_min_scale = ttk.Scale(
            frame,
            from_=0,
            to=1,
            variable=self.app.settings_manager.z_scale_min_var,
            orient="horizontal",
            command=self._on_z_scale_changed,
        )
        self.z_min_scale.grid(row=4, column=1, sticky="ew", padx=4)
        self.z_min_label = ttk.Label(frame, text="0.000", width=8)
        self.z_min_label.grid(row=4, column=2, sticky="e")

        # Max slider
        ttk.Label(frame, text="Max:").grid(row=5, column=0, sticky="w")
        self.z_max_scale = ttk.Scale(
            frame,
            from_=0,
            to=1,
            variable=self.app.settings_manager.z_scale_max_var,
            orient="horizontal",
            command=self._on_z_scale_changed,
        )
        self.z_max_scale.grid(row=5, column=1, sticky="ew", padx=4)
        self.z_max_label = ttk.Label(frame, text="1.000", width=8)
        self.z_max_label.grid(row=5, column=2, sticky="e")

        # Reset button
        reset_btn = ttk.Button(
            frame,
            text="Reset to data range",
            command=self._reset_z_scale,
        )
        reset_btn.grid(row=6, column=0, columnspan=3, pady=(4, 0), sticky="ew")
        ToolTip(reset_btn, "Reset colour scale to actual data range")

        # Separator
        ttk.Separator(frame, orient="horizontal").grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=6
        )

        # --- Display toggles ---
        ttk.Checkbutton(
            frame,
            text="Show mesh grid points",
            variable=self.app.settings_manager.show_mesh_grid,
            command=self.app.canvas_controller.update_probe_overlay,
        ).grid(row=8, column=0, columnspan=3, sticky="w")

        ttk.Checkbutton(
            frame,
            text="Snap rectangles to mesh grid",
            variable=self.app.settings_manager.snap_var,
        ).grid(row=9, column=0, columnspan=3, sticky="w", pady=(2, 0))

        # Configure column weights for proper resizing
        frame.columnconfigure(1, weight=1)

    def _on_z_scale_changed(self, _=None) -> None:
        """Handle z-scale slider changes."""
        vmin = self.app.settings_manager.z_scale_min_var.get()
        vmax = self.app.settings_manager.z_scale_max_var.get()

        # Update labels
        self.z_min_label.config(text=f"{vmin:.3f}")
        self.z_max_label.config(text=f"{vmax:.3f}")

        # Update visualizer if available
        if hasattr(self.app, "visualizer") and self.app.visualizer:
            self.app.visualizer.update_clim(vmin, vmax)

    def _reset_z_scale(self) -> None:
        """Reset z-scale to the actual data range."""
        z_min, z_max = self.app.settings_manager.get_z_range()
        self.app.settings_manager.z_scale_min_var.set(z_min)
        self.app.settings_manager.z_scale_max_var.set(z_max)
        self._on_z_scale_changed()

    def update_z_scale_range(self, z_min: float, z_max: float) -> None:
        """Update slider ranges when new mesh data is loaded."""
        # Update settings manager
        self.app.settings_manager.update_z_range(z_min, z_max)

        # Update slider ranges
        self.z_min_scale.configure(from_=z_min, to=z_max)
        self.z_max_scale.configure(from_=z_min, to=z_max)

        # Update labels
        self._on_z_scale_changed()

    def _build_bed_mesh_settings(self, parent: ttk.Frame) -> None:
        """Build the bed mesh settings section (Klipper config values)."""
        section = CollapsibleFrame(parent, text="Bed mesh settings", collapsed=False)
        section.pack(fill="x", pady=(0, 6))
        frame = section.get_content_frame()

        ttk.Label(frame, text="mesh_min:").grid(row=0, column=0, sticky="w")
        mesh_min_entry = ttk.Entry(
            frame, textvariable=self.app.settings_manager.mesh_min_var, width=14
        )
        mesh_min_entry.grid(row=0, column=1, padx=4)

        ttk.Label(frame, text="mesh_max:").grid(row=1, column=0, sticky="w")
        mesh_max_entry = ttk.Entry(
            frame, textvariable=self.app.settings_manager.mesh_max_var, width=14
        )
        mesh_max_entry.grid(row=1, column=1, padx=4)

        ttk.Label(frame, text="probe_count:").grid(row=2, column=0, sticky="w")
        probe_count_entry = ttk.Entry(
            frame, textvariable=self.app.settings_manager.probe_count_var, width=14
        )
        probe_count_entry.grid(row=2, column=1, padx=4)

        # Separator
        ttk.Separator(frame, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=6
        )

        # Probe overlay controls
        ttk.Checkbutton(
            frame,
            text="Show probe points overlay",
            variable=self.app.settings_manager.show_probe_overlay,
            command=self.app.canvas_controller.update_probe_overlay,
        ).grid(row=4, column=0, columnspan=2, sticky="w")

        # Add trace callbacks to auto-update overlay when settings change
        self.app.settings_manager.mesh_min_var.trace_add(
            "write", self._on_mesh_settings_changed
        )
        self.app.settings_manager.mesh_max_var.trace_add(
            "write", self._on_mesh_settings_changed
        )
        self.app.settings_manager.probe_count_var.trace_add(
            "write", self._on_mesh_settings_changed
        )

    def _on_mesh_settings_changed(self, *args) -> None:
        """Auto-update probe overlay when mesh settings change."""
        # Use after_idle to debounce rapid changes during typing
        if hasattr(self, "_mesh_settings_update_pending"):
            self.app.root.after_cancel(self._mesh_settings_update_pending)
        self._mesh_settings_update_pending = self.app.root.after(
            300, self.app.canvas_controller.update_probe_overlay
        )

    def _build_region_list(self, parent: ttk.Frame) -> None:
        section = CollapsibleFrame(parent, text="Faulty regions", collapsed=False)
        section.pack(fill="both", expand=True, pady=(0, 6))
        frame = section.get_content_frame()

        # Pack buttons at the bottom FIRST so listbox can expand into remaining space
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side="bottom", fill="x", pady=(4, 0))

        del_btn = ttk.Button(
            btn_frame,
            text="Delete",
            width=8,
            command=self.app.region_manager.delete_selected,
        )
        del_btn.pack(side="left", padx=1)
        ToolTip(del_btn, "Delete selected region (Del)")

        clear_btn = ttk.Button(
            btn_frame,
            text="Clear",
            width=8,
            command=self.app.region_manager.clear_all_regions,
        )
        clear_btn.pack(side="left", padx=1)
        ToolTip(clear_btn, "Clear all regions")

        copy_btn = ttk.Button(
            btn_frame,
            text="Copy",
            width=8,
            command=self.app.region_manager.copy_to_clipboard,
        )
        copy_btn.pack(side="left", padx=1)
        ToolTip(copy_btn, "Copy regions to clipboard")

        save_btn = ttk.Button(
            btn_frame,
            text="Save",
            width=8,
            command=self.app.file_manager.update_settings_cfg,
        )
        save_btn.pack(side="left", padx=1)
        ToolTip(save_btn, "Save regions to config file")

        # Create a frame to hold the listbox and scrollbar - fills remaining space
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(side="top", fill="both", expand=True, pady=(2, 4))

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")

        # Create the listbox - expands to fill available space
        self.app.region_list = tk.Listbox(
            listbox_frame,
            width=Config.LISTBOX_WIDTH,
            yscrollcommand=scrollbar.set,
            selectbackground="#4a6cd4",
            selectforeground="white",
        )
        self.app.region_list.pack(side="left", fill="both", expand=True)

        # Configure scrollbar to work with listbox
        scrollbar.config(command=self.app.region_list.yview)

    def _build_toolbar(self, parent: ttk.Frame) -> None:
        """Build the toolbar with undo/redo/close buttons using symbols."""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=(0, 6))

        # Undo button with symbol
        undo_btn = ttk.Button(
            frame,
            text="↶",
            width=3,
            command=self.app.region_manager.undo,
        )
        undo_btn.pack(side="left", padx=1)
        ToolTip(undo_btn, "Undo (Ctrl+Z)")

        # Redo button with symbol
        redo_btn = ttk.Button(
            frame,
            text="↷",
            width=3,
            command=self.app.region_manager.redo,
        )
        redo_btn.pack(side="left", padx=1)
        ToolTip(redo_btn, "Redo (Ctrl+Y)")

        # Spacer
        ttk.Frame(frame).pack(side="left", expand=True)

        # Close button with symbol
        close_btn = ttk.Button(
            frame,
            text="✕",
            width=3,
            command=self._quit_app,
        )
        close_btn.pack(side="right", padx=1)
        ToolTip(close_btn, "Close application")

    def _quit_app(self):
        try:
            self.app.root.quit()
            self.app.root.destroy()
        except Exception:
            pass
        import sys

        sys.exit(0)

    def _build_status_bar(self) -> None:
        frame = ttk.Frame(self.app.root)
        frame.pack(side="bottom", fill="x")
        self.app.status_bar = ttk.Label(
            frame, text="Ready", relief=tk.SUNKEN, anchor="w"
        )
        self.app.status_bar.pack(side="left", fill="x", expand=True)

    def _setup_keybindings(self) -> None:
        self.app.root.bind("<Control-z>", lambda e: self.app.region_manager.undo())
        self.app.root.bind("<Control-y>", lambda e: self.app.region_manager.redo())
        self.app.root.bind(
            "<Delete>", lambda e: self.app.region_manager.delete_selected()
        )
