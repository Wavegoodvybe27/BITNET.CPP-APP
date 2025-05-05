"""
Inference interface widget for the BitNet.cpp desktop application.
"""
import os
import sys
import platform
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QTextEdit, QTextBrowser, QSlider,
    QSpinBox, QSplitter, QMessageBox, QProgressBar, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import config

class InferenceThread(QThread):
    """Thread for running inference."""
    progress = pyqtSignal(str)
    response_received = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, inference_engine, model_name, prompt, n_predict, threads, ctx_size, temperature, conversation):
        """Initialize the thread."""
        super().__init__()
        self.inference_engine = inference_engine
        self.model_name = model_name
        self.prompt = prompt
        self.n_predict = n_predict
        self.threads = threads
        self.ctx_size = ctx_size
        self.temperature = temperature
        self.conversation = conversation
    
    def run(self):
        """Run the thread."""
        try:
            self.progress.emit(f"Running inference with model {self.model_name}...")
            
            # Run inference
            response = self.inference_engine.run_inference(
                model_name=self.model_name,
                prompt=self.prompt,
                n_predict=self.n_predict,
                threads=self.threads,
                ctx_size=self.ctx_size,
                temperature=self.temperature,
                conversation=self.conversation
            )
            
            # Emit response
            self.response_received.emit(response)
            self.finished.emit(True, "Inference completed successfully")
        except Exception as e:
            self.finished.emit(False, f"Error running inference: {str(e)}")

class InferenceInterfaceWidget(QWidget):
    """Widget for inference interface."""
    def __init__(self, model_manager, inference_engine):
        """Initialize the widget."""
        super().__init__()
        
        # Store references to model manager and inference engine
        self.model_manager = model_manager
        self.inference_engine = inference_engine
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create inference interface
        self.create_inference_interface()
        
        # Load models
        self.refresh_models()
    
    def create_inference_interface(self):
        """Create inference interface."""
        # Create main layout
        main_layout = QHBoxLayout()
        
        # Create left panel (settings)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Model selection
        model_group = QGroupBox("Model")
        model_layout = QVBoxLayout()
        
        # Model combo box
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        # Generation parameters
        params_group = QGroupBox("Generation Parameters")
        params_layout = QVBoxLayout()
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)  # Default 0.7
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)
        temp_layout.addWidget(self.temperature_slider)
        
        self.temperature_label = QLabel("0.7")
        temp_layout.addWidget(self.temperature_label)
        
        params_layout.addLayout(temp_layout)
        
        # Max tokens
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Max Tokens:"))
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 2048)
        self.max_tokens_spin.setValue(128)
        tokens_layout.addWidget(self.max_tokens_spin)
        
        params_layout.addLayout(tokens_layout)
        
        # Context size
        ctx_layout = QHBoxLayout()
        ctx_layout.addWidget(QLabel("Context Size:"))
        
        self.ctx_size_spin = QSpinBox()
        self.ctx_size_spin.setRange(512, 4096)
        self.ctx_size_spin.setValue(2048)
        self.ctx_size_spin.setSingleStep(512)
        ctx_layout.addWidget(self.ctx_size_spin)
        
        params_layout.addLayout(ctx_layout)
        
        # Threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Threads:"))
        
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 32)
        self.threads_spin.setValue(4)
        threads_layout.addWidget(self.threads_spin)
        
        params_layout.addLayout(threads_layout)
        
        # Conversation mode
        self.conversation_check = QCheckBox("Conversation Mode")
        params_layout.addWidget(self.conversation_check)
        
        params_group.setLayout(params_layout)
        left_layout.addWidget(params_group)
        
        # Add stretch to push everything to the top
        left_layout.addStretch()
        
        # Create right panel (inference)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Prompt
        prompt_group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout()
        
        # Prompt text edit
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your prompt here...")
        prompt_layout.addWidget(self.prompt_edit)
        
        # Run button
        self.run_button = QPushButton("Run Inference")
        self.run_button.clicked.connect(self.run_inference)
        prompt_layout.addWidget(self.run_button)
        
        prompt_group.setLayout(prompt_layout)
        right_layout.addWidget(prompt_group)
        
        # Response
        response_group = QGroupBox("Response")
        response_layout = QVBoxLayout()
        
        # Response browser
        self.response_browser = QTextBrowser()
        response_layout.addWidget(self.response_browser)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        response_layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel()
        response_layout.addWidget(self.progress_label)
        
        response_group.setLayout(response_layout)
        right_layout.addWidget(response_group)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])  # Set initial sizes
        
        main_layout.addWidget(splitter)
        self.layout.addLayout(main_layout)
    
    def refresh_models(self):
        """Refresh model list."""
        # Clear combo box
        self.model_combo.clear()
        
        # Add installed models
        installed_models = self.model_manager.list_installed_models()
        for model_name, info in installed_models.items():
            self.model_combo.addItem(model_name, model_name)
    
    def update_temperature_label(self):
        """Update temperature label based on slider value."""
        temperature = self.temperature_slider.value() / 100.0
        self.temperature_label.setText(f"{temperature:.1f}")
    
    def run_inference(self):
        """Run inference with selected model and prompt."""
        # Get selected model
        model_name = self.model_combo.currentData()
        
        if not model_name:
            QMessageBox.warning(self, "Warning", "Please select a model")
            return
        
        # Get prompt
        prompt = self.prompt_edit.toPlainText().strip()
        
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt")
            return
        
        # Get generation parameters
        temperature = self.temperature_slider.value() / 100.0
        max_tokens = self.max_tokens_spin.value()
        ctx_size = self.ctx_size_spin.value()
        threads = self.threads_spin.value()
        conversation = self.conversation_check.isChecked()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setText(f"Running inference with model {model_name}...")
        
        # Clear response
        self.response_browser.clear()
        
        # Disable run button
        self.run_button.setEnabled(False)
        
        # Create and start inference thread
        self.inference_thread = InferenceThread(
            self.inference_engine,
            model_name,
            prompt,
            max_tokens,
            threads,
            ctx_size,
            temperature,
            conversation
        )
        self.inference_thread.progress.connect(self.update_progress)
        self.inference_thread.response_received.connect(self.on_response_received)
        self.inference_thread.finished.connect(self.on_inference_finished)
        self.inference_thread.start()
    
    def update_progress(self, message):
        """Update progress message."""
        self.progress_label.setText(message)
    
    def on_response_received(self, response):
        """Handle response received event."""
        # Set response
        self.response_browser.setPlainText(response)
    
    def on_inference_finished(self, success, message):
        """Handle inference finished event."""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.progress_label.setText(message)
        
        # Enable run button
        self.run_button.setEnabled(True)
        
        # Show error message if failed
        if not success:
            QMessageBox.critical(self, "Error", message)
