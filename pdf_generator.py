os
 reportlab.lib.pagesizes  letter
 reportlab.lib  colors
 reportlab.platypus  SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image
 reportlab.lib.styles  getSampleStyleSheet, ParagraphStyle

 create_resume_pdf(data: , filename:  = ) -> :
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()

    # Stillar
    title_style = ParagraphStyle(
        ,
        parent=styles[],
        fontName=,
        fontSize=24,
        leading=28,
        textColor=colors.HexColor()
    )

    section_heading = ParagraphStyle(
        ,
        parent=styles[],
        fontName=,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor(),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        ,
        parent=styles[],
        fontName=,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor()
    )

    # 1. Rasm mavjud bo'lsa qo'shish
    photo_path = data.get()
     photo_path  os.path.exists(photo_path):
        :
            img = Image(photo_path, width=100, height=100)
            story.append(img)
            story.append(Spacer(1, 10))
        :
            

    # 2. F.I.SH
    story.append(Paragraph(data.get(, ), title_style))
    story.append(Spacer(1, 6))

    # 3. Aloqa ma'lumotlari
    contact_info = f"<b>Tel:</b> {data.get('')} | <b>Email:</b> {data.get('')}"
    story.append(Paragraph(contact_info, body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width=, thickness=1.5, color=colors.HexColor(), spaceAfter=15))

    # 4. Ta'lim
    story.append(Paragraph(, section_heading))
    story.append(Paragraph(data.get(, ), body_style))
    story.append(Spacer(1, 10))

    # 5. Ko'nikmalar
    story.append(Paragraph(, section_heading))
    story.append(Paragraph(data.get(, ), body_style))
    story.append(Spacer(1, 10))

    # 6. Ish tajribasi
    story.append(Paragraph(, section_heading))
    story.append(Paragraph(data.get(, ), body_style))

    doc.build(story)
     filename