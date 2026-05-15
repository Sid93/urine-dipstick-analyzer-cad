/*
 * URINE DIPSTICK ANALYZER v2.0 — ESP32-S3 Firmware
 *
 * Hardware: ESP32-S3-DevKitC-1-N8R8, OV2640 camera with CPL,
 *   ILI9341 2.4" TFT (320x240), SHT31, BH1750, DS3231 RTC,
 *   MAX17048 fuel gauge, A4988 stepper, NEMA 17,
 *   UV-C LED, heater film, barcode scanner, SD card
 *
 * Board: "ESP32S3 Dev Module" in Arduino IDE
 * PSRAM: "OPI PSRAM"
 * Partition: "Huge APP (3MB No OTA / 1MB SPIFFS)"
 *
 * Libraries required:
 *   - Adafruit ILI9341
 *   - Adafruit GFX
 *   - Adafruit SHT31
 *   - BH1750 (by Christopher Laws)
 *   - AccelStepper
 *   - ESP32 Camera driver (built-in with ESP32 board package)
 */

#include <Wire.h>
#include "config.h"
#include "display.h"
#include "sensors.h"
#include "stepper.h"
#include "heater.h"
#include "camera.h"
#include "analysis.h"
#include "storage.h"
#include "barcode.h"
#include "safety.h"
#include "leds.h"
#include "rtc.h"
#include "battery.h"

// ============================================================
// STATE MACHINE
// ============================================================
enum State {
    STATE_INIT,
    STATE_IDLE,
    STATE_SCAN_BARCODE,
    STATE_PREHEAT,
    STATE_TRAY_TO_CAPTURE,
    STATE_CAPTURE,
    STATE_ANALYZE,
    STATE_DISPLAY_RESULTS,
    STATE_LOG_RESULTS,
    STATE_TRAY_RETRACT,
    STATE_UV_STERILIZE,
    STATE_VENT,
    STATE_CALIBRATION,
    STATE_ERROR
};

// ============================================================
// GLOBAL OBJECTS
// ============================================================
Display        display;
Sensors        sensors;
TrayMotor      tray;
HeaterPID      heater;
Camera         cam;
Analysis       analysis;
Storage        storage;
BarcodeScanner barcode(Serial1);
SafetyManager  safety;
LEDController  leds;
RealTimeClock  rtc;
BatteryGauge   battery;

State currentState = STATE_INIT;
State prevState    = STATE_INIT;

// Button handling
volatile bool buttonPressed = false;
unsigned long buttonPressTime = 0;
unsigned long lastDebounce = 0;

// Test tracking
char currentPatientID[64] = "UNKNOWN";
int resultPage = 0;
uint32_t testNumber = 0;

// Calibration mode
bool calibrationMode = false;
int calPadIdx = 0;
int calLevel = 0;

// Error
char errorMsg[64] = {0};

// Status bar cache
char _timeStr[8] = "00:00";
float _battPct = 100.0f;
unsigned long _lastStatusUpdate = 0;

// Timing vars
static unsigned long _scanTimeout = 0;
static unsigned long _preheatStart = 0;
static unsigned long _ventStart = 0;

// ============================================================
// HELPERS
// ============================================================
void updateStatusInfo() {
    if (millis() - _lastStatusUpdate < 2000) return;
    _lastStatusUpdate = millis();

    rtc.read();
    rtc.formatTime(_timeStr, sizeof(_timeStr));

    battery.update();
    _battPct = battery.soc;

    if (battery.isCritical()) {
        display.showLowBattery(_battPct);
        leds.beepError();
        delay(2000);
    }
}

// ============================================================
// INTERRUPT
// ============================================================
void IRAM_ATTR onButtonPress() {
    unsigned long now = millis();
    if (now - lastDebounce > 200) {
        buttonPressed = true;
        buttonPressTime = now;
        lastDebounce = now;
    }
}

