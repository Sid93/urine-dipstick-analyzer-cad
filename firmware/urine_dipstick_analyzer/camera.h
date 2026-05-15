#pragma once
#include "esp_camera.h"
#include "config.h"

class Camera {
public:
    bool begin() {
        camera_config_t config;
        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer = LEDC_TIMER_0;
        config.pin_d0 = CAM_PIN_D0;
        config.pin_d1 = CAM_PIN_D1;
        config.pin_d2 = CAM_PIN_D2;
        config.pin_d3 = CAM_PIN_D3;
        config.pin_d4 = CAM_PIN_D4;
        config.pin_d5 = CAM_PIN_D5;
        config.pin_d6 = CAM_PIN_D6;
        config.pin_d7 = CAM_PIN_D7;
        config.pin_xclk = CAM_PIN_XCLK;
        config.pin_pclk = CAM_PIN_PCLK;
        config.pin_vsync = CAM_PIN_VSYNC;
        config.pin_href = CAM_PIN_HREF;
        config.pin_sccb_sda = CAM_PIN_SIOD;
        config.pin_sccb_scl = CAM_PIN_SIOC;
        config.pin_pwdn = CAM_PIN_PWDN;
        config.pin_reset = CAM_PIN_RESET;
        config.xclk_freq_hz = 20000000;
        config.pixel_format = PIXFORMAT_RGB565;
        config.frame_size = FRAMESIZE_QVGA;  // 320x240
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.fb_location = CAMERA_FB_IN_PSRAM;
        config.grab_mode = CAMERA_GRAB_LATEST;

        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) return false;

        sensor_t *s = esp_camera_sensor_get();
        if (s) {
            s->set_brightness(s, 0);
            s->set_contrast(s, 0);
            s->set_saturation(s, 0);
            s->set_whitebal(s, 1);
            s->set_awb_gain(s, 1);
            s->set_wb_mode(s, 0);
            s->set_exposure_ctrl(s, 1);
            s->set_gain_ctrl(s, 1);
        }
        return true;
    }

    camera_fb_t* capture() {
        camera_fb_t *fb = esp_camera_fb_get();
        return fb;
    }

    void release(camera_fb_t *fb) {
        if (fb) esp_camera_fb_return(fb);
    }

    // Extract RGB from RGB565 pixel
    static void rgb565_to_rgb(uint16_t pixel, uint8_t &r, uint8_t &g, uint8_t &b) {
        r = ((pixel >> 11) & 0x1F) << 3;
        g = ((pixel >> 5) & 0x3F) << 2;
        b = (pixel & 0x1F) << 3;
    }

    // Get average RGB for a region of interest
    bool getROI_RGB(camera_fb_t *fb, int roiX, int roiY, int roiW, int roiH,
                    float &avgR, float &avgG, float &avgB) {
        if (!fb || fb->format != PIXFORMAT_RGB565) return false;
        if (roiX + roiW > CAM_WIDTH || roiY + roiH > CAM_HEIGHT) return false;

        uint32_t sumR = 0, sumG = 0, sumB = 0;
        int count = 0;
        uint16_t *pixels = (uint16_t *)fb->buf;

        for (int y = roiY; y < roiY + roiH; y++) {
            for (int x = roiX; x < roiX + roiW; x++) {
                uint16_t p = pixels[y * CAM_WIDTH + x];
                // Swap bytes (ESP32 stores big-endian)
                p = (p >> 8) | (p << 8);
                uint8_t r, g, b;
                rgb565_to_rgb(p, r, g, b);
                sumR += r;
                sumG += g;
                sumB += b;
                count++;
            }
        }

        if (count == 0) return false;
        avgR = (float)sumR / count;
        avgG = (float)sumG / count;
        avgB = (float)sumB / count;
        return true;
    }

    // Convert RGB to HSV
    static void rgb_to_hsv(float r, float g, float b,
                           float &h, float &s, float &v) {
        r /= 255.0f; g /= 255.0f; b /= 255.0f;
        float maxC = max(r, max(g, b));
        float minC = min(r, min(g, b));
        float delta = maxC - minC;

        v = maxC;
        s = (maxC > 0) ? (delta / maxC) : 0;

        if (delta == 0) {
            h = 0;
        } else if (maxC == r) {
            h = 60.0f * fmod((g - b) / delta, 6.0f);
        } else if (maxC == g) {
            h = 60.0f * ((b - r) / delta + 2.0f);
        } else {
            h = 60.0f * ((r - g) / delta + 4.0f);
        }
        if (h < 0) h += 360.0f;
    }
};
