# SOFTWARE LIFECYCLE FILE — IEC 62304
## Urine Dipstick Analyzer — Model UDA-PROTO-001

| | |
|---|---|
| **Document No.** | SDLC-UDA-001 |
| **Version** | 0.1 (Draft) |
| **Date** | 2026-05-16 |
| **Applicable Standards** | IEC 62304:2006 + A1:2015; IEC 82304-1:2016 (where applicable); ISO 14971:2019 (risk linkage) |
| **Software Item Identifier** | `urine_dipstick_analyzer.bin` for ESP32-S3 target |
| **Source Repository** | `firmware/urine_dipstick_analyzer/` |

---

## 1. Software Safety Classification

Per IEC 62304 §4.3 and §B.4.3:

| Question | Answer |
|---|---|
| Can the software contribute to a hazardous situation? | Yes — an incorrect analyte reading could lead to clinical misdiagnosis. |
| What is the worst-case harm if no risk control external to the software is effective? | **Class B — Non-serious injury possible** (delayed treatment due to misdiagnosis; not immediately life-threatening because urinalysis is a screening test, not a sole determinant). The worst credible harm is delayed diagnosis of conditions such as proteinuria or UTI, leading to escalation later — not direct death. |
| Could the software directly cause death or serious injury? | No — there is no direct actuation of therapy; the result is read by a clinician who exercises judgement; reagent strip itself is the primary diagnostic. |

**Software Safety Classification: Class B.**

The full lifecycle (development, maintenance, risk management, configuration management, problem resolution) applies as described in IEC 62304 §5 through §9, with the Class A documentation depth where Class B does not require deeper artefacts (e.g., detailed design depth is moderate, not full).

---

## 2. Software Development Plan

V-model with the following gated phases:

| Phase (IEC 62304 §) | Deliverables |
|---|---|
| §5.1 Planning | This SDLC document; SDP; tooling list |
| §5.2 Requirements | Software Requirements Specification (SRS) — see §3 |
| §5.3 Architectural design | Module diagram, trust boundaries, SOUP inventory — see §4 |
| §5.4 Detailed design | Per-module headers and responsibilities — see §5 |
| §5.5 Unit implementation & verification | Source code; unit tests — see §6 |
| §5.6 Integration & integration testing | Integration test report — see §7 |
| §5.7 System testing | System test report — see §8 |
| §5.8 Release | Frozen build, SBOM, release notes — see §9 |
| §6 Maintenance | Maintenance plan — see §10 |
| §7 Risk management | Linked to RMF document — see §11 |
| §8 Configuration management | CM plan — see §12 |
| §9 Problem resolution | Defect-tracking SOP — see §13 |

### Tools

| Tool | Version | Purpose | Validation status |
|---|---|---|---|
| Arduino-ESP32 core (PlatformIO) | 2.0.14 (frozen) | Toolchain | Validated by community + bench tests |
| PlatformIO Core | ≥ 6.1 | Build orchestration | Validated by reproducible build |
| Git | ≥ 2.40 | Version control | Industry standard |
| KiCad | 8.0 | Schematic / PCB (not software but referenced) | n/a |
| Catch2 / Unity | TBD | Unit testing on host | To validate |

---

## 3. Software Requirements Specification (SRS)

### 3.1 Functional Requirements

| ID | Requirement |
|---|---|
| SRS-F-01 | The software shall initialise all peripherals (camera, display, sensors, stepper, storage, RTC) on power-up and run a self-test, displaying any failure to the user. |
| SRS-F-02 | The software shall present a main menu with options: Run Test, History, Calibrate, Settings, QC. |
| SRS-F-03 | The software shall accept a barcode scan (GM65) and parse strip brand, lot, and expiry date. |
| SRS-F-04 | The software shall refuse to run a test if the scanned strip is expired (RTC date > expiry). |
| SRS-F-05 | The software shall refuse to run a test if the scanned strip brand is not in the calibration table. |
| SRS-F-06 | The software shall command the stepper motor to advance the tray to the imaging position (configurable in calibration). |
| SRS-F-07 | The software shall measure ambient light via BH1750 and refuse imaging if reading exceeds 5 lux at the strip position. |
| SRS-F-08 | The software shall control the white-LED array with PWM during imaging, maintaining intensity within ± 2% of calibration. |
| SRS-F-09 | The software shall capture an RGB image from the OV2640 camera (≥ 800×600). |
| SRS-F-10 | The software shall extract a Region of Interest (ROI) for each of the 10 reagent pads using calibration-defined coordinates. |
| SRS-F-11 | The software shall convert each ROI to mean HSV and apply the per-analyte calibration polynomial. |
| SRS-F-12 | The software shall display semi-quantitative results for all 10 analytes within 120 s of strip insertion. |
| SRS-F-13 | The software shall store each test result (timestamp, brand, lot, raw RGB, computed values) as a JSON record on SD. |
| SRS-F-14 | The software shall export records via USB-serial in CSV or JSON on request. |
| SRS-F-15 | The software shall command UV-C LED for 30 s after each test, only if the reed-switch indicates the tray is closed. |
| SRS-F-16 | The software shall sample the SHT31 temperature/humidity sensor every 5 s and log out-of-range conditions. |
| SRS-F-17 | The software shall close-loop control the polyimide heater via PID to maintain tray temperature at the configurable setpoint ± 1 °C. |
| SRS-F-18 | The software shall monitor battery state-of-charge via MAX17048 and warn the user below 15%, refuse to start a test below 5%. |
| SRS-F-19 | The software shall allow recalibration with a ColorChecker reference card, capturing patches and updating `calibration.json`. |
| SRS-F-20 | The software shall provide a Quality Control mode that runs with manufacturer-provided positive and negative control strips and flags out-of-range results. |
| SRS-F-21 | The software shall display device serial number, firmware version, hardware revision, and calibration date in the About screen. |
| SRS-F-22 | The software shall provide a factory-reset operation, protected by a 4-digit service PIN. |

