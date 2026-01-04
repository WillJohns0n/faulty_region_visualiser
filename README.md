# Bed Mesh Faulty Region Visualiser

A visual tool to help optimize bed mesh settings and faulty regions on a **Prusa MK3/MK3S+ printer running Klipper**.

This tool provides an intuitive graphical interface to define, visualize, and manage faulty regions on your bed mesh.

<img width="1305" height="791" alt="image" src="https://github.com/user-attachments/assets/940ab946-97c0-4def-acd4-7f56872b770f" />


## Features

### Mesh Visualisation
- **Heatmap Display**: View your bed mesh as a color-mapped heatmap (brighter = higher Z offset)
- **Z-Scale Control**: Adjustable colour range sliders to highlight specific height variations
- **Mesh Grid Points**: Toggle display of individual mesh probe points
- **Smart Plot Area**: Dynamic plot area sizing based on print area (defaults to Prusa MK3: 250×210mm)

### Faulty Region Management
- **Interactive Drawing**: Click and drag on the mesh to draw rectangular faulty regions
- **Region Selection**: Click inside a region to select it (highlighted in yellow)
- **Drag to Move**: Click and drag from a region's center to reposition it
- **Resize Handles**: Hover near edges/corners for resize handles, drag to adjust
- **Live Coordinate Updates**: Region coordinates update in real-time during drag and resize operations
- **Grid Snapping**: Optional snapping to mesh grid points for precision alignment

### Probe Point Overlay
- **Visual Probe Points**: See exactly where your printer will probe
- **Exclusion Preview**: Points inside faulty regions shown as crosses (✕), valid points as circles (◯)
- **Auto-Update**: Overlay automatically updates when bed mesh settings or faulty regions change
- **Configurable Settings**: Adjust mesh_min, mesh_max, and probe_count.

### Workflow Features
- **Undo/Redo Support**: Full undo/redo functionality with toolbar buttons and keyboard shortcuts
- **Collapsible Panels**: Clean interface with expandable/collapsible settings sections
- **Tooltips**: Hover over buttons and labels for helpful guidance
- **Copy to Clipboard**: Export faulty region definitions ready to paste into your config
- **Direct Config Update**: Save regions directly to your configuration file

## Prerequisites

Before using this tool, you need to:

### 1. Create a High-Resolution Bed Mesh

On your Prusa MK3/MK3S+ printer, generate a high-resolution bed mesh for accurate faulty region identification:

#### a) Backup Your Configuration
Before making changes, save a copy of your current configuration file as a backup.

> **Note**: The `[bed_mesh]` section may be located in different files depending on your Klipper setup:
> - **Separate file**: Some setups (like Prusa MK3 with einsy-rambo board) use a separate `einsy-rambo.cfg` file
> - **printer.cfg**: Other setups have `[bed_mesh]` directly in `printer.cfg`
>
> Identify which file contains your `[bed_mesh]` section and back up that file.

#### b) Maximize Bed Mesh Area
Edit the `[bed_mesh]` section in your configuration file to maximize the usable bed area. Suggested values:
```ini
[bed_mesh]
mesh_max: 245, 210
mesh_min: 24, 6
```

After updating, run a quick **3x3 mesh test** while watching your printer to ensure these limits are safe and don't cause collisions. Check the probe is not leaving the boundary of the print plate.

#### c) Remove Interpolation
Disable mesh point interpolation for raw probe data:
```ini
mesh_pps: 0
```

#### d) Remove Existing Faulty Regions
Delete or comment out any pre-existing faulty region definitions in the `[bed_mesh]` section to start fresh.

#### e) Increase Probe Count
Use a high-resolution probe count for accurate magnet detection:
```ini
probe_count: 75, 75
```

Higher resolution meshes (e.g., 75x75) provide better accuracy for defining faulty regions but will take a long time for the printer to generate.

#### f) Optimize Probe Sampling (Optional)
In the `[probe]` section, consider reducing the probe sample count to speed up mesh generation if your probe repeatability is good (1 sample maybe enough for SuperPINDA):
```ini
samples: 2
```

Then run the full high-resolution mesh on your printer:
```gcode
BED_MESH_CALIBRATE
```

### 2. Save the mesh data

After calibrating, save the mesh to your printer configuration with the name **default**:

This saves the mesh data to `printer.cfg` in your Klipper configuration directory.

### 3. Restore Your Configuration and Download Mesh Data

Now that you have generated the high-resolution mesh data, restore your normal printing configuration:

#### a) Restore Backup Configuration
Restore your backup [bed_mesh] settings to reinstate your normal day-to-day printing settings. These are the correct settings for regular printing and will be needed to visualise your intended probe points and faulty regions in the tool.

