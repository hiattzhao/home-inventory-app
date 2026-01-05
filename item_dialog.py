"""
Item dialog for adding and editing inventory items.
"""

import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QDoubleSpinBox,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
)
from PyQt6.QtCore import QDate, Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from styles import Styles


class ItemDialog(QDialog):
    """Dialog for adding or editing inventory items."""

    def __init__(
        self,
        parent=None,
        categories=None,
        locations=None,
        item_data=None,
        default_category=None,
        default_date=None,
        default_location=None,
    ):
        """
        Initialize the item dialog.

        Args:
            parent: Parent widget
            categories: List of available categories
            locations: List of available locations
            item_data: Data for editing (None for new item)
            default_category: Last used category to pre-select
            default_date: Last used purchase date to pre-select
            default_location: Last used location to pre-select
        """
        super().__init__(parent)
        self.categories = categories or []
        self.locations = locations or []
        self.item_data = item_data
        self.default_category = default_category
        self.default_date = default_date
        self.default_location = default_location
        self.photos = []  # List of photo paths
        self.photo_ids = []  # List of photo IDs from database (for editing)
        self.is_edit_mode = item_data is not None

        self.setWindowTitle("Edit Item" if self.is_edit_mode else "Add Item")
        self.setMinimumWidth(600)
        self.setWindowIcon(QIcon("icon.png"))

        # Apply dialog stylesheet (Disabled for OS default theme)
        # self.setStyleSheet(Styles.get_dialog_stylesheet())

        self.setup_ui()

        if self.is_edit_mode:
            self.populate_fields()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Form layout for input fields
        form_layout = QFormLayout()

        # Name field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name")
        form_layout.addRow("Name*:", self.name_input)

        # Category dropdown with add button
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(self.categories)
        if (
            self.default_category
            and self.default_category in self.categories
            and not self.is_edit_mode
        ):
            self.category_combo.setCurrentText(self.default_category)
        self.category_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        category_layout.addWidget(self.category_combo)

        self.add_category_btn = QPushButton("+")
        self.add_category_btn.setMaximumWidth(30)
        self.add_category_btn.setToolTip("Add new category")
        self.add_category_btn.clicked.connect(self.add_new_category)
        category_layout.addWidget(self.add_category_btn)

        form_layout.addRow("Category*:", category_layout)

        # Location dropdown with add button
        location_layout = QHBoxLayout()
        self.location_input = QComboBox()
        self.location_input.setEditable(True)
        self.location_input.addItem("")  # Blank option for optional location
        self.location_input.addItems(self.locations)
        if (
            self.default_location
            and self.default_location in self.locations
            and not self.is_edit_mode
        ):
            self.location_input.setCurrentText(self.default_location)
        self.location_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        location_layout.addWidget(self.location_input)

        self.add_location_btn = QPushButton("+")
        self.add_location_btn.setMaximumWidth(30)
        self.add_location_btn.setToolTip("Add new location")
        self.add_location_btn.clicked.connect(self.add_new_location)
        location_layout.addWidget(self.add_location_btn)

        form_layout.addRow("Location:", location_layout)

        # Value field
        self.value_input = QDoubleSpinBox()
        self.value_input.setPrefix("$ ")
        self.value_input.setMaximum(999999.99)
        self.value_input.setDecimals(2)
        self.value_input.setValue(0.00)
        form_layout.addRow("Value*:", self.value_input)

        # Purchase date field
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)

        # Use default_date if provided, otherwise use current date
        if self.default_date and not self.is_edit_mode:
            self.date_input.setDate(self.default_date)
        else:
            self.date_input.setDate(QDate.currentDate())

        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Purchase Date:", self.date_input)

        # Notes field
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(
            "Enter additional notes such as serial number (optional)"
        )
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

        # Photo gallery section
        photo_layout = QVBoxLayout()
        photo_label = QLabel("Photos:")
        photo_layout.addWidget(photo_label)

        # Photo list widget
        self.photo_list = QListWidget()
        self.photo_list.setIconSize(QSize(100, 100))
        self.photo_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.photo_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.photo_list.setSpacing(10)
        self.photo_list.setMinimumHeight(150)
        self.photo_list.setMaximumHeight(200)
        self.photo_list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )  # Enable multi-selection
        photo_layout.addWidget(self.photo_list)

        # Photo buttons
        photo_button_layout = QHBoxLayout()
        self.add_photos_btn = QPushButton("Add Photos")
        self.add_photos_btn.clicked.connect(self.add_photos)
        self.remove_photo_btn = QPushButton("Remove Selected")
        self.remove_photo_btn.clicked.connect(self.remove_selected_photo)
        self.remove_photo_btn.setEnabled(False)

        # Enable/disable remove button based on selection
        self.photo_list.itemSelectionChanged.connect(
            lambda: self.remove_photo_btn.setEnabled(
                len(self.photo_list.selectedItems()) > 0
            )
        )

        photo_button_layout.addWidget(self.add_photos_btn)
        photo_button_layout.addWidget(self.remove_photo_btn)
        photo_button_layout.addStretch()
        photo_layout.addLayout(photo_button_layout)

        layout.addLayout(photo_layout)

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setDefault(True)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_fields(self):
        """Populate fields with existing item data."""
        if not self.item_data:
            return

        # item_data format: (id, name, category, value, purchase_date, notes, photo_path, created_at)
        self.name_input.setText(self.item_data[1])

        # Set category
        category_index = self.category_combo.findText(self.item_data[2])
        if category_index >= 0:
            self.category_combo.setCurrentIndex(category_index)

        self.value_input.setValue(float(self.item_data[3]))

        # Set purchase date
        if self.item_data[4]:
            date = QDate.fromString(self.item_data[4], "yyyy-MM-dd")
            if date.isValid():
                self.date_input.setDate(date)

        self.notes_input.setPlainText(self.item_data[5] or "")

        # Set location
        if len(self.item_data) > 8:
            location_val = self.item_data[8] or ""
            if location_val:
                # If location not in list, add it temporarily (might be an old entry)
                if self.location_input.findText(location_val) < 0:
                    self.location_input.addItem(location_val)
                self.location_input.setCurrentText(location_val)

        # Load photos from database
        if hasattr(self.parent(), "db"):
            item_id = self.item_data[0]
            photos = self.parent().db.get_item_photos(item_id)
            for photo in photos:
                # photo format: (id, item_id, photo_path, caption, display_order, created_at)
                self.photo_ids.append(photo[0])
                self.photos.append(photo[2])
                self.add_photo_to_list(photo[2])

        # Fallback: load old single photo if exists
        if self.item_data[6] and not self.photos:
            self.photos.append(self.item_data[6])
            self.add_photo_to_list(self.item_data[6])

    def add_photos(self):
        """Open file dialog to select multiple photos."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Photos",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)",
        )

        if file_paths:
            # Create photos directory if it doesn't exist
            photos_dir = "photos"
            if not os.path.exists(photos_dir):
                os.makedirs(photos_dir)

            for file_path in file_paths:
                # Copy photo to photos directory preserving original filename
                original_filename = os.path.basename(file_path)
                new_path = os.path.join(photos_dir, original_filename)

                # If file already exists, add a counter suffix
                if os.path.exists(new_path):
                    base_name, ext = os.path.splitext(original_filename)
                    counter = 1
                    while os.path.exists(new_path):
                        new_filename = f"{base_name}_{counter}{ext}"
                        new_path = os.path.join(photos_dir, new_filename)
                        counter += 1

                try:
                    shutil.copy2(file_path, new_path)
                    self.photos.append(new_path)
                    self.add_photo_to_list(new_path)
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to copy photo {os.path.basename(file_path)}: {str(e)}",
                    )

    def add_photo_to_list(self, photo_path):
        """Add a photo to the list widget with thumbnail."""
        if os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap)
                item = QListWidgetItem(icon, os.path.basename(photo_path))
                item.setData(Qt.ItemDataRole.UserRole, photo_path)
                self.photo_list.addItem(item)

    def remove_selected_photo(self):
        """Remove the selected photo from the list."""
        selected_items = self.photo_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            photo_path = item.data(Qt.ItemDataRole.UserRole)
            if photo_path in self.photos:
                self.photos.remove(photo_path)
            row = self.photo_list.row(item)
            self.photo_list.takeItem(row)

    def add_new_category(self):
        """Add a new custom category."""
        from PyQt6.QtWidgets import QInputDialog

        # Always show blank textbox for new category
        category_name, ok = QInputDialog.getText(
            self, "Add New Category", "Enter category name:", text=""
        )

        if ok and category_name.strip():
            category_name = category_name.strip()

            # Check if category already exists
            if category_name in self.categories:
                QMessageBox.information(
                    self,
                    "Category Exists",
                    f"The category '{category_name}' already exists.",
                )
                # Set it as current
                index = self.category_combo.findText(category_name)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                return

            # Add to database (parent window should have db reference)
            if hasattr(self.parent(), "db"):
                success = self.parent().db.add_category(category_name)
                if success:
                    # Add to local list and combo box
                    self.categories.append(category_name)
                    self.categories.sort()

                    # Refresh combo box
                    current_selection = self.category_combo.currentText()
                    self.category_combo.clear()
                    self.category_combo.addItems(self.categories)

                    # Set the new category as current
                    index = self.category_combo.findText(category_name)
                    if index >= 0:
                        self.category_combo.setCurrentIndex(index)

                    QMessageBox.information(
                        self, "Success", f"Category '{category_name}' has been added."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to add category '{category_name}'. It may already exist.",
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Cannot add category: Database connection not available.",
                )

    def add_new_location(self):
        """Add a new custom location."""
        from PyQt6.QtWidgets import QInputDialog

        # Always show blank textbox for new location
        location_name, ok = QInputDialog.getText(
            self, "Add New Location", "Enter location name:", text=""
        )

        if ok and location_name.strip():
            location_name = location_name.strip()

            if location_name in self.locations:
                QMessageBox.information(
                    self,
                    "Location Exists",
                    f"The location '{location_name}' already exists.",
                )
                index = self.location_input.findText(location_name)
                if index >= 0:
                    self.location_input.setCurrentIndex(index)
                return

            if hasattr(self.parent(), "db"):
                success = self.parent().db.add_location(location_name)
                if success:
                    self.locations.append(location_name)
                    self.locations.sort()

                    # Refresh combo box
                    current_selection = self.location_input.currentText()
                    self.location_input.clear()
                    self.location_input.addItems(self.locations)

                    # Set the new location as current
                    index = self.location_input.findText(location_name)
                    if index >= 0:
                        self.location_input.setCurrentIndex(index)

                    QMessageBox.information(
                        self, "Success", f"Location '{location_name}' has been added."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to add location '{location_name}'. It may already exist.",
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Cannot add location: Database connection not available.",
                )

    def accept(self):
        """Validate and accept the dialog."""
        # Validate required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an item name.")
            self.name_input.setFocus()
            return

        # Allow zero-value items; only disallow negative values
        if self.value_input.value() < 0:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter a valid non-negative value (0 or greater).",
            )
            self.value_input.setFocus()
            return

        super().accept()

    def get_data(self):
        """
        Get the form data.

        Returns:
            Dictionary containing form data
        """
        return {
            "name": self.name_input.text().strip(),
            "category": self.category_combo.currentText(),
            "value": self.value_input.value(),
            "purchase_date": self.date_input.date().toString("yyyy-MM-dd"),
            "notes": self.notes_input.toPlainText().strip(),
            "location": self.location_input.currentText().strip(),
            "photo_path": (
                self.photos[0] if self.photos else ""
            ),  # For backward compatibility
            "photos": self.photos,  # New: list of all photos
        }
