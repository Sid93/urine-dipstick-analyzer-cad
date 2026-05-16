// User_Setup.h — TFT_eSPI compatibility shim
//
// This firmware uses Adafruit_ILI9341 (not TFT_eSPI). This file is provided
// as a reference for anyone swapping to TFT_eSPI for higher performance.
// To use it, set lib_deps to bodmer/TFT_eSPI in platformio.ini and add:
//   build_flags = -DUSER_SETUP_LOADED=1 -include "User_Setup.h"

#define ILI9341_2_DRIVER

#define TFT_WIDTH  240
#define TFT_HEIGHT 320

// Pins below match config.h GPIO assignments for the ESP32-S3-DevKitC-1
#define TFT_MISO 38
#define TFT_MOSI 39
#define TFT_SCLK 40
#define TFT_CS   15
#define TFT_DC   16
#define TFT_RST  -1   // tied to ESP32 EN
#define TFT_BL   -1   // backlight tied to 3V3

#define LOAD_GLCD
#define LOAD_FONT2
#define LOAD_FONT4
#define LOAD_FONT6
#define LOAD_FONT7
#define LOAD_FONT8
#define LOAD_GFXFF
#define SMOOTH_FONT

#define SPI_FREQUENCY       40000000
#define SPI_READ_FREQUENCY  20000000
