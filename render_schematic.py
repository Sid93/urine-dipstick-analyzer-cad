#!/usr/bin/env python3
"""Render KiCad .kicad_sch schematic to PNG using matplotlib."""
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import os

SCHEMATIC = os.path.join(os.path.dirname(__file__), "urine_dipstick_analyzer.kicad_sch")
OUTPUT = os.path.join(os.path.dirname(__file__), "schematic_render.png")

def parse_sexpr(text):
    """Minimal S-expression tokenizer."""
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in '(':
            tokens.append('(')
            i += 1
        elif c == ')':
            tokens.append(')')
            i += 1
        elif c == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                if text[j] == '\\': j += 1
                j += 1
            tokens.append(text[i+1:j])
            i = j + 1
        elif c in ' \t\n\r':
            i += 1
        else:
            j = i
            while j < len(text) and text[j] not in '() \t\n\r"':
                j += 1
            tokens.append(text[j - (j-i):j] if j > i else text[i:j])
            tokens.append(text[i:j])
            i = j
    return tokens

def extract_components(text):
    """Extract component instances with position, reference, value."""
    components = []
    # Find top-level (symbol ...) blocks (not inside lib_symbols)
    lib_end = text.find(")\n\n  (symbol")
    if lib_end < 0:
        lib_end = text.find(")\n  (symbol")
    if lib_end < 0:
        lib_end = 0

    work = text[lib_end:]

    pattern = re.compile(
        r'\(symbol\s*\(lib_id\s+"([^"]+)"\)\s*\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)',
        re.DOTALL
    )

    for m in pattern.finditer(work):
        lib_id = m.group(1)
        x, y, angle = float(m.group(2)), float(m.group(3)), float(m.group(4))

        # Find reference and value properties
        block_start = m.start()
        block_text = work[block_start:block_start+2000]

        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block_text)
        val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block_text)

        ref = ref_m.group(1) if ref_m else ""
        val = val_m.group(1) if val_m else lib_id.split(":")[-1]

        components.append({
            'lib_id': lib_id, 'x': x, 'y': y, 'angle': angle,
            'ref': ref, 'value': val
        })

    return components

