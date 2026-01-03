"""
Centralized styles for the Home Inventory Application.
Provides a modern, clean look with consistent colors and spacing.
"""

class Styles:
    # Color Palette - ADA Compliant (WCAG AA)
    PRIMARY_COLOR = "#0056b3"      # Darker Blue for >4.5:1 contrast
    PRIMARY_HOVER = "#004494"      # Hover state
    SECONDARY_COLOR = "#1e7e34"    # Darker Green for >4.5:1 contrast
    ACCENT_COLOR = "#bd2130"       # Darker Red for >4.5:1 contrast
    BACKGROUND_COLOR = "#ffffff"   # White
    SURFACE_COLOR = "#ffffff"      # White
    TEXT_COLOR = "#212529"         # Almost black for max readability
    BORDER_COLOR = "#dee2e6"       # Clear border color
    
    # Fonts
    FONT_FAMILY = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    
    @staticmethod
    def get_main_stylesheet():
        return f"""
            QMainWindow {{
                background-color: {Styles.BACKGROUND_COLOR};
            }}
            
            QWidget {{
                color: {Styles.TEXT_COLOR};
                font-family: {Styles.FONT_FAMILY};
                font-size: 14px;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {Styles.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {Styles.PRIMARY_HOVER};
                border: 2px solid #003d80;
                padding: 6px 14px; /* Adjust padding to separate border */
            }}
            
            QPushButton:pressed {{
                background-color: {Styles.PRIMARY_COLOR};
                padding-top: 10px;
                padding-bottom: 6px;
            }}
            
            QPushButton:disabled {{
                background-color: {Styles.BORDER_COLOR};
                color: #95a5a6;
            }}
            
            /* Tables */
            QTableWidget {{
                background-color: #ffffff;
                alternate-background-color: #fbfbfc;
                border: 1px solid {Styles.BORDER_COLOR};
                border-radius: 8px;
                gridline-color: #f1f2f6;
                selection-background-color: #e1f0fa;
                selection-color: {Styles.TEXT_COLOR};
                outline: none;
                color: {Styles.TEXT_COLOR};
            }}
            
            QHeaderView::section {{
                background-color: #f8f9fa;
                color: {Styles.TEXT_COLOR};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {Styles.BORDER_COLOR};
                font-weight: bold;
                font-size: 13px;
                text-transform: uppercase;
            }}

            QHeaderView::section:vertical {{
                background: #ffffff;
                background-color: #ffffff;
                border: none;
                border-right: 1px solid #dee2e6;
                padding-left: 5px;
            }}

            QTableCornerButton::section {{
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #f1f2f6;
                border-right: 1px solid #dee2e6;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }}
            
            QTableWidget::indicator, QCheckBox::indicator {{
                width: 24px;
                height: 24px;
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
            }}

            QTableWidget::indicator:checked, QCheckBox::indicator:checked {{
                background-color: #6c757d;
                border-color: #6c757d;
                image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
            }}
            
            /* Inputs */
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {{
                background-color: {Styles.SURFACE_COLOR};
                border: 2px solid {Styles.BORDER_COLOR};
                border-radius: 6px;
                padding: 8px;
                selection-background-color: {Styles.PRIMARY_COLOR};
                selection-color: white;
            }}
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {{
                border-color: {Styles.PRIMARY_COLOR};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background-color: #f1f1f1;
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #bdc3c7;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: #95a5a6;
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {Styles.SURFACE_COLOR};
                color: #7f8c8d;
                border-top: 1px solid {Styles.BORDER_COLOR};
            }}
            
            /* Toolbar */
            QToolBar {{
                background-color: {Styles.SURFACE_COLOR};
                border-bottom: 1px solid {Styles.BORDER_COLOR};
                padding: 5px;
                spacing: 10px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border-radius: 4px;
                padding: 6px;
            }}
            
            QToolButton:hover {{
                background-color: #ecf0f1;
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {Styles.SURFACE_COLOR};
                border-bottom: 1px solid {Styles.BORDER_COLOR};
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
            }}
            
            QMenuBar::item:selected {{
                background-color: #ecf0f1;
                color: {Styles.TEXT_COLOR};
            }}
            
            QMenu {{
                background-color: {Styles.SURFACE_COLOR};
                border: 1px solid {Styles.BORDER_COLOR};
                color: {Styles.TEXT_COLOR};
            }}
            
            QMenu::item {{
                padding: 8px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: #ecf0f1;
                color: {Styles.TEXT_COLOR};
            }}
            
            /* ToolTips */
            QToolTip {{
                background-color: {Styles.TEXT_COLOR};
                color: white;
                border: 1px solid {Styles.TEXT_COLOR};
                padding: 4px;
            }}
        """

    @staticmethod
    def get_dialog_stylesheet():
        return f"""
            QDialog {{
                background-color: {Styles.BACKGROUND_COLOR};
            }}
            
            QLabel {{
                color: {Styles.TEXT_COLOR};
                font-weight: 500;
            }}
            
            QGroupBox {{
                background-color: {Styles.SURFACE_COLOR};
                border: 1px solid {Styles.BORDER_COLOR};
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 20px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: {Styles.PRIMARY_COLOR};
                font-weight: bold;
            }}
        """ + Styles.get_main_stylesheet()