### 3.2 Non-Functional Requirements

| ID | Requirement |
|---|---|
| SRS-NF-01 | Boot time from power-on to ready ≤ 5 s. |
| SRS-NF-02 | Memory: software shall fit in 4 MB of ESP32-S3 flash with ≥ 20% headroom; RAM use ≤ 70% of available SRAM + PSRAM. |
| SRS-NF-03 | The software shall implement a hardware watchdog with timeout 8 s. |
| SRS-NF-04 | All persisted files shall include a CRC32 or SHA-256 integrity check. |
| SRS-NF-05 | Firmware updates shall be cryptographically signed and verified before flashing. |
| SRS-NF-06 | The software shall log all errors to SD with timestamp and severity. |
| SRS-NF-07 | The software shall not log Personally Identifiable Information (PII) without explicit operator opt-in. |
| SRS-NF-08 | The software shall provide language strings via a localisation table; first release: English. |

---

## 4. Software Architecture

### 4.1 Module Diagram

```
                ┌───────────────────────────────────────┐
                │             Application Layer        │
                │ ┌────────────┐ ┌────────────────────┐ │
                │ │ Menu / UI  │ │ Workflow / FSM     │ │
                │ └─────┬──────┘ └─────────┬──────────┘ │
                │       │                  │            │
                │  ┌────▼──────────┐  ┌────▼─────────┐  │
                │  │ Analysis      │  │ QC / Cal     │  │
                │  │ (pad ROIs,    │  │ workflows    │  │
                │  │  HSV → conc)  │  │              │  │
                │  └────┬──────────┘  └──────┬───────┘  │
                └───────┼─────────────────────┼─────────┘
                        │                     │
              ┌─────────▼─────────────────────▼─────────┐
              │           Service Layer                │
              │ Camera   Display   Storage   Stepper   │
              │ Heater   UV-C      Barcode   Sensors   │
              │ Battery  RTC       Buzzer    LEDs      │
              └─────────┬─────────────────────┬─────────┘
                        │                     │
              ┌─────────▼─────────────────────▼─────────┐
              │           HAL / SOUP                   │
              │  Arduino-ESP32, TFT_eSPI, AccelStepper,│
              │  Adafruit_SHT31, Adafruit_BH1750,      │
              │  RTClib, ArduinoJson, ESP-IDF          │
              └────────────────────────────────────────┘
```

### 4.2 Trust Boundaries

| Boundary | Source side | Sink side | Validation |
|---|---|---|---|
| USB-serial input | External host | Firmware | All commands parsed by length-limited tokeniser; checksum required |
| OTA payload | Network/USB | Firmware bootloader | RSA-2048 signature verification |
| Calibration file | SD card | Analysis module | SHA-256 hash verified at boot |
| Reagent strip barcode | GM65 scanner | Workflow FSM | Whitelist check; length cap |
| ColorChecker capture | OV2640 | Calibration module | Sanity check on patch values; refuse if out of physical range |

### 4.3 SOUP Inventory (Software of Unknown Provenance)

| SOUP item | Version | Source | Used for | Known anomalies / CVEs |
|---|---|---|---|---|
| Arduino-ESP32 core (esp32 by Espressif) | 2.0.14 | github.com/espressif/arduino-esp32 | HAL, peripherals | Issue list reviewed; no security-critical for our scope |
| TFT_eSPI | 2.5.43 | github.com/Bodmer/TFT_eSPI | Display driver | No CVEs |
| AccelStepper | 1.64 | airspayce.com | Stepper control | No CVEs |
| Adafruit_SHT31 | 2.2.0 | github.com/adafruit/Adafruit_SHT31 | T/RH | No CVEs |
| Adafruit_BH1750 | 1.3.0 | github.com/adafruit/Adafruit_BH1750 | Ambient light | No CVEs |
| RTClib | 2.1.4 | github.com/adafruit/RTClib | DS3231 | No CVEs |
| ArduinoJson | 7.0.4 | arduinojson.org | JSON I/O | No CVEs |
| ESP-IDF (underlying) | 5.1.x | espressif | RTOS, Wi-Fi | Periodic CVE sweep; only relevant CVEs require an update |

