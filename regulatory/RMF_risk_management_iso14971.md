# RISK MANAGEMENT FILE (RMF) — ISO 14971:2019
## Urine Dipstick Analyzer — Model UDA-PROTO-001

| | |
|---|---|
| **Document No.** | RMF-UDA-001 |
| **Version** | 0.1 (Draft) |
| **Date** | 2026-05-16 |
| **Author** | Siddhant Saboo, Design Lead |
| **Reviewer / Approver** | TBD — Quality Manager, TBD — Management Representative |
| **Applicable Standard** | ISO 14971:2019 (with ISO TR 24971:2020 guidance) |

---

## 1. Scope and Risk Management Plan

### 1.1 Scope

This Risk Management File covers the **Urine Dipstick Analyzer UDA-PROTO-001** throughout its entire lifecycle: design, manufacturing, distribution, clinical use, servicing, and disposal. The device is a **Class B in vitro diagnostic** intended for the semi-quantitative measurement of 10 urinalysis analytes from commercial reagent strips.

### 1.2 Risk Management Policy

The manufacturer commits to:

1. Identifying all reasonably foreseeable hazards associated with the device.
2. Estimating and evaluating the risks associated with each hazard.
3. Controlling those risks using the hierarchy of control defined in ISO 14971 §7:
   - (a) inherently safe design,
   - (b) protective measures in the device or manufacturing,
   - (c) information for safety (labelling, IFU, training).
4. Monitoring effectiveness of controls in production and post-production.
5. Maintaining an overall residual risk **As Low As Reasonably Practicable (ALARP)** and acceptable in light of the benefit to the patient.

### 1.3 Risk Acceptability Criteria

A **5 × 5 risk matrix** is used. Severity and probability are categorical scales:

| **Severity** | Description |
|---|---|
| S1 — Negligible | Minor inconvenience; no health impact |
| S2 — Minor | Temporary discomfort; resolved without intervention |
| S3 — Serious | Requires clinical intervention; reversible injury |
| S4 — Critical | Permanent impairment or significant misdiagnosis with delayed treatment |
| S5 — Catastrophic | Death or permanent disability |

| **Probability** | Description | Quantitative guide (per 10⁶ uses) |
|---|---|---|
| P1 — Improbable | Practically impossible | < 1 |
| P2 — Remote | Unlikely but possible | 1 – 100 |
| P3 — Occasional | May happen occasionally | 100 – 10 000 |
| P4 — Probable | Will happen several times in life of device | 10⁴ – 10⁶ |
| P5 — Frequent | Will happen often | > 10⁶ (i.e., routinely) |

### 1.4 Risk Acceptance Matrix

|  | **P1** | **P2** | **P3** | **P4** | **P5** |
|---|---|---|---|---|---|
| **S1** | Acc | Acc | Acc | Acc | ALARP |
| **S2** | Acc | Acc | Acc | ALARP | Unacc |
| **S3** | Acc | Acc | ALARP | Unacc | Unacc |
| **S4** | Acc | ALARP | Unacc | Unacc | Unacc |
| **S5** | ALARP | Unacc | Unacc | Unacc | Unacc |

- **Acc** = Acceptable, no further action required beyond standard documentation.
- **ALARP** = Acceptable only if risk has been reduced as low as reasonably practicable and the residual risk is justified by benefit.
- **Unacc** = Unacceptable; further risk control is mandatory.

---

## 2. Intended Use and Reasonably Foreseeable Misuse

### 2.1 Intended Use Statement

> The Urine Dipstick Analyzer UDA-PROTO-001 is a battery-operated, table-top in vitro diagnostic device intended for the **semi-quantitative measurement of 10 analytes** (glucose, protein, ketones, bilirubin, blood, pH, urobilinogen, nitrite, leukocytes, specific gravity) from **commercial reagent test strips dipped in human urine**. The device is intended for use by a clinical lab technician, general practitioner, or trained healthcare worker, in a clinic or laboratory environment, on adult and paediatric (≥ 2 years) patients. Results are intended to support — not replace — the clinician's diagnostic judgement.

### 2.2 Reasonably Foreseeable Misuse

