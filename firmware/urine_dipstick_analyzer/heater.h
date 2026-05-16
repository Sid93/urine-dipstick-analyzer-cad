#pragma once
#include "config.h"

class HeaterPID {
public:
    float setpoint = HEATER_TARGET_C;
    float kp = HEATER_KP;
    float ki = HEATER_KI;
    float kd = HEATER_KD;

    bool enabled = false;
    int dutyCycle = 0;

    static constexpr int LEDC_CH = 0;
    void begin() {
        ledcSetup(LEDC_CH, 1000, 8);
        ledcAttachPin(PIN_HEATER_GATE, LEDC_CH);
        ledcWrite(LEDC_CH, 0);
    }

    void enable() {
        enabled = true;
        _integral = 0;
        _lastError = 0;
        _lastTime = millis();
    }

    void disable() {
        enabled = false;
        dutyCycle = 0;
        ledcWrite(LEDC_CH,0);
    }

    bool update(float currentTemp) {
        if (!enabled) return false;

        if (currentTemp > HEATER_OVERTEMP_C) {
            disable();
            return false;
        }

        unsigned long now = millis();
        float dt = (now - _lastTime) / 1000.0f;
        if (dt < 0.1f) return true;
        _lastTime = now;

        float error = setpoint - currentTemp;
        _integral += error * dt;
        _integral = constrain(_integral, -50, 50);
        float derivative = (error - _lastError) / dt;
        _lastError = error;

        float output = kp * error + ki * _integral + kd * derivative;
        dutyCycle = constrain((int)output, 0, HEATER_MAX_DUTY);
        ledcWrite(LEDC_CH,dutyCycle);

        return true;
    }

    bool isAtTemp(float currentTemp, float tolerance = 0.5f) {
        return abs(currentTemp - setpoint) < tolerance;
    }

private:
    float _integral = 0;
    float _lastError = 0;
    unsigned long _lastTime = 0;
};
