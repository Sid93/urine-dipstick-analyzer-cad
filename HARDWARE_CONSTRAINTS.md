# Hardware Constraints — ESP32-S3 GPIO Budget Analysis

The current design uses 37 GPIO signals on a module that has ~34 truly-available pins
once OPI flash+PSRAM and USB-CDC are accounted for. Two structural conflicts remain
and require an architectural decision, not pin shuffling.

## Conflict #1 — USB-CDC vs GPIO 19/20

| Pin | Conflicting use | Why |
|---|---|---|
| GPIO 19 | USB D− (native USB) **AND** `I2C_SDA` | `platformio.ini` enables `ARDUINO_USB_CDC_ON_BOOT=1` |
| GPIO 20 | USB D+ (native USB) **AND** `UV_GATE` | Same |

If USB-CDC is initialized, the USB peripheral takes electrical control of GPIO 19/20
and any I²C or GPIO traffic on these pins will fail. UART0 (GPIO 43/44) is also
unavailable because `BUZZER=43` and `HEATER_GATE=44`. Result: there is no clean
programming path **and** I²C+UV control simultaneously.

## Conflict #2 — OPI PSRAM vs GPIO 33-37

The chosen module is **ESP32-S3-WROOM-1-N8R8** = 8 MB flash + **8 MB octal PSRAM**.
OPI PSRAM consumes 8 pins: GPIO 26-32 (flash overlap) and GPIO 33-37 (data).

| Pin | Conflicting use | Why |
|---|---|---|
| GPIO 35 | OPI PSRAM D5 **AND** `CAM_VSYNC` | OPI PSRAM data |
| GPIO 36 | OPI PSRAM D6 **AND** `CAM_HREF` | OPI PSRAM data |
| GPIO 37 | OPI PSRAM D7 **AND** `CAM_PCLK` | OPI PSRAM data |

Camera VSYNC/HREF/PCLK are bus-critical edge-triggered signals — they cannot share
pins with PSRAM. If PSRAM is enabled, the camera bus will not work, and disabling
PSRAM breaks image-buffer allocation for a 2MP camera (need ≥ 2 MB heap for one frame
@ JPEG, ≥ 4 MB for RGB565). Internal RAM is only 512 KB.

---

## Three Resolution Paths

### Path A — Module swap to ESP32-S3-WROOM-1-N16R8V (QSPI PSRAM)

Drop-in pin-compatible module:
- 16 MB flash (was 8)
- 8 MB **quad** PSRAM (was octal) → only uses 4 pins (26-32 area), **frees GPIO 33-37**
- Slightly higher BOM cost: $6 → $8 (+$2)

**Fixes:** Conflict #2 entirely.
**Doesn't fix:** Conflict #1 (USB-CDC still steals GPIO 19/20).

### Path B — Add a PCA9555 I²C I/O expander (and Path A)

16-channel I²C-controlled GPIO expander, ~$1.20.
Move all slow switching signals to the expander:

| Signal | From ESP32 | To PCA9555 |
|---|---|---|
| FAN_GATE | GPIO 2 | EXP_P0 |
| HEATER_GATE | GPIO 44 | EXP_P1 |
| UV_GATE | GPIO 20 | EXP_P2 |
| WHITE_LED | GPIO 6 | EXP_P3 |
| BUZZER | GPIO 43 | EXP_P4 |
| REED_SWITCH | GPIO 21 | EXP_P5 (input) |
| LIMIT_SW | GPIO 42 | EXP_P6 (input) |
| BARCODE_TX | GPIO 0 | (keep — UART must stay on real GPIO) |
| BARCODE_RX | GPIO 17 | (keep — UART) |

This frees **GPIO 2, 6, 20, 21, 42, 43, 44** = **7 GPIOs**. We can then:
- Move I²C off GPIO 19 to GPIO 2 (SDA) + GPIO 42 (SCL), freeing 19
- Move UV_GATE off GPIO 20 (now on expander)
- Restore RGB_BLUE on GPIO 17 (move BARCODE_RX to GPIO 21)
- Re-enable Serial UART debug on GPIO 43/44

**Fixes:** Both conflicts.
**Cost:** +$1.20 BOM + PCB redesign + firmware refactor (~200 lines added).
**Tradeoff:** ~1 ms extra latency on switched signals via I²C — irrelevant for fan/heater/UV/buzzer, fine for limit/reed at typical poll rates.

### Path C — Accept conflicts as software constraints

Keep hardware unchanged. Add firmware safeguards:
- Disable USB-CDC at runtime once boot is complete (`Serial.end()` + reconfigure GPIO 19/20)
- Disable OPI PSRAM entirely (no big image buffers — limits camera capture to thumbnail JPEGs in heap)

**Fixes:** Symptomatic only.
**Cost:** No BOM/PCB changes.
**Tradeoff:** Lose USB serial debug capability after boot; lose PSRAM (camera reduced to ~640×480 JPEG only, max ~80 KB per frame in heap).

---

## Recommendation

**Path B (PCA9555 + module swap)** is the production-grade answer. It costs +$3.20 BOM
and adds two days of work (schematic + PCB + firmware), but produces a board that
actually meets the feature spec without runtime workarounds.

Path A alone is a quick win that fixes the camera conflict — adequate if you accept
that USB programming will work but USB-Serial debug after boot will require external
UART (CH340/CP2102 on GPIO 43/44 after re-freeing them via Path B).

Path C is what you'd ship if the prototype must move tomorrow and you'll respin v2
later with Path B.
