#pragma once
#include <Wire.h>
#include "config.h"

struct DateTime {
    uint16_t year;
    uint8_t month, day, hour, minute, second;
};

class RealTimeClock {
public:
    DateTime now;

    bool begin() {
        Wire.beginTransmission(DS3231_ADDR);
        if (Wire.endTransmission() != 0) return false;
        _ready = true;
        read();
        return true;
    }

    void read() {
        if (!_ready) return;
        Wire.beginTransmission(DS3231_ADDR);
        Wire.write(0x00);
        Wire.endTransmission();
        Wire.requestFrom((uint8_t)DS3231_ADDR, (uint8_t)7);

        now.second = bcdToDec(Wire.read() & 0x7F);
        now.minute = bcdToDec(Wire.read());
        now.hour   = bcdToDec(Wire.read() & 0x3F);
        Wire.read(); // day of week
        now.day    = bcdToDec(Wire.read());
        now.month  = bcdToDec(Wire.read() & 0x1F);
        now.year   = bcdToDec(Wire.read()) + 2000;
    }

    void set(uint16_t yr, uint8_t mo, uint8_t dy,
             uint8_t hr, uint8_t mn, uint8_t sc) {
        if (!_ready) return;
        Wire.beginTransmission(DS3231_ADDR);
        Wire.write(0x00);
        Wire.write(decToBcd(sc));
        Wire.write(decToBcd(mn));
        Wire.write(decToBcd(hr));
        Wire.write(0x01); // day of week placeholder
        Wire.write(decToBcd(dy));
        Wire.write(decToBcd(mo));
        Wire.write(decToBcd(yr - 2000));
        Wire.endTransmission();
    }

    void formatTimestamp(char* buf, int maxLen) {
        read();
        snprintf(buf, maxLen, "%04d-%02d-%02d %02d:%02d:%02d",
                 now.year, now.month, now.day,
                 now.hour, now.minute, now.second);
    }

    void formatTime(char* buf, int maxLen) {
        snprintf(buf, maxLen, "%02d:%02d", now.hour, now.minute);
    }

    void formatDate(char* buf, int maxLen) {
        snprintf(buf, maxLen, "%04d-%02d-%02d", now.year, now.month, now.day);
    }

    float readTemperature() {
        if (!_ready) return -999;
        Wire.beginTransmission(DS3231_ADDR);
        Wire.write(0x11);
        Wire.endTransmission();
        Wire.requestFrom((uint8_t)DS3231_ADDR, (uint8_t)2);
        int8_t msb = Wire.read();
        uint8_t lsb = Wire.read();
        return msb + (lsb >> 6) * 0.25f;
    }

    bool isReady() { return _ready; }

private:
    bool _ready = false;

    uint8_t bcdToDec(uint8_t val) { return (val / 16 * 10) + (val % 16); }
    uint8_t decToBcd(uint8_t val) { return (val / 10 * 16) + (val % 10); }
};
