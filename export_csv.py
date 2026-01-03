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
            QMessageBox.warning(parent, "No Data", "There are no items to export.")
            return False

        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Export to CSV",
            "inventory_export.csv",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not file_path:
            return False

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                # Use minimal quoting so fields with commas (multiple photos) are quoted
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

                # Write header
                writer.writerow(
                    [
                        "ID",
                        "Name",
                        "Category",
                        "Value",
                        "Purchase Date",
                        "Notes",
                        "Photo Path",
                        "Created At",
                        "Location",
                    ]
                )

                # Write data
                for item in items:
                    item_id = item[0]

                    # Collect photo paths: prefer photos table, fallback to legacy photo_path column
                    photo_paths = []
                    try:
                        rows = parent.db.get_item_photos(item_id)
                        photo_paths = [r[2] for r in rows] if rows else []
                    except Exception:
                        photo_paths = []

                    if not photo_paths:
                        # legacy single photo column at index 6
                        legacy = item[6] if len(item) > 6 else ""
                        photo_field = legacy or ""
                    else:
                        # join multiple photo paths with commas; csv will quote field when needed
                        photo_field = ",".join(photo_paths)

                    # Build row explicitly to ensure correct ordering and fallback safety
                    row = [
                        item[0],  # ID
                        item[1] if len(item) > 1 else "",
                        item[2] if len(item) > 2 else "",
                        item[3] if len(item) > 3 else "",
                        item[4] if len(item) > 4 else "",
                        item[5] if len(item) > 5 else "",
                        photo_field,
                        item[7] if len(item) > 7 else "",
                        item[8] if len(item) > 8 else "",
                    ]

                    writer.writerow(row)

            QMessageBox.information(
                parent,
                "Export Successful",
                f"Successfully exported {len(items)} item(s) to:\n{file_path}",
            )
            return True

        except Exception as e:
            QMessageBox.critical(
                parent, "Export Failed", f"Failed to export data:\n{str(e)}"
            )
            return False