| ID | Misuse | Mitigation strategy summary |
|---|---|---|
| MU-1 | Operator uses an expired or wrong-brand strip | Barcode scan + IFU warning |
| MU-2 | Operator reads result before recommended reaction time | Firmware enforces timer |
| MU-3 | Operator places the device in direct sunlight | BH1750 ambient light check; IFU warning |
| MU-4 | Operator drops the device into a urine specimen | IP22 rating; IFU warning |
| MU-5 | Operator opens the chamber during UV cycle | Reed-switch interlock |
| MU-6 | Patient self-tests at home using device | Out of scope; IFU "for professional use only" |
| MU-7 | Operator reuses a single-use strip | Barcode + visual recognition of wet pad |
| MU-8 | Use to test fluids other than urine | IFU contraindication; mechanical strip-only tray |
| MU-9 | Operator ignores low-battery warning, leading to mid-test power loss | RTC + storage; on-resume, the in-progress test is invalidated |

---

## 3. Characteristics Related to Safety (ISO 14971:2019 Annex C / ISO TR 24971 Annex A)

Answers to the standard's prompt questions:

| # | Question | Answer |
|---|---|---|
| C1 | Intended use, intended user, patient population | Professional use; lab tech / GP / clinic; adults and paediatric ≥ 2 yr |
| C2 | Is it intended to be implanted? | No |
| C3 | Is it intended to be in contact with the patient or other persons? | Only indirectly; operator hand contact with enclosure, no direct patient skin contact |
| C4 | Materials/components used; biocompatibility | PETG enclosure, ABS base, silicone gasket, EPDM foam, polyimide heater film. No direct patient contact; ISO 10993-1 surface-contact category not strictly required. Justification documented. |
| C5 | Energy delivered to or extracted from the patient | None directly; UV-C contained internally (Hazard H-3) |
| C6 | Substances delivered to or extracted from the patient | None |
| C7 | Biological materials processed | Urine specimen on the reagent strip (biohazard handling) |
| C8 | Sterile or microbiological state required? | Non-sterile device; tray cleaned with UV-C between uses |
| C9 | Routine measurement of the device | RTC, software self-test on boot |
| C10 | Is software used? | Yes — IEC 62304 Class B (see SDLC document) |
| C11 | Restricted shelf life | Battery (2-year nominal); UV-C LED (1000 h operational); reagent strips have own expiry |
| C12 | Are there delayed/long-term use effects? | No |
| C13 | Mechanical forces to which device is subjected | Bench drop (1 m); strip tray actuation |
| C14 | Determined by user input or affected by environmental factors? | Ambient light, temperature, humidity (compensated by sensors) |
| C15 | Critical or essential outputs | Analyte reading on display |
| C16 | Intended to be reusable? | Yes, multiple uses; reagent strip is single-use |
| C17 | Disposable components? | Reagent strip (consumable), battery (after life) |
| C18 | Installation or operator setup required? | Yes — initial calibration with ColorChecker card |
| C19 | Maintenance / calibration | Annual recalibration recommended; software OTA updates |
| C20 | Medical devices interaction? | None |
| C21 | Unintended outputs of energy or substances? | UV-C leakage if interlock fails (mitigated) |
| C22 | Susceptibility to environmental influences? | EMC: per IEC 60601-1-2 |
| C23 | Does it influence the environment? | E-waste / WEEE applicable at disposal |
| C24 | Essential performance? | Analyte reading accuracy ≥ 90% category agreement with predicate |
| C25 | Single-fault safety? | Critical safety functions (UV interlock, charger fault, thermal runaway) designed to fail safe |

---

## 4. Hazard Identification

Hazards are organised by source.

