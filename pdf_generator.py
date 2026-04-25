from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from datetime import datetime
import os

from settings import load_settings


def generate_pdf(services, total, moms, total_with_moms, hours):

    settings = load_settings()

    filename = f"offert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    #LOGO
    if settings["logo_path"] and os.path.exists(settings["logo_path"]):
        elements.append(Image(settings["logo_path"], width=120, height=60))

    #Företagsinfo
    elements.append(Paragraph(f"<b>{settings['company_name']}</b>", styles["Normal"]))
    elements.append(Paragraph(settings["address"], styles["Normal"]))
    elements.append(Paragraph(settings["phone"], styles["Normal"]))
    elements.append(Paragraph(settings["email"], styles["Normal"]))

    elements.append(Spacer(1, 20))

    #Offert info
    offert_nr = datetime.now().strftime("%Y%m%d%H%M")

    elements.append(Paragraph(f"<b>OFFERT #{offert_nr}</b>", styles["Title"]))
    elements.append(Paragraph(f"Datum: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    #TABELL DATA
    data = [["Tjänst", "Antal", "Pris", "Summa"]]

    #Dela upp tjänster
    engang_services = [s for s in services if s.price_type == "engång"]
    tim_services = [s for s in services if s.price_type == "timme"]

    #Funktion för sektioner
    def add_section(title, service_list):
        if not service_list:
            return

        # 🔹 Sektionstitel
        data.append([title, "", "", ""])

        for s in service_list:

            if s.price_type == "engång":
                amount = "-"
                price_text = f"{s.price} kr"
                row_total = s.price
            else:
                amount = str(hours)
                price_text = f"{s.price} kr/h"
                row_total = s.price * hours

            #Namn + beskrivning
            name_text = f"{s.name}\n- {s.description}" if s.description else s.name

            data.append([
                name_text,
                amount,
                price_text,
                f"{row_total:.2f} kr"
            ])

            # ➕ spacing
            data.append(["", "", "", ""])

    #KÖR SEKTIONER (UTANFÖR FUNKTIONEN!)
    add_section("Engångspriser", engang_services)
    add_section("Timpris", tim_services)

    #TABELL
    table = Table(data, colWidths=[200, 60, 80, 80])

    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        # Sektionstitlar (gör dem bold-ish)
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        # Align
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),

        # Padding (VIKTIG för luft)
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    #TOTALS
    elements.append(Paragraph(f"Summa: {total:.2f} kr", styles["Normal"]))
    elements.append(Paragraph(f"MOMS ({settings.get('moms',25)}%): {moms:.2f} kr", styles["Normal"]))
    elements.append(Paragraph(f"<b>Totalt: {total_with_moms:.2f} kr</b>", styles["Heading2"]))

    elements.append(Spacer(1, 30))

    #Betalningsvillkor (dynamisk)
    elements.append(Paragraph("<b>Betalningsvillkor</b>", styles["Heading3"]))
    elements.append(Paragraph(settings.get("payment_terms", ""), styles["Normal"]))

    elements.append(Spacer(1, 20))

    #Betalningsinfo
    if settings.get("payment_info"):
        elements.append(Paragraph("<b>Betalningsinformation</b>", styles["Heading3"]))
        elements.append(Paragraph(settings["payment_info"], styles["Normal"]))
        elements.append(Spacer(1, 20))

    #Footer
    elements.append(Paragraph(
        f"{settings['company_name']} | {settings['email']} | {settings['phone']}",
        styles["Normal"]
    ))

    doc.build(elements)

    return filename