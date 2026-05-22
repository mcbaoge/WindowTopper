FLUENT_STYLE = """
/* Fluent Design System - Light Theme */
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
    color: #1a1a1a;
}

QMainWindow {
    background-color: #f3f3f3;
}

/* Title Bar */
#titleBar {
    background-color: #f3f3f3;
    border-bottom: 1px solid #e5e5e5;
    padding: 0px;
    min-height: 32px;
}

#titleBar QLabel {
    font-size: 11px;
    color: #666666;
    padding-left: 12px;
}

/* Navigation Sidebar */
#navPanel {
    background-color: #f3f3f3;
    border-right: 1px solid #e5e5e5;
    min-width: 48px;
    max-width: 48px;
}

/* Tree Widget - Fluent ListView style */
QTreeWidget {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    alternate-background-color: #fafafa;
    outline: none;
    show-decoration-selected: 1;
}

QTreeWidget::item {
    padding: 8px 8px;
    min-height: 36px;
    border-bottom: 1px solid #f0f0f0;
}

QTreeWidget::item:selected {
    background-color: #e5f0fa;
    color: #1a1a1a;
    border: none;
}

QTreeWidget::item:hover {
    background-color: #f0f0f0;
}

/* Header */
QHeaderView::section {
    background-color: #f3f3f3;
    color: #333333;
    font-size: 11px;
    font-weight: 600;
    padding: 8px 8px;
    border: none;
    border-bottom: 1px solid #d1d1d1;
    border-right: 1px solid #e5e5e5;
    text-transform: uppercase;
}

QHeaderView::section:hover {
    background-color: #e5e5e5;
}

/* Buttons - Fluent style */
QPushButton {
    background-color: #ffffff;
    color: #1a1a1a;
    border: 1px solid #d1d1d1;
    border-radius: 3px;
    padding: 6px 16px;
    min-height: 24px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #e5e5e5;
    border-color: #bebebe;
}

QPushButton:pressed {
    background-color: #d1d1d1;
    border-color: #999999;
}

QPushButton:disabled {
    background-color: #f0f0f0;
    color: #bebebe;
    border-color: #e5e5e5;
}

#accentButton {
    background-color: #0078d4;
    color: #ffffff;
    border: 1px solid #0078d4;
    font-weight: 600;
}

#accentButton:hover {
    background-color: #106ebe;
    border-color: #106ebe;
}

#accentButton:pressed {
    background-color: #005a9e;
    border-color: #005a9e;
}

/* Toggle Button */
QPushButton#toggleBtn {
    background-color: transparent;
    border: 1px solid #d1d1d1;
    border-radius: 12px;
    padding: 4px 16px;
    min-width: 60px;
}

QPushButton#toggleBtn:checked {
    background-color: #0078d4;
    color: #ffffff;
    border-color: #0078d4;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #bebebe;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

QCheckBox::indicator:hover {
    border-color: #0078d4;
}

/* Scrollbar - Fluent style */
QScrollBar:vertical {
    width: 6px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #c1c1c1;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #a1a1a1;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 6px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #c1c1c1;
    border-radius: 3px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #a1a1a1;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #f3f3f3;
    border-top: 1px solid #e5e5e5;
    font-size: 11px;
    color: #666666;
    padding: 4px 12px;
}

/* Tooltip */
QToolTip {
    background-color: #ffffff;
    color: #1a1a1a;
    border: 1px solid #d1d1d1;
    border-radius: 2px;
    padding: 6px 10px;
    font-size: 12px;
}

/* Search Box */
QLineEdit#searchBox {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 24px;
}

QLineEdit#searchBox:focus {
    border-color: #0078d4;
}

/* Labels */
QLabel#sectionTitle {
    font-size: 20px;
    font-weight: 600;
    color: #1a1a1a;
    padding: 8px 0px;
}

QLabel#countLabel {
    font-size: 11px;
    color: #888888;
}

/* Separator */
QFrame#separator {
    background-color: #e5e5e5;
    max-height: 1px;
}
"""

FLUENT_DARK_STYLE = """
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
    color: #ffffff;
}

QMainWindow {
    background-color: #1e1e1e;
}

#titleBar {
    background-color: #1e1e1e;
    border-bottom: 1px solid #333333;
    padding: 0px;
    min-height: 32px;
}

#titleBar QLabel {
    font-size: 11px;
    color: #999999;
    padding-left: 12px;
}

#navPanel {
    background-color: #1e1e1e;
    border-right: 1px solid #333333;
    min-width: 48px;
    max-width: 48px;
}

QTreeWidget {
    background-color: #252525;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    alternate-background-color: #2a2a2a;
    outline: none;
    show-decoration-selected: 1;
    color: #e0e0e0;
}

QTreeWidget::item {
    padding: 8px 8px;
    min-height: 36px;
    border-bottom: 1px solid #333333;
}

QTreeWidget::item:selected {
    background-color: #3d3d3d;
    color: #ffffff;
    border: none;
}

QTreeWidget::item:hover {
    background-color: #333333;
}

QHeaderView::section {
    background-color: #2a2a2a;
    color: #999999;
    font-size: 11px;
    font-weight: 600;
    padding: 8px 8px;
    border: none;
    border-bottom: 1px solid #3d3d3d;
    border-right: 1px solid #333333;
}

QHeaderView::section:hover {
    background-color: #333333;
}

QPushButton {
    background-color: #333333;
    color: #e0e0e0;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 6px 16px;
    min-height: 24px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #404040;
    border-color: #666666;
}

QPushButton:pressed {
    background-color: #505050;
    border-color: #777777;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #555555;
    border-color: #3d3d3d;
}

#accentButton {
    background-color: #0078d4;
    color: #ffffff;
    border: 1px solid #0078d4;
    font-weight: 600;
}

#accentButton:hover {
    background-color: #106ebe;
    border-color: #106ebe;
}

#accentButton:pressed {
    background-color: #005a9e;
    border-color: #005a9e;
}

QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #555555;
    border-radius: 3px;
    background-color: #333333;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #555555;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #777777;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 6px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #555555;
    border-radius: 3px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #777777;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

QStatusBar {
    background-color: #1e1e1e;
    border-top: 1px solid #333333;
    font-size: 11px;
    color: #999999;
    padding: 4px 12px;
}

QToolTip {
    background-color: #333333;
    color: #e0e0e0;
    border: 1px solid #555555;
    border-radius: 2px;
    padding: 6px 10px;
    font-size: 12px;
}

QLineEdit#searchBox {
    background-color: #333333;
    color: #e0e0e0;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 24px;
}

QLineEdit#searchBox:focus {
    border-color: #0078d4;
}

QLabel {
    color: #e0e0e0;
}

QLabel#sectionTitle {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    padding: 8px 0px;
}

QLabel#countLabel {
    font-size: 11px;
    color: #888888;
}

QFrame#separator {
    background-color: #333333;
    max-height: 1px;
}
"""
