import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_resume_pdf(data: dict, filename: str = "resume.pdf") -> str:
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
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A2B4C")
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2C3E50"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#333333")
    )

    # Ism familiya
    story.append(Paragraph(data.get('full_name', 'F.I.SH'), title_style))
    story.append(Spacer(1, 6))

    # Aloqa ma'lumotlari
    contact_info = f"<b>Tel:</b> {data.get('phone')} | <b>Email:</b> {data.get('email')}"
    story.append(Paragraph(contact_info, body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A2B4C"), spaceAfter=15))

    # Ta'lim
    story.append(Paragraph("TA'LIM", section_heading))
    story.append(Paragraph(data.get('education', '-'), body_style))
    story.append(Spacer(1, 10))

    # Ko'nikmalar
    story.append(Paragraph("KO'NIKMALAR VA KO'NIKMALAR", section_heading))
    story.append(Paragraph(data.get('skills', '-'), body_style))
    story.append(Spacer(1, 10))

    # Ish tajribasi
    story.append(Paragraph("ISH TAJRIBASI", section_heading))
    story.append(Paragraph(data.get('experience', '-'), body_style))

    doc.build(story)
    return filename