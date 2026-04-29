from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from datetime import datetime
import os

from settings import load_settings
from materials import get_materials


def generate_pdf(services, total, moms, total_with_moms, hours_dict=None, discount=0, discount_type=None):

    settings = load_settings()
    all_materials = get_materials()

    filename = f"offert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # 🖼️ LOGO
    if settings.get("logo_path") and os.path.exists(settings["logo_path"]):
        elements.append(Image(settings["logo_path"], width=120, height=60))

    # 🏢 Företag
    elements.append(Paragraph(f"<b>{settings.get('company_name','')}</b>", styles["Normal"]))
    elements.append(Paragraph(settings.get("address",""), styles["Normal"]))
    elements.append(Paragraph(settings.get("phone",""), styles["Normal"]))
    elements.append(Paragraph(settings.get("email",""), styles["Normal"]))

    elements.append(Spacer(1, 20))

    # 🧾 Offert
    offert_nr = datetime.now().strftime("%Y%m%d%H%M")

    elements.append(Paragraph(f"<b>OFFERT #{offert_nr}</b>", styles["Title"]))
    elements.append(Paragraph(f"Datum: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # 📋 TABELL
    data = [["Tjänst", "Antal", "Pris", "Summa"]]

    for s in services:

        # 🔢 timmar per tjänst
        hours = 1
        if hours_dict and s.id in hours_dict:
            hours = hours_dict[s.id]

        if s.price_type == "engång":
            amount = "-"
            price_text = f"{s.price} kr"
            row_total = s.price
        else:
            amount = str(hours)
            price_text = f"{s.price} kr/h"
            row_total = s.price * hours

        # 🧾 namn + beskrivning
        name_text = f"{s.name}"
        if s.description:
            name_text += f"<br/><font size=8>- {s.description}</font>"

        # 📦 material kopplat till tjänst
        if hasattr(s, "materials"):
            for mat_id in s.materials:
                mat = next((m for m in all_materials if m.id == mat_id), None)
                if mat:
                    name_text += f"<br/><font size=8>• {mat.name} ({mat.price} kr)</font>"
                    row_total += mat.price

        data.append([
            Paragraph(name_text, styles["Normal"]),
            amount,
            price_text,
            f"{row_total:.2f} kr"
        ])

        # spacing rad
        data.append(["", "", "", ""])

    table = Table(data, colWidths=[220, 60, 80, 80])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # 💸 RABATT
    if discount > 0:
        if discount_type == "percent":
            elements.append(Paragraph(f"Rabatt ({discount}%): -{(total * discount/100):.2f} kr", styles["Normal"]))
        else:
            elements.append(Paragraph(f"Rabatt: -{discount:.2f} kr", styles["Normal"]))

    # 💰 TOTAL
    elements.append(Paragraph(f"Summa: {total:.2f} kr", styles["Normal"]))
    elements.append(Paragraph(f"MOMS ({settings.get('moms',25)}%): {moms:.2f} kr", styles["Normal"]))
    elements.append(Paragraph(f"<b>Totalt: {total_with_moms:.2f} kr</b>", styles["Heading2"]))

    elements.append(Spacer(1, 30))

    # 💳 Betalning
    elements.append(Paragraph("<b>Betalningsvillkor</b>", styles["Heading3"]))
    elements.append(Paragraph(settings.get("payment_terms", "30 dagar netto"), styles["Normal"]))

    elements.append(Spacer(1, 20))

    # 📞 Footer
    elements.append(Paragraph(
        f"{settings.get('company_name','')} | {settings.get('email','')} | {settings.get('phone','')}",
        styles["Normal"]
    ))

    doc.build(elements)

    return filename