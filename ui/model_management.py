"""
Model management widget for the BitNet.cpp desktop application.
"""
import os
import sys
import platform
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QTextBrowser, QProgressBar,
    QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import config

class ModelDownloadThread(QThread):
    """Thread for downloading models."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, model_manager, model_id, quant_type=None):
        """Initialize the thread."""
        super().__init__()
        self.model_manager = model_manager
        self.model_id = model_id
        self.quant_type = quant_type
    
    def run(self):
        """Run the thread."""
        try:
            self.progress.emit(f"Downloading model {self.model_id}...")
            success = self.model_manager.download_model(self.model_id, self.quant_type)
            if success:
                self.finished.emit(True, f"Model {self.model_id} downloaded successfully")
            else:
                self.finished.emit(False, f"Failed to download model {self.model_id}")
        except Exception as e:
            self.finished.emit(False, f"Error downloading model: {str(e)}")

class ModelRemoveThread(QThread):
    """Thread for removing models."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, model_manager, model_name):
        """Initialize the thread."""
        super().__init__()
        self.model_manager = model_manager
        self.model_name = model_name
    
    def run(self):
        """Run the thread."""
        try:
            self.progress.emit(f"Removing model {self.model_name}...")
            success = self.model_manager.remove_model(self.model_name)
            if success:
                self.finished.emit(True, f"Model {self.model_name} removed successfully")
            else:
                self.finished.emit(False, f"Failed to remove model {self.model_name}")
        except Exception as e:
            self.finished.emit(False, f"Error removing model: {str(e)}")

