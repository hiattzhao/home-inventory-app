"""
Search dialog for filtering inventory items.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QLabel,
    QDoubleSpinBox,
    QDateEdit,
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QIcon
from styles import Styles


class SearchDialog(QDialog):
    """Dialog for searching and filtering inventory items."""

    def __init__(self, parent=None, categories=None, locations=None):
        """
        Initialize the search dialog.

        Args:
            parent: Parent widget
            categories: List of available categories
            locations: List of available locations
        """
        super().__init__(parent)
        self.categories = categories or []
        self.locations = locations or []

        self.setWindowTitle("Search & Filter Items")
        self.setMinimumWidth(450)
        self.setWindowIcon(QIcon("icon.png"))

        # Apply dialog stylesheet (Disabled for OS default theme)
        # self.setStyleSheet(Styles.get_dialog_stylesheet())

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Form layout for search fields
        form_layout = QFormLayout()

        # Name search
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Search by name...")
        form_layout.addRow("Name:", self.name_input)

        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.addItems(self.categories)
        form_layout.addRow("Category:", self.category_combo)

        # Location dropdown
        self.location_combo = QComboBox()
        self.location_combo.addItem("All")
        self.location_combo.addItems(self.locations)
        form_layout.addRow("Location:", self.location_combo)

        # Value range
        value_layout = QHBoxLayout()
        self.min_value_input = QDoubleSpinBox()
        self.min_value_input.setPrefix("$ ")
        self.min_value_input.setMaximum(999999.99)
        self.min_value_input.setDecimals(2)
        self.min_value_input.setSpecialValueText("No minimum")

        self.max_value_input = QDoubleSpinBox()
        self.max_value_input.setPrefix("$ ")
        self.max_value_input.setMaximum(999999.99)
        self.max_value_input.setDecimals(2)
        self.max_value_input.setValue(999999.99)
        self.max_value_input.setSpecialValueText("No maximum")

        value_layout.addWidget(self.min_value_input)
        value_layout.addWidget(QLabel("to"))
        value_layout.addWidget(self.max_value_input)
        form_layout.addRow("Value Range:", value_layout)

        # Date range
        date_layout = QHBoxLayout()
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.start_date_input.setSpecialValueText("No start date")
        self.start_date_input.setDate(QDate(2000, 1, 1))
        self.start_date_input.clearMinimumDate()

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        self.end_date_input.setDate(QDate.currentDate())

        date_layout.addWidget(self.start_date_input)
        date_layout.addWidget(QLabel("to"))
        date_layout.addWidget(self.end_date_input)
        form_layout.addRow("Purchase Date:", date_layout)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.clear_btn = QPushButton("Clear Filters")
        self.clear_btn.clicked.connect(self.clear_filters)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.accept)
        self.search_btn.setDefault(True)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def clear_filters(self):
        """Clear all filter fields."""
        self.name_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.location_combo.setCurrentIndex(0)
        self.min_value_input.setValue(0)
        self.max_value_input.setValue(999999.99)
        self.start_date_input.setDate(QDate(2000, 1, 1))
        self.end_date_input.setDate(QDate.currentDate())

    def get_filters(self):
        """
        Get the search filters.

        Returns:
            Dictionary containing filter criteria
        """
        location_val = self.location_combo.currentText()
        filters = {
            "name": self.name_input.text().strip(),
            "category": self.category_combo.currentText(),
            "location": "" if location_val == "All" else location_val,
            "min_value": (
                None
                if self.min_value_input.value() == 0
                else self.min_value_input.value()
            ),
            "max_value": (
                None
                if self.max_value_input.value() == 999999.99
                else self.max_value_input.value()
            ),
            "start_date": (
                ""
                if self.start_date_input.date() == QDate(2000, 1, 1)
                else self.start_date_input.date().toString("yyyy-MM-dd")
            ),
            "end_date": self.end_date_input.date().toString("yyyy-MM-dd"),
        }
        return filters
