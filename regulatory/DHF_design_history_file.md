# DESIGN HISTORY FILE (DHF)
## Urine Dipstick Analyzer — Model UDA-PROTO-001

| | |
|---|---|
| **Device Name** | Urine Dipstick Analyzer |
| **Model / Catalog No.** | UDA-PROTO-001 |
| **Classification** | Class B IVD (CDSCO MDR 2017, Third Schedule, Rule 3) |
| **Software Safety Class** | Class B (IEC 62304) |
| **Document No.** | DHF-UDA-001 |
| **Version** | 0.1 (Draft) |
| **Issue Date** | 2026-05-16 |
| **Manufacturer** | Siddhant Saboo (sole proprietor); license number TBD |
| **Manufacturing Site** | India (city TBD) |
| **Prepared by** | Siddhant Saboo, Design Lead |
| **Reviewed by** | TBD — Quality Manager (signature placeholder) |
| **Approved by** | TBD — Management Representative (signature placeholder) |

---

## 1. Purpose and Scope

This Design History File (DHF) records the design and development activities of the Urine Dipstick Analyzer (UDA-PROTO-001) in accordance with **ISO 13485:2016 clause 7.3 (Design and Development)** and the **Medical Devices Rules, 2017 (CDSCO)**. It is the master index to all design records — design inputs, outputs, reviews, verifications, validations, and changes — for the life of the device.

The DHF is a **living document**. As the device progresses from prototype to commercialised product, new evidence (test reports, review minutes, change orders) is added under controlled revision.

## 2. Design and Development Planning

### 2.1 Phases and Gate Reviews

