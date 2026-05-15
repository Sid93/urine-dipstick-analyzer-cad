#pragma once
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include "config.h"

#define TFT_W 320
#define TFT_H 240

// Color palette (RGB565)
#define COL_BG         0x0000  // black
#define COL_HEADER     0x1A3A  // dark navy
#define COL_TEXT       0xFFFF  // white
#define COL_TEXT_DIM   0xBDF7  // light grey
#define COL_ACCENT     0x07FF  // cyan
#define COL_GREEN      0x07E0
#define COL_YELLOW     0xFFE0
#define COL_ORANGE     0xFD20
#define COL_RED        0xF800
#define COL_PURPLE     0xF81F
#define COL_BLUE       0x001F
#define COL_DIVIDER    0x4228  // dark grey
#define COL_BAR_BG     0x2104  // very dark grey
#define COL_NORMAL     0x07E0  // green
#define COL_ELEVATED   0xFFE0  // yellow
#define COL_HIGH       0xFD20  // orange
#define COL_CRITICAL   0xF800  // red

class Display {
public:
    Adafruit_ILI9341 tft;

    Display() : tft(TFT_CS, TFT_DC, TFT_RST) {}

    bool begin() {
        tft.begin();
        tft.setRotation(1); // landscape
        tft.fillScreen(COL_BG);
        return true;
    }

    // ── Status Bar (top 24px, shown on most screens) ──
    void drawStatusBar(float battPct, const char* timeStr) {
        tft.fillRect(0, 0, TFT_W, 24, COL_HEADER);

        // Battery icon
        int bx = TFT_W - 34;
        uint16_t battCol = battPct > 25 ? COL_GREEN : (battPct > 10 ? COL_YELLOW : COL_RED);
        tft.drawRect(bx, 5, 24, 14, COL_TEXT);
        tft.fillRect(bx + 24, 9, 3, 6, COL_TEXT);
        int fill = (int)(battPct * 20.0f / 100.0f);
        if (fill > 0) tft.fillRect(bx + 2, 7, fill, 10, battCol);

        // Battery percentage
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT);
        tft.setCursor(bx - 30, 8);
        tft.printf("%.0f%%", battPct);

