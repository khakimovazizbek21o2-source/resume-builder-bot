import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage, ImageDraw

def make_circular_photo(photo_path: str, size: int = 120) -> str:
    """Rasmni dumaloq (circle) shaklga keltirish"""
    try:
        img = PILImage.open(photo_path).convert("RGBA")
        min_dim = min(img.size)
        left = (img.width - min_dim) / 2
        top = (img.height - min_dim) / 2
        right = (img.width + min_dim) / 2
        bottom = (img.height + min_dim) / 2
        img = img.crop((left, top, right, bottom))
        img = img.resize((size, size), PILImage.Resampling.LANCZOS)

        mask = PILImage.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        circular_img = PILImage.new('RGBA', (size, size), (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask=mask)

        temp_circle_path = f"{photo_path}_circle.png"
        circular_img.save(temp_circle_path, "PNG")
        return temp_circle_path
    except Exception as e:
        print(f"Rasm xatosi: {e}")
        return photo_path

def create_resume_pdf(data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    PRIMARY_COLOR = colors.HexColor("#1A365D")
    SECONDARY_COLOR = colors.HexColor("#2B6CB0")
    TEXT_DARK = colors.HexColor("#2D3748")
    BG_LIGHT = colors.HexColor("#F7FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    name_style = ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=PRIMARY_COLOR, spaceAfter=4)
    prof_style = ParagraphStyle('Prof', fontName='Helvetica', fontSize=12, leading=15, textColor=SECONDARY_COLOR, spaceAfter=12)
    section_title = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=PRIMARY_COLOR, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=9, leading=13, textColor=TEXT_DARK, spaceAfter=4)
    bold_body = ParagraphStyle('BoldBody', fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=TEXT_DARK)

    # --- CHAP USTUN ---
    left_flow = []

    photo_p = data.get("photo_path")
    if photo_p and os.path.exists(photo_p):
        circ_path = make_circular_photo(photo_p, size=110)
        if os.path.exists(circ_path):
            left_flow.append(Image(circ_path, width=90, height=90))
            left_flow.append(Spacer(1, 10))

    left_flow.append(Paragraph("<b>ALOQA</b>", section_title))
    left_flow.append(Paragraph(f"<b>Tel:</b><br/>{data.get('phone', '-')}", body_style))
    left_flow.append(Spacer(1, 4))
    left_flow.append(Paragraph(f"<b>Email:</b><br/>{data.get('email', '-')}", body_style))
    left_flow.append(Spacer(1, 4))
    left_flow.append(Paragraph(f"<b>Manzil:</b><br/>{data.get('location', '-')}", body_style))
    
    if data.get("salary"):
        left_flow.append(Spacer(1, 4))
        left_flow.append(Paragraph(f"<b>Kutilgan maosh:</b><br/>{data.get('salary')}", body_style))

    if data.get("languages"):
        left_flow.append(Spacer(1, 10))
        left_flow.append(Paragraph("<b>TILLAR</b>", section_title))
        left_flow.append(Paragraph(data.get("languages"), body_style))

    # --- O'NG USTUN ---
    right_flow = []

    right_flow.append(Paragraph(data.get("full_name", "Ism kiritilmadi"), name_style))
    if data.get("profession"):
        right_flow.append(Paragraph(data.get("profession"), prof_style))

    if data.get("about"):
        right_flow.append(Paragraph("<b>PROFIL / HAQIDA</b>", section_title))
        right_flow.append(Paragraph(data.get("about"), body_style))
        right_flow.append(Spacer(1, 6))

    right_flow.append(Paragraph("<b>ISH TAJRIBASI</b>", section_title))
    if data.get("has_experience"):
        comp = data.get("exp_company", "")
        pos = data.get("exp_position", "")
        period = data.get("exp_period", "")
        duties = data.get("exp_duties", "")

        right_flow.append(Paragraph(f"<b>{pos}</b> — <i>{comp}</i>", bold_body))
        right_flow.append(Paragraph(f"<font color='#718096'><i>{period}</i></font>", body_style))
        if duties:
            right_flow.append(Paragraph(duties, body_style))
    else:
        right_flow.append(Paragraph("<i>Ish tajribasi mavjud emas</i>", body_style))

    right_flow.append(Spacer(1, 6))

    right_flow.append(Paragraph("<b>TA'LIM</b>", section_title))
    right_flow.append(Paragraph(data.get("education", "-"), body_style))
    right_flow.append(Spacer(1, 6))

    right_flow.append(Paragraph("<b>KO'NIKMALAR</b>", section_title))
    right_flow.append(Paragraph(data.get("skills", "-"), body_style))

    # JADVALGA JOYLASHTIRISH
    main_table = Table(
        [[left_flow, right_flow]],
        colWidths=[160, 395]
    )

    main_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, 0), BG_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('LINEAFTER', (0, 0), (0, 0), 1, BORDER_COLOR),
    ]))

    doc.build([main_table])

    if photo_p:
        circ_p = f"{photo_p}_circle.png"
        if os.path.exists(circ_p):
            os.remove(circ_p)