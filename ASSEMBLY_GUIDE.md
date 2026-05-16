# Urine Dipstick Analyzer — Assembly Guide

Prototype build guide for UDA-PROTO-001. Estimated assembly time: 4–6 hours.

---

## 1. Tools Needed

| Tool | Spec | Notes |
|---|---|---|
| Soldering iron | 60–80W temp-controlled, 0.4mm chisel tip | TS100, Pinecil, or Hakko FX-888 |
| Solder | 0.5mm Sn60Pb40 or SAC305 + flux pen | Lead-free OK with extra flux |
| Hot-air rework station | 350°C @ 25 L/min | For SOT-23 / MSOP rework only |
| Desoldering braid | 2.5mm | |
| Helping hands + magnifier | 5x or USB microscope | Required for 0603 passives |
| Tweezers | ESD-safe, fine-tip + curved | |
| Side cutters | Flush-cut | |
| Wire strippers | 22–30 AWG | |
| Multimeter | Continuity + DC voltage | |
| Bench PSU (optional) | 0–12V, current-limit 100mA | For first power-up |
| Hex keys | M2, M2.5, M3 | Ball-end preferred |
| Screwdrivers | PH0, PH1, flat 2mm | |
| Calipers | Digital, 0–150mm | |
| Heat-set insert tool | Soldering iron tip M3 | For HW3 inserts in plastic |
| Kapton tape | 10mm + 25mm rolls | Thermal isolation, masking |
| Heat-shrink tubing | 1.5mm, 3mm, 6mm | Black + assorted |
| Cable ties | 2.5mm | |
| Isopropyl alcohol | 99% + lint-free wipes | Flux cleanup, optics cleaning |

---

## 2. PCB Assembly Order (PCB1 — Power Distribution Board)

Solder the SMT components in order of decreasing thermal mass / increasing height:

1. **0603 / 0805 passives first** (R1–R2 pull-ups, C1–C8 decoupling, CB1–CB4 bulk caps).
   Use the drag-solder technique: tin one pad, place part with tweezers, reflow, then solder opposite pad.
2. **1206 components** — CB5 (100uF motor cap), F1 (PTC fuse).
3. **SOT-23-8** — U4 MAX17048 fuel gauge. Align pin 1 dot with silkscreen mark.
4. **MSOP-10** — U1 MCP73833 charger. Tack one corner pin, verify alignment under magnifier, then solder remaining pins. Drag-solder + flux + braid for any bridges.
5. **USB-C breakout (U1a)** — solder via the breakout's 16-pin header onto PCB1. Mechanically reinforce the connector edges with fillets of solder.
6. **JST-XH 2-pin headers** (5x) — through-hole, last. Label with paint pen: BAT / 9V_OUT / 3V3_OUT / I2C_BUS / MOTOR_PWR.
7. **Mounting hardware** — M2.5 brass standoffs (HW4) at the four corner holes.

**Visual inspection checklist:**
- No solder bridges between IC pins (use 10x magnification).
- All passives sit flat, no tombstoning.
- Polarity correct on CB5 (cap +), MAX17048 (pin 1 dot), MCP73833 (pin 1 dot), USB-C orientation.
- Flux residue cleaned with IPA + brush.

