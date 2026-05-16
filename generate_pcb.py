#!/usr/bin/env python3
"""
generate_pcb.py — Generate a minimal but valid KiCad 10 PCB file for the
Urine Dipstick Analyzer power-distribution board (PCB1).

The board is 50 x 30 mm, 2-layer FR4. Footprints are placed in a clean grid
on the top side. Routing is intentionally LEFT TO THE USER — only the board
outline, footprints, mounting holes, and a GND zone fill on both copper
layers are emitted. KiCad will load the file and let the user run
DRC + interactive routing on the small handful of nets.

Output: urine_dipstick_analyzer.kicad_pcb
"""
from __future__ import annotations
import os
import time
import uuid
from pathlib import Path

OUT = Path(__file__).parent / "urine_dipstick_analyzer.kicad_pcb"

# Board geometry (mm). KiCad origin at top-left of board outline.
BW, BH = 50.0, 30.0

# Standard nets used in the design.
NETS = [
    "",          # 0 — unconnected (always net 0)
    "GND",
    "VBAT",
    "VBUS",
    "+3V3",
    "+5V",
    "+9V",
    "VMOT",
    "SDA",
    "SCL",
    "CHRG_STAT",
    "PG",
    "MOTOR_PWR",
]

def uid() -> str:
    return str(uuid.uuid4())

def header() -> str:
    return f"""(kicad_pcb
\t(version 20240108)
\t(generator "generate_pcb.py")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(31 "B.Cu" signal)
\t\t(32 "B.Adhes" user "B.Adhesive")
\t\t(33 "F.Adhes" user "F.Adhesive")
\t\t(34 "B.Paste" user)
\t\t(35 "F.Paste" user)
\t\t(36 "B.SilkS" user "B.Silkscreen")
\t\t(37 "F.SilkS" user "F.Silkscreen")
\t\t(38 "B.Mask" user)
\t\t(39 "F.Mask" user)
\t\t(40 "Dwgs.User" user "User.Drawings")
\t\t(41 "Cmts.User" user "User.Comments")
\t\t(42 "Eco1.User" user "User.Eco1")
\t\t(43 "Eco2.User" user "User.Eco2")
\t\t(44 "Edge.Cuts" user)
\t\t(45 "Margin" user)
\t\t(46 "B.CrtYd" user "B.Courtyard")
\t\t(47 "F.CrtYd" user "F.Courtyard")
\t\t(48 "B.Fab" user)
\t\t(49 "F.Fab" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(tenting front back)
\t\t(pcbplotparams
\t\t\t(layerselection 0x00010fc_ffffffff)
\t\t\t(plot_on_all_layers_selection 0x0000000_00000000)
\t\t\t(disableapertmacros no)
\t\t\t(usegerberextensions no)
\t\t\t(usegerberattributes yes)
\t\t\t(usegerberadvancedattributes yes)
\t\t\t(creategerberjobfile yes)
\t\t\t(dashed_line_dash_ratio 12.000000)
\t\t\t(dashed_line_gap_ratio 3.000000)
\t\t\t(svgprecision 4)
\t\t\t(plotframeref no)
\t\t\t(viasonmask no)
\t\t\t(mode 1)
\t\t\t(useauxorigin no)
\t\t\t(hpglpennumber 1)
\t\t\t(hpglpenspeed 20)
\t\t\t(hpglpendiameter 15.000000)
\t\t\t(pdf_front_fp_property_popups yes)
\t\t\t(pdf_back_fp_property_popups yes)
\t\t\t(dxfpolygonmode yes)
\t\t\t(dxfimperialunits yes)
\t\t\t(dxfusepcbnewfont yes)
\t\t\t(psnegative no)
\t\t\t(psa4output no)
\t\t\t(plotreference yes)
\t\t\t(plotvalue yes)
\t\t\t(plotfptext yes)
\t\t\t(plotinvisibletext no)
\t\t\t(sketchpadsonfab no)
\t\t\t(subtractmaskfromsilk no)
\t\t\t(outputformat 1)
\t\t\t(mirror no)
\t\t\t(drillshape 1)
\t\t\t(scaleselection 1)
\t\t\t(outputdirectory "gerbers/")
\t\t)
\t)
"""

def nets_block() -> str:
    out = []
    for i, n in enumerate(NETS):
        out.append(f'\t(net {i} "{n}")')
    return "\n".join(out) + "\n"

def board_outline() -> str:
    """Rectangle on Edge.Cuts."""
    pts = [(0, 0), (BW, 0), (BW, BH), (0, BH), (0, 0)]
    seg = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seg.append(f"""\t(gr_line
\t\t(start {x1} {y1})
\t\t(end {x2} {y2})
\t\t(stroke (width 0.1) (type solid))
\t\t(layer "Edge.Cuts")
\t\t(uuid "{uid()}")
\t)""")
    return "\n".join(seg) + "\n"