#### b) Download Configuration Files

Download the required files from your printer via your Klipper web interface (Mainsail/Fluidd) or SSH:

##### `printer.cfg` (always required)
Contains the bed mesh point data (from the high-resolution calibration you just completed).

##### `einsy-rambo.cfg` or similar (only if [bed_mesh] is in a separate file)
If your `[bed_mesh]` settings are in a separate configuration file (common with Prusa MK3/einsy-rambo setups), download that file too.

> **Tip**: If your `[bed_mesh]` section is directly in `printer.cfg`, you only need to download `printer.cfg` — this single file contains both the mesh data and the settings.

## Installation

### System Requirements
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/) if you don't have it
  - During installation, **check the box "Add Python to PATH"** (important for Windows users)
  - Verify installation by opening a terminal/command prompt and typing: `python --version`

### Step-by-Step Setup

#### 1. Download This Repository
- Click the green "Code" button on GitHub and select "Download ZIP"
- Extract the ZIP file to a folder on your computer (e.g., `C:\Users\YourName\Downloads\faulty_region_visualiser`)

#### 2. Open a Terminal/Command Prompt
- **Windows**: Press `Win+R`, type `cmd`, and press Enter. Or right click on folder and select open in terminal.
- **macOS/Linux**: Open Terminal from Applications

#### 3. Navigate to the Project Folder
Type the following command, replacing the path with where you extracted the files:
```bash
cd C:\Users\YourName\Downloads\faulty_region_visualiser
```

#### 4. Install Dependencies
Copy and paste this command, then press Enter:
```bash
pip install -r requirements.txt
```
This will download and install all required Python packages. You'll see some text scrolling by — this is normal. Wait for it to finish.

## Usage

### Running the Tool

```bash
python main.py
```

The GUI will open with a panel interface on the left side.

### Interface Overview

The left panel contains these sections:
- **Toolbar**: Undo (↶), Redo (↷), and Close (✕) buttons
- **Files**: Load mesh data and configuration files
- **Visualisation settings**: Z-scale, print area, mesh grid, and snap options (collapsed by default)
- **Bed mesh settings**: Klipper mesh_min, mesh_max, probe_count, and probe overlay toggle
- **Faulty regions**: List of defined regions with Delete, Clear, Copy, and Save buttons

### Step-by-Step Workflow

1. **Load Mesh Data**
   - Click "..." next to "Mesh source" and select your `printer.cfg` file
   - **If `[bed_mesh]` is in a separate file** (e.g., `einsy-rambo.cfg`):
     - Click "..." next to "Mesh settings" and select that configuration file
   - **If `[bed_mesh]` is in `printer.cfg`**:
     - Check the box **"[bed_mesh] is in printer.cfg"** — this hides the separate settings file option
   - Click "Load data" to import the mesh and settings

2. **Visualize Your Mesh**
   - The bed mesh heatmap displays automatically (brighter colors = higher Z offset)
   - Expand "Visualisation settings" to adjust Z-scale colour range

3. **Configure Probe Overlay**
   - In "Bed mesh settings", verify mesh_min, mesh_max, and probe_count match your intended Klipper config
   - Red circles (◯) = valid probe points
   - Red crosses (✕) = probe points excluded by faulty regions
   - The overlay updates automatically when you change settings or modify regions

4. **Define Faulty Regions**
   - Click and drag on the mesh to draw rectangular regions around areas affected by magnets
   - Regions are outlined in **red dashed lines**

5. **Manage Regions**
   - **Select**: Click inside a region to select it (turns **yellow**)
   - **Move**: Click and drag from the center of a selected region to reposition it
   - **Resize**: Hover near edges/corners for resize handles, drag to adjust
   - **Delete**: Select a region and press **Delete** or click "Delete"
   - **Clear**: Remove all regions at once
   - Coordinates in the list update live during drag and resize operations

6. **Export Configuration**
   - Click "Copy" to copy region definitions to clipboard
   - Click "Save" to write regions directly to your configuration file
     - If "[bed_mesh] is in printer.cfg" is checked, updates `printer.cfg`
     - Otherwise, updates the separate settings file (e.g., `einsy-rambo.cfg`)

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Delete` | Delete selected region |

### Visualisation Settings

Expand the "Visualisation settings" panel to access:
- **Print area X/Y max**: Set your printer's bed dimensions (affects plot bounds)
- **Z-scale sliders**: Adjust the colour range to highlight specific height variations
- **Reset to data range**: Restore Z-scale to the actual mesh data range
- **Show mesh grid points**: Toggle visibility of individual mesh probe points on the heatmap
- **Snap rectangles to mesh grid**: Enable grid snapping for precise region placement