class ModelManagementWidget(QWidget):
    """Widget for managing models."""
    def __init__(self, model_manager):
        """Initialize the widget."""
        super().__init__()
        
        # Store reference to model manager
        self.model_manager = model_manager
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create model management section
        self.create_model_management_section()
        
        # Create model info section
        self.create_model_info_section()
        
        # Create progress section
        self.create_progress_section()
        
        # Load models
        self.refresh_models()
    
    def create_model_management_section(self):
        """Create model management section."""
        # Create group box
        group_box = QGroupBox("Model Management")
        group_layout = QVBoxLayout()
        
        # Available models section
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available Models:"))
        
        # Available models combo box
        self.available_models_combo = QComboBox()
        available_layout.addWidget(self.available_models_combo)
        
        # Download options
        download_layout = QHBoxLayout()
        
        # Quantization type combo box
        self.quant_type_combo = QComboBox()
        self.quant_type_combo.addItem("Default Quantization")
        
        # Add supported quantization types based on architecture
        arch = platform.machine().lower()
        if arch in config.SUPPORTED_QUANT_TYPES:
            for quant_type in config.SUPPORTED_QUANT_TYPES[arch]:
                self.quant_type_combo.addItem(quant_type)
        
        download_layout.addWidget(self.quant_type_combo)
        
        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_model)
        download_layout.addWidget(self.download_button)
        
        available_layout.addLayout(download_layout)
        group_layout.addLayout(available_layout)
        
        # Add separator
        separator = QLabel()
        separator.setFrameShape(QLabel.HLine)
        separator.setFrameShadow(QLabel.Sunken)
        group_layout.addWidget(separator)
        
        # Installed models section
        installed_layout = QVBoxLayout()
        installed_layout.addWidget(QLabel("Installed Models:"))
        
        # Installed models combo box
        self.installed_models_combo = QComboBox()
        self.installed_models_combo.currentIndexChanged.connect(self.update_model_info)
        installed_layout.addWidget(self.installed_models_combo)
        
        # Remove button
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_model)
        installed_layout.addWidget(self.remove_button)
        
        group_layout.addLayout(installed_layout)
        
        # Set layout for group box
        group_box.setLayout(group_layout)
        
        # Add group box to main layout
        self.layout.addWidget(group_box)
    
    def create_model_info_section(self):
        """Create model info section."""
        # Create group box
        group_box = QGroupBox("Model Information")
        group_layout = QVBoxLayout()
        
        # Model info text browser
        self.model_info_browser = QTextBrowser()
        group_layout.addWidget(self.model_info_browser)
        
        # Set layout for group box
        group_box.setLayout(group_layout)
        
        # Add group box to main layout
        self.layout.addWidget(group_box)
    
    def create_progress_section(self):
        """Create progress section."""
        # Create group box
        group_box = QGroupBox("Progress")
        group_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        group_layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel()
        group_layout.addWidget(self.progress_label)
        
        # Set layout for group box
        group_box.setLayout(group_layout)
        
        # Add group box to main layout
        self.layout.addWidget(group_box)
    
    def refresh_models(self):
        """Refresh model lists."""
        # Clear combo boxes
        self.available_models_combo.clear()
        self.installed_models_combo.clear()
        
        # Add available models
        available_models = self.model_manager.list_available_models()
        for model_id, info in available_models.items():
            self.available_models_combo.addItem(model_id, model_id)
        
        # Add installed models
        installed_models = self.model_manager.list_installed_models()
        for model_name, info in installed_models.items():
            self.installed_models_combo.addItem(model_name, model_name)
        
        # Update model info
        self.update_model_info()
    
    def update_model_info(self):
        """Update model info based on selected model."""
        # Get selected model
        model_name = self.installed_models_combo.currentData()
        
        # Clear model info
        self.model_info_browser.clear()
        
        if model_name:
            # Get model info
            installed_models = self.model_manager.list_installed_models()
            if model_name in installed_models:
                info = installed_models[model_name]
                
                # Format model info
                html = f"<h3>{model_name}</h3>"
                html += f"<p><b>Model ID:</b> {info.get('model_id', 'Unknown')}</p>"
                html += f"<p><b>Description:</b> {info.get('description', 'No description available')}</p>"
                html += f"<p><b>Quantization Type:</b> {info.get('quant_type', 'Unknown')}</p>"
                html += f"<p><b>Path:</b> {info.get('path', 'Unknown')}</p>"
                
                # Set model info
                self.model_info_browser.setHtml(html)
    
    def download_model(self):
        """Download selected model."""
        # Get selected model
        model_id = self.available_models_combo.currentData()
        
        if not model_id:
            QMessageBox.warning(self, "Warning", "Please select a model to download")
            return
        
        # Get selected quantization type
        quant_type = None
        if self.quant_type_combo.currentIndex() > 0:
            quant_type = self.quant_type_combo.currentText()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setText(f"Downloading model {model_id}...")
        
        # Disable buttons
        self.download_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        
        # Create and start download thread
        self.download_thread = ModelDownloadThread(self.model_manager, model_id, quant_type)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def remove_model(self):
        """Remove selected model."""
        # Get selected model
        model_name = self.installed_models_combo.currentData()
        
        if not model_name:
            QMessageBox.warning(self, "Warning", "Please select a model to remove")
            return
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove model {model_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setText(f"Removing model {model_name}...")
        
        # Disable buttons
        self.download_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        
        # Create and start remove thread
        self.remove_thread = ModelRemoveThread(self.model_manager, model_name)
        self.remove_thread.progress.connect(self.update_progress)
        self.remove_thread.finished.connect(self.on_remove_finished)
        self.remove_thread.start()
    
    def update_progress(self, message):
        """Update progress message."""
        self.progress_label.setText(message)
    
    def on_download_finished(self, success, message):
        """Handle download finished event."""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.progress_label.setText(message)
        
        # Enable buttons
        self.download_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        
        # Refresh models
        self.refresh_models()
        
        # Show message
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def on_remove_finished(self, success, message):
        """Handle remove finished event."""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.progress_label.setText(message)
        
        # Enable buttons
        self.download_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        
        # Refresh models
        self.refresh_models()
        
        # Show message
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