def mounting_hole(x: float, y: float, ref: str) -> str:
    """M2.5 mounting hole — non-plated, drill 2.7 mm, pad 5.0 mm."""
    return f"""\t(footprint "MountingHole:MountingHole_2.7mm_M2.5"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at {x} {y})
\t\t(property "Reference" "{ref}"
\t\t\t(at 0 -3.5 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "MountingHole"
\t\t\t(at 0 3.5 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(pad "" np_thru_hole circle
\t\t\t(at 0 0)
\t\t\t(size 5 5)
\t\t\t(drill 2.7)
\t\t\t(layers "*.Cu" "*.Mask")
\t\t\t(uuid "{uid()}")
\t\t)
\t)
"""

def fp(library: str, name: str, ref: str, value: str, x: float, y: float,
       rot: float = 0, pads: list[tuple] | None = None) -> str:
    """Generic footprint emitter.

    pads: list of (pad_num, pad_type, shape, dx, dy, sx, sy, drill_or_None, net_idx, net_name)
    pad_type: "smd" or "thru_hole"
    shape: "rect", "roundrect", "oval", "circle"
    """
    pads = pads or []
    pad_strs = []
    for (num, ptype, shape, dx, dy, sx, sy, drill, ni, nn) in pads:
        layers = '"F.Cu" "F.Paste" "F.Mask"' if ptype == "smd" else '"*.Cu" "*.Mask"'
        drill_s = f"(drill {drill})" if drill else ""
        pad_strs.append(f"""\t\t(pad "{num}" {ptype} {shape}
\t\t\t(at {dx} {dy})
\t\t\t(size {sx} {sy})
\t\t\t{drill_s}
\t\t\t(layers {layers})
\t\t\t(net {ni} "{nn}")
\t\t\t(uuid "{uid()}")
\t\t)""")
    pads_block = "\n".join(pad_strs)
    return f"""\t(footprint "{library}:{name}"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at {x} {y} {rot})
\t\t(property "Reference" "{ref}"
\t\t\t(at 0 -2.5 {rot})
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 0.8 0.8) (thickness 0.15)))
\t\t)
\t\t(property "Value" "{value}"
\t\t\t(at 0 2.5 {rot})
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 0.6 0.6) (thickness 0.1)))
\t\t)
{pads_block}
\t)
"""

def cap_0603(ref: str, val: str, x: float, y: float, n1: tuple[int,str], n2: tuple[int,str]) -> str:
    return fp("Capacitor_SMD", "C_0603_1608Metric", ref, val, x, y, 0, [
        ("1", "smd", "roundrect", -0.825, 0, 0.8, 0.95, None, n1[0], n1[1]),
        ("2", "smd", "roundrect",  0.825, 0, 0.8, 0.95, None, n2[0], n2[1]),
    ])

def cap_0805(ref: str, val: str, x: float, y: float, n1: tuple[int,str], n2: tuple[int,str]) -> str:
    return fp("Capacitor_SMD", "C_0805_2012Metric", ref, val, x, y, 0, [
        ("1", "smd", "roundrect", -0.95, 0, 1.025, 1.4, None, n1[0], n1[1]),
        ("2", "smd", "roundrect",  0.95, 0, 1.025, 1.4, None, n2[0], n2[1]),
    ])

def cap_1206(ref: str, val: str, x: float, y: float, n1: tuple[int,str], n2: tuple[int,str]) -> str:
    return fp("Capacitor_SMD", "C_1206_3216Metric", ref, val, x, y, 0, [
        ("1", "smd", "roundrect", -1.475, 0, 1.15, 1.8, None, n1[0], n1[1]),
        ("2", "smd", "roundrect",  1.475, 0, 1.15, 1.8, None, n2[0], n2[1]),
    ])

def res_0603(ref: str, val: str, x: float, y: float, n1: tuple[int,str], n2: tuple[int,str]) -> str:
    return fp("Resistor_SMD", "R_0603_1608Metric", ref, val, x, y, 0, [
        ("1", "smd", "roundrect", -0.825, 0, 0.8, 0.95, None, n1[0], n1[1]),
        ("2", "smd", "roundrect",  0.825, 0, 0.8, 0.95, None, n2[0], n2[1]),
    ])

def fuse_1812(ref: str, val: str, x: float, y: float, n1: tuple[int,str], n2: tuple[int,str]) -> str:
    return fp("Fuse_SMD", "Fuse_1812_4532Metric", ref, val, x, y, 0, [
        ("1", "smd", "roundrect", -2.0, 0, 1.6, 3.4, None, n1[0], n1[1]),
        ("2", "smd", "roundrect",  2.0, 0, 1.6, 3.4, None, n2[0], n2[1]),
    ])

