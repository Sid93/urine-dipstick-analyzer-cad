# Urine Dipstick Analyzer

> Open-source urine dipstick analyzer using ESP32-S3 + computer vision.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Last Commit](https://img.shields.io/github/last-commit/Sid93/urine-dipstick-analyzer-cad)](https://github.com/Sid93/urine-dipstick-analyzer-cad/commits/main)
[![GitHub Stars](https://img.shields.io/github/stars/Sid93/urine-dipstick-analyzer-cad?style=social)](https://github.com/Sid93/urine-dipstick-analyzer-cad/stargazers)
[![Hardware: ESP32-S3](https://img.shields.io/badge/Hardware-ESP32--S3-blue)](https://www.espressif.com/en/products/socs/esp32-s3)
[![Status: Prototype](https://img.shields.io/badge/Status-Prototype-orange)](#project-status)

## What it does

A self-contained device that reads off-the-shelf 10-parameter urine dipsticks
(glucose, ketones, bilirubin, blood, pH, protein, urobilinogen, nitrite,
leukocytes, specific gravity) using a calibrated colorimetric pipeline. A
white + UV LED ring illuminates the strip, an OV2640 camera captures the
reaction pads, and an ESP32-S3 runs per-pad ROI analysis against a factory
calibration set anchored to an X-Rite ColorChecker Nano. Results are shown
on a 2.4" ILI9341 display, logged to SD, and optionally streamed over Wi-Fi.
Total BOM is approximately USD 330 in single-unit quantities.

## Photos and drawings

Mechanical drawings (PDF) for every printed/machined part live in
[`drawings/`](drawings/). 3D models in STEP and STL are in the project root
(`im_enclosure_base.*`, `enclosure_cover.*`, `camera_led_mount.*`,
`scanner_mount.*`, `vent_grill.*`, `im_tray.*`, `internal_wire_frame.*`).
Schematic render: [`schematic_render.png`](schematic_render.png).

## Hardware overview

| Subsystem | Part | Notes |
|---|---|---|
| MCU | ESP32-S3-DevKitC-1-N8R8 | 8 MB flash, 8 MB OPI PSRAM, dual-core |
| Camera | OV2640 (DVP) | hardware DVP on ESP32-S3 |
| Display | 2.4" ILI9341 SPI TFT | 320 x 240, Adafruit_ILI9341 driver |
| Illumination | White + 365 nm UV LEDs | constant-current via PMOS |
| Strip transport | NEMA-8 stepper + A4988 | AccelStepper-driven |
| Environment | SHT31 (T/RH), BH1750 (lux), DS3231 (RTC) | I2C bus |
| Power | Single 18650 + MCP73833 charger + MAX17048 fuel gauge | 3.7 V Li-ion |
| Enclosure | FDM PETG, M2.5 fasteners | STEP files in repo root |
| BOM cost | ~USD 330 | single-unit, see `BOM.csv` |

## Repository structure

```
.
├── README.md                      this file
├── LICENSE                        MIT
├── ASSEMBLY_GUIDE.md              SMT solder order, harnesses, mech build
├── BUILD_REPORT.md / _v2.md       generation pass logs
├── BOM.csv / BOM.pdf              bill of materials with MPNs
├── calibration.json               factory calibration (10 pads, 24-patch ref)
├── urine_dipstick_analyzer.*      KiCad project (sch + pcb + pro)
├── schematic_render.png           SVG-rendered schematic preview
├── generate_*.py                  reproducible build scripts (sch/pcb/cad/bom/drawings)
├── route_pcb.py                   programmatic auto-router for PCB1
├── drawings/                      mechanical PDFs
├── gerbers/                       fab-ready gerbers + drill (PCB1)
├── gerbers.zip                    zipped fab package
├── firmware/urine_dipstick_analyzer/   PlatformIO project + .ino + .h modules
├── *.step / *.stl                 mechanical 3D models (7 parts)
```

## Quick start

```bash
# 1. Clone
git clone https://github.com/Sid93/urine-dipstick-analyzer-cad.git
cd urine-dipstick-analyzer-cad

# 2. Install PlatformIO
pip3 install --user platformio

# 3. Build and flash the ESP32-S3
cd firmware/urine_dipstick_analyzer
pio run -t upload
pio device monitor
```

## Build the prototype

Full step-by-step build instructions live in two documents:

- [`BUILD_REPORT.md`](BUILD_REPORT.md) — design rationale, optical/colorimetric
  pipeline, per-subsystem reasoning.
- [`ASSEMBLY_GUIDE.md`](ASSEMBLY_GUIDE.md) — SMT solder order with bring-up
  tests, harness diagrams, mechanical assembly order, first-boot checklist,
  troubleshooting matrix.

## Project status

What works:

- Schematic and BOM are complete with manufacturer part numbers.
- PCB1 (power-distribution hub) is laid out, programmatically routed, and
  fab-ready gerbers are in `gerbers/`.
- Firmware compiles for ESP32-S3 (PlatformIO project, modular `.h` headers).
- Mechanical CAD is complete (STEP + STL for all 7 parts) with PDF drawings.
- Calibration JSON includes a full 24-patch ColorChecker reference and
  per-pad polynomial coefficients.

What is incomplete or known-issue:

- The PCB router is a simple Manhattan-MST router with naive crossing
  detection — it produces a manufacturable layout but not an optimized one.
  Recommend a manual review pass in KiCad and DRC run before fabricating.
- A few GPIO collisions in `firmware/urine_dipstick_analyzer/config.h` were
  flagged in v2 build report; some are now fixed in commit c849104 but a
  full strapping-pin audit is still recommended.
- Calibration values are realistic placeholders. The in-firmware
  `/calibrate` routine MUST be re-run with a real ColorChecker Nano under
  integrated illumination before any meaningful measurement.
- No clinical validation has been performed.

## Regulatory disclaimer

**This device is for research and educational use only. It is NOT a medical
device. It has not been evaluated or cleared by the U.S. FDA, the European
CE/IVDR process, or India's CDSCO.** In India, any in-vitro diagnostic
device intended for sale or clinical use requires CDSCO approval under the
Medical Devices Rules, 2017. Equivalent regulation applies in every other
jurisdiction. Do not use the output of this device to make clinical or
treatment decisions for yourself or anyone else. The authors and
contributors accept no liability for any use of this hardware or software.

## License

This project is licensed under the [MIT License](LICENSE).

## Citation

If you use this work in academic publications, please cite:

```bibtex
@misc{saboo2026urinedipstick,
  author       = {Saboo, Siddhant},
  title        = {Open-source Urine Dipstick Analyzer (ESP32-S3 + Computer Vision)},
  year         = {2026},
  howpublished = {\url{https://github.com/Sid93/urine-dipstick-analyzer-cad}},
  note         = {Research prototype, not a medical device}
}
```

## Acknowledgments

Built with the open-source ecosystem: KiCad 10, PlatformIO, the Espressif
Arduino core, Adafruit's GFX/ILI9341/BusIO/SHT31 libraries, Mike McCauley's
AccelStepper, Christopher Laws's BH1750 driver, Benoit Blanchon's
ArduinoJson, the X-Rite ColorChecker reference data, and Anthropic's
Claude for the agentic generation passes that produced the CAD, schematic,
PCB, gerbers, BOM, drawings, firmware scaffolding, and assembly guide.
