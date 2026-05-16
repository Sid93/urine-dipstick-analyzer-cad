# CDSCO MDR 2017 Class B Regulatory Dossier — Index

**Device:** Urine Dipstick Analyzer (UDA-PROTO-001)
**Manufacturer:** Siddhant Saboo (sole proprietor) — license number TBD
**Document set version:** 0.1 (Draft for internal review)
**Date:** 2026-05-16
**Status:** Prototype dossier; not yet submitted to CDSCO

---

## 1. Document Index

| # | File | Title | Purpose |
|---|---|---|---|
| 1 | `DHF_design_history_file.md` | Design History File | Evidence of design control per ISO 13485 §7.3 and CDSCO MDR 2017 |
| 2 | `RMF_risk_management_iso14971.md` | Risk Management File | ISO 14971:2019-compliant hazard and risk analysis |
| 3 | `SDLC_iec62304.md` | Software Lifecycle File | IEC 62304 Class B software documentation |
| 4 | `IFU_instructions_for_use.md` | Instructions for Use | End-user IFU per ISO 15223-1 / EN 1041 / IS 14971 |
| 5 | `label_artwork.md` | Label and Carton Artwork | Schedule G label content per CDSCO MDR 2017 |
| 6 | `predicate_comparison.md` | Substantial Equivalence Analysis | Predicate device comparison (Roche, Siemens, ARKRAY) |
| 7 | `00_README.md` | This file | Index and regulatory roadmap |

---

## 2. CDSCO MDR 2017 Classification Rationale

Per the **Medical Devices Rules, 2017**, the Urine Dipstick Analyzer is an **in vitro diagnostic medical device (IVD)**. Classification follows the **First Schedule, Part II** (IVD classification rules) and the **Third Schedule** (risk classes):

- **Rule 3 (Class B IVD):** Devices intended for use in the management of patients suffering from a disease or other medical condition where an erroneous result would not place the patient in immediate danger but would lead to an inappropriate or delayed treatment decision.
- Urinalysis is a **screening test for routine analytes** (glucose, protein, ketones, pH, etc.) — none of which are immediate life-threatening single-result determinants (contrast: blood glucose for diabetic emergency = Class C, blood gas = Class D).
- **Conclusion: Class B IVD.**

## 3. Application Route

| Form | Purpose | Authority |
|---|---|---|
| **Form MD-3** | Application for license to manufacture Class A or B medical device for sale or distribution | State Licensing Authority (FDCA Maharashtra/Karnataka/etc.) |
| **Form MD-4** | Issuance of manufacturing license | State Licensing Authority |
| **Form MD-13** | Loan license (if contract-manufacturing) | State Licensing Authority |
| **Form MD-14** | Import license (only if any sub-assembly imported as finished IVD) | CDSCO Central Licensing Authority |

For Class B IVD manufactured in India, the route is **direct application to the State Licensing Authority** (no Notified Body required, unlike EU IVDR).

## 4. Estimated Timeline and Cost

| Phase | Duration | Cost (INR, indicative) |
|---|---|---|
| Quality Management System setup (ISO 13485) | 4–6 months | 8–15 lakh |
| Design V&V completion | 3–4 months | 5–10 lakh |
| BIS / NABL testing (IEC 61010-1, 61010-2-101, 60601-1-2 EMC) | 2–3 months | 4–7 lakh |
| Clinical evaluation (60 paired samples vs. predicate) | 3 months | 3–5 lakh |
| Dossier compilation and submission (MD-3) | 1 month | 1–2 lakh |
| CDSCO/State LA review and audit | 6–9 months | 50,000 (govt fee) |
| **Total to manufacturing license** | **18–24 months** | **22–40 lakh** |

## 5. Clinical Evaluation Requirement

Per **CDSCO Notice dated 23 September 2022** ("Performance evaluation of in-vitro diagnostic medical devices"):
- Class B IVDs require analytical and clinical performance evaluation.
- Minimum **40 patient samples** for screening IVDs; this dossier targets **60 samples** to strengthen the dataset.
- Comparison against a **legally marketed predicate** (Roche Urisys 1100, CDSCO-licensed) is acceptable as the reference method.
- Performance evaluation must be conducted at a CDSCO-recognised lab or an ICMR-approved investigator site under an Ethics Committee approval.

## 6. BIS / Third-Party Testing Required

| Standard | Scope | Lab |
|---|---|---|
| **IS/IEC 61010-1** | General safety of electrical equipment for measurement, control, laboratory use | NABL-accredited (e.g., CMET, ERTL, SGS India) |
| **IS/IEC 61010-2-101** | Particular requirements for in vitro diagnostic (IVD) medical equipment | Same |
| **IS/IEC 60601-1-2** (4th edition) | EMC for medical electrical equipment | TÜV Süd / UL India |
| **IS 13252 / IEC 62133** | Battery safety (LiPo cell) | Already certified by cell vendor (LP503562 supplier UN 38.3) |
| **ISO 10993-1, -5, -10** | Biocompatibility — surface contact, ≤24h, intact skin | Not strictly required (no patient contact except via reagent strip handle); plastic patient-contact justification documented in RMF |

## 7. Notified Body Engagement

**None required** for Class B IVD in India. Submission is **direct to the State Licensing Authority**. Contrast: EU IVDR 2017/746 would require Notified Body conformity assessment for the same device (Class B EU IVD).

## 8. Compliance Gap Table — Status as of 2026-05-16

| Requirement | Done | In Progress | Pending |
|---|---|---|---|
| Device technical design (schematic, PCB, mech CAD) | Yes (with rework needed — see STATUS.md) | | |
| Firmware functional | Compiles; partial features | UV/heater/PID loop integration | OTA, secure boot |
| Risk Management File (ISO 14971) | This dossier (draft) | | Sign-off after design freeze |
| Design History File | This dossier (draft) | | Design review minutes, signed |
| Software lifecycle docs (IEC 62304) | This dossier (draft) | SOUP analysis | Unit test code, traceability tool |
| IFU and label artwork | This dossier (draft) | | Human-factors validation per IEC 62366-1 |
| Predicate comparison | This dossier (draft) | | |
| Clinical evaluation protocol | | Drafting | IRB submission, 60-sample study |
| BIS/NABL test reports (61010-1, -2-101, 60601-1-2) | | | All pending |
| Biocompatibility justification | | | Section drafted in RMF; full ISO 10993-1 evaluation pending |
| ISO 13485 QMS | | | Procedures drafted; certification audit pending |
| Calibration data per device | | Calibration mode firmware | Per-unit factory calibration record |
| Stability / shelf-life study | | | 6-month accelerated, 24-month real-time |
| Post-market surveillance plan | This dossier (DHF §10) | | Complaint-handling SOP, vigilance reporting per MDR Rule 89 |

**Bottom line:** the device is at "Design Freeze candidate" stage. ~12–18 months of V&V and clinical work remain before MD-3 can be submitted.

---

*All documents in this folder are working drafts intended for use by a regulatory consultant. None of the content constitutes a real submission.*
