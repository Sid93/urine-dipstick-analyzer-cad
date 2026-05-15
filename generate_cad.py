#!/usr/bin/env python3
"""
Urine Dipstick Analyzer — Mechanical Components CAD Generator
Generates STEP and STL files for all mechanical components using CadQuery 2.7.0.
"""

import cadquery as cq
from cadquery import exporters
import os
import math
import traceback

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def save_part(result, name):
    """Export a CadQuery result as both STEP and STL."""
    step_path = os.path.join(OUTPUT_DIR, f"{name}.step")
    stl_path = os.path.join(OUTPUT_DIR, f"{name}.stl")
    exporters.export(result, step_path)
    print(f"  -> {step_path}")
    exporters.export(result, stl_path)
    print(f"  -> {stl_path}")


# ---------------------------------------------------------------------------
# Helper: cylindrical boss (mounting standoff) at a given XY location
# ---------------------------------------------------------------------------
def boss(diameter_outer, diameter_inner, height):
    """Return a single mounting boss workplane-centered."""
    return (
        cq.Workplane("XY")
        .circle(diameter_outer / 2)
        .extrude(height)
        .faces(">Z")
        .circle(diameter_inner / 2)
        .cutBlind(-height)
    )


# ===================================================================
# 1. Molded Enclosure Base
# ===================================================================
def make_enclosure_base():
    print("\n[1/7] Generating enclosure base ...")

    L, W, H = 180.0, 120.0, 40.0
    wall = 2.0
    draft_deg = 2.0
    fillet_outer = 3.0
    fillet_inner = 1.5

    # --- Outer shell (rounded box, then shell to hollow) ---
    # Use a simple box with rounded vertical edges, then shell it
    outer = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(H)
        .edges("|Z")
        .fillet(fillet_outer)
    )

    # Shell it: remove top face, keep walls of given thickness
    base = outer.faces(">Z").shell(-wall)

    # --- Internal ribs (cross pattern) ---
    rib_thickness = 1.5
    rib_height = H - wall - 2  # slightly shorter than cavity

    # Longitudinal center rib
    rib1 = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .center(0, 0)
        .rect(L - 2 * wall - 4, rib_thickness)
        .extrude(rib_height)
    )
    # Transverse rib at ~1/3
    rib2 = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .center(-30, 0)
        .rect(rib_thickness, W - 2 * wall - 4)
        .extrude(rib_height)
    )
    # Transverse rib at ~2/3
    rib3 = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .center(30, 0)
        .rect(rib_thickness, W - 2 * wall - 4)
        .extrude(rib_height)
    )
    base = base.union(rib1).union(rib2).union(rib3)

    # --- Mounting bosses ---
    boss_od = 6.0
    boss_h = 8.0

    # M2.5 bosses for PCBs  (hole=2.5mm)
    pcb_positions = [
        (-60, -40), (-60, -20), (-30, -40), (-30, -20),  # main PCB area
        (50, -40), (50, -20),  # secondary PCB
    ]
    # M3 bosses for stepper motor (hole=3.0mm)
    motor_positions = [(-70, 30), (-70, 45), (-55, 30), (-55, 45)]
    # M3 bosses for fan
    fan_positions = [(60, 35), (60, 50), (75, 35), (75, 50)]

    # M2 bosses for misc: USB-C charger, barcode scanner, UV LED, limit switch,
    # humidity sensor, buzzer, ESP32, ALS sensor
    m2_positions = [
        (70, -45),   # USB-C charger
        (40, 20),    # barcode scanner
        (-20, 45),   # UV LED
        (-75, 0),    # limit switch
        (20, -45),   # humidity sensor
        (0, 45),     # buzzer
        (-40, -45), (-40, -30),  # ESP32
        (10, 30),    # ALS sensor
    ]
    # M3 bosses for heater MOSFET, UV driver MOSFET
    mosfet_positions = [(30, -45), (40, -45)]

    for (x, y) in pcb_positions:
        b = boss(boss_od, 2.5, boss_h).translate((x, y, wall))
        base = base.union(b)
    for (x, y) in motor_positions:
        b = boss(7.0, 3.0, boss_h).translate((x, y, wall))
        base = base.union(b)
    for (x, y) in fan_positions:
        b = boss(7.0, 3.0, boss_h).translate((x, y, wall))
        base = base.union(b)
    for (x, y) in m2_positions:
        b = boss(5.0, 2.0, boss_h).translate((x, y, wall))
        base = base.union(b)
    for (x, y) in mosfet_positions:
        b = boss(7.0, 3.0, boss_h).translate((x, y, wall))
        base = base.union(b)

    # --- Rear panel cutouts ---
    # USB-C port cutout  (9 x 3.5 mm)  on +X face near bottom
    usbc_cut = (
        cq.Workplane("YZ")
        .workplane(offset=L / 2 - wall + 0.1)
        .center(-40, 8)
        .rect(9, 3.5)
        .extrude(-wall - 1)
    )
    base = base.cut(usbc_cut)

    # Ventilation slots on rear (+X face)
    for i in range(6):
        slot = (
            cq.Workplane("YZ")
            .workplane(offset=L / 2 - wall + 0.1)
            .center(10 + i * 6, 25)
            .rect(2, 12)
            .extrude(-wall - 1)
        )
        base = base.cut(slot)

    # --- Bottom rubber feet recesses (4x) ---
    foot_positions = [(-70, -45), (-70, 45), (70, -45), (70, 45)]
    for (x, y) in foot_positions:
        recess = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(5)
            .extrude(-1.5)  # recess into bottom
        )
        base = base.cut(recess)

    # --- Guide rails for dipstick tray (along X-axis center) ---
    rail_w = 3.0
    rail_h = 5.0
    rail_len = 100.0
    for y_off in [-14, 14]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=wall)
            .center(-10, y_off)
            .rect(rail_len, rail_w)
            .extrude(rail_h)
        )
        base = base.union(rail)

    # --- M3 heat-set insert bosses (4x) on top perimeter for cover attachment ---
    cover_boss_positions = [
        (-80, -50), (-80, 50), (80, -50), (80, 50)
    ]
    for (x, y) in cover_boss_positions:
        cb = boss(7.0, 3.0, 10.0).translate((x, y, H - 10))
        base = base.union(cb)

    # Apply a gentle fillet to top edges
    try:
        base = base.edges(">Z").fillet(0.5)
    except Exception:
        pass  # skip if fillet fails on complex geometry

    save_part(base, "im_enclosure_base")
    return base


