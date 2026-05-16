#!/usr/bin/env python3
"""
Generate a KiCad schematic for the ESP32-WROOM-32E + BH1750FVI reference
design. Output: esp32_light_sensor.kicad_sch (KiCad 8/9 compatible,
version 20231120).

Design covers a production-grade USB-C powered ESP32 board with an I2C
ambient light sensor, including:

  1. USB-C input + protection (TVS, USBLC6 ESD, polyfuse, P-channel
     reverse polarity FET).
  2. 3.3V LDO power tree (AMS1117-3.3) with proper bulk + ceramic decoupling
     and a ferrite bead feeding the ESP32 VDD33.
  3. ESP32-WROOM-32E with all strapping pins set up correctly, EN reset RC
     and a tactile RESET + BOOT button.
  4. UART programming header (DTR-less, 6 pin, 2.54 mm pitch).
  5. BH1750FVI ambient light sensor on I2C with proper bypass and 4.7k
     pull-ups, plus DNP series RC EMI filter on the I2C lines.

Lessons applied from the parent urine-dipstick generator:

  * lib_symbol sub-symbol names MUST NOT include the "custom:" prefix
    (i.e. `(symbol "ESP32_0_1")` not `(symbol "custom:ESP32_0_1")`).
  * ASCII only.
  * Every IC pin tip is wired to its passive partner explicitly.
  * Decoupling caps are placed within visual proximity of their host pin.
"""

import os
import uuid


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
        f' (uuid "{uid()}"))'
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
    out = []
    out.append(
        f'  (polyline (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y1:.2f})'
        f' (xy {x2:.2f} {y2:.2f}) (xy {x1:.2f} {y2:.2f}) (xy {x1:.2f} {y1:.2f}))'
        f' (stroke (width 0.254) (type dash)) (uuid "{uid()}"))'
    )
    out.append(txt(title, (x1 + x2) / 2, y1 + 4.0, 2.5, bold=True))
    return out


# ---------------------------------------------------------------------------
# Generic IC placer - returns (element_str, pin_dict)
#   pin_dict maps pin_name -> (abs_x, abs_y) where the wire should attach.
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

    pin_dict = {}
    pin_els = []

    for i, (pname, pnum) in enumerate(left_pins):
        sym_y = hh - pin_spacing - i * pin_spacing
        abs_x = px - hw - pin_len
        abs_y = py + sym_y
        pin_dict[pname] = (snap(abs_x), snap(abs_y))
        pin_els.append(f'    (pin "{pnum}" (uuid "{uid()}"))')

    for i, (pname, pnum) in enumerate(right_pins):
        sym_y = hh - pin_spacing - i * pin_spacing
        abs_x = px + hw + pin_len
        abs_y = py + sym_y
        pin_dict[pname] = (snap(abs_x), snap(abs_y))
        pin_els.append(f'    (pin "{pnum}" (uuid "{uid()}"))')

    pins_str = "\n".join(pin_els)

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
# Passive placers
# ---------------------------------------------------------------------------

def place_cap(ref, value, cx, cy):
    cx, cy = snap(cx), snap(cy)
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
    return elem, (cx, cy - 3.81), (cx, cy + 3.81)


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
    return elem, (rx, ry - 3.81), (rx, ry + 3.81)