def extract_wires(text):
    """Extract wire segments."""
    wires = []
    pattern = re.compile(
        r'\(wire\s*\n?\s*\(pts\s*\n?\s*\(xy\s+([-\d.]+)\s+([-\d.]+)\)\s*\(xy\s+([-\d.]+)\s+([-\d.]+)\)',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        wires.append((float(m.group(1)), float(m.group(2)),
                       float(m.group(3)), float(m.group(4))))
    return wires

def extract_labels(text):
    """Extract net labels and global labels."""
    labels = []

    for pat in [
        re.compile(r'\(label\s+"([^"]+)"\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)'),
        re.compile(r'\(global_label\s+"([^"]+)"\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)')
    ]:
        for m in pat.finditer(text):
            labels.append({
                'name': m.group(1),
                'x': float(m.group(2)), 'y': float(m.group(3)),
                'angle': float(m.group(4)),
                'is_global': 'global' in pat.pattern
            })
    return labels

def extract_texts(text):
    """Extract schematic text annotations."""
    texts = []
    pattern = re.compile(
        r'\(text\s+"([^"]+)"\s*\n?\s*\(exclude_from_sim[^)]*\)\s*\n?\s*\(at\s+([-\d.]+)\s+([-\d.]+)\s*([-\d.]*)\)',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        texts.append({
            'text': m.group(1),
            'x': float(m.group(2)), 'y': float(m.group(3))
        })
    return texts

def get_component_color(lib_id):
    """Color-code by component type."""
    lid = lib_id.lower()
    if 'esp32' in lid or 'mcu' in lid or 'microcontroller' in lid:
        return '#4FC3F7'
    if 'regulator' in lid or 'power' in lid or 'battery' in lid or 'charger' in lid:
        return '#FF7043'
    if 'opamp' in lid or 'amplifier' in lid:
        return '#AB47BC'
    if 'led' in lid:
        return '#FFEE58'
    if 'mosfet' in lid or 'nmos' in lid or 'transistor' in lid:
        return '#66BB6A'
    if 'sensor' in lid or 'sht' in lid or 'bh1750' in lid or 'thermistor' in lid:
        return '#26C6DA'
    if 'motor' in lid or 'stepper' in lid:
        return '#FFA726'
    if 'camera' in lid or 'ov2640' in lid:
        return '#7E57C2'
    if 'display' in lid or 'oled' in lid or 'ili9341' in lid or 'tft' in lid:
        return '#42A5F5'
    if 'sd' in lid or 'card' in lid or 'memory' in lid:
        return '#8D6E63'
    if 'switch' in lid or 'button' in lid or 'reed' in lid:
        return '#78909C'
    if 'connector' in lid or 'usb' in lid or 'jack' in lid:
        return '#BDBDBD'
    if 'r' == lid.split(':')[-1].lower() or 'resistor' in lid:
        return '#A5D6A7'
    if 'c' == lid.split(':')[-1].lower() or 'capacitor' in lid:
        return '#90CAF9'
    return '#E0E0E0'

def get_component_size(lib_id):
    """Return (w, h) for component box."""
    lid = lib_id.lower()
    if 'esp32' in lid or 'mcu' in lid:
        return (30, 60)
    if 'opamp' in lid:
        return (12, 10)
    if 'camera' in lid or 'ov2640' in lid:
        return (15, 12)
    if 'motor' in lid or 'stepper' in lid:
        return (12, 10)
    if 'display' in lid or 'oled' in lid or 'ili9341' in lid:
        return (15, 10)
    if 'regulator' in lid or 'charger' in lid:
        return (14, 8)
    if 'mosfet' in lid or 'nmos' in lid:
        return (8, 8)
    if 'scanner' in lid or 'barcode' in lid:
        return (14, 8)
    if 'r' == lid.split(':')[-1] or 'c' == lid.split(':')[-1]:
        return (4, 8)
    if 'led' in lid:
        return (6, 6)
    if 'switch' in lid:
        return (6, 6)
    if 'gnd' in lid or 'pwr' in lid:
        return (4, 4)
    return (10, 8)

def render(components, wires, labels, texts):
    """Render schematic to PNG."""
    fig, ax = plt.subplots(1, 1, figsize=(48, 32), dpi=150)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    # Gather all coords for auto-scale
    all_x = [c['x'] for c in components] + [l['x'] for l in labels]
    all_y = [c['y'] for c in components] + [l['y'] for l in labels]
    for w in wires:
        all_x.extend([w[0], w[2]])
        all_y.extend([w[1], w[3]])

    if not all_x:
        print("No elements found!")
        return

    margin = 40
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(max(all_y) + margin, min(all_y) - margin)  # KiCad Y is inverted

    # Draw wires
    for x1, y1, x2, y2 in wires:
        ax.plot([x1, x2], [y1, y2], color='#4CAF50', linewidth=0.8, solid_capstyle='round')

    # Draw components
    for comp in components:
        x, y = comp['x'], comp['y']
        lib_id = comp['lib_id']
        color = get_component_color(lib_id)
        w, h = get_component_size(lib_id)

        # Skip power symbols (GND, PWR_FLAG) for cleaner view
        if 'GND' in lib_id or 'PWR_FLAG' in lib_id:
            ax.plot(x, y, marker='v' if 'GND' in lib_id else '^',
                   color='#FF5252' if 'GND' in lib_id else '#FFD740',
                   markersize=6, zorder=5)
            continue

        # Component box
        rect = FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.5",
            facecolor=color, edgecolor='white',
            alpha=0.85, linewidth=1.0, zorder=3
        )
        ax.add_patch(rect)

        # Reference label
        ax.text(x, y - 1.5, comp['ref'], ha='center', va='center',
               fontsize=5, fontweight='bold', color='#1a1a2e', zorder=4)

        # Value label
        val_display = comp['value']
        if len(val_display) > 14:
            val_display = val_display[:12] + '..'
        ax.text(x, y + 2, val_display, ha='center', va='center',
               fontsize=3.5, color='#333333', zorder=4)

    # Draw labels
    for label in labels:
        x, y = label['x'], label['y']
        color = '#FFD740' if label['is_global'] else '#80CBC4'
        fontsize = 3.5 if label['is_global'] else 3

        ax.text(x, y, label['name'], ha='center', va='center',
               fontsize=fontsize, color=color, zorder=6,
               bbox=dict(boxstyle='round,pad=0.2', facecolor='#2a2a4e',
                        edgecolor=color, alpha=0.9, linewidth=0.5))

    # Draw text annotations (section headers)
    for t in texts:
        ax.text(t['x'], t['y'], t['text'], ha='left', va='center',
               fontsize=7, color='#FFB74D', fontweight='bold', zorder=6,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#2a2a4e',
                        edgecolor='#FFB74D', alpha=0.95, linewidth=1))

    # Title
    ax.text(0.5, 0.98, 'URINE DIPSTICK ANALYZER — Full Schematic',
           transform=ax.transAxes, ha='center', va='top',
           fontsize=20, color='white', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='#0d47a1', alpha=0.9))

    ax.text(0.5, 0.955, 'ESP32-S3 • ILI9341 TFT • OV2640 Camera • DS3231 RTC • MAX17048 Battery • A4988 Stepper',
           transform=ax.transAxes, ha='center', va='top',
           fontsize=10, color='#90CAF9')

    # Legend
    legend_items = [
        ('#4FC3F7', 'MCU'), ('#FF7043', 'Power'), ('#AB47BC', 'Analog'),
        ('#FFEE58', 'LEDs'), ('#66BB6A', 'MOSFETs'), ('#26C6DA', 'Sensors'),
        ('#FFA726', 'Motor'), ('#7E57C2', 'Camera'), ('#42A5F5', 'Display'),
        ('#8D6E63', 'Storage'), ('#78909C', 'Switches'), ('#A5D6A7', 'Resistors'),
        ('#90CAF9', 'Capacitors'), ('#4CAF50', 'Wires')
    ]
    for i, (color, name) in enumerate(legend_items):
        lx = 0.02 + (i % 7) * 0.14
        ly = 0.025 - (i // 7) * 0.02
        ax.plot(lx, ly, 's', color=color, markersize=8, transform=ax.transAxes)
        ax.text(lx + 0.012, ly, name, transform=ax.transAxes, va='center',
               fontsize=7, color='white')

    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"Saved: {OUTPUT}")

if __name__ == '__main__':
    with open(SCHEMATIC, 'r') as f:
        text = f.read()

    components = extract_components(text)
    wires = extract_wires(text)
    labels = extract_labels(text)
    texts = extract_texts(text)

    print(f"Components: {len(components)}")
    print(f"Wires: {len(wires)}")
    print(f"Labels: {len(labels)}")
    print(f"Texts: {len(texts)}")

    render(components, wires, labels, texts)