# ===================================================================
# 2. Enclosure Top Cover
# ===================================================================
def make_enclosure_cover():
    print("\n[2/7] Generating enclosure top cover ...")

    L, W, T = 180.0, 120.0, 5.0
    fillet_r = 3.0

    # Main plate
    cover = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(T)
        .edges("|Z")
        .fillet(fillet_r)
    )

    # --- Gasket groove around perimeter (1mm wide, 0.5mm deep) ---
    gasket_outer = (
        cq.Workplane("XY")
        .rect(L - 4, W - 4)
        .extrude(-0.5)
    )
    gasket_inner = (
        cq.Workplane("XY")
        .rect(L - 6, W - 6)
        .extrude(-0.5)
    )
    gasket_groove = gasket_outer.cut(gasket_inner)
    cover = cover.cut(gasket_groove)

    # --- M3 screw holes (4x) matching base bosses ---
    screw_positions = [(-80, -50), (-80, 50), (80, -50), (80, 50)]
    for (x, y) in screw_positions:
        hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(1.6)  # M3 clearance
            .extrude(T + 1)
        )
        cover = cover.cut(hole)
        # Countersink
        csink = (
            cq.Workplane("XY")
            .workplane(offset=T)
            .center(x, y)
            .circle(3.0)
            .extrude(-2)
        )
        cover = cover.cut(csink)

    # --- Status RGB LED hole (5mm) ---
    led_hole = (
        cq.Workplane("XY")
        .center(70, 0)
        .circle(2.5)
        .extrude(T + 1)
    )
    cover = cover.cut(led_hole)

    # --- OLED display window (27x27mm) ---
    oled_cut = (
        cq.Workplane("XY")
        .center(0, 0)
        .rect(27, 27)
        .extrude(T + 1)
    )
    cover = cover.cut(oled_cut)

    # --- Snap-fit clip slots for vent grill (4 small slots) ---
    for dx in [-12, 12]:
        for dy in [-12, 12]:
            clip_slot = (
                cq.Workplane("XY")
                .center(-70 + dx, 40 + dy)
                .rect(2, 1)
                .extrude(T + 1)
            )
            cover = cover.cut(clip_slot)

    # --- Ventilation slots on one side (-Y edge area) ---
    for i in range(8):
        vent = (
            cq.Workplane("XY")
            .center(-60 + i * 12, -55)
            .rect(8, 2)
            .extrude(T + 1)
        )
        cover = cover.cut(vent)

    # --- UV gasket adhesive bezel area (raised rim around a region) ---
    uv_bezel = (
        cq.Workplane("XY")
        .workplane(offset=T)
        .center(-30, 25)
        .rect(24, 14)
        .extrude(1.0)
    )
    uv_bezel_inner = (
        cq.Workplane("XY")
        .workplane(offset=T)
        .center(-30, 25)
        .rect(20, 10)
        .extrude(1.0)
    )
    uv_bezel_frame = uv_bezel.cut(uv_bezel_inner)
    cover = cover.union(uv_bezel_frame)

    # Top surface fillet
    try:
        cover = cover.edges(">Z").fillet(0.3)
    except Exception:
        pass

    save_part(cover, "enclosure_cover")
    return cover


