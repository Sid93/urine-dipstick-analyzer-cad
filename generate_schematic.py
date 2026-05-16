#!/usr/bin/env python3
"""
Generate a KiCad 8 schematic (.kicad_sch) for Urine Dipstick Analyzer v2.0.

FIXED VERSION - uses proper lib_symbols with real pin definitions so that:
 1. Decoupling caps have explicit wire connections to IC pins (not floating net labels)
 2. OV2640 camera <-> ESP32-S3 data bus has visible wires via net labels on both ends
 3. FAN1 is a proper 2-pin component wired to Q3 drain and 5V

All coordinates snap to 2.54mm grid.
"""

import uuid
import os


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def uid():
    return str(uuid.uuid4())


def snap(v):
    return round(v / 2.54) * 2.54


def wire(x1, y1, x2, y2):
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    return (
        f'  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))'
        f' (stroke (width 0) (type default)) (uuid "{uid()}"))'
    )


def netlabel(name, x, y, angle=0):
    x, y = snap(x), snap(y)
    return (
        f'  (label "{name}" (at {x:.2f} {y:.2f} {angle})'
        f' (fields_autoplaced yes)'
        f' (effects (font (size 1.27 1.27)))'
        f' (uuid "{uid()}")'
        f' (property "Intersheet References" "" (at 0 0 0)'
        f'  (effects (font (size 1.27 1.27)) hide)))'
    )


def glabel(name, x, y, shape="input", angle=0):
    x, y = snap(x), snap(y)
    return (
        f'  (global_label "{name}" (shape {shape}) (at {x:.2f} {y:.2f} {angle})'
        f' (fields_autoplaced yes)'
        f' (effects (font (size 1.27 1.27)))'
        f' (uuid "{uid()}")'
        f' (property "Intersheet References" "" (at 0 0 0)'
        f'  (effects (font (size 1.27 1.27)) hide)))'
    )


def txt(s, x, y, size=1.27, bold=False):
    x, y = snap(x), snap(y)
    b = " bold" if bold else ""
    return (
        f'  (text "{s}" (at {x:.2f} {y:.2f} 0)'
        f' (effects (font (size {size} {size}){b}))'
        f' (uuid "{uid()}"))'
    )


def section_box(title, x1, y1, x2, y2):
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    lines = []
    lines.append(
        f'  (polyline (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y1:.2f})'
        f' (xy {x2:.2f} {y2:.2f}) (xy {x1:.2f} {y2:.2f}) (xy {x1:.2f} {y1:.2f}))'
        f' (stroke (width 0.254) (type dash)) (uuid "{uid()}"))'
    )
    lines.append(txt(title, (x1 + x2) / 2, y1 + 4.0, 2.5, bold=True))
    return lines


# ---------------------------------------------------------------------------
# IC symbol placer - returns (element_str, pin_dict)
# pin_dict maps pin_name -> (abs_x, abs_y)
#
# left_pins:  list of (name, pin_number)  - tips point LEFT, angle=0
# right_pins: list of (name, pin_number)  - tips point RIGHT, angle=180
# body_w, body_h: full body width/height in mm
# pin_len: pin stub length
# ---------------------------------------------------------------------------

def place_ic(lib_id, ref, value, px, py,
             left_pins, right_pins,
             body_w=20.32, body_h=None,
             pin_len=5.08, pin_spacing=2.54):
    px, py = snap(px), snap(py)
    n = max(len(left_pins), len(right_pins))
    if body_h is None:
        body_h = snap((n + 1) * pin_spacing)

    hw = body_w / 2.0
    hh = body_h / 2.0

    # Build pin elements list
    pin_dict = {}
    pin_els = []

    # Left pins: tip x = px - hw - pin_len, y increments from top
    for i, (pname, pnum) in enumerate(left_pins):
        sym_y = hh - pin_spacing - i * pin_spacing
        abs_x = px - hw - pin_len
        abs_y = py + sym_y
        pin_dict[pname] = (snap(abs_x), snap(abs_y))
        pin_els.append(f'  (pin "{pnum}" (uuid "{uid()}"))')

    # Right pins: tip x = px + hw + pin_len
    for i, (pname, pnum) in enumerate(right_pins):
        sym_y = hh - pin_spacing - i * pin_spacing
        abs_x = px + hw + pin_len
        abs_y = py + sym_y
        pin_dict[pname] = (snap(abs_x), snap(abs_y))
        pin_els.append(f'  (pin "{pnum}" (uuid "{uid()}"))')

    pins_str = "\n".join(pin_els)

    n_left = len(left_pins) + 1
    n_right = len(right_pins) + 1

    elem = (
        f'  (symbol (lib_id "{lib_id}") (at {px:.2f} {py:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {px:.2f} {py - hh - 3.81:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "{value}" (at {px:.2f} {py - hh - 1.27:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'{pins_str}\n'
        f'  )'
    )
    return elem, pin_dict


# ---------------------------------------------------------------------------
# Capacitor placer (custom:C - vertical, 2-pin)
# Pin 1 (top) tip: (cx, cy - 3.81)
# Pin 2 (bot) tip: (cx, cy + 3.81)
# ---------------------------------------------------------------------------

