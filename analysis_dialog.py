"""
Analysis dialog for viewing inventory data as charts.
Displays pie charts and histograms grouped by category or location.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import backend_pdf  # Force bundling of PDF backend for exports
from matplotlib.figure import Figure
from collections import defaultdict


class AnalysisDialog(QDialog):
    """Dialog for analyzing inventory data with charts."""

    def __init__(self, parent=None, db=None):
        """
        Initialize the analysis dialog.

        Args:
            parent: Parent widget
            db: Database instance
        """
        super().__init__(parent)
        self.db = db
        self.items = []

        self.setWindowTitle("Inventory Analysis")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)  # Set initial size
        self.setWindowIcon(QIcon("icon.png"))

        self.setup_ui()
        self.load_data()
        self.update_chart()  # Display initial chart

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)  # Reduce margins
        layout.setSpacing(8)  # Reduce spacing

        # Control panel
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(6)

        # Chart type selector
        control_layout.addWidget(QLabel("Chart Type:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Pie Chart", "Histogram"])
        self.chart_type_combo.currentIndexChanged.connect(self.update_chart)
        self.chart_type_combo.setMaximumWidth(120)
        control_layout.addWidget(self.chart_type_combo)

        # Grouping selector
        control_layout.addWidget(QLabel("Group By:"))
        self.group_by_combo = QComboBox()
        self.group_by_combo.addItems(["Category", "Location"])
        self.group_by_combo.currentIndexChanged.connect(self.update_chart)
        self.group_by_combo.setMaximumWidth(120)
        control_layout.addWidget(self.group_by_combo)

        control_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_chart)
        control_layout.addWidget(refresh_btn)

        # Export button
        export_btn = QPushButton("Export as PDF")
        export_btn.clicked.connect(self.export_chart)
        control_layout.addWidget(export_btn)

        layout.addLayout(control_layout, 0)  # Don't stretch this

        # Create matplotlib figure with smaller margins
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.figure.subplots_adjust(left=0.08, right=0.95, top=0.90, bottom=0.15)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.canvas, 1)  # Stretch this to fill available space

        self.setLayout(layout)

    def load_data(self):
        """Load inventory data from database."""
        if not self.db:
            QMessageBox.warning(self, "Error", "Database connection not available.")
            return

        try:
            # Fetch all items from database
            self.items = self.db.get_all_items()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load items: {str(e)}")

    def update_chart(self):
        """Update the chart based on selected options."""
        self.figure.clear()

        if not self.items:
            ax = self.figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "No data to display",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=14,
            )
            self.canvas.draw()
            return

        chart_type = self.chart_type_combo.currentText()
        group_by = self.group_by_combo.currentText()

        # Group data
        grouped_data = self.group_data(group_by)

        if chart_type == "Pie Chart":
            self.draw_pie_chart(grouped_data, group_by)
        else:  # Histogram
            self.draw_histogram(grouped_data, group_by)

        self.canvas.draw()

    def group_data(self, group_by):
        """
        Group items by category or location.

        Args:
            group_by: "Category" or "Location"

        Returns:
            Dictionary with group names as keys and total values as values
        """
        grouped = defaultdict(float)

        for item in self.items:
            # item format: (id, name, category, value, purchase_date, notes, photo_path, created_at, location)
            value = float(item[3]) if item[3] else 0.0

            if group_by == "Category":
                key = item[2] if item[2] else "Uncategorized"
            else:  # Location
                key = item[8] if len(item) > 8 and item[8] else "No Location"

            grouped[key] += value

        return dict(sorted(grouped.items()))

    def draw_pie_chart(self, data, group_by):
        """
        Draw a pie chart.

        Args:
            data: Dictionary with group names and values
            group_by: "Category" or "Location"
        """
        ax = self.figure.add_subplot(111)

        labels = list(data.keys())
        values = list(data.values())

        # Filter out zero values for cleaner pie chart
        labels_filtered = [label for label, value in zip(labels, values) if value > 0]
        values_filtered = [value for value in values if value > 0]

        if not values_filtered:
            ax.text(
                0.5,
                0.5,
                "No data to display",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            return

        colors = plt.cm.Set3(range(len(labels_filtered)))
        wedges, texts, autotexts = ax.pie(
            values_filtered,
            labels=labels_filtered,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )

        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontsize(9)
            autotext.set_weight("bold")

        ax.set_title(f"Total Value by {group_by}", fontsize=14, fontweight="bold")

        # Add legend with values below the chart, positioned inside figure
        legend_labels = [
            f"{label}: ${value:,.2f}"
            for label, value in zip(labels_filtered, values_filtered)
        ]
        ax.legend(
            wedges,
            legend_labels,
            title="Groups",
            loc="upper center",
            bbox_to_anchor=(0.5, -0.05),
            ncol=min(4, len(legend_labels)),
            frameon=True,
            fontsize=8,
            title_fontsize=9,
        )

        # Center the pie chart
        ax.set_aspect("equal")

    def draw_histogram(self, data, group_by):
        """
        Draw a histogram.

        Args:
            data: Dictionary with group names and values
            group_by: "Category" or "Location"
        """
        ax = self.figure.add_subplot(111)

        labels = list(data.keys())
        values = list(data.values())

        if not values:
            ax.text(
                0.5,
                0.5,
                "No data to display",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            return

        # Create bar chart (histogram-style)
        colors = plt.cm.Set3(range(len(labels)))
        bars = ax.bar(
            range(len(labels)), values, color=colors, edgecolor="black", linewidth=1.5
        )

        # Add value labels on top of bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${value:,.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

        ax.set_xlabel(group_by, fontsize=11, fontweight="bold")
        ax.set_ylabel("Total Value ($)", fontsize=11, fontweight="bold")
        ax.set_title(f"Total Value by {group_by}", fontsize=14, fontweight="bold")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

        # Add grid for readability
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)

        self.figure.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.15)

    def export_chart(self):
        """Export the current chart as a PDF file."""
        chart_type = self.chart_type_combo.currentText()
        group_by = self.group_by_combo.currentText()
        default_filename = f"inventory_analysis_{group_by.lower()}_{chart_type.lower().replace(' ', '_')}.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chart as PDF",
            default_filename,
            "PDF Files (*.pdf);;All Files (*)",
        )

        if file_path:
            try:
                self.figure.savefig(
                    file_path, format="pdf", dpi=300, bbox_inches="tight"
                )
                QMessageBox.information(
                    self, "Success", f"Chart exported successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export chart:\n{str(e)}")