# ===================================================================
# 3. Dipstick Measurement Tray
# ===================================================================
def make_tray():
    print("\n[3/7] Generating dipstick measurement tray ...")

    L, W, H = 120.0, 25.0, 8.0
    wall = 1.5

    # Main tray body
    tray = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(H)
        .edges("|Z")
        .fillet(1.5)
    )

    # --- Hollow out top (channel for dipstick) ---
    # Leave bottom wall and side walls
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .rect(L - 2 * wall, W - 2 * wall)
        .extrude(H - wall + 0.1)
    )
    tray = tray.cut(cavity)

    # --- Dipstick strip channel/groove (6mm wide, 80mm long, in center floor) ---
    strip_groove = (
        cq.Workplane("XY")
        .workplane(offset=0.5)  # slight depth into floor
        .center(0, 0)
        .rect(80, 6)
        .extrude(-0.8)
    )
    tray = tray.cut(strip_groove)

    # --- Color calibration card recess (20x10mm, one end) ---
    cal_recess = (
        cq.Workplane("XY")
        .workplane(offset=wall - 0.5)
        .center(50, 0)
        .rect(20, 10)
        .extrude(-0.5)
    )
    tray = tray.cut(cal_recess)

    # --- White balance target recess (adjacent to cal card) ---
    wb_recess = (
        cq.Workplane("XY")
        .workplane(offset=wall - 0.5)
        .center(50, -8)
        .rect(10, 5)
        .extrude(-0.3)
    )
    tray = tray.cut(wb_recess)

    # --- Flocking material area (recessed surface in the channel floor) ---
    flock_recess = (
        cq.Workplane("XY")
        .workplane(offset=0.2)
        .center(-10, 0)
        .rect(60, 5)
        .extrude(-0.3)
    )
    tray = tray.cut(flock_recess)

    # --- Bottom: heater film recess (25x50mm) ---
    heater_recess = (
        cq.Workplane("XY")
        .center(0, 0)
        .rect(50, 20)
        .extrude(-0.8)
    )
    tray = tray.cut(heater_recess)

    # --- Bottom: thermistor pocket (small cylindrical cavity) ---
    therm_pocket = (
        cq.Workplane("XY")
        .center(0, 0)
        .circle(1.5)
        .extrude(-1.0)
    )
    tray = tray.cut(therm_pocket)

    # --- T8 copper nut mount hole (centered on one end) ---
    # T8 lead screw nut: ~22mm flange OD, 10.2mm bore, 4x M3 holes
    nut_bore = (
        cq.Workplane("XY")
        .center(-55, 0)
        .circle(5.1)  # nut bore
        .extrude(H)
    )
    tray = tray.cut(nut_bore)
    # Nut flange recess on bottom
    nut_flange = (
        cq.Workplane("XY")
        .center(-55, 0)
        .circle(11)
        .extrude(-1.5)
    )
    tray = tray.cut(nut_flange)
    # M3 nut mounting holes
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        mx = -55 + 8 * math.cos(rad)
        my = 8 * math.sin(rad)
        m3h = (
            cq.Workplane("XY")
            .center(mx, my)
            .circle(1.6)
            .extrude(H)
        )
        tray = tray.cut(m3h)

    # --- Safety interlock magnet pocket (5mm dia, 2mm deep, bottom) ---
    magnet_pocket = (
        cq.Workplane("XY")
        .center(45, 10)
        .circle(2.5)
        .extrude(-2.0)
    )
    tray = tray.cut(magnet_pocket)

    # --- Smooth linear guide surfaces on sides (raised rails) ---
    for y_off in [-W / 2, W / 2 - 1.5]:
        rail = (
            cq.Workplane("XY")
            .center(0, y_off + 0.75)
            .rect(L - 4, 1.5)
            .extrude(H / 2)
        )
        # These are integral to the tray body (already part of walls)
        # Just add a small chamfer channel instead
    # Add guide grooves on sides for the base rails to slide in
    for y_off in [-13.25, 13.25]:
        guide_groove = (
            cq.Workplane("XY")
            .center(0, y_off)
            .rect(L, 3.5)
            .extrude(3)
        )
        tray = tray.cut(guide_groove)

    try:
        tray = tray.edges(">Z").fillet(0.3)
    except Exception:
        pass

    save_part(tray, "im_tray")
    return tray