def place_ferrite(ref, value, fx, fy):
    """Ferrite bead, vertical, same pin geometry as resistor."""
    fx, fy = snap(fx), snap(fy)
    elem = (
        f'  (symbol (lib_id "custom:FB") (at {fx:.2f} {fy:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {fx + 1.27:.2f} {fy - 1.27:.2f} 0)'
        f' (effects (font (size 1.016 1.016)) (justify left)))\n'
        f'    (property "Value" "{value}" (at {fx + 1.27:.2f} {fy + 1.27:.2f} 0)'
        f' (effects (font (size 1.016 1.016)) (justify left)))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    return elem, (fx, fy - 3.81), (fx, fy + 3.81)


def place_diode(ref, value, dx, dy):
    """Generic diode, horizontal: A on left, K on right."""
    dx, dy = snap(dx), snap(dy)
    elem = (
        f'  (symbol (lib_id "custom:D") (at {dx:.2f} {dy:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {dx:.2f} {dy - 2.54:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (property "Value" "{value}" (at {dx:.2f} {dy + 2.54:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    return elem, (dx - 2.54, dy), (dx + 2.54, dy)


def place_pmos(ref, value, mx, my):
    """P-channel MOSFET (custom:PMOSFET), pin geometry mirrors NMOS:
       G tip (mx-7.62, my), D tip (mx, my+5.08), S tip (mx, my-5.08)."""
    mx, my = snap(mx), snap(my)
    elem = (
        f'  (symbol (lib_id "custom:PMOSFET") (at {mx:.2f} {my:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {mx + 5.08:.2f} {my - 2.54:.2f} 0)'
        f' (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'    (property "Value" "{value}" (at {mx + 5.08:.2f} {my:.2f} 0)'
        f' (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'    (pin "3" (uuid "{uid()}"))\n'
        f'  )'
    )
    return elem, (mx - 7.62, my), (mx, my + 5.08), (mx, my - 5.08)


def place_switch(ref, value, sx, sy):
    sx, sy = snap(sx), snap(sy)
    elem = (
        f'  (symbol (lib_id "custom:SW_Push") (at {sx:.2f} {sy:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {sx:.2f} {sy - 3.81:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (property "Value" "{value}" (at {sx:.2f} {sy + 3.81:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    return elem, (sx - 5.08, sy), (sx + 5.08, sy)


def place_polyfuse(ref, value, fx, fy):
    """Polyfuse, horizontal."""
    fx, fy = snap(fx), snap(fy)
    elem = (
        f'  (symbol (lib_id "custom:PolyFuse") (at {fx:.2f} {fy:.2f} 0) (unit 1)\n'
        f'    (property "Reference" "{ref}" (at {fx:.2f} {fy - 2.54:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (property "Value" "{value}" (at {fx:.2f} {fy + 2.54:.2f} 0)'
        f' (effects (font (size 1.016 1.016))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'  )'
    )
    return elem, (fx - 5.08, fy), (fx + 5.08, fy)


def decouple(ref, value, cx, cy, pwr_net, els):
    e, p1, p2 = place_cap(ref, value, cx, cy)
    els.append(e)
    els.append(glabel(pwr_net, p1[0], p1[1], shape="bidirectional", angle=90))
    els.append(glabel("GND", p2[0], p2[1], shape="input", angle=270))


# ===========================================================================
# lib_symbols
# ===========================================================================

def build_lib_symbols():

    def pin(typ, name, num, at_x, at_y, angle, length=5.08, name_sz=1.016):
        return (
            f'      (pin {typ} line (at {at_x:.3f} {at_y:.3f} {angle}) (length {length:.3f})'
            f' (name "{name}" (effects (font (size {name_sz} {name_sz}))))'
            f' (number "{num}" (effects (font (size {name_sz} {name_sz})))))'
        )

    def ic_symbol(sym_id, body_w, body_h, left_pins_def, right_pins_def,
                  pin_spacing=2.54, pin_len=5.08):
        """sym_id is the FULL lib id (e.g. 'custom:ESP32'). The internal
        sub-symbol names MUST NOT include the 'custom:' prefix - they use
        only the bare symbol name (lesson learned from the parent project).
        """
        hw = body_w / 2.0
        hh = body_h / 2.0
        base = sym_id.split(":")[-1]
        lines = []
        lines.append(f'    (symbol "{sym_id}"')
        lines.append(f'      (pin_names (offset 1.016))')
        lines.append(f'      (pin_numbers hide)')
        lines.append(f'      (property "Reference" "U" (at 0 {hh + 2.54:.3f} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'      (property "Value" "{base}" (at 0 {-(hh + 1.27):.3f} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'      (symbol "{base}_0_1"')
        lines.append(f'        (rectangle (start {-hw:.3f} {-hh:.3f}) (end {hw:.3f} {hh:.3f})')
        lines.append(f'          (stroke (width 0.254) (type default)) (fill (type background)))')
        lines.append(f'      )')
        lines.append(f'      (symbol "{base}_1_1"')

        for i, (pname, pnum) in enumerate(left_pins_def):
            sym_y = hh - pin_spacing - i * pin_spacing
            lines.append(pin("passive", pname, pnum,
                             -(hw + pin_len), sym_y, 0, length=pin_len))

        for i, (pname, pnum) in enumerate(right_pins_def):
            sym_y = hh - pin_spacing - i * pin_spacing
            lines.append(pin("passive", pname, pnum,
                             (hw + pin_len), sym_y, 180, length=pin_len))

        lines.append(f'      )')
        lines.append(f'    )')
        return "\n".join(lines)

    parts = []

    # ---- custom:C ----
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

    # ---- custom:R ----
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

    # ---- custom:FB ferrite bead ----
    parts.append("""\
    (symbol "custom:FB"
      (pin_names (offset 0.254))
      (pin_numbers hide)
      (property "Reference" "FB" (at 1.27 0 0) (effects (font (size 1.016 1.016)) (justify left)))
      (property "Value" "FB" (at 1.27 2.54 0) (effects (font (size 1.016 1.016)) (justify left)))
      (symbol "FB_0_1"
        (rectangle (start -1.524 -2.54) (end 1.524 2.54)
          (stroke (width 0.254) (type default)) (fill (type background)))
        (polyline (pts (xy -1.524 -1.27) (xy 1.524 -1.27))
          (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "FB_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27)
          (name "~" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 -3.81 90) (length 1.27)
          (name "~" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ---- custom:D generic diode (horizontal) ----
    parts.append("""\
    (symbol "custom:D"
      (pin_names (offset 1.016) hide)
      (pin_numbers hide)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.016 1.016))))
      (property "Value" "D" (at 0 -2.54 0) (effects (font (size 1.016 1.016))))
      (symbol "D_0_1"
        (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27) (xy -1.27 1.27))
          (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "D_1_1"
        (pin passive line (at -2.54 0 0) (length 1.27)
          (name "A" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 2.54 0 180) (length 1.27)
          (name "K" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ---- custom:PolyFuse ----
    parts.append("""\
    (symbol "custom:PolyFuse"
      (pin_names (offset 1.016) hide)
      (pin_numbers hide)
      (property "Reference" "F" (at 0 2.54 0) (effects (font (size 1.016 1.016))))
      (property "Value" "PolyFuse" (at 0 -2.54 0) (effects (font (size 1.016 1.016))))
      (symbol "PolyFuse_0_1"
        (rectangle (start -2.54 -1.27) (end 2.54 1.27)
          (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.524 0.762) (xy 1.524 -0.762))
          (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "PolyFuse_1_1"
        (pin passive line (at -5.08 0 0) (length 2.54)
          (name "1" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 5.08 0 180) (length 2.54)
          (name "2" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ---- custom:PMOSFET (3 pin) ----
    # G tip at (-7.62, 0)  angle 0
    # D tip at (0, +5.08)  angle 270 (drain bottom for high-side pass)
    # S tip at (0, -5.08)  angle 90  (source top, on VBUS)
    parts.append("""\
    (symbol "custom:PMOSFET"
      (pin_names (offset 0.254) hide)
      (pin_numbers hide)
      (property "Reference" "Q" (at 5.08 1.905 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "PMOSFET" (at 5.08 0 0) (effects (font (size 1.27 1.27)) (justify left)))
      (symbol "PMOSFET_0_1"
        (polyline (pts (xy 0.254 1.905) (xy 0.254 -1.905)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 0.254 0) (xy -2.54 0)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 1.27) (xy 0.762 2.286)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 -1.27) (xy 0.762 -2.286)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 0.508) (xy 0.762 -0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy 2.54 2.54) (xy 2.54 1.778) (xy 0.762 1.778)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0.762 -1.778) (xy 2.54 -1.778) (xy 2.54 -2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 2.032 0) (xy 1.016 0.381) (xy 1.016 -0.381) (xy 2.032 0)) (stroke (width 0) (type default)) (fill (type outline)))
      )
      (symbol "PMOSFET_1_1"
        (pin passive line (at -7.62 0 0) (length 5.08)
          (name "G" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 5.08 270) (length 2.54)
          (name "D" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
        (pin passive line (at 0 -5.08 90) (length 2.54)
          (name "S" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
      )
    )""")

    # ---- custom:SW_Push ----
    parts.append("""\
    (symbol "custom:SW_Push"
      (pin_names (offset 1.016) hide)
      (pin_numbers hide)
      (property "Reference" "SW" (at 0 -3.81 0) (effects (font (size 1.016 1.016))))
      (property "Value" "SW_Push" (at 0 3.81 0) (effects (font (size 1.016 1.016))))
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

    # ---- custom:USB_C ----
    # Simplified 6-pin USB-C: VBUS, GND, CC1, CC2, D+, D-
    usbc_left  = [("VBUS","1"),("GND","2"),("CC1","3")]
    usbc_right = [("CC2","4"),("DP","5"),("DM","6")]
    parts.append(ic_symbol("custom:USB_C", 12.7, 10.16, usbc_left, usbc_right))

    # ---- custom:USBLC6 ESD diode array (USBLC6-2SC6) ----
    # 6-pin SOT-23-6: 1=IO1, 2=GND, 3=IO2, 4=IO2', 5=VBUS, 6=IO1'
    usblc_left  = [("IO1","1"),("GND","2"),("IO2","3")]
    usblc_right = [("IO2p","4"),("VBUS","5"),("IO1p","6")]
    parts.append(ic_symbol("custom:USBLC6", 10.16, 7.62, usblc_left, usblc_right))

    # ---- custom:AMS1117 LDO ----
    # SOT-223: 1=GND/Adj, 2=VOUT, 3=VIN, 4=VOUT (tab)
    ams_left  = [("ADJ_GND","1"),("VIN","3")]
    ams_right = [("VOUT","2"),("VOUT_TAB","4")]
    parts.append(ic_symbol("custom:AMS1117", 12.7, 7.62, ams_left, ams_right))

    # ---- custom:ESP32 (WROOM-32E, 38 pins) ----
    esp_left = [
        ("GND1","1"),  ("3V3","2"),     ("EN","3"),    ("SENSOR_VP","4"),
        ("SENSOR_VN","5"), ("IO34","6"), ("IO35","7"), ("IO32","8"),
        ("IO33","9"),  ("IO25","10"),   ("IO26","11"), ("IO27","12"),
        ("IO14","13"), ("IO12","14"),   ("GND2","15"), ("IO13","16"),
        ("SD2","17"),  ("SD3","18"),    ("CMD","19"),
    ]
    esp_right = [
        ("GND3","38"), ("IO23","37"),   ("IO22","36"), ("TXD0","35"),
        ("RXD0","34"), ("IO21","33"),   ("NC1","32"),  ("IO19","31"),
        ("IO18","30"), ("IO5","29"),    ("IO17","28"), ("IO16","27"),
        ("IO4","26"),  ("IO0","25"),    ("IO2","24"),  ("IO15","23"),
        ("SD1","22"),  ("SD0","21"),    ("CLK","20"),
    ]
    parts.append(ic_symbol("custom:ESP32", 30.48, 53.34, esp_left, esp_right))

    # ---- custom:BH1750 (5 pins on package, 5L 0R for clarity) ----
    bh_left  = [("VCC","1"),("ADDR","2"),("GND","3"),("SCL","4"),("SDA","5")]
    bh_right = [("DVI","6")]
    parts.append(ic_symbol("custom:BH1750", 10.16, 15.24, bh_left, bh_right))

    # ---- custom:UART_Header (6 pin programming header) ----
    hdr_left  = [("3V3","1"),("GND","2"),("TXD","3")]
    hdr_right = [("RXD","4"),("EN","5"),("BOOT","6")]
    parts.append(ic_symbol("custom:UART_HDR", 10.16, 10.16, hdr_left, hdr_right))

    inner = "\n".join(parts)
    return f"  (lib_symbols\n{inner}\n  )"


# ===========================================================================
# Main schematic generator
# ===========================================================================

def generate_schematic():
    els = []

    # -----------------------------------------------------------------------
    # Section boundary boxes (A2 sheet ~ 594 x 420 mm)
    # -----------------------------------------------------------------------
    els.extend(section_box("1 - USB-C Input + Protection", 10, 10, 200, 130))
    els.extend(section_box("2 - 3V3 LDO Power Tree",       10, 135, 200, 240))
    els.extend(section_box("3 - ESP32-WROOM-32E + Strapping",
                           210, 10, 430, 320))
    els.extend(section_box("4 - UART Programming Header",  10, 245, 200, 320))
    els.extend(section_box("5 - BH1750FVI I2C Sensor",     440, 10, 580, 200))

    els.append(txt("ESP32-WROOM-32E + BH1750FVI Reference Design  Rev 1.0",
                   295, 5, 2.0, bold=True))

    # =======================================================================
    # SECTION 1 - USB-C Input + Protection
    # =======================================================================
    # USB-C connector at left edge
    usbc_lp = [("VBUS","1"),("GND","2"),("CC1","3")]
    usbc_rp = [("CC2","4"),("DP","5"),("DM","6")]
    usbc_e, usbc_pins = place_ic("custom:USB_C", "J1", "USB-C",
                                  35, 50, usbc_lp, usbc_rp,
                                  body_w=12.7, body_h=10.16)
    els.append(usbc_e)
    # VBUS label (raw 5V from USB before fuse)
    els.append(netlabel("VBUS_RAW", usbc_pins["VBUS"][0],
                        usbc_pins["VBUS"][1], angle=180))
    els.append(glabel("GND", usbc_pins["GND"][0],
                      usbc_pins["GND"][1], shape="input", angle=180))

    # CC1 / CC2 5.1k pull-down resistors to GND (UFP detection)
    cc1_e, cc1_p1, cc1_p2 = place_res("R1", "5.1k",
                                       snap(usbc_pins["CC1"][0] - 7),
                                       snap(usbc_pins["CC1"][1] + 10))
    els.append(cc1_e)
    els.append(wire(usbc_pins["CC1"][0], usbc_pins["CC1"][1],
                    cc1_p1[0], cc1_p1[1]))
    els.append(glabel("GND", cc1_p2[0], cc1_p2[1], shape="input", angle=270))

    cc2_e, cc2_p1, cc2_p2 = place_res("R2", "5.1k",
                                       snap(usbc_pins["CC2"][0] + 7),
                                       snap(usbc_pins["CC2"][1] + 10))
    els.append(cc2_e)
    els.append(wire(usbc_pins["CC2"][0], usbc_pins["CC2"][1],
                    cc2_p1[0], cc2_p1[1]))
    els.append(glabel("GND", cc2_p2[0], cc2_p2[1], shape="input", angle=270))

    # D+ / D- net labels for USBLC6 routing
    els.append(netlabel("USB_DP", usbc_pins["DP"][0],
                        usbc_pins["DP"][1], angle=0))
    els.append(netlabel("USB_DM", usbc_pins["DM"][0],
                        usbc_pins["DM"][1], angle=0))

    # Polyfuse on VBUS (500mA hold, 1A trip)
    pf_e, pf_p1, pf_p2 = place_polyfuse("F1", "MF-MSMF050-2",
                                         70, 38)
    els.append(pf_e)
    els.append(netlabel("VBUS_RAW", pf_p1[0], pf_p1[1], angle=180))
    els.append(netlabel("VBUS_FUSED", pf_p2[0], pf_p2[1], angle=0))

    # TVS diode on VBUS_FUSED to GND (SMAJ5.0CA)
    tvs_e, tvs_pa, tvs_pk = place_diode("D1", "SMAJ5.0CA", 90, 50)
    els.append(tvs_e)
    els.append(netlabel("VBUS_FUSED", tvs_pa[0], tvs_pa[1], angle=180))
    # Cathode of bidir TVS goes to GND
    els.append(glabel("GND", tvs_pk[0], tvs_pk[1], shape="input", angle=0))

    # USBLC6 ESD on D+/D-/VBUS
    usblc_lp = [("IO1","1"),("GND","2"),("IO2","3")]
    usblc_rp = [("IO2p","4"),("VBUS","5"),("IO1p","6")]
    usblc_e, usblc_pins = place_ic("custom:USBLC6", "U1", "USBLC6-2SC6",
                                    130, 60, usblc_lp, usblc_rp,
                                    body_w=10.16, body_h=7.62)
    els.append(usblc_e)
    els.append(netlabel("USB_DM", usblc_pins["IO1"][0],
                        usblc_pins["IO1"][1], angle=180))
    els.append(glabel("GND", usblc_pins["GND"][0],
                      usblc_pins["GND"][1], shape="input", angle=180))
    els.append(netlabel("USB_DP", usblc_pins["IO2"][0],
                        usblc_pins["IO2"][1], angle=180))
    els.append(netlabel("USB_DP_FILT", usblc_pins["IO2p"][0],
                        usblc_pins["IO2p"][1], angle=0))
    els.append(netlabel("VBUS_FUSED", usblc_pins["VBUS"][0],
                        usblc_pins["VBUS"][1], angle=0))
    els.append(netlabel("USB_DM_FILT", usblc_pins["IO1p"][0],
                        usblc_pins["IO1p"][1], angle=0))

    # Reverse polarity P-MOSFET (high-side, S=VBUS_FUSED, D=VBUS_PROT, G=GND)
    # AO3401A
    pmos_e, pm_g, pm_d, pm_s = place_pmos("Q1", "AO3401A", 165, 50)
    els.append(pmos_e)
    els.append(netlabel("VBUS_FUSED", pm_s[0], pm_s[1], angle=270))
    els.append(netlabel("VBUS_PROT", pm_d[0], pm_d[1], angle=90))
    els.append(glabel("GND", pm_g[0], pm_g[1], shape="input", angle=180))
    # Gate pull-up to VBUS_FUSED (10k, holds FET off if VBUS missing)
    rg_e, rg_p1, rg_p2 = place_res("R3", "10k",
                                    snap(pm_g[0] + 5),
                                    snap(pm_g[1] - 10))
    els.append(rg_e)
    els.append(wire(pm_g[0], pm_g[1], pm_g[0] + 5.08, pm_g[1]))
    els.append(wire(pm_g[0] + 5.08, pm_g[1], rg_p2[0], rg_p2[1]))
    els.append(netlabel("VBUS_FUSED", rg_p1[0], rg_p1[1], angle=90))

    # Bulk cap on VBUS_PROT (4.7uF X5R)
    decouple("C1", "4.7uF", 185, 75, "VBUS_PROT", els)

    # Power indicator LED on VBUS_PROT via 1k
    led_x, led_y = 185, 105
    led_e, led_p1, led_p2 = place_res("R4", "1k", led_x, led_y)
    els.append(led_e)
    els.append(netlabel("VBUS_PROT", led_p1[0], led_p1[1], angle=90))
    pwr_d_e, pwr_da, pwr_dk = place_diode("D2", "LED_GRN",
                                           snap(led_x), snap(led_y + 10))
    els.append(pwr_d_e)
    els.append(wire(led_p2[0], led_p2[1], pwr_da[0], pwr_da[1]))
    els.append(glabel("GND", pwr_dk[0], pwr_dk[1], shape="input", angle=0))

    # =======================================================================
    # SECTION 2 - 3V3 LDO Power Tree
    # =======================================================================
    # AMS1117-3.3 SOT-223
    ams_lp = [("ADJ_GND","1"),("VIN","3")]
    ams_rp = [("VOUT","2"),("VOUT_TAB","4")]
    ams_e, ams_pins = place_ic("custom:AMS1117", "U2", "AMS1117-3.3",
                                70, 175, ams_lp, ams_rp,
                                body_w=12.7, body_h=7.62)
    els.append(ams_e)
    els.append(netlabel("VBUS_PROT", ams_pins["VIN"][0],
                        ams_pins["VIN"][1], angle=180))
    els.append(glabel("GND", ams_pins["ADJ_GND"][0],
                      ams_pins["ADJ_GND"][1], shape="input", angle=180))
    els.append(netlabel("3V3_LDO", ams_pins["VOUT"][0],
                        ams_pins["VOUT"][1], angle=0))
    # Tab pin - tied to VOUT internally, just bring it out to VOUT net
    els.append(netlabel("3V3_LDO", ams_pins["VOUT_TAB"][0],
                        ams_pins["VOUT_TAB"][1], angle=0))

    # Input bulk: 10uF
    decouple("C2", "10uF",
             snap(ams_pins["VIN"][0] - 12),
             snap(ams_pins["VIN"][1] + 8),
             "VBUS_PROT", els)
    # Input ceramic: 100nF
    decouple("C3", "100nF",
             snap(ams_pins["VIN"][0] - 22),
             snap(ams_pins["VIN"][1] + 8),
             "VBUS_PROT", els)
    # Output bulk: 22uF (AMS1117 needs >=22uF tantalum or low-ESR ceramic)
    decouple("C4", "22uF",
             snap(ams_pins["VOUT"][0] + 12),
             snap(ams_pins["VOUT"][1] + 8),
             "3V3_LDO", els)
    # Output ceramic: 100nF
    decouple("C5", "100nF",
             snap(ams_pins["VOUT"][0] + 22),
             snap(ams_pins["VOUT"][1] + 8),
             "3V3_LDO", els)

    # Ferrite bead from 3V3_LDO -> 3V3 (clean rail to ESP32 VDD33)
    fb_e, fb_p1, fb_p2 = place_ferrite("FB1", "BLM18PG121SN1D 120R",
                                        130, 200)
    els.append(fb_e)
    els.append(netlabel("3V3_LDO", fb_p1[0], fb_p1[1], angle=90))
    els.append(glabel("3V3", fb_p2[0], fb_p2[1], shape="bidirectional", angle=270))

    # Bulk + bypass on the clean side: 1uF + 100nF + 10nF
    decouple("C6", "1uF",   150, 215, "3V3", els)
    decouple("C7", "100nF", 165, 215, "3V3", els)
    decouple("C8", "10nF",  180, 215, "3V3", els)

    # =======================================================================
    # SECTION 3 - ESP32-WROOM-32E + Strapping
    # =======================================================================
    # 19 pins per side. body 30.48 x 53.34, half = 15.24 x 26.67
    esp_cx, esp_cy = 320, 165
    esp_lp = [
        ("GND1","1"),  ("3V3","2"),     ("EN","3"),    ("SENSOR_VP","4"),
        ("SENSOR_VN","5"), ("IO34","6"), ("IO35","7"), ("IO32","8"),
        ("IO33","9"),  ("IO25","10"),   ("IO26","11"), ("IO27","12"),
        ("IO14","13"), ("IO12","14"),   ("GND2","15"), ("IO13","16"),
        ("SD2","17"),  ("SD3","18"),    ("CMD","19"),
    ]
    esp_rp = [
        ("GND3","38"), ("IO23","37"),   ("IO22","36"), ("TXD0","35"),
        ("RXD0","34"), ("IO21","33"),   ("NC1","32"),  ("IO19","31"),
        ("IO18","30"), ("IO5","29"),    ("IO17","28"), ("IO16","27"),
        ("IO4","26"),  ("IO0","25"),    ("IO2","24"),  ("IO15","23"),
        ("SD1","22"),  ("SD0","21"),    ("CLK","20"),
    ]
    esp_e, esp_pins = place_ic("custom:ESP32", "U3", "ESP32-WROOM-32E",
                                esp_cx, esp_cy, esp_lp, esp_rp,
                                body_w=30.48, body_h=53.34)
    els.append(esp_e)

    # Power: pin 2 (3V3) and pin 38 (GND3) - all GND pins to GND
    els.append(glabel("3V3", esp_pins["3V3"][0], esp_pins["3V3"][1],
                      shape="bidirectional", angle=180))
    for g in ("GND1", "GND2", "GND3"):
        els.append(glabel("GND", esp_pins[g][0], esp_pins[g][1],
                          shape="input", angle=180 if g != "GND3" else 0))

    # Module-pin decoupling: 100nF + 1uF right next to pin 2
    decouple("C9",  "100nF",
             snap(esp_pins["3V3"][0] - 10),
             snap(esp_pins["3V3"][1] - 10),
             "3V3", els)
    decouple("C10", "1uF",
             snap(esp_pins["3V3"][0] - 20),
             snap(esp_pins["3V3"][1] - 10),
             "3V3", els)

    # ----- EN pin: 10k pull-up + 100nF to GND + RESET button -----
    en_x, en_y = esp_pins["EN"]
    en_pu_e, en_pu_p1, en_pu_p2 = place_res("R5", "10k",
                                              snap(en_x - 12),
                                              snap(en_y - 10))
    els.append(en_pu_e)
    els.append(glabel("3V3", en_pu_p1[0], en_pu_p1[1],
                      shape="bidirectional", angle=90))
    els.append(wire(en_pu_p2[0], en_pu_p2[1], en_pu_p2[0], en_y))
    els.append(wire(en_pu_p2[0], en_y, en_x, en_y))

    en_cap_e, en_cap_p1, en_cap_p2 = place_cap("C11", "100nF",
                                                 snap(en_x - 12),
                                                 snap(en_y + 10))
    els.append(en_cap_e)
    els.append(wire(en_cap_p1[0], en_cap_p1[1], en_cap_p1[0], en_y))
    els.append(wire(en_cap_p1[0], en_y, en_x, en_y))
    els.append(glabel("GND", en_cap_p2[0], en_cap_p2[1],
                      shape="input", angle=270))
    els.append(netlabel("EN_NET", en_x - 5, en_y, angle=180))

    # RESET tactile button: EN_NET to GND
    sw_rst_e, sw_rst_p1, sw_rst_p2 = place_switch("SW1", "RESET",
                                                    snap(en_x - 30), en_y)
    els.append(sw_rst_e)
    els.append(netlabel("EN_NET", sw_rst_p2[0], sw_rst_p2[1], angle=0))
    els.append(glabel("GND", sw_rst_p1[0], sw_rst_p1[1],
                      shape="input", angle=180))

    # ----- IO0 strapping: 10k pull-up to 3V3 + BOOT button to GND -----
    io0_x, io0_y = esp_pins["IO0"]
    io0_pu_e, io0_pu_p1, io0_pu_p2 = place_res("R6", "10k",
                                                 snap(io0_x + 15),
                                                 snap(io0_y - 10))
    els.append(io0_pu_e)
    els.append(glabel("3V3", io0_pu_p1[0], io0_pu_p1[1],
                      shape="bidirectional", angle=90))
    els.append(wire(io0_pu_p2[0], io0_pu_p2[1], io0_pu_p2[0], io0_y))
    els.append(wire(io0_pu_p2[0], io0_y, io0_x, io0_y))
    els.append(netlabel("IO0_BOOT", io0_x + 5, io0_y, angle=0))

    sw_boot_e, sw_boot_p1, sw_boot_p2 = place_switch("SW2", "BOOT",
                                                       snap(io0_x + 30), io0_y)
    els.append(sw_boot_e)
    els.append(netlabel("IO0_BOOT", sw_boot_p1[0], sw_boot_p1[1], angle=180))
    els.append(glabel("GND", sw_boot_p2[0], sw_boot_p2[1],
                      shape="input", angle=0))

    # ----- IO2 strapping: 10k pull-down to GND -----
    io2_x, io2_y = esp_pins["IO2"]
    io2_pd_e, io2_pd_p1, io2_pd_p2 = place_res("R7", "10k",
                                                 snap(io2_x + 15),
                                                 snap(io2_y + 10))
    els.append(io2_pd_e)
    els.append(wire(io2_x, io2_y, io2_pd_p1[0], io2_y))
    els.append(wire(io2_pd_p1[0], io2_y, io2_pd_p1[0], io2_pd_p1[1]))
    els.append(glabel("GND", io2_pd_p2[0], io2_pd_p2[1],
                      shape="input", angle=270))

    # ----- IO15 strapping: 10k pull-up to 3V3 (silent boot) -----
    io15_x, io15_y = esp_pins["IO15"]
    io15_pu_e, io15_pu_p1, io15_pu_p2 = place_res("R8", "10k",
                                                    snap(io15_x + 15),
                                                    snap(io15_y - 10))
    els.append(io15_pu_e)
    els.append(glabel("3V3", io15_pu_p1[0], io15_pu_p1[1],
                      shape="bidirectional", angle=90))
    els.append(wire(io15_pu_p2[0], io15_pu_p2[1], io15_pu_p2[0], io15_y))
    els.append(wire(io15_pu_p2[0], io15_y, io15_x, io15_y))

    # ----- I2C nets out of ESP32 -----
    sda_x, sda_y = esp_pins["IO21"]
    scl_x, scl_y = esp_pins["IO22"]
    els.append(netlabel("I2C_SDA", sda_x + 5, sda_y, angle=0))
    els.append(wire(sda_x, sda_y, sda_x + 5.08, sda_y))
    els.append(netlabel("I2C_SCL", scl_x + 5, scl_y, angle=0))
    els.append(wire(scl_x, scl_y, scl_x + 5.08, scl_y))

    # ----- UART out of ESP32 to programming header -----
    txd_x, txd_y = esp_pins["TXD0"]
    rxd_x, rxd_y = esp_pins["RXD0"]
    els.append(netlabel("UART_TXD", txd_x + 5, txd_y, angle=0))
    els.append(wire(txd_x, txd_y, txd_x + 5.08, txd_y))
    els.append(netlabel("UART_RXD", rxd_x + 5, rxd_y, angle=0))
    els.append(wire(rxd_x, rxd_y, rxd_x + 5.08, rxd_y))

    # =======================================================================
    # SECTION 4 - UART Programming Header
    # =======================================================================
    hdr_lp = [("3V3","1"),("GND","2"),("TXD","3")]
    hdr_rp = [("RXD","4"),("EN","5"),("BOOT","6")]
    hdr_e, hdr_pins = place_ic("custom:UART_HDR", "J2",
                                "UART 6-pin 2.54mm",
                                75, 280, hdr_lp, hdr_rp,
                                body_w=10.16, body_h=10.16)
    els.append(hdr_e)
    els.append(glabel("3V3", hdr_pins["3V3"][0], hdr_pins["3V3"][1],
                      shape="bidirectional", angle=180))
    els.append(glabel("GND", hdr_pins["GND"][0], hdr_pins["GND"][1],
                      shape="input", angle=180))
    els.append(netlabel("UART_RXD", hdr_pins["TXD"][0],
                        hdr_pins["TXD"][1], angle=180))
    els.append(netlabel("UART_TXD", hdr_pins["RXD"][0],
                        hdr_pins["RXD"][1], angle=0))
    els.append(netlabel("EN_NET", hdr_pins["EN"][0],
                        hdr_pins["EN"][1], angle=0))
    els.append(netlabel("IO0_BOOT", hdr_pins["BOOT"][0],
                        hdr_pins["BOOT"][1], angle=0))
    els.append(txt("Note: TXD pin on header drives RXD0 of MCU and vice versa.",
                   30, 305, 1.0))

    # =======================================================================
    # SECTION 5 - BH1750FVI I2C Sensor
    # =======================================================================
    bh_lp = [("VCC","1"),("ADDR","2"),("GND","3"),("SCL","4"),("SDA","5")]
    bh_rp = [("DVI","6")]
    bh_e, bh_pins = place_ic("custom:BH1750", "U4", "BH1750FVI-TR",
                              490, 50, bh_lp, bh_rp,
                              body_w=10.16, body_h=15.24)
    els.append(bh_e)
    els.append(glabel("3V3", bh_pins["VCC"][0], bh_pins["VCC"][1],
                      shape="bidirectional", angle=180))
    els.append(glabel("GND", bh_pins["GND"][0], bh_pins["GND"][1],
                      shape="input", angle=180))
    # ADDR pin tied to GND -> address 0x23
    els.append(glabel("GND", bh_pins["ADDR"][0], bh_pins["ADDR"][1],
                      shape="input", angle=180))
    # DVI tied to VCC (per BH1750 datasheet, internal LDO supply pin)
    els.append(glabel("3V3", bh_pins["DVI"][0], bh_pins["DVI"][1],
                      shape="bidirectional", angle=0))
    # SDA / SCL net labels - these connect to the I2C bus
    els.append(netlabel("I2C_SDA", bh_pins["SDA"][0],
                        bh_pins["SDA"][1], angle=180))
    els.append(netlabel("I2C_SCL", bh_pins["SCL"][0],
                        bh_pins["SCL"][1], angle=180))

    # Bypass on VCC: 100nF + 1uF
    decouple("C12", "100nF",
             snap(bh_pins["VCC"][0] + 22),
             snap(bh_pins["VCC"][1] + 8),
             "3V3", els)
    decouple("C13", "1uF",
             snap(bh_pins["VCC"][0] + 32),
             snap(bh_pins["VCC"][1] + 8),
             "3V3", els)

    # I2C pull-ups: 4.7k each on SDA/SCL to 3V3
    pu_sda_e, pu_sda_p1, pu_sda_p2 = place_res("R9", "4.7k", 470, 130)
    els.append(pu_sda_e)
    els.append(glabel("3V3", pu_sda_p1[0], pu_sda_p1[1],
                      shape="bidirectional", angle=90))
    els.append(netlabel("I2C_SDA", pu_sda_p2[0], pu_sda_p2[1], angle=270))

    pu_scl_e, pu_scl_p1, pu_scl_p2 = place_res("R10", "4.7k", 485, 130)
    els.append(pu_scl_e)
    els.append(glabel("3V3", pu_scl_p1[0], pu_scl_p1[1],
                      shape="bidirectional", angle=90))
    els.append(netlabel("I2C_SCL", pu_scl_p2[0], pu_scl_p2[1], angle=270))

    # Optional DNP series RC EMI filter on SDA/SCL (R 100R + C 10nF)
    rsda_dnp_e, rsda_dnp_p1, rsda_dnp_p2 = place_res(
        "R11", "100R DNP", 510, 155)
    els.append(rsda_dnp_e)
    els.append(netlabel("I2C_SDA", rsda_dnp_p1[0], rsda_dnp_p1[1], angle=90))
    els.append(netlabel("I2C_SDA_F", rsda_dnp_p2[0], rsda_dnp_p2[1], angle=270))
    csda_dnp_e, csda_dnp_p1, csda_dnp_p2 = place_cap(
        "C14", "10nF DNP", 510, 175)
    els.append(csda_dnp_e)
    els.append(netlabel("I2C_SDA_F", csda_dnp_p1[0], csda_dnp_p1[1], angle=90))
    els.append(glabel("GND", csda_dnp_p2[0], csda_dnp_p2[1],
                      shape="input", angle=270))

    rscl_dnp_e, rscl_dnp_p1, rscl_dnp_p2 = place_res(
        "R12", "100R DNP", 530, 155)
    els.append(rscl_dnp_e)
    els.append(netlabel("I2C_SCL", rscl_dnp_p1[0], rscl_dnp_p1[1], angle=90))
    els.append(netlabel("I2C_SCL_F", rscl_dnp_p2[0], rscl_dnp_p2[1], angle=270))
    cscl_dnp_e, cscl_dnp_p1, cscl_dnp_p2 = place_cap(
        "C15", "10nF DNP", 530, 175)
    els.append(cscl_dnp_e)
    els.append(netlabel("I2C_SCL_F", cscl_dnp_p1[0], cscl_dnp_p1[1], angle=90))
    els.append(glabel("GND", cscl_dnp_p2[0], cscl_dnp_p2[1],
                      shape="input", angle=270))

    els.append(txt("R11/C14, R12/C15: DNP series-RC EMI filter.",
                   447, 195, 1.0))

    # =======================================================================
    # Assemble schematic
    # =======================================================================
    lib_sym = build_lib_symbols()

    header = f"""(kicad_sch
  (version 20231120)
  (generator "python_esp32_light_sensor")
  (generator_version "8.0")
  (uuid "{uid()}")
  (paper "A2")

  (title_block
    (title "ESP32-WROOM-32E + BH1750FVI Reference Design")
    (date "2026-05-16")
    (rev "1.0")
    (comment 1 "Production-grade USB-C powered ambient light sensor board")
    (comment 2 "Ferrite-isolated 3V3 rail, full ESD/TVS/reverse-polarity protection")
    (comment 3 "Strapping pins set per Espressif HW Design Guidelines")
    (comment 4 "Sub-symbol names in lib_symbols intentionally omit custom: prefix")
  )

{lib_sym}

"""
    footer = "\n)\n"
    body = "\n".join(els)
    return header + body + footer


def main():
    out_dir = "/Users/siddhantsaboo/Desktop/agentic workflows/urine_dipstick_cad/reference_designs/esp32_light_sensor"
    out_file = os.path.join(out_dir, "esp32_light_sensor.kicad_sch")
    os.makedirs(out_dir, exist_ok=True)

    sch = generate_schematic()
    with open(out_file, "w") as f:
        f.write(sch)

    lines = sch.count("\n")
    symbols = sch.count("(lib_id")
    wires = sch.count("(wire")
    labels = sch.count("(label ")
    glabels = sch.count("(global_label")
    print(f"Written: {out_file}")
    print(f"  Lines:            {lines:,}")
    print(f"  Symbol instances: {symbols}")
    print(f"  Wires:            {wires}")
    print(f"  Net labels:       {labels}")
    print(f"  Global labels:    {glabels}")
    print(f"  File size:        {os.path.getsize(out_file):,} bytes")


if __name__ == "__main__":
    main()
