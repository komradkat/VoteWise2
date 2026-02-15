from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .utils import get_election_data, generate_charts, generate_narrative_report
from .decorators import sudo_required
from apps.elections.models import Election, Candidate, Position
from apps.accounts.models import StudentProfile, Course, YearLevel
from apps.administration.models import AuditLog

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
@sudo_required
def reports_hub(request):
    """
    Central hub for generating and downloading system reports.
    Requires password verification. Grants 5-minute sudo mode after verification.
    """
    elections = Election.objects.all().order_by('-start_time')
    return render(request,
                  'reports/reports_hub.html',
                  {'elections': elections})


@user_passes_test(is_admin)
@sudo_required
def generate_election_report(request, election_id):
    """
    Generates a PDF report for the given election.
    Uses sudo mode from Reports Hub verification (5 minutes).
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
    styles.add(
        ParagraphStyle(
            name='CenterTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=20))
    styles.add(
        ParagraphStyle(
            name='Justify',
            parent=styles['Normal'],
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14))
    styles.add(
        ParagraphStyle(
            name='Disclaimer',
            parent=styles['Normal'],
            textColor=colors.gray,
            fontSize=8,
            spaceAfter=12))

    story = []

    # Title
    story.append(
        Paragraph(
            f"Election Report: {
                election.name}",
            styles['CenterTitle']))

    # Meta Info
    story.append(
        Paragraph(f"<b>Status:</b> {election.status}", styles['Normal']))
    story.append(Paragraph(
        f"<b>Date Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Turnout Section
    story.append(Paragraph("Turnout Statistics", styles['Heading2']))
    data_table = [
        ['Eligible Voters', str(data['eligible_voters'])],
        ['Ballots Cast', str(data['ballots_cast'])],
        ['Turnout Percentage', f"{data['turnout_percentage']}%"]
    ]
    t = Table(data_table, colWidths=[3 * inch, 2 * inch], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 24))

    # AI Narrative Section
    story.append(
        Paragraph(
            "AI-Generated Narrative Analysis",
            styles['Heading2']))

    # Simple markdown-to-reportlab formatting
    # Replace bold **text** with <b>text</b>
    formatted_narrative = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', narrative)

    for line in formatted_narrative.split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('#'):
            # Handle headers
            header_level = len(line.split()[0])  # Count #s
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
    story.append(
        Paragraph(
            "Detailed Results & Visualizations",
            styles['Heading2']))

    for position, graphic_base64 in charts.items():
        story.append(Paragraph(f"Position: {position}", styles['Heading3']))

        # Decode base64 image
        img_data = base64.b64decode(graphic_base64)
        img_buffer = io.BytesIO(img_data)
        img = Image(img_buffer)

        # Resize to fit page width roughly
        img.drawHeight = 4 * inch
        img.drawWidth = 6.5 * inch

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

        t = Table(
            res_data,
            colWidths=[
                2.5 * inch,
                1.5 * inch,
                1 * inch,
                1 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 24))

    doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="election_report_{election_id}.pdf"'
    # Set cookie to signal download start (client-side will poll for this)
    response.set_cookie('report_download_started', 'true', max_age=20)
    return response


@user_passes_test(is_admin)
@sudo_required
def generate_voter_demographics_report(request):
    """
    Generates a PDF report for voter demographics.
    Uses sudo mode from Reports Hub verification (5 minutes).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name='CenterTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=20))

    story = []

    # Title
    story.append(
        Paragraph(
            "Voter Demographics & Registration Report",
            styles['CenterTitle']))
    story.append(Paragraph(
        f"<b>Date Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Summary Stats
    total_students = StudentProfile.objects.count()
    verified_students = StudentProfile.objects.filter(
        verification_status='VERIFIED').count()
    pending_students = StudentProfile.objects.filter(
        verification_status='PENDING').count()
    eligible_voters = StudentProfile.objects.filter(
        is_eligible_to_vote=True).count()

    story.append(Paragraph("Registration Summary", styles['Heading2']))

    summary_data = [
        ['Metric', 'Count'],
        ['Total Registered Students', str(total_students)],
        ['Verified Accounts', str(verified_students)],
        ['Pending Verifications', str(pending_students)],
        ['Eligible to Vote', str(eligible_voters)]
    ]

    t = Table(summary_data, colWidths=[3 * inch, 2 * inch], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Breakdown by Course
    story.append(Paragraph("Breakdown by Course", styles['Heading2']))

    course_data = [['Course', 'Total', 'Verified', 'Pending']]
    for course in Course:
        total = StudentProfile.objects.filter(course=course).count()
        verified = StudentProfile.objects.filter(
            course=course, verification_status='VERIFIED').count()
        pending = StudentProfile.objects.filter(
            course=course, verification_status='PENDING').count()
        course_data.append(
            [course.label, str(total), str(verified), str(pending)])

    t_course = Table(
        course_data,
        colWidths=[
            3.5 * inch,
            1 * inch,
            1 * inch,
            1 * inch],
        hAlign='LEFT')
    t_course.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    story.append(t_course)
    story.append(Spacer(1, 20))

    # Breakdown by Year Level
    story.append(Paragraph("Breakdown by Year Level", styles['Heading2']))

    year_data = [['Year Level', 'Total', 'Verified', 'Pending']]
    for year in YearLevel:
        total = StudentProfile.objects.filter(year_level=year).count()
        verified = StudentProfile.objects.filter(
            year_level=year, verification_status='VERIFIED').count()
        pending = StudentProfile.objects.filter(
            year_level=year, verification_status='PENDING').count()
        year_data.append([year.label, str(total), str(verified), str(pending)])

    t_year = Table(
        year_data,
        colWidths=[
            3.5 * inch,
            1 * inch,
            1 * inch,
            1 * inch],
        hAlign='LEFT')
    t_year.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    story.append(t_year)

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="voter_demographics_report.pdf"'
    return response


@user_passes_test(is_admin)
@sudo_required
def generate_audit_log_report(request):
    """
    Generates a PDF report for system audit logs.
    Uses sudo mode from Reports Hub verification (5 minutes).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name='CenterTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=20))

    story = []

    # Title
    story.append(
        Paragraph(
            "System Audit & Security Log",
            styles['CenterTitle']))
    story.append(Paragraph(
        f"<b>Date Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Fetch logs (limit to last 200 for performance in this simple
    # implementation)
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:200]

    data = [['Time', 'User', 'Action', 'Details']]
    for log in logs:
        user_str = log.user.username if log.user else "System"
        # Wrap details text
        details = Paragraph(log.details, styles['Normal'])
        data.append([
            log.timestamp.strftime('%Y-%m-%d %H:%M'),
            user_str,
            log.action,
            details
        ])

    t = Table(
        data,
        colWidths=[
            1.2 * inch,
            1 * inch,
            1.5 * inch,
            3.5 * inch],
        repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    story.append(t)
    doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="audit_log_report.pdf"'
    return response


@user_passes_test(is_admin)
@sudo_required
def generate_candidate_summary_report(request):
    """
    Generates a PDF summary of all candidates.
    Uses sudo mode from Reports Hub verification (5 minutes).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name='CenterTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=20))

    story = []

    # Title
    story.append(Paragraph("Official Candidate List", styles['CenterTitle']))
    story.append(Paragraph(
        f"<b>Date Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    elections = Election.objects.all().order_by('-start_time')

    for election in elections:
        story.append(
            Paragraph(
                f"Election: {
                    election.name}",
                styles['Heading2']))
        story.append(Paragraph(f"Status: {election.status}", styles['Normal']))
        story.append(Spacer(1, 10))

        positions = Position.objects.filter(
            candidates__election=election).distinct().order_by('order_on_ballot')

        if not positions.exists():
            story.append(
                Paragraph(
                    "No candidates registered.",
                    styles['Normal']))
            story.append(Spacer(1, 20))
            continue

        for position in positions:
            story.append(
                Paragraph(
                    f"Position: {
                        position.name}",
                    styles['Heading3']))

            candidates = Candidate.objects.filter(
                election=election, position=position).select_related(
                'student_profile__user', 'partylist')

            c_data = [['Name', 'Party', 'Platform Summary']]
            for c in candidates:
                name = c.student_profile.user.get_full_name()
                party = c.partylist.name if c.partylist else "Independent"
                platform = Paragraph(
                    c.biography[:200] + "..." if c.biography else "No biography provided.", styles['Normal'])
                c_data.append([name, party, platform])

            t = Table(c_data, colWidths=[2 * inch, 1.5 * inch, 3 * inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="candidate_summary_report.pdf"'
    return response
