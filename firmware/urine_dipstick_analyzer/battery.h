#pragma once
#include <Wire.h>
#include "config.h"

class BatteryGauge {
public:
    float voltage = 0;
    float soc = 0;        // state of charge (0-100%)
    float chargeRate = 0;  // %/hr

    bool begin() {
        Wire.beginTransmission(MAX17048_ADDR);
        if (Wire.endTransmission() != 0) return false;

        // Quick-start for fast initial SOC estimate
        writeRegister(0x06, 0x4000);
        _ready = true;
        return true;
    }

    void update() {
        if (!_ready) return;
        voltage = readVoltage();
        soc = readSOC();
        chargeRate = readChargeRate();
    }

    bool isLow() { return soc <= BATT_LOW_PCT && soc > BATT_CRITICAL_PCT; }
    bool isCritical() { return soc <= BATT_CRITICAL_PCT; }

    int getBatteryIcon() {
        if (soc > 75) return 4;
        if (soc > 50) return 3;
        if (soc > 25) return 2;
        if (soc > 10) return 1;
        return 0;
    }

private:
    bool _ready = false;

    float readVoltage() {
        uint16_t raw = readRegister(0x02);
        return raw * 78.125f / 1000000.0f;
    }

    float readSOC() {
        uint16_t raw = readRegister(0x04);
        return raw / 256.0f;
    }

    float readChargeRate() {
        uint16_t raw = readRegister(0x16);
        int16_t signed_raw = (int16_t)raw;
        return signed_raw * 0.208f;
    }

    uint16_t readRegister(uint8_t reg) {
        Wire.beginTransmission(MAX17048_ADDR);
        Wire.write(reg);
        Wire.endTransmission(false);
        Wire.requestFrom((uint8_t)MAX17048_ADDR, (uint8_t)2);
        uint16_t val = (Wire.read() << 8) | Wire.read();
        return val;
    }

    void writeRegister(uint8_t reg, uint16_t val) {
        Wire.beginTransmission(MAX17048_ADDR);
        Wire.write(reg);
        Wire.write((uint8_t)(val >> 8));
        Wire.write((uint8_t)(val & 0xFF));
        Wire.endTransmission();
    }
};
