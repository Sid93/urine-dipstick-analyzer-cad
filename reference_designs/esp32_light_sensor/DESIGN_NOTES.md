# ESP32-WROOM-32E + BH1750FVI Reference Design - Engineering Notes

## 1. System Overview

This board is a minimal but production-grade USB-C powered Wi-Fi/Bluetooth
ambient-light sensor. It pairs an ESP32-WROOM-32E module with a Rohm
BH1750FVI 16-bit lux sensor over I2C, and is intended as a teaching reference
for what a "real" ESP32 board needs beyond the typical Aliexpress dev kit.

### Block diagram (ASCII)

```
       +-----------+
       |  USB-C    |
       |  J1       |
       +--+--+--+--+
          |  |  |
   VBUS  D+ D-  CC1/CC2 (5.1k pull-downs - UFP detection)
    |    |   |
    v    v   v
  +-----+ +--------+
  | F1  | | U1     |  USBLC6-2SC6 (low-cap ESD on D+/D-/VBUS)
  | PTC | | ESD    |
  +--+--+ +---+----+
     |        |
     v        v
   +---+    (D+/D- to MCU, not used in this design)
   | D1|    TVS 5V bidir
   +-+-+
     |
     v
   +-----+
   | Q1  |   AO3401A P-MOS reverse polarity protection
   | PMOS|
   +--+--+
      |  VBUS_PROT
      v
   +-----+      +-----+      +------------+
   | U2  +----->| FB1 +----->| ESP32      |
   | LDO |3V3   |120R |3V3   | WROOM-32E  |
   +-----+      +-----+      +------+-----+
                                    | I2C
                                    v
                              +-----------+
                              | U4 BH1750 |
                              +-----------+
```

### Power tree

```
USB-C VBUS 5.0V (nominal, 4.4-5.25 valid per USB 2.0)
   |
   +-> Polyfuse F1 (500 mA hold / 1 A trip)
   |
   +-> TVS D1 (clamp 6.4V max, 400W peak)
   |
   +-> USBLC6 U1 (D+/D-/VBUS ESD)
   |
   +-> P-MOSFET Q1 (reverse polarity)
   |
   v
VBUS_PROT 5.0V (drop ~ I * Rds(on) = 0.5A * 60mOhm = 30 mV)
   |
   +-> Power LED (D2) via R4 1k -> GND
   |
   +-> AMS1117-3.3 (U2) Vin
            |
            +-> Cin: 10uF + 100nF
            +-> Cout: 22uF + 100nF
            v
       3V3_LDO 3.3V +- 1.5% (line + load + temp)
            |
            +-> Ferrite bead FB1 (BLM18PG121SN1D, 120 Ohm @ 100 MHz, 2 A, 50 mOhm DC)
                  |
                  +-> 1uF + 100nF + 10nF clean rail caps
                  v
              3V3 (to ESP32 VDD33 and BH1750)
```

### Interface inventory

| Net          | Pins             | Purpose                              |
| ------------ | ---------------- | ------------------------------------ |
| 3V3          | ESP32 pin 2, BH1750 VCC/DVI | Clean supply rail            |
| I2C_SDA      | ESP32 IO21, BH1750 SDA      | I2C data                     |
| I2C_SCL      | ESP32 IO22, BH1750 SCL      | I2C clock                    |
| UART_TXD     | ESP32 TXD0 (35) -> J2 RXD   | Programming + console        |
| UART_RXD     | ESP32 RXD0 (34) -> J2 TXD   | Programming                  |
| EN_NET       | ESP32 EN (3), SW1, R5, C11  | Reset control                |
| IO0_BOOT     | ESP32 IO0 (25), SW2, R6     | Boot mode selection          |

## 2. Power Architecture

### Why AMS1117-3.3

The ESP32-WROOM-32E peaks at ~500 mA during Wi-Fi TX with all RF chains
active. Idle is roughly 30-60 mA. The BH1750 typical IDD is 120 uA (active)
and 1 uA (power-down), negligible.

