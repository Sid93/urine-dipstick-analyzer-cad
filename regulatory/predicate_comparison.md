# PREDICATE DEVICE COMPARISON / SUBSTANTIAL EQUIVALENCE ANALYSIS
## Urine Dipstick Analyzer — Model UDA-PROTO-001

| | |
|---|---|
| **Document No.** | PRED-UDA-001 |
| **Version** | 0.1 (Draft) |
| **Date** | 2026-05-16 |
| **Purpose** | Establish substantial equivalence to legally marketed predicate devices, in support of the CDSCO Class B IVD application (and as input to any future FDA 510(k) or EU IVDR technical file). |

---

## 1. Subject Device

| Attribute | UDA-PROTO-001 |
|---|---|
| Manufacturer | Siddhant Saboo, India |
| Trade name | Urine Dipstick Analyzer |
| Model | UDA-PROTO-001 |
| Intended use | Semi-quantitative in vitro determination of 10 urinalysis analytes from commercial reagent strips |
| Analytes (10) | Glucose, Protein, Ketones, Bilirubin, Blood, pH, Urobilinogen, Nitrite, Leukocytes, Specific Gravity |
| Sample type | Human urine |
| Technology | Optical reflectance imaging with white LED illumination and OV2640 RGB CMOS camera |
| Light source | White LED array (~5500 K), PWM-controlled, diffused |
| Detector | OV2640 2 MP CMOS, 1600 × 1200 max, DVP interface |
| Algorithm | Per-pad ROI extraction → mean HSV → polynomial / lookup mapping per analyte |
| Throughput | Up to ~30 tests / hour |
| Time to result | ≤ 120 s |
| Calibration | Per-device factory + user-recalibration with ColorChecker card |
| User interface | 2.4" colour TFT touchscreen + 1 tactile button |
| Connectivity | USB-C (charge + serial export); barcode scanner internal |
| Storage | microSD up to 1 000 records |
| Power | 3.7 V / 1000 mAh LiPo; USB-C 5 V / 1 A charge |
| Sterilisation | Integrated 275 nm UV-C between tests |
| Dimensions | 180 × 120 × 40 mm |
| Weight | ~ 350 g |
| Regulatory status | **Class B IVD, CDSCO MDR 2017** (this dossier) |

---

## 2. Predicate Devices

Three legally marketed predicates are compared. All three are CDSCO-licensed and widely deployed in Indian clinical laboratories.

### 2.1 Roche Urisys 1100 (primary predicate)

| Attribute | Urisys 1100 |
|---|---|
| Manufacturer | Roche Diagnostics |
| Intended use | Semi-quantitative urinalysis (same 10 analytes) |
| Technology | Optical reflectance, single-LED + photodetector array |
| Light source | LEDs at 555 / 620 / 880 nm |
| Detector | Photodetector array (scanning) |
| Algorithm | Reflectance vs. proprietary calibration |
| Throughput | ~ 50 strips / hour |
| Time to result | 70 s per strip |
| Calibration | Self-calibrating with internal reference; auto check at startup |
| User interface | Monochrome LCD + keypad |
| Connectivity | RS-232 serial, optional thermal printer |
| Storage | ~ 100 results in memory |
| Power | Mains AC 100–240 V via external adapter (no battery) |
| Sterilisation | None integrated; manual wipe-down |
| Dimensions | 350 × 140 × 95 mm |
| Weight | ~ 1.5 kg |
| Indicative price (India, 2024) | ₹ 1.0–1.4 lakh |
| Regulatory status | CDSCO-licensed; FDA 510(k) K013316 (Roche legacy) |

### 2.2 Siemens Clinitek Status+

| Attribute | Clinitek Status+ |
|---|---|
| Manufacturer | Siemens Healthineers |
| Intended use | Semi-quantitative urinalysis (10 analytes + hCG strip option) |
| Technology | Optical reflectance; CCD reader |
| Light source | LEDs in multiple wavelengths |
| Detector | CCD line sensor |
| Throughput | ~ 50 strips / hour |
| Time to result | 60–120 s (depends on strip) |
| Calibration | Internal calibration with each strip; QC strip workflow |
| User interface | Colour touchscreen |
| Connectivity | Ethernet (Connect+ variant); barcode reader |
| Storage | ~ 950 results |
| Power | Mains AC or 6 × C-cell batteries |
| Sterilisation | None integrated |
| Dimensions | 248 × 130 × 178 mm |
| Weight | ~ 1.8 kg |
| Regulatory status | CDSCO-licensed; FDA 510(k) K081283 |