// ============================================================
// SETUP
// ============================================================
void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Urine Dipstick Analyzer v2.0 ===\n");

    // I2C
    Wire.begin(I2C_SDA, I2C_SCL);

    // Button interrupt
    pinMode(PIN_BUTTON, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_BUTTON), onButtonPress, FALLING);

    // Initialize all subsystems
    leds.begin();
    leds.rgbYellow();

    // TFT Display
    display.begin();
    display.showSplash();

    // RTC
    if (rtc.begin()) {
        rtc.formatTime(_timeStr, sizeof(_timeStr));
        Serial.printf("RTC: OK (%s)\n", _timeStr);
    } else {
        Serial.println("RTC: not found (using millis fallback)");
    }

    // Battery Gauge
    if (battery.begin()) {
        battery.update();
        _battPct = battery.soc;
        Serial.printf("Battery: %.0f%% (%.2fV)\n", _battPct, battery.voltage);
    } else {
        Serial.println("Battery gauge: not found");
    }

    // Sensors
    bool sht_ok = sensors.beginSHT31();
    bool bh_ok  = sensors.beginBH1750();
    Serial.printf("SHT31: %s, BH1750: %s\n", sht_ok ? "OK" : "FAIL", bh_ok ? "OK" : "FAIL");

    // Stepper
    tray.begin();

    // Heater
    heater.begin();

    // Camera
    if (!cam.begin()) {
        Serial.println("ERROR: Camera init failed");
        snprintf(errorMsg, sizeof(errorMsg), "Camera init failed");
        currentState = STATE_ERROR;
        return;
    }
    Serial.println("Camera: OK");

    // Analysis
    analysis.initDefaultROIs();
    if (analysis.loadCalibration()) {
        Serial.println("Calibration loaded from NVS");
    } else {
        Serial.println("No calibration found, using defaults");
    }

    // SD Card
    storage.setRTC(&rtc);
    if (storage.begin()) {
        Serial.println("SD Card: OK");
        testNumber = storage.getTestCount();
    } else {
        Serial.println("SD Card: not present (logging disabled)");
    }

    // Barcode scanner
    barcode.begin();
    Serial.println("Barcode scanner: OK");

    // Safety
    safety.begin();

    // Home the tray
    display.showStatus("Homing tray...");
    if (!tray.home()) {
        Serial.println("WARNING: Tray homing failed");
        display.showStatus("Tray home failed", "Continuing anyway...");
        delay(1500);
    } else {
        Serial.println("Tray: homed");
    }

    // Eject tray for strip insertion
    tray.moveToEject();
    while (!tray.isAtTarget()) tray.update();

    leds.rgbGreen();
    leds.beepSuccess();
    currentState = STATE_IDLE;
}

// ============================================================
// MAIN LOOP
// ============================================================
void loop() {
    tray.update();
    barcode.update();
    updateStatusInfo();

    switch (currentState) {
        case STATE_IDLE:            stateIdle();          break;
        case STATE_SCAN_BARCODE:    stateScanBarcode();   break;
        case STATE_PREHEAT:         statePreheat();       break;
        case STATE_TRAY_TO_CAPTURE: stateTrayToCapture(); break;
        case STATE_CAPTURE:         stateCapture();       break;
        case STATE_ANALYZE:         stateAnalyze();       break;
        case STATE_DISPLAY_RESULTS: stateDisplayResults(); break;
        case STATE_LOG_RESULTS:     stateLogResults();    break;
        case STATE_TRAY_RETRACT:    stateTrayRetract();   break;
        case STATE_UV_STERILIZE:    stateUVSterilize();   break;
        case STATE_VENT:            stateVent();          break;
        case STATE_CALIBRATION:     stateCalibration();   break;
        case STATE_ERROR:           stateError();         break;
        default: break;
    }

    prevState = currentState;
}

// ============================================================
// STATE HANDLERS
// ============================================================

void stateIdle() {
    if (prevState != STATE_IDLE) {
        display.showReady(_battPct, _timeStr, testNumber);
        leds.rgbGreen();
        strcpy(currentPatientID, "UNKNOWN");
    }

    // Check for long press -> calibration mode
    if (buttonPressed) {
        buttonPressed = false;

        if (digitalRead(PIN_BUTTON) == LOW) {
            unsigned long holdStart = millis();
            while (digitalRead(PIN_BUTTON) == LOW && (millis() - holdStart < 3000)) {
                delay(10);
            }
            if (millis() - holdStart >= 3000) {
                calPadIdx = 0;
                calLevel = 0;
                currentState = STATE_CALIBRATION;
                return;
            }
        }

        leds.beepShort();
        currentState = STATE_SCAN_BARCODE;
    }

    // Auto-trigger on barcode scan
    char code[64];
    if (barcode.read(code, sizeof(code))) {
        strncpy(currentPatientID, code, sizeof(currentPatientID) - 1);
        Serial.printf("Barcode scanned: %s\n", currentPatientID);
        display.showStatus("Patient ID:", currentPatientID);
        delay(1000);
        currentState = STATE_PREHEAT;
    }
}

