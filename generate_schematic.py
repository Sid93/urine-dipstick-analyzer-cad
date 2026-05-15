#!/usr/bin/env python3
"""
Generate a KiCad 8 schematic (.kicad_sch) for a Urine Dipstick Analyzer.

Circuit: ESP32-S3 based, camera-based dipstick analysis with:
- LiPo battery + USB-C charging (MCP73833)
- Dual buck-boost regulators (3.3V and 5V/9V)
- OV2640 camera with CPL filter
- OLED display, BH1750 light sensor, SHT31 humidity sensor
- Stepper motor (NEMA 17 + A4988 driver)
- UV-C LED, heater film, vent fan (MOSFET-switched)
- SD card, barcode scanner, buzzer, RGB LED, safety interlock
"""

import uuid
import os


def uid():
    """Generate a UUID string for KiCad elements."""
    return str(uuid.uuid4())


# ─────────────────────────────────────────────
# Helper functions for KiCad S-expression output
# ─────────────────────────────────────────────

def kicad_text(text, x, y, size=3.0):
    """Section title text annotation."""
    return f'''  (text "{text}"
    (exclude_from_sim no)
    (at {x} {y} 0)
    (effects
      (font
        (size {size} {size})
        (bold yes)
      )
    )
    (uuid "{uid()}")
  )'''


def kicad_wire(x1, y1, x2, y2):
    """A wire segment between two points."""
    return f'''  (wire
    (pts
      (xy {x1} {y1}) (xy {x2} {y2})
    )
    (stroke
      (width 0)
      (type default)
    )
    (uuid "{uid()}")
  )'''


def kicad_label(name, x, y, angle=0):
    """A net label at a point."""
    return f'''  (label "{name}"
    (at {x} {y} {angle})
    (effects
      (font
        (size 1.27 1.27)
      )
    )
    (uuid "{uid()}")
  )'''


def kicad_global_label(name, x, y, angle=0, shape="input"):
    """A global/power label."""
    return f'''  (global_label "{name}"
    (shape {shape})
    (at {x} {y} {angle})
    (effects
      (font
        (size 1.27 1.27)
      )
    )
    (uuid "{uid()}")
  )'''


def kicad_power_symbol(lib_id, ref, x, y, angle=0):
    """A power symbol (GND, +3V3, +5V, +9V, VCC, etc.)."""
    u = uid()
    return f'''  (symbol
    (lib_id "power:{lib_id}")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom no)
    (on_board no)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "#{ref}" (at {x} {y-2} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "{lib_id}" (at {x} {y+2} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
  )'''


def kicad_pwr_flag(x, y, ref_num):
    """PWR_FLAG symbol."""
    u = uid()
    return f'''  (symbol
    (lib_id "power:PWR_FLAG")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom no)
    (on_board no)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "#FLG0{ref_num}" (at {x} {y-3} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "PWR_FLAG" (at {x} {y+3} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
  )'''


