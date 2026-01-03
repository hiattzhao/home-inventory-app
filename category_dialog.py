"""
Dialog for configuring item categories.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QLineEdit, QLabel, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class CategoryDialog(QDialog):
    """Dialog for managing inventory categories."""
    
    def __init__(self, parent=None, db=None):
        """
        Initialize the category dialog.
        
        Args:
            parent: Parent widget
            db: Database instance
        """
        super().__init__(parent)
        self.db = db
        
        self.setWindowTitle("Configure Categories")
        self.setMinimumWidth(400)
        self.setWindowIcon(QIcon("icon.png"))
        
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Current Categories:"))
        
        # Category list
        self.category_list = QListWidget()
        layout.addWidget(self.category_list)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Category")
        self.add_btn.clicked.connect(self.add_category)
        
        self.delete_btn = QPushButton("Delete Category")
        self.delete_btn.clicked.connect(self.delete_category)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_categories(self):
        """Load categories from database into the list widget."""
        self.category_list.clear()
        if self.db:
            categories = self.db.get_categories()
            self.category_list.addItems(categories)
    
    def add_category(self):
        """Add a new category."""
        category_name, ok = QInputDialog.getText(
            self, "Add Category", "Enter category name:"
        )
        
        if ok and category_name.strip():
            category_name = category_name.strip()
            if self.db.add_category(category_name):
                self.load_categories()
                # Select the new category
                items = self.category_list.findItems(category_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.category_list.setCurrentItem(items[0])
            else:
                QMessageBox.warning(
                    self, "Error", f"Category '{category_name}' already exists or could not be added."
                )
    
    def delete_category(self):
        """Delete the selected category."""
        selected_items = self.category_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a category to delete.")
            return
        
        category_name = selected_items[0].text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the category '{category_name}'?\n\n"
            "Note: Default categories cannot be deleted, and items in this category will not be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_category(category_name):
                self.load_categories()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not delete category '{category_name}'. It may be a default category."
                )
