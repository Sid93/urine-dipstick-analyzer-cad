"""
Generate 2D engineering drawing PDFs with orthographic views,
dimensions, and tolerances for all 7 urine dipstick analyzer components.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os

OUT_DIR = "/Users/siddhantsaboo/Desktop/agentic workflows/urine_dipstick_cad/drawings"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Drawing helpers ---

def dim_horizontal(ax, x1, x2, y, text, offset=5, fontsize=7):
    """Draw a horizontal dimension line with arrows and text."""
    yo = y + offset
    ax.annotate('', xy=(x1, yo), xytext=(x2, yo),
                arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
    ax.plot([x1, x1], [y, yo], 'k-', lw=0.4, ls='--')
    ax.plot([x2, x2], [y, yo], 'k-', lw=0.4, ls='--')
    ax.text((x1+x2)/2, yo+1, text, ha='center', va='bottom', fontsize=fontsize,
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none'))

def dim_vertical(ax, y1, y2, x, text, offset=5, fontsize=7):
    """Draw a vertical dimension line with arrows and text."""
    xo = x + offset
    ax.annotate('', xy=(xo, y1), xytext=(xo, y2),
                arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
    ax.plot([x, xo], [y1, y1], 'k-', lw=0.4, ls='--')
    ax.plot([x, xo], [y2, y2], 'k-', lw=0.4, ls='--')
    ax.text(xo+1, (y1+y2)/2, text, ha='left', va='center', fontsize=fontsize,
            rotation=90, bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none'))

def dim_leader(ax, x, y, text, dx=10, dy=10, fontsize=6.5):
    """Draw a leader line with annotation."""
    ax.annotate(text, xy=(x, y), xytext=(x+dx, y+dy),
                fontsize=fontsize, ha='left',
                arrowprops=dict(arrowstyle='->', color='black', lw=0.6),
                bbox=dict(boxstyle='round,pad=0.15', fc='lightyellow', ec='gray', lw=0.4))

def title_block(ax, fig, part_name, part_no, material, scale, tolerances, dims_text):
    """Draw a title block at the bottom of the drawing."""
    tb_y = 0.02
    tb_h = 0.10
    tb = fig.add_axes([0.05, tb_y, 0.9, tb_h])
    tb.set_xlim(0, 100)
    tb.set_ylim(0, 10)
    tb.set_aspect('auto')

    tb.add_patch(patches.Rectangle((0, 0), 100, 10, fill=False, ec='black', lw=1.5))
    tb.plot([0, 100], [5, 5], 'k-', lw=0.8)
    tb.plot([30, 30], [0, 10], 'k-', lw=0.8)
    tb.plot([55, 55], [0, 10], 'k-', lw=0.8)
    tb.plot([75, 75], [0, 10], 'k-', lw=0.8)

    tb.text(15, 7.5, part_name, ha='center', va='center', fontsize=9, fontweight='bold')
    tb.text(15, 2.5, f'Part No: {part_no}', ha='center', va='center', fontsize=7)

    tb.text(42.5, 7.5, f'Material: {material}', ha='center', va='center', fontsize=7)
    tb.text(42.5, 2.5, f'Scale: {scale}', ha='center', va='center', fontsize=7)

    tb.text(65, 7.5, 'General Tolerances:', ha='center', va='center', fontsize=6.5, fontweight='bold')
    tb.text(65, 2.5, tolerances, ha='center', va='center', fontsize=6)

    tb.text(87.5, 7.5, 'Dims: mm', ha='center', va='center', fontsize=7)
    tb.text(87.5, 2.5, dims_text, ha='center', va='center', fontsize=6)

    tb.set_xticks([])
    tb.set_yticks([])
    for spine in tb.spines.values():
        spine.set_visible(False)

def setup_view(ax, title):
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=8, fontweight='bold', pad=4)
    ax.grid(True, alpha=0.15, lw=0.3)
    ax.tick_params(labelsize=5)


# ===================================================================
# 1. ENCLOSURE BASE
# ===================================================================
def draw_enclosure_base():
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('ENGINEERING DRAWING — Molded Enclosure Base', fontsize=14, fontweight='bold', y=0.97)

    # TOP VIEW
    ax1 = fig.add_axes([0.05, 0.45, 0.42, 0.45])
    setup_view(ax1, 'TOP VIEW')
    # Outer shell
    outer = patches.FancyBboxPatch((0, 0), 180, 120, boxstyle="round,pad=3",
                                    fill=False, ec='black', lw=1.5)
    ax1.add_patch(outer)
    # Inner cavity (2mm walls)
    inner = patches.FancyBboxPatch((2, 2), 176, 116, boxstyle="round,pad=2",
                                    fill=True, fc='#f0f0f0', ec='black', lw=0.8, ls='--')
    ax1.add_patch(inner)
    # Tray guide rails
    ax1.add_patch(patches.Rectangle((10, 45), 160, 3, fc='#ccc', ec='black', lw=0.5))
    ax1.add_patch(patches.Rectangle((10, 72), 160, 3, fc='#ccc', ec='black', lw=0.5))
    # M3 cover bosses (4 corners)
    for cx, cy in [(15, 15), (165, 15), (15, 105), (165, 105)]:
        ax1.add_patch(plt.Circle((cx, cy), 4, fc='#ddd', ec='black', lw=0.6))
        ax1.add_patch(plt.Circle((cx, cy), 1.5, fc='white', ec='black', lw=0.4))
    # Mounting bosses (representative)
    boss_positions = [
        (30, 25, 'MCU'), (60, 25, 'PWR PCB'), (90, 95, 'Stepper'),
        (140, 95, 'Fan'), (45, 95, 'Scanner'), (120, 25, 'Charger'),
    ]
    for bx, by, label in boss_positions:
        ax1.add_patch(plt.Circle((bx, by), 2.5, fc='#e8e8e8', ec='black', lw=0.5))
        ax1.text(bx, by-5, label, ha='center', fontsize=4.5, color='gray')
    # USB-C cutout (rear)
    ax1.add_patch(patches.Rectangle((80, -1), 9, 3, fc='white', ec='black', lw=0.8))
    ax1.text(84.5, -4, 'USB-C', ha='center', fontsize=5, color='blue')

    # Dimensions
    dim_horizontal(ax1, 0, 180, -8, '180.0 +/-0.3', offset=-8)
    dim_vertical(ax1, 0, 120, -8, '120.0 +/-0.3', offset=-8)
    dim_horizontal(ax1, 10, 170, 125, '160.0 (guide rails)', offset=5)
    dim_horizontal(ax1, 80, 89, -18, '9.0 (USB-C)', offset=-6)
    dim_leader(ax1, 15, 15, 'M3 boss x4\n(heat-set insert)\ndia 8.0, bore 4.2', dx=15, dy=15)
    dim_leader(ax1, 10, 46, 'Tray guide rail\n3.0 wide x 160 long', dx=20, dy=15)

    ax1.set_xlim(-25, 210)
    ax1.set_ylim(-30, 150)

    # FRONT VIEW
    ax2 = fig.add_axes([0.05, 0.14, 0.42, 0.28])
    setup_view(ax2, 'FRONT VIEW')
    ax2.add_patch(patches.FancyBboxPatch((0, 0), 180, 40, boxstyle="round,pad=2",
                                          fill=False, ec='black', lw=1.5))
    # Wall thickness indicator
    ax2.add_patch(patches.Rectangle((2, 2), 176, 36, fill=False, ec='black', lw=0.5, ls='--'))
    # Rubber feet
    for fx in [15, 55, 125, 165]:
        ax2.add_patch(patches.Rectangle((fx-4, -2), 8, 2, fc='#888', ec='black', lw=0.5))
    # Vent slots
    for vy in [8, 14, 20, 26, 32]:
        ax2.add_patch(patches.Rectangle((170, vy), 8, 2, fc='white', ec='black', lw=0.3))

    dim_horizontal(ax2, 0, 180, -8, '180.0', offset=-6)
    dim_vertical(ax2, 0, 40, -8, '40.0 +/-0.2', offset=-8)
    dim_vertical(ax2, 0, 2, 185, '2.0 wall', offset=5)
    dim_leader(ax2, 15, -2, 'Rubber feet x4\n8x8x2mm recess', dx=20, dy=-8)
    dim_leader(ax2, 174, 20, 'Vent slots x5\n8x2mm', dx=10, dy=10)

    ax2.set_xlim(-20, 210)
    ax2.set_ylim(-20, 55)

    # SIDE VIEW
    ax3 = fig.add_axes([0.52, 0.45, 0.25, 0.45])
    setup_view(ax3, 'RIGHT SIDE VIEW')
    ax3.add_patch(patches.FancyBboxPatch((0, 0), 120, 40, boxstyle="round,pad=2",
                                          fill=False, ec='black', lw=1.5))
    ax3.add_patch(patches.Rectangle((2, 2), 116, 36, fill=False, ec='black', lw=0.5, ls='--'))
    # Internal ribs
    for rx in [40, 80]:
        ax3.plot([rx, rx], [2, 38], 'k-', lw=0.4, ls='-.')
    ax3.text(60, 20, 'Internal ribs\n(2mm thick)', ha='center', fontsize=5, color='gray')

    dim_horizontal(ax3, 0, 120, -6, '120.0', offset=-5)
    dim_vertical(ax3, 0, 40, -6, '40.0', offset=-5)

    ax3.set_xlim(-15, 140)
    ax3.set_ylim(-15, 55)

    # Notes
    ax4 = fig.add_axes([0.52, 0.14, 0.44, 0.28])
    ax4.set_xlim(0, 100)
    ax4.set_ylim(0, 100)
    ax4.set_xticks([])
    ax4.set_yticks([])
    notes = [
        "NOTES:",
        "1. Material: ABS (injection molded) or PETG (3D printed)",
        "2. All internal surfaces matte black finish",
        "3. Draft angle: 2 deg on all vertical walls (molding)",
        "4. Wall thickness: 2.0mm uniform +/-0.1mm",
        "5. M3 heat-set insert bosses: OD 8.0, ID 4.2, depth 6.0",
        "6. M2 mounting bosses: OD 5.0, ID 2.2, depth 5.0",
        "7. M2.5 standoff holes: OD 6.0, ID 2.7, depth 5.0",
        "8. M3 screw bosses: OD 7.0, ID 3.2, depth 6.0",
        "9. Tray guide rails: 3.0W x 2.0H, polished surface",
        "10. USB-C port: 9.0W x 3.5H cutout, rear center",
        "11. Fillet all internal edges R1.0 min",
        "12. 4x rubber feet recesses: 8x8mm, 2mm deep",
    ]
    for i, note in enumerate(notes):
        weight = 'bold' if i == 0 else 'normal'
        ax4.text(2, 95 - i*7.5, note, fontsize=6.5, fontweight=weight, va='top')
    for spine in ax4.spines.values():
        spine.set_linewidth(1)

    title_block(ax4, fig, 'Molded Enclosure Base', 'UDA-001',
                'ABS / PETG', '1:1',
                'Linear: +/-0.3mm\nAngular: +/-0.5 deg',
                '180 x 120 x 40')

    fig.savefig(os.path.join(OUT_DIR, '01_enclosure_base.pdf'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  1/7 Enclosure base done")


# ===================================================================
# 2. ENCLOSURE COVER
# ===================================================================
def draw_enclosure_cover():
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('ENGINEERING DRAWING — Enclosure Top Cover', fontsize=14, fontweight='bold', y=0.97)

    # TOP VIEW
    ax1 = fig.add_axes([0.05, 0.45, 0.42, 0.45])
    setup_view(ax1, 'TOP VIEW (exterior)')
    outer = patches.FancyBboxPatch((0, 0), 180, 120, boxstyle="round,pad=3",
                                    fill=True, fc='#f8f8f8', ec='black', lw=1.5)
    ax1.add_patch(outer)
    # OLED window
    ax1.add_patch(patches.Rectangle((30, 46), 27, 27, fc='white', ec='blue', lw=1))
    ax1.text(43.5, 59.5, 'OLED\n27x27', ha='center', va='center', fontsize=5, color='blue')
    # LED hole
    ax1.add_patch(plt.Circle((150, 100), 2.5, fc='white', ec='red', lw=0.8))
    ax1.text(150, 93, 'LED dia 5.0', ha='center', fontsize=5, color='red')
    # M3 screw holes
    for cx, cy in [(15, 15), (165, 15), (15, 105), (165, 105)]:
        ax1.add_patch(plt.Circle((cx, cy), 2, fc='white', ec='black', lw=0.8))
        ax1.add_patch(plt.Circle((cx, cy), 3.5, fc='none', ec='black', lw=0.4, ls='--'))
    # Vent grill opening
    ax1.add_patch(patches.Rectangle((135, 5), 38, 38, fc='#eee', ec='black', lw=0.6, ls='--'))
    ax1.text(154, 24, 'Vent grill\nsnap-fit\n38x38', ha='center', fontsize=4.5, color='gray')
    # UV bezel
    ax1.add_patch(patches.Rectangle((70, 75), 40, 25, fill=False, ec='purple', lw=0.8, ls='--'))
    ax1.text(90, 87, 'UV bezel area', ha='center', fontsize=5, color='purple')
    # Gasket groove (dashed inner perimeter)
    ax1.add_patch(patches.FancyBboxPatch((3, 3), 174, 114, boxstyle="round,pad=2",
                                          fill=False, ec='green', lw=0.6, ls='--'))
    ax1.text(90, 7, 'Gasket groove (1.0W x 0.5D)', ha='center', fontsize=5, color='green')

    dim_horizontal(ax1, 0, 180, -8, '180.0 +/-0.2', offset=-8)
    dim_vertical(ax1, 0, 120, -8, '120.0 +/-0.2', offset=-8)
    dim_horizontal(ax1, 30, 57, 130, '27.0 (OLED)', offset=5)
    dim_leader(ax1, 15, 15, 'M3 countersunk\ndia 6.5/3.2\nx4 places', dx=15, dy=15)

    ax1.set_xlim(-25, 210)
    ax1.set_ylim(-25, 150)

    # SECTION VIEW
    ax2 = fig.add_axes([0.05, 0.14, 0.42, 0.28])
    setup_view(ax2, 'SECTION A-A (cross section)')
    # Cover profile
    ax2.add_patch(patches.Rectangle((0, 0), 180, 5, fc='#e0e0e0', ec='black', lw=1.2))
    # Gasket groove
    ax2.add_patch(patches.Rectangle((3, 0), 1, 0.5, fc='white', ec='green', lw=0.6))
    ax2.add_patch(patches.Rectangle((176, 0), 1, 0.5, fc='white', ec='green', lw=0.6))
    # Screw hole
    ax2.plot([15, 15], [0, 5], 'k--', lw=0.5)
    ax2.add_patch(plt.Circle((15, 2.5), 1.6, fc='white', ec='black', lw=0.5))
    # OLED cutout
    ax2.add_patch(patches.Rectangle((30, 0), 27, 5, fc='white', ec='blue', lw=0.8))
    ax2.text(43.5, 2.5, 'OLED window', ha='center', fontsize=5, color='blue')

    dim_vertical(ax2, 0, 5, -6, '5.0 +/-0.1', offset=-5)
    dim_horizontal(ax2, 0, 180, -5, '180.0', offset=-4)
    dim_leader(ax2, 3, 0.5, 'Gasket groove\n1.0W x 0.5D', dx=10, dy=5)

    ax2.set_xlim(-15, 200)
    ax2.set_ylim(-12, 15)

    # Notes
    ax3 = fig.add_axes([0.52, 0.14, 0.44, 0.78])
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_xticks([])
    ax3.set_yticks([])
    notes = [
        "NOTES:",
        "1. Material: PETG (3D printed, 100% infill)",
        "2. Thickness: 5.0mm uniform",
        "3. M3 countersunk holes: dia 6.5 top, dia 3.2 thru",
        "4. OLED display window: 27.0 x 27.0mm thru-cut",
        "5. Status LED hole: dia 5.0mm, friction fit",
        "6. Perimeter gasket groove: 1.0mm wide, 0.5mm deep",
        "7. Vent grill snap-fit: 2 slots, 2.0W x 1.5D x 5.0L",
        "8. UV bezel area: 40 x 25mm recessed 0.5mm",
        "9. Corner radius: R3.0 all corners",
        "10. Surface finish: matte (medical device aesthetic)",
        "",
        "TOLERANCES (GD&T):",
        "  Flatness: 0.2mm over full surface",
        "  Perpendicularity (screw holes): 0.1mm",
        "  Position (screw holes): +/-0.15mm true position",
        "  Position (OLED window): +/-0.2mm true position",
    ]
    for i, note in enumerate(notes):
        weight = 'bold' if i == 0 or 'GD&T' in note else 'normal'
        ax3.text(2, 97 - i*5.5, note, fontsize=7, fontweight=weight, va='top')
    for spine in ax3.spines.values():
        spine.set_linewidth(1)

    title_block(ax3, fig, 'Enclosure Top Cover', 'UDA-002',
                'PETG (100% infill)', '1:1',
                'Linear: +/-0.2mm\nPosition: +/-0.15mm',
                '180 x 120 x 5')

    fig.savefig(os.path.join(OUT_DIR, '02_enclosure_cover.pdf'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  2/7 Enclosure cover done")


# ===================================================================
# 3. DIPSTICK TRAY
# ===================================================================
def draw_dipstick_tray():
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('ENGINEERING DRAWING — Dipstick Measurement Tray', fontsize=14, fontweight='bold', y=0.97)

    # TOP VIEW
    ax1 = fig.add_axes([0.05, 0.52, 0.55, 0.38])
    setup_view(ax1, 'TOP VIEW')
    ax1.add_patch(patches.Rectangle((0, 0), 120, 25, fc='#f5f5f5', ec='black', lw=1.5))
    # Strip channel
    ax1.add_patch(patches.Rectangle((20, 9.5), 80, 6, fc='#333', ec='black', lw=0.8))
    ax1.text(60, 12.5, 'Dipstick channel (flocked)', ha='center', va='center',
             fontsize=5, color='white')
    # Calibration card recess
    ax1.add_patch(patches.Rectangle((5, 7.5), 10, 5, fc='#ffd', ec='orange', lw=0.6))
    ax1.text(10, 5, 'Cal card\n10x5', ha='center', fontsize=4, color='orange')
    # White balance target
    ax1.add_patch(patches.Rectangle((5, 14), 10, 5, fc='#eef', ec='blue', lw=0.6))
    ax1.text(10, 21, 'WB target\n10x5', ha='center', fontsize=4, color='blue')
    # T8 nut bore
    ax1.add_patch(plt.Circle((110, 12.5), 4, fc='#ddd', ec='black', lw=0.8))
    ax1.add_patch(plt.Circle((110, 12.5), 5.5, fc='none', ec='black', lw=0.4, ls='--'))
    ax1.text(110, 3, 'T8 nut\nbore', ha='center', fontsize=4.5)
    # Magnet pocket
    ax1.add_patch(plt.Circle((3, 12.5), 2.5, fc='#ddf', ec='purple', lw=0.6))
    ax1.text(-6, 12.5, 'Magnet', ha='center', fontsize=4, color='purple')
    # Guide grooves on sides
    ax1.add_patch(patches.Rectangle((5, -1), 110, 1.5, fc='#ccc', ec='black', lw=0.3))
    ax1.add_patch(patches.Rectangle((5, 24.5), 110, 1.5, fc='#ccc', ec='black', lw=0.3))

    dim_horizontal(ax1, 0, 120, -8, '120.0 +/-0.2', offset=-6)
    dim_vertical(ax1, 0, 25, -8, '25.0 +/-0.15', offset=-6)
    dim_horizontal(ax1, 20, 100, 28, '80.0 (channel length)', offset=4)
    dim_vertical(ax1, 9.5, 15.5, 105, '6.0 (channel W)', offset=8)
    dim_leader(ax1, 5, -1, 'Guide groove\n1.5H, full length', dx=15, dy=-8)

    ax1.set_xlim(-20, 145)
    ax1.set_ylim(-18, 40)

    # BOTTOM VIEW
    ax2 = fig.add_axes([0.05, 0.14, 0.55, 0.33])
    setup_view(ax2, 'BOTTOM VIEW')
    ax2.add_patch(patches.Rectangle((0, 0), 120, 25, fc='#f0f0f0', ec='black', lw=1.5))
    # Heater film recess
    ax2.add_patch(patches.Rectangle((35, 3), 50, 19, fc='#ffe0e0', ec='red', lw=0.8, ls='--'))
    ax2.text(60, 12.5, 'Heater film recess\n50 x 19 x 0.5 deep', ha='center',
             fontsize=5, color='red')
    # Thermistor pocket
    ax2.add_patch(plt.Circle((90, 12.5), 2, fc='#fff0e0', ec='orange', lw=0.6))
    ax2.text(90, 7, 'Thermistor\npocket', ha='center', fontsize=4.5, color='orange')
    # T8 flange recess
    ax2.add_patch(plt.Circle((110, 12.5), 7, fc='#eee', ec='black', lw=0.5, ls='--'))
    ax2.text(110, 3, 'T8 flange\nrecess dia 14', ha='center', fontsize=4.5)

    dim_horizontal(ax2, 35, 85, -5, '50.0 (heater)', offset=-4)
    dim_vertical(ax2, 3, 22, -5, '19.0', offset=-5)

    ax2.set_xlim(-12, 135)
    ax2.set_ylim(-12, 35)

    # SECTION + NOTES
    ax3 = fig.add_axes([0.62, 0.14, 0.35, 0.78])
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_xticks([])
    ax3.set_yticks([])

    # Cross-section sketch at top
    ax3.text(50, 98, 'SECTION B-B', ha='center', fontsize=8, fontweight='bold')
    # Draw simplified cross section
    xs = [10, 10, 15, 15, 18, 18, 72, 72, 75, 75, 90, 90]
    ys = [80, 88, 88, 85, 85, 88, 88, 85, 85, 88, 88, 80]
    ax3.plot(xs, ys, 'k-', lw=1.2)
    ax3.plot([10, 90], [80, 80], 'k-', lw=1.2)
    ax3.text(45, 86, '6.0 channel', ha='center', fontsize=5, color='#333')
    ax3.text(50, 78, '25.0', ha='center', fontsize=5)
    ax3.text(5, 84, '8.0', ha='center', fontsize=5, rotation=90)

    notes = [
        "NOTES:",
        "1. Material: ABS (injection molded)",
        "   - No undercuts, uniform wall 2.0mm",
        "   - 2 deg draft on all vertical faces",
        "2. Strip channel: 6.0W x 3.0D x 80.0L",
        "   - Apply flocking sheet to channel floor",
        "   - Surface must be matte black",
        "3. Cal card recess: 10x5mm, 0.3mm deep",
        "4. WB target recess: 10x5mm, 0.3mm deep",
        "5. T8 copper nut bore: dia 8.0 thru",
        "   - Flange recess: dia 14.0, 1.5mm deep",
        "   - 2x M3 mounting holes at 10mm PCD",
        "6. Heater film recess (bottom): 50x19mm, 0.5D",
        "7. Thermistor pocket: dia 4.0, 2.0mm deep",
        "8. Magnet pocket: dia 5.0, 3.0mm deep",
        "9. Side guide grooves: 1.5H x 2.0W, full L",
        "",
        "CRITICAL TOLERANCES:",
        "  Channel width: 6.0 +/-0.1mm",
        "  Channel depth: 3.0 +/-0.05mm",
        "  T8 bore position: +/-0.1mm true position",
        "  Guide groove parallelism: 0.1mm/100mm",
        "  Flatness (channel floor): 0.05mm",
    ]
    for i, note in enumerate(notes):
        weight = 'bold' if i == 0 or 'CRITICAL' in note else 'normal'
        ax3.text(2, 70 - i*3.2, note, fontsize=5.5, fontweight=weight, va='top',
                 family='monospace' if note.startswith('  ') else 'sans-serif')
    for spine in ax3.spines.values():
        spine.set_linewidth(1)

    title_block(ax3, fig, 'Dipstick Measurement Tray', 'UDA-003',
                'ABS (injection molded)', '2:1',
                'Linear: +/-0.15mm\nChannel: +/-0.1mm',
                '120 x 25 x 8')

    fig.savefig(os.path.join(OUT_DIR, '03_dipstick_tray.pdf'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  3/7 Dipstick tray done")


# ===================================================================
# 4. CAMERA & LED MOUNT
# ===================================================================
def draw_camera_led_mount():
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('ENGINEERING DRAWING — Camera & LED Mount', fontsize=14, fontweight='bold', y=0.97)

    # FRONT VIEW
    ax1 = fig.add_axes([0.05, 0.45, 0.4, 0.45])
    setup_view(ax1, 'FRONT VIEW')
    ax1.add_patch(patches.Rectangle((0, 0), 40, 30, fc='#f0f0f0', ec='black', lw=1.5))
    # Camera pocket
    ax1.add_patch(patches.Rectangle((4, 4), 32, 22, fc='#ddd', ec='black', lw=0.8))
    ax1.add_patch(patches.Rectangle((10, 7), 20, 16, fc='#eee', ec='blue', lw=0.8, ls='--'))
    ax1.text(20, 15, 'OV2640\ncavity\n20x16', ha='center', va='center', fontsize=5, color='blue')
    # Snap clips
    ax1.add_patch(patches.Rectangle((4, 25), 4, 2, fc='#aaa', ec='black', lw=0.4))
    ax1.add_patch(patches.Rectangle((32, 25), 4, 2, fc='#aaa', ec='black', lw=0.4))

    dim_horizontal(ax1, 0, 40, -5, '40.0 +/-0.2', offset=-4)
    dim_vertical(ax1, 0, 30, -5, '30.0 +/-0.2', offset=-5)
    dim_horizontal(ax1, 10, 30, 32, '20.0 (camera pocket)', offset=3)
    dim_leader(ax1, 6, 26, 'Snap clip x2', dx=12, dy=5)

    ax1.set_xlim(-12, 55)
    ax1.set_ylim(-12, 42)

    # SIDE VIEW (section showing 45-deg LED angle)
    ax2 = fig.add_axes([0.5, 0.45, 0.35, 0.45])
    setup_view(ax2, 'SIDE VIEW (section showing LED angle)')
    ax2.add_patch(patches.Rectangle((0, 0), 30, 25, fc='#f0f0f0', ec='black', lw=1.5))
    # Camera looking down
    ax2.add_patch(patches.Rectangle((8, 17), 14, 6, fc='#ddd', ec='blue', lw=0.8))
    ax2.text(15, 20, 'Camera', ha='center', fontsize=5, color='blue')
    # LED slot at 45 degrees
    led_x = [2, 8, 10, 4]
    led_y = [8, 14, 12, 6]
    ax2.fill(led_x, led_y, fc='#ffe0a0', ec='orange', lw=0.8)
    ax2.text(3, 3, 'LED slot\n45 deg', fontsize=5, color='orange')
    # Light path arrow
    ax2.annotate('', xy=(15, 0), xytext=(6, 11),
                arrowprops=dict(arrowstyle='->', color='orange', lw=1, ls='--'))
    # Diffuser slot
    ax2.add_patch(patches.Rectangle((0, 14), 30, 1, fc='#eef', ec='green', lw=0.6))
    ax2.text(22, 15.5, 'Diffuser slot', fontsize=4.5, color='green')
    # Quartz glass shelf
    ax2.add_patch(patches.Rectangle((5, 16), 20, 1, fc='#eef', ec='purple', lw=0.6))
    ax2.text(22, 17.5, 'Quartz shelf', fontsize=4.5, color='purple')

    dim_vertical(ax2, 0, 25, -5, '25.0 +/-0.2', offset=-5)
    dim_horizontal(ax2, 0, 30, -4, '30.0', offset=-3)
    # 45 degree angle annotation
    from matplotlib.patches import Arc
    arc = Arc((6, 11), 8, 8, angle=0, theta1=-90, theta2=-45, color='orange', lw=0.8)
    ax2.add_patch(arc)
    ax2.text(9, 5, '45 deg', fontsize=5, color='orange')

    ax2.set_xlim(-10, 42)
    ax2.set_ylim(-8, 32)

    # BOTTOM VIEW
    ax3 = fig.add_axes([0.05, 0.14, 0.4, 0.28])
    setup_view(ax3, 'BOTTOM VIEW (LED & diffuser face)')
    ax3.add_patch(patches.Rectangle((0, 0), 40, 30, fc='#f0f0f0', ec='black', lw=1.5))
    # LED array slot
    ax3.add_patch(patches.Rectangle((5, 18), 30, 10, fc='#ffe0a0', ec='orange', lw=0.8))
    ax3.text(20, 23, 'LED array slot\n30 x 10', ha='center', fontsize=5, color='orange')
    # Diffuser slot
    ax3.add_patch(patches.Rectangle((5, 5), 30, 20, fc='none', ec='green', lw=0.8, ls='--'))
    ax3.text(20, 2, 'Diffuser slot 30x20x1', ha='center', fontsize=5, color='green')
    # M2 mounting holes
    ax3.add_patch(plt.Circle((5, 2), 1, fc='white', ec='black', lw=0.5))
    ax3.add_patch(plt.Circle((35, 2), 1, fc='white', ec='black', lw=0.5))
    ax3.text(20, -3, 'M2 mounting holes x2', ha='center', fontsize=5)
    # Cable channels
    ax3.add_patch(patches.Rectangle((38, 10), 2, 10, fc='#eee', ec='gray', lw=0.4))
    ax3.text(42, 15, 'Cable\nchannel', fontsize=4, color='gray')

    dim_horizontal(ax3, 5, 35, 30, '30.0 (LED/diffuser)', offset=3)

    ax3.set_xlim(-8, 50)
    ax3.set_ylim(-8, 38)

    # Notes
    ax4 = fig.add_axes([0.5, 0.14, 0.45, 0.28])
    ax4.set_xlim(0, 100)
    ax4.set_ylim(0, 100)
    ax4.set_xticks([])
    ax4.set_yticks([])
    notes = [
        "NOTES:",
        "1. Material: PETG (black, 50% infill, 0.2mm layer)",
        "2. Camera pocket: 32x22mm, snap-fit clips hold OV2640",
        "3. LED slot: 30x10x2mm at 45 deg angle",
        "4. Diffuser panel press-fit: 30x20x1mm slot",
        "5. Quartz glass shelf: 20x20mm recess, 1mm deep",
        "6. Cable routing channels: 5x3mm on rear face",
        "7. M2 mounting holes: 2x, 30mm spacing",
        "",
        "TOLERANCES:",
        "  Camera pocket: +/-0.15mm (snap-fit critical)",
        "  LED angle: 45 deg +/-1 deg",
        "  Diffuser slot depth: 1.0 +/-0.05mm",
        "  Mounting holes: +/-0.1mm true position",
    ]
    for i, note in enumerate(notes):
        weight = 'bold' if i == 0 or 'TOLERANCES' in note else 'normal'
        ax4.text(2, 95 - i*6.5, note, fontsize=6, fontweight=weight, va='top')
    for spine in ax4.spines.values():
        spine.set_linewidth(1)

    title_block(ax4, fig, 'Camera & LED Mount', 'UDA-004',
                'PETG (3D printed)', '2:1',
                'Linear: +/-0.2mm\nAngular: +/-1 deg',
                '40 x 30 x 25')

    fig.savefig(os.path.join(OUT_DIR, '04_camera_led_mount.pdf'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  4/7 Camera & LED mount done")


# ===================================================================
# 5. SCANNER MOUNT
# ===================================================================
def draw_scanner_mount():
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('ENGINEERING DRAWING — Barcode Scanner Mount', fontsize=14, fontweight='bold', y=0.97)

    # FRONT VIEW
    ax1 = fig.add_axes([0.05, 0.45, 0.35, 0.45])
    setup_view(ax1, 'FRONT VIEW')
    ax1.add_patch(patches.Rectangle((0, 0), 35, 25, fc='#f0f0f0', ec='black', lw=1.5))
    # Scanner cradle
    ax1.add_patch(patches.Rectangle((3, 5), 29, 18, fc='#ddd', ec='black', lw=0.8))
    ax1.text(17.5, 14, 'GM65 module\ncradle\n29 x 18', ha='center', va='center', fontsize=5)
    # Snap ridges
    ax1.add_patch(patches.Rectangle((3, 22), 2, 1, fc='#aaa', ec='black', lw=0.4))
    ax1.add_patch(patches.Rectangle((30, 22), 2, 1, fc='#aaa', ec='black', lw=0.4))

    dim_horizontal(ax1, 0, 35, -5, '35.0 +/-0.2', offset=-4)
    dim_vertical(ax1, 0, 25, -5, '25.0 +/-0.2', offset=-5)
    dim_horizontal(ax1, 3, 32, 27, '29.0 (cradle)', offset=3)
    dim_vertical(ax1, 5, 23, 38, '18.0', offset=4)

    ax1.set_xlim(-12, 48)
    ax1.set_ylim(-12, 35)

    # SIDE VIEW (showing angle)
    ax2 = fig.add_axes([0.45, 0.45, 0.3, 0.45])
    setup_view(ax2, 'SIDE VIEW (showing tilt angle)')
    # Bracket body
    pts_x = [0, 25, 25, 20, 0]
    pts_y = [0, 3, 15, 15, 12]
    ax2.fill(pts_x, pts_y, fc='#f0f0f0', ec='black', lw=1.5)
    ax2.text(12, 8, 'Angled\nwedge', ha='center', fontsize=5, color='gray')
    # M2 holes
    ax2.add_patch(plt.Circle((5, 1.5), 1, fc='white', ec='black', lw=0.5))
    ax2.add_patch(plt.Circle((20, 3), 1, fc='white', ec='black', lw=0.5))
    # Cable exit
    ax2.add_patch(patches.Rectangle((-1, 8), 2, 4, fc='white', ec='gray', lw=0.5))
    ax2.text(-4, 10, 'Cable\nexit', fontsize=4, color='gray')

    dim_horizontal(ax2, 0, 25, -4, '25.0', offset=-3)
    dim_vertical(ax2, 0, 15, -4, '15.0', offset=-4)
    # Angle annotation
    ax2.annotate('~10 deg tilt', xy=(22, 5), fontsize=6, color='blue')

    ax2.set_xlim(-10, 35)
    ax2.set_ylim(-8, 22)

    # Notes
    ax3 = fig.add_axes([0.05, 0.14, 0.88, 0.28])
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_xticks([])
    ax3.set_yticks([])
    notes = [
        "NOTES:",
        "1. Material: PETG (black, 50% infill)",
        "2. Scanner cradle: sized for GM65 module (29x18mm internal)",
        "3. Snap-fit ridges: 2mm wide, 1mm tall retention clips",
        "4. Angled wedge: ~10 deg tilt to point scanner at tray entry",
        "5. M2 mounting holes: 2x through-holes for base attachment",
        "6. Cable exit slot: 4x2mm opening on rear face",
        "",
        "TOLERANCES:     Cradle width: 29.0 +0.2/-0mm (clearance fit)",
        "                Cradle depth: 18.0 +0.2/-0mm",
        "                M2 holes: +/-0.1mm true position, 20mm spacing",
        "                Snap-fit: +/-0.1mm (critical for retention)",
    ]
    for i, note in enumerate(notes):
        weight = 'bold' if i == 0 else 'normal'
        ax3.text(2, 95 - i*8, note, fontsize=7, fontweight=weight, va='top')
    for spine in ax3.spines.values():
        spine.set_linewidth(1)

    title_block(ax3, fig, 'Barcode Scanner Mount', 'UDA-005',
                'PETG (3D printed)', '3:1',
                'Linear: +/-0.2mm\nCradle: +0.2/-0mm',
                '35 x 25 x 15')

    fig.savefig(os.path.join(OUT_DIR, '05_scanner_mount.pdf'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  5/7 Scanner mount done")


# ===================================================================
# 6. VENT GRILL
# ===================================================================
def draw_vent_grill():
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('ENGINEERING DRAWING — Exhaust Vent Grill', fontsize=14, fontweight='bold', y=0.97)

    # TOP VIEW
    ax1 = fig.add_axes([0.05, 0.42, 0.4, 0.5])
    setup_view(ax1, 'TOP VIEW (exterior face)')
    ax1.add_patch(patches.FancyBboxPatch((0, 0), 35, 35, boxstyle="round,pad=2",
                                          fc='#f0f0f0', ec='black', lw=1.5))
    # Slotted openings
    for sy in range(4, 32, 3):
        ax1.add_patch(patches.Rectangle((5, sy), 25, 1, fc='white', ec='black', lw=0.5))

    # Snap tabs (extending outward)
    for tx, ty in [(0, 8), (0, 25), (35, 8), (35, 25)]:
        dx = -3 if tx == 0 else 0
        ax1.add_patch(patches.Rectangle((tx+dx, ty), 3, 4, fc='#ccc', ec='black', lw=0.6))

    dim_horizontal(ax1, 0, 35, -5, '35.0 +/-0.2', offset=-4)
    dim_vertical(ax1, 0, 35, -5, '35.0 +/-0.2', offset=-5)
    dim_horizontal(ax1, 5, 30, 37, '25.0 (slot length)', offset=3)
    dim_leader(ax1, -3, 10, 'Snap tab x4\n3x4x1.5mm\nwith locking ridge', dx=-12, dy=8)
    dim_leader(ax1, 15, 16, 'Slots: 1.0W, 1.5 spacing\n10 openings', dx=14, dy=8)

    ax1.set_xlim(-20, 52)
    ax1.set_ylim(-12, 48)

    # SECTION VIEW
    ax2 = fig.add_axes([0.5, 0.42, 0.4, 0.5])
    setup_view(ax2, 'SECTION C-C (profile)')
    # Dome profile
    xs = np.linspace(0, 35, 50)
    dome = 3 + 1.5 * np.sin(np.pi * xs / 35)
    ax2.fill_between(xs, 0, dome, fc='#f0f0f0', ec='black', lw=1.2)
    ax2.plot(xs, dome, 'k-', lw=1.2)
    ax2.plot([0, 35], [0, 0], 'k-', lw=1.2)
    # Snap tab
    ax2.add_patch(patches.Rectangle((-3, 0), 3, 1.5, fc='#ccc', ec='black', lw=0.6))
    ax2.add_patch(patches.Rectangle((35, 0), 3, 1.5, fc='#ccc', ec='black', lw=0.6))
    # Locking ridge on tab
    ax2.add_patch(patches.Rectangle((-3, 1.2), 1, 0.5, fc='#aaa', ec='black', lw=0.4))
    ax2.add_patch(patches.Rectangle((37, 1.2), 1, 0.5, fc='#aaa', ec='black', lw=0.4))

    dim_vertical(ax2, 0, 3, -5, '3.0 (base)', offset=-5)
    dim_vertical(ax2, 0, 4.5, 40, '4.5 (peak)', offset=5)
    dim_horizontal(ax2, 0, 35, -3, '35.0', offset=-3)
    dim_leader(ax2, -2, 1.5, 'Locking ridge\n0.5mm', dx=-8, dy=3)

    ax2.set_xlim(-15, 48)
    ax2.set_ylim(-8, 12)

    # Notes
    ax3 = fig.add_axes([0.05, 0.14, 0.88, 0.24])
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_xticks([])
    ax3.set_yticks([])
    notes = [
        "NOTES:                                                             TOLERANCES:",
        "1. Material: PETG (any color, 20% infill)                          Slot width: 1.0 +/-0.1mm",
        "2. Dome profile: sinusoidal, 1.5mm rise at center                  Snap tab: +/-0.1mm (press-fit critical)",
        "3. 10 parallel slots: 1.0mm wide, 25.0mm long, 1.5mm spacing      Locking ridge height: 0.5 +/-0.05mm",
        "4. 4x snap-fit tabs: 3W x 4L x 1.5H with 0.5mm locking ridge     Overall: +/-0.2mm",
        "5. Mates with enclosure cover snap-fit slots (2.0W x 1.5D x 5.0L)",
        "6. Must allow free airflow from 30mm fan exhaust",
    ]
    for i, note in enumerate(notes):
        weight = 'bold' if i == 0 else 'normal'
        ax3.text(2, 92 - i*13, note, fontsize=6.5, fontweight=weight, va='top', family='monospace')
    for spine in ax3.spines.values():
        spine.set_linewidth(1)

    title_block(ax3, fig, 'Exhaust Vent Grill', 'UDA-006',
                'PETG (3D printed)', '3:1',
                'Linear: +/-0.2mm\nSlots: +/-0.1mm',
                '35 x 35 x 4.5')

    fig.savefig(os.path.join(OUT_DIR, '06_vent_grill.pdf'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  6/7 Vent grill done")


# ===================================================================
# 7. INTERNAL WIRE FRAME
# ===================================================================
def draw_wire_frame():
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('ENGINEERING DRAWING — Internal Cable Management Frame', fontsize=14, fontweight='bold', y=0.97)

    # TOP VIEW
    ax1 = fig.add_axes([0.05, 0.42, 0.55, 0.5])
    setup_view(ax1, 'TOP VIEW')
    # Perimeter frame
    ax1.add_patch(patches.Rectangle((0, 0), 160, 100, fill=False, ec='black', lw=1.5))
    ax1.add_patch(patches.Rectangle((5, 5), 150, 90, fill=False, ec='black', lw=1.0))
    # Center beam
    ax1.add_patch(patches.Rectangle((5, 47), 150, 6, fc='#e0e0e0', ec='black', lw=0.8))
    # Transverse beams
    for tx in [40, 80, 120]:
        ax1.add_patch(patches.Rectangle((tx, 5), 5, 42, fc='#e8e8e8', ec='black', lw=0.6))
        ax1.add_patch(patches.Rectangle((tx, 53), 5, 42, fc='#e8e8e8', ec='black', lw=0.6))
    # Cable channels (grooves in beams)
    for cx in [42, 82, 122]:
        ax1.add_patch(patches.Rectangle((cx-1, 15), 3, 5, fc='white', ec='gray', lw=0.4))
        ax1.add_patch(patches.Rectangle((cx-1, 75), 3, 5, fc='white', ec='gray', lw=0.4))
    # M2.5 standoff holes (12 positions)
    standoff_pos = [
        (20, 20), (60, 20), (100, 20), (140, 20),
        (20, 50), (60, 50), (100, 50), (140, 50),
        (20, 80), (60, 80), (100, 80), (140, 80),
    ]
    for sx, sy in standoff_pos:
        ax1.add_patch(plt.Circle((sx, sy), 2, fc='white', ec='red', lw=0.5))
        ax1.add_patch(plt.Circle((sx, sy), 3.5, fc='none', ec='red', lw=0.3, ls='--'))
    # Press-fit tabs
    for py in [25, 75]:
        ax1.add_patch(patches.Rectangle((-2, py), 2, 6, fc='#ccc', ec='black', lw=0.4))
        ax1.add_patch(patches.Rectangle((160, py), 2, 6, fc='#ccc', ec='black', lw=0.4))

    dim_horizontal(ax1, 0, 160, -8, '160.0 +/-0.3', offset=-6)
    dim_vertical(ax1, 0, 100, -8, '100.0 +/-0.3', offset=-8)
    dim_horizontal(ax1, 40, 80, 103, '40.0 (beam spacing)', offset=4)
    dim_leader(ax1, 20, 20, 'M2.5 standoff hole\ndia 2.7 thru\n12 places', dx=15, dy=15)
    dim_leader(ax1, -2, 28, 'Press-fit tab\n2x6x2mm\n4 places', dx=-18, dy=8)
    dim_leader(ax1, 42, 17, 'Cable channel\n3x5mm groove', dx=12, dy=-10)

    ax1.set_xlim(-25, 185)
    ax1.set_ylim(-18, 115)

    # SECTION VIEW
    ax2 = fig.add_axes([0.65, 0.42, 0.3, 0.5])
    setup_view(ax2, 'SECTION D-D')
    # Frame cross-section
    ax2.add_patch(patches.Rectangle((0, 0), 100, 3, fc='#e0e0e0', ec='black', lw=1.2))
    # Beams going up
    ax2.add_patch(patches.Rectangle((0, 0), 5, 10, fc='#e0e0e0', ec='black', lw=0.8))
    ax2.add_patch(patches.Rectangle((95, 0), 5, 10, fc='#e0e0e0', ec='black', lw=0.8))
    ax2.add_patch(patches.Rectangle((47, 0), 6, 10, fc='#e0e0e0', ec='black', lw=0.8))
    # Cable channel groove
    ax2.add_patch(patches.Rectangle((48.5, 7), 3, 3, fc='white', ec='gray', lw=0.5))
    # Standoff holes
    ax2.add_patch(plt.Circle((20, 1.5), 1.3, fc='white', ec='red', lw=0.5))
    ax2.add_patch(plt.Circle((80, 1.5), 1.3, fc='white', ec='red', lw=0.5))

    dim_horizontal(ax2, 0, 100, -4, '100.0', offset=-3)
    dim_vertical(ax2, 0, 10, -4, '10.0', offset=-4)
    dim_vertical(ax2, 0, 3, 104, '3.0 (base)', offset=4)
    dim_leader(ax2, 50, 8, 'Cable channel\n3W x 3D', dx=12, dy=4)

    ax2.set_xlim(-10, 115)
    ax2.set_ylim(-8, 18)

    # Notes
    ax3 = fig.add_axes([0.05, 0.14, 0.88, 0.24])
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_xticks([])
    ax3.set_yticks([])
    notes = [
        "NOTES:                                                           TOLERANCES:",
        "1. Material: PETG (black, 20% infill for weight saving)          Standoff holes: dia 2.7 +0.1/-0mm",
        "2. Open skeleton design for maximum airflow                      Hole position: +/-0.2mm true position",
        "3. Base plate: 3.0mm thick, beams: 5.0mm wide x 10.0mm tall      Press-fit tabs: +/-0.1mm",
        "4. Cable channels: 3W x 3D (5mm deep from beam top)              Beam straightness: 0.3mm/100mm",
        "5. 12x M2.5 standoff mounting holes (dia 2.7mm thru)             Overall: +/-0.3mm",
        "6. 4x press-fit tabs: 2W x 6L x 2H for base engagement",
        "7. Center beam + 3 transverse beams for rigidity",
    ]
    for i, note in enumerate(notes):
        weight = 'bold' if i == 0 else 'normal'
        ax3.text(2, 92 - i*12, note, fontsize=6, fontweight=weight, va='top', family='monospace')
    for spine in ax3.spines.values():
        spine.set_linewidth(1)

    title_block(ax3, fig, 'Internal Cable Management Frame', 'UDA-007',
                'PETG (3D printed)', '1:1',
                'Linear: +/-0.3mm\nHoles: +/-0.2mm',
                '160 x 100 x 10')

    fig.savefig(os.path.join(OUT_DIR, '07_internal_wire_frame.pdf'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  7/7 Internal wire frame done")


# ===================================================================
# RUN ALL
# ===================================================================
if __name__ == '__main__':
    print("Generating engineering drawings...")
    draw_enclosure_base()
    draw_enclosure_cover()
    draw_dipstick_tray()
    draw_camera_led_mount()
    draw_scanner_mount()
    draw_vent_grill()
    draw_wire_frame()
    print(f"\nAll 7 drawings saved to {OUT_DIR}/")
