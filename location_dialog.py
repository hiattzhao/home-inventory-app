"""
Dialog for configuring inventory locations (rooms).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QLabel, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class LocationDialog(QDialog):
    """Dialog for managing inventory locations."""
    
    def __init__(self, parent=None, db=None):
        """
        Initialize the location dialog.
        
        Args:
            parent: Parent widget
            db: Database instance
        """
        super().__init__(parent)
        self.db = db
        
        self.setWindowTitle("Configure Locations")
        self.setMinimumWidth(400)
        self.setWindowIcon(QIcon("icon.png"))
        
        self.setup_ui()
        self.load_locations()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Current Locations (Rooms):"))
        
        # Location list
        self.location_list = QListWidget()
        layout.addWidget(self.location_list)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Location")
        self.add_btn.clicked.connect(self.add_location)
        
        self.delete_btn = QPushButton("Delete Location")
        self.delete_btn.clicked.connect(self.delete_location)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_locations(self):
        """Load locations from database into the list widget."""
        self.location_list.clear()
        if self.db:
            locations = self.db.get_locations()
            self.location_list.addItems(locations)
    
    def add_location(self):
        """Add a new location."""
        location_name, ok = QInputDialog.getText(
            self, "Add Location", "Enter room/location name:"
        )
        
        if ok and location_name.strip():
            location_name = location_name.strip()
            if self.db.add_location(location_name):
                self.load_locations()
                # Select the new location
                items = self.location_list.findItems(location_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.location_list.setCurrentItem(items[0])
            else:
                QMessageBox.warning(
                    self, "Error", f"Location '{location_name}' already exists or could not be added."
                )
    
    def delete_location(self):
        """Delete the selected location."""
        selected_items = self.location_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a location to delete.")
            return
        
        location_name = selected_items[0].text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the location '{location_name}'?\n\n"
            "Note: Default locations cannot be deleted, and items in this location will not be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_location(location_name):
                self.load_locations()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not delete location '{location_name}'. It may be a default room."
                )
