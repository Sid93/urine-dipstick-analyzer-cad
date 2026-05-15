#pragma once
#include "config.h"

class LEDController {
public:
    void begin() {
        // White LED (on/off via digital pin)
        pinMode(PIN_WHITE_LED, OUTPUT);
        digitalWrite(PIN_WHITE_LED, LOW);

        // RGB status LED (common anode: LOW = ON)
        pinMode(PIN_RGB_RED, OUTPUT);
        pinMode(PIN_RGB_GREEN, OUTPUT);
        pinMode(PIN_RGB_BLUE, OUTPUT);
        rgbOff();

        // Fan
        pinMode(PIN_FAN_GATE, OUTPUT);
        digitalWrite(PIN_FAN_GATE, LOW);

        // Buzzer
        pinMode(PIN_BUZZER, OUTPUT);
        digitalWrite(PIN_BUZZER, LOW);
    }

    // --- White LED ---
    void whiteLedOn()  { digitalWrite(PIN_WHITE_LED, HIGH); }
    void whiteLedOff() { digitalWrite(PIN_WHITE_LED, LOW);  }

    // --- RGB Status LED (common anode: LOW = ON) ---
    void rgbOff() {
        digitalWrite(PIN_RGB_RED, HIGH);
        digitalWrite(PIN_RGB_GREEN, HIGH);
        digitalWrite(PIN_RGB_BLUE, HIGH);
    }

    void rgbRed() {
        digitalWrite(PIN_RGB_RED, LOW);
        digitalWrite(PIN_RGB_GREEN, HIGH);
        digitalWrite(PIN_RGB_BLUE, HIGH);
    }

    void rgbGreen() {
        digitalWrite(PIN_RGB_RED, HIGH);
        digitalWrite(PIN_RGB_GREEN, LOW);
        digitalWrite(PIN_RGB_BLUE, HIGH);
    }

    void rgbBlue() {
        digitalWrite(PIN_RGB_RED, HIGH);
        digitalWrite(PIN_RGB_GREEN, HIGH);
        digitalWrite(PIN_RGB_BLUE, LOW);
    }

    void rgbYellow() {
        digitalWrite(PIN_RGB_RED, LOW);
        digitalWrite(PIN_RGB_GREEN, LOW);
        digitalWrite(PIN_RGB_BLUE, HIGH);
    }

    void rgbPurple() {
        digitalWrite(PIN_RGB_RED, LOW);
        digitalWrite(PIN_RGB_GREEN, HIGH);
        digitalWrite(PIN_RGB_BLUE, LOW);
    }

    void rgbWhite() {
        digitalWrite(PIN_RGB_RED, LOW);
        digitalWrite(PIN_RGB_GREEN, LOW);
        digitalWrite(PIN_RGB_BLUE, LOW);
    }

    // --- Fan ---
    void fanOn()  { digitalWrite(PIN_FAN_GATE, HIGH); }
    void fanOff() { digitalWrite(PIN_FAN_GATE, LOW);  }

    // --- Buzzer ---
    void beepShort() {
        digitalWrite(PIN_BUZZER, HIGH);
        delay(100);
        digitalWrite(PIN_BUZZER, LOW);
    }

    void beepLong() {
        digitalWrite(PIN_BUZZER, HIGH);
        delay(500);
        digitalWrite(PIN_BUZZER, LOW);
    }

    void beepSuccess() {
        for (int i = 0; i < 2; i++) {
            digitalWrite(PIN_BUZZER, HIGH);
            delay(80);
            digitalWrite(PIN_BUZZER, LOW);
            delay(80);
        }
    }

    void beepError() {
        for (int i = 0; i < 3; i++) {
            digitalWrite(PIN_BUZZER, HIGH);
            delay(200);
            digitalWrite(PIN_BUZZER, LOW);
            delay(100);
        }
    }
};
