# Build Report v2 — Prototype Asset Generation Pass

Date: 2026-05-16
Author: automated generation pass

This pass added five missing prototype assets on top of the v1 build (which
already contained the schematic, BOM, mechanical CAD, and firmware).

## Generated artifacts

| # | Artifact | Path | Status |
|---|---|---|---|
| 1 | PCB layout (PCB1 power hub) | `urine_dipstick_analyzer.kicad_pcb` | Generated, **unrouted** |
| 1b | PCB generator | `generate_pcb.py` | OK |
| 2 | Gerbers | `gerbers/*.g??`, `gerbers.zip` | OK (20 layers + drill) |
| 3 | PlatformIO config | `firmware/urine_dipstick_analyzer/platformio.ini` | OK |
| 3b | TFT_eSPI shim | `firmware/urine_dipstick_analyzer/User_Setup.h` | Reference-only (firmware uses Adafruit_ILI9341) |
| 4 | Calibration data | `calibration.json` | OK |
| 5 | Assembly guide | `ASSEMBLY_GUIDE.md` | OK |

## Deliverable 1 — PCB layout: known limitations

The PCB generator places footprints, mounting holes, and GND zone fills on
both copper layers, but **does not auto-route** any signal nets. KiCad will
load the file cleanly; the user must run interactive routing on the small
handful of nets (VBUS, VBAT, +3V3, +5V, +9V, VMOT, SDA, SCL, CHRG_STAT, PG)
before fabricating. Net assignments are correct and DRC will identify the
remaining unrouted segments as ratlines.

Footprints emitted use KiCad standard library names — they are referenced by
name only, so the user must have KiCad's standard footprint libraries
installed (default with the KiCad install). Specifically:

- `MountingHole:MountingHole_2.7mm_M2.5`
- `Capacitor_SMD:C_0603_1608Metric`, `C_0805_2012Metric`, `C_1206_3216Metric`
- `Resistor_SMD:R_0603_1608Metric`
- `Fuse_SMD:Fuse_1812_4532Metric`
- `Package_SO:MSOP-10_3x3mm_P0.5mm`
- `Package_TO_SOT_SMD:SOT-23-8`
- `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`
- `Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical`

The USB-C breakout (U1a) is represented as a 2x8 pin-header footprint matching
the Adafruit/Amazon-style USB-C-BO-16P breakout. Only VBUS and GND pads are
mapped to nets; data lines are intentionally NC because PCB1 is a power hub
only — USB data passes through the breakout to a separate cable.

## Deliverable 2 — Gerbers: status

Exported successfully via `kicad-cli` 10.x:

- 20 gerber layer files (Cu, mask, silk, paste, courtyard, fab, edge cuts)
- 1 drill file (`urine_dipstick_analyzer.drl`)
- 1 gerber job file (`urine_dipstick_analyzer-job.gbrjob`)
- All packaged in `gerbers.zip` (≈24 KB)

Because the board is unrouted, the copper layers contain only pads + ground
fill. After hand-routing in KiCad, re-run:

```bash
python3 generate_pcb.py    # only if you want to start fresh
/Applications/KiCad.app/Contents/MacOS/kicad-cli pcb export gerbers --output gerbers/ urine_dipstick_analyzer.kicad_pcb
/Applications/KiCad.app/Contents/MacOS/kicad-cli pcb export drill   --output gerbers/ urine_dipstick_analyzer.kicad_pcb
cd gerbers && zip -r ../gerbers.zip *
```

## Deliverable 3 — PlatformIO

`platformio.ini` targets `esp32-s3-devkitc-1` with QIO flash + OPI PSRAM
build flags for the N8R8 variant. Library list reflects what the firmware
actually `#include`s (Adafruit_ILI9341, Adafruit_GFX, Adafruit_SHT31_Library,
BH1750 by claws, AccelStepper, ArduinoJson). DS3231 and MAX17048 are accessed
via raw `Wire`, so RTClib / MAX1704X libs are NOT pulled in. The OV2640 driver
ships with the espressif32 Arduino core.

`User_Setup.h` is included as a reference for users who want to swap to
TFT_eSPI for ~2× display performance. Not required for the current build.

## Deliverable 4 — Calibration

`calibration.json` (v1.0) contains:

- LED correction factors (white + UV intensity)
- Camera sensor settings (locked exposure, gain, AWB gains)
- Full 24-patch X-Rite ColorChecker Nano reference (Lab + sRGB)
- Per-pad calibration for all 10 dipstick parameters with: channel,
  range thresholds, reference RGB triplets per level, polynomial coefficients,
  units
- Pad ROI offsets in mm (10 pads, 6 mm pitch)
- Temperature compensation coefficients per parameter
- Reaction timing windows per pad

Values are realistic placeholders meant for first-power-on. The user MUST
re-run the in-firmware `/calibrate` routine with the actual ColorChecker
Nano (CAL1) under integrated illumination before clinical use.

## Deliverable 5 — Assembly guide

`ASSEMBLY_GUIDE.md` covers tools, PCB SMT solder order with bring-up tests,
seven harness diagrams (Display, Camera, I2C, Stepper, Power, UI, Safety),
mechanical assembly order keyed to existing STEP/STL files, first-boot
checklist with expected serial output, and a troubleshooting matrix.

## Known issues flagged for next pass

The following GPIO collisions in `firmware/urine_dipstick_analyzer/config.h`
need resolution before final firmware flash — they are documented in the
assembly guide but not auto-fixed:

- `CAM_PIN_D3 = 47` and `PIN_HEATER_GATE = 47` — same pin
- `CAM_PIN_D0 = 3`  and `BARCODE_RX = 3`     — same pin

Suggested fix: move `PIN_HEATER_GATE` to GPIO 6 (currently white LED — also
needs a remap) and `BARCODE_RX` to GPIO 17 (currently RGB_BLUE — same).
A clean re-pinning pass against an ESP32-S3 strapping-pin reference is needed.
