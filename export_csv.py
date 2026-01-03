"""
CSV export functionality for inventory items.
"""

import csv
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class CSVExporter:
    """Handles exporting inventory items to CSV format."""
    
    @staticmethod
    def export(parent, items):
        """
        Export items to CSV file.
        
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
            "Export to CSV",
            "inventory_export.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'ID', 'Name', 'Category', 'Value', 'Purchase Date',
                    'Notes', 'Photo Path', 'Created At'
                ])
                
                # Write data
                for item in items:
                    writer.writerow(item)
            
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
