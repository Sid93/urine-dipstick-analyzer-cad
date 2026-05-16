# Prototype Status & Known Issues

Last updated: 2026-05-16. Auto-generated from `kicad-cli drc/erc` + `pio run`.

## ✅ Working

| Asset | Status | Notes |
|---|---|---|
| BOM (`BOM.csv`, `BOM.pdf`) | ✅ Complete | 111 parts, $330, real MPNs |
| Mechanical CAD (`*.step`, `*.stl`) | ✅ Complete | Enclosure, tray, brackets, mounts |
| 2D drawings (`drawings/*.pdf`) | ✅ Complete | 7 dimensioned drawings |
| Firmware build (`platformio.ini`) | ✅ Compiles | RAM 8.1%, Flash 14.2% on ESP32-S3 |
| Calibration data (`calibration.json`) | ✅ Schema valid | Placeholder values — needs real capture |
| README + LICENSE | ✅ Complete | MIT licensed |
| Assembly guide | ✅ Complete | Tools, harnesses, troubleshooting |
| GPIO assignments | ✅ Clean | 27 unique pins, no collisions |

## ⚠️ Needs human attention

### Schematic (`urine_dipstick_analyzer.kicad_sch`)
- **252 ERC violations** — primarily unconnected pins on passives (R6, R7, R11–R14, D1–D3) and dangling labels (`RGB_R`, `RGB_G`, `RGB_B`, `VBAT`)
- **Root cause:** the auto-generator places components but doesn't always wire both terminals
- **Fix:** open in KiCad eeschema and manually wire the dangling pins, or patch `generate_schematic.py` to ensure every passive has both terminals connected to a net label or wire stub

### PCB (`urine_dipstick_analyzer.kicad_pcb`)
- **75 DRC violations** even after stripping bad routes:
  - 27× `lib_footprint_mismatch` — programmatically inserted footprints don't match standard KiCad library
  - 14× `solder_mask_bridge` — pads too close for mask separation
  - 8× `shorting_items` — leftover from imperfect autoroute strip
  - 7× `clearance` — copper traces too close
- **51 unrouted nets** — expected; needs manual routing in KiCad
- **Recommendation:** Treat the current `.kicad_pcb` as a starting placement only. In KiCad PCB Editor:
  1. Update footprints from library (`Tools → Update Footprints from Library`)
  2. Run `Tools → Cleanup Tracks & Vias`
  3. Reroute by hand (`X` shortcut for single track) — only ~30 nets, ~30 minutes for someone fluent
  4. Add ground pour on both layers
  5. Re-run DRC until clean
  6. Re-export gerbers

### Gerbers (`gerbers.zip`)
- ⚠️ **Not yet manufacturable** — derived from the unrouted PCB above. Do not send to fab until DRC is clean.

## ❌ Not started

- **Calibration capture procedure** — `calibration.json` has placeholder coefficients. A one-time `calibrate` mode in firmware that shows the ColorChecker card, captures patch RGBs, and writes real per-device data hasn't been written.
- **Validation/test protocol** — no documented pass/fail criteria for camera SNR, LED intensity stability, stepper repeatability, heater PID overshoot, or end-to-end pad-reading accuracy.
- **Power budget** — current draw per phase (idle/scan/heat/UV) not measured; battery life estimate is missing.
- **CDSCO regulatory dossier** — required before sale in India as a Class B medical device under MDR 2017. Includes ISO 14971 risk analysis, IEC 62304 software lifecycle, IFU, clinical data.

## Build artifacts

Run from project root:
```
# Schematic ERC
kicad-cli sch erc --output erc_report.txt urine_dipstick_analyzer.kicad_sch

# PCB DRC
kicad-cli pcb drc --output drc_report.txt urine_dipstick_analyzer.kicad_pcb

# Firmware build (requires PATH=$HOME/Library/Python/3.13/bin and pip3 install --user intelhex)
cd firmware/urine_dipstick_analyzer && pio run

# Gerbers (only after PCB DRC is clean!)
kicad-cli pcb export gerbers --output gerbers/ urine_dipstick_analyzer.kicad_pcb
kicad-cli pcb export drill --output gerbers/ urine_dipstick_analyzer.kicad_pcb
cd gerbers && zip -r ../gerbers.zip *
```
