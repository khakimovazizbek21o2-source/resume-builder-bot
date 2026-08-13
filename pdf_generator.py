import os
from PIL import Image, ImageDraw, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Circle

def make_circular_image(image_path, output_path):
    """Rasmni mukammal aylana (dumaloq) shaklga keltirib saqlash"""
    try:
        img = Image.open(image_path).convert("RGBA")
        size = min(img.size)
        
        # Rasmni kvadrat shaklida qirqish
        img = ImageOps.fit(img, (size, size), Image.Resampling.LANCZOS)
        
        # Maska yaratish
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        img.putalpha(mask)
        img.save(output_path, format="PNG")
        return True
    except Exception as e:
        print(f"Rasmga ishlov berishda xatolik: {e}")
        return False

def create_resume_pdf(data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Stil belgilashlar
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1A1A1A')
    )

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#555555')
    )

    contact_left_style = ParagraphStyle(
        'ContactLeft',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#333333')
    )

    contact_right_style = ParagraphStyle(
        'ContactRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#333333')
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#222222'),
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#444444')
    )

    # 1. HEADER (Ism va Kasb)
    full_name = data.get("full_name", "ISM FAMILIYA").upper()
    profession = data.get("profession", "MUTAXASSISLIK").upper()

    story.append(Paragraph(full_name, name_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(profession, title_style))
    story.append(Spacer(1, 15))

    # 2. ALOQA MA'LUMOTLARI VA RASM
    phone = data.get("phone", "")
    email = data.get("email", "")
    salary = data.get("salary", "")
    location = data.get("location", "Toshkent, O'zbekiston")

    left_contacts = f"<b>Tel:</b> {phone}<br/><b>Email:</b> {email}"
    right_contacts = f"<b>Maosh:</b> {salary if salary else 'Kelishiladi'}<br/><b>Manzil:</b> {location}"

    photo_path = data.get("photo_path")
    circle_photo_path = "temp_photos/circle_temp.png"
    
    if photo_path and os.path.exists(photo_path) and make_circular_image(photo_path, circle_photo_path):
        img_element = RLImage(circle_photo_path, width=80, height=80)
    else:
        d = Drawing(80, 80)
        d.add(Circle(40, 40, 38, fillColor=colors.HexColor('#E0E0E0'), strokeColor=colors.HexColor('#B0B0B0'), strokeWidth=1))
        img_element = d

    header_table_data = [
        [
            Paragraph(left_contacts, contact_left_style),
            img_element,
            Paragraph(right_contacts, contact_right_style)
        ]
    ]

    header_table = Table(header_table_data, colWidths=[200, 100, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#D0D0D0')),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#D0D0D0')),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 12))

    # 3. PROFIL / HAQIDA
    story.append(Paragraph("<b>PROFIL</b>", section_heading))
    story.append(Paragraph("<hr color='#D0D0D0' size='1'/>", body_style))
    story.append(Spacer(1, 4))
    
    about_text = data.get("about") or "O'z sohasi bo'yicha yuqori malakali, mas'uliyatli va natijaga yo'naltirilgan mutaxassis."
    story.append(Paragraph(about_text, body_style))
    story.append(Spacer(1, 15))

    # 4. IKKI USTUNLI QISM
    left_content = []
    
    # Ko'nikmalar
    left_content.append(Paragraph("<b>KO'NIKMALAR</b>", section_heading))
    left_content.append(Paragraph("<hr color='#D0D0D0' size='1'/>", body_style))
    left_content.append(Spacer(1, 4))
    skills = data.get("skills", "").split(",")
    for skill in skills:
        if skill.strip():
            left_content.append(Paragraph(f"• {skill.strip()}", body_style))
    left_content.append(Spacer(1, 15))

    # Ta'lim
    left_content.append(Paragraph("<b>TA'LIM</b>", section_heading))
    left_content.append(Paragraph("<hr color='#D0D0D0' size='1'/>", body_style))
    left_content.append(Spacer(1, 4))
    education = data.get("education", "")
    left_content.append(Paragraph(f"• {education}", body_style))
    left_content.append(Spacer(1, 15))

    # Chet tillari
    if data.get("languages"):
        left_content.append(Paragraph("<b>CHET TILLARI</b>", section_heading))
        left_content.append(Paragraph("<hr color='#D0D0D0' size='1'/>", body_style))
        left_content.append(Spacer(1, 4))
        langs = data.get("languages", "").split(",")
        for lang in langs:
            if lang.strip():
                left_content.append(Paragraph(f"• {lang.strip()}", body_style))

    # O'ng ustun (Ish tajribasi)
    right_content = []
    right_content.append(Paragraph("<b>ISH TAJRIBASI</b>", section_heading))
    right_content.append(Paragraph("<hr color='#D0D0D0' size='1'/>", body_style))
    right_content.append(Spacer(1, 6))

    if data.get("has_experience"):
        company = data.get("exp_company", "")
        position = data.get("exp_position", "")
        period = data.get("exp_period", "")
        duties = data.get("exp_duties", "")

        exp_text = f"<b>{position}</b> — <i>{company}</i><br/>" \
                   f"<font color='#777777'>📅 {period}</font><br/><br/>" \
                   f"{duties}"
        right_content.append(Paragraph(f"• {exp_text}", body_style))
    else:
        right_content.append(Paragraph("• Ish tajribasi kiritilmagan.", body_style))

    # Asosiy jadval
    main_table_data = [[left_content, right_content]]
    main_table = Table(main_table_data, colWidths=[200, 310])
    main_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (1,0), (1,0), 15),
        ('RIGHTPADDING', (0,0), (0,0), 10),
        ('LINEBEFORE', (1,0), (1,0), 0.5, colors.HexColor('#D0D0D0')),
    ]))

    story.append(main_table)
    doc.build(story)

    # Vaqtinchalik aylanali rasmni o'chirish
    if os.path.exists(circle_photo_path):
        os.remove(circle_photo_path)