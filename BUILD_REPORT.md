# Urine Dipstick Analyzer -- Comprehensive Build Report

**Document Version:** 1.0  
**Date:** 2026-05-15  
**Target Market:** India (CDSCO-regulated)  
**Platform:** ESP32-S3 MCU with OV2640 Camera  

---

## Table of Contents

1. [Scientific Principle and Method](#1-scientific-principle-and-method)
2. [Optical Design](#2-optical-design)
3. [Full Bill of Materials with Costs](#3-full-bill-of-materials-with-costs)
4. [PCB Design Notes](#4-pcb-design-notes)
5. [Mechanical Assembly Instructions](#5-mechanical-assembly-instructions)
6. [Firmware Overview](#6-firmware-overview)
7. [Calibration Procedure](#7-calibration-procedure)
8. [Regulatory Considerations for India](#8-regulatory-considerations-for-india-cdsco--mdr-2017)

---

## 1. Scientific Principle and Method

### 1.1 Reflectance Photometry Overview

The Urine Dipstick Analyzer operates on the principle of **reflectance photometry** (also called colorimetric analysis). A urine dipstick is a narrow plastic strip with 10 discrete reagent pads bonded along its length. Each pad contains dried chemical reagents specific to a single analyte. When the strip is dipped in a urine sample, the reagent pads absorb the specimen and undergo chemical reactions that produce a visible color change. The intensity and hue of that color change are proportional to the concentration of the target analyte in the sample.

In traditional manual reading, a trained technician visually compares each pad against a printed color chart supplied by the strip manufacturer. This method is inherently subjective, operator-dependent, and prone to timing errors. Automated reflectance photometry eliminates these variables by using a controlled light source, a calibrated image sensor, and algorithmic color quantification to produce consistent, reproducible results.

### 1.2 Parameters Measured

The device measures 10 standard urinalysis parameters. Each parameter, its underlying chemical reaction, and clinical significance are summarized below.

| Parameter | Reagent Chemistry | Clinical Range | Clinical Significance |
|---|---|---|---|
| Glucose | Glucose oxidase / peroxidase | Negative to 2000 mg/dL | Diabetes screening, glycosuria |
| Protein (Albumin) | Tetrabromophenol blue (protein error of indicators) | Negative to 2000 mg/dL | Kidney disease, proteinuria |
| pH | Methyl red + bromothymol blue | 5.0 -- 9.0 | Acid-base status, UTI, renal tubular acidosis |
| Specific Gravity | Polyionic electrolyte complex | 1.000 -- 1.030 | Hydration status, concentrating ability |
| Ketones | Sodium nitroprusside (Legal test) | Negative to 160 mg/dL | Diabetic ketoacidosis, starvation |
| Bilirubin | Diazotized dichloroaniline | Negative to 6 mg/dL | Liver disease, biliary obstruction |
| Urobilinogen | Modified Ehrlich reagent | 0.2 -- 8.0 mg/dL | Hemolysis, liver function |
| Blood / Hemoglobin | Pseudoperoxidase activity of hemoglobin | Negative to 250 RBC/uL | Hematuria, kidney stones, infection |
| Nitrite | Griess reaction (aromatic amine + coupling agent) | Negative / Positive | Bacteriuria (gram-negative organisms) |
| Leukocytes | Esterase hydrolysis of indoxyl derivative | Negative to 500 WBC/uL | Urinary tract infection, inflammation |

### 1.3 Measurement Principle

The measurement workflow proceeds as follows:

1. The urine-wetted dipstick is placed on the motorized tray.
2. After a manufacturer-specified reaction time (typically 60--120 seconds), the tray advances the strip to the imaging position.
3. A white LED array illuminates the strip under controlled, diffuse lighting conditions.
4. The OV2640 camera captures a high-resolution image of the strip surface.
5. Firmware extracts a Region of Interest (ROI) for each reagent pad.
6. The RGB pixel values within each ROI are converted to HSV color space for analysis.
7. The measured HSV triplet is compared against pre-stored calibration lookup tables (derived from known-concentration calibration strips).
8. A polynomial fitting function maps the color values to analyte concentration.
9. The concentration is classified into semiquantitative clinical categories: Negative, Trace, 1+, 2+, 3+, 4+ (or specific mg/dL ranges, depending on the analyte).

### 1.4 Applicable Standards

- **CLSI GP16-A3** -- Urinalysis: Approved Guideline (specimen handling, strip reading timing, QC)
- **ISO 15197** -- In vitro diagnostic test systems (performance requirements)
- **ISO 14971** -- Application of risk management to medical devices

---

## 2. Optical Design

### 2.1 LED Illumination System

Uniform, repeatable illumination is critical for accurate colorimetric measurement. The illumination subsystem consists of:

- **Light Source:** 5V white LED array module (color temperature ~5500K, daylight-equivalent). A single module provides sufficient flux for the small imaging area (~120 x 25 mm strip surface).
- **Diffuser:** A frosted acrylic diffuser panel (30 x 20 x 1 mm) is placed between the LED array and the dipstick surface. This converts the point-source LED output into spatially uniform, diffuse illumination across the entire strip length.
- **Illumination Geometry:** The LED/diffuser assembly is mounted at a **45-degree angle** relative to the strip surface. This angled illumination minimizes specular (mirror-like) reflections from the wet reagent pads, which would otherwise saturate the camera sensor and corrupt color readings.
- **Light Isolation:** The interior of the measurement chamber is lined with **self-adhesive flocking sheet** (black, velvet-like material). This absorbs stray light and prevents internal reflections that could contaminate the measurement.

### 2.2 Imaging System

- **Camera:** OV2640 module, 2 megapixel (1600 x 1200 resolution), connected via DVP (Digital Video Port) interface to the ESP32-S3. The DVP interface provides faster frame transfer than SPI-based camera modules, which is important for the 8-bit RGB565 or JPEG capture modes used during analysis.
- **Polarizer:** A **circular polarizer (CPL) filter** is attached to the camera lens. The CPL further rejects specular reflections from the wet, glossy surface of reagent pads. This is especially important for pads that remain visibly moist during reading.
- **Working Distance:** The camera is fixed at approximately **50 mm** from the strip surface. At this distance, the camera field of view covers the full 10-pad strip length with sufficient pixel density for per-pad ROI extraction (~80-100 pixels per pad).
- **Focus:** Fixed focus, preset at the dipstick plane during assembly. No autofocus mechanism is required because the strip-to-camera distance is mechanically constrained by the tray and mount geometry.

### 2.3 Color Calibration System

- **Color Calibration Card:** A printed reference card (20 x 10 mm) with known color patches is permanently mounted on the dipstick tray surface, adjacent to the strip position. Every captured image includes these reference patches, enabling firmware-based drift compensation.
- **White Balance Target Card:** A separate mini gray/white card provides a known-reflectance surface for automatic white balance correction. This compensates for LED aging and temperature-dependent color shifts.
- **Ambient Light Sensor:** A **BH1750** digital ambient light sensor (I2C interface) is mounted inside the measurement chamber. It detects any ambient light leakage through the tray aperture or enclosure seams. If ambient light exceeds a threshold (>5 lux), the firmware delays measurement until conditions are stable, or alerts the operator to close the tray fully.

### 2.4 UV-C Sterilization System

Urine dipstick analysis involves biological specimens, and cross-contamination between successive tests is a concern. The device includes an integrated UV-C sterilization stage:

- **UV-C LED:** A **275 nm UV-C LED module** is mounted above the tray in the retracted (home) position. After each measurement, the tray retracts to the UV-C exposure zone and the LED operates for 30 seconds, delivering germicidal irradiance to the tray surface.
- **UV Window:** A **quartz glass window** (20 x 20 mm, UV-transparent) protects the camera lens from UV exposure while allowing transmission at 275 nm. Standard glass or acrylic would absorb UV-C radiation.
- **Safety Interlock:** An **MC-38 magnetic reed switch** is mounted at the tray aperture. The switch detects whether the tray is retracted and the chamber is sealed before allowing UV-C activation. If the tray is extended or the chamber is open, UV-C emission is hardware-blocked via MOSFET gate control.
- **UV Shielding:** **EPDM foam gaskets** are installed at all seams and joints in the UV-C zone to prevent UV light leakage to the exterior. EPDM rubber is highly resistant to UV degradation.

---

## 3. Full Bill of Materials with Costs

### 3.1 Electrical Components

| Component | Description | Qty | Unit Cost (USD) | Total (USD) | Source |
|---|---|---|---|---|---|
| ESP32-S3-DevKitC-1-N8R8 | Main MCU, 8MB PSRAM for image processing | 1 | 15.00 | 15.00 | DigiKey |
| OV2640 Camera + CPL | Camera module with circular polarizer filter | 1 | 22.00 | 22.00 | Amazon |
| SSD1306 OLED Display | 0.96" I2C monochrome display, 128x64 px | 1 | 5.00 | 5.00 | Amazon |
| White LED Array | 5V LED module, ~5500K color temp | 1 | 3.00 | 3.00 | Amazon |
| 3.7V 1000mAh LiPo | Rechargeable lithium polymer battery | 1 | 10.00 | 10.00 | Amazon |
| MCP73833 USB-C Charger | LiPo charge management IC breakout | 1 | 12.50 | 12.50 | Adafruit |
| Pololu S13V25F9 | 9V/5V buck-boost voltage regulator | 1 | 12.00 | 12.00 | Pololu |
| Pololu S7V8F3 | 3.3V buck-boost voltage regulator | 1 | 6.00 | 6.00 | Pololu |
| Power Distribution PCB | Custom 2-layer power management hub | 1 | 5.00 | 5.00 | OSHPark |
| A4988 Stepper Driver | Bipolar stepper motor driver, adjustable current | 1 | 5.00 | 5.00 | Amazon |
| NEMA 17 Stepper Motor | 20mm body length, 200 steps/rev, 12V rated | 1 | 12.00 | 12.00 | Amazon |
| SHT31-D | Digital temperature and humidity sensor (I2C) | 1 | 12.00 | 12.00 | Adafruit |
| BH1750 | Digital ambient light sensor module (I2C) | 1 | 4.50 | 4.50 | Amazon |
| 10K NTC Thermistor | Tray surface temperature sensing | 1 | 0.50 | 0.50 | Amazon |
| GM65 Barcode Scanner | QR/barcode reader module (UART interface) | 1 | 28.00 | 28.00 | Amazon |
| Micro SD Card Module | SPI interface, data logging | 1 | 4.00 | 4.00 | Amazon |
| 275nm UV-C LED | Germicidal sterilization LED | 1 | 15.00 | 15.00 | DigiKey |
| Polyimide Heater Film | 25x50mm, 5V, ~2W | 1 | 8.00 | 8.00 | Amazon |
| 30mm 5V DC Fan | Chamber ventilation and cooling | 1 | 5.00 | 5.00 | Amazon |
| 5V Active Piezo Buzzer | Audible alerts and notifications | 1 | 1.50 | 1.50 | Amazon |
| RGB LED (Common Anode) | Status indicator (R/G/B channels) | 1 | 0.50 | 0.50 | Amazon |
| Tactile Push Button 6x6mm | Measure trigger, menu navigation | 1 | 0.50 | 0.50 | Amazon |
| MC-38 Reed Switch | Magnetic safety interlock sensor | 1 | 4.00 | 4.00 | Amazon |
| Micro Limit Switch | Tray home position detection | 1 | 2.00 | 2.00 | Amazon |
| 2N7000 MOSFET (N-ch) | Fan control switching | 1 | 0.50 | 0.50 | Amazon |
| IRLZ44N MOSFET (N-ch) | UV LED driver (logic-level gate) | 1 | 1.00 | 1.00 | Amazon |
| IRLZ44N MOSFET (N-ch) | Heater control switching | 1 | 1.00 | 1.00 | Amazon |
| Resistors (assorted) | Pull-ups, current limiters, voltage dividers | ~20 | 0.05 | 1.00 | Local |
| Capacitors (assorted) | 100nF ceramic decoupling, 10uF bulk | ~15 | 0.05 | 0.75 | Local |

**Electrical Subtotal: $197.25**

### 3.2 Mechanical Components

| Component | Description | Qty | Unit Cost (USD) | Total (USD) | Source |
|---|---|---|---|---|---|
| Molded Enclosure Base | 180x120x40mm ABS/PETG, main housing | 1 | 25.00 | 25.00 | 3D print / mold |
| Enclosure Top Cover | 180x120x5mm PETG, snap-fit or screw mount | 1 | 7.00 | 7.00 | 3D print |
| Molded Dipstick Tray | 120x25x8mm, strip channel with calibration card recess | 1 | 10.00 | 10.00 | 3D print / mold |
| Camera and LED Mount | 40x30x25mm PETG bracket, 45-degree LED angle | 1 | 4.00 | 4.00 | 3D print |
| Scanner Mount | 35x25x15mm bracket for GM65 barcode module | 1 | 3.00 | 3.00 | 3D print |
| Vent Grill | 35x35mm slotted panel for fan exhaust | 1 | 2.00 | 2.00 | 3D print |
| Cable Management Frame | 160x100x10mm internal skeleton for routing wires | 1 | 2.00 | 2.00 | 3D print |
| T8 Lead Screw + Nut | 100mm linear actuator, 2mm pitch | 1 | 8.00 | 8.00 | Amazon |
| M2x6mm Screws | PCB and module mounting | 12 | 0.05 | 0.60 | Amazon |
| M3x8mm Screws | Enclosure cover attachment | 4 | 0.10 | 0.40 | Amazon |
| M3 Heat-Set Inserts | Brass threaded inserts for PETG | 4 | 0.20 | 0.80 | Amazon |
| M2.5 Standoffs (kit) | PCB mounting standoff set (M/F, various lengths) | 1 | 4.00 | 4.00 | Amazon |
| Silicone Gasket | 98x68x1mm chamber seal | 1 | 3.00 | 3.00 | Amazon |
| Frosted Acrylic Diffuser | 30x20x1mm, light diffusion panel | 1 | 2.00 | 2.00 | Amazon |
| Color Calibration Card | 20x10mm printed color reference patches | 1 | 1.00 | 1.00 | Amazon |
| White Balance Card | Mini gray/white reference card | 1 | 5.00 | 5.00 | Amazon |
| Quartz Glass Window | 20x20mm UV-transparent window | 1 | 8.00 | 8.00 | Amazon |
| Flocking Sheet | Self-adhesive black light absorber, A4 sheet | 1 | 10.00 | 10.00 | Amazon |
| EPDM Foam Gasket | UV shielding strips, adhesive-backed | 1 | 5.00 | 5.00 | Amazon |

**Mechanical Subtotal: $100.80**

### 3.3 Cost Summary

| Category | Cost (USD) |
|---|---|
| Electrical Components | $197.25 |
| Mechanical Components | $100.80 |
| **Prototype Total** | **~$298** |
| **Estimated Volume Cost (100+ units)** | **$180 -- $220** |

Volume cost reductions come from: bulk component pricing (30--40% savings on passives and modules), injection-molded enclosure parts replacing 3D prints, and consolidated PCB assembly replacing hand-wired breakout boards.

---

## 4. PCB Design Notes

### 4.1 Architecture

The prototype uses the **ESP32-S3-DevKitC-1** development board as the main controller, paired with a custom **Power Distribution PCB** that centralizes voltage regulation, decoupling, and ground management.

For production, these should be consolidated into a single application-specific PCB carrying the ESP32-S3 module (ESP32-S3-WROOM-1) directly, along with all power management, sensor interfaces, and driver circuits.

### 4.2 Power Distribution PCB

- **Layer Count:** 2-layer FR-4, 1.6mm thickness, 1oz copper
- **Dimensions:** Approximately 50 x 40 mm
- **Function:** Accepts 3.3V and 5V from the buck-boost regulators and distributes to all subsystems with per-rail decoupling and protection

### 4.3 Grounding Strategy

- **Star grounding topology:** Separate analog and digital ground planes converge at a single star point near the power entry. This prevents digital switching noise (stepper driver, ESP32 clock) from coupling into the analog sensor readings (thermistor ADC, camera DVP bus).
- The camera DVP data bus and the I2C sensor bus should be routed on opposite sides of the PCB with a ground pour separating them.

### 4.4 Decoupling

- **100nF ceramic capacitor** placed within 5mm of every IC power pin (ESP32-S3, SHT31, BH1750, OLED driver, A4988)
- **10uF electrolytic or tantalum** bulk capacitor on each power rail at the point of entry to the PCB
- **100uF electrolytic** on the stepper driver VMOT pin (required by A4988 datasheet to absorb back-EMF spikes)

### 4.5 Interface Bus Layout

| Bus | Signals | GPIO Assignments | Notes |
|---|---|---|---|
| I2C | SCL, SDA | GPIO18 (SCL), GPIO19 (SDA) | 4.7K ohm pull-ups to 3.3V; max 3 devices |
| SPI (SD Card) | MOSI, MISO, SCK, CS | GPIO38, GPIO39, GPIO40, GPIO41 | Dedicated bus, no shared devices |
| DVP (Camera) | D0-D7, PCLK, VSYNC, HREF, XCLK | Per ESP32-S3 DVP pin map | Short traces, matched length preferred |
| UART (Scanner) | TX, RX | GPIO43 (TX), GPIO44 (RX) | 9600 baud default for GM65 |
| Stepper | STEP, DIR | GPIO4 (STEP), GPIO16 (DIR) | 100 ohm series resistors recommended |

### 4.6 MOSFET Driver Circuits

All three MOSFET-switched loads (fan, UV LED, heater) use identical driver topology:

- **Gate:** Connected to ESP32 GPIO via 100 ohm series resistor (limits inrush current to gate capacitance)
- **Gate Pull-Down:** 10K ohm resistor from gate to ground (ensures load is OFF during ESP32 boot/reset when GPIOs are floating)
- **Drain:** Connected to load negative terminal
- **Source:** Connected to ground
- **Flyback Diode:** 1N4007 across the fan motor terminals (suppresses inductive kick)

### 4.7 Production Recommendations

- Move to a **4-layer stackup** (Signal / Ground / Power / Signal) for the production board. This provides a continuous ground plane for EMI control and simplifies routing.
- Add **ESD protection** (TVS diodes) on the USB-C connector, UART lines, and any external-facing connectors.
- Add **reverse polarity protection** (P-channel MOSFET) on the battery input.
- Recommended fabricators: **JLCPCB** (lowest cost, fast turnaround), **OSHPark** (higher quality, US-based), or local Indian PCB shops for rapid iteration.

---

## 5. Mechanical Assembly Instructions

### Phase 1: Part Fabrication and Preparation

1. **3D print all mechanical parts.** Use PETG filament (preferred for chemical resistance and moderate heat tolerance) or ABS. Print internal parts (cable frame, mounts) in black to minimize internal reflections. Print the enclosure base and cover in the desired product color (white or light gray recommended for a clinical appearance).
2. **Install M3 heat-set inserts** into the four corner mounting holes of the enclosure base. Use a soldering iron set to 220C with a heat-set insert tip. Press each insert flush with the surface.
3. **Apply flocking material.** Cut self-adhesive flocking sheet to fit the interior surfaces of the measurement chamber (the area around the camera and LED mount). Peel and apply, pressing firmly to remove air bubbles.
4. **Prepare the dipstick tray.** Attach the color calibration card and white balance card to their respective recesses on the tray surface using thin double-sided adhesive tape.
5. **Install optical elements.** Press-fit the quartz glass window into the camera mount aperture. Press-fit the frosted acrylic diffuser into the LED mount slot.

### Phase 2: Electrical Wiring

**Power chain (wire first, verify before connecting MCU):**

1. Solder the LiPo battery connector to the MCP73833 USB-C charger board input.
2. Connect charger board output to the input of both buck-boost regulators (Pololu S13V25F9 for 9V/5V and Pololu S7V8F3 for 3.3V). Use a solder-bridge jumper or small slide switch for a master power cutoff.
3. Route regulator outputs to the power distribution PCB input terminals.

**3.3V rail distribution (from power PCB):**

4. ESP32-S3 DevKit 3.3V pin, SSD1306 OLED VCC, SHT31-D VCC, BH1750 VCC, GM65 barcode scanner VCC, SD card module VCC, tactile button pull-up, RGB LED anodes (via current-limiting resistors), buzzer logic supply.

**5V rail distribution:**

5. Fan positive (through 2N7000 MOSFET drain), UV-C LED anode (through IRLZ44N MOSFET drain with appropriate current-limiting resistor -- calculate based on UV LED forward voltage and desired drive current), polyimide heater (through IRLZ44N MOSFET drain), white LED array VCC.

**9V rail:**

6. A4988 stepper driver VMOT pin (with 100uF decoupling capacitor across VMOT and GND).

**Signal wiring:**

7. **I2C bus:** Wire GPIO18 (SCL) and GPIO19 (SDA) from ESP32 to SSD1306, SHT31-D, and BH1750 in a daisy-chain topology. Install 4.7K ohm pull-up resistors from SCL and SDA to 3.3V at the ESP32 end of the bus.
8. **SPI bus:** Wire GPIO38 (MOSI), GPIO39 (MISO), GPIO40 (SCK), GPIO41 (CS) to the SD card module.
9. **Stepper driver:** Wire GPIO4 to A4988 STEP input, GPIO16 to A4988 DIR input. Connect A4988 motor outputs (1A, 1B, 2A, 2B) to NEMA 17 motor windings per the motor datasheet.
10. **MOSFET gates:** Wire ESP32 GPIOs to each MOSFET gate via 100 ohm series resistor. Install 10K ohm pull-down resistors from each gate to ground.
11. **Camera DVP bus:** Connect OV2640 module to ESP32-S3 DVP pins per the ESP32-S3 camera pinout reference. This is typically an 8-bit parallel data bus plus PCLK, VSYNC, HREF, XCLK, SIOD, and SIOC.
12. **Barcode scanner UART:** Wire GM65 TX to ESP32 GPIO44 (RX), GM65 RX to ESP32 GPIO43 (TX).
13. **Safety interlock:** Wire MC-38 reed switch between GPIO21 and ground (enable internal pull-up in firmware).
14. **Limit switch:** Wire micro limit switch between GPIO15 and ground (enable internal pull-up in firmware).
15. **Thermistor:** Wire 10K NTC in a voltage divider (10K NTC + 10K fixed resistor) to an ESP32 ADC-capable GPIO.
16. **Button:** Wire tactile switch between a GPIO and ground (enable internal pull-up).
17. **Buzzer:** Wire to a GPIO (active buzzer, digital HIGH = ON).
18. **RGB LED:** Wire each color channel (R, G, B) through a 330 ohm current-limiting resistor to individual ESP32 GPIOs. Common anode connects to 3.3V.

### Phase 3: Bring-Up and Verification

1. **Power rail verification.** Before connecting the ESP32 or any sensor modules, power on the system and measure all rails with a multimeter: 3.3V (+/- 0.1V), 5V (+/- 0.25V), 9V (+/- 0.5V). Verify that MOSFETs are OFF (gate pull-downs holding loads off).
2. **Flash firmware.** Connect ESP32-S3 via USB-C and flash the firmware using `idf.py flash` (ESP-IDF) or Arduino IDE upload.
3. **I2C device scan.** Run an I2C scanner sketch to verify all three devices respond: OLED at 0x3C, SHT31 at 0x44, BH1750 at 0x23.
4. **Stepper calibration.** Command the stepper to advance slowly until the limit switch triggers. Record the step count as the home position. Measure the total travel from home to the camera imaging position and program the target step count.
5. **Camera test.** Initialize the OV2640 in JPEG mode, capture a test frame, and verify image quality on the OLED or via serial output to a PC.
6. **White balance calibration.** Capture an image of the white balance card under LED illumination. Record the reference RGB values and store in NVS flash.
7. **Heater PID tuning.** Enable the heater and monitor the thermistor reading. Tune PID constants (Kp, Ki, Kd) to achieve a stable 37C setpoint with less than 1C overshoot. This temperature optimizes enzyme reaction kinetics on the reagent pads.
8. **UV-C interlock test.** With the tray extended (chamber open), attempt to activate the UV-C LED via firmware. Verify that the reed switch interlock prevents activation. Retract the tray (chamber closed) and verify UV-C activates.
9. **Barcode scanner test.** Present a QR code to the GM65 module and verify UART data reception on the ESP32.

### Phase 4: Final Assembly

1. Mount the ESP32 DevKit and power distribution PCB to the cable management frame using M2.5 standoffs and M2x6mm screws.
2. Install the tray mechanism: attach the NEMA 17 motor to the enclosure base, install the T8 lead screw through the tray nut, and verify smooth linear travel.
3. Secure the camera/LED mount to the enclosure base above the tray imaging position. Verify alignment by capturing a test image of a dipstick on the tray.
4. Mount the GM65 scanner bracket at the tray entry point.
5. Route all wiring through the cable management frame channels. Use small cable ties or adhesive clips to secure loose wires away from moving tray parts.
6. Install the silicone gasket around the perimeter of the measurement chamber opening.
7. Install EPDM foam gaskets around the UV-C LED zone to seal UV light leakage paths.
8. Install the vent grill in the enclosure wall (snap-fit design) and mount the 30mm fan behind it.
9. Place the enclosure top cover and secure with four M3x8mm screws into the heat-set inserts.
10. Perform a final functional test: full measurement cycle (insert strip, press button, capture, analyze, display, sterilize).

---

## 6. Firmware Overview

### 6.1 Architecture

- **Platform:** ESP-IDF v5.x (recommended for full hardware control and PSRAM management) or Arduino-ESP32 core for faster prototyping.
- **Processor:** ESP32-S3 dual-core Xtensa LX7 at 240 MHz.
- **Memory:** 8MB PSRAM (external, accessed via OPI interface) is essential for holding camera frame buffers. A single 1600x1200 RGB565 frame consumes approximately 3.75 MB. PSRAM also holds the color lookup tables and image processing buffers.
- **Storage:** Internal NVS (Non-Volatile Storage) partition for calibration coefficients, device settings, and usage counters. External Micro SD card for CSV data logging.

### 6.2 State Machine

The main firmware loop operates as a state machine with the following states:

```
IDLE --> SCAN_BARCODE --> WAIT_REACTION --> CAPTURE --> ANALYZE --> DISPLAY --> LOG --> STERILIZE --> IDLE
```

| State | Description | Duration |
|---|---|---|
| IDLE | Awaiting button press, showing status on OLED | Indefinite |
| SCAN_BARCODE | Optional: scan patient ID or reagent lot QR code | 5 seconds timeout |
| WAIT_REACTION | Countdown timer for reagent reaction (60--120 sec) | Configurable |
| CAPTURE | Advance tray, turn on LED, capture camera image | ~2 seconds |
| ANALYZE | ROI extraction, color quantification, classification | ~3 seconds |
| DISPLAY | Show results on OLED, beep buzzer for completion | Until dismissed |
| LOG | Write CSV record to SD card | <1 second |
| STERILIZE | Retract tray, run UV-C for 30 seconds | 30 seconds |

### 6.3 Key Firmware Modules

1. **Camera Driver** -- OV2640 initialization via SCCB (I2C-like) protocol, register configuration for resolution, exposure, gain, white balance. DVP capture in RGB565 mode for color analysis or JPEG mode for storage. Frame buffer allocated in PSRAM.

2. **Image Processing** -- ROI extraction using predefined pixel coordinates for each of the 10 reagent pads (coordinates determined during calibration setup). Median filter (3x3 kernel) applied within each ROI to reject salt-and-pepper noise. RGB-to-HSV conversion for each pad region. Mean H, S, V values computed for the ROI.

3. **Color Analysis** -- Each pad's measured HSV triplet is compared against a calibration lookup table stored in NVS. The lookup table contains HSV values for each concentration level (typically 5--7 levels per analyte). A polynomial curve fit (second or third order) interpolates between calibration points to determine the analyte concentration. The result is then classified into the nearest semiquantitative category.

4. **Calibration Engine** -- Manages factory calibration data, daily QC validation, and field recalibration. Stores per-pad polynomial coefficients, temperature compensation factors, and white balance reference values in NVS flash. Provides an OLED-guided recalibration workflow.

5. **Stepper Control** -- Uses the AccelStepper library (or equivalent ESP-IDF driver) for smooth acceleration/deceleration profiles. Homing sequence runs at startup: the stepper retracts until the limit switch triggers, then the step counter resets to zero. Target positions for each pad are stored as step offsets from home.

6. **Thermal Control** -- PID control loop for the polyimide heater. Setpoint: 37C (body temperature, optimal for most dipstick enzyme reactions). Process variable: NTC thermistor reading via ADC. Control output: PWM duty cycle to the heater MOSFET. Ambient temperature and humidity monitored by SHT31-D for environmental compensation.

7. **Display Manager** -- SSD1306 OLED driver (using U8g2 or Adafruit SSD1306 library). Implements a menu system: main results screen, scrollable parameter list, history browser, settings menu, calibration mode, and QC status display. 128x64 pixel resolution constrains layout to compact, text-focused interfaces.

8. **Data Logger** -- Writes CSV records to the Micro SD card via SPI. Each record contains: timestamp (from RTC or NTP if WiFi available), patient ID (from barcode scanner), all 10 parameter results (semiquantitative category and raw HSV values), ambient temperature, humidity, and QC status flag.

9. **Barcode Scanner Interface** -- GM65 UART protocol handler. Parses scanned QR codes or barcodes for patient ID strings and reagent lot numbers. Lot numbers enable automatic selection of the correct calibration table if multiple strip brands are supported.

10. **Safety Manager** -- Continuously monitors: reed switch state (UV interlock), thermistor for over-temperature (shutdown heater above 50C), battery voltage via ADC (low-battery warning below 3.4V, shutdown below 3.2V), ambient light level (measurement inhibit if chamber is not dark).

### 6.4 Measurement Workflow (Detailed)

1. User places urine-wetted dipstick on tray and presses the Measure button.
2. (Optional) GM65 scans patient ID barcode if present on the strip packaging or a label.
3. OLED displays a countdown timer for the reagent reaction period (configurable, default 120 seconds for most commercial strips).
4. When the timer expires, the stepper motor advances the tray into the measurement chamber.
5. The limit switch confirms the tray has cleared the aperture; the reed switch confirms chamber closure.
6. The white LED array is powered on. The firmware waits 200 ms for LED thermal stabilization.
7. The BH1750 sensor confirms illumination levels are within the expected range.
8. The OV2640 captures a single frame in RGB565 mode, stored in PSRAM.
9. The white LED is turned off.
10. The firmware identifies the calibration card region in the image, measures its RGB values, and computes a per-channel gain correction relative to the stored reference values.
11. For each of the 10 reagent pads, the firmware extracts the ROI, applies median filtering, converts to HSV, and applies the gain correction.
12. Each pad's corrected HSV values are mapped to an analyte concentration via the stored polynomial calibration curves.
13. Concentrations are classified into semiquantitative categories.
14. Results are displayed on the OLED.
15. A CSV record is appended to the SD card.
16. The buzzer sounds a completion tone.
17. The stepper retracts the tray to the home position (UV-C zone).
18. The UV-C LED activates for 30 seconds (with interlock verification).
19. The UV-C LED turns off, and the system returns to IDLE.

---

## 7. Calibration Procedure

### 7.1 Initial Factory Calibration

Factory calibration establishes the baseline color-to-concentration mapping for each analyte. This must be performed once during manufacturing, using manufacturer-supplied calibration strips with known analyte concentrations.

**Step 1: White Balance**

1. Insert a blank (unreacted) dipstick strip onto the tray.
2. Run the measurement sequence.
3. Record the RGB values for the white balance card region. These become the reference white point.
4. Record the RGB values for each unreacted pad. These become the "negative" baseline for each analyte.
5. Store all reference values in NVS flash.

**Step 2: Multi-Level Calibration**

For each of the 10 analytes, measure calibration strips at 5 known concentration levels:

| Level | Example (Glucose) | Example (Protein) |
|---|---|---|
| Level 0 (Negative) | 0 mg/dL | 0 mg/dL |
| Level 1 (Trace/Low) | 100 mg/dL | 15 mg/dL |
| Level 2 (Moderate) | 250 mg/dL | 30 mg/dL |
| Level 3 (High) | 500 mg/dL | 100 mg/dL |
| Level 4 (Very High) | 2000 mg/dL | 2000 mg/dL |

For each level, capture the image and record the H, S, V values for the corresponding pad. This yields a 5-point calibration dataset per analyte.

**Step 3: Curve Fitting**

Fit a second-order polynomial to each analyte's calibration data:

```
Concentration = a0 + a1*H + a2*S + a3*V + a4*H^2 + a5*S^2 + a6*V^2
```

The coefficients (a0 through a6) are stored in NVS flash. At measurement time, the firmware evaluates this polynomial with the measured H, S, V values to determine the concentration.

**Step 4: Linearity Verification**

After curve fitting, verify monotonicity: as the known concentration increases, the predicted concentration must also increase without sign reversals. Non-monotonic behavior indicates a bad calibration point or an inappropriate polynomial order.

**Step 5: Temperature Compensation**

Repeat the full calibration at four temperatures: 20C, 25C, 30C, and 35C (controlled by the internal heater and SHT31 monitoring). Derive linear temperature correction factors for each analyte:

```
Corrected_Concentration = Raw_Concentration * (1 + Kt * (T_measured - T_reference))
```

Store the temperature coefficient Kt for each analyte in NVS.

### 7.2 Daily Quality Control

1. At the start of each operating day, the operator inserts a provided QC calibration strip with known analyte values.
2. The device runs a standard measurement cycle and compares the results against the expected values stored in firmware.
3. If all 10 parameters fall within +/- 10% of expected values, the QC passes and normal operation is enabled.
4. If any parameter deviates more than 10%, the OLED displays a QC FAIL warning and prompts the operator to run a field recalibration.
5. QC results (pass/fail, deviations for each parameter) are logged to the SD card with a QC flag.

### 7.3 Field Recalibration

1. The operator accesses calibration mode via the OLED menu (long-press the button for 3 seconds).
2. On-screen prompts guide insertion of calibration strips at each concentration level.
3. The firmware captures and processes each strip, then recomputes the polynomial coefficients.
4. Updated coefficients are stored in NVS, overwriting the previous values.
5. A verification pass automatically runs: the operator inserts one additional calibration strip, and the firmware confirms the new coefficients produce results within specification.

---

## 8. Regulatory Considerations for India (CDSCO / MDR 2017)

### 8.1 Device Classification

Under India's **Medical Devices Rules, 2017** (MDR 2017), administered by the **Central Drugs Standard Control Organization (CDSCO)**, this device is classified as a **Class B In-Vitro Diagnostic (IVD) Medical Device** (moderate risk). The classification is based on:

- The device performs in-vitro analysis of human biological specimens (urine).
- Results are used for screening and monitoring, not as sole confirmatory diagnostic evidence.
- The device does not involve invasive contact with the patient.
- Urine dipstick analyzers are explicitly categorized under moderate-risk IVD devices in the CDSCO classification guidelines.

### 8.2 Registration Process

**Step 1: Manufacturing License (Form MD-1)**

- **Applicant:** The manufacturing entity (company or individual).
- **Authority:** State Drug Licensing Authority of the state where the manufacturing facility is located.
- **Requirements:** GMP-compliant manufacturing facility, qualified technical staff, documented manufacturing process, quality control laboratory.
- **Fee:** INR 5,000 -- 10,000 (approximately USD 60 -- 120).
- **Timeline:** 2 -- 3 months from application to issuance.

**Step 2: Product Registration (Form MD-6)**

- **Authority:** CDSCO, New Delhi (online submission via the SUGAM portal).
- **Required Documentation:**
  - Device Master File (description, intended use, specifications)
  - Technical documentation (design files, schematics, firmware description)
  - Risk analysis per ISO 14971 (FMEA, hazard analysis, risk mitigation)
  - Performance evaluation data (analytical sensitivity, specificity, precision, accuracy studies comparing against a predicate device)
  - Clinical evidence or literature review demonstrating clinical validity of urine dipstick analysis
  - QMS certificate (ISO 13485:2016)
  - Labeling and Instructions for Use (IFU) drafts
  - Declaration of conformity
- **Fee:** INR 10,000 -- 50,000 (approximately USD 120 -- 600), depending on device sub-class.
- **Timeline:** 6 -- 12 months. CDSCO may request additional data or clarification, which can extend the timeline.

**Step 3: Quality Management System Certification**

- **Standard:** ISO 13485:2016 (Medical Devices -- Quality Management Systems)
- **Certification Bodies:** TUV SUD, BSI, SGS, or Bureau Veritas (must be accredited notified bodies).
- **Cost:** USD 5,000 -- 15,000 for initial certification audit, plus annual surveillance audit fees (USD 2,000 -- 5,000).
- **Scope:** Covers design controls, document management, supplier management, production controls, CAPA, and post-market surveillance.

### 8.3 Standards Compliance

The following standards apply to the design, manufacture, and testing of this device:

| Standard | Title | Applicability |
|---|---|---|
| IEC 61010-1 | Safety for electrical equipment for measurement, control, and laboratory use | General safety requirements |
| IEC 61010-2-101 | Particular requirements for IVD medical equipment | IVD-specific safety requirements |
| ISO 14971 | Application of risk management to medical devices | Risk analysis (FMEA, FTA) |
| IEC 62304 | Medical device software -- Software lifecycle processes | Firmware development lifecycle |
| ISO 13485 | Quality management systems for medical devices | Manufacturing QMS |
| CLSI GP16-A3 | Urinalysis -- Approved Guideline | Analytical methodology, QC requirements |
| IEC 62471 | Photobiological safety of lamps and lamp systems | UV-C LED safety assessment |

### 8.4 Labeling Requirements (MDR 2017)

All labels, packaging, and Instructions for Use must include:

- Device name and model number
- Manufacturer name, address, and contact information
- "For In-Vitro Diagnostic Use Only" (prominently displayed)
- Batch or lot number
- Date of manufacture
- Expiry date or shelf life (if applicable to consumables)
- Storage and operating conditions (temperature, humidity)
- CDSCO registration number (after approval)
- Unique Device Identification (UDI) number
- CE or BIS mark (if applicable)
- Instructions in **English and Hindi** (minimum two languages)
- Caution: "UV-C radiation source -- do not operate with tray open"
- Electrical safety symbols per IEC 60417

### 8.5 Post-Market Requirements

- **Adverse Event Reporting:** Mandatory reporting to CDSCO within 10 days for serious incidents.
- **Field Safety Corrective Actions (FSCA):** Documented procedure for recalls or safety notices.
- **Post-Market Surveillance:** Periodic review of device performance, customer complaints, and QC data.
- **Annual License Renewal:** Manufacturing license must be renewed annually with the state licensing authority.

### 8.6 Market Positioning and Pricing

| Competing Device | Approximate Price (INR) | Origin |
|---|---|---|
| Siemens Clinitek Status+ | 80,000 -- 1,20,000 | Imported (Germany) |
| Arkray PocketChem UA | 60,000 -- 80,000 | Imported (Japan) |
| Mission U120 | 35,000 -- 50,000 | Imported (China) |
| **This Device (Target)** | **15,000 -- 20,000** | **Domestic (India)** |

The target price of INR 15,000 -- 20,000 represents a 60 -- 80% cost reduction versus imported alternatives. This is achievable due to: local manufacturing (no import duties, lower logistics costs), ESP32-based platform (low-cost MCU versus proprietary ASICs), 3D-printed or locally injection-molded enclosure (versus imported housings), and simplified optical design (single camera versus multi-LED reflectance arrays). The target market includes primary health centers (PHCs), community health centers (CHCs), diagnostic laboratories, and point-of-care clinics across rural and semi-urban India, where imported analyzers are cost-prohibitive.

---

*End of Build Report*