        // Time
        tft.setCursor(6, 8);
        tft.setTextColor(COL_ACCENT);
        tft.print(timeStr);
    }

    // ── Splash Screen ──
    void showSplash() {
        tft.fillScreen(COL_BG);
        tft.setTextSize(3);
        tft.setTextColor(COL_ACCENT);
        centerText("DIPSTICK", 50);
        tft.setTextSize(3);
        tft.setTextColor(COL_TEXT);
        centerText("ANALYZER", 85);
        tft.drawLine(60, 120, 260, 120, COL_DIVIDER);
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        centerText("v2.0  |  10-Parameter Urine Analysis", 135);
        tft.setTextSize(1);
        tft.setTextColor(COL_YELLOW);
        centerText("Initializing hardware...", 200);
    }

    // ── Ready / Idle Screen ──
    void showReady(float battPct, const char* timeStr, uint32_t testCount) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.fillRoundRect(30, 60, 260, 80, 8, COL_HEADER);
        tft.setTextSize(3);
        tft.setTextColor(COL_GREEN);
        centerText("READY", 80);
        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        centerText("Insert strip & press", 115);

        tft.drawLine(30, 160, 290, 160, COL_DIVIDER);
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        tft.setCursor(30, 170);
        tft.printf("Tests completed: %lu", (unsigned long)testCount);
        tft.setCursor(30, 185);
        tft.print("Hold 3s for calibration mode");
    }

    // ── Generic Status ──
    void showStatus(const char* line1, const char* line2 = nullptr) {
        tft.fillScreen(COL_BG);
        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        centerText(line1, 90);
        if (line2) {
            tft.setTextSize(2);
            tft.setTextColor(COL_ACCENT);
            centerText(line2, 125);
        }
    }

    // ── Measuring Progress ──
    void showMeasuring(int step, int total, const char* stepLabel) {
        tft.fillScreen(COL_BG);

        tft.setTextSize(2);
        tft.setTextColor(COL_ACCENT);
        centerText("MEASURING", 40);

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT);
        centerText(stepLabel, 70);

        // Step indicator
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        char stepBuf[16];
        snprintf(stepBuf, sizeof(stepBuf), "Step %d of %d", step, total);
        centerText(stepBuf, 100);

        // Progress bar
        int barX = 30, barY = 120, barW = 260, barH = 20;
        tft.fillRoundRect(barX, barY, barW, barH, 4, COL_BAR_BG);
        int fillW = (int)((float)step / total * barW);
        if (fillW > 0) {
            uint16_t barCol = (step == total) ? COL_GREEN : COL_ACCENT;
            tft.fillRoundRect(barX, barY, fillW, barH, 4, barCol);
        }

        // Percentage
        int pct = step * 100 / total;
        char pctBuf[8];
        snprintf(pctBuf, sizeof(pctBuf), "%d%%", pct);
        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        centerText(pctBuf, 155);

        // Step dots
        int dotY = 190;
        int dotSpacing = barW / total;
        for (int i = 0; i < total; i++) {
            int cx = barX + dotSpacing / 2 + i * dotSpacing;
            if (i < step) {
                tft.fillCircle(cx, dotY, 5, COL_GREEN);
            } else if (i == step) {
                tft.fillCircle(cx, dotY, 5, COL_ACCENT);
            } else {
                tft.drawCircle(cx, dotY, 5, COL_DIVIDER);
            }
        }
    }

    // ── Results Screen (color-coded, paginated) ──
    void showResults(const char* padNames[], float values[], const char* categories[],
                     int count, int page, float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        int maxPages = (count + 4) / 5;

        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        tft.setCursor(10, 30);
        tft.print("RESULTS");
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        tft.setCursor(250, 35);
        tft.printf("Page %d/%d", page + 1, maxPages);
        tft.drawLine(10, 50, 310, 50, COL_DIVIDER);

        // Column headers
        tft.setTextSize(1);
        tft.setTextColor(COL_ACCENT);
        tft.setCursor(15, 58);
        tft.print("ANALYTE");
        tft.setCursor(120, 58);
        tft.print("VALUE");
        tft.setCursor(220, 58);
        tft.print("STATUS");
        tft.drawLine(10, 68, 310, 68, COL_DIVIDER);

        int start = page * 5;
        int end = min(start + 5, count);
        for (int i = start; i < end; i++) {
            int y = 76 + (i - start) * 32;
            uint16_t catColor = categoryColor(categories[i]);

            // Alternating row background
            if ((i - start) % 2 == 0) {
                tft.fillRect(10, y - 2, 300, 28, 0x0841);
            }

            // Color indicator dot
            tft.fillCircle(22, y + 10, 6, catColor);

            // Pad name
            tft.setTextSize(2);
            tft.setTextColor(COL_TEXT);
            tft.setCursor(35, y + 3);
            tft.print(padNames[i]);

            // Value
            tft.setCursor(120, y + 3);
            tft.printf("%.1f", values[i]);

            // Category label
            tft.setTextSize(1);
            tft.setTextColor(catColor);
            tft.setCursor(220, y + 6);
            tft.print(categories[i]);
        }

        // Navigation hint
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        centerText("Press button for next page", 225);
    }

    // ── Preheat Screen ──
    void showPreheat(float currentTemp, float targetTemp, float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.setTextSize(2);
        tft.setTextColor(COL_YELLOW);
        centerText("PREHEATING", 40);

        // Temperature gauge
        int gaugeX = 100, gaugeY = 70, gaugeW = 120, gaugeH = 80;
        tft.drawRoundRect(gaugeX, gaugeY, gaugeW, gaugeH, 6, COL_DIVIDER);

        tft.setTextSize(3);
        tft.setTextColor(COL_TEXT);
        char tempBuf[8];
        snprintf(tempBuf, sizeof(tempBuf), "%.1f", currentTemp);
        centerText(tempBuf, gaugeY + 15);

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        char targetBuf[24];
        snprintf(targetBuf, sizeof(targetBuf), "Target: %.1f C", targetTemp);
        centerText(targetBuf, gaugeY + 55);

        // Progress bar (temperature as fraction of target)
        int barX = 40, barY = 170, barW = 240, barH = 14;
        float pct = min(currentTemp / targetTemp, 1.0f);
        tft.fillRoundRect(barX, barY, barW, barH, 3, COL_BAR_BG);
        int fillW = (int)(pct * barW);
        uint16_t barCol = (pct >= 1.0f) ? COL_GREEN : COL_ORANGE;
        if (fillW > 0) tft.fillRoundRect(barX, barY, fillW, barH, 3, barCol);
    }

    // ── Environment Screen ──
    void showEnvironment(float tempC, float humidity, float luxVal,
                         float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        tft.setCursor(10, 30);
        tft.print("ENVIRONMENT");
        tft.drawLine(10, 50, 310, 50, COL_DIVIDER);

        drawEnvRow(60,  "TEMP",     tempC,    "C",   tempC > 10 && tempC < 40);
        drawEnvRow(105, "HUMIDITY", humidity,  "%",   humidity < 85);
        drawEnvRow(150, "LIGHT",    luxVal,   "lux", luxVal < 50);
    }

    // ── Calibration Screen ──
    void showCalibration(int padIdx, int level, const char* padName,
                         float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.setTextSize(2);
        tft.setTextColor(COL_PURPLE);
        centerText("CALIBRATION", 35);
        tft.drawLine(10, 55, 310, 55, COL_DIVIDER);

        // Pad info
        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        tft.setCursor(30, 70);
        tft.printf("Pad: %s", padName);
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        tft.setCursor(30, 95);
        tft.printf("Analyte %d of %d", padIdx + 1, NUM_PADS);

        // Level indicator boxes
        int boxX = 30, boxY = 120;
        for (int i = 0; i < CAL_LEVELS; i++) {
            uint16_t col = (i < level) ? COL_GREEN : ((i == level) ? COL_ACCENT : COL_BAR_BG);
            tft.fillRoundRect(boxX + i * 45, boxY, 38, 24, 4, col);
            tft.setTextSize(1);
            tft.setTextColor(COL_TEXT);
            tft.setCursor(boxX + i * 45 + 12, boxY + 8);
            tft.printf("L%d", i + 1);
        }

        tft.setTextSize(2);
        tft.setTextColor(COL_YELLOW);
        centerText("Insert cal strip", 170);
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        centerText("Press MEASURE when ready", 200);
    }

    // ── Error Screen ──
    void showError(const char* msg, float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.fillRoundRect(20, 50, 280, 100, 8, 0x4000);
        tft.drawRoundRect(20, 50, 280, 100, 8, COL_RED);

        tft.setTextSize(2);
        tft.setTextColor(COL_RED);
        centerText("ERROR", 65);

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT);
        centerText(msg, 105);

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        centerText("Press button to reset", 175);
    }

    // ── UV Sterilization Screen ──
    void showUVSterilizing(int pctDone, float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.setTextSize(2);
        tft.setTextColor(COL_PURPLE);
        centerText("UV STERILIZING", 40);

        tft.setTextSize(1);
        tft.setTextColor(COL_RED);
        centerText("! DO NOT OPEN TRAY !", 70);

        // Large percentage
        tft.setTextSize(4);
        tft.setTextColor(COL_TEXT);
        char pctBuf[8];
        snprintf(pctBuf, sizeof(pctBuf), "%d%%", pctDone);
        centerText(pctBuf, 100);

        // Progress bar
        int barX = 30, barY = 160, barW = 260, barH = 20;
        tft.fillRoundRect(barX, barY, barW, barH, 4, COL_BAR_BG);
        int fillW = (int)((float)pctDone / 100.0f * barW);
        if (fillW > 0) tft.fillRoundRect(barX, barY, fillW, barH, 4, COL_PURPLE);

        // Time remaining
        int secLeft = (100 - pctDone) * UV_CYCLE_MS / 100 / 1000;
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        tft.setCursor(120, 195);
        tft.printf("~%ds remaining", secLeft);
    }

    // ── Low Battery Warning ──
    void showLowBattery(float battPct) {
        tft.fillRoundRect(60, 80, 200, 80, 8, 0x4000);
        tft.drawRoundRect(60, 80, 200, 80, 8, COL_RED);
        tft.setTextSize(2);
        tft.setTextColor(COL_RED);
        centerText("LOW BATTERY", 95);
        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT);
        char buf[24];
        snprintf(buf, sizeof(buf), "%.0f%% - Charge soon", battPct);
        centerText(buf, 130);
    }

    // ── Barcode Scan Screen ──
    void showScanBarcode(float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.setTextSize(2);
        tft.setTextColor(COL_ACCENT);
        centerText("SCAN BARCODE", 60);

        // Barcode icon (stylized bars)
        int bx = 120, by = 95;
        int barWidths[] = {3,2,4,2,3,5,2,3,4,2,3,2,4};
        int x = bx;
        for (int i = 0; i < 13; i++) {
            if (i % 2 == 0) tft.fillRect(x, by, barWidths[i], 40, COL_TEXT);
            x += barWidths[i] + 1;
        }

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        centerText("Scan patient ID or press to skip", 155);

        // Countdown hint
        tft.setTextColor(COL_YELLOW);
        centerText("Auto-skip in 5 seconds", 180);
    }

    // ── Venting Screen ──
    void showVenting(float humidity, float battPct, const char* timeStr) {
        tft.fillScreen(COL_BG);
        drawStatusBar(battPct, timeStr);

        tft.setTextSize(2);
        tft.setTextColor(COL_ACCENT);
        centerText("VENTING", 60);

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        centerText("Cooling and dehumidifying...", 90);

        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        char humBuf[16];
        snprintf(humBuf, sizeof(humBuf), "%.1f%%", humidity);
        centerText(humBuf, 130);

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        centerText("Humidity", 160);
    }