| ID | Source | Hazard | Hazardous Situation | Potential Harm |
|---|---|---|---|---|
| H-01 | Electrical | LiPo battery thermal runaway | Battery overheats, vents | Burn, fire |
| H-02 | Electrical | USB-C charger over-voltage | Excess voltage into charger IC | Component damage, fire |
| H-03 | Electrical | Mains-derived leakage current | User touches enclosure while charging | Microshock |
| H-04 | Electrical | Reverse polarity from non-compliant USB-C charger | Charger feeds reverse current | Battery damage |
| H-05 | Optical | UV-C leakage through tray gap | Operator's eye exposed | Photokeratitis, retinal injury |
| H-06 | Optical | White LED inadvertent direct view | Operator stares at LED at close range | Glare; minor; no retinal injury at this power |
| H-07 | Mechanical | Stepper-driven tray pinches finger | User holds tray while motor activates | Pinch injury |
| H-08 | Mechanical | Sharp edge on enclosure | User runs finger over un-deburred seam | Cut |
| H-09 | Mechanical | Drop hazard if pushed off bench | Device falls 1 m | Functional damage, bystander toe injury |
| H-10 | Biological | Urine contamination of operator hands | Splash during strip handling | Biological exposure |
| H-11 | Biological | Cross-contamination strip-to-strip | Previous urine residue on tray | False positive on next test |
| H-12 | Biological | Allergic reaction to enclosure plastic | Sensitised user touches PETG | Contact dermatitis |
| H-13 | Software | Incorrect analyte result due to algorithm bug | Display shows wrong value | Misdiagnosis, delayed treatment |
| H-14 | Software | Missed alert (silent failure mode) | Device unable to read but reports OK | Misdiagnosis |
| H-15 | Software | Calibration data corruption | Bad coefficients applied | All results biased |
| H-16 | Software | Firmware update bricks device | OTA failure | Loss of use; not safety-critical |
| H-17 | Software | Data integrity loss | SD corruption loses patient records | Audit failure |
| H-18 | Use-error | Wrong strip brand inserted | Calibration mismatch | Wrong result |
| H-19 | Use-error | Expired strip used | Reagent degraded | Wrong result |
| H-20 | Use-error | Wet/moist hands contact charger port | Splash into USB | Charger fault |
| H-21 | Use-error | Operator places device in direct sunlight | Image saturation | Wrong result |
| H-22 | Use-error | Operator obscures ambient sensor | BH1750 reading false-low | Wrong result |
| H-23 | Environmental | High humidity causes condensation in chamber | Optics fogged | Wrong result |
| H-24 | Environmental | EMC: radio (e.g., cellphone) corrupts I2C | Sensor read fails | Error or wrong result |
| H-25 | Environmental | Temperature out-of-range (cold storage) | Battery + plastics out of spec | Functional failure |
| H-26 | Environmental | Strong static discharge from operator | ESD into button or USB port | Component damage |
| H-27 | Disposal | LiPo cell discarded in regular waste | Cell punctured at landfill | Environmental fire |
| H-28 | Service | Operator opens enclosure | Exposes battery and high-current rails | Burn / shock |

---

## 5. Risk Estimation (Pre-Control)

| ID | Severity | Probability | Score (S×P) | Pre-Control Acceptability |
|---|---|---|---|---|
| H-01 | S4 | P3 | 12 | Unacc |
| H-02 | S3 | P3 | 9 | ALARP |
| H-03 | S3 | P2 | 6 | Acc |
| H-04 | S2 | P3 | 6 | Acc |
| H-05 | S4 | P3 | 12 | Unacc |
| H-06 | S2 | P3 | 6 | Acc |
| H-07 | S2 | P3 | 6 | Acc |
| H-08 | S2 | P2 | 4 | Acc |
| H-09 | S2 | P3 | 6 | Acc |
| H-10 | S3 | P4 | 12 | Unacc |
| H-11 | S4 | P4 | 16 | Unacc |
| H-12 | S2 | P2 | 4 | Acc |
| H-13 | S4 | P3 | 12 | Unacc |
| H-14 | S4 | P3 | 12 | Unacc |
| H-15 | S4 | P2 | 8 | ALARP |
| H-16 | S1 | P3 | 3 | Acc |
| H-17 | S2 | P3 | 6 | Acc |
| H-18 | S3 | P4 | 12 | Unacc |
| H-19 | S3 | P4 | 12 | Unacc |
| H-20 | S2 | P3 | 6 | Acc |
| H-21 | S3 | P3 | 9 | ALARP |
| H-22 | S3 | P3 | 9 | ALARP |
| H-23 | S3 | P3 | 9 | ALARP |
| H-24 | S3 | P3 | 9 | ALARP |
| H-25 | S2 | P3 | 6 | Acc |
| H-26 | S2 | P3 | 6 | Acc |
| H-27 | S2 | P3 | 6 | Acc |
| H-28 | S3 | P2 | 6 | Acc |

---

## 6. Risk Control Measures

Every **Unacceptable** and **ALARP** risk is reduced. For each, the control type (per ISO 14971 §7.1) and residual estimate are recorded. Verification refers to V&V tests in the DHF.

