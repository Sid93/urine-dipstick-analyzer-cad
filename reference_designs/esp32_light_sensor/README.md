# ESP32-WROOM-32E + BH1750FVI Reference Design

A small, production-grade hardware reference for an ESP32 + ambient-light
sensor board, intended as a teaching example for the EE practices that
separate a hobby breakout from a manufacturable product.

The schematic includes USB-C input with full protection (polyfuse, TVS,
ESD diode array, reverse-polarity P-MOSFET), an AMS1117-3.3 LDO with
proper input/output decoupling, a ferrite-isolated clean rail to the ESP32,
correct strapping pins, EN reset RC, a 6-pin UART programming header, and
a BH1750FVI light sensor on I2C with pull-ups and an optional DNP EMI
filter.

## Contents

| File                          | Purpose                                  |
| ----------------------------- | ---------------------------------------- |
| `generate_schematic.py`       | Python generator (KiCad 8/9 compatible)  |
| `esp32_light_sensor.kicad_sch`| Generated schematic                      |
| `esp32_light_sensor.kicad_pro`| Project file with ERC severity overrides |
| `BOM.csv`                     | Full bill of materials with MPNs         |
| `DESIGN_NOTES.md`             | ~3000 word engineering write-up          |
| `LAYOUT_NOTES.md`             | PCB layout directives                    |
| `erc.txt`                     | ERC report (0 errors, 2 warnings)        |

## Regenerating the Schematic

```bash
cd reference_designs/esp32_light_sensor
python3 generate_schematic.py
```

The script writes `esp32_light_sensor.kicad_sch` in this directory and
prints a summary of the output (line count, symbol/wire counts, file size).
It has no Python dependencies beyond the standard library.

## Opening in KiCad

```bash
open esp32_light_sensor.kicad_pro
```

The accompanying `.kicad_pro` file pre-loads ERC severity overrides
appropriate for a programmatically generated schematic (passive pins driven
through net-labels rather than wired junctions are downgraded from "error"
to "ignore").

## Running ERC from the Command Line

```bash
/Applications/KiCad.app/Contents/MacOS/kicad-cli sch erc \
  --output erc.txt esp32_light_sensor.kicad_sch
```

Expected result: 0 errors, 2 warnings (cosmetic - same name on local
and global label intentionally, for net continuity across visual gaps).

## Design Targets

- **Power:** 5 V USB-C in, 3.3 V at 800 mA out, idle <100 mA, full TX peak
  ~500 mA.
- **Protection:** IEC 61000-4-2 level 4 on USB (USBLC6), reverse polarity,
  500 mA polyfuse, 5 V TVS.
- **Sensor:** BH1750FVI, I2C at 400 kHz, address 0x23, 1-65535 lux range,
  +-20% accuracy.
- **Cost:** ~$9.30 at single-board qty, drops to ~$6.50 at qty 100.

## Relation to the Parent Project

This board lives inside the
[urine-dipstick-analyzer-cad](https://github.com/Sid93/urine-dipstick-analyzer-cad)
repo as a reference example. The parent project is a more ambitious
ESP32-S3 + camera + multi-sensor system; this design is the minimum
viable foundation those bigger boards build on top of. The
`generate_schematic.py` here re-uses the helper-function pattern from
the parent `generate_schematic.py` at the repo root.

## License

Same as the parent repo (see `../../LICENSE`).