def make_resistor(ref, value, x, y, angle=0):
    """Resistor symbol using Device:R."""
    u = uid()
    ref_x = x + 2.54 if angle == 0 else x
    ref_y = y if angle == 0 else y - 2.54
    val_x = ref_x
    val_y = ref_y + 2.54 if angle == 0 else ref_y + 2.54
    return f'''  (symbol
    (lib_id "Device:R")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {ref_x} {ref_y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {val_x} {val_y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def make_capacitor(ref, value, x, y, angle=0):
    """Capacitor symbol using Device:C."""
    u = uid()
    ref_x = x + 2.54 if angle == 0 else x
    ref_y = y if angle == 0 else y - 2.54
    val_x = ref_x
    val_y = ref_y + 2.54 if angle == 0 else ref_y + 2.54
    return f'''  (symbol
    (lib_id "Device:C")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {ref_x} {ref_y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {val_x} {val_y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def make_led(ref, value, x, y, angle=0):
    """LED symbol using Device:LED."""
    u = uid()
    return f'''  (symbol
    (lib_id "Device:LED")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x+2.54} {y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x+2.54} {y+2.54} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def make_mosfet_n(ref, value, x, y):
    """N-Channel MOSFET using Device:Q_NMOS_GDS."""
    u = uid()
    return f'''  (symbol
    (lib_id "Device:Q_NMOS_GDS")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x+5.08} {y-2.54} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x+5.08} {y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
    (pin "3"
      (uuid "{uid()}")
    )
  )'''


def make_switch(ref, value, x, y, angle=0):
    """Switch symbol using Device:SW_Push."""
    u = uid()
    return f'''  (symbol
    (lib_id "Switch:SW_Push")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x} {y-3.81} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x} {y+3.81} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def make_generic_ic(ref, value, x, y, pin_names, pin_count=None):
    """
    Generic rectangular IC block.
    Uses Simulation_SPICE:OPAMP as a stand-in for custom multi-pin ICs,
    but we'll just create them as custom symbols with labeled pins.
    We use a text box approach: symbol + pin labels as text.
    """
    if pin_count is None:
        pin_count = len(pin_names)
    u = uid()
    pins_str = ""
    for i in range(pin_count):
        pins_str += f'''    (pin "{i+1}"
      (uuid "{uid()}")
    )\n'''

    # Put pin labels as nearby text annotations
    pin_labels = ""
    spacing = 2.54
    start_y = y - (pin_count / 2) * spacing
    for i, name in enumerate(pin_names):
        py = start_y + i * spacing
        pin_labels += kicad_text(name, x + 12, py, 1.0) + "\n"

    return f'''  (symbol
    (lib_id "Simulation_SPICE:OPAMP")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x} {y-5.08} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x} {y+5.08} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
{pins_str}  )
{pin_labels}'''


def make_custom_block(ref, value, x, y, left_pins, right_pins):
    """
    Create a custom component as a labeled box with net labels for pins.
    Returns the text annotation for the box title, plus net labels for each pin.
    """
    elements = []
    # Title
    elements.append(kicad_text(f"{ref}: {value}", x, y - 10, 1.5))

    # Left-side pins
    spacing = 5.08
    for i, (pin_name, net_name) in enumerate(left_pins):
        py = y + i * spacing
        elements.append(kicad_text(pin_name, x - 8, py, 1.0))
        if net_name:
            elements.append(kicad_label(net_name, x - 2, py, 180))

    # Right-side pins
    for i, (pin_name, net_name) in enumerate(right_pins):
        py = y + i * spacing
        elements.append(kicad_text(pin_name, x + 15, py, 1.0))
        if net_name:
            elements.append(kicad_label(net_name, x + 12, py, 0))

    return "\n".join(elements)


# ─────────────────────────────────────────────
# Main schematic generation
# ─────────────────────────────────────────────

def generate_schematic():
    elements = []

    # ═══════════════════════════════════════════
    # SECTION 1: POWER SUPPLY (left side)
    # ═══════════════════════════════════════════
    px, py = 25, 30  # base position for power section

    elements.append(kicad_text("=== POWER SUPPLY ===", px + 15, py - 10, 4.0))

    # --- LiPo Battery ---
    elements.append(kicad_text("BT1: LiPo 3.7V 1000mAh", px, py, 1.5))
    elements.append(kicad_label("VBAT", px + 5, py + 5, 0))
    elements.append(kicad_global_label("GND", px + 5, py + 10, 270, "input"))

    # Wire from battery VBAT out
    elements.append(kicad_wire(px + 5, py + 5, px + 25, py + 5))

    # --- USB-C Charger (MCP73833) ---
    cx, cy = px + 30, py
    elements.append(kicad_text("U1: MCP73833 USB-C Charger", cx, cy, 1.5))
    # Input: USB-C VBUS
    elements.append(kicad_label("VUSB", cx, cy + 5, 180))
    # Output: VBAT
    elements.append(kicad_label("VBAT", cx + 25, cy + 5, 0))
    elements.append(kicad_global_label("GND", cx + 12, cy + 15, 270, "input"))
    # Decoupling cap
    elements.append(make_capacitor("C1", "100nF", cx + 5, cy + 12))
    # Wire VBAT out to regulators
    elements.append(kicad_wire(cx + 25, cy + 5, cx + 45, cy + 5))

    # PWR_FLAG on VBAT
    elements.append(kicad_pwr_flag(cx + 30, cy + 2, 1))
    elements.append(kicad_wire(cx + 30, cy + 2, cx + 30, cy + 5))

    # --- Buck-Boost Regulator 5V/9V (Pololu S13V25F9) ---
    rx, ry = px + 80, py - 10
    elements.append(kicad_text("U2: Pololu S13V25F9", rx, ry, 1.5))
    elements.append(kicad_text("Buck-Boost 5V/9V", rx, ry + 3, 1.2))
    elements.append(kicad_label("VBAT", rx, ry + 7, 180))
    elements.append(kicad_label("5V", rx + 25, ry + 7, 0))
    elements.append(kicad_label("9V", rx + 25, ry + 12, 0))
    elements.append(kicad_global_label("GND", rx + 12, ry + 20, 270, "input"))
    elements.append(make_capacitor("C2", "100nF", rx + 5, ry + 15))
    # PWR_FLAG on 5V
    elements.append(kicad_pwr_flag(rx + 30, ry + 4, 2))
    elements.append(kicad_wire(rx + 30, ry + 4, rx + 30, ry + 7))
    # PWR_FLAG on 9V
    elements.append(kicad_pwr_flag(rx + 35, ry + 9, 3))
    elements.append(kicad_wire(rx + 35, ry + 9, rx + 35, ry + 12))

    # --- MCU Buck-Boost 3.3V (Pololu S7V8F3) ---
    rx2, ry2 = px + 80, py + 25
    elements.append(kicad_text("U3: Pololu S7V8F3", rx2, ry2, 1.5))
    elements.append(kicad_text("MCU Buck-Boost 3.3V", rx2, ry2 + 3, 1.2))
    elements.append(kicad_label("VBAT", rx2, ry2 + 7, 180))
    elements.append(kicad_label("3V3", rx2 + 25, ry2 + 7, 0))
    elements.append(kicad_global_label("GND", rx2 + 12, ry2 + 15, 270, "input"))
    elements.append(make_capacitor("C3", "100nF", rx2 + 5, ry2 + 12))
    # PWR_FLAG on 3V3
    elements.append(kicad_pwr_flag(rx2 + 30, ry2 + 4, 4))
    elements.append(kicad_wire(rx2 + 30, ry2 + 4, rx2 + 30, ry2 + 7))

    # --- Power Management PCB ---
    pmx, pmy = px + 80, py + 55
    elements.append(kicad_text("U4: Power Management PCB", pmx, pmy, 1.5))
    elements.append(kicad_label("3V3", pmx, pmy + 5, 180))
    elements.append(kicad_label("9V", pmx, pmy + 10, 180))
    # Outputs
    elements.append(kicad_label("3V3_OUT", pmx + 30, pmy + 5, 0))
    elements.append(kicad_label("9V_OUT", pmx + 30, pmy + 10, 0))
    elements.append(kicad_label("GND_OUT", pmx + 30, pmy + 15, 0))
    elements.append(kicad_global_label("GND", pmx + 15, pmy + 20, 270, "input"))

    # PWR_FLAG on GND
    elements.append(kicad_pwr_flag(pmx + 20, pmy + 20, 5))
    elements.append(kicad_wire(pmx + 20, pmy + 20, pmx + 20, pmy + 23))
    elements.append(kicad_global_label("GND", pmx + 20, pmy + 23, 270, "input"))

    # ═══════════════════════════════════════════
    # SECTION 2: ESP32-S3 MCU (center)
    # ═══════════════════════════════════════════
    mx, my = 200, 30  # MCU base position

    elements.append(kicad_text("=== ESP32-S3 MCU ===", mx + 15, my - 10, 4.0))

    elements.append(kicad_text("U5: ESP32-S3-WROOM-1", mx, my, 2.0))

    # Power pins
    elements.append(kicad_label("3V3_OUT", mx - 5, my + 8, 180))
    elements.append(kicad_wire(mx - 5, my + 8, mx + 2, my + 8))
    elements.append(kicad_text("3V3", mx + 3, my + 8, 1.0))

    elements.append(kicad_global_label("GND", mx + 15, my + 100, 270, "input"))
    elements.append(kicad_wire(mx + 15, my + 97, mx + 15, my + 100))
    elements.append(kicad_text("GND", mx + 3, my + 97, 1.0))

    # Decoupling caps for ESP32
    elements.append(make_capacitor("C4", "100nF", mx - 10, my + 12))
    elements.append(make_capacitor("C5", "10uF", mx - 10, my + 20))

    # --- GPIO Pin labels (left side of MCU) ---
    gpio_left = [
        ("GPIO1", "MEASURE_BTN", my + 15),
        ("GPIO2", "FAN_GATE", my + 20),
        ("GPIO4", "STEP", my + 25),
        ("GPIO5", "WLED_CTRL", my + 30),
        ("GPIO6", "RGB_R", my + 35),
        ("GPIO7", "RGB_G", my + 40),
        ("GPIO8", "RGB_B", my + 45),
        ("GPIO15", "HEATER_GATE", my + 50),
        ("GPIO16", "DIR", my + 55),
        ("GPIO17", "LIMIT_SW", my + 60),
    ]

    for gpio, net, pin_y in gpio_left:
        elements.append(kicad_text(gpio, mx - 12, pin_y, 1.0))
        elements.append(kicad_label(net, mx - 5, pin_y, 180))
        elements.append(kicad_wire(mx - 5, pin_y, mx + 2, pin_y))

    # --- GPIO Pin labels (right side of MCU) ---
    gpio_right = [
        ("GPIO18", "I2C_SCL", my + 15),
        ("GPIO19", "I2C_SDA", my + 20),
        ("GPIO20", "UV_GATE", my + 25),
        ("GPIO21", "REED_SW", my + 30),
        ("GPIO38", "SD_MISO", my + 35),
        ("GPIO39", "SD_MOSI", my + 40),
        ("GPIO40", "SD_SCK", my + 45),
        ("GPIO41", "SD_CS", my + 50),
        ("GPIO42", "BUZZER", my + 55),
        ("GPIO43", "BARCODE_TX", my + 60),
        ("GPIO44", "BARCODE_RX", my + 65),
    ]

    for gpio, net, pin_y in gpio_right:
        elements.append(kicad_text(gpio, mx + 38, pin_y, 1.0))
        elements.append(kicad_label(net, mx + 35, pin_y, 0))
        elements.append(kicad_wire(mx + 30, pin_y, mx + 35, pin_y))

    # DVP camera bus labels
    dvp_pins = [
        ("DVP_D0-D7", "CAM_DATA", my + 72),
        ("DVP_PCLK", "CAM_PCLK", my + 77),
        ("DVP_VSYNC", "CAM_VSYNC", my + 82),
        ("DVP_HREF", "CAM_HREF", my + 87),
        ("DVP_XCLK", "CAM_XCLK", my + 92),
    ]
    for pin, net, pin_y in dvp_pins:
        elements.append(kicad_text(pin, mx + 38, pin_y, 1.0))
        elements.append(kicad_label(net, mx + 35, pin_y, 0))

    # MCU outline box (using wires to draw rectangle)
    box_left = mx
    box_right = mx + 30
    box_top = my + 5
    box_bottom = my + 97
    elements.append(kicad_wire(box_left, box_top, box_right, box_top))
    elements.append(kicad_wire(box_right, box_top, box_right, box_bottom))
    elements.append(kicad_wire(box_right, box_bottom, box_left, box_bottom))
    elements.append(kicad_wire(box_left, box_bottom, box_left, box_top))

    # ═══════════════════════════════════════════
    # SECTION 3: SENSORS & I2C (upper right)
    # ═══════════════════════════════════════════
    sx, sy = 300, 20

    elements.append(kicad_text("=== SENSORS & I2C ===", sx + 10, sy - 10, 4.0))

    # --- OLED Display (I2C) ---
    elements.append(kicad_text("U6: OLED Display (SSD1306)", sx, sy, 1.5))
    elements.append(kicad_label("3V3_OUT", sx, sy + 5, 180))
    elements.append(kicad_text("VCC", sx + 1, sy + 5, 1.0))
    elements.append(kicad_label("I2C_SCL", sx, sy + 10, 180))
    elements.append(kicad_text("SCL", sx + 1, sy + 10, 1.0))
    elements.append(kicad_label("I2C_SDA", sx, sy + 15, 180))
    elements.append(kicad_text("SDA", sx + 1, sy + 15, 1.0))
    elements.append(kicad_global_label("GND", sx + 10, sy + 20, 270, "input"))
    elements.append(make_capacitor("C6", "100nF", sx + 15, sy + 5))

    # --- SHT31 Humidity/Temp Sensor (I2C) ---
    s2x, s2y = sx, sy + 30
    elements.append(kicad_text("U7: SHT31 Humidity Sensor", s2x, s2y, 1.5))
    elements.append(kicad_label("3V3_OUT", s2x, s2y + 5, 180))
    elements.append(kicad_text("VCC", s2x + 1, s2y + 5, 1.0))
    elements.append(kicad_label("I2C_SCL", s2x, s2y + 10, 180))
    elements.append(kicad_text("SCL", s2x + 1, s2y + 10, 1.0))
    elements.append(kicad_label("I2C_SDA", s2x, s2y + 15, 180))
    elements.append(kicad_text("SDA", s2x + 1, s2y + 15, 1.0))
    elements.append(kicad_global_label("GND", s2x + 10, s2y + 20, 270, "input"))
    elements.append(make_capacitor("C7", "100nF", s2x + 15, s2y + 5))

    # --- BH1750 Light Sensor (I2C) ---
    s3x, s3y = sx, sy + 60
    elements.append(kicad_text("U8: BH1750 Light Sensor", s3x, s3y, 1.5))
    elements.append(kicad_label("3V3_OUT", s3x, s3y + 5, 180))
    elements.append(kicad_text("VCC", s3x + 1, s3y + 5, 1.0))
    elements.append(kicad_label("I2C_SCL", s3x, s3y + 10, 180))
    elements.append(kicad_text("SCL", s3x + 1, s3y + 10, 1.0))
    elements.append(kicad_label("I2C_SDA", s3x, s3y + 15, 180))
    elements.append(kicad_text("SDA", s3x + 1, s3y + 15, 1.0))
    elements.append(kicad_global_label("GND", s3x + 10, s3y + 20, 270, "input"))
    elements.append(make_capacitor("C8", "100nF", s3x + 15, s3y + 5))

    # I2C pull-up resistors
    elements.append(kicad_text("I2C Pull-ups", sx + 40, sy, 1.2))
    elements.append(make_resistor("R1", "4.7k", sx + 45, sy + 7))
    elements.append(kicad_label("I2C_SCL", sx + 45, sy + 3.47, 0))
    elements.append(kicad_label("3V3_OUT", sx + 45, sy - 0.5, 0))

    elements.append(make_resistor("R2", "4.7k", sx + 55, sy + 7))
    elements.append(kicad_label("I2C_SDA", sx + 55, sy + 3.47, 0))
    elements.append(kicad_label("3V3_OUT", sx + 55, sy - 0.5, 0))

    # --- Thermistor ---
    s4x, s4y = sx, sy + 90
    elements.append(kicad_text("Thermistor Circuit", s4x, s4y, 1.5))
    # Thermistor + voltage divider
    elements.append(make_resistor("R3", "NTC 10k", s4x + 10, s4y + 7))
    elements.append(kicad_label("3V3_OUT", s4x + 10, s4y + 3.47, 0))
    elements.append(make_resistor("R4", "10k", s4x + 10, s4y + 17))
    elements.append(kicad_global_label("GND", s4x + 10, s4y + 22, 270, "input"))
    elements.append(kicad_wire(s4x + 10, s4y + 10.53, s4x + 10, s4y + 13.47))
    elements.append(kicad_label("THERM_ADC", s4x + 14, s4y + 12, 0))
    elements.append(kicad_wire(s4x + 10, s4y + 12, s4x + 14, s4y + 12))

    # --- Barcode Scanner (UART) ---
    s5x, s5y = sx + 50, sy + 60
    elements.append(kicad_text("U9: Barcode Scanner (UART)", s5x, s5y, 1.5))
    elements.append(kicad_label("3V3_OUT", s5x, s5y + 5, 180))
    elements.append(kicad_text("VCC", s5x + 1, s5y + 5, 1.0))
    elements.append(kicad_label("BARCODE_TX", s5x, s5y + 10, 180))
    elements.append(kicad_text("RX", s5x + 1, s5y + 10, 1.0))
    elements.append(kicad_label("BARCODE_RX", s5x, s5y + 15, 180))
    elements.append(kicad_text("TX", s5x + 1, s5y + 15, 1.0))
    elements.append(kicad_global_label("GND", s5x + 10, s5y + 20, 270, "input"))
    elements.append(make_capacitor("C9", "100nF", s5x + 15, s5y + 5))

    # ═══════════════════════════════════════════
    # SECTION 4: CAMERA & OPTICS (right center)
    # ═══════════════════════════════════════════
    cx, cy = 300, 140

    elements.append(kicad_text("=== CAMERA & OPTICS ===", cx + 10, cy - 10, 4.0))

    # --- OV2640 Camera ---
    elements.append(kicad_text("U10: OV2640 Camera + CPL Filter", cx, cy, 1.5))
    cam_pins = [
        ("3V3_OUT", "VCC", cy + 5),
        ("CAM_DATA", "D0-D7", cy + 10),
        ("CAM_PCLK", "PCLK", cy + 15),
        ("CAM_VSYNC", "VSYNC", cy + 20),
        ("CAM_HREF", "HREF", cy + 25),
        ("CAM_XCLK", "XCLK", cy + 30),
    ]
    for net, pin, pin_y in cam_pins:
        elements.append(kicad_label(net, cx, pin_y, 180))
        elements.append(kicad_text(pin, cx + 1, pin_y, 1.0))
    elements.append(kicad_global_label("GND", cx + 10, cy + 35, 270, "input"))
    elements.append(make_capacitor("C10", "100nF", cx + 20, cy + 5))
    elements.append(make_capacitor("C11", "10uF", cx + 28, cy + 5))

    # --- White LED Array ---
    wlx, wly = cx, cy + 45
    elements.append(kicad_text("White LED Array", wlx, wly, 1.5))
    # MOSFET switch for white LEDs
    elements.append(make_mosfet_n("Q1", "2N7000", wlx + 15, wly + 10))
    elements.append(kicad_label("WLED_CTRL", wlx + 12, wly + 10, 180))
    # Gate pull-down
    elements.append(make_resistor("R5", "10k", wlx + 10, wly + 18))
    elements.append(kicad_global_label("GND", wlx + 10, wly + 24, 270, "input"))
    # LEDs with current-limiting resistors
    for i in range(3):
        lx = wlx + 25 + i * 10
        elements.append(make_resistor(f"R{6+i}", "330", lx, wly + 5))
        elements.append(make_led(f"D{1+i}", "White", lx, wly + 15))
        elements.append(kicad_label("3V3_OUT", lx, wly + 1.47, 0))
        elements.append(kicad_wire(lx, wly + 8.53, lx, wly + 12))  # R to LED
    # Common drain to MOSFET
    elements.append(kicad_wire(wlx + 25, wly + 18, wlx + 45, wly + 18))
    elements.append(kicad_wire(wlx + 35, wly + 18, wlx + 35, wly + 18))
    elements.append(kicad_global_label("GND", wlx + 17.54, wly + 20, 270, "input"))

    # --- UV-C LED (5V, MOSFET-switched) ---
    uvx, uvy = cx + 65, cy
    elements.append(kicad_text("UV-C LED Circuit", uvx, uvy, 1.5))
    elements.append(make_mosfet_n("Q2", "IRLZ44N", uvx + 10, uvy + 15))
    elements.append(kicad_label("UV_GATE", uvx + 7, uvy + 15, 180))
    # Gate pull-down
    elements.append(make_resistor("R9", "10k", uvx + 5, uvy + 22))
    elements.append(kicad_global_label("GND", uvx + 5, uvy + 28, 270, "input"))
    # UV LED + resistor
    elements.append(make_resistor("R10", "47", uvx + 12.54, uvy + 5))
    elements.append(make_led("D4", "UV-C", uvx + 12.54, uvy + 12))
    elements.append(kicad_label("5V", uvx + 12.54, uvy + 1.47, 0))
    elements.append(kicad_global_label("GND", uvx + 12.54, uvy + 25, 270, "input"))

    # ═══════════════════════════════════════════
    # SECTION 5: MOTOR & ACTUATORS (lower right)
    # ═══════════════════════════════════════════
    ax, ay = 300, 220

    elements.append(kicad_text("=== MOTOR & ACTUATORS ===", ax + 10, ay - 10, 4.0))

    # --- A4988 Stepper Driver ---
    elements.append(kicad_text("U11: A4988 Stepper Driver", ax, ay, 1.5))
    a4988_left = [
        ("STEP", ay + 7),
        ("DIR", ay + 12),
        ("3V3_OUT", ay + 17),  # VDD
        ("9V_OUT", ay + 22),   # VMOT
    ]
    for net, pin_y in a4988_left:
        elements.append(kicad_label(net, ax, pin_y, 180))

    elements.append(kicad_text("STEP", ax + 1, ay + 7, 1.0))
    elements.append(kicad_text("DIR", ax + 1, ay + 12, 1.0))
    elements.append(kicad_text("VDD", ax + 1, ay + 17, 1.0))
    elements.append(kicad_text("VMOT", ax + 1, ay + 22, 1.0))

    a4988_right = [
        ("1A", "STEPPER_1A", ay + 7),
        ("1B", "STEPPER_1B", ay + 12),
        ("2A", "STEPPER_2A", ay + 17),
        ("2B", "STEPPER_2B", ay + 22),
    ]
    for pin, net, pin_y in a4988_right:
        elements.append(kicad_text(pin, ax + 28, pin_y, 1.0))
        elements.append(kicad_label(net, ax + 30, pin_y, 0))

    elements.append(kicad_global_label("GND", ax + 15, ay + 28, 270, "input"))
    elements.append(make_capacitor("C12", "100nF", ax + 5, ay + 25))
    elements.append(make_capacitor("C13", "100uF", ax + 22, ay + 25))

    # A4988 box
    elements.append(kicad_wire(ax + 1, ay + 4, ax + 27, ay + 4))
    elements.append(kicad_wire(ax + 27, ay + 4, ax + 27, ay + 26))
    elements.append(kicad_wire(ax + 27, ay + 26, ax + 1, ay + 26))
    elements.append(kicad_wire(ax + 1, ay + 26, ax + 1, ay + 4))

    # --- NEMA 17 Stepper Motor ---
    nmx, nmy = ax + 50, ay
    elements.append(kicad_text("M1: NEMA 17 Stepper", nmx, nmy, 1.5))
    stepper_pins = [
        ("A1", "STEPPER_1A", nmy + 7),
        ("A2", "STEPPER_1B", nmy + 12),
        ("B1", "STEPPER_2A", nmy + 17),
        ("B2", "STEPPER_2B", nmy + 22),
    ]
    for pin, net, pin_y in stepper_pins:
        elements.append(kicad_text(pin, nmx + 1, pin_y, 1.0))
        elements.append(kicad_label(net, nmx, pin_y, 180))

    # --- Limit Switch ---
    lsx, lsy = ax + 50, ay + 30
    elements.append(kicad_text("Limit Switch", lsx, lsy, 1.5))
    elements.append(make_switch("SW2", "Limit", lsx + 10, lsy + 7))
    elements.append(kicad_global_label("GND", lsx + 7.46, lsy + 7, 180, "input"))
    elements.append(kicad_label("LIMIT_SW", lsx + 12.54, lsy + 7, 0))
    # Pull-up resistor
    elements.append(make_resistor("R11", "10k", lsx + 18, lsy + 3))
    elements.append(kicad_label("3V3_OUT", lsx + 18, lsy - 0.53, 0))
    elements.append(kicad_wire(lsx + 18, lsy + 6.53, lsx + 18, lsy + 7))
    elements.append(kicad_wire(lsx + 12.54, lsy + 7, lsx + 18, lsy + 7))

    # --- Heater Film (5V, MOSFET-switched) ---
    hx, hy = ax, ay + 45
    elements.append(kicad_text("Heater Film Circuit", hx, hy, 1.5))
    elements.append(make_mosfet_n("Q3", "IRLZ44N", hx + 15, hy + 10))
    elements.append(kicad_label("HEATER_GATE", hx + 12, hy + 10, 180))
    # Gate pull-down
    elements.append(make_resistor("R12", "10k", hx + 10, hy + 18))
    elements.append(kicad_global_label("GND", hx + 10, hy + 24, 270, "input"))
    # Heater film load
    elements.append(kicad_text("Heater Film", hx + 17.54, hy + 3, 1.2))
    elements.append(kicad_label("5V", hx + 17.54, hy + 5, 0))
    elements.append(kicad_global_label("GND", hx + 17.54, hy + 20, 270, "input"))

    # --- Vent Fan (5V, MOSFET-switched) ---
    fx, fy = ax + 50, ay + 45
    elements.append(kicad_text("Vent Fan Circuit", fx, fy, 1.5))
    elements.append(make_mosfet_n("Q4", "2N7000", fx + 15, fy + 10))
    elements.append(kicad_label("FAN_GATE", fx + 12, fy + 10, 180))
    # Gate pull-down
    elements.append(make_resistor("R13", "10k", fx + 10, fy + 18))
    elements.append(kicad_global_label("GND", fx + 10, fy + 24, 270, "input"))
    # Fan load
    elements.append(kicad_text("Vent Fan", fx + 17.54, fy + 3, 1.2))
    elements.append(kicad_label("5V", fx + 17.54, fy + 5, 0))
    elements.append(kicad_global_label("GND", fx + 17.54, fy + 20, 270, "input"))

    # --- Buzzer ---
    bx, by = ax, ay + 75
    elements.append(kicad_text("Buzzer Circuit", bx, by, 1.5))
    elements.append(kicad_text("BZ1: Active Buzzer", bx, by + 4, 1.2))
    elements.append(kicad_label("BUZZER", bx, by + 8, 180))
    elements.append(kicad_text("VCC", bx + 1, by + 8, 1.0))
    elements.append(kicad_global_label("GND", bx + 10, by + 13, 270, "input"))

    # ═══════════════════════════════════════════
    # SECTION 6: USER INTERFACE (upper center)
    # ═══════════════════════════════════════════
    ux, uy = 200, 150

    elements.append(kicad_text("=== USER INTERFACE ===", ux + 15, uy - 10, 4.0))

    # --- Measure Button ---
    elements.append(kicad_text("Measure Button", ux, uy, 1.5))
    elements.append(make_switch("SW1", "Measure", ux + 10, uy + 7))
    elements.append(kicad_label("3V3_OUT", ux + 7.46, uy + 7, 180))
    elements.append(kicad_label("MEASURE_BTN", ux + 12.54, uy + 7, 0))
    # Pull-up resistor
    elements.append(make_resistor("R14", "10k", ux + 18, uy + 3))
    elements.append(kicad_label("3V3_OUT", ux + 18, uy - 0.53, 0))
    elements.append(kicad_wire(ux + 18, uy + 6.53, ux + 18, uy + 7))
    elements.append(kicad_wire(ux + 12.54, uy + 7, ux + 18, uy + 7))

    # --- RGB LED ---
    rx, ry = ux, uy + 20
    elements.append(kicad_text("RGB Status LED", rx, ry, 1.5))

    # Red channel
    elements.append(make_resistor("R15", "330", rx + 5, ry + 7))
    elements.append(make_led("D5", "Red", rx + 5, ry + 17))
    elements.append(kicad_label("RGB_R", rx + 5, ry + 3.47, 0))
    elements.append(kicad_wire(rx + 5, ry + 10.53, rx + 5, ry + 14))
    elements.append(kicad_global_label("GND", rx + 5, ry + 22, 270, "input"))

    # Green channel
    elements.append(make_resistor("R16", "330", rx + 15, ry + 7))
    elements.append(make_led("D6", "Green", rx + 15, ry + 17))
    elements.append(kicad_label("RGB_G", rx + 15, ry + 3.47, 0))
    elements.append(kicad_wire(rx + 15, ry + 10.53, rx + 15, ry + 14))
    elements.append(kicad_global_label("GND", rx + 15, ry + 22, 270, "input"))

    # Blue channel
    elements.append(make_resistor("R17", "330", rx + 25, ry + 7))
    elements.append(make_led("D7", "Blue", rx + 25, ry + 17))
    elements.append(kicad_label("RGB_B", rx + 25, ry + 3.47, 0))
    elements.append(kicad_wire(rx + 25, ry + 10.53, rx + 25, ry + 14))
    elements.append(kicad_global_label("GND", rx + 25, ry + 22, 270, "input"))

    # Anode label
    elements.append(kicad_label("3V3_OUT", rx + 15, ry - 2, 0))
    elements.append(kicad_text("(common anode through resistors)", rx, ry - 5, 1.0))

    # --- SD Card Module (SPI) ---
    sdx, sdy = ux + 50, uy
    elements.append(kicad_text("U12: SD Card Module (SPI)", sdx, sdy, 1.5))
    sd_pins = [
        ("3V3_OUT", "VCC", sdy + 5),
        ("SD_MISO", "MISO", sdy + 10),
        ("SD_MOSI", "MOSI", sdy + 15),
        ("SD_SCK", "SCK", sdy + 20),
        ("SD_CS", "CS", sdy + 25),
    ]
    for net, pin, pin_y in sd_pins:
        elements.append(kicad_label(net, sdx, pin_y, 180))
        elements.append(kicad_text(pin, sdx + 1, pin_y, 1.0))
    elements.append(kicad_global_label("GND", sdx + 10, sdy + 30, 270, "input"))
    elements.append(make_capacitor("C14", "100nF", sdx + 15, sdy + 5))

    # ═══════════════════════════════════════════
    # SECTION 7: SAFETY (bottom)
    # ═══════════════════════════════════════════
    safex, safey = 200, 210

    elements.append(kicad_text("=== SAFETY ===", safex + 10, safey - 10, 4.0))

    # --- Reed Switch Interlock ---
    elements.append(kicad_text("Reed Switch Safety Interlock", safex, safey, 1.5))
    elements.append(make_switch("SW3", "Reed_Switch", safex + 15, safey + 7))
    elements.append(kicad_global_label("GND", safex + 12.46, safey + 7, 180, "input"))
    elements.append(kicad_label("REED_SW", safex + 17.54, safey + 7, 0))
    # Pull-up
    elements.append(make_resistor("R18", "10k", safex + 23, safey + 3))
    elements.append(kicad_label("3V3_OUT", safex + 23, safey - 0.53, 0))
    elements.append(kicad_wire(safex + 23, safey + 6.53, safex + 23, safey + 7))
    elements.append(kicad_wire(safex + 17.54, safey + 7, safex + 23, safey + 7))

    # ═══════════════════════════════════════════
    # SECTION: POWER DISTRIBUTION LABELS
    # ═══════════════════════════════════════════
    # Add power flag symbols at key power nodes

    # Global power net labels at the boundary between sections
    pdx, pdy = 160, 130
    elements.append(kicad_text("=== POWER NETS ===", pdx, pdy - 5, 2.0))
    power_nets = [
        ("VBAT", "3.7V LiPo"),
        ("3V3", "3.3V Rail"),
        ("3V3_OUT", "3.3V Distributed"),
        ("5V", "5V Rail"),
        ("9V", "9V Rail"),
        ("9V_OUT", "9V Distributed"),
        ("GND_OUT", "Ground Distributed"),
    ]
    for i, (net, desc) in enumerate(power_nets):
        ny = pdy + 5 + i * 5
        elements.append(kicad_global_label(net, pdx, ny, 0, "bidirectional"))
        elements.append(kicad_text(desc, pdx + 15, ny, 1.0))

    # ═══════════════════════════════════════════
    # Assemble the full schematic
    # ═══════════════════════════════════════════

    # KiCad 8 lib_symbols definitions for all used library symbols
    lib_symbols = generate_lib_symbols()

    header = f'''(kicad_sch
  (version 20231120)
  (generator "python_urine_dipstick_generator")
  (generator_version "8.0")
  (uuid "{uid()}")
  (paper "A1")

  (title_block
    (title "Urine Dipstick Analyzer")
    (date "2026-05-15")
    (rev "1.0")
    (comment 1 "ESP32-S3 Based Camera Dipstick Analyzer")
    (comment 2 "Power: LiPo 3.7V + USB-C Charging")
    (comment 3 "Generated by Python script")
  )

{lib_symbols}

'''

    footer = "\n)\n"

    content = header + "\n".join(elements) + footer
    return content


def generate_lib_symbols():
    """Generate the lib_symbols section with all symbol definitions needed."""
    return '''  (lib_symbols
    (symbol "Device:R"
      (pin_numbers hide)
      (pin_names (offset 0))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at -1.778 0 90) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.54) (end 1.016 2.54)
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Device:C"
      (pin_numbers hide)
      (pin_names (offset 0.254))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "C" (at 0.635 2.54 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "C" (at 0.635 -2.54 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "" (at 0.9652 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_0_1"
        (polyline
          (pts (xy -2.032 -0.762) (xy 2.032 -0.762))
          (stroke (width 0.508) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy -2.032 0.762) (xy 2.032 0.762))
          (stroke (width 0.508) (type default))
          (fill (type none))
        )
      )
      (symbol "C_1_1"
        (pin passive line (at 0 3.81 270) (length 3.048) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 3.048) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Device:LED"
      (pin_numbers hide)
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LED" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "LED_0_1"
        (polyline
          (pts (xy -1.27 -1.27) (xy -1.27 1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy -1.27 0) (xy 1.27 0))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy -3.048 -0.762) (xy -4.572 -2.286))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy -1.778 -0.762) (xy -3.302 -2.286))
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "LED_1_1"
        (pin passive line (at -3.81 0 0) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 0 180) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Device:Q_NMOS_GDS"
      (pin_names (offset 0.254) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "Q" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "Q_NMOS_GDS" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "" (at 5.08 2.54 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Q_NMOS_GDS_0_1"
        (polyline
          (pts (xy 0.254 0) (xy -2.54 0))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0.254 1.905) (xy 0.254 -1.905))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0.762 -1.27) (xy 0.762 -2.286))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0.762 0.508) (xy 0.762 -0.508))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0.762 2.286) (xy 0.762 1.27))
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 2.54 2.54) (xy 2.54 1.778) (xy 0.762 1.778))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 2.54 -2.54) (xy 2.54 0) (xy 0.762 0))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0.762 -1.778) (xy 2.54 -1.778) (xy 2.54 -2.54))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 1.016 0) (xy 2.032 0.381) (xy 2.032 -0.381) (xy 1.016 0))
          (stroke (width 0) (type default))
          (fill (type outline))
        )
      )
      (symbol "Q_NMOS_GDS_1_1"
        (pin passive line (at -5.08 0 0) (length 2.54) (name "G" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 2.54 5.08 270) (length 2.54) (name "D" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 2.54 -5.08 90) (length 2.54) (name "S" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Switch:SW_Push"
      (pin_numbers hide)
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "SW" (at 1.27 6.35 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "SW_Push" (at 0 -1.524 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "SW_Push_0_1"
        (circle (center -2.032 0) (radius 0.508)
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0 1.524) (xy 0 3.048))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 2.54 1.524) (xy -2.54 1.524))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (circle (center 2.032 0) (radius 0.508)
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (pin passive line (at -5.08 0 0) (length 2.54) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 5.08 0 180) (length 2.54) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "power:GND"
      (power)
      (pin_numbers hide)
      (pin_names (offset 0) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "GND_0_1"
        (polyline
          (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "GND_1_1"
        (pin power_in line (at 0 0 270) (length 0) (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "power:PWR_FLAG"
      (power)
      (pin_numbers hide)
      (pin_names (offset 0) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#FLG" (at 0 1.905 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "PWR_FLAG" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "PWR_FLAG_0_1"
        (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Simulation_SPICE:OPAMP"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "OPAMP" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "OPAMP_0_1"
        (polyline
          (pts (xy -5.08 5.08) (xy 5.08 0) (xy -5.08 -5.08) (xy -5.08 5.08))
          (stroke (width 0.254) (type default))
          (fill (type background))
        )
      )
      (symbol "OPAMP_1_1"
        (pin input line (at -7.62 2.54 0) (length 2.54) (name "+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 -2.54 0) (length 2.54) (name "-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
      )
    )
  )
'''


def main():
    output_dir = "/Users/siddhantsaboo/Desktop/agentic workflows/urine_dipstick_cad"
    output_file = os.path.join(output_dir, "urine_dipstick_analyzer.kicad_sch")

    os.makedirs(output_dir, exist_ok=True)

    schematic = generate_schematic()

    with open(output_file, "w") as f:
        f.write(schematic)

    print(f"Schematic generated: {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")

    # Count elements
    lines = schematic.split("\n")
    symbols = schematic.count("(lib_id")
    wires = schematic.count("(wire")
    labels = schematic.count("(label")
    glabels = schematic.count("(global_label")
    texts = schematic.count('(text "')

    print(f"\nSchematic statistics:")
    print(f"  Total lines: {len(lines)}")
    print(f"  Symbol instances: {symbols}")
    print(f"  Wires: {wires}")
    print(f"  Net labels: {labels}")
    print(f"  Global labels: {glabels}")
    print(f"  Text annotations: {texts}")


if __name__ == "__main__":
    main()