Total worst-case load: ~600 mA with margin. The AMS1117-3.3 is rated for
800 mA continuous with adequate thermal copper. Its dropout is **1.1 V at
800 mA**, so with USB VBUS at 5.0 V (worst case 4.4 V after cable+connector
drop), the regulator sees Vin = 4.4 V, Vout = 3.3 V, headroom = 1.1 V, which
is right at the dropout boundary. For tighter regulation, an LP5907MFX-3.3
(150 mA, ultra-low noise) could replace it for the analog/RF rail and the
ESP32 could be fed from a buck regulator like the MP2315GJ. For this
reference design the AMS1117 is intentional because it is the canonical
"hobby vs production" delineator and demonstrates correct decoupling.

Power dissipation at 500 mA average: P = (5.0 - 3.3) V * 0.5 A = 0.85 W,
which is at the edge of what a SOT-223 with a 1 sq in copper pour can
dissipate (theta_JA ~ 60 C/W -> 50 C rise). A 4-layer board with a copper
flood on the underside is recommended above 400 mA continuous.

### Capacitor selection by location

The basic rule: **every IC supply pin gets at least one local 100 nF X7R
ceramic, plus bulk capacitance shared by the rail.** The split is by
impedance vs frequency:

- **10 uF / 22 uF** (X5R or X7R, 0805 or larger): bulk reservoir, handles
  load transients up to ~100 kHz and serves as Cout for the LDO. The
  AMS1117 datasheet requires a minimum 22 uF tantalum or low-ESR ceramic
  on the output to be stable; we use 22 uF X5R ceramic. C4 in the schematic.
- **4.7 uF** (X5R, 0603): VBUS bulk on the protected rail. Smooths the
  P-MOSFET turn-on transient and supplies the LED current.
- **1 uF** (X5R, 0603): mid-band bypass. Sits between bulk and ceramic on
  the clean 3V3 rail and at the ESP32 module pin.
- **100 nF** (X7R, 0603): high-frequency bypass. Placed within 2 mm of every
  IC supply pin to short the loop inductance to the ground plane at MHz.
- **10 nF** (X7R, 0603): RF bypass on the ferrite-bead clean rail. Resonates
  with the bead at ~10 MHz and helps with WiFi 2.4 GHz spurious.

Total per ESP32 module: 10 uF (bulk on LDO output) + 1 uF + 100 nF + 10 nF
(after ferrite) + 1 uF + 100 nF (at module pin 2). This matches the
Espressif Hardware Design Guidelines recommendation.

### Ferrite bead rationale

The ESP32-WROOM-32E pulls switching current at the 2.4 GHz carrier frequency
during TX. Without isolation, this couples back through the shared supply
trace and contaminates other rails (and the LDO feedback loop). A 120 Ohm
@ 100 MHz ferrite bead with ~50 mOhm DC resistance presents <30 mV DC drop
at 500 mA but ~120 Ohm impedance to the noise. Combined with the local
100 nF + 1 uF caps it forms a low-pass with corner ~150 kHz and >40 dB
attenuation at 100 MHz.

The bead must be on the **supply line, NOT the data line.** A bead on SDA
or D+ destroys edge rates and breaks I2C/USB timing.

### Expected supply noise budget

- LDO PSRR: 60 dB at 100 Hz, 40 dB at 100 kHz (AMS1117 typical)
- Output ripple: <15 mVpp at 500 mA load (with 22 uF Cout)
- After ferrite + bypass: <5 mVpp on 3V3
- ADC effective resolution given 5 mVpp / 3.3 V * 4096 = ~6 LSB of noise on
  a 12-bit ESP32 ADC. For sub-LSB performance a separate reference is needed.

## 3. ESP32 Boot Configuration

The ESP32-WROOM-32E samples six strapping pins on the rising edge of CHIP_PU
(EN). Wrong levels send the chip into download mode, the wrong flash voltage,
or a stuck boot loop.

