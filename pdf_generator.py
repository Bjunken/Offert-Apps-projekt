from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from datetime import datetime

from materials import get_materials
from settings import load_settings


def generate_pdf(services, service_hours):

    filename = f"offert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    materials = {m.id: m for m in get_materials()}

    total = 0

    elements.append(Paragraph("<b>OFFERT</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    for s in services:

        elements.append(Paragraph(f"<b>{s.name}</b>", styles["Normal"]))

        if s.price_type == "engång":
            service_total = s.price
            elements.append(Paragraph(f"{s.price} kr", styles["Normal"]))
        else:
            hours = service_hours.get(s.id, 1)
            service_total = s.price * hours
            elements.append(Paragraph(f"{hours}h x {s.price} kr", styles["Normal"]))

        total += service_total

        # 📦 MATERIAL
        if s.materials:
            elements.append(Paragraph("<b>Material:</b>", styles["Normal"]))

            for mid in s.materials:
                if mid in materials:
                    m = materials[mid]
                    elements.append(Paragraph(f"- {m.name} ({m.price} kr)", styles["Normal"]))
                    total += m.price

        elements.append(Spacer(1, 10))

    settings = load_settings()
    moms = total * (settings.get("moms", 25) / 100)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Summa: {total:.2f} kr", styles["Normal"]))
    elements.append(Paragraph(f"MOMS: {moms:.2f} kr", styles["Normal"]))
    elements.append(Paragraph(f"<b>Totalt: {total+moms:.2f} kr</b>", styles["Heading2"]))

    doc.build(elements)

    return filename