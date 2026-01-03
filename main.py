"""
Home Inventory Application - Main Window
A cross-platform desktop application for managing home inventory.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QToolBar,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QLabel,
    QStyle,
    QStyleOptionButton,
    QSizePolicy,
    QCheckBox,
    QMenu,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap

from database import Database
from item_dialog import ItemDialog
from category_dialog import CategoryDialog
from location_dialog import LocationDialog
from search_dialog import SearchDialog
from export_csv import CSVExporter
from export_pdf import PDFExporter
from styles import Styles


class SortableTableWidgetItem(QTableWidgetItem):
    """
    Custom TableWidgetItem that sorts based on a specific value
    rather than the display text.
    """

    def __init__(self, text, sort_value=None):
        super().__init__(text)
        self.sort_value = sort_value if sort_value is not None else text

    def __lt__(self, other):
        try:
            return self.sort_value < other.sort_value
        except TypeError:
            # Fallback for incompatible types
            return str(self.sort_value) < str(other.sort_value)


class CheckBoxHeader(QHeaderView):
    """Custom header with a checkbox in the first column."""

    checkBoxClicked = pyqtSignal(bool)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.isChecked = False
        self.setSectionsClickable(True)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            option = QStyleOptionButton()
            section_rect = QRect(rect)

            # Center the checkbox
            box_width = 16
            box_height = 16
            x = section_rect.x() + (section_rect.width() - box_width) // 2
            y = section_rect.y() + (section_rect.height() - box_height) // 2

            option.rect = QRect(x, y, box_width, box_height)
            option.state = (
                QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
            )

            if self.isChecked:
                option.state |= QStyle.StateFlag.State_On
            else:
                option.state |= QStyle.StateFlag.State_Off

            # Draw white background for the checkbox
            painter.fillRect(option.rect, Qt.GlobalColor.white)

            self.style().drawPrimitive(
                QStyle.PrimitiveElement.PE_IndicatorCheckBox, option, painter
            )

    def mousePressEvent(self, event):
        idx = self.logicalIndexAt(event.pos())
        if idx == 0:
            self.isChecked = not self.isChecked
            self.checkBoxClicked.emit(self.isChecked)
            self.viewport().update()
        else:
            super().mousePressEvent(event)


class MainWindow(QMainWindow):
    """Main application window for Home Inventory."""

    def __init__(self):
        super().__init__()

        # Initialize database
        self.db = Database()
        self.current_items = []
        self.is_filtered = False
        self.last_selected_category = None  # Track last used category
        self.last_selected_date = None  # Track last used date
        self.last_selected_location = None  # Track last used location

        self.setWindowTitle("Home Inventory Manager")
        self.setMinimumSize(1100, 700)
        self.setWindowIcon(QIcon("icon.png"))

        # Apply checkbox styling specifically while keeping OS native for others
        self.setStyleSheet(
            """
            QCheckBox::indicator, QTableWidget::indicator {
                width: 16px;
                height: 16px;
            }
        """
        )

        self.setup_ui()
        self.load_items()
        self.table.horizontalHeader().setSortIndicatorShown(False)

    def setup_ui(self):
        """Set up the user interface."""
        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "",
                "Purchase Date",
                "Name",
                "Category",
                "Location",
                "Notes",
                "Photo",
                "Value",
            ]
        )

        # Table settings
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)  # Enable sorting
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Custom header with checkbox
        header = CheckBoxHeader(Qt.Orientation.Horizontal, self.table)
        header.setSortIndicatorShown(False)
        self.table.setHorizontalHeader(header)
        header.checkBoxClicked.connect(self.toggle_all_selection)

        # Resize columns
        # header = self.table.horizontalHeader()  # No longer needed as we set it above
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Select checkbox
        self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # Purchase Date
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # Category
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )  # Location — size to content
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Notes
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Photo
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Value

        # Double-click to edit
        self.table.doubleClicked.connect(self.edit_item)

        layout.addWidget(self.table)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Status bar
        self.statusBar().showMessage("Ready")

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        export_csv_action = QAction("Export to &CSV", self)
        export_csv_action.setShortcut("Ctrl+E")
        export_csv_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_csv_action)

        export_pdf_action = QAction("Export to &PDF", self)
        export_pdf_action.setShortcut("Ctrl+P")
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        configure_categories_action = QAction("Configure &Categories", self)
        configure_categories_action.triggered.connect(self.configure_categories)
        file_menu.addAction(configure_categories_action)

        configure_locations_action = QAction("Configure &Locations", self)
        configure_locations_action.triggered.connect(self.configure_locations)
        file_menu.addAction(configure_locations_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        # Add item action
        add_action = QAction("Add Item", self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self.add_item)
        toolbar.addAction(add_action)

        # Edit item action
        edit_action = QAction("Edit Item", self)
        edit_action.setShortcut("Ctrl+E")
        edit_action.triggered.connect(self.edit_item)
        toolbar.addAction(edit_action)

        # Delete item action
        delete_action = QAction("Delete Item", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_item)
        toolbar.addAction(delete_action)

        # Search action
        search_action = QAction("Search", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.search_items)
        toolbar.addAction(search_action)

        clear_action = QAction("Clear Filters", self)
        clear_action.triggered.connect(self.clear_filters)
        toolbar.addAction(clear_action)

        # Spacer to push summary to right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Total Items
        self.total_items_label = QLabel("Total Items: 0")
        self.total_items_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                margin-left: 10px;
            }
        """
        )
        toolbar.addWidget(self.total_items_label)

        # Total Photos
        self.total_photos_label = QLabel("Total Photos: 0")
        self.total_photos_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                margin-left: 10px;
            }
        """
        )
        toolbar.addWidget(self.total_photos_label)

        # Total Value
        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_value_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                margin-left: 10px;
            }
        """
        )
        toolbar.addWidget(self.total_value_label)

    def load_items(self, items=None):
        """
        Load items into the table.

        Args:
            items: List of items to display (if None, loads all items)
        """
        if items is None:
            items = self.db.get_all_items()
            self.is_filtered = False
        else:
            self.is_filtered = True

        self.current_items = items

        # Disable sorting while populating
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            # item format: (id, name, category, value, purchase_date, notes, photo_path, created_at)
            # New column order: Purchase Date, Name, Category, Notes, Photo, Value

            # Checkbox (column 0)
            # Use a widget to center the checkbox
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)

            checkbox = QCheckBox()
            checkbox.setChecked(False)
            cell_layout.addWidget(checkbox)

            self.table.setCellWidget(row, 0, cell_widget)

            # Store ID in a hidden item in column 0 for retrieval
            id_item = QTableWidgetItem()
            id_item.setData(Qt.ItemDataRole.UserRole, item[0])
            self.table.setItem(row, 0, id_item)

            # Purchase Date (column 1)
            date_str = item[4] or ""
            date_item = SortableTableWidgetItem(date_str, date_str)
            self.table.setItem(row, 1, date_item)

            # Name (column 2)
            self.table.setItem(row, 2, QTableWidgetItem(item[1]))

            # Category (column 3)
            self.table.setItem(row, 3, QTableWidgetItem(item[2]))

            # Location (column 4)
            location_str = item[8] if len(item) > 8 else ""
            self.table.setItem(row, 4, QTableWidgetItem(location_str or ""))

            # Notes (column 5)
            self.table.setItem(row, 5, QTableWidgetItem(item[5] or ""))

            # Photo count (column 6)
            photo_count = len(self.db.get_item_photos(item[0]))
            if photo_count == 0 and item[6]:  # Fallback for old single photo
                photo_count = 1
            photo_text = (
                f"{photo_count} photo{'s' if photo_count != 1 else ''}"
                if photo_count > 0
                else "No photos"
            )
            self.table.setItem(row, 6, SortableTableWidgetItem(photo_text, photo_count))

            # Value (column 7)
            value_float = float(item[3])
            self.table.setItem(
                row, 7, SortableTableWidgetItem(f"${value_float:,.2f}", value_float)
            )

        # Re-enable sorting
        self.table.setSortingEnabled(True)

        # Update status bar
        status = f"Showing {len(items)} item(s)"
        if self.is_filtered:
            status += " (filtered)"
        self.statusBar().showMessage(status)

        # Update summary header
        total_items = len(items)
        total_value = sum(float(item[3]) for item in items)

        # Calculate total photos
        total_photos = 0
        for item in items:
            photo_count = len(self.db.get_item_photos(item[0]))
            if photo_count == 0 and item[6]:  # Fallback for old single photo
                photo_count = 1
            total_photos += photo_count

        # Update labels
        self.total_items_label.setText(f"Total Items: {total_items}")
        self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")
        self.total_photos_label.setText(f"Total Photos: {total_photos}")

    def toggle_all_selection(self, checked):
        """Toggle all checkboxes in the first column."""
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(checked)

    def add_item(self):
        """Open dialog to add a new item."""
        categories = self.db.get_categories()  # Refresh categories from database

        # Convert last_selected_date string back to QDate if it exists
        default_qdate = None
        if self.last_selected_date:
            from PyQt6.QtCore import QDate

            default_qdate = QDate.fromString(self.last_selected_date, "yyyy-MM-dd")

        locations = self.db.get_locations()
        dialog = ItemDialog(
            self,
            categories=categories,
            locations=locations,
            default_category=self.last_selected_category,
            default_date=default_qdate,
            default_location=self.last_selected_location,
        )

        if dialog.exec():
            data = dialog.get_data()
            self.last_selected_category = data["category"]  # Remember category
            self.last_selected_date = data["purchase_date"]  # Remember date
            self.last_selected_location = data.get("location", "")
            item_id = self.db.add_item(
                data["name"],
                data["category"],
                data["value"],
                data["purchase_date"],
                data["notes"],
                data["photo_path"],
                data["location"],
            )

            if item_id:
                # Save all photos to photos table
                for idx, photo_path in enumerate(data.get("photos", [])):
                    self.db.add_photo(item_id, photo_path, "", idx)

                self.statusBar().showMessage(f"Added item: {data['name']}", 3000)
                self.load_items()

    def edit_item(self):
        """Open dialog to edit the selected item."""
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
            return

        # Get item ID from UserRole data in first column
        item_id = self.table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        item_data = self.db.get_item(item_id)

        if not item_data:
            QMessageBox.warning(self, "Error", "Failed to load item data.")
            return

        categories = self.db.get_categories()  # Refresh categories from database
        locations = self.db.get_locations()
        dialog = ItemDialog(
            self,
            categories=categories,
            locations=locations,
            item_data=item_data,
            default_location=self.last_selected_location,
        )

        if dialog.exec():
            data = dialog.get_data()
            self.last_selected_category = data["category"]  # Remember category
            success = self.db.update_item(
                item_id,
                data["name"],
                data["category"],
                data["value"],
                data["purchase_date"],
                data["notes"],
                data["photo_path"],
                data["location"],
            )

            if success:
                self.last_selected_date = data["purchase_date"]  # Remember date
                self.last_selected_location = data.get("location", "")
                # Update photos: delete old ones and add new ones
                # Get existing photo IDs
                existing_photos = self.db.get_item_photos(item_id)
                existing_photo_paths = [p[2] for p in existing_photos]

                # Delete photos that are no longer in the list
                for photo in existing_photos:
                    if photo[2] not in data.get("photos", []):
                        self.db.delete_photo(photo[0])

                # Add new photos
                for idx, photo_path in enumerate(data.get("photos", [])):
                    if photo_path not in existing_photo_paths:
                        self.db.add_photo(item_id, photo_path, "", idx)

                self.statusBar().showMessage(f"Updated item: {data['name']}", 3000)
                self.load_items()

                # Highlight the edited item
                for row in range(self.table.rowCount()):
                    row_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                    if row_id == item_id:
                        self.table.selectRow(row)
                        item = self.table.item(row, 0)
                        if item:
                            self.table.scrollToItem(item)
                        break

    def delete_item(self):
        """Delete selected item(s)."""
        # First check for checked items
        checked_items = []
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    item = self.table.item(row, 0)
                    if item:
                        item_id = item.data(Qt.ItemDataRole.UserRole)
                        item_name = self.table.item(row, 2).text()
                        checked_items.append((item_id, item_name))

        if checked_items:
            # Multi-delete mode
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete these {len(checked_items)} items?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                success_count = 0
                for item_id, _ in checked_items:
                    if self.db.delete_item(item_id):
                        success_count += 1

                self.statusBar().showMessage(f"Deleted {success_count} items", 3000)
                self.load_items()
            return

        # Fallback to single selection
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select items to delete.")
            return

        # Get item details from UserRole data
        item_id = self.table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        item_name = self.table.item(selected_row, 2).text()  # Name is now in column 2

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{item_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.db.delete_item(item_id)

            if success:
                self.statusBar().showMessage(f"Deleted item: {item_name}", 3000)
                self.load_items()

    def search_items(self):
        """Open search dialog and filter items."""
        categories = self.db.get_categories()  # Refresh categories from database
        locations = self.db.get_locations()
        dialog = SearchDialog(self, categories, locations)

        if dialog.exec():
            filters = dialog.get_filters()
            items = self.db.search_items(
                filters["name"],
                filters["category"],
                filters["min_value"],
                filters["max_value"],
                filters["start_date"],
                filters["end_date"],
                filters.get("location", ""),
            )
            self.load_items(items)

    def clear_filters(self):
        """Clear all filters and show all items."""
        self.load_items()
        self.statusBar().showMessage("Filters cleared", 3000)

    def show_context_menu(self, pos):
        """Show context menu for table items."""
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        # Select the row that was right-clicked
        self.table.selectRow(row)

        menu = QMenu(self)

        edit_action = menu.addAction("Edit Item")
        edit_action.triggered.connect(self.edit_item)

        delete_action = menu.addAction("Delete Item")
        delete_action.triggered.connect(self.delete_item)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def export_csv(self):
        """Export current items to CSV."""
        CSVExporter.export(self, self.current_items)

    def export_pdf(self):
        """Export current items to PDF."""
        PDFExporter.export(self, self.current_items)

    def configure_categories(self):
        """Open the category configuration dialog."""
        dialog = CategoryDialog(self, self.db)
        if dialog.exec():
            # No specific action needed if dialog was just closed
            # but categories are updated in the database by the dialog itself.
            pass

    def configure_locations(self):
        """Open the location configuration dialog."""
        dialog = LocationDialog(self, self.db)
        if dialog.exec():
            # Locations updated in database by dialog
            pass

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Home Inventory Manager",
            "<h2>Home Inventory Manager</h2>"
            "<p>Version 1.0</p>"
            "<p>A cross-platform desktop application for managing your home inventory.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Add, edit, and delete items</li>"
            "<li>Organize by categories and locations</li>"
            "<li>Track values and purchase dates</li>"
            "<li>Attach photos to items</li>"
            "<li>Search and filter items</li>"
            "<li>Export to CSV or PDF</li>"
            "</ul>",
        )

    def closeEvent(self, event):
        """Handle application close event."""
        self.db.close()
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
