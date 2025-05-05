"""
Stylesheet definitions for the BitNet.cpp desktop application.
"""

# Light theme stylesheet
LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
}

QLabel {
    color: #333333;
}

QPushButton {
    background-color: #0078d7;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #0063b1;
}

QPushButton:pressed {
    background-color: #004e8c;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

QComboBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px;
    background-color: white;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QTextEdit, QTextBrowser {
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: white;
}

QGroupBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 1ex;
    padding-top: 1ex;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #e6e6e6;
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 12px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
}

QTabBar::tab:hover {
    background-color: #f0f0f0;
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d7;
}

QSlider::groove:horizontal {
    border: 1px solid #cccccc;
    height: 8px;
    background: #f0f0f0;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #0078d7;
    border: 1px solid #0078d7;
    width: 18px;
    margin: -2px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #0063b1;
    border: 1px solid #0063b1;
}

QSpinBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px;
    background-color: white;
}
"""

# Dark theme stylesheet
DARK_STYLESHEET = """
QMainWindow {
    background-color: #2d2d2d;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #e0e0e0;
}

QLabel {
    color: #e0e0e0;
}

QPushButton {
    background-color: #0078d7;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #0063b1;
}

QPushButton:pressed {
    background-color: #004e8c;
}

QPushButton:disabled {
    background-color: #555555;
    color: #888888;
}

QComboBox {
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
    background-color: #3d3d3d;
    color: #e0e0e0;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QTextEdit, QTextBrowser {
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #3d3d3d;
    color: #e0e0e0;
}

QGroupBox {
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 1ex;
    padding-top: 1ex;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
    color: #e0e0e0;
}

QTabWidget::pane {
    border: 1px solid #555555;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #3d3d3d;
    border: 1px solid #555555;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 12px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
}

QTabBar::tab:hover {
    background-color: #454545;
}

QProgressBar {
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d7;
}

QSlider::groove:horizontal {
    border: 1px solid #555555;
    height: 8px;
    background: #3d3d3d;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #0078d7;
    border: 1px solid #0078d7;
    width: 18px;
    margin: -2px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #0063b1;
    border: 1px solid #0063b1;
}

QSpinBox {
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
    background-color: #3d3d3d;
    color: #e0e0e0;
}
"""
