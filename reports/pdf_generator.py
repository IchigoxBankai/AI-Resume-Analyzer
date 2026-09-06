import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class PDFReportGenerator:
    @staticmethod
    def generate_report(output_pdf_path, resume_name, ats_score, job_role, skills, missing_skills, suggestions):
        """Generates a professional PDF report containing the resume analysis results."""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Define clean, professional color palette
        primary_color = colors.HexColor("#1A365D")   # Deep Slate Blue
        secondary_color = colors.HexColor("#2B6CB0") # Vibrant Blue
        accent_color = colors.HexColor("#319795")    # Teal Accent
        dark_text = colors.HexColor("#2D3748")       # Charcoal Text
        light_bg = colors.HexColor("#F7FAFC")        # Warm White / Light Grey

        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=primary_color,
            spaceAfter=15
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=secondary_color,
            spaceAfter=20
        )

        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=primary_color,
            spaceBefore=15,
            spaceAfter=8
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10.5,
            textColor=dark_text,
            leading=14,
            spaceAfter=6
        )

        bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=body_style,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=5
        )

        story = []

        # 1. Header Title
        story.append(Paragraph("ResumeAI Analyzer", title_style))
        story.append(Paragraph(f"Analysis Report for: {resume_name}", subtitle_style))
        story.append(Spacer(1, 10))

        # 2. Main Executive Summary / Score Box
        # We put score inside a nice table
        score_text = f"<font size='40' color='{primary_color}'><b>{ats_score}</b></font><font size='16' color='#718096'>/100</font>"
        score_p = Paragraph(score_text, ParagraphStyle('ScoreP', alignment=1)) # Centered
        
        target_role_display = job_role if job_role else "General Assessment (No Role Specified)"
        summary_text = f"<b>Target Job Role:</b> {target_role_display}<br/><br/>This score is calculated based on resume formatting, section structure, contact details availability, and skill alignment with the targeted market profile."
        summary_p = Paragraph(summary_text, body_style)

        score_table_data = [
            [score_p, summary_p]
        ]
        
        score_table = Table(score_table_data, colWidths=[2.0*inch, 5.0*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 20))

        # 3. Detected Skills Section
        story.append(Paragraph("Detected Skills & Capabilities", heading_style))
        if skills:
            skills_joined = ", ".join(skills)
            story.append(Paragraph(skills_joined, body_style))
        else:
            story.append(Paragraph("No major technical or professional skills were programmatically detected. Consider structuring your skill-list explicitly.", body_style))
        story.append(Spacer(1, 15))

        # 4. Target Role Analysis (Missing Keywords)
        if job_role:
            story.append(Paragraph(f"Target Role Gap Analysis ({target_role_display})", heading_style))
            if missing_skills:
                story.append(Paragraph("To optimize your resume for automated applicant tracking workflows, consider incorporating references to the following missing skills/keywords:", body_style))
                for skill in missing_skills:
                    story.append(Paragraph(f"• <b>{skill}</b>", bullet_style))
            else:
                story.append(Paragraph("Excellent matching! The resume contains all the standard keywords required for the designated target role.", body_style))
            story.append(Spacer(1, 15))

        # 5. Improvement Suggestions
        story.append(Paragraph("Actionable Improvement Suggestions", heading_style))
        if suggestions:
            for sug in suggestions:
                story.append(Paragraph(f"• {sug}", bullet_style))
        else:
            story.append(Paragraph("Your resume already satisfies our primary automated review parameters. Ensure your achievements represent quantitative results.", body_style))

        # Build document
        doc.build(story)
        return output_pdf_path
