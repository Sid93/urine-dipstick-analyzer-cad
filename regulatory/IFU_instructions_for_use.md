# INSTRUCTIONS FOR USE (IFU)
## Urine Dipstick Analyzer — Model UDA-PROTO-001

**For professional in vitro diagnostic use only.**

| | |
|---|---|
| **Document No.** | IFU-UDA-001 |
| **Version** | 0.1 (Draft) |
| **Date** | 2026-05-16 |
| **Languages provided** | English (this revision) |

---

## 1. Symbols Glossary (ISO 15223-1)

| Symbol | Reference | Meaning |
|---|---|---|
| Factory icon | 15223-1 5.1.1 | Manufacturer |
| Date in box | 15223-1 5.1.3 | Date of manufacture |
| Hourglass / expiry | 15223-1 5.1.4 | Use-by date |
| LOT | 15223-1 5.1.5 | Batch / lot code |
| REF | 15223-1 5.1.6 | Catalogue / model number |
| SN | 15223-1 5.1.7 | Serial number |
| Two-arrow recycle | 15223-1 5.4.5 | Single-use (applies to reagent strip, not to device) |
| IVD | 15223-1 5.5.1 | In vitro diagnostic medical device |
| Open book | 15223-1 5.4.3 | Consult instructions for use |
| Exclamation triangle | 15223-1 5.4.4 | Caution |
| Biohazard | 15223-1 5.4.6 (ISO 7010 W009) | Biological hazard |
| UV warning | ISO 7010 W027 | Ultraviolet radiation |
| Crossed-bin | EN 50419 / WEEE | Do not discard in normal waste |
| Temperature range | 15223-1 5.3.7 | Storage temperature limits |
| Humidity range | 15223-1 5.3.8 | Storage humidity limits |
| Umbrella with droplets | 15223-1 5.3.4 | Keep dry |
| Sun-with-cross | 15223-1 5.3.2 | Keep away from sunlight |
| Country of origin | 15223-1 5.1.11 | Country of manufacture |
| Authorised representative | 15223-1 5.1.2 | If applicable |

---

## 2. Indications for Use

The Urine Dipstick Analyzer UDA-PROTO-001 is intended for the **semi-quantitative measurement** of glucose, protein, ketones, bilirubin, blood, pH, urobilinogen, nitrite, leukocytes, and specific gravity in human urine, using commercially available 10-pad reagent strips.

- **Intended user:** clinical laboratory technician, general practitioner, trained healthcare worker.
- **Intended environment:** indoor clinic or laboratory bench; ambient 15–35 °C, 20–80% RH non-condensing, indoor lighting 200–1000 lux.
- **Patient population:** adults and children ≥ 2 years of age.
- **Contraindications:** not for use with paediatric < 2 years; not for testing fluids other than human urine; not for use as a sole determinant in critical-care decisions; not for home use by lay persons.

Results from this device must be interpreted by a qualified healthcare provider in conjunction with clinical findings.

---

## 3. Warnings and Precautions

1. **Biohazard.** Urine is a potentially infectious body fluid. Always wear gloves; avoid splashes; clean the tray between tests.
2. **UV-C radiation.** The device contains a 275 nm UV-C LED used for tray sterilisation. **Do not stare into the chamber or attempt to defeat the tray interlock.** UV-C can cause photokeratitis (eye burns) and skin erythema.
3. **Do not open the device.** No user-serviceable parts are inside. Opening voids warranty and may expose internal hazards.
4. **Do not immerse the device.** It is rated IP22 (drip-resistant from above only). Do not place under running water.
5. **Use only specified reagent strips.** Refer to §5 for the validated brands. Use of other strips may produce inaccurate results.
6. **Do not use expired strips.** Expired reagents give unreliable readings.
7. **Do not place the device in direct sunlight.** Ambient light leakage will saturate the optical reading and produce errors.
8. **Battery safety.** Use only the supplied USB-C charger or a certified USB-C 5 V / 1 A source. Do not puncture, crush, or expose to temperatures above 60 °C. In the event of swelling or unusual heating, stop use immediately and contact service.
9. **Charging environment.** Charge only on a non-flammable, dry surface, in a ventilated area.
10. **EMC.** Maintain ≥ 30 cm distance from active radio-frequency transmitters (e.g., mobile phones in voice mode).
11. **Cleanliness.** Wipe the tray with 70% IPA between tests. Do not use bleach (sodium hypochlorite) — it degrades the EPDM gasket.
12. **No reuse of strips.** Reagent strips are single-use only.
13. **Calibration.** Recalibrate annually or after any service event. Use only the supplied ColorChecker card.
14. **Software updates.** Install firmware updates only when prompted by the device and only from the manufacturer's authorised source.
15. **Disposal.** Do not discard the device or its battery in ordinary refuse; see §14.

