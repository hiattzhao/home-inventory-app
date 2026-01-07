"""
CSV import functionality for inventory items.
"""

import csv
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class CSVImporter:
    """Handles importing inventory items from CSV format."""

    @staticmethod
    def import_csv(parent):
        """
        Import items from CSV file.

        Args:
            parent: Parent widget (MainWindow) with db attribute

        Returns:
            Number of items imported, or -1 on failure
        """
        # Get file path
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Import from CSV",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not file_path:
            return 0

        try:
            imported_count = 0
            errors = []
            duplicates = []

            with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate header
                if not reader.fieldnames:
                    QMessageBox.warning(
                        parent,
                        "Invalid CSV",
                        "The CSV file is empty or has no headers.",
                    )
                    return -1

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 (after header)
                    try:
                        # Extract fields from CSV
                        name = row.get("Name", "").strip()
                        category = row.get("Category", "").strip()
                        value = row.get("Value", "0").strip()
                        purchase_date = row.get("Purchase Date", "").strip()
                        notes = row.get("Notes", "").strip()
                        photo_path = row.get("Photo Path", "").strip()
                        location = row.get("Location", "").strip()

                        # Validate required fields
                        if not name:
                            errors.append(f"Row {row_num}: Name is required")
                            continue

                        # Convert value to float
                        try:
                            value_float = float(value) if value else 0.0
                        except ValueError:
                            errors.append(f"Row {row_num}: Invalid value '{value}'")
                            continue

                        # Check for duplicates in database
                        # A duplicate is an item with same name, category, purchase_date, and location
                        existing_items = parent.db.get_all_items()
                        is_duplicate = False
                        for existing_item in existing_items:
                            existing_name = existing_item[1]
                            existing_category = existing_item[2]
                            existing_date = existing_item[4] or ""
                            existing_location = (
                                existing_item[8] if len(existing_item) > 8 else ""
                            )

                            if (
                                existing_name.lower() == name.lower()
                                and existing_category.lower() == category.lower()
                                and existing_date == purchase_date
                                and (existing_location or "").lower()
                                == location.lower()
                            ):
                                is_duplicate = True
                                duplicates.append(
                                    f"Row {row_num}: '{name}' (Category: {category}, Date: {purchase_date})"
                                )
                                break

                        if is_duplicate:
                            continue

                        # Add item to database
                        item_id = parent.db.add_item(
                            name=name,
                            category=category or None,
                            value=value_float,
                            purchase_date=purchase_date or None,
                            notes=notes or None,
                            photo_path=photo_path or None,
                            location=location or None,
                        )

                        if item_id:
                            # Handle multiple photos if they're comma-separated
                            if photo_path:
                                photo_paths = [p.strip() for p in photo_path.split(",")]
                                for idx, path in enumerate(photo_paths):
                                    if path:
                                        parent.db.add_photo(item_id, path, "", idx)

                            imported_count += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        continue

            # Show result message
            message_parts = [f"Successfully imported {imported_count} item(s)."]

            if duplicates:
                message_parts.append(f"Skipped {len(duplicates)} duplicate(s):")
                duplicate_summary = "\n".join(duplicates[:10])
                if len(duplicates) > 10:
                    duplicate_summary += (
                        f"\n... and {len(duplicates) - 10} more duplicates"
                    )
                message_parts.append(duplicate_summary)

            if errors:
                message_parts.append(f"Errors encountered:")
                error_summary = "\n".join(errors[:10])
                if len(errors) > 10:
                    error_summary += f"\n... and {len(errors) - 10} more errors"
                message_parts.append(error_summary)

            full_message = "\n\n".join(message_parts)

            if duplicates or errors:
                QMessageBox.warning(
                    parent,
                    "Import Complete with Issues",
                    full_message,
                )
            else:
                QMessageBox.information(
                    parent,
                    "Import Successful",
                    full_message + f"\nfrom:\n{file_path}",
                )

            return imported_count

        except Exception as e:
            QMessageBox.critical(
                parent, "Import Failed", f"Failed to import data:\n{str(e)}"
            )
            return -1