The development of UDA-PROTO-001 follows a V-model with five gated phases. Each gate is a formal Design Review (DR-#) chaired by the Design Lead with mandatory attendance of Quality and Regulatory.

| Phase | Name | Key Activities | Output(s) | Gate |
|---|---|---|---|---|
| 0 | Concept | Market research; user persona; predicate landscape | Concept brief | DR-1 |
| 1 | Feasibility | Optical bench experiments; reagent strip compatibility study; component down-select | Feasibility report; risk-management plan v0.1 | DR-2 |
| 2 | Design | Schematic, PCB, mechanical CAD, firmware architecture, RMF, SRS | Design output dossier | DR-3 |
| 3 | Verification & Validation | Bench V&V; usability formative; pilot clinical | V&V protocols and reports; clinical evaluation report | DR-4 |
| 4 | Design Transfer | IQ/OQ/PQ; supplier qualification; pilot build | Master Device Record (MDR); manufacturing instructions | DR-5 |
| 5 | Post-Market | Surveillance, vigilance, periodic safety update | PSUR; complaint reports | n/a |

### 2.2 Roles and Responsibilities

| Role | Responsibility |
|---|---|
| Design Lead (S. Saboo) | Overall design authority; signs off design outputs |
| Software Lead | IEC 62304 deliverables, code review, SBOM |
| Quality Manager (TBD) | ISO 13485 conformance, design review minutes, CAPA |
| Regulatory Affairs (TBD) | CDSCO submission, BIS test coordination |
| Clinical Investigator (TBD) | Performance evaluation per CDSCO Sept 2022 notice |
| Manufacturing Lead (TBD) | Design transfer, supplier audits |

### 2.3 Planned Outputs per Gate

- **DR-1:** Concept brief; preliminary intended-use statement.
- **DR-2:** Feasibility report; predicate comparison v0; risk-management plan.
- **DR-3:** Frozen schematic (`urine_dipstick_analyzer.kicad_sch`), PCB (`*.kicad_pcb`), BOM (`BOM.csv`), firmware repository tag, mechanical CAD (`*.step`), IFU draft, label artwork draft, RMF, SRS, traceability matrix.
- **DR-4:** All verification reports; validation summary; clinical report; usability validation report.
- **DR-5:** Approved master records; IQ/OQ/PQ reports; first-article inspection; design transfer certificate.

## 3. Design Inputs

### 3.1 User Needs (UN-###)

Compiled from interviews with primary-care physicians, lab technicians, and a literature scan of point-of-care urinalysis workflows.

| ID | User Need |
|---|---|
| UN-001 | Device shall read a 10-pad commercial urine dipstick and report semi-quantitative results for glucose, protein, ketones, bilirubin, blood, pH, urobilinogen, nitrite, leukocytes, and specific gravity. |
| UN-002 | Time-to-result ≤ 120 seconds from strip insertion to display. |
| UN-003 | Operable by a clinical lab technician with no specialised training beyond reading the IFU. |
| UN-004 | Runs on internal rechargeable battery for ≥ 50 tests per charge. |
| UN-005 | Charges via USB-C from a standard 5 V / 1 A source. |
| UN-006 | Tolerates indoor lighting (offices, clinics, 200–1000 lux ambient). |
| UN-007 | Operates between 15 °C and 35 °C ambient. |
| UN-008 | Operates between 20% and 80% non-condensing relative humidity. |
| UN-009 | Compatible with at least three commercial reagent strip brands (Multistix, Combur-10, AUTION-Sticks). |
| UN-010 | Displays results on an integrated colour screen ≥ 2 inches. |
| UN-011 | Allows the operator to scan a patient or sample barcode and associate results with the ID. |
| UN-012 | Stores at least 1 000 historical records on internal SD card. |
| UN-013 | Exports records as CSV or JSON over USB. |
| UN-014 | Provides audible and visual alerts for completion, low battery, and errors. |
| UN-015 | Sterilises the strip tray between tests to prevent cross-contamination. |
| UN-016 | Prevents UV-C emission whenever the tray is open. |
| UN-017 | Allows the operator to recalibrate using a ColorChecker reference card without opening the enclosure. |
| UN-018 | Provides a Quality Control (QC) workflow with positive and negative control strips. |
| UN-019 | Indicates expired or incompatible strips before reading. |
| UN-020 | Retains time/date through power loss (RTC backup). |
| UN-021 | Survives a 1 m drop onto vinyl flooring without functional loss. |
| UN-022 | Cleanable with isopropyl alcohol 70% and quaternary ammonium wipes. |
| UN-023 | All patient-contacting surfaces (tray) are non-porous and disinfectable. |
| UN-024 | Audit-trail captures operator ID, timestamp, lot of reagent strip, and raw result. |

### 3.2 Regulatory and Standards Inputs

| Input | Source | Applicability |
|---|---|---|
| Medical Devices Rules, 2017 (MDR-2017) | CDSCO, India | Class B IVD; Form MD-3 manufacturing licence |
| ISO 13485:2016 | International | Quality Management System |
| ISO 14971:2019 | International | Risk management |
| IEC 62304:2006 / A1:2015 | International | Software lifecycle (Class B) |
| IEC 61010-1:2010+A1:2019 | International / BIS adoption | General safety, electrical equipment for laboratory use |
| IEC 61010-2-101:2018 | International | Particular requirements for IVD medical equipment |
| IEC 62366-1:2015 | International | Usability engineering |
| IEC 60601-1-2:2014 (4th ed.) | International | EMC for medical electrical equipment |
| ISO 15223-1:2021 | International | Symbols for medical device labels |
| CLSI GP16-A3 | CLSI (USA) | Urinalysis good practice guideline |
| ISO 10993-1:2018 | International | Biocompatibility (surface contact, brief duration) |
| WEEE / E-Waste (Management) Rules 2022 | MoEF&CC, India | End-of-life disposal of electronics |
| AERB GSR Part-3 | AERB India | (Non-applicable — no ionising radiation; UV-C only) |

### 3.3 Performance Inputs (Targets)

Derived from predicate device performance and intended-use claims. Acceptance is established at design verification. These numbers are **engineering targets**; final accuracy claims will be set after V&V data.

| Parameter | Target |
|---|---|
| Glucose | ≥ 90% agreement with predicate at each semi-quantitative level (Neg, Trace, 1+, 2+, 3+, 4+) |
| Protein | ≥ 90% agreement |
| Ketones | ≥ 90% agreement |
| Bilirubin | ≥ 85% agreement (typically the noisiest pad) |
| Blood | ≥ 90% agreement |
| pH | ± 0.5 units vs. predicate |
| Urobilinogen | ≥ 85% agreement |
| Nitrite | ≥ 95% qualitative agreement |
| Leukocytes | ≥ 90% agreement |
| Specific Gravity | ± 0.005 vs. predicate |
| Time-to-result | ≤ 120 s after strip insertion |
| Repeatability | CV ≤ 10% on triplicate reads of the same dry strip |
| Battery life | ≥ 50 measurements per full charge |
| Charge time | ≤ 3 h from 0% to 100% |
| IP rating | IP22 (vertical drip protection for spill resistance) |

## 4. Design Outputs

The design outputs frozen at DR-3 are version-controlled in the repository at `/Users/siddhantsaboo/Desktop/agentic workflows/urine_dipstick_cad/`:

| Output | File(s) | Status |
|---|---|---|
| Schematic | `urine_dipstick_analyzer.kicad_sch`, `schematic_render.png` | Draft — 252 ERC violations to be cleared before freeze (see STATUS.md) |
| PCB layout | `urine_dipstick_analyzer.kicad_pcb` | Draft — 75 DRC violations, 51 unrouted nets |
| Gerbers | `gerbers.zip` | NOT manufacturable; placeholder |
| BOM | `BOM.csv`, `BOM.pdf` | Complete, 111 parts, real MPNs |
| Mechanical CAD | `*.step`, `*.stl` (enclosure, tray, mounts) | Complete |
| 2D drawings | `drawings/*.pdf` | Complete (7 sheets) |
| Firmware source | `firmware/urine_dipstick_analyzer/` | Compiles; integration of UV/heater/PID still pending |
| Calibration data | `calibration.json` | Schema valid; placeholder coefficients |
| IFU | `regulatory/IFU_instructions_for_use.md` | This dossier |
| Label artwork | `regulatory/label_artwork.md` | This dossier |
| Risk Management File | `regulatory/RMF_risk_management_iso14971.md` | This dossier |

## 5. Design Reviews

| DR # | Phase Gate | Planned Date | Attendees (target) | Output |
|---|---|---|---|---|
| DR-1 | Concept | 2025-09-15 (held informally) | Design Lead | Concept brief approved |
| DR-2 | Feasibility | 2026-01-20 (held informally) | Design Lead | Predicate comparison v0; component down-select |
| DR-3 | Design Freeze | TBD (target 2026-08-01) | Design Lead, Quality Mgr, Reg Affairs, Software Lead | Sign-off on schematic/PCB/firmware/IFU/RMF |
| DR-4 | Pre-V&V | TBD (target 2026-11-01) | All above + Clinical Investigator | Sign-off on V&V protocols and clinical plan |
| DR-5 | Pre-Transfer | TBD (target 2027-03-01) | All above + Manufacturing Lead | Approve design transfer to manufacturing |

Each review will produce minutes recording: items reviewed, findings, action items with owner and due date, and a sign-off on whether to proceed to the next phase. Minutes are stored under `regulatory/design_reviews/DR-#_minutes.pdf`.

## 6. Design Verification

Verification answers "did we build the device right?" — i.e., do the design outputs meet the design inputs? Each input ID (UN-### and performance target) is verified through one or more tests.

### Planned Verification Activities

| Test ID | Scope | Method | Acceptance |
|---|---|---|---|
| VER-01 | Strip image capture quality | Capture 50 strip images; measure pad ROI SNR | SNR ≥ 30 dB per pad |
| VER-02 | LED intensity stability | Log white-LED output over 1 h | ≤ 2% drift |
| VER-03 | Stepper repeatability | Move strip 100 times to imaging position, measure with dial gauge | ≤ 0.2 mm RMS deviation |
| VER-04 | Heater PID overshoot | Step setpoint 25 → 30 °C, log SHT31 | ≤ 1 °C overshoot, ≤ 60 s settle |
| VER-05 | UV-C interlock | Open tray during UV cycle; measure UV-C with radiometer | UV-C off within 100 ms |
| VER-06 | Battery life | Run 100 simulated cycles | ≥ 50 measurements per charge |
| VER-07 | Drop test | 1 m drop, six faces, vinyl floor | No functional loss |
| VER-08 | IP22 | Dip simulation per IEC 60529 | Pass IP22 |
| VER-09 | EMC immunity & emissions | External BIS lab | IEC 60601-1-2 ed.4 |
| VER-10 | Electrical safety | External BIS lab | IEC 61010-1, IEC 61010-2-101 |
| VER-11 | Time-to-result | Stopwatch, 30 strips | ≤ 120 s |
| VER-12 | Software unit tests | per IEC 62304 §5.5 | 100% pass on Class B critical units |
| VER-13 | Software system test | Black-box per IEC 62304 §5.7 | 100% pass on system requirements |
| VER-14 | Calibration repeatability | 10 ColorChecker captures | ΔE ≤ 3.0 between runs |
| VER-15 | Cross-contamination | UV cycle effectiveness study, RLU swab pre/post | ≥ 3 log reduction |

Verification reports are filed under `regulatory/verification/VER-##.pdf`.

## 7. Design Validation

Validation answers "did we build the right device?" — i.e., does the finished device meet the user needs in the actual use environment?

### Clinical Evaluation Plan (Summary)

| Item | Description |
|---|---|
| Objective | Demonstrate substantial equivalence in semi-quantitative analyte readings between UDA-PROTO-001 and Roche Urisys 1100 (predicate) |
| Site | One pathology lab in India (TBD) |
| Investigator | TBD |
| Sample size | 60 paired urine samples (rationale: detect ≥80% agreement at α=0.05, power 0.80) |
| Reagent strip | Roche Combur-10 (CDSCO-approved) |
| Ethics approval | Institutional Ethics Committee (IEC) approval required before enrolment |
| Acceptance | ≥ 90% category agreement for 7/10 analytes; ≥ 85% for bilirubin and urobilinogen; ± 0.5 pH; ± 0.005 SG |
| Sub-study | Inter-device variability across 3 production units of UDA-PROTO-001 |

### Usability Validation (IEC 62366-1)

A formative usability study with 5 representative users (lab tech, GP, nurse) using the IFU and prototype. Tasks: (a) unpack and set up, (b) charge, (c) calibrate, (d) run a test, (e) interpret results, (f) export data. Findings drive IFU revisions before summative validation.

## 8. Design Transfer

Design transfer occurs at DR-5 and includes:

- **Master Device Record (MDR):** consolidated drawings, BOM, software image, firmware OTA package, test specifications.
- **Manufacturing Process Instructions (MPI):** PCBA assembly, mechanical assembly, factory calibration with ColorChecker, functional test station design.
- **Supplier Qualification:**
  - Tier-1 critical: OV2640 camera, ESP32-S3, LiPo cell, UV-C LED. Each supplier subjected to supplier audit and incoming inspection plan.
  - Tier-2: passives, connectors. Inspected on lot-acceptance basis.
- **IQ/OQ/PQ Plan:**
  - **IQ (Installation Qualification):** verify factory assembly fixtures, test jigs, calibration cards.
  - **OQ (Operational Qualification):** run 3 pilot lots (10 units each) and demonstrate process capability Cpk ≥ 1.33.
  - **PQ (Performance Qualification):** 30-unit pilot lot tested against full V&V protocol with no deviations.
- **Training records** for production operators.

## 9. Design Changes

A change control SOP (`SOP-CC-001`) governs all post-freeze changes. Workflow:

1. Change request raised in change-control register with rationale.
2. Impact assessment: design inputs/outputs affected, risk-management impact, regulatory impact (does it require re-submission?).
3. Approval by Design Lead, Quality Manager, and (for risk-relevant changes) Regulatory Affairs.
4. Implementation in version-controlled outputs.
5. Re-verification and re-validation as appropriate.
6. Closure with updated traceability matrix.

Software changes additionally follow IEC 62304 §6 (Software Maintenance Process).

## 10. Post-Market Surveillance

Per **MDR-2017 Rule 89** (Post-market surveillance):

- Complaint-handling SOP (`SOP-PMS-001`) — all complaints logged, investigated, trended.
- Periodic Safety Update Reports (PSUR) annually for the first three years, then per CDSCO direction.
- Vigilance reporting: serious adverse events to CDSCO within 15 days; non-serious within 30 days.
- Field Safety Corrective Actions (FSCA) executed as required.

## 11. Traceability Matrix

Cross-reference from user need → design input → design output → verification → validation. (Abridged: top 20 needs.)

| UN | Input/Spec | Output (file) | Verification | Validation |
|---|---|---|---|---|
| UN-001 | 10-pad reading | Firmware `analysis.h`, calibration.json | VER-01, VER-14 | Clinical 60-sample |
| UN-002 | ≤120 s | Firmware main loop timing | VER-11 | Usability formative |
| UN-003 | Tech user | IFU §6, §7 | n/a | Usability summative |
| UN-004 | ≥50 tests/charge | MAX17048 fuel-gauge integration | VER-06 | Field test |
| UN-005 | USB-C 5V/1A | MCP73833 charger; BOM | Charge time bench | n/a |
| UN-006 | 200–1000 lux | BH1750 ambient compensation | VER-01 (varied lighting) | Clinical site lighting |
| UN-007 | 15–35 °C | SHT31 monitoring; heater | Environmental chamber test | n/a |
| UN-008 | 20–80% RH | SHT31 logging | Environmental chamber | n/a |
| UN-009 | 3 strip brands | Calibration tables × 3 | VER-01 per brand | Clinical sub-study |
| UN-010 | 2" colour screen | ILI9341 display | Display readability test | Usability |
| UN-011 | Barcode scan | GM65 module + firmware | Scan-rate test, 100 barcodes | Usability |
| UN-012 | 1000 records | SD storage, JSON log | Storage stress test | n/a |
| UN-013 | CSV/JSON export | Serial/USB export module | Round-trip parse test | Usability |
| UN-014 | Audible/visual alerts | Buzzer + RGB LED | Acoustic/visual bench check | Usability |
| UN-015 | UV sterilisation | UV-C LED + cycle in firmware | VER-15 (3-log reduction) | n/a |
| UN-016 | UV interlock | Reed switch + MOSFET gate | VER-05 | n/a |
| UN-017 | Recalibration | Calibration mode in firmware | VER-14 | Usability |
| UN-018 | QC workflow | QC mode in firmware | QC strip read test | Clinical sub-study |
| UN-019 | Expired strip detection | Barcode + RTC check | Expired-strip simulation | Usability |
| UN-020 | RTC backup | DS3231 + CR2032 | Power-loss test | n/a |
| UN-021 | 1 m drop | Enclosure design | VER-07 | n/a |
| UN-022 | Disinfectable | Material selection (PETG/ABS), no porous surfaces | Chemical compatibility test (IPA 70%, quat-amm) | n/a |
| UN-023 | Non-porous patient contact | Tray PETG | Visual + ISO 10993 surface category justification | n/a |
| UN-024 | Audit trail | Storage module + RTC | Log integrity test | Site auditor review |

The full machine-readable traceability matrix lives in `regulatory/traceability_matrix.xlsx` (TBD).

## 12. References

- ISO 13485:2016 — Medical devices — Quality management systems.
- ISO 14971:2019 — Medical devices — Application of risk management.
- IEC 62304:2006/A1:2015 — Medical device software — software lifecycle processes.
- IEC 61010-1:2010+A1:2019 / IEC 61010-2-101:2018.
- IEC 62366-1:2015 — Application of usability engineering.
- CDSCO, Medical Devices Rules, 2017 and subsequent amendments.
- CDSCO Notice dated 23 September 2022, *Performance evaluation of in-vitro diagnostic medical devices*.

---

*End of DHF v0.1. Next revision after DR-3 with frozen design outputs.*