---

## 4. Device Description

### 4.1 What's in the box

- Urine Dipstick Analyzer device (1)
- USB-C charging cable (1, 1 m)
- ColorChecker calibration card (1)
- White-balance card (1)
- Quick-start guide (1)
- Full IFU (this document)
- Warranty card (1)

### 4.2 Controls and indicators

- **Front:** 2.4" colour touchscreen TFT (320 × 240)
- **Right side:** tactile push-button (Power / Wake / Run)
- **Top:** strip-tray slot with motorised tray
- **Rear:** USB-C charging port; barcode-scan window (GM65)
- **Bottom:** vent grill, serial-number label, rubber feet (×4)
- **Indicator LED:** RGB status LED on the front panel (Green = ready; Amber = busy; Red = error)
- **Buzzer:** internal piezo (audible alerts)

---

## 5. Compatible Reagent Strips

Calibration tables ship for the following validated brands:

| Brand | Model |
|---|---|
| Siemens | Multistix 10 SG |
| Roche | Combur-10 Test M |
| ARKRAY | AUTION-Sticks 10EA |

Other brands may be added in future firmware updates. The device will refuse to test an unrecognised strip.

---

## 6. Setup

### 6.1 First-time setup

1. Place the device on a flat, dry, level surface, away from direct sunlight and heat sources.
2. Charge fully before first use (~3 h). The RGB LED is amber while charging and green when complete.
3. Power on by pressing the side button for 1 s.
4. Set date, time, and clinic name on the on-screen prompts.
5. From the menu, select **Calibrate** → **Initial Setup**. Insert the supplied ColorChecker card into the tray when prompted and follow the on-screen instructions. The device captures the card and stores the per-device calibration.
6. After successful calibration, the device returns to the main menu. Setup complete.

### 6.2 Routine calibration

Repeat the calibration step every 12 months, or:

- After any service or repair,
- If results trend out of expected ranges in QC,
- If you observe colour-related warning messages on the display.

---

## 7. Performing a Test

1. **Don gloves.** Collect a fresh urine specimen in a clean container.
2. From the main menu, select **Run Test**.
3. When prompted, scan the reagent strip vial's barcode using the rear-window scanner. Wait for the on-screen confirmation of brand, lot, and expiry.
4. Dip a single reagent strip into the urine specimen for 1 s, then briefly tap the edge against the container rim to remove excess fluid.
5. Place the strip on the tray with the reagent pads facing up, aligned with the imprinted guide marks. *[See Figure 1 — strip placement diagram.]*
6. Press the side button to start. The tray closes automatically; the indicator LED turns amber.
7. The display shows a countdown to result. Do not open the tray during this period.
8. When the reading is complete, the LED returns to green and the buzzer chirps once. Results are displayed.
9. Open the tray, dispose of the strip in a biohazard bag, and wipe the tray surface with a 70% IPA wipe.
10. The device begins a 30-s UV-C sterilisation cycle automatically. The display shows "Sterilising — do not open." Wait for the cycle to complete before the next test.

---

## 8. Reading Results

The display shows each of the 10 analytes with a semi-quantitative category. The reference ranges (per Siemens Multistix labelling) are:

| Analyte | Categories shown | Typical normal |
|---|---|---|
| Glucose | Neg, 100, 250, 500, 1000, 2000 mg/dL | Negative |
| Bilirubin | Neg, Small, Mod, Large | Negative |
| Ketones | Neg, Trace, Small, Mod, Large | Negative |
| Specific Gravity | 1.000–1.030 | 1.005–1.030 |
| Blood | Neg, Trace, Small, Mod, Large | Negative |
| pH | 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0 | 5.5–7.0 |
| Protein | Neg, Trace, 30, 100, 300, 2000 mg/dL | Negative–Trace |
| Urobilinogen | 0.2, 1, 2, 4, 8 mg/dL | 0.2–1.0 |
| Nitrite | Neg, Positive | Negative |
| Leukocytes | Neg, Trace, Small, Mod, Large | Negative |

Tap any row on the display to see a clinical-notes pop-up.

---

## 9. Quality Control

- **Frequency:** at start of each shift, after any maintenance, and after firmware update.
- **Materials:** positive and negative urinalysis control solutions (e.g., BioRad Liquichek Urinalysis Control levels 1 and 2).
- **Workflow:** Menu → **QC** → follow prompts. Results are stored in a QC log separate from patient data.
- **Failure handling:** if a QC result is out of expected range, repeat with a fresh strip. Persistent failure indicates the need for recalibration or service.

---

## 10. Cleaning and Disinfection

**Allowed agents:**
- 70% isopropyl alcohol (IPA) wipes
- Quaternary ammonium compound wipes (e.g., CaviWipes)

