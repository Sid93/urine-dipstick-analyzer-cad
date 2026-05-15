#pragma once
#include <HardwareSerial.h>
#include "config.h"

class BarcodeScanner {
public:
    HardwareSerial &port;
    char lastCode[64] = {0};
    bool hasNewCode = false;

    BarcodeScanner(HardwareSerial &serial) : port(serial) {}

    void begin() {
        port.begin(9600, SERIAL_8N1, BARCODE_RX, BARCODE_TX);
    }

    void update() {
        while (port.available()) {
            char c = port.read();
            if (c == '\r' || c == '\n') {
                if (_bufIdx > 0) {
                    _buf[_bufIdx] = '\0';
                    strncpy(lastCode, _buf, sizeof(lastCode) - 1);
                    hasNewCode = true;
                    _bufIdx = 0;
                }
            } else if (_bufIdx < (int)sizeof(_buf) - 1) {
                _buf[_bufIdx++] = c;
            }
        }
    }

    bool read(char* out, int maxLen) {
        if (!hasNewCode) return false;
        strncpy(out, lastCode, maxLen - 1);
        out[maxLen - 1] = '\0';
        hasNewCode = false;
        return true;
    }

    void sendCommand(const uint8_t* cmd, int len) {
        port.write(cmd, len);
    }

    void triggerScan() {
        // GM65 trigger command
        static const uint8_t trigCmd[] = {0x7E, 0x00, 0x08, 0x01, 0x00, 0x02, 0x01, 0xAB, 0xCD};
        sendCommand(trigCmd, sizeof(trigCmd));
    }

private:
    char _buf[64] = {0};
    int _bufIdx = 0;
};
