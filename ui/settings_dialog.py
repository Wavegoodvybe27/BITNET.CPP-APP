"""
Settings dialog for the BitNet.cpp desktop application.
"""
import os
import sys
import platform
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QTabWidget, QWidget, QGroupBox,
    QFormLayout, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
import config

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super().__init__(parent)
        
        # Set dialog properties
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create tabs
        self.create_tabs()
        
        # Create buttons
        self.create_buttons()
    
    def create_tabs(self):
        """Create tabs for different settings categories."""
        self.tabs = QTabWidget()
        
        # Server settings tab
        self.server_tab = QWidget()
        self.create_server_tab()
        self.tabs.addTab(self.server_tab, "Server")
        
        # Model settings tab
        self.model_tab = QWidget()
        self.create_model_tab()
        self.tabs.addTab(self.model_tab, "Models")
        
        # UI settings tab
        self.ui_tab = QWidget()
        self.create_ui_tab()
        self.tabs.addTab(self.ui_tab, "UI")
        
        self.layout.addWidget(self.tabs)
    
    def create_server_tab(self):
        """Create server settings tab."""
        layout = QVBoxLayout(self.server_tab)
        
        # API server settings
        group = QGroupBox("API Server")
        form = QFormLayout()
        
        # Host
        self.host_edit = QLineEdit(config.API_HOST)
        form.addRow("Host:", self.host_edit)
        
        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(config.API_PORT)
        form.addRow("Port:", self.port_spin)
        
        # Auto-start server
        self.auto_start_check = QCheckBox("Start server automatically")
        self.auto_start_check.setChecked(True)
        form.addRow("", self.auto_start_check)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def create_model_tab(self):
        """Create model settings tab."""
        layout = QVBoxLayout(self.model_tab)
        
        # Model directory
        group = QGroupBox("Model Directory")
        form = QFormLayout()
        
        # Directory
        self.model_dir_edit = QLineEdit(config.MODELS_DIR)
        form.addRow("Directory:", self.model_dir_edit)
        
        # Browse button
        browse_button = QPushButton("Browse...")
        form.addRow("", browse_button)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Default model settings
        group = QGroupBox("Default Settings")
        form = QFormLayout()
        
        # Default model
        self.default_model_edit = QLineEdit(config.DEFAULT_MODEL)
        form.addRow("Default Model:", self.default_model_edit)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def create_ui_tab(self):
        """Create UI settings tab."""
        layout = QVBoxLayout(self.ui_tab)
        
        # UI settings
        group = QGroupBox("UI Settings")
        form = QFormLayout()
        
        # Minimize to tray
        self.minimize_to_tray_check = QCheckBox("Minimize to system tray")
        self.minimize_to_tray_check.setChecked(True)
        form.addRow("", self.minimize_to_tray_check)
        
        # Show notifications
        self.show_notifications_check = QCheckBox("Show notifications")
        self.show_notifications_check.setChecked(True)
        form.addRow("", self.show_notifications_check)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def create_buttons(self):
        """Create dialog buttons."""
        button_layout = QHBoxLayout()
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.layout.addLayout(button_layout)
    
    def save_settings(self):
        """Save settings and close dialog."""
        # Validate settings
        if not self.validate_settings():
            return
        
        # Save settings
        # Note: In a real implementation, we would update the config module
        # and save the settings to a file. For this example, we just show a message.
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved. Some settings may require a restart to take effect."
        )
        
        # Close dialog
        self.accept()
    
    def validate_settings(self):
        """Validate settings."""
        # Validate host
        host = self.host_edit.text().strip()
        if not host:
            QMessageBox.warning(self, "Invalid Host", "Host cannot be empty")
            return False
        
        # Validate model directory
        model_dir = self.model_dir_edit.text().strip()
        if not model_dir:
            QMessageBox.warning(self, "Invalid Model Directory", "Model directory cannot be empty")
            return False
        
        return True
