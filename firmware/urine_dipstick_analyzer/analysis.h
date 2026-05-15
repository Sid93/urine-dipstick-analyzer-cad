#pragma once
#include <Preferences.h>
#include "config.h"
#include "camera.h"

struct PadROI {
    int x, y, w, h;
};

struct PadReading {
    float r, g, b;
    float h, s, v;
    float concentration;
    int category;          // 0=neg, 1=trace, 2=1+, 3=2+, 4=3+, 5=4+
    const char* catLabel;
};

struct CalCoefficients {
    float a0, a1, a2, a3;  // polynomial: conc = a0 + a1*H + a2*H^2 + a3*H^3
};

static const char* CAT_LABELS[] = {"NEG", "TRACE", "1+", "2+", "3+", "4+"};

static const char* PAD_NAMES_ARR[] = {"GLU","PRO","pH","SG","KET","BIL","URO","BLD","NIT","LEU"};

static const char* PAD_UNITS[] = {
    "mg/dL",  // Glucose
    "mg/dL",  // Protein
    "",       // pH
    "",       // Specific Gravity
    "mg/dL",  // Ketones
    "mg/dL",  // Bilirubin
    "mg/dL",  // Urobilinogen
    "RBC/uL", // Blood
    "",       // Nitrite (pos/neg)
    "WBC/uL"  // Leukocytes
};

// Default calibration thresholds (Hue-based boundaries for each pad)
// These are initial values; real calibration replaces them via NVS
static const float DEFAULT_HUE_THRESHOLDS[NUM_PADS][CAL_LEVELS] = {
    // GLU:  neg(yellow-green) -> pos(brown)
    {80, 65, 50, 35, 25, 15},
    // PRO:  neg(yellow) -> pos(green-blue)
    {55, 70, 100, 140, 170, 200},
    // pH:   continuous range (orange=5 -> blue=9)
    {30, 50, 80, 120, 160, 200},
    // SG:   neg(blue-green) -> pos(yellow-green)
    {180, 150, 120, 90, 70, 50},
    // KET:  neg(beige) -> pos(purple)
    {40, 60, 120, 200, 250, 290},
    // BIL:  neg(cream) -> pos(tan-brown)
    {45, 40, 35, 28, 20, 12},
    // URO:  neg(light pink) -> pos(dark pink/red)
    {350, 340, 330, 320, 310, 300},
    // BLD:  neg(yellow) -> pos(green dots -> dark green)
    {55, 70, 100, 130, 150, 170},
    // NIT:  neg(white) -> pos(pink)
    {0, 330, 320, 310, 300, 290},
    // LEU:  neg(cream) -> pos(purple)
    {45, 60, 120, 200, 240, 280},
};

static const float DEFAULT_CONC_LEVELS[NUM_PADS][CAL_LEVELS] = {
    {0, 50, 100, 250, 500, 1000},     // GLU mg/dL
    {0, 15, 30, 100, 300, 500},       // PRO mg/dL
    {5.0, 6.0, 6.5, 7.0, 8.0, 9.0},  // pH
    {1.000, 1.005, 1.010, 1.015, 1.020, 1.030},  // SG
    {0, 5, 15, 40, 80, 160},          // KET mg/dL
    {0, 0.5, 1.0, 3.0, 6.0, 12.0},   // BIL mg/dL
    {0.2, 1.0, 2.0, 4.0, 8.0, 12.0}, // URO mg/dL
    {0, 5, 25, 50, 150, 250},         // BLD RBC/uL
    {0, 0, 0, 1, 1, 1},              // NIT (0=neg, 1=pos)
    {0, 15, 25, 75, 250, 500},        // LEU WBC/uL
};

class Analysis {
public:
    PadROI rois[NUM_PADS];
    PadReading readings[NUM_PADS];
    CalCoefficients calCoeffs[NUM_PADS];
    float whiteRef[3] = {255, 255, 255};  // R, G, B white reference