def msop10(ref: str, val: str, x: float, y: float, pinmap: list[tuple[int,str]]) -> str:
    """MSOP-10 0.5mm pitch. pinmap: list of (net_idx, net_name) for pads 1..10."""
    pads = []
    # pads 1..5 left, 6..10 right (CCW from upper-left)
    pitch = 0.5
    y0 = -1.0  # pad 1 sits topmost
    for i in range(5):
        ni, nn = pinmap[i]
        pads.append((str(i+1), "smd", "roundrect", -1.45, y0 + i*pitch, 0.95, 0.3, None, ni, nn))
    for i in range(5):
        ni, nn = pinmap[9-i]
        pads.append((str(10-i), "smd", "roundrect", 1.45, y0 + i*pitch, 0.95, 0.3, None, ni, nn))
    return fp("Package_SO", "MSOP-10_3x3mm_P0.5mm", ref, val, x, y, 0, pads)

def sot23_8(ref: str, val: str, x: float, y: float, pinmap: list[tuple[int,str]]) -> str:
    pads = []
    pitch = 0.65
    y0 = -0.975  # 4 pins, centered
    for i in range(4):
        ni, nn = pinmap[i]
        pads.append((str(i+1), "smd", "roundrect", -1.4, y0 + i*pitch, 0.9, 0.45, None, ni, nn))
    for i in range(4):
        ni, nn = pinmap[7-i]
        pads.append((str(8-i), "smd", "roundrect", 1.4, y0 + i*pitch, 0.9, 0.45, None, ni, nn))
    return fp("Package_TO_SOT_SMD", "SOT-23-8", ref, val, x, y, 0, pads)

def jst_xh_2(ref: str, val: str, x: float, y: float, n1: tuple[int,str], n2: tuple[int,str]) -> str:
    """2-pin JST-XH 2.5mm pitch through-hole."""
    return fp("Connector_JST", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", ref, val, x, y, 0, [
        ("1", "thru_hole", "circle", -1.25, 0, 1.8, 1.8, 1.0, n1[0], n1[1]),
        ("2", "thru_hole", "circle",  1.25, 0, 1.8, 1.8, 1.0, n2[0], n2[1]),
    ])

def usb_c_breakout(ref: str, val: str, x: float, y: float) -> str:
    """16-pin 0.1\" header for USB-C breakout (U1a). Two rows of 8."""
    pads = []
    # Simplified: 2x8 header, only VBUS + GND mapped here; data lines NC.
    # Pads 1,2 = GND ; 3,4 = VBUS ; rest unused on this hub.
    netmap = {
        1: (1, "GND"), 2: (1, "GND"),
        3: (3, "VBUS"), 4: (3, "VBUS"),
    }
    for i in range(8):
        for j in range(2):
            num = i*2 + j + 1
            ni, nn = netmap.get(num, (0, ""))
            pads.append((str(num), "thru_hole", "circle",
                         -8.89 + i*2.54, -1.27 + j*2.54, 1.7, 1.7, 1.0, ni, nn))
    return fp("Connector_PinHeader_2.54mm", "PinHeader_2x08_P2.54mm_Vertical", ref, val, x, y, 0, pads)

def gnd_zone(layer: str) -> str:
    return f"""\t(zone
\t\t(net 1)
\t\t(net_name "GND")
\t\t(layer "{layer}")
\t\t(uuid "{uid()}")
\t\t(name "GND_FILL_{layer}")
\t\t(hatch edge 0.5)
\t\t(connect_pads (clearance 0.25))
\t\t(min_thickness 0.25)
\t\t(filled_areas_thickness no)
\t\t(fill yes
\t\t\t(thermal_gap 0.5)
\t\t\t(thermal_bridge_width 0.5)
\t\t)
\t\t(polygon
\t\t\t(pts
\t\t\t\t(xy 0 0) (xy {BW} 0) (xy {BW} {BH}) (xy 0 {BH})
\t\t\t)
\t\t)
\t)
"""

def silk_text(text: str, x: float, y: float, size: float = 1.0) -> str:
    return f"""\t(gr_text "{text}"
\t\t(at {x} {y})
\t\t(layer "F.SilkS")
\t\t(uuid "{uid()}")
\t\t(effects (font (size {size} {size}) (thickness 0.15)) (justify left))
\t)
"""