**Prohibited agents:**
- Sodium hypochlorite (bleach) — degrades EPDM gasket
- Acetone, methylethylketone — attacks PETG
- Hydrogen peroxide > 3% — may discolour optics
- Abrasive cleaners

**Procedure:**
- Power off the device.
- Wipe the tray with a single IPA wipe. Allow 60 s contact time.
- Wipe the external enclosure with a damp lint-free cloth, then dry.
- Do not immerse. Do not spray cleaner directly onto the device.

---

## 11. Storage and Transport

- **Storage temperature:** 5 to 40 °C
- **Storage humidity:** 10–90% RH, non-condensing
- **Operating temperature:** 15 to 35 °C
- **Operating humidity:** 20–80% RH, non-condensing
- **Shock / vibration during transport:** withstands packaged 1 m drop per ISTA 1A
- **Long-term storage:** charge the battery every 6 months to prevent deep discharge.

---

## 12. Troubleshooting

| Code | Message | Possible cause | Remedy |
|---|---|---|---|
| E-01 | Camera not detected | DVP cable loose | Power-cycle; if persistent, service |
| E-02 | Ambient light too high | Direct sunlight or open chamber | Move device; close tray; retry |
| E-03 | Strip not recognised | Barcode unreadable / unsupported brand | Use a supported strip; clean barcode window |
| E-04 | Strip expired | Use-by date passed | Use a fresh vial |
| E-05 | Battery low | Below 5% SoC | Charge before testing |
| E-06 | UV interlock open | Tray not closed or reed switch fault | Close tray; if persistent, service |
| E-07 | Storage full / SD error | SD missing or corrupt | Insert/replace SD card |
| E-08 | Calibration data invalid | Hash mismatch | Re-run calibration |
| E-09 | Heater fault | SHT31 fault or thermal cut | Power-cycle; service |
| E-10 | Stepper home miss | Limit-switch fault | Power-cycle; service |

If an error persists, contact the manufacturer (see §15).

---

## 13. Specifications

| Item | Specification |
|---|---|
| Analytes measured | 10 (glucose, protein, ketones, bilirubin, blood, pH, urobilinogen, nitrite, leukocytes, specific gravity) |
| Sample type | Human urine on commercial reagent strip |
| Accuracy claim | ≥ 90% category agreement with predicate device, **per analyte; to be confirmed in clinical V&V** |
| Repeatability | CV ≤ 10% on triplicate reads, **to be measured during V&V** |
| Time to result | ≤ 120 s |
| Throughput | Up to 30 tests per hour |
| Display | 2.4" colour TFT, 320 × 240 |
| User input | Touchscreen + 1 tactile button |
| Connectivity | USB-C (charge + data); barcode scan (UART, internal) |
| Storage | Up to 1 000 records on internal microSD |
| Battery | 3.7 V / 1000 mAh LiPo, ≥ 50 tests per charge |
| Charge | USB-C, 5 V / 1 A, ~3 h to full |
| Sterilisation | 275 nm UV-C, 30 s per cycle |
| Dimensions | 180 × 120 × 40 mm |
| Weight | ~ 350 g |
| Electrical | SELV throughout; ≤ 5 V internal |
| Operating environment | 15–35 °C, 20–80% RH non-condensing |
| Storage environment | 5–40 °C, 10–90% RH non-condensing |
| IP rating | IP22 |

*Accuracy and repeatability figures will be finalised after design verification and clinical evaluation.*

---

## 14. Disposal

The device contains electronic components and a rechargeable lithium-polymer battery, both regulated under the **E-Waste (Management) Rules, 2022** of India.

- **Before disposal,** wipe all external surfaces with 70% IPA to remove any biological residue. The tray is the only surface that contacted patient samples.
- **Do not** dispose of the device or the battery in regular municipal waste.
- Return the device to the manufacturer's take-back programme, or hand it to an authorised e-waste collector.
- Battery: do not puncture or incinerate. If swollen, place in a sand-filled metal container before transport.

---

## 15. Manufacturer and Service Contact

| | |
|---|---|
| Manufacturer | Siddhant Saboo (sole proprietor) |
| Address | [Address line 1, India — TBD] |
| Phone | [TBD] |
| Email | siddhantsaboo@gmail.com |
| Manufacturing licence number | [MD-TBD] (to be issued by State Licensing Authority) |
| Service hours | Mon–Fri, 09:00–18:00 IST |

For complaints, adverse events, or unexpected device behaviour, contact the manufacturer immediately. Adverse events involving patient harm should additionally be reported to the **Materiovigilance Programme of India** (MvPI), CDSCO.

---

## 16. Revision History

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | 2026-05-16 | Initial draft for internal review | S. Saboo |

---

*End of IFU v0.1.*