private:
    void centerText(const char* text, int y) {
        int16_t x1, y1;
        uint16_t w, h;
        tft.getTextBounds(text, 0, 0, &x1, &y1, &w, &h);
        tft.setCursor((TFT_W - w) / 2, y);
        tft.print(text);
    }

    uint16_t categoryColor(const char* cat) {
        if (!cat) return COL_TEXT_DIM;
        if (strcmp(cat, "Normal") == 0 || strcmp(cat, "Negative") == 0) return COL_NORMAL;
        if (strcmp(cat, "Trace") == 0)    return COL_ELEVATED;
        if (strcmp(cat, "Low") == 0)      return COL_ELEVATED;
        if (strcmp(cat, "Moderate") == 0) return COL_HIGH;
        if (strcmp(cat, "High") == 0)     return COL_CRITICAL;
        if (strcmp(cat, "Very High") == 0) return COL_CRITICAL;
        if (strcmp(cat, "Positive") == 0) return COL_RED;
        return COL_TEXT;
    }

    void drawEnvRow(int y, const char* label, float value, const char* unit, bool ok) {
        tft.fillRoundRect(15, y, 290, 35, 4, 0x0841);
        uint16_t dotCol = ok ? COL_GREEN : COL_RED;
        tft.fillCircle(30, y + 17, 6, dotCol);

        tft.setTextSize(1);
        tft.setTextColor(COL_TEXT_DIM);
        tft.setCursor(45, y + 6);
        tft.print(label);

        tft.setTextSize(2);
        tft.setTextColor(COL_TEXT);
        tft.setCursor(145, y + 7);
        tft.printf("%.1f %s", value, unit);

        tft.setTextSize(1);
        tft.setTextColor(ok ? COL_GREEN : COL_RED);
        tft.setCursor(270, y + 12);
        tft.print(ok ? "OK" : "!");
    }
};
