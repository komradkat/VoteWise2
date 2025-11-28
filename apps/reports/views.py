from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .utils import get_election_data, generate_charts, generate_narrative_report
from apps.elections.models import Election

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import io
import base64
import re

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def generate_election_report(request, election_id):
    """
    Generates a PDF report for the given election.
    """
    # Fetch data
    data = get_election_data(election_id)
    if not data:
        return HttpResponse("Election not found", status=404)
        
    election = data['election']
    
    # Generate assets
    charts = generate_charts(data)
    narrative = generate_narrative_report(data)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=20))
    styles.add(ParagraphStyle(name='Justify', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceAfter=12, leading=14))
    styles.add(ParagraphStyle(name='Disclaimer', parent=styles['Normal'], textColor=colors.gray, fontSize=8, spaceAfter=12))
    
    story = []
    
    # Title
    story.append(Paragraph(f"Election Report: {election.name}", styles['CenterTitle']))
    
    # Meta Info
    story.append(Paragraph(f"<b>Status:</b> {election.status}", styles['Normal']))
    story.append(Paragraph(f"<b>Date Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Turnout Section
    story.append(Paragraph("Turnout Statistics", styles['Heading2']))
    data_table = [
        ['Eligible Voters', str(data['eligible_voters'])],
        ['Ballots Cast', str(data['ballots_cast'])],
        ['Turnout Percentage', f"{data['turnout_percentage']}%"]
    ]
    t = Table(data_table, colWidths=[3*inch, 2*inch], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 24))
    
    # AI Narrative Section
    story.append(Paragraph("AI-Generated Narrative Analysis", styles['Heading2']))
    
    # Simple markdown-to-reportlab formatting
    # Replace bold **text** with <b>text</b>
    formatted_narrative = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', narrative)
    
    for line in formatted_narrative.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#'):
            # Handle headers
            header_level = len(line.split()[0]) # Count #s
            text = line.lstrip('#').strip()
            if header_level == 1:
                story.append(Paragraph(text, styles['Heading2']))
            elif header_level == 2:
                story.append(Paragraph(text, styles['Heading3']))
            else:
                story.append(Paragraph(text, styles['Heading4']))
        elif line.startswith('- '):
             # Bullet points
             story.append(Paragraph(f"• {line[2:]}", styles['Justify']))
        else:
            story.append(Paragraph(line, styles['Justify']))
            
    story.append(Spacer(1, 24))
    story.append(PageBreak())
    
    # Results & Charts Section
    story.append(Paragraph("Detailed Results & Visualizations", styles['Heading2']))
    
    for position, graphic_base64 in charts.items():
        story.append(Paragraph(f"Position: {position}", styles['Heading3']))
        
        # Decode base64 image
        img_data = base64.b64decode(graphic_base64)
        img_buffer = io.BytesIO(img_data)
        img = Image(img_buffer)
        
        # Resize to fit page width roughly
        img.drawHeight = 4*inch
        img.drawWidth = 6.5*inch
        
        story.append(img)
        story.append(Spacer(1, 12))
        
        # Add table of results for this position
        candidates = data['results'][position]
        res_data = [['Candidate', 'Party', 'Votes', '%']]
        for c in candidates:
            res_data.append([
                c['name'], 
                c['party'], 
                str(c['votes']), 
                f"{c['percentage']:.1f}%"
            ])
            
        t = Table(res_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 24))
        
    doc.build(story)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="election_report_{election_id}.pdf"'
    return response