**Bench bring-up before connecting battery:**
1. Continuity-test VBAT → GND (must NOT short).
2. Continuity-test 3V3 → GND (must NOT short).
3. Inject 5V/100mA on USB-C VBUS pin via current-limited bench supply. Verify 4.2V max appears on BAT pad (charger output; with no battery it will float briefly, that's OK).
4. Connect a single LiPo (BT1) to the BAT JST. Confirm charger LED behavior (or scope CHRG pin).
5. Probe 9V_OUT (should read open until U2 attached) and 3V3_OUT JSTs.

---

## 3. Wire Harness Diagrams

All GPIO numbers below come from `firmware/urine_dipstick_analyzer/config.h`.
Recommend 28 AWG silicone-jacketed stranded wire for signal, 22 AWG for power. JST-XH on PCB-side, Dupont 2.54mm on module-side, with crimp ferrules at both ends (no bare-wire splices).

### HARNESS A — ESP32 ↔ Display (ILI9341 2.4" SPI)

```
+---+----------------+----------------+--------+--------+
| # | From (ESP32)   | To (TFT pin)   | Color  | Length |
+---+----------------+----------------+--------+--------+
| 1 | GPIO 40        | SCK (SCL/CLK)  | Yellow | 90mm   |
| 2 | GPIO 39        | MOSI (SDA/DIN) | Orange | 90mm   |
| 3 | GPIO 38        | MISO (SDO)     | Brown  | 90mm   |
| 4 | GPIO 15        | CS / TFT_CS    | Green  | 90mm   |
| 5 | GPIO 16        | DC / RS        | Blue   | 90mm   |
| 6 | EN (RST)       | RST            | Purple | 90mm   |
| 7 | 3V3            | VCC            | Red    | 90mm   |
| 8 | 3V3            | LED (backlight)| Pink   | 90mm   |
| 9 | GND            | GND            | Black  | 90mm   |
+---+----------------+----------------+--------+--------+
```

### HARNESS B — ESP32 ↔ Camera (OV2640 24-pin DVP)

Use a 24-conductor flat ribbon (or a pre-made FPC adapter) ≤80mm. Keep PCLK/HREF/VSYNC pairs short and impedance-matched.

```
+---+----------------+----------------+--------+--------+
| # | From (ESP32)   | To (OV2640)    | Color  | Length |
+---+----------------+----------------+--------+--------+
| 1 | GPIO 10        | XCLK           | White  | 80mm   |
| 2 | GPIO 11        | SIOD (SDA)     | Yellow | 80mm   |
| 3 | GPIO 12        | SIOC (SCL)     | Orange | 80mm   |
| 4 | GPIO 35        | VSYNC          | Brown  | 80mm   |
| 5 | GPIO 36        | HREF           | Green  | 80mm   |
| 6 | GPIO 37        | PCLK           | Blue   | 80mm   |
| 7 | GPIO 13        | D7             | Grey   | 80mm   |
| 8 | GPIO 14        | D6             | Grey   | 80mm   |
| 9 | GPIO 9         | D5             | Grey   | 80mm   |
|10 | GPIO 48        | D4             | Grey   | 80mm   |
|11 | GPIO 47        | D3             | Grey   | 80mm   |
|12 | GPIO 46        | D2             | Grey   | 80mm   |
|13 | GPIO 45        | D1             | Grey   | 80mm   |
|14 | GPIO 3         | D0             | Grey   | 80mm   |
|15 | 3V3            | 3V3 / DOVDD    | Red    | 80mm   |
|16 | 3V3            | DVDD           | Red    | 80mm   |
|17 | GND            | GND (x3)       | Black  | 80mm   |
|18 | NC             | PWDN (tie GND) | Black  | 80mm   |
|19 | NC             | RESET (tie 3V3)| Red    | 80mm   |
+---+----------------+----------------+--------+--------+
```

NOTE: GPIO collisions resolved — HEATER_GATE now on GPIO 4, BARCODE_TX on GPIO 16, BARCODE_RX on GPIO 18.

### HARNESS C — I2C Bus (shared: SHT31, BH1750, DS3231, MAX17048)

Daisy-chain modules in this order: ESP32 → SHT31 → BH1750 → DS3231 → MAX17048(on PCB1). 4.7k pull-ups (R1, R2) live on PCB1 only — do NOT add per-module pull-ups.

```
+---+----------------+-----------------------+--------+--------+
| # | From           | To                    | Color  | Length |
+---+----------------+-----------------------+--------+--------+
| 1 | ESP32 GPIO 19  | SDA bus              | Yellow | 250mm  |
| 2 | ESP32 GPIO 18  | SCL bus              | Green  | 250mm  |
| 3 | 3V3 rail       | VCC of each module   | Red    | 250mm  |
| 4 | GND rail       | GND of each module   | Black  | 250mm  |
+---+----------------+-----------------------+--------+--------+
```

I2C addresses (from `config.h`):
SHT31 = 0x44, BH1750 = 0x23, DS3231 = 0x68, MAX17048 = 0x36.

### HARNESS D — Stepper (A4988 → NEMA17)

```
+---+----------------+-------------------+--------+--------+
| # | From (ESP32)   | To (A4988)        | Color  | Length |
+---+----------------+-------------------+--------+--------+
| 1 | GPIO 4         | STEP              | Yellow | 60mm   |
| 2 | GPIO 5         | DIR               | Orange | 60mm   |
| 3 | GND            | ENABLE (tie LOW)  | Black  | 60mm   |
| 4 | 3V3            | RESET, SLEEP (tie)| Red    | 60mm   |
| 5 | 3V3            | VDD               | Red    | 60mm   |
| 6 | GND            | GND (logic)       | Black  | 60mm   |
+---+----------------+-------------------+--------+--------+
| 7 | 9V_OUT (PCB1)  | VMOT              | Red    | 100mm  |
| 8 | GND            | GND (motor)       | Black  | 100mm  |
+---+----------------+-------------------+--------+--------+
A4988 → NEMA17 (17HS08-1004S):
| 9 | A1             | Motor coil A+     | Red    | 200mm  |
|10 | A2             | Motor coil A-     | Yellow | 200mm  |
|11 | B1             | Motor coil B+     | Green  | 200mm  |
|12 | B2             | Motor coil B-     | Blue   | 200mm  |
+---+----------------+-------------------+--------+--------+
```

Set A4988 Vref to ~0.50V (≈ 0.8A peak / 0.56A RMS for the 1A coil). Microstep jumpers MS1/MS2/MS3 = HIGH/HIGH/HIGH (1/16 step) to match `MICROSTEPS=16`. Place CB5 (100uF) across VMOT/GND **at the driver**, not at the PCB.

### HARNESS E — Power Distribution

```
+---+----------------+-----------------------+--------+--------+
| # | From (PCB1)    | To                    | Color  | Length |
+---+----------------+-----------------------+--------+--------+
| 1 | BAT JST        | LiPo BT1 (3.7V)       | Red/Bk | 50mm   |
| 2 | 3V3_OUT JST    | ESP32 5V/USB pin      | Red/Bk | 60mm   |
| 3 | 3V3_OUT JST    | U3 (Pololu 3V3) IN    | Red/Bk | 60mm   |
| 4 | 9V_OUT JST     | U2 (Pololu 9V) IN     | Red/Bk | 80mm   |
| 5 | U2 OUT         | A4988 VMOT            | Red/Bk | 100mm  |
| 6 | U2 OUT         | Heater HTR1 (via Q2)  | Red/Bk | 120mm  |
| 7 | U2 OUT         | UV-C D3 (via Q3+R7)  | Red/Bk | 150mm  |
| 8 | 3V3 rail       | Fan FAN1 (via Q1)     | Red/Bk | 100mm  |
+---+----------------+-----------------------+--------+--------+
```

Strain-relieve the LiPo leads with hot glue at the PCB JST. **Never** mate/unmate the BAT JST while charger is plugged in.

### HARNESS F — UI (Buttons, Buzzer, RGB LED, White LED)

```
+---+----------------+-----------------------+--------+--------+
| # | From (ESP32)   | To                    | Color  | Length |
+---+----------------+-----------------------+--------+--------+
| 1 | GPIO 1         | SW1 tactile, other →GND| White | 80mm   |
| 2 | GPIO 43        | BZ1 buzzer +, − → GND | Yellow | 80mm   |
| 3 | GPIO 6         | D1 WS2812B DIN        | Green  | 120mm  |
| 4 | GPIO 7         | D2 RGB LED R via 330R | Red    | 60mm   |
| 5 | GPIO 8         | D2 RGB LED G via 330R | Green  | 60mm   |
| 6 | GPIO 17        | D2 RGB LED B via 330R | Blue   | 60mm   |
| 7 | 5V             | D1 VCC                | Red    | 120mm  |
| 8 | 3V3            | D2 common anode       | Red    | 60mm   |
+---+----------------+-----------------------+--------+--------+
```

D2 is common-anode → drive each cathode LOW to light. Resistors R11–R13 (330Ω) in series.

### HARNESS G — Safety (UV-C, Reed Switch, Limit Switch, Thermistor)

```
+---+----------------+--------------------------+--------+--------+
| # | From (ESP32)   | To                       | Color  | Length |
+---+----------------+--------------------------+--------+--------+
| 1 | GPIO 20        | Q3 gate (UV MOSFET)      | Purple | 100mm  |
| 2 | Q3 drain       | D3 UV-C cathode via R7   | White  | 50mm   |
| 3 | 9V_OUT         | D3 UV-C anode            | Red    | 150mm  |
| 4 | GPIO 21        | SW3 reed switch, other→3V3| Grey  | 200mm  |
| 5 | GPIO 42        | SW2 limit switch NC→GND  | Brown  | 120mm  |
| 6 | A0 (GPIO ADC)  | R_NTC + 10k divider to 3V3| Yellow| 80mm   |
+---+----------------+--------------------------+--------+--------+
```

UV-C interlock rule: firmware MUST verify `PIN_REED_SWITCH == HIGH` (lid closed) before asserting `PIN_UV_GATE`. If reed opens during a UV cycle, kill the gate within 50ms.

---

## 4. Mechanical Assembly Order

1. **Insert M3 heat-set inserts (HW3)** into the four standoff bosses of `im_enclosure_base.step` using a soldering iron at 230°C. Apply axial pressure only — do not twist.
2. **Mount PCB1** on M2.5 brass standoffs (HW4) at the rear-left quadrant of the base.
3. **Mount ESP32-S3 DevKit** on M2x6 screws (HW1) at the rear-right quadrant.
4. **Install lead screw assembly (LS1)** — lead screw bearings into the front + rear motor ribs of the base, T8 nut into the underside of `im_tray.step`. Verify the tray slides freely 0–80mm before tightening.
5. **Mount NEMA17 stepper (M1)** at the rear of the base with 4× M3x8 (HW2). Couple to lead screw via 5mm-to-8mm flex coupler.
6. **Install limit switch (SW2)** at the home (rear) end of tray travel. Adjust so plunger contacts at ≤2mm from hard stop.
7. **Mount camera + LED bracket (`camera_led_mount.step`)** above the strip channel at 45° angle. Camera (CAM1) screws via 4× M2x6 with CPL filter (CAM1a) clipped over the lens. White LED module (D1) glued to the bracket lip, wired to the rear.
8. **Mount barcode scanner (`scanner_mount.step`)** at the front of the lid, GM65 (U9) angled toward the operator's QR position.
9. **Mount UV-C LED (D3)** to the underside of the cover, centered over tray rest position. Use SMD-to-wire pigtail; do NOT use white LED in same circuit.
10. **Adhere reed switch (SW3)** body to base wall + magnet to cover, gap ≤8mm when closed.
11. **Install heater (HTR1)** on the underside of the tray with thermal adhesive, NTC thermistor (R_NTC) glued adjacent to the heater (max 5mm spacing).
12. **Mount fan (FAN1)** behind exhaust grill (`vent_grill.step`), filter side facing in.
13. **Route harnesses A–G through `internal_wire_frame.step`** — never above the optical path.
14. **Apply EPDM foam strip (GSK2)** along the cover mating surface for light-seal.
15. **Install fused quartz window (OPT2)** + flocking paper (OPT3) inside the optical chamber.
16. **Snap-fit the cover (`enclosure_cover.step`)**, secure with 4× M3x8 (HW2). Verify reed switch triggers on close.

Torque all screws to "snug + 1/8 turn" — do NOT crack the ABS bosses.

---

## 5. First Boot Checklist

With LiPo charged to ≥50% (charger LED solid green):

1. Press main button (SW1) for 1s. Expect:
   - Power LED solid green within 200ms.
   - Buzzer beep (50ms).
   - TFT splash screen "UDA-PROTO-001 booting…" within 1s.
   - Stepper homing: tray moves rearward until limit switch trips, then advances 5mm. Audible 1 click/step at homing speed.

2. Serial monitor (115200, USB-CDC) should show:
   ```
   [BOOT] ESP32-S3 PSRAM=8192KB Flash=8MB
   [I2C] Scan: 0x23 (BH1750) 0x36 (MAX17048) 0x44 (SHT31) 0x68 (DS3231)
   [CAM] OV2640 init OK, fb=320x240 RGB565
   [SD] Card mounted, FAT32, free=XX MB
   [RTC] 2026-05-16 09:21:00
   [BATT] 3.92V  78%
   [DISP] ILI9341 init OK
   [HOME] Tray homed at step 0
   [READY]
   ```

3. On TFT, the home screen should show: battery %, time, last test result placeholder, and "INSERT STRIP" prompt.

4. Trigger a self-test from the menu: it should sequentially flash white LED, blink RGB through R/G/B, pulse buzzer, run UV for 1s (only with cover closed!), and do a 10mm tray jog forward + back.

If any I2C device is missing from the scan, see Troubleshooting.

---

## 6. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| TFT stays black, backlight on | TFT_DC swapped with TFT_CS, or SPI clock too fast | Check Harness A pin 4/5 wiring; reduce SPI to 20MHz in `display.h` |
| TFT stays black, backlight off | LED pin floating or 3V3 missing on TFT board | Verify Harness A pin 8 + pin 7 |
| `[I2C] Scan: (none)` | Missing or wrong pull-ups, SDA/SCL swapped | Confirm R1/R2 4.7k installed on PCB1; check Harness C wiring |
| Only some I2C devices found | Address conflict, bad solder joint on a module | Disconnect modules one by one to isolate; reflow VCC/GND on suspect |
| `[CAM] init failed` | DVP wiring, GPIO47 conflict with heater, missing PSRAM | Check Harness B; verify `BOARD_HAS_PSRAM` build flag; ensure heater FET disconnected during cam init |
| Tray doesn't home | Limit switch wired NC vs NO, or A4988 ENABLE high | Verify SW2 pulls GPIO 42 LOW when pressed; check A4988 ENABLE tied to GND |
| Stepper buzzes but doesn't turn | Coil pairs miswired (A1/A2 vs B1/B2), Vref too low | Re-pair coils with multimeter (low-resistance pair = one coil); raise Vref toward 0.55V |
| UV-C never fires | Reed switch reads "lid open" | Adjust magnet gap ≤8mm; swap to a NO reed if always-LOW |
| UV-C fires with lid open | Reed switch wired NO→NC inverted | Re-wire SW3 or invert logic in `safety.h` |
| Heater hits OVERTEMP_C immediately | NTC thermistor disconnected (reads -999) or shorted | Check Harness G pin 6; resistance NTC at 25°C should be 10kΩ ±5% |
| Boot loops, brownout reset | LiPo too low, or charger not delivering | Charge 30+ min; measure VBAT under load > 3.4V |
| SD card fails to mount | Wrong SPI bus (TFT and SD share SPI here), CS conflict | Confirm only TFT_CS or SD_CS asserted at any time; format SD as FAT32 |
| Barcode scanner silent | Check UART1 wiring on GPIO 16 (TX) / 18 (RX); confirm 9600 baud | Verify GM65 power LED is on; swap TX/RX if scanner doesn't respond |

---

## 7. Skipped / Deferred Items in This Build

See `BUILD_REPORT_v2.md` for what was generated programmatically vs. what still requires manual KiCad work (PCB routing, gerber export status). The pin collisions noted in Harness B (GPIO 47, GPIO 3) are documented for resolution before any production tooling.
