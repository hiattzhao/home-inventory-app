"""
Item dialog for adding and editing inventory items.
"""

import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QDoubleSpinBox, QListWidget, QListWidgetItem, QInputDialog
)
from PyQt6.QtCore import QDate, Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from styles import Styles


class ItemDialog(QDialog):
    """Dialog for adding or editing inventory items."""
    
    def __init__(self, parent=None, categories=None, item_data=None, default_category=None):
        """
        Initialize the item dialog.
        
        Args:
            parent: Parent widget
            categories: List of available categories
            item_data: Tuple of existing item data for editing (optional)
            default_category: Category to select by default (optional)
        """
        super().__init__(parent)
        self.categories = categories or []
        self.item_data = item_data
        self.default_category = default_category
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
        if self.default_category and self.default_category in self.categories and not self.is_edit_mode:
            self.category_combo.setCurrentText(self.default_category)
        self.category_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        category_layout.addWidget(self.category_combo)
        
        self.add_category_btn = QPushButton("+")
        self.add_category_btn.setMaximumWidth(30)
        self.add_category_btn.setToolTip("Add new category")
        self.add_category_btn.clicked.connect(self.add_new_category)
        category_layout.addWidget(self.add_category_btn)
        
        form_layout.addRow("Category*:", category_layout)
        
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
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Purchase Date:", self.date_input)
        
        # Notes field
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter additional notes (optional)")
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
        self.photo_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Enable multi-selection
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
            lambda: self.remove_photo_btn.setEnabled(len(self.photo_list.selectedItems()) > 0)
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
        
        # Load photos from database
        if hasattr(self.parent(), 'db'):
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
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
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
                        f"Failed to copy photo {os.path.basename(file_path)}: {str(e)}"
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
        
        # Get the current text from the combo box (in case user typed something)
        current_text = self.category_combo.currentText().strip()
        
        # Show input dialog
        category_name, ok = QInputDialog.getText(
            self,
            "Add New Category",
            "Enter category name:",
            text=current_text
        )
        
        if ok and category_name.strip():
            category_name = category_name.strip()
            
            # Check if category already exists
            if category_name in self.categories:
                QMessageBox.information(
                    self,
                    "Category Exists",
                    f"The category '{category_name}' already exists."
                )
                # Set it as current
                index = self.category_combo.findText(category_name)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                return
            
            # Add to database (parent window should have db reference)
            if hasattr(self.parent(), 'db'):
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
                        self,
                        "Success",
                        f"Category '{category_name}' has been added."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to add category '{category_name}'. It may already exist."
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Cannot add category: Database connection not available."
                )
    
    def accept(self):
        """Validate and accept the dialog."""
        # Validate required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an item name.")
            self.name_input.setFocus()
            return
        
        if self.value_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid value greater than 0.")
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
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText(),
            'value': self.value_input.value(),
            'purchase_date': self.date_input.date().toString("yyyy-MM-dd"),
            'notes': self.notes_input.toPlainText().strip(),
            'photo_path': self.photos[0] if self.photos else "",  # For backward compatibility
            'photos': self.photos  # New: list of all photos
        }