All SOUP versions are pinned in `platformio.ini`. CVE sweep is performed quarterly and on every release candidate.

---

## 5. Software Detailed Design

Each header file in `firmware/urine_dipstick_analyzer/` corresponds to a module.

| Header | Responsibility | Inputs | Outputs | Error states |
|---|---|---|---|---|
| `config.h` | Pin map, constants, calibration limits | Compile-time | Macros | n/a |
| `camera.h` | Init OV2640, capture frame, return buffer | trigger | RGB buffer | sensor not found, capture timeout |
| `display.h` | TFT init, draw menus, error screens | display state | rendered frame | bus error |
| `analysis.h` | ROI extraction, HSV conversion, calibration polynomial | RGB buffer, calibration table | per-analyte semi-quant values | invalid ROI, out-of-range |
| `heater.h` | PID loop on tray temperature | setpoint, SHT31 value | PWM to IRLZ44N gate | sensor fail, over-temp shutdown |
| `stepper.h` | AccelStepper wrapper; home, advance, retract | move command | step pulses | limit-switch miss |
| `storage.h` | SD card init; JSON read/write | record | persisted record | SD missing, write error |
| `sensors.h` | I2C wrappers for SHT31, BH1750, MAX17048, DS3231 | poll trigger | sensor structs | NACK, CRC fail |
| `uv.h` | UV-C LED control with interlock check | request | gate state | reed-switch open → refuse |
| `barcode.h` | UART parser for GM65 | byte stream | parsed strip info | timeout, bad format |
| `battery.h` | MAX17048 polling, warning thresholds | poll | percent | I2C fail |
| `buzzer.h` | Buzzer tones, jingles | request | square wave | n/a |
| `leds.h` | RGB status LED | colour | PWM | n/a |
| `state.h` | Workflow finite-state machine | events | transitions | invalid transition → safe state |
| `secure_boot.h` (planned) | OTA signature verification | image | accept/reject | bad signature → rollback |

---

## 6. Software Unit Verification

Per IEC 62304 §5.5, Class B requires unit verification by code review and/or test of safety-critical units.

| Unit | Test method | Tool | Pass criterion |
|---|---|---|---|
| `analysis.h` polynomial | Host-side unit test against synthetic RGB | Catch2 on PC | Each known input → expected category |
| `uv.h` interlock | Host-side mocked reed switch | Catch2 | UV gate stays low when reed open |
| `battery.h` thresholds | Host-side mocked SoC | Catch2 | Warning at ≤ 15%, refusal at ≤ 5% |
| `barcode.h` parser | Fuzz with random and malformed payloads | libFuzzer | No crash, no buffer overrun |
| `storage.h` CRC | Inject corrupted record | Catch2 | Read returns error, not corrupted data |
| `heater.h` PID limits | Sim with step input | Host sim | No setpoint overshoot > 1.5 °C |
| `state.h` FSM | Coverage of all defined transitions | Manual + state-table | 100% transition coverage |

Code review is mandatory for safety-critical modules (`analysis`, `uv`, `battery`, `secure_boot`). Reviews are tracked in pull-request history on the git repository.

---

## 7. Software Integration Testing

| Test | Modules involved | Scenario |
|---|---|---|
| INT-01 | camera + analysis | Capture a known calibration card and verify all 10 ROIs map to expected values |
| INT-02 | stepper + state | Run home → advance → image → retract sequence; verify position via limit switch |
| INT-03 | uv + reed switch + state | UV cycle: open tray mid-cycle → confirm UV gate de-asserts within 100 ms |
| INT-04 | heater + sensors + state | Step setpoint; verify PID brings actual to set within 60 s |
| INT-05 | barcode + state | Scan known strips, unknown strips, expired strips; verify firmware response |
| INT-06 | storage + analysis | Run 50 successive tests; verify all records stored and retrievable |
| INT-07 | battery + state | Discharge to 5%; verify refusal-to-start behaviour |
| INT-08 | display + state | Walk the whole menu tree; verify no orphan screens |

---

## 8. Software System Testing

Black-box, per the SRS:

