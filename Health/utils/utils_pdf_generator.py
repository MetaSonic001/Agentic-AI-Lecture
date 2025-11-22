from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

def generate_prescription_pdf(extracted_data):
    """
    Generate a prescription PDF from extracted data
    
    Args:
        extracted_data: Dictionary containing patient and prescription info
    
    Returns:
        str: Filename of the generated PDF
    """
    try:
        # Create prescriptions directory
        output_dir = Path('prescriptions')
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        patient_name = extracted_data['patient']['name'].replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{patient_name}_{timestamp}.pdf"
        filepath = output_dir / filename
        
        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12
        )
        
        # Title
        story.append(Paragraph("MEDICAL PRESCRIPTION", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Date
        date_text = f"Date: {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", heading_style))
        
        patient_data = [
            ['Name:', extracted_data['patient']['name']],
            ['Age:', str(extracted_data['patient']['age'])],
            ['Diagnosis:', extracted_data.get('diagnosis', 'N/A')]
        ]
        
        patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Prescription
        story.append(Paragraph("Prescription", heading_style))
        
        if extracted_data.get('prescription'):
            prescription_data = [['Medication', 'Dosage', 'Frequency', 'Duration']]
            
            for med in extracted_data['prescription']:
                prescription_data.append([
                    med.get('medication', 'N/A'),
                    med.get('dosage', 'N/A'),
                    med.get('frequency', 'N/A'),
                    med.get('duration', 'N/A')
                ])
            
            prescription_table = Table(prescription_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            prescription_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
            ]))
            
            story.append(prescription_table)
        else:
            story.append(Paragraph("No prescription items", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Follow-up
        if extracted_data.get('followup'):
            story.append(Paragraph("Follow-up", heading_style))
            followup_text = f"Next appointment: {extracted_data['followup']}"
            story.append(Paragraph(followup_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = """
        <para align=center>
        <font size=8 color="#6b7280">
        This is a computer-generated prescription.<br/>
        Please consult your doctor for any clarifications.
        </font>
        </para>
        """
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Prescription PDF generated: {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Failed to generate prescription PDF: {str(e)}")
        return None