void stateScanBarcode() {
    if (prevState != STATE_SCAN_BARCODE) {
        display.showScanBarcode(_battPct, _timeStr);
        barcode.triggerScan();
        _scanTimeout = millis();
    }

    char code[64];
    if (barcode.read(code, sizeof(code))) {
        strncpy(currentPatientID, code, sizeof(currentPatientID) - 1);
        display.showStatus("Patient ID:", currentPatientID);
        leds.beepShort();
        delay(800);
        currentState = STATE_PREHEAT;
        return;
    }

    if (buttonPressed || (millis() - _scanTimeout > 5000)) {
        buttonPressed = false;
        currentState = STATE_PREHEAT;
    }
}

void statePreheat() {
    if (prevState != STATE_PREHEAT) {
        leds.rgbYellow();
        heater.enable();
        _preheatStart = millis();
    }

    sensors.readAll();
    heater.update(sensors.trayTempC);

    if (millis() % 500 < 50) {
        display.showPreheat(sensors.trayTempC, HEATER_TARGET_C, _battPct, _timeStr);
    }

    if (heater.isAtTemp(sensors.trayTempC) || (millis() - _preheatStart > 60000)) {
        currentState = STATE_TRAY_TO_CAPTURE;
    }

    if (sensors.trayTempC > HEATER_OVERTEMP_C) {
        heater.disable();
        snprintf(errorMsg, sizeof(errorMsg), "Over-temp: %.1fC", sensors.trayTempC);
        currentState = STATE_ERROR;
    }
}

void stateTrayToCapture() {
    if (prevState != STATE_TRAY_TO_CAPTURE) {
        display.showMeasuring(1, 6, "Moving tray to capture position");
        tray.moveToCapture();
    }

    if (tray.isAtTarget()) {
        delay(500);
        currentState = STATE_CAPTURE;
    }
}

void stateCapture() {
    if (prevState != STATE_CAPTURE) {
        display.showMeasuring(2, 6, "Capturing strip image");
        leds.rgbBlue();
    }

    sensors.readAll();
    if (!sensors.isAmbientLightOK()) {
        display.showStatus("Warning:", "High ambient light!");
        delay(1000);
    }

    leds.whiteLedOn();
    delay(200);

    camera_fb_t *discard = cam.capture();
    cam.release(discard);
    delay(100);

    analysis.captureWhiteReference(cam);

    display.showMeasuring(3, 6, "White reference captured");
    currentState = STATE_ANALYZE;
}

void stateAnalyze() {
    if (prevState != STATE_ANALYZE) {
        display.showMeasuring(4, 6, "Analyzing colorimetry");
    }

    bool ok = analysis.analyzeStrip(cam);
    leds.whiteLedOff();

    if (!ok) {
        snprintf(errorMsg, sizeof(errorMsg), "Image analysis failed");
        currentState = STATE_ERROR;
        return;
    }

    Serial.println("\n--- RESULTS ---");
    for (int i = 0; i < NUM_PADS; i++) {
        Serial.printf("  %-4s: %.1f %s (%s) [H=%.0f S=%.2f V=%.2f]\n",
            PAD_NAMES_ARR[i],
            analysis.readings[i].concentration,
            PAD_UNITS[i],
            analysis.readings[i].catLabel,
            analysis.readings[i].h,
            analysis.readings[i].s,
            analysis.readings[i].v);
    }
    Serial.println("---------------\n");

    leds.beepSuccess();
    display.showMeasuring(5, 6, "Analysis complete");
    delay(500);
    resultPage = 0;
    currentState = STATE_DISPLAY_RESULTS;
}

void stateDisplayResults() {
    if (prevState != STATE_DISPLAY_RESULTS || prevState == currentState) {
        leds.rgbGreen();

        float vals[NUM_PADS];
        const char* cats[NUM_PADS];
        for (int i = 0; i < NUM_PADS; i++) {
            vals[i] = analysis.readings[i].concentration;
            cats[i] = analysis.readings[i].catLabel;
        }
        display.showResults(PAD_NAMES_ARR, vals, cats, NUM_PADS, resultPage, _battPct, _timeStr);
    }

    if (buttonPressed) {
        buttonPressed = false;
        resultPage++;
        int maxPages = (NUM_PADS + 4) / 5;
        if (resultPage >= maxPages) {
            currentState = STATE_LOG_RESULTS;
        } else {
            float vals[NUM_PADS];
            const char* cats[NUM_PADS];
            for (int i = 0; i < NUM_PADS; i++) {
                vals[i] = analysis.readings[i].concentration;
                cats[i] = analysis.readings[i].catLabel;
            }
            display.showResults(PAD_NAMES_ARR, vals, cats, NUM_PADS, resultPage, _battPct, _timeStr);
        }
    }
}

