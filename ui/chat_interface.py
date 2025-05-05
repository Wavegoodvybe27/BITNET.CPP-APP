"""
Chat interface widget for the BitNet.cpp desktop application.
"""
import os
import sys
import platform
import threading
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QTextEdit, QTextBrowser, QSlider,
    QSpinBox, QSplitter, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QTextCursor, QFont
import config

class ChatCompletionThread(QThread):
    """Thread for chat completion."""
    progress = pyqtSignal(str)
    response_received = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, inference_engine, model_name, messages, n_predict, threads, temperature):
        """Initialize the thread."""
        super().__init__()
        self.inference_engine = inference_engine
        self.model_name = model_name
        self.messages = messages
        self.n_predict = n_predict
        self.threads = threads
        self.temperature = temperature
    
    def run(self):
        """Run the thread."""
        try:
            self.progress.emit(f"Generating response with model {self.model_name}...")
            
            # Convert messages to format expected by inference engine
            formatted_messages = []
            for msg in self.messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Run chat completion
            response = self.inference_engine.chat_completion(
                model_name=self.model_name,
                messages=formatted_messages,
                n_predict=self.n_predict,
                threads=self.threads,
                ctx_size=2048,
                temperature=self.temperature
            )
            
            # Extract assistant response
            assistant_response = response["choices"][0]["message"]["content"]
            
            # Emit response
            self.response_received.emit(assistant_response)
            self.finished.emit(True, "Response generated successfully")
        except Exception as e:
            self.finished.emit(False, f"Error generating response: {str(e)}")

class ChatInterfaceWidget(QWidget):
    """Widget for chat interface."""
    def __init__(self, model_manager, inference_engine):
        """Initialize the widget."""
        super().__init__()
        
        # Store references to model manager and inference engine
        self.model_manager = model_manager
        self.inference_engine = inference_engine
        
        # Initialize chat messages
        self.messages = []
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create chat interface
        self.create_chat_interface()
        
        # Load models
        self.refresh_models()
    
    def create_chat_interface(self):
        """Create chat interface."""
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
        
        # System message
        system_group = QGroupBox("System Message")
        system_layout = QVBoxLayout()
        
        # System message text edit
        self.system_message_edit = QTextEdit()
        self.system_message_edit.setPlaceholderText("Optional system message")
        system_layout.addWidget(self.system_message_edit)
        
        system_group.setLayout(system_layout)
        left_layout.addWidget(system_group)
        
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
        
        # Threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Threads:"))
        
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 32)
        self.threads_spin.setValue(4)
        threads_layout.addWidget(self.threads_spin)
        
        params_layout.addLayout(threads_layout)
        
        params_group.setLayout(params_layout)
        left_layout.addWidget(params_group)
        
        # Add stretch to push everything to the top
        left_layout.addStretch()
        
        # Create right panel (chat)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Chat history
        chat_group = QGroupBox("Chat")
        chat_layout = QVBoxLayout()
        
        # Chat history browser
        self.chat_browser = QTextBrowser()
        self.chat_browser.setMinimumHeight(300)
        chat_layout.addWidget(self.chat_browser)
        
        # User input
        self.user_input_edit = QTextEdit()
        self.user_input_edit.setPlaceholderText("Type your message here...")
        self.user_input_edit.setMaximumHeight(100)
        chat_layout.addWidget(self.user_input_edit)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        chat_layout.addWidget(self.send_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        chat_layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel()
        chat_layout.addWidget(self.progress_label)
        
        chat_group.setLayout(chat_layout)
        right_layout.addWidget(chat_group)
        
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
    
    def send_message(self):
        """Send user message and get response."""
        # Get selected model
        model_name = self.model_combo.currentData()
        
        if not model_name:
            QMessageBox.warning(self, "Warning", "Please select a model")
            return
        
        # Get user input
        user_input = self.user_input_edit.toPlainText().strip()
        
        if not user_input:
            return
        
        # Clear user input
        self.user_input_edit.clear()
        
        # Get system message if present and not already added
        system_message = self.system_message_edit.toPlainText().strip()
        
        # Add system message if not already added and not empty
        if system_message and not any(msg["role"] == "system" for msg in self.messages):
            self.messages.append({
                "role": "system",
                "content": system_message
            })
            
            # Add system message to chat
            self.add_message_to_chat("system", system_message)
        
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Add user message to chat
        self.add_message_to_chat("user", user_input)
        
        # Get generation parameters
        temperature = self.temperature_slider.value() / 100.0
        max_tokens = self.max_tokens_spin.value()
        threads = self.threads_spin.value()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setText(f"Generating response with model {model_name}...")
        
        # Disable send button
        self.send_button.setEnabled(False)
        
        # Create and start chat completion thread
        self.chat_thread = ChatCompletionThread(
            self.inference_engine,
            model_name,
            self.messages,
            max_tokens,
            threads,
            temperature
        )
        self.chat_thread.progress.connect(self.update_progress)
        self.chat_thread.response_received.connect(self.on_response_received)
        self.chat_thread.finished.connect(self.on_chat_finished)
        self.chat_thread.start()
    
    def add_message_to_chat(self, role, content):
        """Add a message to the chat history."""
        # Create formatted message
        if role == "user":
            formatted_message = f"<div style='text-align: right; margin: 10px;'><b>You:</b> {content}</div>"
        elif role == "assistant":
            formatted_message = f"<div style='text-align: left; margin: 10px;'><b>Assistant:</b> {content}</div>"
        elif role == "system":
            formatted_message = f"<div style='text-align: center; margin: 10px; color: gray;'><i>System: {content}</i></div>"
        else:
            formatted_message = f"<div style='margin: 10px;'><b>{role}:</b> {content}</div>"
        
        # Add to chat browser
        self.chat_browser.append(formatted_message)
        
        # Scroll to bottom
        self.chat_browser.verticalScrollBar().setValue(self.chat_browser.verticalScrollBar().maximum())
    
    def update_progress(self, message):
        """Update progress message."""
        self.progress_label.setText(message)
    
    def on_response_received(self, response):
        """Handle response received event."""
        # Add assistant message
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Add assistant message to chat
        self.add_message_to_chat("assistant", response)
    
    def on_chat_finished(self, success, message):
        """Handle chat finished event."""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.progress_label.setText(message)
        
        # Enable send button
        self.send_button.setEnabled(True)
        
        # Show error message if failed
        if not success:
            QMessageBox.critical(self, "Error", message)