# ===================================================================
# 4. Camera & LED Mount
# ===================================================================
def make_camera_led_mount():
    print("\n[4/7] Generating camera & LED mount ...")

    L, W, H = 40.0, 30.0, 25.0
    wall = 2.0

    # Main body block
    body = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(H)
        .edges("|Z")
        .fillet(2.0)
    )

    # --- Camera module pocket (OV2640, ~32x32mm cavity on top face) ---
    cam_pocket = (
        cq.Workplane("XY")
        .workplane(offset=H)
        .center(0, 0)
        .rect(32, 25)  # constrained to body width
        .extrude(-8)  # 8mm deep pocket
    )
    body = body.cut(cam_pocket)

    # Camera lens hole through bottom of pocket
    lens_hole = (
        cq.Workplane("XY")
        .workplane(offset=H - 8)
        .center(0, 0)
        .circle(5)
        .extrude(-wall)
    )
    body = body.cut(lens_hole)

    # --- Snap-fit clips for camera (small tabs on pocket walls) ---
    for x_off in [-14, 14]:
        clip = (
            cq.Workplane("XY")
            .workplane(offset=H - 4)
            .center(x_off, 0)
            .rect(1.5, 8)
            .extrude(2)
        )
        body = body.union(clip)

    # --- LED array holder slot (30x10mm) on front face ---
    led_slot = (
        cq.Workplane("XZ")
        .workplane(offset=-W / 2 + 0.1)
        .center(0, H / 2)
        .rect(30, 10)
        .extrude(wall + 1)
    )
    body = body.cut(led_slot)

    # --- 45-degree angled LED illumination surface ---
    # Cut a triangular wedge from front-bottom to create 45deg angle
    wedge = (
        cq.Workplane("YZ")
        .moveTo(-W / 2, 0)
        .lineTo(-W / 2 + 8, 0)
        .lineTo(-W / 2 + 8, 8)
        .close()
        .extrude(30)
        .translate((-15, 0, 0))
    )
    body = body.cut(wedge)

    # --- Diffuser panel press-fit slot (30x20x1mm) ---
    diffuser_slot = (
        cq.Workplane("XY")
        .workplane(offset=H - 10)
        .center(0, 0)
        .rect(32, 22)
        .extrude(-1.2)
    )
    diffuser_inner = (
        cq.Workplane("XY")
        .workplane(offset=H - 10)
        .center(0, 0)
        .rect(30, 20)
        .extrude(-1.2)
    )
    diffuser_channel = diffuser_slot.cut(diffuser_inner)
    # This creates a 1mm wide shelf; instead let's make a slot opening
    diff_cut = (
        cq.Workplane("XZ")
        .workplane(offset=W / 2 - wall + 0.1)
        .center(0, H - 10)
        .rect(32, 1.2)
        .extrude(-wall - 1)
    )
    body = body.cut(diff_cut)

    # --- Quartz glass shield press-fit slot (20x20mm) ---
    # Ledge/shelf for quartz glass to sit on: cut a 22x22 pocket, then
    # leave a 1mm shelf by cutting a deeper 20x20 through-pocket
    quartz_shelf_outer = (
        cq.Workplane("XY")
        .workplane(offset=H - 13.5)
        .center(0, -2)
        .rect(22, 22)
        .extrude(1.5)
    )
    body = body.cut(quartz_shelf_outer)
    quartz_recess = (
        cq.Workplane("XY")
        .workplane(offset=H - 15)
        .center(0, -2)
        .rect(20, 20)
        .extrude(1.5)
    )
    body = body.cut(quartz_recess)

    # --- Cable routing channels on back (+Y face) ---
    for x_off in [-8, 8]:
        cable_ch = (
            cq.Workplane("XZ")
            .workplane(offset=W / 2 - 0.1)
            .center(x_off, H / 2)
            .rect(4, 15)
            .extrude(-3)
        )
        body = body.cut(cable_ch)

    # --- Mounting holes (M2) for attaching to enclosure ---
    for x_off in [-15, 15]:
        mh = (
            cq.Workplane("XY")
            .center(x_off, 10)
            .circle(1.1)
            .extrude(H)
        )
        body = body.cut(mh)

    try:
        body = body.edges("|Z").fillet(0.5)
    except Exception:
        pass

    save_part(body, "camera_led_mount")
    return body