def build() -> str:
    parts = [header()]
    parts.append(nets_block())
    parts.append(board_outline())

    # Title text
    parts.append(silk_text("UDA-PROTO-001 PCB1 Power Hub v1.0", 2, -1.5, 1.0))
    parts.append(silk_text("USB-C", 7, 4.5, 0.8))
    parts.append(silk_text("CHARGER", 22, 4.5, 0.8))
    parts.append(silk_text("FUEL GAUGE", 36, 4.5, 0.8))

    # Mounting holes — four corners with 3mm setback
    parts.append(mounting_hole(3,    3,    "MH1"))
    parts.append(mounting_hole(BW-3, 3,    "MH2"))
    parts.append(mounting_hole(3,    BH-3, "MH3"))
    parts.append(mounting_hole(BW-3, BH-3, "MH4"))

    GND  = (1, "GND")
    VBAT = (2, "VBAT")
    VBUS = (3, "VBUS")
    V3V3 = (4, "+3V3")
    V5V  = (5, "+5V")
    V9V  = (6, "+9V")
    VMOT = (7, "VMOT")
    SDA  = (8, "SDA")
    SCL  = (9, "SCL")
    CHRG = (10, "CHRG_STAT")
    PG   = (11, "PG")
    MPWR = (12, "MOTOR_PWR")
    NC   = (0, "")

    # USB-C breakout (top edge)
    parts.append(usb_c_breakout("U1a", "USB-C-BO", 8, 8))

    # MCP73833 charger (center).  Pins (datasheet MSOP-10):
    # 1=STAT1, 2=STAT2, 3=PG, 4=Vss, 5=Vbat, 6=Vbat, 7=THERM, 8=PROG, 9=Vss, 10=Vdd
    mcp_pins = [
        CHRG, CHRG, PG, GND, VBAT, VBAT, GND, GND, GND, VBUS,
    ]
    parts.append(msop10("U1", "MCP73833", 22, 12, mcp_pins))

    # MAX17048 fuel gauge SOT-23-8.
    # Pins: 1=CTG, 2=VDD, 3=VSS, 4=SDA, 5=SCL, 6=ALRT, 7=CELL, 8=QSTRT (typical)
    max_pins = [GND, VBAT, GND, SDA, SCL, NC, VBAT, NC]
    parts.append(sot23_8("U4", "MAX17048", 36, 12, max_pins))

    # PTC fuse on VBUS line
    parts.append(fuse_1812("F1", "500mA_PTC", 14, 8, VBUS, VBUS))

    # Bulk caps
    parts.append(cap_0805("CB1", "10uF",  18, 18, VBUS, GND))
    parts.append(cap_0805("CB2", "10uF",  22, 18, VBAT, GND))
    parts.append(cap_0805("CB3", "10uF",  26, 18, V3V3, GND))
    parts.append(cap_0805("CB4", "10uF",  30, 18, V5V,  GND))
    parts.append(cap_1206("CB5", "100uF", 38, 22, VMOT, GND))

    # Decoupling caps (100nF) near each IC
    parts.append(cap_0603("C1", "100nF", 18, 14, VBUS, GND))
    parts.append(cap_0603("C2", "100nF", 26, 14, VBAT, GND))
    parts.append(cap_0603("C3", "100nF", 36, 16, VBAT, GND))
    parts.append(cap_0603("C4", "100nF", 38, 16, V3V3, GND))
    parts.append(cap_0603("C5", "100nF", 14, 18, VBAT, GND))
    parts.append(cap_0603("C6", "100nF", 16, 18, V3V3, GND))
    parts.append(cap_0603("C7", "100nF", 32, 18, V5V,  GND))
    parts.append(cap_0603("C8", "100nF", 34, 18, V9V,  GND))

    # I2C pull-ups
    parts.append(res_0603("R1", "4.7k", 32, 12, SDA, V3V3))
    parts.append(res_0603("R2", "4.7k", 34, 12, SCL, V3V3))

    # JST-XH 2-pin headers along bottom edge
    parts.append(silk_text("BAT",  4,  BH-7, 0.7))
    parts.append(jst_xh_2("J1", "BAT",        6,  BH-4.5, VBAT, GND))
    parts.append(silk_text("9V",  13,  BH-7, 0.7))
    parts.append(jst_xh_2("J2", "9V_OUT",    15,  BH-4.5, V9V,  GND))
    parts.append(silk_text("3V3", 22,  BH-7, 0.7))
    parts.append(jst_xh_2("J3", "3V3_OUT",   24,  BH-4.5, V3V3, GND))
    parts.append(silk_text("I2C", 31,  BH-7, 0.7))
    parts.append(jst_xh_2("J4", "I2C_BUS",   33,  BH-4.5, SDA,  SCL))
    parts.append(silk_text("MOT", 40,  BH-7, 0.7))
    parts.append(jst_xh_2("J5", "MOTOR_PWR", 42,  BH-4.5, VMOT, GND))

    # Ground fills both layers
    parts.append(gnd_zone("F.Cu"))
    parts.append(gnd_zone("B.Cu"))

    parts.append(")\n")
    return "".join(parts)


def main() -> None:
    pcb = build()
    OUT.write_text(pcb)
    print(f"Wrote {OUT} ({len(pcb)} bytes)")


if __name__ == "__main__":
    main()
