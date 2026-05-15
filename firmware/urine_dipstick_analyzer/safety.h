#pragma once
#include "config.h"

class SafetyManager {
public:
    bool uvActive = false;
    unsigned long uvStartTime = 0;

    void begin() {
        pinMode(PIN_REED_SWITCH, INPUT_PULLUP);
        pinMode(PIN_UV_GATE, OUTPUT);
        digitalWrite(PIN_UV_GATE, LOW);
    }

    bool isTrayInserted() {
        return digitalRead(PIN_REED_SWITCH) == LOW;
    }

    bool startUV() {
        if (!isTrayInserted()) return false;
        uvActive = true;
        uvStartTime = millis();
        digitalWrite(PIN_UV_GATE, HIGH);
        return true;
    }

    void stopUV() {
        uvActive = false;
        digitalWrite(PIN_UV_GATE, LOW);
    }

    // Returns 0-100 progress, or -1 if not running
    int updateUV() {
        if (!uvActive) return -1;

        if (!isTrayInserted()) {
            stopUV();
            return -1;
        }

        unsigned long elapsed = millis() - uvStartTime;
        if (elapsed >= UV_CYCLE_MS) {
            stopUV();
            return 100;
        }

        return (int)(elapsed * 100 / UV_CYCLE_MS);
    }

    bool isUVComplete() {
        return !uvActive && (millis() - uvStartTime > UV_CYCLE_MS) && uvStartTime > 0;
    }
};
