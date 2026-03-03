from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from typing import List, Dict, Any


def generate_report_pdf(url: str, report: Dict[str, Any]) -> BytesIO:
    """
    Generate a PDF report from the analysis results.
    
    Args:
        url: The analyzed URL
        report: The report dictionary containing summary, recommendations, and prioritization
        
    Returns:
        BytesIO object containing the PDF content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=6
    )
    
    # Title
    story.append(Paragraph("Web Page Quality Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # URL and Date
    info_data = [
        ['URL:', url],
        ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    info_table = Table(info_data, colWidths=[1.2*inch, 4.3*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Summary
    story.append(Paragraph("Summary", heading_style))
    story.append(Paragraph(report.get('summary', 'No summary available'), body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Recommendations
    if report.get('recommendations'):
        story.append(Paragraph("Recommendations", heading_style))
        for recommendation in report['recommendations']:
            story.append(Paragraph(f"• {recommendation}", body_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Prioritization
    prioritization = report.get('prioritization', {})
    
    if prioritization.get('critical'):
        story.append(Paragraph("Critical Issues", heading_style))
        story.append(Paragraph("The following issues require immediate attention:", body_style))
        for issue in prioritization['critical']:
            if isinstance(issue, dict):
                story.append(Paragraph(f"• [{issue.get('type', 'Unknown')}] {issue.get('message', 'No message')}", body_style))
            else:
                story.append(Paragraph(f"• {issue}", body_style))
        story.append(Spacer(1, 0.15*inch))
    
    if prioritization.get('warning'):
        story.append(Paragraph("Warnings", heading_style))
        story.append(Paragraph("These issues may impact user experience or performance:", body_style))
        for issue in prioritization['warning']:
            if isinstance(issue, dict):
                story.append(Paragraph(f"• [{issue.get('type', 'Unknown')}] {issue.get('message', 'No message')}", body_style))
            else:
                story.append(Paragraph(f"• {issue}", body_style))
        story.append(Spacer(1, 0.15*inch))
    
    if prioritization.get('info'):
        story.append(Paragraph("Information", heading_style))
        story.append(Paragraph("General information and suggestions:", body_style))
        for issue in prioritization['info']:
            if isinstance(issue, dict):
                story.append(Paragraph(f"• [{issue.get('type', 'Unknown')}] {issue.get('message', 'No message')}", body_style))
            else:
                story.append(Paragraph(f"• {issue}", body_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
