# ui_builder.py

import tkinter as tk
from tkinter import ttk

from config import Config
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from visualizer import MeshVisualizer


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

        self._build_file_selection(left)
        self._build_settings_section(left)
        self._build_snap_toggle(left)
        self._build_region_list(left)
        self._build_buttons(left)

        # Matplotlib figure
        self.app.fig, self.app.ax = plt.subplots(figsize=Config.FIGURE_SIZE)
        self.app.visualizer = MeshVisualizer(self.app.fig, self.app.ax)
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
        frame = ttk.LabelFrame(parent, text="Files", padding=(4, 4))
        frame.pack(fill="x", pady=(0, 6))

        ttk.Label(frame, text="Mesh source (printer.cfg):").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(frame, textvariable=self.app.mesh_path_var, width=32).grid(
            row=0, column=1, padx=4
        )
        ttk.Button(
            frame, text="Browse", command=lambda: self.app.file_manager.browse_mesh()
        ).grid(row=0, column=2, padx=2)

        # Checkbox for [bed_mesh] in printer.cfg
        ttk.Checkbutton(
            frame,
            text="[bed_mesh] is in printer.cfg",
            variable=self.app.settings_manager.bed_mesh_in_printer_cfg,
            command=self._toggle_settings_row,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 4))

        # Settings file row (can be hidden)
        self.settings_label = ttk.Label(frame, text="Settings (einsy-rambo.cfg):")
        self.settings_label.grid(row=2, column=0, sticky="w")
        self.settings_entry = ttk.Entry(
            frame, textvariable=self.app.settings_path_var, width=32
        )
        self.settings_entry.grid(row=2, column=1, padx=4)
        self.settings_browse_btn = ttk.Button(
            frame,
            text="Browse",
            command=lambda: self.app.file_manager.browse_settings(),
        )
        self.settings_browse_btn.grid(row=2, column=2, padx=2)

        self.app.load_button = ttk.Button(
            frame, text="Load data", command=self.app.file_manager.load_data
        )
        self.app.load_button.grid(row=3, column=1, pady=6)

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

    def _build_settings_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Bed mesh settings", padding=(4, 4))
        frame.pack(fill="x", pady=(0, 6))

        ttk.Label(frame, text="mesh_min:").grid(row=0, column=0, sticky="w")
        ttk.Entry(
            frame, textvariable=self.app.settings_manager.mesh_min_var, width=16
        ).grid(row=0, column=1, padx=4)

        ttk.Label(frame, text="mesh_max:").grid(row=1, column=0, sticky="w")
        ttk.Entry(
            frame, textvariable=self.app.settings_manager.mesh_max_var, width=16
        ).grid(row=1, column=1, padx=4)

        ttk.Label(frame, text="probe_count:").grid(row=2, column=0, sticky="w")
        ttk.Entry(
            frame, textvariable=self.app.settings_manager.probe_count_var, width=16
        ).grid(row=2, column=1, padx=4)

        # Plot area settings
        ttk.Separator(frame, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=6
        )

        ttk.Label(frame, text="print area x max (mm):").grid(
            row=4, column=0, sticky="w"
        )
        ttk.Entry(
            frame, textvariable=self.app.settings_manager.plot_area_x_var, width=16
        ).grid(row=4, column=1, padx=4)

        ttk.Label(frame, text="print area y max (mm):").grid(
            row=5, column=0, sticky="w"
        )
        ttk.Entry(
            frame, textvariable=self.app.settings_manager.plot_area_y_var, width=16
        ).grid(row=5, column=1, padx=4)

        # Probe overlay controls
        ttk.Checkbutton(
            frame,
            text="Show probe points",
            variable=self.app.settings_manager.show_probe_overlay,
            command=self.app.canvas_controller.update_probe_overlay,
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 0))

        ttk.Button(
            frame,
            text="Update overlay",
            command=self.app.canvas_controller.update_probe_overlay,
        ).grid(row=7, column=0, columnspan=2, pady=(4, 0), sticky="ew")

    def _build_snap_toggle(self, parent: ttk.Frame) -> None:
        ttk.Checkbutton(
            parent,
            text="Snap rectangles to mesh grid",
            variable=self.app.settings_manager.snap_var,
        ).pack(anchor="w", pady=(4, 6))

    def _build_region_list(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="faulty_region definitions:").pack(anchor="w")

        # Create a frame to hold the listbox and scrollbar
        listbox_frame = ttk.Frame(parent)
        listbox_frame.pack(pady=(2, 4), fill="both", expand=True)

        # Create the scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")

        # Create the listbox and configure it with the scrollbar
        self.app.region_list = tk.Listbox(
            listbox_frame,
            width=Config.LISTBOX_WIDTH,
            height=Config.LISTBOX_HEIGHT,
            yscrollcommand=scrollbar.set,
        )
        self.app.region_list.pack(side="left", fill="both", expand=True)

        # Configure scrollbar to work with listbox
        scrollbar.config(command=self.app.region_list.yview)

    def _build_buttons(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        ttk.Button(
            frame,
            text="Delete selected",
            command=self.app.region_manager.delete_selected,
        ).pack(side="left", padx=2)
        ttk.Button(
            frame, text="Clear all", command=self.app.region_manager.clear_all_regions
        ).pack(side="left", padx=2)

        frame2 = ttk.Frame(parent)
        frame2.pack(fill="x", pady=(4, 0))
        ttk.Button(frame2, text="Undo", command=self.app.region_manager.undo).pack(
            side="left", padx=2
        )
        ttk.Button(frame2, text="Redo", command=self.app.region_manager.redo).pack(
            side="left", padx=2
        )

        frame3 = ttk.Frame(parent)
        frame3.pack(fill="x", pady=(4, 0))
        ttk.Button(
            frame3,
            text="Copy to clipboard",
            command=self.app.region_manager.copy_to_clipboard,
        ).pack(side="left", padx=2)
        ttk.Button(
            frame3,
            text="Update config file",
            command=self.app.file_manager.update_settings_cfg,
        ).pack(side="left", padx=2)

        frame4 = ttk.Frame(parent)
        frame4.pack(fill="x", pady=(6, 0))
        ttk.Button(frame4, text="Close", command=self._quit_app).pack(
            side="left", padx=2
        )

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