# ===================================================================
# 5. Scanner Mount
# ===================================================================
def make_scanner_mount():
    print("\n[5/7] Generating scanner mount ...")

    L, W, H = 35.0, 25.0, 15.0
    angle_deg = 15.0  # tilt angle

    # Base plate
    base_plate = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(3)
        .edges("|Z")
        .fillet(1.5)
    )

    # Angled cradle for scanner module
    # Build a wedge shape to create the angle
    cradle_h = H - 3
    cradle = (
        cq.Workplane("XY")
        .workplane(offset=3)
        .rect(L, W)
        .extrude(cradle_h)
    )
    # Hollow out the cradle for the GM65 module (~22x20mm)
    cradle_cavity = (
        cq.Workplane("XY")
        .workplane(offset=3 + 2)
        .center(0, 0)
        .rect(22, 20)
        .extrude(cradle_h)
    )
    cradle = cradle.cut(cradle_cavity)

    # Side walls with snap-fit features
    # Add small snap-fit bumps inside the cavity
    for x_off in [-11.5, 11.5]:
        snap = (
            cq.Workplane("XY")
            .workplane(offset=3 + 5)
            .center(x_off, 0)
            .rect(1, 10)
            .extrude(4)
        )
        cradle = cradle.union(snap)
        # Snap ridge
        ridge = (
            cq.Workplane("XY")
            .workplane(offset=3 + 8)
            .center(x_off + (0.5 if x_off > 0 else -0.5), 0)
            .rect(0.5, 8)
            .extrude(1.5)
        )
        cradle = cradle.union(ridge)

    mount = base_plate.union(cradle)

    # Cut a wedge to tilt the scanner cradle back by ~15 degrees
    # Triangular prism cut from the back-top
    tilt_wedge = (
        cq.Workplane("XZ")
        .moveTo(-W / 2, H)
        .lineTo(-W / 2, H - 4)
        .lineTo(-W / 2 + 6, H)
        .close()
        .extrude(L)
        .translate((-L / 2, 0, 0))
    )
    mount = mount.cut(tilt_wedge)

    # --- M2 screw holes (2x) for mounting to enclosure base ---
    for x_off in [-12, 12]:
        mh = (
            cq.Workplane("XY")
            .center(x_off, 0)
            .circle(1.1)
            .extrude(3 + 1)
        )
        mount = mount.cut(mh)

    # --- Cable exit slot on back ---
    cable_slot = (
        cq.Workplane("XZ")
        .workplane(offset=-W / 2 + 0.1)
        .center(0, 6)
        .rect(10, 4)
        .extrude(3)
    )
    mount = mount.cut(cable_slot)

    try:
        mount = mount.edges(">Z").fillet(0.3)
    except Exception:
        pass

    save_part(mount, "scanner_mount")
    return mount