| ID | Control Type | Control Measure | Post-Control S × P | Verification |
|---|---|---|---|---|
| H-01 | (a) Inherent + (b) Protective | LiPo cell with internal PTC + MAX17048 fuel gauge + MCP73833 charger with thermal regulation; PCB-level 500 mA PTC fuse; enclosure ventilation; firmware monitors SHT31 chamber temp and shuts down ≥ 60 °C | S4 × P1 = 4 (Acc) | UN 38.3, cell datasheet; bench short-circuit test |
| H-02 | (a) Inherent | MCP73833 supports up to 7 V input absolute max; USB-C breakout exposes only 5 V; PCB-level TVS diode | S3 × P1 = 3 (Acc) | Over-voltage injection test up to 9 V |
| H-03 | (b) Protective | Plastic enclosure; only SELV inside; isolation by USB-C-rated wall adapter (user-supplied) | S3 × P1 = 3 (Acc) | IEC 61010-1 dielectric test |
| H-04 | (a) Inherent | USB-C polarity by design; charger IC has reverse-blocking | S2 × P1 = 2 (Acc) | Reverse-polarity injection |
| H-05 | (b) Protective + (c) Info | (i) MC-38 reed-switch + IRLZ44N MOSFET in **series with UV-C LED supply** — opening the tray opens the gate; (ii) EPDM foam gasket at tray seam; (iii) UV-on indicator on display + buzzer; (iv) IFU UV warning | S4 × P1 = 4 (Acc) | VER-05 with UV-C radiometer; firmware FMEA on interlock |
| H-06 | (c) Info | IFU warns not to stare at LED during reading | S2 × P2 = 4 (Acc) | IFU review |
| H-07 | (a) Inherent + (c) Info | NEMA17 20 mm body provides limited torque (0.13 Nm); tray gap < 3 mm closed → finger cannot enter; IFU warning | S2 × P1 = 2 (Acc) | Mechanical pinch-gap test |
| H-08 | (a) Inherent | Enclosure design: all external edges ≥ 1 mm radius; injection-mould inspection | S2 × P1 = 2 (Acc) | First-article inspection |
| H-09 | (b) Protective | 1 m drop survival design; rubber feet | S2 × P2 = 4 (Acc) | VER-07 |
| H-10 | (c) Info + (b) Protective | IFU mandates gloves; tray catches drips into removable channel; IPA 70% wipe-down between tests | S3 × P2 = 6 (Acc) | IFU review; tray cleanability test |
| H-11 | (b) Protective + (a) Inherent | UV-C 30-s sterilisation between tests + non-porous PETG tray + IFU 70% IPA wipe; firmware enforces UV before next strip allowed | S4 × P2 = 8 (ALARP) — justified by benefit; further reduction not practicable without disposable tray | VER-15 (≥ 3-log reduction) |
| H-12 | (a) Inherent + (c) Info | PETG and ABS are widely-used skin-contact-safe plastics; IFU lists materials so sensitised users can opt out | S2 × P1 = 2 (Acc) | Material certificate; ISO 10993-1 surface category justification |
| H-13 | (b) Protective | IEC 62304 Class B software lifecycle; code review; unit tests; algorithm validation against ColorChecker; clinical validation 60 paired samples | S4 × P1 = 4 (Acc) | VER-12, VER-13; clinical report |
| H-14 | (b) Protective | Software watchdog timer; per-step health checks; if any sensor fails firmware shows error and refuses to display result | S4 × P1 = 4 (Acc) | Fault-injection test |
| H-15 | (b) Protective | Calibration file stored with SHA-256 hash; firmware refuses to operate on mismatch | S4 × P1 = 4 (Acc) | Cal-corruption injection test |
| H-16 | (b) Protective | A/B firmware partitions with rollback; OTA failure reverts to last-known-good | S1 × P2 = 2 (Acc) | OTA fault-injection test |
| H-17 | (b) Protective | Wear-levelled writes; CRC32 per record; periodic flush | S2 × P2 = 4 (Acc) | SD pull-during-write test |
| H-18 | (b) Protective + (c) Info | GM65 barcode scanner reads strip vial label; firmware whitelists supported brands; warns operator if unknown | S3 × P2 = 6 (Acc) | Unknown-strip simulation |
| H-19 | (b) Protective + (c) Info | Barcode includes expiry date; firmware refuses to read expired strip; IFU warning | S3 × P1 = 3 (Acc) | Expired-strip simulation |
| H-20 | (c) Info | IFU instructs dry hands and dry surfaces around USB port | S2 × P2 = 4 (Acc) | IFU review |
| H-21 | (b) Protective | BH1750 ambient sensor; firmware blocks reading if > 5 lux ambient at imaging position; IFU warns about direct sunlight | S3 × P1 = 3 (Acc) | VER-01 varied lighting |
| H-22 | (b) Protective | BH1750 placed where the user is unlikely to cover it; firmware sanity-checks reading; tray geometry shields sensor | S3 × P2 = 6 (Acc) | Obstruction test |
| H-23 | (b) Protective + (c) Info | SHT31 detects RH > 80%; firmware warns; chamber fan + heater raise dewpoint margin; IFU storage RH 20–80% | S3 × P2 = 6 (Acc) | Environmental chamber |
| H-24 | (b) Protective | IEC 60601-1-2 ed.4 EMC testing; I2C with pull-ups and shielded cable; firmware retries on CRC error | S3 × P2 = 6 (Acc) | VER-09 |
| H-25 | (c) Info | IFU storage spec 5–40 °C; operate 15–35 °C; firmware refuses to operate below 10 °C | S2 × P1 = 2 (Acc) | Cold-start test |
| H-26 | (b) Protective | ESD diodes at USB port and exposed button; PCB has ground plane | S2 × P1 = 2 (Acc) | IEC 61000-4-2 air/contact discharge |
| H-27 | (c) Info | IFU + label: WEEE crossed-bin symbol; instructions to return cell to authorised e-waste vendor | S2 × P1 = 2 (Acc) | Label inspection |
| H-28 | (c) Info + (a) Inherent | Enclosure secured with M3 inserts requiring tool; service-only access labelled inside; no user-replaceable parts | S3 × P1 = 3 (Acc) | Label inspection |

