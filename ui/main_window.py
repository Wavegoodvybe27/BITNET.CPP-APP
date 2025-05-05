"""
Main window for the BitNet.cpp desktop application.
"""
import os
import sys
import platform
import webbrowser
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QAction, QMenu, QToolBar,
    QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from ui.model_management import ModelManagementWidget
from ui.chat_interface import ChatInterfaceWidget
from ui.inference_interface import InferenceInterfaceWidget
from ui.settings_dialog import SettingsDialog
import config

class MainWindow(QMainWindow):
    """Main window for the BitNet.cpp desktop application."""
    def __init__(self, model_manager, inference_engine):
        """Initialize the main window."""
        super().__init__()
        
        # Store references to model manager and inference engine
        self.model_manager = model_manager
        self.inference_engine = inference_engine
        
        # Set window properties
        self.setWindowTitle("BitNet.cpp Desktop")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create header
        self.create_header()
        
        # Create tab widget
        self.create_tabs()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
    
    def create_header(self):
        """Create header with title and description."""
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("BitNet.cpp Desktop")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Description
        description_label = QLabel("Run BitNet models locally on your CPU")
        description_label.setStyleSheet("font-size: 14px;")
        description_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(description_label)
        
        # Note
        note_label = QLabel("All processing is done locally - no cloud services or GPU required")
        note_label.setStyleSheet("font-size: 12px; color: gray;")
        note_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(note_label)
        
        self.layout.addLayout(header_layout)
    
    def create_tabs(self):
        """Create tab widget with tabs for different functionality."""
        self.tabs = QTabWidget()
        
        # Model management tab
        self.model_management_widget = ModelManagementWidget(self.model_manager)
        self.tabs.addTab(self.model_management_widget, "Model Management")
        
        # Chat interface tab
        self.chat_interface_widget = ChatInterfaceWidget(self.model_manager, self.inference_engine)
        self.tabs.addTab(self.chat_interface_widget, "Chat")
        
        # Inference interface tab
        self.inference_interface_widget = InferenceInterfaceWidget(self.model_manager, self.inference_engine)
        self.tabs.addTab(self.inference_interface_widget, "Inference")
        
        self.layout.addWidget(self.tabs)
    
    def create_menu_bar(self):
        """Create menu bar with menus and actions."""
        # File menu
        file_menu = self.menuBar().addMenu("File")
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("Help")
        
        # Documentation action
        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(lambda: webbrowser.open("https://github.com/microsoft/BitNet"))
        help_menu.addAction(docs_action)
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create toolbar with quick access buttons."""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        
        # Refresh models action
        refresh_action = QAction("Refresh Models", self)
        refresh_action.triggered.connect(self.refresh_models)
        self.toolbar.addAction(refresh_action)
        
        self.toolbar.addSeparator()
        
        # Web UI action
        web_ui_action = QAction("Open Web UI", self)
        web_ui_action.triggered.connect(lambda: webbrowser.open(f"http://{config.API_HOST}:{config.API_PORT}"))
        self.toolbar.addAction(web_ui_action)
        
        self.addToolBar(self.toolbar)
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About BitNet.cpp Desktop",
            "BitNet.cpp Desktop\n\n"
            "A desktop application for downloading, managing, and running BitNet models locally on CPU.\n\n"
            "All processing is done locally on your machine without requiring any cloud services or GPU."
        )
    
    def refresh_models(self):
        """Refresh model lists."""
        self.model_management_widget.refresh_models()
        self.chat_interface_widget.refresh_models()
        self.inference_interface_widget.refresh_models()
        self.status_bar.showMessage("Models refreshed", 3000)
    
    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
