# R6 Sensitivity Calibration System

A **Python + Pygame** mouse sensitivity calibration tool for Rainbow Six Siege. It uses Flick Tests to measure your actual aiming consistency and provides sensitivity adjustment recommendations.

---

## Core Design Philosophy

**Not an exact simulation of the R6 physics engine**, but a **relative, repeatable linear model**:

1. A red target appears at a random position on screen
2. You flick your mouse from screen center toward the target
3. The system records "actual mouse movement" vs "ideal distance (center to target)"
4. It calculates the overshoot/undershoot ratio and suggests sensitivity adjustments

---

## Features

| Feature | Description |
|---------|-------------|
| **Settings Screen** | Adjust DPI, FOV, XFactorAiming, horizontal/vertical sensitivity, resolution, aspect ratio, ADS |
| **Flick Test** | Randomly generated targets, records each trial's mouse movement |
| **Real-time Analysis** | After 3 trials, automatically calculates average ratio and recommends sensitivity values |
| **Adjustable Threshold** | Threshold(%) can be changed in Settings to control how strict "on target" is judged |
| **Dynamic Window** | Auto-calculates window size based on screen resolution; supports 16:9 / 4:3 switching |

---

## Installation

```bash
pip install -r requirements.txt
```

Only dependency: `pygame>=2.5.0`

---

## Usage

```bash
python main.py
```

By default, it launches directly into the **Experiment** screen. Use the top-right button to switch to **Settings**.

---

## Building a Standalone Executable

Want to share this tool with friends without asking them to install Python? Package it with **PyInstaller**.

### Prerequisites

```bash
pip install pyinstaller
```

### One-Time Setup (Optional Icon)

Place your `icon.ico` in the project root.

### Build Command

```bash
# Onedir (recommended — faster startup, smaller file size)
pyinstaller main.py --name "R6-Sens-Calibration" --windowed --onedir --noupx --icon "icon.ico"

# Or oneline (single .exe — slower startup, easier to share)
pyinstaller main.py --name "R6-Sens-Calibration" --windowed --onefile --noupx --icon "icon.ico"
```

| Parameter | Meaning |
|-----------|---------|
| `--windowed` | No console window pops up |
| `--onedir` | Output a folder with all dependencies |
| `--onefile` | Output a single .exe (slower launch) |
| `--noupx` | Disable UPX compression (avoids DLL issues) |
| `--icon "icon.ico"` | Custom application icon |

### Output

```
dist/
└── R6-Sens-Calibration/          ← Ready-to-run folder
    ├── R6-Sens-Calibration.exe
    ├── python3.dll
    └── ...
```

**The entire `dist/R6-Sens-Calibration/` folder is portable.** Zip it up and run on any Windows PC without Python installed.

### Rebuild After Code Changes

```bash
rm -r -fo build, dist        # Clean old artifacts
pyinstaller R6-Sens-Calibration.spec --clean
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `Failed to load Python DLL` | Add `--noupx` or manually copy `python312.dll` from your Python install into `build/R6-Sens-Calibration/_internal/` |
| Output file too large | Normal — PyInstaller bundles the entire Python runtime |
| Icon not showing | Make sure the file is a valid `.ico` format, not just renamed `.png` |

---

## Controls

### Flick Test Screen

| Key / Action | Function |
|--------------|----------|
| `SPACE` | Start / end a trial |
| Move mouse | Flick from center toward the red target |
| `Reset` button (bottom-left) | Clear all trial records |

**Analysis Logic**:
- `ratio = 1.0`: Perfectly hit the target
- `ratio > 1.0`: Overshoot (mouse moved farther than the target)
- `ratio < 1.0`: Undershoot (mouse moved less than the target)
- Average ratio within `[1 - threshold%, 1 + threshold%]` is considered "on target"

---

## Project Structure

```
dpiFineTune/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── config/
│   └── ads_data.py            # ADS zoom level data table
├── core/
│   └── app.py                 # Main Application, SensitivityModel
├── models/
│   └── settings.py            # R6Settings dataclass (all settings fields)
└── ui/
    ├── colors.py              # Centralized color constants
    ├── components.py          # Reusable UI components (Dropdown, InputField)
    ├── settings_screen.py     # Settings screen
    └── experiment_screen.py   # Flick Test experiment screen
```

---

## Settings Reference

| Field | Default | Description |
|-------|---------|-------------|
| DPI | 900 | Mouse DPI |
| FOV | 84 | Field of view |
| XFactorAiming | 0.00223 | Aiming sensitivity multiplier |
| **Threshold(%)** | **15** | **Flick Test hit detection tolerance** |
| Horizontal | 10 | Horizontal sensitivity |
| Vertical | 10 | Vertical sensitivity |
| Resolution | 1920x1080 | Screen resolution |
| Aspect Ratio | 16:9 | Display aspect ratio |
| Zoom | 1.0x | ADS zoom level |

---

## Development History

Built with **incremental development** — each layer was verified before adding the next:

1. ✅ Basic Pygame window and screen switching
2. ✅ Settings dataclass and UI components (Dropdown, InputField)
3. ✅ Dynamic window sizing and aspect ratio adaptation
4. ✅ Flick Test screen and mouse recording
5. ✅ Pixel-based ratio analysis (abandoned angle conversion)
6. ✅ Threshold centralization and Settings page integration
7. ✅ Dead code cleanup and architecture refinement

---

## Notes

- All sensitivity recommendations are **relative reference values**; actual feel depends on personal preference
- The `zoom` field in the ADS data table is a placeholder, not the official Ubisoft multiplier
- This project is for personal learning and aim calibration purposes; not affiliated with Ubisoft

---

## License

MIT