| Pin    | Function                            | Required State | Resistor   |
| ------ | ----------------------------------- | -------------- | ---------- |
| GPIO0  | Boot mode (low = download, high = run) | High (run)  | 10k PU + button to GND |
| GPIO2  | Boot mode aux (must be low or floating during normal boot) | Low | 10k PD |
| GPIO5  | Timing of SDIO slave (not used) | High (default)  | Internal PU OK |
| GPIO12 | MTDI / Flash voltage select        | Low (3.3 V flash) | Internal PD - DO NOT pull up |
| GPIO15 | Debug log enable (low = print) / SDIO slave | High (silent) | 10k PU |
| MTDI   | Same as GPIO12                     | Low            | Default     |

**GPIO12 is the dangerous one.** If you pull it high externally, the chip
configures its internal flash regulator for 1.8 V output. The WROOM-32E
internal flash is 3.3 V, so a high GPIO12 at boot corrupts the flash voltage
and the module bricks until you reflash eFuse settings. Always leave GPIO12
floating or pulled DOWN, and never wire a status LED to it.

Boot mode summary (the only two we use):

| GPIO0 | GPIO2 | Mode         |
| ----- | ----- | ------------ |
| 1     | x     | SPI flash boot (normal run) |
| 0     | 0     | UART download (programming) |