void stateLogResults() {
    if (prevState != STATE_LOG_RESULTS) {
        display.showMeasuring(6, 6, "Saving results to SD");
    }

    sensors.readAll();
    storage.logResult(currentPatientID, analysis.readings,
                      sensors.temperature, sensors.humidity,
                      sensors.lux, sensors.trayTempC,
                      _battPct, battery.voltage);
    storage.incrementTestCount();
    testNumber++;

    heater.disable();
    currentState = STATE_TRAY_RETRACT;
}

void stateTrayRetract() {
    if (prevState != STATE_TRAY_RETRACT) {
        display.showStatus("Retracting tray...");
        tray.moveToHome();
    }

    if (tray.isAtTarget()) {
        currentState = STATE_UV_STERILIZE;
    }
}

void stateUVSterilize() {
    if (prevState != STATE_UV_STERILIZE) {
        display.showUVSterilizing(0, _battPct, _timeStr);
        leds.rgbPurple();

        if (!safety.startUV()) {
            display.showStatus("UV skipped:", "Tray not sealed");
            delay(1500);
            currentState = STATE_VENT;
            return;
        }
    }

    int progress = safety.updateUV();
    if (progress < 0) {
        display.showStatus("UV interrupted!", "Tray opened");
        leds.beepError();
        delay(1500);
        currentState = STATE_VENT;
        return;
    }

    display.showUVSterilizing(progress, _battPct, _timeStr);

    if (progress >= 100) {
        display.showStatus("UV complete");
        delay(500);
        currentState = STATE_VENT;
    }
}

void stateVent() {
    if (prevState != STATE_VENT) {
        leds.fanOn();
        _ventStart = millis();
    }

    sensors.readAll();
    display.showVenting(sensors.humidity, _battPct, _timeStr);

    if ((millis() - _ventStart > 10000) || sensors.isHumidityOK()) {
        leds.fanOff();

        tray.moveToEject();
        while (!tray.isAtTarget()) tray.update();

        currentState = STATE_IDLE;
    }
}

void stateCalibration() {
    if (prevState != STATE_CALIBRATION) {
        display.showCalibration(calPadIdx, calLevel, PAD_NAMES_ARR[calPadIdx], _battPct, _timeStr);
        leds.rgbPurple();
        leds.beepLong();
    }

    if (buttonPressed) {
        buttonPressed = false;

        leds.whiteLedOn();
        delay(300);

        camera_fb_t *discard = cam.capture();
        cam.release(discard);
        delay(100);

        analysis.captureWhiteReference(cam);
        camera_fb_t *fb = cam.capture();
        if (fb) {
            float r, g, b;
            cam.getROI_RGB(fb, analysis.rois[calPadIdx].x, analysis.rois[calPadIdx].y,
                           analysis.rois[calPadIdx].w, analysis.rois[calPadIdx].h,
                           r, g, b);
            cam.release(fb);

            float h, s, v;
            Camera::rgb_to_hsv(r, g, b, h, s, v);

            Serial.printf("CAL [%s] Level %d: R=%.0f G=%.0f B=%.0f H=%.0f S=%.2f V=%.2f\n",
                PAD_NAMES_ARR[calPadIdx], calLevel, r, g, b, h, s, v);

            char logMsg[128];
            snprintf(logMsg, sizeof(logMsg), "CAL %s L%d: H=%.1f S=%.2f V=%.2f",
                     PAD_NAMES_ARR[calPadIdx], calLevel, h, s, v);
            storage.logCalibrationEvent(logMsg);

            leds.beepShort();
        }

        leds.whiteLedOff();

        calLevel++;
        if (calLevel >= CAL_LEVELS) {
            calLevel = 0;
            calPadIdx++;
            if (calPadIdx >= NUM_PADS) {
                analysis.saveCalibration();
                storage.logCalibrationEvent("Calibration complete");
                display.showStatus("Calibration", "SAVED!");
                leds.beepSuccess();
                delay(2000);
                calPadIdx = 0;
                calLevel = 0;
                currentState = STATE_IDLE;
                return;
            }
        }

        display.showCalibration(calPadIdx, calLevel, PAD_NAMES_ARR[calPadIdx], _battPct, _timeStr);
    }
}

void stateError() {
    if (prevState != STATE_ERROR) {
        display.showError(errorMsg, _battPct, _timeStr);
        leds.rgbRed();
        leds.beepError();
        heater.disable();
        leds.whiteLedOff();
        safety.stopUV();
        leds.fanOff();
        Serial.printf("ERROR: %s\n", errorMsg);
    }

    if (buttonPressed) {
        buttonPressed = false;
        currentState = STATE_IDLE;
    }
}
