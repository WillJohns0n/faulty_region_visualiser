# Bed Mesh Faulty Region Visualiser

A visual tool to help optimize bed mesh settings and faulty regions on a **Prusa MK3/MK3S+ printer running Klipper**.

This tool provides an intuitive graphical interface to define, visualize, and manage faulty regions on your bed mesh.

## Features

- **Visual Mesh Display**: See your bed mesh as a color-mapped heatmap
- **Interactive Region Drawing**: Draw rectangular faulty regions directly on the mesh visualization
- **Region Management**: Select, resize, and delete regions with real-time updates
- **Probe Point Overlay**: Visualize bed probe points and excluded regions
- **Auto-generated Config**: Export faulty region definitions directly to your configuration
- **Undo/Redo Support**: Full undo/redo functionality for all operations
- **Grid Snapping**: Optional snapping to mesh grid points for precision

## Prerequisites

Before using this tool, you need to:

### 1. Create a High-Resolution Bed Mesh

On your Prusa MK3/MK3S+ printer, generate a high-resolution bed mesh (minimum **50x50 points**):

```gcode
BED_MESH_CALIBRATE METHOD=automatic PROFILE=default
```

Higher resolution meshes (e.g., 100x100) provide better accuracy for defining faulty regions.

### 2. Save Configuration

After calibrating, save the mesh to your printer configuration:

```gcode
SAVE_CONFIG
```

This saves the mesh data to `printer.cfg` in your Klipper configuration directory.

### 3. Download Configuration Files

You need two files from your printer:

#### `printer.cfg`
Contains the bed mesh point data. Download from your Klipper web interface or via SSH.

#### `einsy-rambo.cfg`
Contains existing faulty region definitions and bed mesh settings.

## Installation

### Requirements
- Python 3.8+
- pip

### Setup

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Tool

```bash
python main.py
```

The GUI will open with a file selection panel on the left.

### Step-by-Step Workflow

1. **Load Mesh Data**
   - Click "Browse" next to "Mesh source (printer.cfg)" and select your `printer.cfg` file
   - Click "Browse" next to "Settings (einsy-rambo.cfg)" and select your configuration file
   - Click "Load data" to import the mesh and settings

2. **Visualize Your Mesh**
   - The bed mesh heatmap will display (brighter colors = higher Z offset)
   - Black dots show all probe points in the mesh

3. **Define Faulty Regions**
   - Click and drag on the mesh to draw rectangular regions that need compensation
   - Regions are outlined in **red dashed lines**
   - Release to finish drawing

4. **Manage Regions**
   - **Select**: Click inside a region to select it (turns **yellow**)
   - **Resize**: Hover near edges/corners for resize handles, drag to adjust
   - **Delete**: Select a region and press **Delete** or click "Delete selected"
   - **Clear All**: Remove all regions at once

5. **Adjust Settings**
   - Configure mesh bounds in "Bed mesh settings":
     - **mesh_min**: Lower-left corner of mesh (mm)
     - **mesh_max**: Upper-right corner of mesh (mm)
     - **probe_count**: Number of probe points (e.g., 7x7)

6. **Preview Probe Points**
   - Enable "Show probe points" checkbox to overlay probe locations
   - Red circles (◯) = valid probe points
   - Red crosses (✕) = probe points excluded by faulty regions
   - Adjust settings and click "Update overlay" to refresh

7. **Export Configuration**
   - Click "Copy to clipboard" to copy region definitions
   - Click "Update einsy-rambo.cfg" to automatically save to your settings file

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Delete` | Delete selected region |

### Grid Snapping

Enable "Snap rectangles to mesh grid" to automatically align regions to your mesh points.

## Configuration File Format

### einsy-rambo.cfg

The tool generates configuration in Klipper format:

```ini
[bed_mesh]
mesh_min: 0.1, 0.1
mesh_max: 249.0, 209.0
probe_count: 50, 50

faulty_region_1_min: 10.0, 20.5
faulty_region_1_max: 40.0, 50.5
faulty_region_2_min: 100.0, 100.0
faulty_region_2_max: 150.0, 120.0
```

Copy these definitions into your Klipper configuration:
- For Mainsail/Fluidd web interface: Paste into your `einsy-rambo.cfg` file
- Or add directly to `printer.cfg` and run `SAVE_CONFIG`

