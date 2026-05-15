#pragma once
#include <Wire.h>
#include <Adafruit_SHT31.h>
#include <BH1750.h>
#include "config.h"

class Sensors {
public:
    Adafruit_SHT31 sht31;
    BH1750 lightMeter;

    float temperature = 0;
    float humidity = 0;
    float lux = 0;
    float trayTempC = 0;

    bool beginSHT31() {
        return sht31.begin(SHT31_ADDR);
    }

    bool beginBH1750() {
        return lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE, BH1750_ADDR);
    }

    void readAll() {
        temperature = sht31.readTemperature();
        humidity = sht31.readHumidity();
        lux = lightMeter.readLightLevel();
        trayTempC = readThermistor();
    }

    float readThermistor() {
        int raw = analogRead(PIN_THERMISTOR);
        if (raw == 0) return -999;
        float resistance = THERM_SERIES_R / ((4095.0f / raw) - 1.0f);
        float steinhart = resistance / THERM_NOMINAL_R;
        steinhart = log(steinhart);
        steinhart /= THERM_BCOEFF;
        steinhart += 1.0f / (THERM_NOMINAL_T + 273.15f);
        steinhart = 1.0f / steinhart;
        return steinhart - 273.15f;
    }

    bool isAmbientLightOK() {
        return lux < 50.0f;
    }

    bool isTemperatureOK() {
        return temperature > 10.0f && temperature < 40.0f;
    }

    bool isHumidityOK() {
        return humidity < 85.0f;
    }
};