---

## 7. Risk-Benefit Analysis (for ALARP-residual items)

**H-11 (cross-contamination):** Residual risk S4 × P2 = 8 (ALARP). Further reduction would require a single-use disposable tray, which would significantly increase per-test cost (≈ ₹40/test) and waste, contrary to the device's value proposition for low-resource settings. The 30-second 275 nm UV-C cycle is documented in literature to provide ≥ 3-log microbial reduction on non-porous surfaces. The IFU additionally mandates 70% IPA wipe between tests. Benefit (point-of-care urinalysis access in primary care, where the predicate Roche Urisys 1100 at ₹1.2 lakh is unaffordable) substantially outweighs the residual risk. **Accepted.**

---

## 8. Overall Residual Risk Evaluation

After applying the controls in §6, **no individual residual risk falls in the Unacceptable zone**. One residual risk (H-11) is in ALARP and is justified by the risk-benefit narrative above. All other residuals are Acceptable.

**Conclusion:** The overall residual risk of UDA-PROTO-001 is judged **acceptable** in relation to the benefits of providing rapid, low-cost semi-quantitative urinalysis to primary care.

---

## 9. Production and Post-Production Information

### 9.1 Production Controls

- Incoming inspection of safety-critical components (LiPo cell, UV-C LED, charger IC, MOSFETs) per defined sampling plan.
- 100% functional test at end-of-line: (a) UV interlock; (b) battery charge cycle; (c) full strip-read calibration check.
- Lot-by-lot retention sample.

### 9.2 Post-Production Surveillance

- **Complaint handling:** SOP-PMS-001. All complaints logged within 24 h; investigated and trended monthly.
- **Vigilance reporting** per MDR-2017 Rule 89: serious adverse events to CDSCO within 15 days, others within 30 days.
- **Periodic review:** RMF reviewed annually and after any of: (i) post-market complaint trend, (ii) design change, (iii) new standard release, (iv) field safety corrective action.
- **Inputs to review:** complaints, returns, social-media monitoring, literature scan, supplier change notices, SOUP CVE feeds.

---

## 10. References

- ISO 14971:2019 — Application of risk management to medical devices.
- ISO/TR 24971:2020 — Guidance on the application of ISO 14971.
- IEC 62366-1:2015 — Usability engineering.
- CDSCO MDR 2017, Rule 89 (Post-market surveillance) and Schedule G (label content).
- *Urine reagent strip cross-contamination and UV-C decontamination* — internal literature review (TBD).

---

*End of RMF v0.1. Next revision at DR-3.*
