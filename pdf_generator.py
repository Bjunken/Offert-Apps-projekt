from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from datetime import datetime
import os
import sys

from company_info import load_settings
from materials import get_materials


def get_archive_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    archive = os.path.join(base, "gamla_offerter")
    os.makedirs(archive, exist_ok=True)
    return archive


def generate_pdf(services, total, moms, total_with_moms, hours_dict=None, discount=0, discount_type=None):

    settings      = load_settings()
    all_materials = get_materials()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"offert_{timestamp}.pdf"
    filepath  = os.path.join(get_archive_dir(), filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # ── Styles ────────────────────────────────────────────
    style_normal = ParagraphStyle(
        "normal", fontSize=10, leading=14, textColor=colors.black
    )
    style_small = ParagraphStyle(
        "small", fontSize=8, leading=12, textColor=colors.HexColor("#555555")
    )
    style_small_right = ParagraphStyle(
        "small_right", fontSize=8, leading=12,
        textColor=colors.HexColor("#555555"), alignment=TA_RIGHT
    )
    style_company = ParagraphStyle(
        "company", fontSize=14, leading=18, textColor=colors.black,
        fontName="Helvetica-Bold", alignment=TA_RIGHT
    )
    style_offert_nr = ParagraphStyle(
        "offert_nr", fontSize=13, leading=18, textColor=colors.black,
        fontName="Helvetica-Bold"
    )
    style_total_label = ParagraphStyle(
        "total_label", fontSize=10, leading=16,
        textColor=colors.black, alignment=TA_RIGHT
    )
    style_total_bold = ParagraphStyle(
        "total_bold", fontSize=12, leading=18,
        textColor=colors.black, fontName="Helvetica-Bold", alignment=TA_RIGHT
    )
    style_discount = ParagraphStyle(
        "discount", fontSize=10, leading=16,
        textColor=colors.HexColor("#cc1111"), alignment=TA_RIGHT
    )
    style_footer = ParagraphStyle(
        "footer", fontSize=8, leading=12,
        textColor=colors.HexColor("#888888"), alignment=TA_CENTER
    )
    style_payment_header = ParagraphStyle(
        "payment_header", fontSize=10, leading=14,
        textColor=colors.black, fontName="Helvetica-Bold"
    )
    style_table_header = ParagraphStyle(
        "table_header", fontSize=10, leading=14,
        textColor=colors.white, fontName="Helvetica-Bold"
    )
    style_mat_sub = ParagraphStyle(
        "mat_sub", fontSize=8, leading=12,
        textColor=colors.HexColor("#444444"),
        leftIndent=10
    )

    elements = []

    # ── Header: logo left, company info right ─────────────
    logo_path = settings.get("logo_path", "")

    if logo_path and os.path.exists(logo_path):
        logo_cell = Image(logo_path, width=35*mm, height=18*mm)
    else:
        logo_cell = Paragraph("", style_normal)

    company_info_cell = [
        Paragraph(settings.get("company_name", ""), style_company),
        Paragraph(settings.get("address", ""),      style_small_right),
        Paragraph(settings.get("phone", ""),         style_small_right),
        Paragraph(settings.get("email", ""),         style_small_right),
    ]

    header_table = Table(
        [[logo_cell, company_info_cell]],
        colWidths=[60*mm, 110*mm]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",(0, 0), (-1, -1), 0),
        ("TOPPADDING",  (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0,0), (-1, -1), 0),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 4*mm))

    # ── Offert number + date ──────────────────────────────
    offert_nr = datetime.now().strftime("%Y%m%d%H%M")
    elements.append(Paragraph(f"OFFERT #{offert_nr}", style_offert_nr))
    elements.append(Spacer(1, 1*mm))
    elements.append(Paragraph(f"Datum: {datetime.now().strftime('%Y-%m-%d')}", style_small))
    elements.append(Spacer(1, 6*mm))

    # ── Services table ────────────────────────────────────
    col_widths = [95*mm, 25*mm, 30*mm, 30*mm]

    table_data = [[
        Paragraph("Tjänst", style_table_header),
        Paragraph("Antal",  style_table_header),
        Paragraph("Pris",   style_table_header),
        Paragraph("Summa",  style_table_header),
    ]]

    table_styles = [
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("TOPPADDING",    (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LINEBELOW",     (0, 1), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ]

    row_index = 1

    for i, s in enumerate(services):

        # Resolve hours
        hours = 1
        if hours_dict and s.id in hours_dict:
            field = hours_dict[s.id]
            if hasattr(field, "text"):
                try:
                    hours = float(field.text or 1)
                except (ValueError, TypeError):
                    hours = 1
            else:
                try:
                    hours = float(field)
                except (ValueError, TypeError):
                    hours = 1

        if s.price_type == "engång":
            amount     = "-"
            price_text = f"{s.price:.2f} kr"
            row_total  = s.price
        else:
            amount     = f"{hours} h"
            price_text = f"{s.price:.2f} kr/h"
            row_total  = s.price * hours

        mat_lines = []
        if hasattr(s, "materials"):
            for mat_id in s.materials:
                mat = next((m for m in all_materials if m.id == mat_id), None)
                if mat:
                    mat_lines.append(mat)
                    row_total += mat.price

        name_cell_text = f"<b>{s.name}</b>"
        if s.description:
            name_cell_text += f"<br/><font size=8 color='#555555'>  {s.description}</font>"

        bg = colors.HexColor("#f5f5f5") if i % 2 == 0 else colors.white
        table_styles.append(("BACKGROUND", (0, row_index), (-1, row_index), bg))

        table_data.append([
            Paragraph(name_cell_text, style_normal),
            Paragraph(amount,         style_normal),
            Paragraph(price_text,     style_normal),
            Paragraph(f"{row_total:.2f} kr", style_normal),
        ])
        row_index += 1

        for mat in mat_lines:
            mat_bg = colors.HexColor("#efefef") if i % 2 == 0 else colors.HexColor("#f9f9f9")
            table_styles.append(("BACKGROUND",    (0, row_index), (-1, row_index), mat_bg))
            table_styles.append(("TOPPADDING",    (0, row_index), (-1, row_index), 2))
            table_styles.append(("BOTTOMPADDING", (0, row_index), (-1, row_index), 2))

            table_data.append([
                Paragraph(f"• {mat.name}", style_mat_sub),
                "", "",
                Paragraph(f"{mat.price:.2f} kr", style_mat_sub)
            ])
            row_index += 1

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle(table_styles))

    elements.append(table)
    elements.append(Spacer(1, 6*mm))

    # ── Discount ──────────────────────────────────────────
    if discount and discount > 0:
        if discount_type == "percent":
            discount_amount = total * (discount / 100)
            elements.append(Paragraph(
                f"Rabatt ({discount:.0f}%): -{discount_amount:.2f} kr",
                style_discount
            ))
        else:
            elements.append(Paragraph(
                f"Rabatt: -{discount:.2f} kr",
                style_discount
            ))
        elements.append(Spacer(1, 2*mm))

    # ── Totals ────────────────────────────────────────────
    moms_pct = settings.get("moms", 25)

    elements.append(Paragraph(f"Summa:  {total:.2f} kr",              style_total_label))
    elements.append(Spacer(1, 1*mm))
    elements.append(Paragraph(f"MOMS ({moms_pct}%):  {moms:.2f} kr",  style_total_label))
    elements.append(Spacer(1, 1*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 1*mm))
    elements.append(Paragraph(f"Totalt:  {total_with_moms:.2f} kr",   style_total_bold))

    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 4*mm))

    # ── Payment terms ─────────────────────────────────────
    elements.append(Paragraph("Betalningsvillkor", style_payment_header))
    elements.append(Spacer(1, 1*mm))
    elements.append(Paragraph(
        settings.get("payment_terms", "30 dagar netto"), style_small
    ))

    if settings.get("payment_info"):
        elements.append(Spacer(1, 1*mm))
        elements.append(Paragraph(settings.get("payment_info", ""), style_small))

    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 2*mm))

    # ── Footer ────────────────────────────────────────────
    elements.append(Paragraph(
        f"{settings.get('company_name','')}  |  "
        f"{settings.get('email','')}  |  "
        f"{settings.get('phone','')}",
        style_footer
    ))

    doc.build(elements)

    return filepath