| ID | SRS coverage | Test |
|---|---|---|
| SYS-01 | F-01..F-22 | End-to-end test with real urine sample and reference predicate (within clinical evaluation) |
| SYS-02 | F-09..F-12 | Time-to-result ≤ 120 s on 30 consecutive strips |
| SYS-03 | F-15, NF-04 | 30 successive tests with UV cycle; CFU swab pre/post |
| SYS-04 | NF-03 | Inject software lock-up; verify watchdog reboot |
| SYS-05 | NF-05 | OTA: push valid signed image (accept), corrupted image (reject), valid unsigned image (reject) |
| SYS-06 | F-19 | Recalibrate with ColorChecker; verify accuracy preserved over 10 sessions |
| SYS-07 | F-20 | QC pos/neg strips; firmware flags out-of-range correctly |
| SYS-08 | F-14 | Export 100 records via USB; round-trip CSV/JSON parse |

System-test results are filed under `regulatory/system_test_reports/`.

---

## 9. Software Release

| Activity | Tool / artefact |
|---|---|
| Version numbering | SemVer (MAJOR.MINOR.PATCH); current `0.1.0-prealpha` |
| Source tagging | `git tag v0.1.0` annotated; signed by Design Lead key |
| Build reproducibility | PlatformIO frozen versions, locked toolchain; Docker build container `Dockerfile.build` (TBD) |
| Binary artefact | `urine_dipstick_analyzer.bin`, with `.sha256` and `.sig` files |
| Software Bill of Materials | `SBOM.cyclonedx.json` enumerating Arduino core, TFT_eSPI, AccelStepper, Adafruit_SHT31, Adafruit_BH1750, RTClib, ArduinoJson, ESP-IDF and their pinned versions |
| Release notes | `CHANGELOG.md` per release; references closed issues |
| Branch protection | `main` requires pull request and 1 reviewer; signed commits |

---

## 10. Software Maintenance Plan (IEC 62304 §6)

- **Modification request flow:** issue raised in tracker → triage (defect or enhancement) → impact analysis → change classified (Class B critical / non-critical) → development on feature branch → review → test → release.
- **OTA delivery (planned):** ESP32-S3 OTA partition scheme with A/B rollback. Signed payload. User must explicitly accept update in the menu (no silent updates).
- **USB-only fallback:** if OTA is not yet implemented at first release, IFU will state firmware updates are by USB-flashing only, performed by an authorised service technician.
- **SOUP monitoring:** quarterly review of CVE feeds for each SOUP item; tracked in `SOUP_changelog.md`.
- **Anomaly classification:** P0 safety / P1 functional / P2 cosmetic. P0 anomalies trigger a Field Safety Notice within 5 days.

---

## 11. Software Risk Management

Software-related hazards are catalogued in the RMF (`regulatory/RMF_risk_management_iso14971.md`), in particular H-13, H-14, H-15, H-16, H-17. Each is traced to one or more SRS requirements and to specific verification tests in §6–§8 above.

| Hazard | SRS controls | Verification |
|---|---|---|
| H-13 wrong analyte result | F-10..F-12, NF-04 | Unit test on `analysis.h`; SYS-01 clinical |
| H-14 missed alert | F-01 self-test, NF-03 watchdog | INT-03, SYS-04 |
| H-15 calibration corruption | NF-04 integrity check | Unit test storage CRC; SYS-06 |
| H-16 OTA failure | NF-05 signed updates, A/B rollback | SYS-05 |
| H-17 data loss | NF-04 CRC + wear-levelling | INT-06 |

---

## 12. Configuration Management

Items under configuration control:

- Source code (git repository, signed commits).
- `platformio.ini` (toolchain and SOUP versions).
- `calibration.json` reference schema (per-unit instance is in the device, hashed).
- Build container (Dockerfile, TBD).
- Test data sets (in `tests/fixtures/`).
- Documentation (this file, SRS in this file, traceability).

Change control: pull-request workflow with mandatory review; CI must pass (build + unit tests).

---

## 13. Problem Resolution Process

1. Defect or complaint logged in issue tracker with severity (P0/P1/P2) and one of: safety, function, performance, cosmetic.
2. P0 → immediate triage by Design Lead + Quality; risk-impact assessed; corrective action plan in 48 h.
3. Root-cause analysis (5-why or fishbone) for P0/P1.
4. Fix on feature branch; unit + integration tests added to prevent regression.
5. Post-mortem note appended to issue; closed with sign-off.
6. If field units are affected: FSN issued to operators; OTA or USB-flash deployed; RMF updated; CAPA recorded.

---

## 14. References

- IEC 62304:2006 + A1:2015 — Medical device software — Software life cycle processes.
- IEC 82304-1:2016 — Health software — General requirements for product safety.
- ISO 14971:2019 — Risk management.
- AAMI TIR45:2012 — Use of agile practices in development of medical device software (informative).
- OWASP Embedded Application Security guidelines.

---

*End of SDLC v0.1.*