    // ROI positions along the strip (adjusted during calibration)
    void initDefaultROIs() {
        // 10 pads evenly spaced along 80mm channel
        // In 320px image, 80mm maps to roughly 240px
        int startX = 40;  // left margin in image
        int spacing = 22; // px between pad centers
        int y = (CAM_HEIGHT / 2) - (PAD_ROI_H / 2);

        for (int i = 0; i < NUM_PADS; i++) {
            rois[i].x = startX + i * spacing;
            rois[i].y = y;
            rois[i].w = PAD_ROI_W;
            rois[i].h = PAD_ROI_H;
        }
    }

    // Capture white reference from blank pad area
    void captureWhiteReference(Camera &cam) {
        camera_fb_t *fb = cam.capture();
        if (!fb) return;

        // Use center of image as white reference area
        float r, g, b;
        cam.getROI_RGB(fb, CAM_WIDTH/2 - 15, CAM_HEIGHT/2 - 8, 30, 16, r, g, b);
        whiteRef[0] = r;
        whiteRef[1] = g;
        whiteRef[2] = b;
        cam.release(fb);
    }

    // Analyze all pads from a captured frame
    bool analyzeStrip(Camera &cam) {
        camera_fb_t *fb = cam.capture();
        if (!fb) return false;

        for (int i = 0; i < NUM_PADS; i++) {
            float r, g, b;
            if (!cam.getROI_RGB(fb, rois[i].x, rois[i].y,
                                rois[i].w, rois[i].h, r, g, b)) {
                cam.release(fb);
                return false;
            }

            // White-balance normalize
            readings[i].r = (whiteRef[0] > 0) ? (r / whiteRef[0]) * 255.0f : r;
            readings[i].g = (whiteRef[1] > 0) ? (g / whiteRef[1]) * 255.0f : g;
            readings[i].b = (whiteRef[2] > 0) ? (b / whiteRef[2]) * 255.0f : b;

            readings[i].r = constrain(readings[i].r, 0, 255);
            readings[i].g = constrain(readings[i].g, 0, 255);
            readings[i].b = constrain(readings[i].b, 0, 255);

            Camera::rgb_to_hsv(readings[i].r, readings[i].g, readings[i].b,
                               readings[i].h, readings[i].s, readings[i].v);

            classifyPad(i);
        }

        cam.release(fb);
        return true;
    }

    void classifyPad(int padIdx) {
        float hue = readings[padIdx].h;

        // Find which calibration bracket the hue falls into
        int cat = 0;
        const float *thresholds = DEFAULT_HUE_THRESHOLDS[padIdx];
        const float *concLevels = DEFAULT_CONC_LEVELS[padIdx];

        // Determine if hue increases or decreases with concentration
        bool ascending = thresholds[CAL_LEVELS-1] > thresholds[0];

        if (ascending) {
            for (int lvl = CAL_LEVELS - 1; lvl >= 0; lvl--) {
                if (hue >= thresholds[lvl]) {
                    cat = lvl;
                    break;
                }
            }
        } else {
            for (int lvl = CAL_LEVELS - 1; lvl >= 0; lvl--) {
                if (hue <= thresholds[lvl]) {
                    cat = lvl;
                    break;
                }
            }
        }

        readings[padIdx].category = cat;
        readings[padIdx].catLabel = CAT_LABELS[min(cat, 5)];
        readings[padIdx].concentration = concLevels[cat];
    }

    // Save calibration to NVS flash
    bool saveCalibration() {
        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, false)) return false;

        for (int i = 0; i < NUM_PADS; i++) {
            char key[16];
            snprintf(key, sizeof(key), "wr%d", i);
            prefs.putFloat(key, whiteRef[0]);
        }
        prefs.putFloat("wr_r", whiteRef[0]);
        prefs.putFloat("wr_g", whiteRef[1]);
        prefs.putFloat("wr_b", whiteRef[2]);
        prefs.putBool("calibrated", true);
        prefs.end();
        return true;
    }

    bool loadCalibration() {
        Preferences prefs;
        if (!prefs.begin(NVS_NAMESPACE, true)) return false;

        if (!prefs.getBool("calibrated", false)) {
            prefs.end();
            return false;
        }

        whiteRef[0] = prefs.getFloat("wr_r", 255);
        whiteRef[1] = prefs.getFloat("wr_g", 255);
        whiteRef[2] = prefs.getFloat("wr_b", 255);
        prefs.end();
        return true;
    }
};