# ===================================================================
# 6. Exhaust Vent Grill
# ===================================================================
def make_vent_grill():
    print("\n[6/7] Generating exhaust vent grill ...")

    L, W, T = 35.0, 35.0, 3.0
    slot_w = 1.0
    slot_spacing = 1.5
    slot_len = 25.0

    # Main plate with slight dome
    # Build as a flat plate first, then we'll add curvature via a cut
    grill = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(T)
        .edges("|Z")
        .fillet(2.0)
    )

    # Add slight dome: create a curved top surface
    # Approximate dome with a spherical cut from below
    dome_sphere = (
        cq.Workplane("XY")
        .workplane(offset=-80)  # center sphere well below
        .sphere(82)  # large sphere, slight curvature at top
    )
    # This would remove material from the flat top creating a dome
    # Actually, let's add material for the dome
    dome_add = (
        cq.Workplane("XY")
        .workplane(offset=T)
        .rect(L - 2, W - 2)
        .extrude(1.0)
    )
    # Simpler: just make a slightly thicker center
    dome_center = (
        cq.Workplane("XY")
        .workplane(offset=T)
        .center(0, 0)
        .rect(L - 8, W - 8)
        .extrude(0.8)
    )
    grill = grill.union(dome_center)

    # --- Slotted grill pattern ---
    n_slots = int((slot_len) / (slot_w + slot_spacing))
    start_x = -(n_slots - 1) * (slot_w + slot_spacing) / 2

    for i in range(n_slots):
        x = start_x + i * (slot_w + slot_spacing)
        slot = (
            cq.Workplane("XY")
            .center(x, 0)
            .rect(slot_w, slot_len)
            .extrude(T + 2)
        )
        grill = grill.cut(slot)

    # --- Snap-fit tabs (4x, one on each side) ---
    tab_positions = [
        (0, -W / 2, 0),      # -Y
        (0, W / 2, 180),     # +Y
        (-L / 2, 0, 90),     # -X
        (L / 2, 0, 270),     # +X
    ]
    for (tx, ty, _rot) in tab_positions:
        # Simple tab protruding downward
        if abs(tx) > abs(ty):  # X-side tab
            tab = (
                cq.Workplane("XY")
                .center(tx, 0)
                .rect(2, 6)
                .extrude(-3)
            )
        else:  # Y-side tab
            tab = (
                cq.Workplane("XY")
                .center(0, ty)
                .rect(6, 2)
                .extrude(-3)
            )
        grill = grill.union(tab)

        # Snap ridge on each tab
        if abs(tx) > abs(ty):
            ridge = (
                cq.Workplane("XY")
                .workplane(offset=-2.5)
                .center(tx + (0.5 if tx > 0 else -0.5), 0)
                .rect(0.5, 5)
                .extrude(1)
            )
        else:
            ridge = (
                cq.Workplane("XY")
                .workplane(offset=-2.5)
                .center(0, ty + (0.5 if ty > 0 else -0.5))
                .rect(5, 0.5)
                .extrude(1)
            )
        grill = grill.union(ridge)

    try:
        grill = grill.edges(">Z").fillet(0.2)
    except Exception:
        pass

    save_part(grill, "vent_grill")
    return grill


