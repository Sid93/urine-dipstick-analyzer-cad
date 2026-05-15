#pragma once
#include <AccelStepper.h>
#include "config.h"

class TrayMotor {
public:
    AccelStepper motor;
    bool isHomed = false;

    TrayMotor()
        : motor(AccelStepper::DRIVER, STEPPER_STEP, STEPPER_DIR) {}

    void begin() {
        motor.setMaxSpeed(STEPPER_MAX_SPEED);
        motor.setAcceleration(STEPPER_ACCEL);
        if (STEPPER_ENABLE >= 0) {
            pinMode(STEPPER_ENABLE, OUTPUT);
            digitalWrite(STEPPER_ENABLE, LOW);
        }
        pinMode(PIN_LIMIT_SW, INPUT_PULLUP);
    }

    long mmToSteps(float mm) {
        return (long)(mm / LEAD_SCREW_PITCH_MM * STEPS_PER_REV * MICROSTEPS);
    }

    bool home() {
        motor.setMaxSpeed(HOME_SPEED);
        motor.moveTo(-mmToSteps(TRAY_TRAVEL_MM + 20));

        while (motor.distanceToGo() != 0) {
            if (digitalRead(PIN_LIMIT_SW) == LOW) {
                motor.stop();
                motor.setCurrentPosition(0);
                isHomed = true;
                motor.setMaxSpeed(STEPPER_MAX_SPEED);
                return true;
            }
            motor.run();
        }
        motor.setMaxSpeed(STEPPER_MAX_SPEED);
        return false;
    }

    void moveTo_mm(float mm) {
        motor.moveTo(mmToSteps(mm));
    }

    void moveToCapture() {
        moveTo_mm(TRAY_TRAVEL_MM / 2.0f);
    }

    void moveToHome() {
        moveTo_mm(0);
    }

    void moveToEject() {
        moveTo_mm(TRAY_TRAVEL_MM);
    }

    bool isAtTarget() {
        return motor.distanceToGo() == 0;
    }

    void update() {
        motor.run();
    }

    void disable() {
        if (STEPPER_ENABLE >= 0) {
            digitalWrite(STEPPER_ENABLE, HIGH);
        }
    }

    void enable() {
        if (STEPPER_ENABLE >= 0) {
            digitalWrite(STEPPER_ENABLE, LOW);
        }
    }
};