### 2.3 ARKRAY AUTION Eleven AE-4020

| Attribute | AUTION Eleven AE-4020 |
|---|---|
| Manufacturer | ARKRAY, Inc., Japan |
| Intended use | Semi-quantitative urinalysis (11 analytes including colour and turbidity) |
| Technology | Dual-wavelength reflectance + transmittance for colour/turbidity |
| Light source | LEDs at multiple wavelengths |
| Detector | Photodetector array |
| Throughput | ~ 225 strips / hour (high-throughput) |
| Time to result | 60 s |
| Calibration | Automatic with reference plate every batch |
| User interface | Colour LCD + keypad |
| Connectivity | RS-232, LIS interface |
| Storage | 520 results |
| Power | Mains AC 100–240 V |
| Sterilisation | None integrated |
| Dimensions | 348 × 339 × 257 mm |
| Weight | ~ 9.0 kg |
| Regulatory status | CDSCO-licensed; FDA 510(k) K072830 |

---

## 3. Comparison Table

| Feature | UDA-PROTO-001 (Subject) | Roche Urisys 1100 | Siemens Clinitek Status+ | ARKRAY AUTION Eleven |
|---|---|---|---|---|
| Intended use | Semi-quant urinalysis | Same | Same | Same |
| Analytes | 10 | 10 | 10 (+ hCG) | 11 (+ colour, turbidity) |
| Sample type | Human urine | Same | Same | Same |
| Technology | RGB CMOS + reflectance | LED + photodetector array, reflectance | CCD + reflectance | LED + photodetector, dual mode |
| Light source | White LED (broadband) | 3 wavelengths discrete | Multi-LED | Multi-LED |
| Detector | 2 MP CMOS (RGB) | Photodetector array | CCD line | Photodetector array |
| Throughput | ~ 30 / h | 50 / h | 50 / h | 225 / h |
| Time-to-result | ≤ 120 s | 70 s | 60–120 s | 60 s |
| Accuracy (per analyte) | Target ≥ 90% category agreement (TBD V&V) | Published 80–95% per analyte | Published 80–95% | Published 85–96% |
| Calibration | Per-device factory + user ColorChecker | Self-calibrating | Each-strip internal | Reference plate per batch |
| Connectivity | USB-C, internal barcode | RS-232, optional printer | Ethernet, barcode | RS-232, LIS |
| Display | 2.4" colour TFT touch | Mono LCD | Colour touchscreen | Colour LCD |
| Storage | 1 000 records (SD) | 100 | ~ 950 | 520 |
| Power | LiPo battery (≥ 50 tests / charge) + USB-C | Mains only | Mains or C-cells | Mains only |
| Sterilisation | Integrated UV-C 275 nm, 30 s | None | None | None |
| Form factor | 180 × 120 × 40 mm, 350 g | 350 × 140 × 95 mm, 1.5 kg | 248 × 130 × 178 mm, 1.8 kg | 348 × 339 × 257 mm, 9.0 kg |
| Indicative price | Target < ₹ 25 000 | ₹ 1.0–1.4 lakh | ₹ 1.2–1.6 lakh | ₹ 4–6 lakh |
| Regulatory status | Class B IVD (CDSCO; pending) | CDSCO-licensed; FDA 510(k) | CDSCO-licensed; FDA 510(k) | CDSCO-licensed; FDA 510(k) |

---

## 4. Differences Analysis

Substantial equivalence requires that any differences between the subject and predicate do **not raise new questions of safety or effectiveness**. Below, each material difference is examined.

### 4.1 Detector technology (CMOS RGB camera vs. photodetector array)

- **Difference:** The subject device uses a 2 MP RGB CMOS image sensor and software ROI extraction. Predicates use discrete photodetectors at fixed wavelengths.
- **Safety/effectiveness impact:** None inherent. CMOS reflectance imaging is well-established in newer analyzers (e.g., URiSCAN, mobile-app readers). The information content (per-pad colour) is the same; the implementation is digital rather than analog.
- **Mitigation:** Performance demonstrated through 60-paired-sample clinical evaluation against the Roche predicate, with acceptance criterion ≥ 90% category agreement.

### 4.2 Light source (broadband white LED vs. discrete wavelengths)

