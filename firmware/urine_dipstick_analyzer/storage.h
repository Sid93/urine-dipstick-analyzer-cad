#pragma once
#include <SD.h>
#include <SPI.h>
#include "config.h"
#include "analysis.h"
#include "rtc.h"

class Storage {
public:
    bool sdReady = false;
    RealTimeClock *rtc = nullptr;

    void setRTC(RealTimeClock *r) { rtc = r; }

    bool begin() {
        SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
        sdReady = SD.begin(SD_CS);
        if (sdReady) {
            ensureHeader();
        }
        return sdReady;
    }

    void ensureHeader() {
        if (!sdReady) return;
        if (SD.exists("/results.csv")) return;

        File f = SD.open("/results.csv", FILE_WRITE);
        if (!f) return;
        f.print("timestamp,patient_id,");
        for (int i = 0; i < NUM_PADS; i++) {
            f.printf("%s_val,%s_cat,", PAD_NAMES_ARR[i], PAD_NAMES_ARR[i]);
        }
        f.print("amb_temp,amb_humid,amb_lux,tray_temp,batt_pct,batt_v");
        f.println();
        f.close();
    }

    bool logResult(const char* patientID, PadReading readings[],
                   float ambTemp, float ambHumid, float ambLux, float trayTemp,
                   float battPct, float battV) {
        if (!sdReady) return false;

        File f = SD.open("/results.csv", FILE_APPEND);
        if (!f) return false;

        char ts[24];
        getTimestamp(ts, sizeof(ts));
        f.printf("%s,%s,", ts, patientID);

        for (int i = 0; i < NUM_PADS; i++) {
            f.printf("%.1f,%s,", readings[i].concentration, readings[i].catLabel);
        }

        f.printf("%.1f,%.1f,%.0f,%.1f,%.0f,%.2f", ambTemp, ambHumid, ambLux, trayTemp, battPct, battV);
        f.println();
        f.close();
        return true;
    }

    bool logRawImage(camera_fb_t *fb, int testNum) {
        if (!sdReady || !fb) return false;

        char path[32];
        snprintf(path, sizeof(path), "/img_%05d.raw", testNum);
        File f = SD.open(path, FILE_WRITE);
        if (!f) return false;
        f.write(fb->buf, fb->len);
        f.close();
        return true;
    }

    bool logCalibrationEvent(const char* msg) {
        if (!sdReady) return false;

        File f = SD.open("/cal_log.txt", FILE_APPEND);
        if (!f) return false;
        char ts[24];
        getTimestamp(ts, sizeof(ts));
        f.printf("[%s] %s\n", ts, msg);
        f.close();
        return true;
    }

    uint32_t getTestCount() {
        if (!sdReady) return 0;
        if (!SD.exists("/test_count.txt")) return 0;

        File f = SD.open("/test_count.txt", FILE_READ);
        if (!f) return 0;
        String s = f.readString();
        f.close();
        return s.toInt();
    }

    void incrementTestCount() {
        if (!sdReady) return;
        uint32_t count = getTestCount() + 1;
        File f = SD.open("/test_count.txt", FILE_WRITE);
        if (!f) return;
        f.printf("%u", count);
        f.close();
    }

private:
    void getTimestamp(char* buf, int maxLen) {
        if (rtc && rtc->isReady()) {
            rtc->formatTimestamp(buf, maxLen);
        } else {
            snprintf(buf, maxLen, "%lu", millis());
        }
    }
};