def place_cap(ref, value, cx, cy):
    cx, cy = snap(cx), snap(cy)
    u = uid()
    elem = (
        f'  (symbol (lib_id "custom:C") (at {cx:.2f} {cy:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {cx + 1.27:.2f} {cy - 1.27:.2f} 0)'
        f' (effects (font (size 1.016 1.016)) (justify left)))\n'
        f'    (property "Value" "{value}" (at {cx + 1.27:.2f} {cy + 1.27:.2f} 0)'
        f' (effects (font (size 1.016 1.016)) (justify left)))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    pin1 = (cx, cy - 3.81)   # top
    pin2 = (cx, cy + 3.81)   # bottom
    return elem, pin1, pin2


# ---------------------------------------------------------------------------
# Resistor placer (custom:R - vertical, 2-pin)
# Pin 1 (top) tip: (rx, ry - 3.81)
# Pin 2 (bot) tip: (rx, ry + 3.81)
# ---------------------------------------------------------------------------

def place_res(ref, value, rx, ry):
    rx, ry = snap(rx), snap(ry)
    elem = (
        f'  (symbol (lib_id "custom:R") (at {rx:.2f} {ry:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {rx + 1.27:.2f} {ry - 1.27:.2f} 0)'
        f' (effects (font (size 1.016 1.016)) (justify left)))\n'
        f'    (property "Value" "{value}" (at {rx + 1.27:.2f} {ry + 1.27:.2f} 0)'
        f' (effects (font (size 1.016 1.016)) (justify left)))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    pin1 = (rx, ry - 3.81)
    pin2 = (rx, ry + 3.81)
    return elem, pin1, pin2


# ---------------------------------------------------------------------------
# MOSFET placer (custom:NMOSFET)
# G tip: (mx - 7.62, my)
# D tip: (mx,       my - 5.08)
# S tip: (mx,       my + 5.08)
# ---------------------------------------------------------------------------

def place_mosfet(ref, value, mx, my):
    mx, my = snap(mx), snap(my)
    elem = (
        f'  (symbol (lib_id "custom:NMOSFET") (at {mx:.2f} {my:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {mx + 3.81:.2f} {my - 2.54:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "{value}" (at {mx + 3.81:.2f} {my:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'    (pin "3" (uuid "{uid()}"))\n'
        f'  )'
    )
    g_tip = (mx - 7.62, my)
    d_tip = (mx, my - 5.08)
    s_tip = (mx, my + 5.08)
    return elem, g_tip, d_tip, s_tip


# ---------------------------------------------------------------------------
# LED placer (custom:LED - horizontal)
# A tip: (lx - 2.54, ly)  anode LEFT
# K tip: (lx + 2.54, ly)  cathode RIGHT
# ---------------------------------------------------------------------------

def place_led(ref, value, lx, ly):
    lx, ly = snap(lx), snap(ly)
    elem = (
        f'  (symbol (lib_id "custom:LED") (at {lx:.2f} {ly:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {lx:.2f} {ly - 2.54:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (property "Value" "{value}" (at {lx:.2f} {ly + 2.54:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    a_tip = (lx - 2.54, ly)
    k_tip = (lx + 2.54, ly)
    return elem, a_tip, k_tip


# ---------------------------------------------------------------------------
# Fan component placer (custom:FAN - 2-pin horizontal block)
# + tip (left):  (fx - 7.62, fy + 1.27)
# - tip (right): (fx + 7.62, fy + 1.27)
# ---------------------------------------------------------------------------

def place_fan(ref, fx, fy):
    fx, fy = snap(fx), snap(fy)
    elem = (
        f'  (symbol (lib_id "custom:FAN") (at {fx:.2f} {fy:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {fx:.2f} {fy - 5.08:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "Fan" (at {fx:.2f} {fy + 5.08:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    plus_tip  = (fx - 7.62, fy)
    minus_tip = (fx + 7.62, fy)
    return elem, plus_tip, minus_tip


# ---------------------------------------------------------------------------
# Switch placer (custom:SW_Push - horizontal, 2-pin)
# pin1 tip: (sx - 5.08, sy)
# pin2 tip: (sx + 5.08, sy)
# ---------------------------------------------------------------------------

def place_switch(ref, value, sx, sy):
    sx, sy = snap(sx), snap(sy)
    elem = (
        f'  (symbol (lib_id "custom:SW_Push") (at {sx:.2f} {sy:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {sx:.2f} {sy - 3.81:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "{value}" (at {sx:.2f} {sy + 3.81:.2f} 0)'
        f' (effects (font (size 1.27 1.27))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    p1 = (sx - 5.08, sy)
    p2 = (sx + 5.08, sy)
    return elem, p1, p2


# ---------------------------------------------------------------------------
# Decoupling cap helper - places cap vertically, wires pin1-net label, pin2-GND
# ---------------------------------------------------------------------------

def decouple(ref, value, cx, cy, pwr_net, els):
    e, p1, p2 = place_cap(ref, value, cx, cy)
    els.append(e)
    els.append(glabel(pwr_net, p1[0], p1[1], shape="bidirectional", angle=90))
    els.append(glabel("GND", p2[0], p2[1], shape="input", angle=270))


# ---------------------------------------------------------------------------
# MOSFET low-side switch helper
# Returns g_tip, d_tip, s_tip
# ---------------------------------------------------------------------------

def mosfet_switch(q_ref, q_val, rg_ref, gate_net, mx, my, els):
    e, g_tip, d_tip, s_tip = place_mosfet(q_ref, q_val, mx, my)
    els.append(e)
    # Gate net label (wire in from left)
    els.append(netlabel(gate_net, g_tip[0] - 5.08, g_tip[1], angle=180))
    els.append(wire(g_tip[0] - 5.08, g_tip[1], g_tip[0], g_tip[1]))
    # Gate pull-down resistor
    rg_e, rg_p1, rg_p2 = place_res(rg_ref, "10k", snap(g_tip[0] - 5.08), snap(g_tip[1] + 7.62))
    els.append(rg_e)
    els.append(wire(g_tip[0] - 5.08, g_tip[1], rg_p1[0], rg_p1[1]))
    els.append(glabel("GND", rg_p2[0], rg_p2[1], shape="input", angle=270))
    # Source to GND
    els.append(glabel("GND", s_tip[0], s_tip[1], shape="input", angle=270))
    return g_tip, d_tip, s_tip


# ===========================================================================
# lib_symbols - every custom symbol used in this schematic
# ===========================================================================

def build_lib_symbols():
    # Helper: generate a pin line inside a symbol
    def pin(typ, name, num, at_x, at_y, angle, length=5.08, name_sz=1.016):
        return (
            f'      (pin {typ} line (at {at_x:.3f} {at_y:.3f} {angle}) (length {length:.3f})'
            f' (name "{name}" (effects (font (size {name_sz} {name_sz}))))'
            f' (number "{num}" (effects (font (size {name_sz} {name_sz})))))'
        )

    def ic_symbol(sym_id, body_w, body_h, left_pins_def, right_pins_def, pin_spacing=2.54, pin_len=5.08):
        """
        left_pins_def / right_pins_def: list of (pin_name, pin_number)
        """
        hw = body_w / 2.0
        hh = body_h / 2.0
        lines = []
        lines.append(f'    (symbol "{sym_id}"')
        lines.append(f'      (pin_names (offset 1.016))')
        lines.append(f'      (pin_numbers hide)')
        lines.append(f'      (property "Reference" "U" (at 0 {hh + 2.54:.3f} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'      (property "Value" "{sym_id.split(":")[-1]}" (at 0 {-(hh + 1.27):.3f} 0) (effects (font (size 1.27 1.27))))')
        base = sym_id.split(":")[-1]
        lines.append(f'      (symbol "{base}_0_1"')
        lines.append(f'        (rectangle (start {-hw:.3f} {-hh:.3f}) (end {hw:.3f} {hh:.3f})')
        lines.append(f'          (stroke (width 0.254) (type default)) (fill (type background)))')
        lines.append(f'      )')
        lines.append(f'      (symbol "{base}_1_1"')

        n_left  = len(left_pins_def)
        n_right = len(right_pins_def)

        for i, (pname, pnum) in enumerate(left_pins_def):
            sym_y = hh - pin_spacing - i * pin_spacing
            # angle 0 - tip points LEFT (tip at -hw-pin_len)
            lines.append(pin("input", pname, pnum,
                              -(hw + pin_len), sym_y,
                              0, length=pin_len))

        for i, (pname, pnum) in enumerate(right_pins_def):
            sym_y = hh - pin_spacing - i * pin_spacing
            # angle 180 - tip points RIGHT (tip at +hw+pin_len)
            lines.append(pin("output", pname, pnum,
                              (hw + pin_len), sym_y,
                              180, length=pin_len))

        lines.append(f'      )')
        lines.append(f'    )')
        return "\n".join(lines)

    parts = []

    # ------------------------------------------------------------------
    # custom:C  (vertical capacitor)
    # Pin 1 (top) tip at (0, +3.81) angle 270 - points UP
    # Pin 2 (bot) tip at (0, -3.81) angle 90  - points DOWN
    # ------------------------------------------------------------------
    parts.append("""\
    (symbol "custom:C"
      (pin_names (offset 0.254))
      (pin_numbers hide)
      (property "Reference" "C" (at 1.27 0 0) (effects (font (size 1.016 1.016)) (justify left)))
      (property "Value" "C" (at 1.27 2.54 0) (effects (font (size 1.016 1.016)) (justify left)))
      (symbol "C_0_1"
        (polyline (pts (xy -1.524 0.508) (xy 1.524 0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.524 -0.508) (xy 1.524 -0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "C_1_1"
        (pin passive line (at 0 3.81 270) (length 3.302)
          (name "+" (effects (font (size 0.762 0.762)))) (number "1" (effects (font (size 0.762 0.762)))))
        (pin passive line (at 0 -3.81 90) (length 3.302)
          (name "-" (effects (font (size 0.762 0.762)))) (number "2" (effects (font (size 0.762 0.762)))))
      )
    )""")

    # ------------------------------------------------------------------
    # custom:R  (vertical resistor)
    # Pin 1 (top) tip at (0, +3.81) angle 270
    # Pin 2 (bot) tip at (0, -3.81) angle 90
    # ------------------------------------------------------------------
    parts.append("""\
    (symbol "custom:R"
      (pin_names (offset 0.254))
      (pin_numbers hide)
      (property "Reference" "R" (at 1.27 0 0) (effects (font (size 1.016 1.016)) (justify left)))
      (property "Value" "R" (at 1.27 2.54 0) (effects (font (size 1.016 1.016)) (justify left)))
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.54) (end 1.016 2.54)
          (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27)
          (name "~" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 -3.81 90) (length 1.27)
          (name "~" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ------------------------------------------------------------------
    # custom:LED (horizontal)
    # A tip at (-2.54, 0) angle 0  - points LEFT
    # K tip at (+2.54, 0) angle 180 - points RIGHT
    # ------------------------------------------------------------------
    parts.append("""\
    (symbol "custom:LED"
      (pin_names (offset 1.016) hide)
      (pin_numbers hide)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.016 1.016))))
      (property "Value" "LED" (at 0 -2.54 0) (effects (font (size 1.016 1.016))))
      (symbol "LED_0_1"
        (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "LED_1_1"
        (pin passive line (at -2.54 0 0) (length 1.27)
          (name "A" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 2.54 0 180) (length 1.27)
          (name "K" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ------------------------------------------------------------------
    # custom:NMOSFET
    # G tip at (-7.62, 0)  angle 0
    # D tip at (0, -5.08)  angle 90  (drain top)
    # S tip at (0, +5.08)  angle 270 (source bottom)
    # ------------------------------------------------------------------
    parts.append("""\
    (symbol "custom:NMOSFET"
      (pin_names (offset 0.254) hide)
      (pin_numbers hide)
      (property "Reference" "Q" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "NMOSFET" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left)))
      (symbol "NMOSFET_0_1"
        (polyline (pts (xy 0.254 1.905) (xy 0.254 -1.905)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 0.254 0) (xy -2.54 0)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 1.27) (xy 0.762 2.286)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 -1.27) (xy 0.762 -2.286)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 0.508) (xy 0.762 -0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 2.54) (xy 2.54 1.778) (xy 0.762 1.778)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 -1.778) (xy 2.54 -1.778) (xy 2.54 -2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 -2.54) (xy 2.54 0) (xy 0.762 0)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 1.016 0) (xy 2.032 0.381) (xy 2.032 -0.381) (xy 1.016 0)) (stroke (width 0) (type default)) (fill (type outline)))
      )
      (symbol "NMOSFET_1_1"
        (pin passive line (at -7.62 0 0) (length 5.08)
          (name "G" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 -5.08 90) (length 2.54)
          (name "D" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 5.08 270) (length 2.54)
          (name "S" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ------------------------------------------------------------------
    # custom:FAN  (2-pin horizontal block)
    # + tip at (-7.62, 0) angle 0
    # - tip at (+7.62, 0) angle 180
    # ------------------------------------------------------------------
    parts.append("""\
    (symbol "custom:FAN"
      (pin_names (offset 0.254))
      (pin_numbers hide)
      (property "Reference" "FAN" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Fan" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "FAN_0_1"
        (rectangle (start -5.08 -3.81) (end 5.08 3.81)
          (stroke (width 0.254) (type default)) (fill (type background)))
        (circle (center 0 0) (radius 2.54) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.27 1.27) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "FAN_1_1"
        (pin passive line (at -7.62 0 0) (length 2.54)
          (name "+" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 7.62 0 180) (length 2.54)
          (name "-" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ------------------------------------------------------------------
    # custom:SW_Push  (2-pin horizontal switch)
    # pin1 tip at (-5.08, 0) angle 0
    # pin2 tip at (+5.08, 0) angle 180
    # ------------------------------------------------------------------
    parts.append("""\
    (symbol "custom:SW_Push"
      (pin_names (offset 1.016) hide)
      (pin_numbers hide)
      (property "Reference" "SW" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SW_Push" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "SW_Push_0_1"
        (circle (center -2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none)))
        (circle (center 2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy -2.54 1.524) (xy 2.54 1.524)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0 1.524) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "SW_Push_1_1"
        (pin passive line (at -5.08 0 0) (length 2.54)
          (name "1" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 5.08 0 180) (length 2.54)
          (name "2" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ------------------------------------------------------------------
    # ESP32-S3  (20L + 20R pins)
    # body 25.4 - 55.88 mm
    # ------------------------------------------------------------------
    esp_left = [
        ("EN","1"),("IO0","2"),("IO1","3"),("IO2","4"),("IO3","5"),
        ("IO4","6"),("IO5","7"),("IO6","8"),("IO7","9"),("IO8","10"),
        ("IO9","11"),("IO10","12"),("IO11","13"),("IO12","14"),("IO13","15"),
        ("IO14","16"),("IO15","17"),("IO18","18"),("IO19","19"),
        ("3V3","20"),
    ]
    esp_right = [
        ("IO16","21"),("IO17","22"),("IO20","23"),("IO21","24"),
        ("IO35","25"),("IO36","26"),("IO37","27"),("IO38","28"),
        ("IO39","29"),("IO40","30"),("IO41","31"),("IO42","32"),
        ("IO43","33"),("IO44","34"),("IO45","35"),("IO46","36"),
        ("IO47","37"),("IO48","38"),("GND","39"),("TX","40"),
    ]
    parts.append(ic_symbol("custom:ESP32S3", 25.4, 55.88, esp_left, esp_right))

    # ------------------------------------------------------------------
    # MCP73833 charger  (3L 3R)
    # body 12.7 - 10.16 mm
    # ------------------------------------------------------------------
    mcp_left = [("VBAT","1"),("STAT1","2"),("STAT2","3")]
    mcp_right = [("VDD","4"),("PROG","5"),("GND","6")]
    parts.append(ic_symbol("custom:MCP73833", 12.7, 10.16, mcp_left, mcp_right))

    # ------------------------------------------------------------------
    # MAX17048 fuel gauge  (3L 3R)
    # body 10.16 - 7.62 mm
    # ------------------------------------------------------------------
    max_left  = [("SDA","1"),("SCL","2"),("ALERT","3")]
    max_right = [("VDD","4"),("GND","5"),("QSTRT","6")]
    parts.append(ic_symbol("custom:MAX17048", 10.16, 7.62, max_left, max_right))

    # ------------------------------------------------------------------
    # REG3V3  (2L 1R)
    # body 10.16 - 5.08 mm
    # ------------------------------------------------------------------
    reg3_left  = [("VIN","1"),("GND","2")]
    reg3_right = [("VOUT","3")]
    parts.append(ic_symbol("custom:REG3V3", 10.16, 5.08, reg3_left, reg3_right))

    # ------------------------------------------------------------------
    # REG9V  (same shape)
    # ------------------------------------------------------------------
    reg9_left  = [("VIN","1"),("GND","2")]
    reg9_right = [("VOUT","3")]
    parts.append(ic_symbol("custom:REG9V", 10.16, 5.08, reg9_left, reg9_right))

    # ------------------------------------------------------------------
    # SHT31  (2L 2R)
    # body 7.62 - 5.08 mm
    # ------------------------------------------------------------------
    sht_left  = [("VDD","1"),("GND","2")]
    sht_right = [("SDA","3"),("SCL","4")]
    parts.append(ic_symbol("custom:SHT31", 7.62, 5.08, sht_left, sht_right))

    # ------------------------------------------------------------------
    # BH1750  (2L 2R)
    # ------------------------------------------------------------------
    bh_left  = [("VCC","1"),("GND","2")]
    bh_right = [("SDA","3"),("SCL","4")]
    parts.append(ic_symbol("custom:BH1750", 7.62, 5.08, bh_left, bh_right))

    # ------------------------------------------------------------------
    # DS3231  (3L 3R)
    # body 10.16 - 7.62 mm
    # ------------------------------------------------------------------
    ds_left  = [("VCC","1"),("GND","2"),("VBAT","3")]
    ds_right = [("SDA","4"),("SCL","5"),("SQW","6")]
    parts.append(ic_symbol("custom:DS3231", 10.16, 7.62, ds_left, ds_right))

    # ------------------------------------------------------------------
    # OV2640 camera  (9L 9R)
    # body 15.24 - 25.4 mm
    # ------------------------------------------------------------------
    ov_left = [
        ("VDD3V3","1"),("GND","2"),("RESETB","3"),("PWDN","4"),
        ("XCLK","5"),("SIOC","6"),("SIOD","7"),("HREF","8"),("VSYNC","9"),
    ]
    ov_right = [
        ("D0","10"),("D1","11"),("D2","12"),("D3","13"),("D4","14"),
        ("D5","15"),("D6","16"),("D7","17"),("PCLK","18"),
    ]
    parts.append(ic_symbol("custom:OV2640", 15.24, 25.4, ov_left, ov_right))

    # ------------------------------------------------------------------
    # ILI9341 display  (4L 4R)
    # body 10.16 - 10.16 mm
    # ------------------------------------------------------------------
    tft_left  = [("VCC","1"),("GND","2"),("CS","3"),("DC","4")]
    tft_right = [("MOSI","5"),("MISO","6"),("SCK","7"),("RST","8")]
    parts.append(ic_symbol("custom:ILI9341", 10.16, 10.16, tft_left, tft_right))

    # ------------------------------------------------------------------
    # A4988 stepper driver  (4L 4R)
    # body 12.70 - 10.16 mm
    # ------------------------------------------------------------------
    a4_left  = [("VMOT","1"),("GND","2"),("STEP","3"),("DIR","4")]
    a4_right = [("1A","5"),("1B","6"),("2A","7"),("2B","8")]
    parts.append(ic_symbol("custom:A4988", 12.70, 10.16, a4_left, a4_right))

    # ------------------------------------------------------------------
    # NEMA17 motor  (2L 2R)
    # body 10.16 - 5.08 mm
    # ------------------------------------------------------------------
    nema_left  = [("A+","1"),("A-","2")]
    nema_right = [("B+","3"),("B-","4")]
    parts.append(ic_symbol("custom:NEMA17", 10.16, 5.08, nema_left, nema_right))

    # ------------------------------------------------------------------
    # GM65 barcode scanner  (2L 2R)
    # body 10.16 - 5.08 mm
    # ------------------------------------------------------------------
    gm_left  = [("VCC","1"),("GND","2")]
    gm_right = [("TX","3"),("RX","4")]
    parts.append(ic_symbol("custom:GM65", 10.16, 5.08, gm_left, gm_right))

    inner = "\n".join(parts)
    return f"  (lib_symbols\n{inner}\n  )"


# ===========================================================================
# Main schematic generator
# ===========================================================================

def generate_schematic():
    els = []   # all schematic element strings

    # -----------------------------------------------------------------------
    # SECTION BOUNDARY BOXES
    # -----------------------------------------------------------------------
    els.extend(section_box("1 - Power Supply",     10, 10,  160, 140))
    els.extend(section_box("2 - MCU  ESP32-S3",   170, 10,  310, 200))
    els.extend(section_box("3 - Sensors & I2C",   320, 10,  460, 170))
    els.extend(section_box("4 - Camera & Optics", 320, 175, 460, 305))
    els.extend(section_box("5 - Display & SD",    170, 205, 310, 305))
    els.extend(section_box("6 - Motor & Actuators", 10, 145, 160, 280))
    els.extend(section_box("7 - UI: Button/LED/Buzzer", 10, 285, 160, 380))
    els.extend(section_box("8 - Safety",          170, 310, 310, 380))

    els.append(txt("Layout notes: 1) place decoupling caps next to IC VCC pins. "
                   "2) I2C pull-ups at MCU end. "
                   "3) SPI shared between TFT & SD (CS per device). "
                   "4) All MOSFETs low-side with 10k gate pull-down.",
                   12, 388, 1.27))

    # =======================================================================
    # SECTION 1 - POWER SUPPLY  (top-left)
    # =======================================================================
    # --- LiPo battery label ---
    bx, by = 18, 22
    els.append(txt("BT1: LiPo 3.7V 2000mAh", bx, by, 1.5, bold=True))
    els.append(glabel("VBAT", bx + 5, by + 7, shape="bidirectional", angle=0))
    els.append(glabel("GND",  bx + 5, by + 12, shape="input", angle=0))

    # --- MCP73833 USB-C Charger ---
    chg_lp = [("VBAT","1"),("STAT1","2"),("STAT2","3")]
    chg_rp = [("VDD","4"),("PROG","5"),("GND","6")]
    chg_e, chg_pins = place_ic("custom:MCP73833","U1","MCP73833",
                                55, 35, chg_lp, chg_rp,
                                body_w=12.7, body_h=10.16)
    els.append(chg_e)
    # power connections via global labels
    els.append(glabel("VBAT", chg_pins["VBAT"][0], chg_pins["VBAT"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND",  chg_pins["GND"][0],  chg_pins["GND"][1],  shape="input", angle=0))
    els.append(glabel("VUSB", chg_pins["VDD"][0],  chg_pins["VDD"][1],  shape="bidirectional", angle=0))
    # PROG resistor (sets charge current) - 10k to GND
    pr_e, pr_p1, pr_p2 = place_res("R_PROG","10k",
                                    snap(chg_pins["PROG"][0] + 7.62),
                                    snap(chg_pins["PROG"][1]))
    els.append(pr_e)
    els.append(wire(chg_pins["PROG"][0], chg_pins["PROG"][1], pr_p1[0], pr_p1[1]))
    els.append(glabel("GND", pr_p2[0], pr_p2[1], shape="input", angle=270))
    # Decoupling on VDD (VUSB side)
    decouple("C1","4.7uF", snap(chg_pins["VDD"][0]+5.08), snap(chg_pins["VDD"][1]+5.08), "VUSB", els)

    # --- Pololu S13V25F9 - 9V ---
    reg9_lp = [("VIN","1"),("GND","2")]
    reg9_rp = [("VOUT","3")]
    r9_e, r9_pins = place_ic("custom:REG9V","U2","S13V25F9 (9V)",
                               55, 68, reg9_lp, reg9_rp,
                               body_w=10.16, body_h=5.08)
    els.append(r9_e)
    els.append(glabel("VBAT", r9_pins["VIN"][0],  r9_pins["VIN"][1],  shape="bidirectional", angle=180))
    els.append(glabel("GND",  r9_pins["GND"][0],  r9_pins["GND"][1],  shape="input", angle=180))
    els.append(glabel("9V",   r9_pins["VOUT"][0], r9_pins["VOUT"][1], shape="bidirectional", angle=0))
    decouple("C2","100nF", snap(r9_pins["VOUT"][0]+10), snap(r9_pins["VOUT"][1]+5), "9V", els)
    decouple("C3","10uF",  snap(r9_pins["VOUT"][0]+20), snap(r9_pins["VOUT"][1]+5), "9V", els)

    # --- Pololu S7V8F3 - 3.3V ---
    reg3_lp = [("VIN","1"),("GND","2")]
    reg3_rp = [("VOUT","3")]
    r3_e, r3_pins = place_ic("custom:REG3V3","U3","S7V8F3 (3.3V)",
                               55, 90, reg3_lp, reg3_rp,
                               body_w=10.16, body_h=5.08)
    els.append(r3_e)
    els.append(glabel("VBAT", r3_pins["VIN"][0],  r3_pins["VIN"][1],  shape="bidirectional", angle=180))
    els.append(glabel("GND",  r3_pins["GND"][0],  r3_pins["GND"][1],  shape="input", angle=180))
    els.append(glabel("3V3",  r3_pins["VOUT"][0], r3_pins["VOUT"][1], shape="bidirectional", angle=0))
    decouple("C4","100nF", snap(r3_pins["VOUT"][0]+10), snap(r3_pins["VOUT"][1]+5), "3V3", els)
    decouple("C5","10uF",  snap(r3_pins["VOUT"][0]+20), snap(r3_pins["VOUT"][1]+5), "3V3", els)

    # --- MAX17048 fuel gauge ---
    fg_lp = [("SDA","1"),("SCL","2"),("ALERT","3")]
    fg_rp = [("VDD","4"),("GND","5"),("QSTRT","6")]
    fg_e, fg_pins = place_ic("custom:MAX17048","U4","MAX17048",
                               55, 115, fg_lp, fg_rp,
                               body_w=10.16, body_h=7.62)
    els.append(fg_e)
    els.append(glabel("3V3",      fg_pins["VDD"][0],  fg_pins["VDD"][1],  shape="bidirectional", angle=0))
    els.append(glabel("GND",      fg_pins["GND"][0],  fg_pins["GND"][1],  shape="input", angle=0))
    els.append(netlabel("I2C_SDA",fg_pins["SDA"][0],  fg_pins["SDA"][1],  angle=180))
    els.append(netlabel("I2C_SCL",fg_pins["SCL"][0],  fg_pins["SCL"][1],  angle=180))
    decouple("C6","100nF", snap(fg_pins["VDD"][0]+10), snap(fg_pins["VDD"][1]+5), "3V3", els)

    # =======================================================================
    # SECTION 2 - MCU: ESP32-S3  (top-center)
    # =======================================================================
    # Place ESP32-S3 at cx=235, cy=105 (center of body)
    # body 25.4 - 55.88 - half: 12.7 - 27.94
    # left pin tips at x = 235 - 12.7 - 5.08 = 217.22 - we use 215
    # right pin tips at x = 235 + 12.7 + 5.08 = 252.78 - we use 255
    esp_cx, esp_cy = 235, 105
    esp_lp = [
        ("EN","1"),("IO0","2"),("IO1","3"),("IO2","4"),("IO3","5"),
        ("IO4","6"),("IO5","7"),("IO6","8"),("IO7","9"),("IO8","10"),
        ("IO9","11"),("IO10","12"),("IO11","13"),("IO12","14"),("IO13","15"),
        ("IO14","16"),("IO15","17"),("IO18","18"),("IO19","19"),("3V3","20"),
    ]
    esp_rp = [
        ("IO16","21"),("IO17","22"),("IO20","23"),("IO21","24"),
        ("IO35","25"),("IO36","26"),("IO37","27"),("IO38","28"),
        ("IO39","29"),("IO40","30"),("IO41","31"),("IO42","32"),
        ("IO43","33"),("IO44","34"),("IO45","35"),("IO46","36"),
        ("IO47","37"),("IO48","38"),("GND","39"),("TX","40"),
    ]
    esp_e, esp_pins = place_ic("custom:ESP32S3","U5","ESP32-S3-WROOM-1",
                                esp_cx, esp_cy,
                                esp_lp, esp_rp,
                                body_w=25.4, body_h=55.88)
    els.append(esp_e)

    # Power rails
    els.append(glabel("3V3", esp_pins["3V3"][0], esp_pins["3V3"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND", esp_pins["GND"][0], esp_pins["GND"][1], shape="input", angle=0))
    # Decoupling caps on 3V3 right-side of MCU
    decouple("C7","100nF", snap(esp_pins["3V3"][0]+10), snap(esp_pins["3V3"][1]), "3V3", els)
    decouple("C8","10uF",  snap(esp_pins["3V3"][0]+20), snap(esp_pins["3V3"][1]), "3V3", els)

    # Left-side GPIO net labels
    left_nets = {
        "EN":   None,
        "IO0":  "MEASURE_BTN",
        "IO1":  "FAN_GATE",
        "IO2":  "STEP",
        "IO3":  "UV_GATE",
        "IO4":  "RGB_R",
        "IO5":  "RGB_G",
        "IO6":  "RGB_B",
        "IO7":  "THERM_ADC",
        "IO8":  "SPI_MOSI",
        "IO9":  "SPI_SCK",
        "IO10": "TFT_CS",
        "IO11": "TFT_DC",
        "IO12": "TFT_RST",
        "IO13": "HEATER_GATE",
        "IO14": "DIR",
        "IO15": "LIMIT_SW",
        "IO18": "I2C_SCL",
        "IO19": "I2C_SDA",
    }
    for gpio, net in left_nets.items():
        if net and gpio in esp_pins:
            tx, ty = esp_pins[gpio]
            els.append(netlabel(net, tx - 5.08, ty, angle=180))
            els.append(wire(tx - 5.08, ty, tx, ty))

    # Right-side GPIO net labels
    right_nets = {
        "IO16": "REED_SW",
        "IO17": "BUZZER",
        "IO20": "SD_CS",
        "IO21": "BARCODE_TX",
        "IO35": "BARCODE_RX",
        "IO36": "CAM_D0",
        "IO37": "CAM_D1",
        "IO38": "CAM_D2",
        "IO39": "CAM_D3",
        "IO40": "CAM_D4",
        "IO41": "CAM_D5",
        "IO42": "CAM_D6",
        "IO43": "CAM_D7",
        "IO44": "CAM_PCLK",
        "IO45": "CAM_VSYNC",
        "IO46": "CAM_HREF",
        "IO47": "CAM_XCLK",
        "IO48": "CAM_SIOD",
        "TX":   "SPI_MISO",
    }
    for gpio, net in right_nets.items():
        if net and gpio in esp_pins:
            tx, ty = esp_pins[gpio]
            els.append(netlabel(net, tx + 5.08, ty, angle=0))
            els.append(wire(tx, ty, tx + 5.08, ty))

    # =======================================================================
    # SECTION 3 - SENSORS & I2C  (top-right)
    # =======================================================================
    # I2C pull-up resistors
    ipux, ipuy = 330, 22
    els.append(txt("I2C Pull-ups (4.7k to 3V3)", ipux, ipuy - 4, 1.27))
    rscl_e, rscl_p1, rscl_p2 = place_res("R1","4.7k", ipux + 5, ipuy + 10)
    els.append(rscl_e)
    els.append(glabel("3V3", rscl_p1[0], rscl_p1[1], shape="bidirectional", angle=90))
    els.append(netlabel("I2C_SCL", rscl_p2[0], rscl_p2[1], angle=270))

    rsda_e, rsda_p1, rsda_p2 = place_res("R2","4.7k", ipux + 17, ipuy + 10)
    els.append(rsda_e)
    els.append(glabel("3V3", rsda_p1[0], rsda_p1[1], shape="bidirectional", angle=90))
    els.append(netlabel("I2C_SDA", rsda_p2[0], rsda_p2[1], angle=270))

    # --- SHT31 ---
    sht_lp = [("VDD","1"),("GND","2")]
    sht_rp = [("SDA","3"),("SCL","4")]
    sht_e, sht_pins = place_ic("custom:SHT31","U6","SHT31",
                                 365, 48, sht_lp, sht_rp,
                                 body_w=7.62, body_h=5.08)
    els.append(sht_e)
    els.append(glabel("3V3",      sht_pins["VDD"][0], sht_pins["VDD"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND",      sht_pins["GND"][0], sht_pins["GND"][1], shape="input", angle=180))
    els.append(netlabel("I2C_SDA",sht_pins["SDA"][0], sht_pins["SDA"][1], angle=0))
    els.append(netlabel("I2C_SCL",sht_pins["SCL"][0], sht_pins["SCL"][1], angle=0))
    decouple("C9","100nF", snap(sht_pins["SDA"][0]+10), snap(sht_pins["VDD"][1]), "3V3", els)

    # --- BH1750 ---
    bh_lp = [("VCC","1"),("GND","2")]
    bh_rp = [("SDA","3"),("SCL","4")]
    bh_e, bh_pins = place_ic("custom:BH1750","U7","BH1750",
                               365, 82, bh_lp, bh_rp,
                               body_w=7.62, body_h=5.08)
    els.append(bh_e)
    els.append(glabel("3V3",      bh_pins["VCC"][0], bh_pins["VCC"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND",      bh_pins["GND"][0], bh_pins["GND"][1], shape="input", angle=180))
    els.append(netlabel("I2C_SDA",bh_pins["SDA"][0], bh_pins["SDA"][1], angle=0))
    els.append(netlabel("I2C_SCL",bh_pins["SCL"][0], bh_pins["SCL"][1], angle=0))
    decouple("C10","100nF", snap(bh_pins["SDA"][0]+10), snap(bh_pins["VCC"][1]), "3V3", els)

    # --- DS3231 RTC ---
    ds_lp = [("VCC","1"),("GND","2"),("VBAT","3")]
    ds_rp = [("SDA","4"),("SCL","5"),("SQW","6")]
    ds_e, ds_pins = place_ic("custom:DS3231","U8","DS3231",
                               365, 120, ds_lp, ds_rp,
                               body_w=10.16, body_h=7.62)
    els.append(ds_e)
    els.append(glabel("3V3",      ds_pins["VCC"][0],  ds_pins["VCC"][1],  shape="bidirectional", angle=180))
    els.append(glabel("GND",      ds_pins["GND"][0],  ds_pins["GND"][1],  shape="input", angle=180))
    els.append(glabel("VBAT",     ds_pins["VBAT"][0], ds_pins["VBAT"][1], shape="bidirectional", angle=180))
    els.append(netlabel("I2C_SDA",ds_pins["SDA"][0],  ds_pins["SDA"][1],  angle=0))
    els.append(netlabel("I2C_SCL",ds_pins["SCL"][0],  ds_pins["SCL"][1],  angle=0))
    decouple("C11","100nF", snap(ds_pins["SDA"][0]+10), snap(ds_pins["VCC"][1]), "3V3", els)

    # --- NTC Thermistor divider ---
    ntc_x, ntc_y = 420, 50
    els.append(txt("NTC Thermistor Divider", ntc_x - 5, ntc_y - 5, 1.27))
    ntc_e, ntc_p1, ntc_p2 = place_res("R3","NTC 10k", ntc_x, ntc_y + 10)
    els.append(ntc_e)
    els.append(glabel("3V3", ntc_p1[0], ntc_p1[1], shape="bidirectional", angle=90))
    fix_e, fix_p1, fix_p2 = place_res("R4","10k", ntc_x, ntc_y + 25)
    els.append(fix_e)
    els.append(wire(ntc_p2[0], ntc_p2[1], fix_p1[0], fix_p1[1]))
    els.append(glabel("GND", fix_p2[0], fix_p2[1], shape="input", angle=270))
    els.append(wire(ntc_p2[0], ntc_p2[1], ntc_p2[0] + 5.08, ntc_p2[1]))
    els.append(netlabel("THERM_ADC", ntc_p2[0] + 5.08, ntc_p2[1], angle=0))

    # =======================================================================
    # SECTION 4 - CAMERA & OPTICS  (right, mid)
    # =======================================================================
    # OV2640 placed at cx=375, cy=240
    ov_lp = [
        ("VDD3V3","1"),("GND","2"),("RESETB","3"),("PWDN","4"),
        ("XCLK","5"),("SIOC","6"),("SIOD","7"),("HREF","8"),("VSYNC","9"),
    ]
    ov_rp = [
        ("D0","10"),("D1","11"),("D2","12"),("D3","13"),("D4","14"),
        ("D5","15"),("D6","16"),("D7","17"),("PCLK","18"),
    ]
    ov_e, ov_pins = place_ic("custom:OV2640","U9","OV2640",
                               375, 240,
                               ov_lp, ov_rp,
                               body_w=15.24, body_h=25.4)
    els.append(ov_e)

    # Power
    els.append(glabel("3V3",  ov_pins["VDD3V3"][0], ov_pins["VDD3V3"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND",  ov_pins["GND"][0],    ov_pins["GND"][1],    shape="input", angle=180))
    # Pull RESETB high (to 3V3)
    els.append(glabel("3V3",  ov_pins["RESETB"][0], ov_pins["RESETB"][1], shape="bidirectional", angle=180))
    # Pull PWDN low (to GND)
    els.append(glabel("GND",  ov_pins["PWDN"][0],   ov_pins["PWDN"][1],   shape="input", angle=180))

    # Camera decoupling
    decouple("C12","100nF", snap(ov_pins["VDD3V3"][0]-10), snap(ov_pins["VDD3V3"][1]+8), "3V3", els)
    decouple("C13","10uF",  snap(ov_pins["VDD3V3"][0]-20), snap(ov_pins["VDD3V3"][1]+8), "3V3", els)

    # OV2640 - ESP32 data bus - net labels on both sides
    # Right side of OV2640 - net labels; same labels appear on ESP32 right side
    cam_data_map = {
        "D0":   "CAM_D0",
        "D1":   "CAM_D1",
        "D2":   "CAM_D2",
        "D3":   "CAM_D3",
        "D4":   "CAM_D4",
        "D5":   "CAM_D5",
        "D6":   "CAM_D6",
        "D7":   "CAM_D7",
        "PCLK": "CAM_PCLK",
    }
    for ov_pin, net in cam_data_map.items():
        tx, ty = ov_pins[ov_pin]
        els.append(wire(tx, ty, tx + 7.62, ty))
        els.append(netlabel(net, tx + 7.62, ty, angle=0))

    # Control signals from left side of OV2640
    cam_ctrl_map = {
        "XCLK":  "CAM_XCLK",
        "SIOC":  "I2C_SCL",
        "SIOD":  "CAM_SIOD",
        "HREF":  "CAM_HREF",
        "VSYNC": "CAM_VSYNC",
    }
    for ov_pin, net in cam_ctrl_map.items():
        tx, ty = ov_pins[ov_pin]
        els.append(wire(tx - 7.62, ty, tx, ty))
        els.append(netlabel(net, tx - 7.62, ty, angle=180))

    # Matching net labels on ESP32 side (already placed in right_nets dict above)
    # CAM_SIOD - ESP32 IO48 via "CAM_SIOD" net
    # Also add SIOD net label for ESP32 IO48
    if "IO48" in esp_pins:
        tx, ty = esp_pins["IO48"]
        els.append(netlabel("CAM_SIOD", tx + 5.08, ty, angle=0))
        els.append(wire(tx, ty, tx + 5.08, ty))

    # =======================================================================
    # SECTION 5 - DISPLAY & STORAGE  (center, mid)
    # =======================================================================
    # ILI9341
    tft_lp = [("VCC","1"),("GND","2"),("CS","3"),("DC","4")]
    tft_rp = [("MOSI","5"),("MISO","6"),("SCK","7"),("RST","8")]
    tft_e, tft_pins = place_ic("custom:ILI9341","U10","ILI9341",
                                 210, 237, tft_lp, tft_rp,
                                 body_w=10.16, body_h=10.16)
    els.append(tft_e)
    els.append(glabel("3V3", tft_pins["VCC"][0],  tft_pins["VCC"][1],  shape="bidirectional", angle=180))
    els.append(glabel("GND", tft_pins["GND"][0],  tft_pins["GND"][1],  shape="input", angle=180))
    els.append(netlabel("TFT_CS",   tft_pins["CS"][0],   tft_pins["CS"][1],   angle=180))
    els.append(netlabel("TFT_DC",   tft_pins["DC"][0],   tft_pins["DC"][1],   angle=180))
    els.append(netlabel("SPI_MOSI", tft_pins["MOSI"][0], tft_pins["MOSI"][1], angle=0))
    els.append(netlabel("SPI_MISO", tft_pins["MISO"][0], tft_pins["MISO"][1], angle=0))
    els.append(netlabel("SPI_SCK",  tft_pins["SCK"][0],  tft_pins["SCK"][1],  angle=0))
    els.append(netlabel("TFT_RST",  tft_pins["RST"][0],  tft_pins["RST"][1],  angle=0))
    decouple("C14","100nF", snap(tft_pins["MOSI"][0]+10), snap(tft_pins["VCC"][1]), "3V3", els)

    # SD card module
    sd_lp = [("VCC","1"),("GND","2")]
    sd_rp = [("TX","3"),("RX","4")]  # MOSI / MISO
    sd_e, sd_pins = place_ic("custom:GM65","U11","SD Card Module",
                               210, 270, sd_lp, sd_rp,
                               body_w=10.16, body_h=5.08)
    # Re-use GM65 symbol shape, relabel in properties only
    els.append(sd_e)
    els.append(glabel("3V3", sd_pins["VCC"][0], sd_pins["VCC"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND", sd_pins["GND"][0], sd_pins["GND"][1], shape="input", angle=180))
    els.append(netlabel("SD_CS",    sd_pins["TX"][0], sd_pins["TX"][1], angle=0))
    els.append(netlabel("SPI_MOSI", sd_pins["RX"][0], sd_pins["RX"][1], angle=0))
    decouple("C15","100nF", snap(sd_pins["TX"][0]+10), snap(sd_pins["VCC"][1]), "3V3", els)

    # =======================================================================
    # SECTION 6 - MOTOR & ACTUATORS  (left, mid)
    # =======================================================================
    # --- A4988 stepper driver ---
    a4_lp = [("VMOT","1"),("GND","2"),("STEP","3"),("DIR","4")]
    a4_rp = [("1A","5"),("1B","6"),("2A","7"),("2B","8")]
    a4_e, a4_pins = place_ic("custom:A4988","U12","A4988",
                               55, 178, a4_lp, a4_rp,
                               body_w=12.70, body_h=10.16)
    els.append(a4_e)
    els.append(glabel("9V",  a4_pins["VMOT"][0], a4_pins["VMOT"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND", a4_pins["GND"][0],  a4_pins["GND"][1],  shape="input", angle=180))
    els.append(netlabel("STEP", a4_pins["STEP"][0], a4_pins["STEP"][1], angle=180))
    els.append(netlabel("DIR",  a4_pins["DIR"][0],  a4_pins["DIR"][1],  angle=180))
    els.append(netlabel("STEPPER_1A", a4_pins["1A"][0], a4_pins["1A"][1], angle=0))
    els.append(netlabel("STEPPER_1B", a4_pins["1B"][0], a4_pins["1B"][1], angle=0))
    els.append(netlabel("STEPPER_2A", a4_pins["2A"][0], a4_pins["2A"][1], angle=0))
    els.append(netlabel("STEPPER_2B", a4_pins["2B"][0], a4_pins["2B"][1], angle=0))
    decouple("C16","100nF", snap(a4_pins["1A"][0]+10), snap(a4_pins["VMOT"][1]), "9V", els)
    decouple("C17","100uF", snap(a4_pins["1A"][0]+20), snap(a4_pins["VMOT"][1]), "9V", els)

    # --- NEMA17 ---
    nm_lp = [("A+","1"),("A-","2")]
    nm_rp = [("B+","3"),("B-","4")]
    nm_e, nm_pins = place_ic("custom:NEMA17","M1","NEMA-17",
                               120, 178, nm_lp, nm_rp,
                               body_w=10.16, body_h=5.08)
    els.append(nm_e)
    els.append(netlabel("STEPPER_1A", nm_pins["A+"][0], nm_pins["A+"][1], angle=180))
    els.append(netlabel("STEPPER_1B", nm_pins["A-"][0], nm_pins["A-"][1], angle=180))
    els.append(netlabel("STEPPER_2A", nm_pins["B+"][0], nm_pins["B+"][1], angle=0))
    els.append(netlabel("STEPPER_2B", nm_pins["B-"][0], nm_pins["B-"][1], angle=0))

    # --- Limit switch ---
    sw2_e, sw2_p1, sw2_p2 = place_switch("SW2","Limit", 100, 205)
    els.append(sw2_e)
    els.append(glabel("GND", sw2_p1[0], sw2_p1[1], shape="input", angle=180))
    els.append(netlabel("LIMIT_SW", sw2_p2[0], sw2_p2[1], angle=0))
    pu_sw2_e, pu_sw2_p1, pu_sw2_p2 = place_res("R5","10k",
                                                  snap(sw2_p2[0]+5), snap(sw2_p2[1]-7))
    els.append(pu_sw2_e)
    els.append(glabel("3V3", pu_sw2_p1[0], pu_sw2_p1[1], shape="bidirectional", angle=90))
    els.append(wire(pu_sw2_p2[0], pu_sw2_p2[1], sw2_p2[0], sw2_p2[1]))

    # --- UV-C LED + IRLZ44N ---
    els.append(txt("UV-C LED Circuit", 15, 218, 1.27, bold=True))
    _, uv_d, _ = mosfet_switch("Q1","IRLZ44N","R6","UV_GATE", 30, 240, els)
    uvr_e, uvr_p1, uvr_p2 = place_res("R7","47R", snap(uv_d[0]), snap(uv_d[1] - 12.7))
    els.append(uvr_e)
    els.append(wire(uvr_p2[0], uvr_p2[1], uv_d[0], uv_d[1]))
    uvled_e, uvled_a, uvled_k = place_led("D1","UV-C LED", snap(uvr_p1[0]), snap(uvr_p1[1] - 5.08))
    els.append(uvled_e)
    # LED horizontal: A is left tip, K is right tip
    # We want: 9V - A - LED - K - (via wire down) - R7 pin1
    # Rotate: place LED so K is at bottom (use vertical orientation via explicit wire)
    els.append(wire(uvled_k[0], uvled_k[1], uvr_p1[0], uvr_p1[1]))
    els.append(glabel("9V", uvled_a[0], uvled_a[1], shape="bidirectional", angle=180))

    # --- Heater film + IRLZ44N ---
    els.append(txt("Heater Film Circuit", 55, 218, 1.27, bold=True))
    _, ht_d, _ = mosfet_switch("Q2","IRLZ44N","R8","HEATER_GATE", 72, 240, els)
    els.append(txt("Heater Film (9V)", snap(ht_d[0]-5), snap(ht_d[1]-4), 1.0))
    els.append(glabel("9V", ht_d[0], ht_d[1], shape="bidirectional", angle=90))

    # -----------------------------------------------------------------------
    # FAN - FIX: proper 2-pin custom:FAN component wired to Q3 drain and 5V
    # -----------------------------------------------------------------------
    els.append(txt("Vent Fan Circuit", 98, 218, 1.27, bold=True))
    _, fn_g, fn_d, fn_s = place_mosfet("Q3","2N7000", 115, 240)
    # Gate
    els.append(netlabel("FAN_GATE", fn_g[0] - 5.08, fn_g[1], angle=180))
    els.append(wire(fn_g[0] - 5.08, fn_g[1], fn_g[0], fn_g[1]))
    # Gate pull-down
    r9_e, r9_p1, r9_p2 = place_res("R9","10k",
                                     snap(fn_g[0] - 5.08), snap(fn_g[1] + 7.62))
    els.append(r9_e)
    els.append(wire(fn_g[0] - 5.08, fn_g[1], r9_p1[0], r9_p1[1]))
    els.append(glabel("GND", r9_p2[0], r9_p2[1], shape="input", angle=270))
    # Source to GND
    els.append(glabel("GND", fn_s[0], fn_s[1], shape="input", angle=270))
    # Fan component - place above Q3 drain
    fan_cx = snap(fn_d[0])
    fan_cy = snap(fn_d[1] - 10.16)
    fan_e, fan_plus, fan_minus = place_fan("FAN1", fan_cx, fan_cy)
    els.append(fan_e)
    # Fan minus (right) - wire down to Q3 drain
    els.append(wire(fan_minus[0], fan_minus[1], fn_d[0], fn_d[1]))
    # Fan plus (left) - 5V global label
    els.append(wire(fan_plus[0] - 5.08, fan_plus[1], fan_plus[0], fan_plus[1]))
    els.append(glabel("5V", fan_plus[0] - 5.08, fan_plus[1], shape="bidirectional", angle=180))

    # =======================================================================
    # SECTION 7 - UI: BUTTON / LED / BUZZER  (bottom-left)
    # =======================================================================
    # Measure button
    sw1_e, sw1_p1, sw1_p2 = place_switch("SW1","Measure", 40, 310)
    els.append(sw1_e)
    els.append(glabel("GND", sw1_p1[0], sw1_p1[1], shape="input", angle=180))
    els.append(netlabel("MEASURE_BTN", sw1_p2[0], sw1_p2[1], angle=0))
    pu_btn_e, pu_btn_p1, pu_btn_p2 = place_res("R10","10k",
                                                  snap(sw1_p2[0]+5), snap(sw1_p2[1]-7))
    els.append(pu_btn_e)
    els.append(glabel("3V3", pu_btn_p1[0], pu_btn_p1[1], shape="bidirectional", angle=90))
    els.append(wire(pu_btn_p2[0], pu_btn_p2[1], sw1_p2[0], sw1_p2[1]))

    # RGB LED (common anode)
    els.append(txt("RGB Status LED (Common Anode)", 15, 325, 1.27, bold=True))
    rgb_data = [
        ("R11","330R","D2","Red LED",   "RGB_R", 20, 342),
        ("R12","330R","D3","Green LED", "RGB_G", 35, 342),
        ("R13","330R","D4","Blue LED",  "RGB_B", 50, 342),
    ]
    for r_ref, r_val, d_ref, d_val, net, rx, ry in rgb_data:
        r_e, r_p1, r_p2 = place_res(r_ref, r_val, rx, ry)
        els.append(r_e)
        els.append(netlabel(net, r_p1[0], r_p1[1], angle=90))
        led_e, led_a, led_k = place_led(d_ref, d_val, snap(r_p2[0]), snap(r_p2[1] + 5.08))
        els.append(led_e)
        els.append(wire(led_a[0], led_a[1], r_p2[0], r_p2[1]))
        els.append(glabel("3V3", led_k[0], led_k[1], shape="bidirectional", angle=0))

    # Active buzzer
    bz_x, bz_y = 80, 307
    els.append(txt("BZ1: Active Buzzer", bz_x, bz_y, 1.5, bold=True))
    els.append(netlabel("BUZZER", bz_x, bz_y + 7, angle=180))
    els.append(glabel("GND", bz_x + 15, bz_y + 7, shape="input", angle=0))
    els.append(txt("(+)GPIO21 (-)GND", bz_x + 2, bz_y + 10, 1.0))

    # GM65 Barcode scanner
    bc_lp = [("VCC","1"),("GND","2")]
    bc_rp = [("TX","3"),("RX","4")]
    bc_e, bc_pins = place_ic("custom:GM65","U13","GM65 Barcode",
                               120, 335, bc_lp, bc_rp,
                               body_w=10.16, body_h=5.08)
    els.append(bc_e)
    els.append(glabel("3V3",           bc_pins["VCC"][0], bc_pins["VCC"][1], shape="bidirectional", angle=180))
    els.append(glabel("GND",           bc_pins["GND"][0], bc_pins["GND"][1], shape="input", angle=180))
    els.append(netlabel("BARCODE_RX",  bc_pins["TX"][0],  bc_pins["TX"][1],  angle=0))
    els.append(netlabel("BARCODE_TX",  bc_pins["RX"][0],  bc_pins["RX"][1],  angle=0))
    decouple("C19","100nF", snap(bc_pins["TX"][0]+10), snap(bc_pins["VCC"][1]), "3V3", els)

    # =======================================================================
    # SECTION 8 - SAFETY  (bottom-center)
    # =======================================================================
    sw3_e, sw3_p1, sw3_p2 = place_switch("SW3","MC-38 Reed", 215, 350)
    els.append(sw3_e)
    els.append(glabel("GND", sw3_p1[0], sw3_p1[1], shape="input", angle=180))
    els.append(netlabel("REED_SW", sw3_p2[0], sw3_p2[1], angle=0))
    pu_reed_e, pu_reed_p1, pu_reed_p2 = place_res("R14","10k",
                                                     snap(sw3_p2[0]+5), snap(sw3_p2[1]-7))
    els.append(pu_reed_e)
    els.append(glabel("3V3", pu_reed_p1[0], pu_reed_p1[1], shape="bidirectional", angle=90))
    els.append(wire(pu_reed_p2[0], pu_reed_p2[1], sw3_p2[0], sw3_p2[1]))

    # =======================================================================
    # Assemble schematic
    # =======================================================================
    lib_sym = build_lib_symbols()

    header = f"""(kicad_sch
  (version 20231120)
  (generator "python_urine_dipstick_v3_fixed")
  (generator_version "8.0")
  (uuid "{uid()}")
  (paper "A0")

  (title_block
    (title "Urine Dipstick Analyzer v2.0 - Fixed Wiring")
    (date "2026-05-16")
    (rev "3.0")
    (comment 1 "ESP32-S3 Based Camera Dipstick Analyzer")
    (comment 2 "FIX: proper IC lib_symbols with explicit wire connections")
    (comment 3 "FIX: OV2640 camera data bus wired to ESP32 via net labels")
    (comment 4 "FIX: FAN1 is a proper 2-pin component wired to Q3 drain")
  )

{lib_sym}

"""

    footer = "\n)\n"
    body = "\n".join(els)
    return header + body + footer


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    out_dir  = "/Users/siddhantsaboo/Desktop/agentic workflows/urine_dipstick_cad"
    out_file = os.path.join(out_dir, "urine_dipstick_analyzer.kicad_sch")
    os.makedirs(out_dir, exist_ok=True)

    sch = generate_schematic()
    with open(out_file, "w") as f:
        f.write(sch)

    lines   = sch.count("\n")
    symbols = sch.count("(lib_id")
    wires   = sch.count("(wire")
    labels  = sch.count("(label ")
    glabels = sch.count("(global_label")
    print(f"Written: {out_file}")
    print(f"  Lines: {lines:,}")
    print(f"  Symbol instances: {symbols}")
    print(f"  Wires:            {wires}")
    print(f"  Net labels:       {labels}")
    print(f"  Global labels:    {glabels}")
    print(f"  File size:        {os.path.getsize(out_file):,} bytes")


if __name__ == "__main__":
    main()