- **Difference:** Subject uses a single broadband white LED with a CPL filter; predicates use narrow-band LEDs at analyte-specific wavelengths.
- **Safety/effectiveness impact:** Broadband illumination can have lower SNR per analyte if pad chemistry is wavelength-sensitive. Mitigated by per-analyte calibration polynomials trained against the same reagent strip chemistry.
- **Additional testing:** Per-analyte SNR characterised in V&V (VER-01). LED drift monitored by white-balance card and BH1750 ambient sensor.

### 4.3 Battery operation (subject) vs. mains operation (predicates)

- **Difference:** Subject is portable, runs from LiPo.
- **Safety/effectiveness impact:** Introduces battery-related hazards (thermal runaway, fault during charge). These are addressed in the RMF (H-01, H-02, H-04) with MCP73833 charge management, MAX17048 fuel gauge, and 500 mA PTC fuse. No new clinical effectiveness question.
- **Additional testing:** Battery safety testing per UN 38.3 (already certified by the LP503562 cell vendor); device-level over-discharge / over-charge fault injection.

### 4.4 Integrated UV-C sterilisation (subject only)

- **Difference:** Subject device sterilises the tray between tests with 275 nm UV-C; predicates require manual cleaning.
- **Safety/effectiveness impact:** Introduces UV-C as a new hazard (H-05). Mitigated by reed-switch interlock that cuts the UV LED gate when the tray is open, EPDM gasket shielding, and IFU warnings.
- **Additional testing:** UV-C interlock verification (VER-05); UV leakage measurement with a calibrated radiometer; cross-contamination reduction study (VER-15, target ≥ 3 log reduction). This is a **clinical effectiveness improvement** rather than a degradation.

### 4.5 Form factor and throughput

- **Difference:** Subject is smaller, lighter, lower-throughput.
- **Safety/effectiveness impact:** None — throughput is a clinical convenience metric, not a safety issue. Smaller form-factor expands the use environment (rural clinics, mobile units) without changing the intended user or sample type.

### 4.6 Software architecture and class

- **Difference:** Subject uses modern microcontroller (ESP32-S3) running real-time firmware. IEC 62304 Class B. Predicates use embedded systems of similar class.
- **Safety/effectiveness impact:** None. Software lifecycle documented per IEC 62304 (see SDLC document).

### 4.7 Algorithm (RGB → HSV polynomial vs. proprietary reflectance equations)

- **Difference:** Subject uses RGB-to-HSV conversion with per-pad polynomial fit; predicates use proprietary reflectance equations.
- **Safety/effectiveness impact:** Same underlying physical phenomenon (colour change of reagent pad). Translation through HSV is well-documented in colorimetric literature.
- **Additional testing:** Algorithm verification on a curated panel of known-concentration samples (synthetic + clinical); clinical correlation to Roche predicate.

### 4.8 Connectivity

- **Difference:** Subject uses USB-C; predicates have RS-232 / Ethernet.
- **Safety/effectiveness impact:** None. Just a modern interface.

---

## 5. Conclusion — Substantial Equivalence Claim

The Urine Dipstick Analyzer UDA-PROTO-001 has the **same intended use, sample type, target analyte panel, and underlying scientific principle (optical reflectance colorimetry of reagent strip pads)** as the three predicate devices.

Technological differences — CMOS RGB sensing in place of discrete photodetectors, broadband white LED in place of narrow-band LEDs, battery operation, integrated UV-C — are well-understood and do not introduce new types of safety or effectiveness concerns. Each difference is supported by a specific risk control (RMF) and a specific verification test (DHF §6) or clinical study (DHF §7).

Performance is to be confirmed in a 60-paired-sample clinical evaluation against the Roche Urisys 1100 predicate, with category-agreement acceptance criteria per analyte as documented in the DHF. Subject to those V&V results being met, the Urine Dipstick Analyzer UDA-PROTO-001 is **substantially equivalent** to the predicate devices and suitable for CDSCO Class B IVD licensure under the Medical Devices Rules, 2017.

---

## 6. References

- Roche Urisys 1100 user manual and Roche Combur-Test strip insert.
- Siemens Clinitek Status+ operator manual; FDA 510(k) summary K081283.
- ARKRAY AUTION Eleven AE-4020 operator manual; FDA 510(k) summary K072830.
- CDSCO MDR 2017, Third Schedule.
- CDSCO Notice dated 23 September 2022 — Performance evaluation of IVDs.
- CLSI GP16-A3 — Urinalysis: Approved Guideline.

---

*End of predicate comparison v0.1.*
