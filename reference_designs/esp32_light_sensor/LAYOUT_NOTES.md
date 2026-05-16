# PCB Layout Notes

Concrete layout directives, keyed to the schematic reference designators.

## Board Constraints

- **Dimensions:** 40 mm x 40 mm, rounded corners 2 mm radius.
- **Stackup:** 2-layer FR4, 1.6 mm thick, 1 oz outer copper. JLCPCB default
  green soldermask, white silkscreen.
- **Design rules:**
  - Minimum trace width: 5 mil (0.127 mm)
  - Minimum clearance: 5 mil (0.127 mm)
  - Minimum drill: 0.25 mm (annular ring 0.15 mm)
  - Min via: 0.6 mm pad / 0.3 mm drill (signal stitching)
  - Min via: 0.8 mm pad / 0.4 mm drill (thermal)

## Antenna Keepout (Critical)

A **15 mm x 25 mm rectangular cut-out** must extend past the WROOM-32E
antenna at the board edge:

```
   |<---- 15 mm ---->|
   +-----------------+ ---
   | NO COPPER       |  ^
   | NO TRACES       |  |
   | NO GND FILL     | 25 mm
   | NO SILKSCREEN   |  |
   | (cut out from   |  v
   |  board outline) | ---
   +-----------------+
   |                 |
   |   WROOM-32E     |
   |   module pads   |
```

Both the top and bottom layers must be cleared in this region. The cleanest
implementation is to recess the board outline so this area is empty PCB
space (i.e. notch the corner of the board). If the board outline must remain
rectangular, leave the copper void and add a "no fill" zone in KiCad.

## Component Placement (top-down sweep)

1. **J1 (USB-C)** at the south edge of the board, centred. The CC1/CC2
   pull-downs (R1, R2) and the USB shell screws within 3 mm.

2. **U1 (USBLC6-2SC6)** within **5 mm** of J1's D+/D- pins. Its GND pin
   (pin 2) drops straight into the bottom GND plane through one via
   directly under the pad (no GND trace).

3. **F1 (polyfuse)** in the VBUS path, between USBLC6 and the rest of the
   board. Place ~5 mm from J1.

4. **D1 (TVS)** parallel to VBUS_FUSED right after F1. Cathode via to bottom
   GND, again directly under the pad.

5. **Q1 (AO3401A)** P-MOSFET reverse polarity. Source on VBUS_FUSED side,
   drain on the protected rail (VBUS_PROT). R3 (10k gate pull-up) within
   3 mm.

6. **U2 (AMS1117-3.3)** central in the south half of the board.
   - **Cin (C2 10 uF, C3 100 nF):** within 2 mm of VIN pin (pin 3).
   - **Cout (C4 22 uF, C5 100 nF):** within 2 mm of VOUT pin (pin 2).
   - **Thermal pad** (pin 2 tab): 9 stitching vias (3x3 array, 0.4 mm drill,
     0.8 mm pad) to a bottom-layer copper pour at least 100 mm^2.

7. **FB1 (ferrite bead)** in the trace between LDO output and the ESP32
   3V3 net. Orient perpendicular to the supply trace; do not run other
   signals under it.

8. **C6 (1 uF), C7 (100 nF), C8 (10 nF)** on the clean side of FB1, all
   within 5 mm of FB1's load-side pad.

9. **U3 (ESP32-WROOM-32E)** in the centre-north half of the board with the
   antenna corner facing the antenna keepout (north edge).
   - **C9 (100 nF):** within 2 mm of pin 2 (3V3).
   - **C10 (1 uF):** within 5 mm of pin 2.
   - GND pins (1, 15, 38) each get their own via to the bottom plane.

10. **R5 (10k pullup) + C11 (100 nF) + SW1 (RESET button)** within 10 mm
    of EN pin (pin 3). Keep the EN trace short and away from switching nets.

11. **R6 (10k IO0 pullup) + SW2 (BOOT button)** within 10 mm of IO0
    (pin 25).

12. **R7 (10k IO2 pulldown), R8 (10k IO15 pullup)** as close to their
    respective ESP32 pins as routing allows.

13. **J2 (UART header)** at the east edge of the board for easy probe
    access. Route TXD0 (pin 35) and RXD0 (pin 34) as parallel pair under
    the ESP32 ground (return current on the bottom plane).

14. **U4 (BH1750)** at least **30 mm** from both U3 (RF emitter) and J1
    (ESD ingress). Place on the north edge of the board with an unobstructed
    view of the light source. If the board is going in an enclosure with a
    light pipe, align with the pipe.
    - **C12 (100 nF), C13 (1 uF):** within 2 mm of VCC pin.
    - Local GND pour under the sensor, stitched to the main plane with 4
      vias near the corners.

15. **R9, R10 (I2C pull-ups)** near the ESP32 end of the I2C bus, not at
    the sensor end. The pull-up loop area should be small.

16. **R11/C14, R12/C15 (DNP RC filters)** placed but unpopulated. Keep the
    footprints accessible for hand-population during EMC debug.

## Routing Guidance

- **Power traces:** VBUS_PROT and 3V3 at 0.5 mm (20 mil) minimum. AMS1117
  output trace 1.0 mm if running >2 cm.
- **USB D+/D-:** 90 Ohm differential pair, 12 mil trace, 7 mil gap,
  length-matched to 1 mm. Total length <50 mm. No vias if possible.
- **I2C:** 8 mil traces. SDA and SCL routed parallel, similar length, with
  the bottom-layer ground plane directly underneath. Total length under
  20 cm (well within 400 kHz capacitance budget).
- **UART:** 8 mil traces, no special impedance, but keep TXD0/RXD0 away
  from D+/D- and the antenna keepout.
- **No traces under the WROOM antenna footprint or in the keepout zone.**
- **No GND fill in the keepout zone** (top or bottom).
- **No silkscreen** in the keepout zone.
- **Edge stitching:** GND vias every 5 mm along the board edge (except in
  the antenna keepout) to suppress edge radiation.

## Silkscreen

- Component reference designators next to each part, 1 mm text, top side only.
- Pin 1 markers on U1, U2, U3, U4 (small triangle).
- Polarity marker on C2, C4 (electrolytics in BOM upgrade path).
- USB-C orientation indicator (top side, near J1).
- BOOT and RESET labels next to SW1, SW2.
- Project name and rev in the south-east corner: "ESP32+BH1750 Ref Rev 1.0".

## Manufacturing Notes

- Solder mask expansion: default 0.05 mm.
- Paste mask: 100% of pad area for 0603 and larger; 80% for QFN or SOT-23-6
  to reduce solder ball risk.
- Acceptance: IPC-A-610 Class 2 sufficient for a reference/dev board.
  Class 3 for any deployed-in-field unit.
- Panel: single-up acceptable for prototype; v-score in 5x4 panel for
  production of 100+ boards.
