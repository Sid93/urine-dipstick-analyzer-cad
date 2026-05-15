#!/usr/bin/env python3
"""Generate a formatted BOM PDF from BOM.csv."""
import csv
import os
from fpdf import FPDF, XPos, YPos

BASE = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE, "BOM.csv")
PDF_PATH = os.path.join(BASE, "BOM.pdf")

class BOMPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "Urine Dipstick Analyzer v2.0 - Bill of Materials", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, "ESP32-S3 | ILI9341 TFT | OV2640 Camera | DS3231 RTC | MAX17048 Battery Gauge", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def main():
    pdf = BOMPDF("L", "mm", "A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    col_widths = [55, 14, 52, 72, 8, 16, 16, 20, 24]
    col_names = ["Category", "Ref", "Component", "Description", "Qty", "Unit $", "Total $", "Source", ""]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(41, 65, 122)
    pdf.set_text_color(255, 255, 255)
    for i, name in enumerate(col_names):
        pdf.cell(col_widths[i], 6, name, border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)

    current_section = ""
    total_cost = 0.0
    total_parts = 0
    electrical_cost = 0.0
    mechanical_cost = 0.0

    for row in rows:
        if len(row) < 9:
            continue

        cat, ref, comp, desc, qty_s, unit_s, total_s, source, url = row

        if cat.startswith("ELECTRONICS") or cat.startswith("MECHANICAL"):
            if cat != current_section:
                current_section = cat
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_fill_color(230, 240, 255)
                pdf.cell(sum(col_widths), 5, cat, border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Helvetica", "", 6.5)
            continue

        try:
            qty = int(qty_s)
            unit_cost = float(unit_s)
            line_total = float(total_s)
        except ValueError:
            continue

        total_cost += line_total
        total_parts += qty
        if "electrical" in current_section.lower() or "ELECTRONICS" in current_section:
            electrical_cost += line_total
        else:
            mechanical_cost += line_total

        if desc and len(desc) > 45:
            desc = desc[:43] + ".."
        if comp and len(comp) > 32:
            comp = comp[:30] + ".."

        alt_row = (total_parts % 2 == 0)
        if alt_row:
            pdf.set_fill_color(245, 248, 255)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(col_widths[0], 5, "", border=1, fill=alt_row)
        pdf.cell(col_widths[1], 5, ref, border=1, fill=alt_row)
        pdf.cell(col_widths[2], 5, comp, border=1, fill=alt_row)
        pdf.cell(col_widths[3], 5, desc, border=1, fill=alt_row)
        pdf.cell(col_widths[4], 5, str(qty), border=1, fill=alt_row, align="C")
        pdf.cell(col_widths[5], 5, f"${unit_cost:.2f}", border=1, fill=alt_row, align="R")
        pdf.cell(col_widths[6], 5, f"${line_total:.2f}", border=1, fill=alt_row, align="R")
        pdf.cell(col_widths[7], 5, source, border=1, fill=alt_row)
        pdf.cell(col_widths[8], 5, "Link" if url and url != "N/A" else "", border=1, fill=alt_row, align="C")
        if url and url != "N/A":
            x = pdf.get_x() - col_widths[8]
            y = pdf.get_y()
            pdf.link(x, y, col_widths[8], 5, url)
        pdf.ln()

    # Totals
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(41, 65, 122)
    pdf.set_text_color(255, 255, 255)

    sum_w = sum(col_widths[:6])
    pdf.cell(sum_w, 7, f"TOTAL ({total_parts} parts)", border=1, fill=True)
    pdf.cell(col_widths[6], 7, f"${total_cost:.2f}", border=1, fill=True, align="R")
    pdf.cell(sum(col_widths[7:]), 7, "", border=1, fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    pdf.ln(4)
    pdf.cell(0, 5, f"Electronics subtotal: ${electrical_cost:.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, f"Mechanical subtotal: ${mechanical_cost:.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 4, "Notes: Prices are approximate and based on single-unit purchases. Volume pricing (100+ units) typically reduces costs by 30-50%. The ILI9341 TFT, DS3231 RTC, and MAX17048 fuel gauge are v2.0 upgrades replacing the original SSD1306 OLED. Custom injection-molded parts (enclosure, tray) can be 3D-printed for prototyping.")

    pdf.output(PDF_PATH)
    print(f"BOM PDF saved: {PDF_PATH}")
    print(f"Total parts: {total_parts}")
    print(f"Total cost: ${total_cost:.2f}")

if __name__ == "__main__":
    main()
