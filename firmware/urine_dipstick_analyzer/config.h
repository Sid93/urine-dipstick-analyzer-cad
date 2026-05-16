#pragma once

// ============================================================
// PIN DEFINITIONS — ESP32-S3-DevKitC-1-N8R8
// ============================================================

// --- Camera (OV2640 DVP) ---
#define CAM_PIN_PWDN   -1
#define CAM_PIN_RESET  -1
#define CAM_PIN_XCLK   10
#define CAM_PIN_SIOD   11
#define CAM_PIN_SIOC   12
#define CAM_PIN_D7     13
#define CAM_PIN_D6     14
#define CAM_PIN_D5      9
#define CAM_PIN_D4     48
#define CAM_PIN_D3     47
#define CAM_PIN_D2     46
#define CAM_PIN_D1     45
#define CAM_PIN_D0      3
#define CAM_PIN_VSYNC  35
#define CAM_PIN_HREF   36
#define CAM_PIN_PCLK   37

// --- I2C Bus (shared: TFT touch, SHT31, BH1750, DS3231, MAX17048) ---
#define I2C_SDA        19
#define I2C_SCL        18

// --- SPI Bus (SD Card + TFT Display) ---
#define SD_MISO        38
#define SD_MOSI        39
#define SD_SCK         40
#define SD_CS          41

// --- TFT Display (ILI9341 2.4" 320x240, SPI) ---
#define TFT_CS         15
#define TFT_DC         16
#define TFT_RST        -1
#define TFT_MOSI       SD_MOSI
#define TFT_SCK        SD_SCK
#define TFT_MISO       SD_MISO
#define TFT_BL         -1

// --- Stepper Motor (A4988 Driver) ---
#define STEPPER_STEP    4
#define STEPPER_DIR     5
#define STEPPER_ENABLE -1

// --- MOSFET Gates ---
#define PIN_FAN_GATE    2
#define PIN_HEATER_GATE 44  // was 4 (collided with STEPPER_STEP); UART0 RX repurposed, debug via USB-CDC
#define PIN_UV_GATE     20

// --- White LED Array ---
#define PIN_WHITE_LED    6

// --- RGB Status LED (Common Anode, active LOW) ---
#define PIN_RGB_RED      7
#define PIN_RGB_GREEN    8
#define PIN_RGB_BLUE    -1  // dropped: GPIO 17 reassigned to BARCODE_RX; use TFT for status

// --- User Input ---
#define PIN_BUTTON       1

// --- Safety Interlock (Reed Switch) ---
#define PIN_REED_SWITCH 21

// --- Limit Switch (Tray Home) ---
#define PIN_LIMIT_SW    42

// --- Buzzer ---
#define PIN_BUZZER      43

// --- Barcode Scanner (UART) ---
#define BARCODE_TX      0   // was 16 (collided with TFT_DC); strapping pin, UART idle HIGH is compatible
#define BARCODE_RX      17  // was 18 (collided with I2C_SCL); reclaimed from RGB_BLUE (D2 dropped)

// --- Thermistor (ADC) ---
#define PIN_THERMISTOR  A0

// ============================================================
// I2C ADDRESSES
// ============================================================
#define SHT31_ADDR      0x44
#define BH1750_ADDR     0x23
#define DS3231_ADDR     0x68
#define MAX17048_ADDR   0x36

// ============================================================
// BATTERY THRESHOLDS
// ============================================================
#define BATT_LOW_PCT    15
#define BATT_CRITICAL_PCT 5

// ============================================================
// SYSTEM CONSTANTS
// ============================================================

// Stepper motor
#define STEPS_PER_REV       200
#define MICROSTEPS          16
#define LEAD_SCREW_PITCH_MM 8.0f
#define TRAY_TRAVEL_MM      80.0f
#define STEPPER_MAX_SPEED   1000
#define STEPPER_ACCEL       500
#define HOME_SPEED          200

// Heater PID
#define HEATER_TARGET_C     37.0f
#define HEATER_KP           20.0f
#define HEATER_KI           1.0f
#define HEATER_KD           5.0f
#define HEATER_MAX_DUTY     200
#define HEATER_OVERTEMP_C   45.0f

// UV sterilization
#define UV_CYCLE_MS         30000

// Thermistor
#define THERM_NOMINAL_R     10000.0f
#define THERM_NOMINAL_T     25.0f
#define THERM_BCOEFF        3950.0f
#define THERM_SERIES_R      10000.0f

// Camera
#define CAM_WIDTH           320
#define CAM_HEIGHT          240

// Dipstick analysis
#define NUM_PADS            10
#define PAD_NAMES           {"GLU","PRO","pH","SG","KET","BIL","URO","BLD","NIT","LEU"}

// Pad ROI positions (x, y, width, height) in captured image
// These are calibrated for the specific tray/channel geometry
#define PAD_ROI_W           20
#define PAD_ROI_H           12

// Calibration
#define CAL_LEVELS          6
#define NVS_NAMESPACE       "dipstick_cal"
