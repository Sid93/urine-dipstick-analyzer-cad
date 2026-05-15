#!/usr/bin/env python3
"""
Generate a KiCad 8 schematic (.kicad_sch) for a Urine Dipstick Analyzer v2.0.

All coordinates snap to 2.54mm grid.
All wires land exactly on component pin coordinates.
Custom ICs are rendered as labeled wire-rectangle blocks with net labels at pin positions.
The ESP32-S3 is a large block with properly spaced pin labels.

Components:
- Power: LiPo, MCP73833 USB-C charger, Pololu S13V25F9 (5V/9V), Pololu S7V8F3 (3.3V),
         MAX17048 fuel gauge
- MCU: ESP32-S3-WROOM-1
- Sensors: SHT31 (I2C), BH1750 (I2C), DS3231 RTC (I2C), NTC thermistor
- Camera: OV2640 (DVP bus)
- Display: ILI9341 TFT (SPI)
- Motor: A4988 + NEMA 17 stepper, limit switch
- Actuators: UV-C LED + IRLZ44N, heater film + IRLZ44N, vent fan + 2N7000
- UI: Measure button, RGB LED (common anode) with 330R, active buzzer
- Barcode: GM65 scanner (UART)
- Storage: SD card module (SPI, shared bus with display)
- Safety: MC-38 reed switch
- Passives: decoupling 100nF per IC, 10uF bulk, 4.7k I2C pull-ups
"""

import uuid
import os


def uid():
    return str(uuid.uuid4())


def snap(v):
    """Snap a value to the nearest 2.54mm grid point."""
    return round(v / 2.54) * 2.54


# ============================================================
# KiCad S-expression primitives
# ============================================================

def kicad_text(text, x, y, size=3.0):
    x, y = snap(x), snap(y)
    return f'''  (text "{text}"
    (exclude_from_sim no)
    (at {x:.2f} {y:.2f} 0)
    (effects
      (font
        (size {size} {size})
        (bold yes)
      )
    )
    (uuid "{uid()}")
  )'''


def kicad_wire(x1, y1, x2, y2):
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    return f'''  (wire
    (pts
      (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})
    )
    (stroke
      (width 0)
      (type default)
    )
    (uuid "{uid()}")
  )'''


def kicad_label(name, x, y, angle=0):
    x, y = snap(x), snap(y)
    return f'''  (label "{name}"
    (at {x:.2f} {y:.2f} {angle})
    (effects
      (font
        (size 1.27 1.27)
      )
    )
    (uuid "{uid()}")
  )'''


def kicad_global_label(name, x, y, angle=0, shape="input"):
    x, y = snap(x), snap(y)
    return f'''  (global_label "{name}"
    (shape {shape})
    (at {x:.2f} {y:.2f} {angle})
    (effects
      (font
        (size 1.27 1.27)
      )
    )
    (uuid "{uid()}")
  )'''


def kicad_pwr_flag(x, y, ref_num):
    x, y = snap(x), snap(y)
    u = uid()
    return f'''  (symbol
    (lib_id "power:PWR_FLAG")
    (at {x:.2f} {y:.2f} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom no)
    (on_board no)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "#FLG0{ref_num}" (at {x:.2f} {y - 3:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "PWR_FLAG" (at {x:.2f} {y + 3:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
  )'''


# ============================================================
# Component primitives -- all pin offsets are KiCad-accurate
# ============================================================

# Resistor pins: pin1 at (0, +3.81), pin2 at (0, -3.81) when angle=0
# Capacitor pins: pin1 at (0, +3.81), pin2 at (0, -3.81) when angle=0
# LED pins: pin1 (K) at (-3.81, 0), pin2 (A) at (+3.81, 0) when angle=0
# MOSFET Q_NMOS_GDS: Gate pin1 at (-5.08, 0), Drain pin2 at (+2.54, +5.08), Source pin3 at (+2.54, -5.08)
# Switch SW_Push: pin1 at (-5.08, 0), pin2 at (+5.08, 0) when angle=0