The auto-reset circuit on USB-UART bridges (CP2102, FT232) typically
pulses DTR and RTS to force GPIO0 low and EN low simultaneously. Our 6-pin
header brings both EN and IO0_BOOT out, so any external bridge or ESP-Prog
adapter can do this in software (via esptool's `--before default_reset`).

## 4. EN / Reset Circuit

EN is an active-high enable. When low, the chip is in deep reset and draws
~5 uA. We need three things on this pin:

1. Default high during run.
2. Manual reset via SW1 (pull EN to GND).
3. Power-on delay so VDD33 stabilises before the chip wakes.

The standard topology is a 10k pull-up to 3V3 + 100 nF cap to GND, giving
**tau = R * C = 10k * 100n = 1 ms** time constant. The cap also rejects
brownout retriggering: if VBUS dips below 4.0 V for <500 us, the cap holds
EN above the 2.5 V threshold (the EN pin is a CMOS Schmitt input,
VIH = 0.75 * VDD = 2.475 V) and the chip stays alive.

For harsher environments (motor noise, hot-plug events) add a TPS3839K33
supervisor: it asserts a reset until VDD33 has been stable above 3.0 V for
200 ms. Wire its open-drain RESET output to EN_NET in parallel with the
existing RC. This is a populated-on-demand option, not in the base BOM.

## 5. I2C Design

### Pull-up sizing

The BH1750 SDA is an open-drain output with **Iol max = 3 mA at Vol = 0.4 V**.
Pulling the line to 3.3 V through 4.7 kOhm sinks 3.3 V / 4.7k = **702 uA**,
well within the 3 mA budget with margin for the ESP32 also sinking.

Rise time at 400 kHz Fast-mode I2C is limited to 300 ns (per the I2C spec).
With a 4.7 kOhm pull-up and a typical bus capacitance of 50 pF on a 5 cm
trace, tau = R * C = 4.7k * 50 pF = 235 ns, and 0-to-70%-Vdd rise time =
1.2 * tau = 280 ns. We are just inside spec for 400 kHz.

For 1 MHz (Fast-mode Plus) you need lower R: 2.2 kOhm gives Iol = 1.5 mA
(still within spec) and a 110 ns rise time on the same bus. Above ~100 pF
of bus capacitance, an active termination IC (PCA9517) is needed.

### Capacitive load budget

I2C spec: 400 pF max for standard 100 kHz, 200 pF max for 400 kHz.
Per-IC contribution: 10 pF typical for a sensor input. Per-cm of FR4 trace:
~0.5-1.0 pF/cm with adjacent ground. For a 10 cm trace + BH1750 + ESP32 =
~30 pF, comfortably under 200 pF.

### Series RC EMI filter

R11/C14 and R12/C15 form a 100 Ohm series resistor + 10 nF shunt cap on
each line. The pole is at f = 1/(2*pi*R*C) = 1/(2*pi*100*10n) = **160 kHz**,
which severely attenuates 400 kHz I2C. These are **DNP (Do Not Populate)
by default** and only useful in environments with high radiated EMI where
the I2C bus runs at 100 kHz. If populated, the resistor wraps over the cap
position - never short the cap pads.

## 6. ESD and Protection Topology

USB ports are the primary ESD ingress on any board, so they get the most
attention.

- **USBLC6-2SC6** clamps D+/D- (low capacitance, 1.5 pF, so it does not
  degrade USB2.0 eye) and VBUS (higher capacitance allowed) to GND through
  a back-to-back diode array. IEC 61000-4-2 level 4: +-8 kV contact / +-15 kV air.
- **SMAJ5.0CA** bidirectional TVS on VBUS. Standoff 5 V, clamp 9.2 V at
  peak current, 400 W. Catches power-line surges (lightning-induced or
  inductive kickback from cables).
- **Polyfuse MF-MSMF050-2**: holds 0.5 A, trips at 1 A within 0.1 s. Protects
  against downstream short (e.g. someone shorts VBUS_PROT to GND). PTC
  resistance after one trip is ~5x initial, so the part is good for one
  rescue event before replacement.
- **Reverse polarity P-MOSFET (AO3401A)**: source on VBUS_FUSED, drain on
  VBUS_PROT, gate to GND through 10k. With correct polarity, Vgs =
  -VBUS_FUSED = -5 V which is well below the -1.0 V threshold; FET turns on,
  body diode is reverse-biased, conduction is through Rds(on) ~60 mOhm =
  60 mV drop @ 1 A. With reverse polarity, Vgs is positive, FET is off,
  body diode is reverse-biased: no current flows.

Why PMOS not Schottky? A Schottky (SS14) drops 0.4 V at 1 A = 400 mW
dissipation. The PMOS drops 60 mV at 1 A = 60 mW. For battery-powered
designs this is a 90% efficiency improvement in the protection element.
Schottky is acceptable for USB-only designs where 400 mW is negligible.

## 7. Grounding Strategy

This board is too small (40 x 40 mm) to benefit from split planes; the
ground is a **single pour on the bottom layer.** The principles:

- **Star ground at the LDO output.** The C4 (22 uF) negative pin is the
  single point where the analog and digital grounds "meet" by design. All
  other GND vias drop into this point through the bottom plane.
- **Decoupling caps stitch directly to the plane.** Cap GND pin -> via
  -> bottom ground plane, within 0.5 mm of the cap pad. Long return traces
  create loop inductance and ruin the bypass.
- **USB connector shell** is connected to chassis ground (which on a USB
  device is the same as signal GND, via a 1 MOhm and 10 nF cap in parallel
  - omitted here for simplicity but recommended for EMC compliance).
- **Exposed pad of the AMS1117 SOT-223 (pin 2 tab)** is the heat-sink. It
  doubles as the GND return for the device. Place at least 9 thermal vias
  to bottom GND under the tab.

When to split planes: only with sensitive analog (24-bit ADC, instrumentation
amp) drawing current returns that must NOT couple to digital ground.
Splitting in a 2-layer board with a single analog sensor is almost always
a mistake - it creates loop-area issues that are worse than the EMI it
tries to fix.

## 8. PCB Layout Recommendations

### Stackup

2-layer, FR4, 1.6 mm, 1 oz copper outer. JLCPCB default.

For 4-layer (recommended for production):
- Top: signal + GND fill
- Inner1: solid GND
- Inner2: solid 3V3 (or split 3V3/VBUS)
- Bottom: signal + GND fill

### Antenna keepout

The WROOM-32E's PCB antenna is a meandered F-antenna at the module edge.
Per the Espressif datasheet, **no copper, no traces, no ground fill, no
silkscreen** in a 15 mm clear zone extending past the antenna. The module
must be mounted at the edge of the host PCB with that zone overhanging
(or removed from the host).

The board outline includes a 15 x 25 mm rectangular cut-out under the
antenna, marked in the LAYOUT_NOTES.md.

### USB differential routing

D+ and D- should be routed as a 90 Ohm differential pair. On 2-layer
FR4 1.6 mm, this needs ~12 mil traces with 7 mil spacing. Length-match
within 5 mm. Keep total length under 50 mm. The USBLC6 cap is 1.5 pF -
low enough not to require a stub-impedance correction.

### Decoupling cap placement

Within 2 mm of the IC supply pin, on the same layer, with the GND via
on the inside of the loop. For multiple caps on the same rail (1 uF + 100 nF),
the **smallest cap closest to the pin**.

### Via stitching

GND vias along the board edge every 5 mm and around the USB connector
shell to suppress edge radiation. Around the AMS1117 thermal pad: a 3x3
array of 0.4 mm drill / 0.8 mm pad vias.

## 9. EMI Mitigation Checklist

- Use slow GPIO drive strength (ESP32 supports 5/10/20/40 mA selection -
  default is 20 mA, too fast for most signals). Set to 5 mA in software for
  unused or slow-rate GPIOs.
- Tie unused pins low through internal pull-down or external 10k. Floating
  CMOS inputs oscillate at the supply rail and radiate.
- For long traces: add 22-33 Ohm series termination at the source end.
- Cable shielding: connect USB shell to PCB ground at a single point.

## 10. ADC Noise Filtering

The ESP32 ADC1 is monotonic-ish 12-bit (eff. ~9 bit) at 11 dB attenuation
(0-3.1 V range). Issues:

- **ADC2 is shared with WiFi** and unreadable while WiFi is active. Always
  use ADC1 (GPIO32-39) for analog inputs.
- Add an anti-alias RC at the pin: R = 1 kOhm, C = 10 nF -> fc = 16 kHz,
  attenuating above the sample rate.
- Reference voltage filtering: tie ADC_REF to a clean 1.1 V via 100 nF +
  10 nF and a 100 Ohm series. The internal Vref is calibrated per chip via
  eFuse - read it with `esp_adc_cal_check_efuse` at boot.
- For sub-LSB resolution, oversample by 16x and average (gains 2 bits).

## 11. Common Mistakes to Avoid

1. Pulling GPIO0 down at boot - chip enters UART download instead of
   running firmware.
2. No EN cap - chip never starts because EN slew rate is too fast and
   brownout triggers before the LDO settles.
3. Ferrite bead on data lines (D+/D-, SDA, SCL, I2S) - kills edge rates
   and breaks the protocol.
4. Shared GND return through a trace - LDO ground via and the digital
   ground via must drop into the same plane within 1 mm; not connect via
   a 10 mm trace.
5. Via under the WROOM antenna - completely detunes it, range drops 80%.
6. I2C pull-up resistors to 5 V on a 3.3 V slave - exceeds the input
   absolute max rating (typically Vdd+0.3 V).
7. AMS1117 with only a 1 uF output cap - oscillates because the LDO loop
   needs >22 uF for stability.
8. USB-C CC1 and CC2 pins floating - port presents as a power-only cable
   and host never enumerates the data lines.
9. Polyfuse on D+ or D- instead of VBUS - PTC's hold-then-trip behaviour
   is incompatible with USB negotiation timing.
10. Missing 100 nF at every ESP32 VDD pin - intermittent reboots during
    WiFi TX bursts.
11. BH1750 ADDR pin floating - I2C address is undefined, sensor enumerates
    at random address or not at all.
12. Pulling GPIO12 (MTDI) high at boot - sets flash voltage to 1.8 V,
    corrupts the WROOM-32E module.
13. Tying CHIP_EN directly to VDD33 instead of through a pull-up - cannot
    reset, and brownout cannot pull EN low.
14. Using ADC2 while WiFi is active - reads garbage.
15. Routing high-speed traces over a split in the ground plane - return
    current detours around the split, radiates as a loop antenna.
16. Reset button without debouncing cap - button bounce can re-trigger
    reset mid-boot, looping.
17. USB shield not connected to chassis GND - allows ESD to enter through
    the cable shield and find ground via the IC's substrate diodes.
18. Bulk cap before the polyfuse - inrush current trips the fuse on every
    plug event.
19. Single ground via for the entire MCU - shared return inductance modulates
    every signal with the supply current.
20. Reverse-polarity Schottky on the input rail without a fuse - if the
    diode fails short, no protection remains and downstream parts die.
21. Power LED with no series resistor - LED dies, sometimes shorts to GND
    and trips the polyfuse.
22. Tactile button across EN without RC - bounces cause multiple resets
    in 1 ms; chip may enter download mode by accident if IO0 was already
    being held.

## 12. Validation Checklist

Bring-up sequence after first reflow:

1. **Visual:** No solder bridges. USB-C orientation correct (CC1 on the
   "A" side). All 0603 caps oriented (polarity doesn't matter for ceramic
   but check that none are tombstoned).
2. **Power-off ohms:** With nothing connected, measure VBUS-to-GND, 3V3-to-GND.
   Should be >100 kOhm (the LDO and ESP32 present high impedance unmounted).
3. **Slow ramp:** Apply USB through a current-limited bench supply set to
   5.0 V / 200 mA. Confirm current <50 mA at idle.
4. **Voltage spot-check:**
   - VBUS_PROT: 4.95-5.05 V
   - 3V3_LDO: 3.27-3.33 V (+- 2% tolerance)
   - 3V3 (after FB): 3.27-3.33 V
5. **Ripple:** Scope on 3V3 with 50 MHz bandwidth limit. Should be
   <30 mVpp during idle, <80 mVpp during WiFi TX.
6. **I2C probe:** Run `i2cdetect`. Address 0x23 (BH1750) ack expected. SCL
   waveform: clean square wave, rise time <1 us at 400 kHz.
7. **Lux validation:** Compare against a calibrated meter (e.g. Extech
   LT45). Should be within +-20% across 10 lux to 10 klx range. The
   BH1750 spec is +-20% accuracy and 1 lux resolution.
8. **WiFi range:** Walk test 10 m through one wall, RSSI > -65 dBm. If
   range is poor, check antenna keepout was honoured.
9. **Reset test:** Press SW1, chip resets and reboots. Boot log on UART.
10. **Programming test:** Hold SW2 (BOOT), tap SW1 (RESET), release SW2.
    Chip enters download mode. `esptool.py flash_id` reads the flash chip
    MID/DID.

## 13. References

- Espressif. *ESP32 Hardware Design Guidelines.* v3.3, 2024.
  Section 2.1 (power), 2.2 (decoupling), 2.4 (antenna), 4.3 (strapping pins).
- Rohm Semiconductor. *BH1750FVI Datasheet.* Rev D, 2011.
  I2C timing, 0x23/0x5C address selection, typical IDD curves.
- Advanced Monolithic Systems. *AMS1117 Datasheet.* Rev 9.
  Min Cout, dropout vs Iout, thermal characterisation.
- USB-IF. *USB Type-C Cable and Connector Specification.* Rel 2.2.
  Section 4.5.1 (CC pin pull-down for UFP detection).
- USB-IF. *USB 2.0 Specification.* Section 7.1.1 (90 Ohm differential),
  7.1.2 (eye mask).
- I2C-bus specification and user manual. NXP UM10204, Rev 7.0.
  Table 10 (capacitive load), Section 7.1 (pull-up sizing).
- Texas Instruments. *AN-1148 Linear Regulator Stability.* Discussion of
  Cout ESR requirements.
- IEC 61000-4-2. ESD test methodology.
- Murata. *Ferrite Bead Application Note.* Selection by impedance-vs-DCR.
