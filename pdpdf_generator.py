import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Circle, Rect, Path
from PIL import Image as PILImage, ImageDraw, ImageOps

def make_circular_photo(photo_path: str, size: int = 120) -> str:
    """Rasmni yuklab, uni doira shakliga keltirib vaqtinchalik saqlaydi."""
    try:
        img = PILImage.open(photo_path).convert("RGBA")
        # Kvadrat shaklida qirqib olish (crop)
        min_dim = min(img.size)
        left = (img.width - min_dim) / 2
        top = (img.height - min_dim) / 2
        right = (img.width + min_dim) / 2
        bottom = (img.height + min_dim) / 2
        img = img.crop((left, top, right, bottom))
        img = img.resize((size, size), PILImage.Resampling.LANCZOS)

        # Dumaloq maska yaratish
        mask = PILImage.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        # Doira qilib qirqish
        circular_img = PILImage.new('RGBA', (size, size), (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask=mask)

        # Vaqtinchalik PNG fayl sifatida saqlash
        temp_circle_path = f"{photo_path}_circle.png"
        circular_img.save(temp_circle_path, "PNG")
        return temp_circle_path
    except Exception as e:
        print(f"Rasmga ishlov berishda xatolik: {e}")
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

    # Ranglar palitrasi
    PRIMARY_COLOR = colors.HexColor("#1A365D")  # To'q ko'k
    SECONDARY_COLOR = colors.HexColor("#2B6CB0")
    TEXT_DARK = colors.HexColor("#2D3748")
    BG_LIGHT = colors.HexColor("#F7FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Uslublar (Styles)
    name_style = ParagraphStyle(
        'NameStyle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=4
    )

    prof_style = ParagraphStyle(
        'ProfStyle',
        fontName='Helvetica',
        fontSize=12,
        leading=15,
        textColor=SECONDARY_COLOR,
        spaceAfter=15
    )

    section_title = ParagraphStyle(
        'SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=4
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK
    )

    # --- CHAP USTUN (Profil, Rasm va Aloqa) ---
    left_flow = []

    # 1. Rasm (Doira)
    photo_p = data.get("photo_path")
    if photo_p and os.path.exists(photo_p):
        circ_path = make_circular_photo(photo_p, size=110)
        if os.path.exists(circ_path):
            img_obj = Image(circ_path, width=100, height=100)
            left_flow.append(img_obj)
            left_flow.append(Spacer(1, 15))

    # 2. Aloqa ma'lumotlari
    left_flow.append(Paragraph("<b>ALOQA</b>", section_title))
    left_flow.append(Paragraph(f"<b>Tel:</b><br/>{data.get('phone', '-')}", body_style))
    left_flow.append(Spacer(1, 4))
    left_flow.append(Paragraph(f"<b>Email:</b><br/>{data.get('email', '-')}", body_style))
    left_flow.append(Spacer(1, 4))
    left_flow.append(Paragraph(f"<b>Manzil:</b><br/>{data.get('location', '-')}", body_style))
    
    if data.get("salary"):
        left_flow.append(Spacer(1, 4))
        left_flow.append(Paragraph(f"<b>Kutilayotgan maosh:</b><br/>{data.get('salary')}", body_style))

    # 3. Tillar
    if data.get("languages"):
        left_flow.append(Spacer(1, 10))
        left_flow.append(Paragraph("<b>TILLAR</b>", section_title))
        left_flow.append(Paragraph(data.get("languages"), body_style))


    # --- O'NG USTUN (Asosiy ma'lumotlar) ---
    right_flow = []

    # 1. Ism va Kasb
    right_flow.append(Paragraph(data.get("full_name", "Ism kiritilmadi"), name_style))
    if data.get("profession"):
        right_flow.append(Paragraph(data.get("profession"), prof_style))

    # 2. Profil / Haqida
    if data.get("about"):
        right_flow.append(Paragraph("<b>MEN HAQIMDA</b>", section_title))
        right_flow.append(Paragraph(data.get("about"), body_style))
        right_flow.append(Spacer(1, 8))

    # 3. Ish Tajribasi
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
        right_flow.append(Paragraph("<i>Ish tajribasi kiritilmagan</i>", body_style))

    right_flow.append(Spacer(1, 8))

    # 4. Ta'lim
    right_flow.append(Paragraph("<b>TA'LIM</b>", section_title))
    right_flow.append(Paragraph(data.get("education", "-"), body_style))
    right_flow.append(Spacer(1, 8))

    # 5. Ko'nikmalar
    right_flow.append(Paragraph("<b>KO'NIKMALAR</b>", section_title))
    right_flow.append(Paragraph(data.get("skills", "-"), body_style))


    # --- IKKI USTUNNI JADVALGA JOYLASH ---
    main_table = Table(
        [[left_flow, right_flow]],
        colWidths=[170, 385]  # Chap ustun: 170pt, O'ng ustun: 385pt
    )

    main_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, 0), BG_LIGHT),  # Chap ustun fon rangi
        ('PADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (0, 0), (0, 0), 15),
        ('LEFTPADDING', (1, 0), (1, 0), 15),
        ('LINEAFTER', (0, 0), (0, 0), 1, BORDER_COLOR),  # O'rtadagi ajratuvchi chiziq
    ]))

    doc.build([main_table])

    # Vaqtinchalik doira shaklidagi rasmni tozalash
    if photo_p:
        circ_p = f"{photo_p}_circle.png"
        if os.path.exists(circ_p):
            os.remove(circ_p)