# ===================================================================
# 7. Internal Wire/Cable Management Frame
# ===================================================================
def make_internal_wire_frame():
    print("\n[7/7] Generating internal wire/cable management frame ...")

    L, W, H = 160.0, 100.0, 10.0
    frame_w = 6.0  # width of frame members
    channel_w = 5.0
    channel_d = 3.0

    # --- Outer perimeter frame ---
    outer = (
        cq.Workplane("XY")
        .rect(L, W)
        .extrude(H)
    )
    inner = (
        cq.Workplane("XY")
        .rect(L - 2 * frame_w, W - 2 * frame_w)
        .extrude(H)
    )
    frame = outer.cut(inner)

    # --- Cross members ---
    # Longitudinal center beam
    beam1 = (
        cq.Workplane("XY")
        .center(0, 0)
        .rect(L - 2 * frame_w, frame_w)
        .extrude(H)
    )
    frame = frame.union(beam1)

    # Transverse beams
    for x_pos in [-50, 0, 50]:
        beam = (
            cq.Workplane("XY")
            .center(x_pos, 0)
            .rect(frame_w, W - 2 * frame_w)
            .extrude(H)
        )
        frame = frame.union(beam)

    # --- Cable routing channels (grooves in top of frame members) ---
    # Channels along the longitudinal beam
    for y_off in [-2.5, 2.5]:
        ch = (
            cq.Workplane("XY")
            .workplane(offset=H - channel_d)
            .center(0, y_off)
            .rect(L - 2 * frame_w - 4, channel_w)
            .extrude(channel_d + 0.1)
        )
        # Only cut a channel, not through the full beam
        channel_cut = (
            cq.Workplane("XY")
            .workplane(offset=H - channel_d)
            .center(0, y_off + 15)
            .rect(40, channel_w)
            .extrude(channel_d + 0.1)
        )
        frame = frame.cut(channel_cut)

    # Channels along transverse beams
    for x_pos in [-50, 0, 50]:
        ch = (
            cq.Workplane("XY")
            .workplane(offset=H - channel_d)
            .center(x_pos, 25)
            .rect(channel_w, 30)
            .extrude(channel_d + 0.1)
        )
        frame = frame.cut(ch)

    # --- M2.5 standoff mounting holes for PCBs ---
    standoff_positions = [
        (-60, -35), (-60, -15), (-30, -35), (-30, -15),
        (30, -35), (30, -15), (60, -35), (60, -15),
        (-60, 25), (-30, 25), (30, 25), (60, 25),
    ]
    for (x, y) in standoff_positions:
        # Check if position is on a frame member (approximately)
        hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(1.3)  # M2.5 hole
            .extrude(H + 0.1)
        )
        frame = frame.cut(hole)

    # --- Press-fit tabs (protruding downward to snap into base) ---
    tab_positions_pf = [
        (-70, -W / 2 + frame_w / 2),
        (70, -W / 2 + frame_w / 2),
        (-70, W / 2 - frame_w / 2),
        (70, W / 2 - frame_w / 2),
    ]
    for (x, y) in tab_positions_pf:
        tab = (
            cq.Workplane("XY")
            .center(x, y)
            .rect(4, 3)
            .extrude(-4)  # protrude below
        )
        frame = frame.union(tab)

    # --- Large cutouts in panels to allow airflow ---
    # Cut large openings in the areas between cross members
    for x_center in [-25, 25]:
        for y_center in [-25, 25]:
            airflow_cut = (
                cq.Workplane("XY")
                .center(x_center, y_center)
                .rect(35, 30)
                .extrude(H + 0.1)
            )
            frame = frame.cut(airflow_cut)

    try:
        frame = frame.edges("|Z").fillet(0.5)
    except Exception:
        pass

    save_part(frame, "internal_wire_frame")
    return frame


# ===================================================================
# Main
# ===================================================================
def main():
    print("=" * 60)
    print("Urine Dipstick Analyzer - CAD Generation")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"CadQuery version: {cq.__version__}")
    print("=" * 60)

    components = [
        ("Enclosure Base", make_enclosure_base),
        ("Enclosure Cover", make_enclosure_cover),
        ("Dipstick Tray", make_tray),
        ("Camera & LED Mount", make_camera_led_mount),
        ("Scanner Mount", make_scanner_mount),
        ("Vent Grill", make_vent_grill),
        ("Wire Management Frame", make_internal_wire_frame),
    ]

    results = {}
    for name, func in components:
        try:
            results[name] = func()
            print(f"  [OK] {name} generated successfully.")
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            traceback.print_exc()

    print("\n" + "=" * 60)
    ok = sum(1 for v in results.values() if v is not None)
    print(f"Done. {ok}/{len(components)} components generated.")
    print("=" * 60)


if __name__ == "__main__":
    main()