def make_resistor(ref, value, x, y, angle=0):
    """Resistor: Device:R.  Pins at (0, +/-3.81) from center for angle=0."""
    x, y = snap(x), snap(y)
    u = uid()
    rx = x + 2.54 if angle == 0 else x
    ry = y if angle == 0 else y - 2.54
    vx = rx
    vy = ry + 2.54 if angle == 0 else ry + 2.54
    return f'''  (symbol
    (lib_id "Device:R")
    (at {x:.2f} {y:.2f} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {rx:.2f} {ry:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {vx:.2f} {vy:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def resistor_pin1(x, y, angle=0):
    """Return the absolute position of pin 1 for a resistor at (x,y,angle)."""
    if angle == 0:
        return (x, y - 3.81)
    elif angle == 90:
        return (x + 3.81, y)
    elif angle == 180:
        return (x, y + 3.81)
    elif angle == 270:
        return (x - 3.81, y)
    return (x, y - 3.81)


def resistor_pin2(x, y, angle=0):
    if angle == 0:
        return (x, y + 3.81)
    elif angle == 90:
        return (x - 3.81, y)
    elif angle == 180:
        return (x, y - 3.81)
    elif angle == 270:
        return (x + 3.81, y)
    return (x, y + 3.81)


def make_capacitor(ref, value, x, y, angle=0):
    """Capacitor: Device:C.  Pins at (0, +/-3.81) from center for angle=0."""
    x, y = snap(x), snap(y)
    u = uid()
    rx = x + 2.54 if angle == 0 else x
    ry = y if angle == 0 else y - 2.54
    vx = rx
    vy = ry + 2.54 if angle == 0 else ry + 2.54
    return f'''  (symbol
    (lib_id "Device:C")
    (at {x:.2f} {y:.2f} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {rx:.2f} {ry:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {vx:.2f} {vy:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def cap_pin1(x, y, angle=0):
    return resistor_pin1(x, y, angle)


def cap_pin2(x, y, angle=0):
    return resistor_pin2(x, y, angle)


def make_led(ref, value, x, y, angle=0):
    """LED: Device:LED.  Pin1(K) at (-3.81,0), Pin2(A) at (+3.81,0) for angle=0."""
    x, y = snap(x), snap(y)
    u = uid()
    return f'''  (symbol
    (lib_id "Device:LED")
    (at {x:.2f} {y:.2f} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x + 2.54:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x + 2.54:.2f} {y + 2.54:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def led_pin_k(x, y, angle=0):
    """Cathode pin of LED."""
    if angle == 0:
        return (x - 3.81, y)
    elif angle == 90:
        return (x, y - 3.81)
    elif angle == 180:
        return (x + 3.81, y)
    elif angle == 270:
        return (x, y + 3.81)
    return (x - 3.81, y)


def led_pin_a(x, y, angle=0):
    """Anode pin of LED."""
    if angle == 0:
        return (x + 3.81, y)
    elif angle == 90:
        return (x, y + 3.81)
    elif angle == 180:
        return (x - 3.81, y)
    elif angle == 270:
        return (x, y - 3.81)
    return (x + 3.81, y)


def make_mosfet_n(ref, value, x, y):
    """N-MOSFET: Device:Q_NMOS_GDS.
    Gate(pin1) at (x-5.08, y), Drain(pin2) at (x+2.54, y-5.08 top),
    Source(pin3) at (x+2.54, y+5.08 bottom).
    Note: in KiCad, Drain is UP (y-5.08) and Source is DOWN (y+5.08) in screen coords.
    """
    x, y = snap(x), snap(y)
    u = uid()
    return f'''  (symbol
    (lib_id "Device:Q_NMOS_GDS")
    (at {x:.2f} {y:.2f} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x + 5.08:.2f} {y - 2.54:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x + 5.08:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0)
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


def mosfet_gate(x, y):
    return (x - 5.08, y)


def mosfet_drain(x, y):
    return (x + 2.54, y - 5.08)


def mosfet_source(x, y):
    return (x + 2.54, y + 5.08)


def make_switch(ref, value, x, y, angle=0):
    """Switch: Switch:SW_Push.  pin1 at (-5.08,0), pin2 at (+5.08,0) for angle=0."""
    x, y = snap(x), snap(y)
    u = uid()
    return f'''  (symbol
    (lib_id "Switch:SW_Push")
    (at {x:.2f} {y:.2f} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x:.2f} {y - 3.81:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x:.2f} {y + 3.81:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (pin "2"
      (uuid "{uid()}")
    )
  )'''


def switch_pin1(x, y, angle=0):
    if angle == 0:
        return (x - 5.08, y)
    elif angle == 90:
        return (x, y - 5.08)
    return (x - 5.08, y)


def switch_pin2(x, y, angle=0):
    if angle == 0:
        return (x + 5.08, y)
    elif angle == 90:
        return (x, y + 5.08)
    return (x + 5.08, y)


# ============================================================
# Section boundary box (dashed rectangle with title)
# ============================================================

def kicad_section_box(title, x1, y1, x2, y2):
    """Draw a dashed boundary rectangle with a title, like the reference schematic."""
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    elems = []
    elems.append(f'''  (polyline
    (pts
      (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})
      (xy {x1:.2f} {y2:.2f}) (xy {x1:.2f} {y1:.2f})
    )
    (stroke
      (width 0.254)
      (type dash)
    )
    (uuid "{uid()}")
  )''')
    elems.append(kicad_text(title, (x1 + x2) / 2, y1 + 5.08, 3.0))
    return elems


# ============================================================
# Module block builder -- draws a wire rectangle with title
# and places net labels at pin positions along the edges.
# ============================================================

def make_module_block(title, x, y, width, left_pins, right_pins, pin_spacing=7.62):
    """
    Draw a labeled wire rectangle representing a module/IC.
    left_pins / right_pins: list of (pin_label_text, net_label_name_or_None)
    Pin spacing defaults to 7.62mm (300 mils) to prevent label overlap.
    Net labels are placed outside the box edge with a short wire stub.

    Returns list of element strings.
    """
    x, y = snap(x), snap(y)
    width = snap(width)
    n_pins = max(len(left_pins), len(right_pins))
    height = snap((n_pins + 1) * pin_spacing)

    elems = []

    elems.append(kicad_text(title, x + width / 2, y - 5.08, 2.0))

    bx1, by1 = x, y
    bx2, by2 = x + width, y + height
    elems.append(kicad_wire(bx1, by1, bx2, by1))
    elems.append(kicad_wire(bx2, by1, bx2, by2))
    elems.append(kicad_wire(bx2, by2, bx1, by2))
    elems.append(kicad_wire(bx1, by2, bx1, by1))

    for i, (pin_text, net_name) in enumerate(left_pins):
        py = y + (i + 1) * pin_spacing
        elems.append(kicad_text(pin_text, x + 2.54, py, 1.27))
        if net_name:
            elems.append(kicad_wire(x, py, x - 7.62, py))
            elems.append(kicad_label(net_name, x - 7.62, py, 180))

    for i, (pin_text, net_name) in enumerate(right_pins):
        py = y + (i + 1) * pin_spacing
        elems.append(kicad_text(pin_text, x + width - 12.70, py, 1.27))
        if net_name:
            elems.append(kicad_wire(x + width, py, x + width + 7.62, py))
            elems.append(kicad_label(net_name, x + width + 7.62, py, 0))

    return elems


def make_module_block_global(title, x, y, width, left_pins, right_pins, pin_spacing=7.62):
    """Same as make_module_block but uses global_label for power nets."""
    x, y = snap(x), snap(y)
    width = snap(width)
    n_pins = max(len(left_pins), len(right_pins))
    height = snap((n_pins + 1) * pin_spacing)

    elems = []
    elems.append(kicad_text(title, x + width / 2, y - 5.08, 2.0))

    bx1, by1 = x, y
    bx2, by2 = x + width, y + height
    elems.append(kicad_wire(bx1, by1, bx2, by1))
    elems.append(kicad_wire(bx2, by1, bx2, by2))
    elems.append(kicad_wire(bx2, by2, bx1, by2))
    elems.append(kicad_wire(bx1, by2, bx1, by1))

    for i, (pin_text, net_name, is_global) in enumerate(left_pins):
        py = y + (i + 1) * pin_spacing
        elems.append(kicad_text(pin_text, x + 2.54, py, 1.27))
        if net_name:
            elems.append(kicad_wire(x, py, x - 10.16, py))
            if is_global:
                elems.append(kicad_global_label(net_name, x - 10.16, py, 180, "bidirectional"))
            else:
                elems.append(kicad_label(net_name, x - 10.16, py, 180))

    for i, (pin_text, net_name, is_global) in enumerate(right_pins):
        py = y + (i + 1) * pin_spacing
        elems.append(kicad_text(pin_text, x + width - 12.70, py, 1.27))
        if net_name:
            elems.append(kicad_wire(x + width, py, x + width + 10.16, py))
            if is_global:
                elems.append(kicad_global_label(net_name, x + width + 10.16, py, 0, "bidirectional"))
            else:
                elems.append(kicad_label(net_name, x + width + 10.16, py, 0))

    return elems


# ============================================================
# Decoupling cap helper
# ============================================================

def add_decoupling_cap(ref, x, y, vcc_net, elements, bulk_ref=None, bulk_value="10uF"):
    """Place a 100nF cap from VCC to GND next to an IC.
    Cap is vertical: pin1 (top) = VCC, pin2 (bottom) = GND.
    Optionally add a bulk cap too.
    """
    cx, cy = snap(x), snap(y)
    elements.append(make_capacitor(ref, "100nF", cx, cy))
    p1 = cap_pin1(cx, cy)
    p2 = cap_pin2(cx, cy)
    elements.append(kicad_global_label(vcc_net, p1[0], p1[1], 0, "bidirectional"))
    elements.append(kicad_global_label("GND", p2[0], p2[1], 270, "input"))

    if bulk_ref:
        bx = cx + 7.62
        elements.append(make_capacitor(bulk_ref, bulk_value, bx, cy))
        bp1 = cap_pin1(bx, cy)
        bp2 = cap_pin2(bx, cy)
        elements.append(kicad_global_label(vcc_net, bp1[0], bp1[1], 0, "bidirectional"))
        elements.append(kicad_global_label("GND", bp2[0], bp2[1], 270, "input"))


# ============================================================
# MOSFET low-side switch helper
# ============================================================

def add_mosfet_switch(q_ref, q_value, r_pulldown_ref, gate_net, drain_net, x, y, elements):
    """
    Low-side MOSFET switch:
      Load -> Drain (top), Source -> GND (bottom), Gate <- MCU GPIO with pull-down R.
    Places MOSFET at (x,y), pull-down resistor below gate.
    Returns drain position for connecting load.
    """
    mx, my = snap(x), snap(y)
    elements.append(make_mosfet_n(q_ref, q_value, mx, my))

    g = mosfet_gate(mx, my)
    d = mosfet_drain(mx, my)
    s = mosfet_source(mx, my)

    # Gate label
    elements.append(kicad_label(gate_net, g[0], g[1], 180))

    # Source to GND
    elements.append(kicad_global_label("GND", s[0], s[1], 270, "input"))

    # Drain label
    elements.append(kicad_label(drain_net, d[0], d[1], 0))

    # Gate pull-down resistor: placed to the left, below gate
    prx, pry = snap(g[0]), snap(g[1] + 7.62)
    elements.append(make_resistor(r_pulldown_ref, "10k", prx, pry))
    p1 = resistor_pin1(prx, pry)  # top connects to gate wire
    p2 = resistor_pin2(prx, pry)  # bottom to GND
    elements.append(kicad_wire(g[0], g[1], p1[0], p1[1]))
    elements.append(kicad_global_label("GND", p2[0], p2[1], 270, "input"))

    return d


# ============================================================
# Main schematic generator
# ============================================================

def generate_schematic():
    elements = []

    # =========================================================
    # SECTION BOUNDARY BOXES (dashed rectangles like reference)
    # =========================================================
    elements.extend(kicad_section_box("Power Supply Section",
                                      10.16, 7.62, 165.10, 114.30))
    elements.extend(kicad_section_box("MCU & GPIO Section",
                                      172.72, 7.62, 302.26, 198.12))
    elements.extend(kicad_section_box("Sensors & I2C Section",
                                      309.88, 7.62, 444.50, 160.02))
    elements.extend(kicad_section_box("Camera & Optics Section",
                                      309.88, 165.10, 444.50, 297.18))
    elements.extend(kicad_section_box("Display & Storage Section",
                                      172.72, 200.66, 302.26, 299.72))
    elements.extend(kicad_section_box("Motor & Actuator Section",
                                      10.16, 116.84, 165.10, 248.92))
    elements.extend(kicad_section_box("UI: Button / LED / Buzzer Section",
                                      10.16, 251.46, 165.10, 353.06))
    elements.extend(kicad_section_box("Safety Section",
                                      172.72, 302.26, 302.26, 355.60))

    # Layout Instructions (like reference schematic)
    elements.append(kicad_text("Layout Instructions:", 10.16, 363.22, 2.5))
    elements.append(kicad_text("1. All decoupling caps should be placed as close to IC VCC pins as possible.", 10.16, 370.84, 1.5))
    elements.append(kicad_text("2. I2C bus pull-ups: single pair of 4.7k at MCU end.", 10.16, 376.0, 1.5))
    elements.append(kicad_text("3. SPI bus shared between TFT display and SD card (active-low CS per device).", 10.16, 381.0, 1.5))
    elements.append(kicad_text("4. All MOSFETs are low-side switches with 10k gate pull-downs.", 10.16, 386.0, 1.5))
    elements.append(kicad_text("5. UV-C LED requires series current-limiting resistor (47R @ 9V).", 10.16, 391.0, 1.5))

    # =========================================================
    # SECTION 1: POWER SUPPLY  (x=20, y=20)
    # =========================================================
    px, py = 20.32, 20.32

    elements.append(kicad_text("", px + 30.48, py - 7.62, 4.0))  # title in section box now

    # --- LiPo Battery ---
    elements.append(kicad_text("BT1: LiPo 3.7V 2000mAh", px, py, 1.5))
    elements.append(kicad_global_label("VBAT", px + 10.16, py + 5.08, 0, "bidirectional"))
    elements.append(kicad_global_label("GND", px + 10.16, py + 10.16, 270, "input"))

    # --- MCP73833 USB-C Charger ---
    chg_x, chg_y = px + 30.48, py
    chg_elems = make_module_block_global(
        "U1: MCP73833 USB-C Charger", chg_x, chg_y, 43.18,
        left_pins=[
            ("VIN (USB-C)", "VUSB", True),
            ("VSS", "GND", True),
            ("PROG", None, False),
        ],
        right_pins=[
            ("VBAT", "VBAT", True),
            ("STAT1", None, False),
            ("STAT2", None, False),
        ]
    )
    elements.extend(chg_elems)
    add_decoupling_cap("C1", chg_x + 55.88, chg_y + 5.08, "VUSB", elements)

    # PWR_FLAG on VBAT
    elements.append(kicad_pwr_flag(px + 25.40, py + 2.54, 1))
    elements.append(kicad_wire(px + 25.40, py + 2.54, px + 25.40, py + 5.08))
    elements.append(kicad_global_label("VBAT", px + 25.40, py + 5.08, 270, "bidirectional"))

    # --- Pololu S13V25F9 (5V/9V Buck-Boost) ---
    r1x, r1y = px + 76.20, py
    r1_elems = make_module_block_global(
        "U2: Pololu S13V25F9 (9V)", r1x, r1y, 43.18,
        left_pins=[
            ("VIN", "VBAT", True),
            ("GND", "GND", True),
            ("EN", None, False),
        ],
        right_pins=[
            ("VOUT (9V)", "9V", True),
            ("GND", "GND", True),
        ]
    )
    elements.extend(r1_elems)
    add_decoupling_cap("C2", r1x + 55.88, r1y + 5.08, "9V", elements,
                       bulk_ref="C3", bulk_value="10uF")

    # PWR_FLAG on 9V
    elements.append(kicad_pwr_flag(r1x + 35.56, r1y - 5.08, 2))
    elements.append(kicad_wire(r1x + 35.56, r1y - 5.08, r1x + 35.56, r1y - 2.54))
    elements.append(kicad_global_label("9V", r1x + 35.56, r1y - 2.54, 270, "bidirectional"))

    # --- Pololu S7V8F3 (3.3V) ---
    r2x, r2y = px + 76.20, py + 30.48
    r2_elems = make_module_block_global(
        "U3: Pololu S7V8F3 (3.3V)", r2x, r2y, 43.18,
        left_pins=[
            ("VIN", "VBAT", True),
            ("GND", "GND", True),
            ("EN", None, False),
        ],
        right_pins=[
            ("VOUT (3.3V)", "3V3", True),
            ("GND", "GND", True),
        ]
    )
    elements.extend(r2_elems)
    add_decoupling_cap("C4", r2x + 55.88, r2y + 5.08, "3V3", elements,
                       bulk_ref="C5", bulk_value="10uF")

    # PWR_FLAG on 3V3
    elements.append(kicad_pwr_flag(r2x + 35.56, r2y - 5.08, 3))
    elements.append(kicad_wire(r2x + 35.56, r2y - 5.08, r2x + 35.56, r2y - 2.54))
    elements.append(kicad_global_label("3V3", r2x + 35.56, r2y - 2.54, 270, "bidirectional"))

    # --- MAX17048 Battery Fuel Gauge (I2C) ---
    fg_x, fg_y = px, py + 50.80
    fg_elems = make_module_block_global(
        "U4: MAX17048 Fuel Gauge", fg_x, fg_y, 30.48,
        left_pins=[
            ("VDD", "VBAT", True),
            ("GND", "GND", True),
            ("CELL", "VBAT", True),
        ],
        right_pins=[
            ("SDA", "I2C_SDA", False),
            ("SCL", "I2C_SCL", False),
            ("ALT", None, False),
        ]
    )
    elements.extend(fg_elems)
    add_decoupling_cap("C6", fg_x + 33.02, fg_y + 5.08, "VBAT", elements)

    # PWR_FLAG on GND
    elements.append(kicad_pwr_flag(px + 50.80, py + 73.66, 4))
    elements.append(kicad_wire(px + 50.80, py + 73.66, px + 50.80, py + 76.20))
    elements.append(kicad_global_label("GND", px + 50.80, py + 76.20, 270, "input"))

    # =========================================================
    # SECTION 2: ESP32-S3 MCU  (x=180, y=20)
    # =========================================================
    mx, my = 180.34, 20.32

    elements.append(kicad_text("ESP32-S3 MCU", mx + 20.32, my - 7.62, 4.0))

    # Build a large block for ESP32-S3
    esp_left_pins = [
        ("3V3", "3V3", True),
        ("GND", "GND", True),
        ("GPIO1", "MEASURE_BTN", False),
        ("GPIO2", "FAN_GATE", False),
        ("GPIO4", "STEP", False),
        ("GPIO5", "UV_GATE", False),
        ("GPIO6", "RGB_R", False),
        ("GPIO7", "RGB_G", False),
        ("GPIO8", "RGB_B", False),
        ("GPIO9", "THERM_ADC", False),
        ("GPIO10", "SPI_MOSI", False),
        ("GPIO11", "SPI_SCK", False),
        ("GPIO12", "TFT_CS", False),
        ("GPIO13", "TFT_DC", False),
        ("GPIO14", "TFT_RST", False),
        ("GPIO15", "HEATER_GATE", False),
        ("GPIO16", "DIR", False),
        ("GPIO17", "LIMIT_SW", False),
        ("GPIO18", "I2C_SCL", False),
        ("GPIO19", "I2C_SDA", False),
    ]
    esp_right_pins = [
        ("GPIO20", "REED_SW", False),
        ("GPIO21", "BUZZER", False),
        ("GPIO35", "SD_CS", False),
        ("GPIO36", "CAM_D0", False),
        ("GPIO37", "CAM_D1", False),
        ("GPIO38", "CAM_D2", False),
        ("GPIO39", "CAM_D3", False),
        ("GPIO40", "CAM_D4", False),
        ("GPIO41", "CAM_D5", False),
        ("GPIO42", "CAM_D6", False),
        ("GPIO43", "CAM_D7", False),
        ("GPIO44", "CAM_PCLK", False),
        ("GPIO45", "CAM_VSYNC", False),
        ("GPIO46", "CAM_HREF", False),
        ("GPIO47", "CAM_XCLK", False),
        ("GPIO48", "CAM_SIOD", False),
        ("SPI_MISO", "SPI_MISO", False),
        ("BARCODE_TX", "BARCODE_TX", False),
        ("BARCODE_RX", "BARCODE_RX", False),
        ("EN", None, False),
    ]

    esp_elems = make_module_block_global(
        "U5: ESP32-S3-WROOM-1", mx, my, 76.20,
        left_pins=esp_left_pins,
        right_pins=esp_right_pins,
    )
    elements.extend(esp_elems)

    # Decoupling caps for ESP32
    add_decoupling_cap("C7", mx + 91.44, my + 5.08, "3V3", elements,
                       bulk_ref="C8", bulk_value="10uF")

    # =========================================================
    # SECTION 3: SENSORS & I2C  (x=320, y=20)
    # =========================================================
    sx, sy = 320.04, 20.32

    elements.append(kicad_text("SENSORS & I2C", sx + 15.24, sy - 7.62, 4.0))

    # --- I2C Pull-up Resistors (4.7k) ---
    elements.append(kicad_text("I2C Pull-ups", sx, sy, 1.5))
    # R_SCL
    rscl_x, rscl_y = sx + 5.08, sy + 10.16
    elements.append(make_resistor("R1", "4.7k", rscl_x, rscl_y))
    p1_scl = resistor_pin1(rscl_x, rscl_y)
    p2_scl = resistor_pin2(rscl_x, rscl_y)
    elements.append(kicad_global_label("3V3", p1_scl[0], p1_scl[1], 0, "bidirectional"))
    elements.append(kicad_label("I2C_SCL", p2_scl[0], p2_scl[1], 270))

    # R_SDA
    rsda_x, rsda_y = sx + 15.24, sy + 10.16
    elements.append(make_resistor("R2", "4.7k", rsda_x, rsda_y))
    p1_sda = resistor_pin1(rsda_x, rsda_y)
    p2_sda = resistor_pin2(rsda_x, rsda_y)
    elements.append(kicad_global_label("3V3", p1_sda[0], p1_sda[1], 0, "bidirectional"))
    elements.append(kicad_label("I2C_SDA", p2_sda[0], p2_sda[1], 270))

    # --- SHT31 Humidity/Temp Sensor ---
    sht_x, sht_y = sx, sy + 25.40
    sht_elems = make_module_block(
        "U6: SHT31 Humidity Sensor", sht_x, sht_y, 38.10,
        left_pins=[
            ("VDD", "3V3"),
            ("GND", "GND"),
            ("SDA", "I2C_SDA"),
        ],
        right_pins=[
            ("SCL", "I2C_SCL"),
            ("ADDR", None),
            ("ALT", None),
        ]
    )
    elements.extend(sht_elems)
    # Global labels for power pins
    elements.append(kicad_global_label("3V3", sht_x, sht_y + 5.08, 180, "bidirectional"))
    elements.append(kicad_global_label("GND", sht_x, sht_y + 10.16, 180, "input"))
    add_decoupling_cap("C9", sht_x + 50.80, sht_y + 5.08, "3V3", elements)

    # --- BH1750 Light Sensor ---
    bh_x, bh_y = sx, sy + 66.04
    bh_elems = make_module_block(
        "U7: BH1750 Light Sensor", bh_x, bh_y, 38.10,
        left_pins=[
            ("VCC", "3V3"),
            ("GND", "GND"),
            ("SDA", "I2C_SDA"),
        ],
        right_pins=[
            ("SCL", "I2C_SCL"),
            ("ADDR", None),
        ]
    )
    elements.extend(bh_elems)
    elements.append(kicad_global_label("3V3", bh_x, bh_y + 5.08, 180, "bidirectional"))
    elements.append(kicad_global_label("GND", bh_x, bh_y + 10.16, 180, "input"))
    add_decoupling_cap("C10", bh_x + 50.80, bh_y + 5.08, "3V3", elements)

    # --- DS3231 RTC ---
    rtc_x, rtc_y = sx, sy + 111.76
    rtc_elems = make_module_block(
        "U8: DS3231 RTC", rtc_x, rtc_y, 38.10,
        left_pins=[
            ("VCC", "3V3"),
            ("GND", "GND"),
            ("SDA", "I2C_SDA"),
        ],
        right_pins=[
            ("SCL", "I2C_SCL"),
            ("SQW", None),
            ("32K", None),
        ]
    )
    elements.extend(rtc_elems)
    elements.append(kicad_global_label("3V3", rtc_x, rtc_y + 5.08, 180, "bidirectional"))
    elements.append(kicad_global_label("GND", rtc_x, rtc_y + 10.16, 180, "input"))
    add_decoupling_cap("C11", rtc_x + 50.80, rtc_y + 5.08, "3V3", elements)

    # --- NTC Thermistor Voltage Divider ---
    th_x, th_y = sx + 40.64, sy + 25.40
    elements.append(kicad_text("NTC Thermistor Divider", th_x, th_y, 1.5))

    # Top resistor (NTC): pin1=3V3, pin2=midpoint
    ntc_x, ntc_y = th_x + 7.62, th_y + 10.16
    elements.append(make_resistor("R3", "NTC 10k", ntc_x, ntc_y))
    p1_ntc = resistor_pin1(ntc_x, ntc_y)
    p2_ntc = resistor_pin2(ntc_x, ntc_y)
    elements.append(kicad_global_label("3V3", p1_ntc[0], p1_ntc[1], 0, "bidirectional"))

    # Bottom resistor (fixed 10k): pin1=midpoint, pin2=GND
    fix_x, fix_y = th_x + 7.62, th_y + 20.32
    elements.append(make_resistor("R4", "10k", fix_x, fix_y))
    p1_fix = resistor_pin1(fix_x, fix_y)
    p2_fix = resistor_pin2(fix_x, fix_y)
    elements.append(kicad_global_label("GND", p2_fix[0], p2_fix[1], 270, "input"))

    # Wire midpoint: R3 pin2 to R4 pin1
    elements.append(kicad_wire(p2_ntc[0], p2_ntc[1], p1_fix[0], p1_fix[1]))
    # ADC label at midpoint
    mid_y = (p2_ntc[1] + p1_fix[1]) / 2
    elements.append(kicad_wire(p2_ntc[0], p2_ntc[1], p2_ntc[0] + 5.08, p2_ntc[1]))
    elements.append(kicad_label("THERM_ADC", p2_ntc[0] + 5.08, p2_ntc[1], 0))

    # =========================================================
    # SECTION 4: CAMERA & OPTICS  (x=320, y=170)
    # =========================================================
    cx, cy = 320.04, 170.18

    elements.append(kicad_text("CAMERA & OPTICS", cx + 15.24, cy - 7.62, 4.0))

    # --- OV2640 Camera Module ---
    cam_x, cam_y = cx, cy
    cam_left = [
        ("VCC", "3V3"),
        ("GND", "GND"),
        ("SIOD", "CAM_SIOD"),
        ("SIOC", "I2C_SCL"),
        ("VSYNC", "CAM_VSYNC"),
        ("HREF", "CAM_HREF"),
        ("PCLK", "CAM_PCLK"),
    ]
    cam_right = [
        ("XCLK", "CAM_XCLK"),
        ("D0", "CAM_D0"),
        ("D1", "CAM_D1"),
        ("D2", "CAM_D2"),
        ("D3", "CAM_D3"),
        ("D4", "CAM_D4"),
        ("D5", "CAM_D5"),
        ("D6", "CAM_D6"),
        ("D7", "CAM_D7"),
    ]
    cam_elems = make_module_block(
        "U9: OV2640 Camera", cam_x, cam_y, 43.18,
        left_pins=cam_left,
        right_pins=cam_right,
    )
    elements.extend(cam_elems)
    elements.append(kicad_global_label("3V3", cam_x, cam_y + 5.08, 180, "bidirectional"))
    elements.append(kicad_global_label("GND", cam_x, cam_y + 10.16, 180, "input"))
    add_decoupling_cap("C12", cam_x + 58.42, cam_y + 5.08, "3V3", elements,
                       bulk_ref="C13", bulk_value="10uF")

    # =========================================================
    # SECTION 5: DISPLAY & STORAGE  (x=180, y=200)
    # =========================================================
    dx, dy = 180.34, 200.66

    elements.append(kicad_text("DISPLAY & STORAGE", dx + 15.24, dy - 7.62, 4.0))

    # --- ILI9341 TFT Display (SPI) ---
    tft_x, tft_y = dx, dy
    tft_elems = make_module_block(
        "U10: ILI9341 2.4in TFT", tft_x, tft_y, 38.10,
        left_pins=[
            ("VCC", "3V3"),
            ("GND", "GND"),
            ("CS", "TFT_CS"),
            ("DC", "TFT_DC"),
            ("RST", "TFT_RST"),
        ],
        right_pins=[
            ("MOSI", "SPI_MOSI"),
            ("SCK", "SPI_SCK"),
            ("LED", "3V3"),
            ("MISO", "SPI_MISO"),
        ]
    )
    elements.extend(tft_elems)
    elements.append(kicad_global_label("3V3", tft_x, tft_y + 5.08, 180, "bidirectional"))
    elements.append(kicad_global_label("GND", tft_x, tft_y + 10.16, 180, "input"))
    add_decoupling_cap("C14", tft_x + 50.80, tft_y + 5.08, "3V3", elements)

    # --- SD Card Module (SPI, shares bus) ---
    sd_x, sd_y = dx, dy + 55.88
    sd_elems = make_module_block(
        "U11: SD Card Module (SPI)", sd_x, sd_y, 38.10,
        left_pins=[
            ("VCC", "3V3"),
            ("GND", "GND"),
            ("CS", "SD_CS"),
        ],
        right_pins=[
            ("MOSI", "SPI_MOSI"),
            ("SCK", "SPI_SCK"),
            ("MISO", "SPI_MISO"),
        ]
    )
    elements.extend(sd_elems)
    elements.append(kicad_global_label("3V3", sd_x, sd_y + 5.08, 180, "bidirectional"))
    elements.append(kicad_global_label("GND", sd_x, sd_y + 10.16, 180, "input"))
    add_decoupling_cap("C15", sd_x + 50.80, sd_y + 5.08, "3V3", elements)

    # =========================================================
    # SECTION 6: MOTOR & ACTUATORS  (x=20, y=120)
    # =========================================================
    ax_m, ay_m = 20.32, 119.38

    elements.append(kicad_text("MOTOR & ACTUATORS", ax_m + 20.32, ay_m - 7.62, 4.0))

    # --- A4988 Stepper Driver ---
    a4_x, a4_y = ax_m, ay_m
    a4_elems = make_module_block_global(
        "U12: A4988 Stepper Driver", a4_x, a4_y, 43.18,
        left_pins=[
            ("STEP", "STEP", False),
            ("DIR", "DIR", False),
            ("VDD", "3V3", True),
            ("VMOT", "9V", True),
            ("GND", "GND", True),
            ("EN", None, False),
        ],
        right_pins=[
            ("1A", "STEPPER_1A", False),
            ("1B", "STEPPER_1B", False),
            ("2A", "STEPPER_2A", False),
            ("2B", "STEPPER_2B", False),
            ("MS1", None, False),
            ("MS2", None, False),
        ]
    )
    elements.extend(a4_elems)
    add_decoupling_cap("C16", a4_x + 58.42, a4_y + 5.08, "3V3", elements)
    # Bulk cap on VMOT
    add_decoupling_cap("C17", a4_x + 68.58, a4_y + 5.08, "9V", elements,
                       bulk_ref="C18", bulk_value="100uF")

    # --- NEMA 17 Stepper Motor ---
    nm_x, nm_y = ax_m + 83.82, ay_m
    nm_elems = make_module_block(
        "M1: NEMA 17 Stepper", nm_x, nm_y, 25.40,
        left_pins=[
            ("A1", "STEPPER_1A"),
            ("A2", "STEPPER_1B"),
            ("B1", "STEPPER_2A"),
            ("B2", "STEPPER_2B"),
        ],
        right_pins=[]
    )
    elements.extend(nm_elems)

    # --- Limit Switch ---
    ls_x, ls_y = ax_m + 83.82, ay_m + 45.72
    elements.append(kicad_text("Limit Switch", ls_x, ls_y, 1.5))
    sw_x, sw_y = ls_x + 10.16, ls_y + 7.62
    elements.append(make_switch("SW2", "Limit", sw_x, sw_y))
    sp1 = switch_pin1(sw_x, sw_y)
    sp2 = switch_pin2(sw_x, sw_y)
    elements.append(kicad_global_label("GND", sp1[0], sp1[1], 180, "input"))
    elements.append(kicad_label("LIMIT_SW", sp2[0], sp2[1], 0))
    # Pull-up
    pu_x, pu_y = snap(sp2[0] + 5.08), snap(sp2[1] - 5.08)
    elements.append(make_resistor("R5", "10k", pu_x, pu_y))
    p1_pu = resistor_pin1(pu_x, pu_y)
    p2_pu = resistor_pin2(pu_x, pu_y)
    elements.append(kicad_global_label("3V3", p1_pu[0], p1_pu[1], 0, "bidirectional"))
    elements.append(kicad_wire(p2_pu[0], p2_pu[1], sp2[0], sp2[1]))

    # --- UV-C LED + IRLZ44N MOSFET ---
    uv_x, uv_y = ax_m, ay_m + 50.80
    elements.append(kicad_text("UV-C LED Circuit", uv_x, uv_y, 1.5))
    uv_drain = add_mosfet_switch("Q1", "IRLZ44N", "R6", "UV_GATE", "UV_DRAIN",
                                  uv_x + 12.70, uv_y + 15.24, elements)
    # UV LED + series resistor above drain
    uvr_x, uvr_y = snap(uv_drain[0]), snap(uv_drain[1] - 10.16)
    elements.append(make_resistor("R7", "47R", uvr_x, uvr_y))
    p1_uvr = resistor_pin1(uvr_x, uvr_y)
    p2_uvr = resistor_pin2(uvr_x, uvr_y)
    elements.append(kicad_wire(p2_uvr[0], p2_uvr[1], uv_drain[0], uv_drain[1]))
    # LED above resistor
    uvled_x, uvled_y = snap(p1_uvr[0]), snap(p1_uvr[1] - 7.62)
    elements.append(make_led("D1", "UV-C", uvled_x, uvled_y, 90))
    led_a = led_pin_a(uvled_x, uvled_y, 90)
    led_k = led_pin_k(uvled_x, uvled_y, 90)
    elements.append(kicad_wire(led_a[0], led_a[1], p1_uvr[0], p1_uvr[1]))
    elements.append(kicad_global_label("9V", led_k[0], led_k[1], 0, "bidirectional"))

    # --- Heater Film + IRLZ44N MOSFET ---
    ht_x, ht_y = ax_m + 45.72, ay_m + 50.80
    elements.append(kicad_text("Heater Film Circuit", ht_x, ht_y, 1.5))
    ht_drain = add_mosfet_switch("Q2", "IRLZ44N", "R8", "HEATER_GATE", "HTR_DRAIN",
                                  ht_x + 12.70, ht_y + 15.24, elements)
    # Heater film load: just a label connecting to supply
    elements.append(kicad_text("Heater Film", snap(ht_drain[0] - 2.54), snap(ht_drain[1] - 5.08), 1.2))
    elements.append(kicad_global_label("9V", ht_drain[0], ht_drain[1], 0, "bidirectional"))

    # --- Vent Fan + 2N7000 MOSFET ---
    fn_x, fn_y = ax_m + 91.44, ay_m + 50.80
    elements.append(kicad_text("Vent Fan Circuit", fn_x, fn_y, 1.5))
    fn_drain = add_mosfet_switch("Q3", "2N7000", "R9", "FAN_GATE", "FAN_DRAIN",
                                  fn_x + 12.70, fn_y + 15.24, elements)
    elements.append(kicad_text("Vent Fan", snap(fn_drain[0] - 2.54), snap(fn_drain[1] - 5.08), 1.2))
    elements.append(kicad_global_label("5V", fn_drain[0], fn_drain[1], 0, "bidirectional"))
    # PWR_FLAG on 5V (define 5V rail here)
    elements.append(kicad_pwr_flag(fn_x + 30.48, fn_y, 5))
    elements.append(kicad_wire(fn_x + 30.48, fn_y, fn_x + 30.48, fn_y + 2.54))
    elements.append(kicad_global_label("5V", fn_x + 30.48, fn_y + 2.54, 270, "bidirectional"))

    # =========================================================
    # SECTION 7: UI (Button/LED/Buzzer)  (x=20, y=280)
    # =========================================================
    ux, uy = 20.32, 259.08

    elements.append(kicad_text("UI: BUTTON / LED / BUZZER", ux + 20.32, uy - 7.62, 4.0))

    # --- Measure Button with pull-up ---
    elements.append(kicad_text("Measure Button", ux, uy, 1.5))
    btn_x, btn_y = ux + 12.70, uy + 7.62
    elements.append(make_switch("SW1", "Measure", btn_x, btn_y))
    bp1 = switch_pin1(btn_x, btn_y)
    bp2 = switch_pin2(btn_x, btn_y)
    elements.append(kicad_global_label("GND", bp1[0], bp1[1], 180, "input"))
    elements.append(kicad_label("MEASURE_BTN", bp2[0], bp2[1], 0))
    # Pull-up resistor
    btn_pu_x, btn_pu_y = snap(bp2[0] + 5.08), snap(bp2[1] - 5.08)
    elements.append(make_resistor("R10", "10k", btn_pu_x, btn_pu_y))
    p1_btn = resistor_pin1(btn_pu_x, btn_pu_y)
    p2_btn = resistor_pin2(btn_pu_x, btn_pu_y)
    elements.append(kicad_global_label("3V3", p1_btn[0], p1_btn[1], 0, "bidirectional"))
    elements.append(kicad_wire(p2_btn[0], p2_btn[1], bp2[0], bp2[1]))

    # --- RGB LED (Common Anode) with 330 ohm resistors ---
    elements.append(kicad_text("RGB Status LED (Common Anode)", ux, uy + 22.86, 1.5))

    rgb_channels = [
        ("R11", "330R", "D2", "Red", "RGB_R", 0),
        ("R12", "330R", "D3", "Green", "RGB_G", 15.24),
        ("R13", "330R", "D4", "Blue", "RGB_B", 30.48),
    ]
    for r_ref, r_val, d_ref, d_val, net, x_offset in rgb_channels:
        ch_x = snap(ux + 5.08 + x_offset)
        ch_y = snap(uy + 30.48)

        # Resistor (vertical): pin1 (top) = from MCU GPIO, pin2 (bottom) = to LED cathode
        elements.append(make_resistor(r_ref, r_val, ch_x, ch_y))
        rp1 = resistor_pin1(ch_x, ch_y)
        rp2 = resistor_pin2(ch_x, ch_y)
        elements.append(kicad_label(net, rp1[0], rp1[1], 0))

        # LED (vertical, angle=270 so anode is at top, cathode at bottom)
        # Actually, use angle=90: pin1(K) goes up (y-3.81), pin2(A) goes down (y+3.81)
        # We want: Anode at top (3V3), Cathode at bottom (to resistor)
        # LED angle=270: K at (x, y+3.81), A at (x, y-3.81)
        led_x, led_y = ch_x, snap(rp2[1] + 7.62)
        elements.append(make_led(d_ref, d_val, led_x, led_y, 270))
        la = led_pin_a(led_x, led_y, 270)  # anode = goes to 3V3
        lk = led_pin_k(led_x, led_y, 270)  # cathode = goes to resistor

        # Wire cathode to resistor pin2
        elements.append(kicad_wire(lk[0], lk[1], rp2[0], rp2[1]))
        # Anode to 3V3
        elements.append(kicad_global_label("3V3", la[0], la[1], 270, "bidirectional"))

    # --- Active Buzzer ---
    bz_x, bz_y = ux + 55.88, uy
    elements.append(kicad_text("BZ1: Active Buzzer", bz_x, bz_y, 1.5))
    elements.append(kicad_label("BUZZER", bz_x, bz_y + 5.08, 180))
    elements.append(kicad_global_label("GND", bz_x + 10.16, bz_y + 5.08, 0, "input"))
    elements.append(kicad_text("(+) GPIO21", bz_x + 2.54, bz_y + 5.08, 1.0))

    # --- GM65 Barcode Scanner (UART) ---
    bc_x, bc_y = ux + 55.88, uy + 15.24
    bc_elems = make_module_block(
        "U13: GM65 Barcode Scanner", bc_x, bc_y, 38.10,
        left_pins=[
            ("VCC", "3V3"),
            ("GND", "GND"),
            ("TX", "BARCODE_RX"),
        ],
        right_pins=[
            ("RX", "BARCODE_TX"),
            ("TRIG", None),
        ]
    )
    elements.extend(bc_elems)
    elements.append(kicad_global_label("3V3", bc_x, bc_y + 5.08, 180, "bidirectional"))
    elements.append(kicad_global_label("GND", bc_x, bc_y + 10.16, 180, "input"))
    add_decoupling_cap("C19", bc_x + 50.80, bc_y + 5.08, "3V3", elements)

    # =========================================================
    # SECTION 8: SAFETY  (x=180, y=310)
    # =========================================================
    safex, safey = 180.34, 309.88

    elements.append(kicad_text("SAFETY", safex + 10.16, safey - 7.62, 4.0))

    # --- MC-38 Reed Switch with pull-up ---
    elements.append(kicad_text("MC-38 Reed Switch Interlock", safex, safey, 1.5))
    reed_x, reed_y = safex + 12.70, safey + 7.62
    elements.append(make_switch("SW3", "MC-38_Reed", reed_x, reed_y))
    rp1 = switch_pin1(reed_x, reed_y)
    rp2 = switch_pin2(reed_x, reed_y)
    elements.append(kicad_global_label("GND", rp1[0], rp1[1], 180, "input"))
    elements.append(kicad_label("REED_SW", rp2[0], rp2[1], 0))
    # Pull-up
    reed_pu_x, reed_pu_y = snap(rp2[0] + 5.08), snap(rp2[1] - 5.08)
    elements.append(make_resistor("R14", "10k", reed_pu_x, reed_pu_y))
    p1_reed = resistor_pin1(reed_pu_x, reed_pu_y)
    p2_reed = resistor_pin2(reed_pu_x, reed_pu_y)
    elements.append(kicad_global_label("3V3", p1_reed[0], p1_reed[1], 0, "bidirectional"))
    elements.append(kicad_wire(p2_reed[0], p2_reed[1], rp2[0], rp2[1]))

    # =========================================================
    # Assemble schematic
    # =========================================================
    lib_symbols = generate_lib_symbols()

    header = f'''(kicad_sch
  (version 20231120)
  (generator "python_urine_dipstick_generator_v2")
  (generator_version "8.0")
  (uuid "{uid()}")
  (paper "A0")

  (title_block
    (title "Urine Dipstick Analyzer v2.0")
    (date "2026-05-15")
    (rev "2.0")
    (comment 1 "ESP32-S3 Based Camera Dipstick Analyzer")
    (comment 2 "Power: LiPo 3.7V + USB-C Charging + MAX17048 Fuel Gauge")
    (comment 3 "Display: ILI9341 TFT | RTC: DS3231 | Camera: OV2640")
    (comment 4 "Generated by Python script v2.0")
  )

{lib_symbols}

'''

    footer = "\n)\n"

    content = header + "\n".join(elements) + footer
    return content


def generate_lib_symbols():
    """lib_symbols section with all required symbol definitions."""
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
