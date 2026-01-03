"""
PDF export functionality for inventory items.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class PDFExporter:
    """Handles exporting inventory items to PDF format."""
    
    @staticmethod
    def export(parent, items):
        """
        Export items to PDF file.
        
        Args:
            parent: Parent widget for dialogs
            items: List of item tuples to export
            
        Returns:
            True if export was successful, False otherwise
        """
        if not items:
            QMessageBox.warning(
                parent,
                "No Data",
                "There are no items to export."
            )
            return False
        
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Export to PDF",
            "inventory_export.pdf",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_path:
            return False
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Title
            title = Paragraph("Home Inventory Report", title_style)
            elements.append(title)
            
            # Generation date
            date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            date_para = Paragraph(date_text, styles['Normal'])
            elements.append(date_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary
            summary_text = f"Total Items: {len(items)}"
            total_value = sum(float(item[3]) for item in items)
            summary_text += f" | Total Value: ${total_value:,.2f}"
            summary_para = Paragraph(summary_text, styles['Heading2'])
            elements.append(summary_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Create table data
            table_data = [['Name', 'Category', 'Value', 'Purchase Date', 'Notes']]
            
            for item in items:
                # item format: (id, name, category, value, purchase_date, notes, photo_path, created_at)
                row = [
                    item[1][:30],  # Name (truncated)
                    item[2],  # Category
                    f"${float(item[3]):,.2f}",  # Value
                    item[4] or 'N/A',  # Purchase date
                    (item[5][:50] + '...') if item[5] and len(item[5]) > 50 else (item[5] or '')  # Notes (truncated)
                ]
                table_data.append(row)
            
            # Create table
            table = Table(table_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 1*inch, 2*inch])
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Align value column right
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
            ]))
            
            elements.append(table)
            
            # Add photos section - get photos from photos table if parent has db
            if hasattr(parent, 'db'):
                elements.append(Spacer(1, 0.5*inch))
                photo_title = Paragraph("Item Photos", styles['Heading2'])
                elements.append(photo_title)
                elements.append(Spacer(1, 0.2*inch))
                
                for item in items:
                    item_id = item[0]
                    photos = parent.db.get_item_photos(item_id)
                    
                    # Fallback to old single photo if no photos in photos table
                    if not photos and item[6]:
                        photos = [(None, item_id, item[6], None, 0, None)]
                    
                    if photos:
                        # Add item name
                        item_name = Paragraph(f"<b>{item[1]}</b>", styles['Normal'])
                        elements.append(item_name)
                        elements.append(Spacer(1, 0.1*inch))
                        
                        for photo in photos:
                            photo_path = photo[2]
                            if os.path.exists(photo_path):
                                try:
                                    # Add photo
                                    img = Image(photo_path, width=2*inch, height=2*inch, kind='proportional')
                                    elements.append(img)
                                    elements.append(Spacer(1, 0.2*inch))
                                except Exception as e:
                                    print(f"Error adding photo {photo_path}: {e}")
                        
                        elements.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(elements)
            
            QMessageBox.information(
                parent,
                "Export Successful",
                f"Successfully exported {len(items)} item(s) to:\n{file_path}"
            )
            return True
            
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Export Failed",
                f"Failed to export data:\n{str(e)}"
            )
            return False
