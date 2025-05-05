#!/usr/bin/env python3
"""
Desktop application for BitNet.cpp.
Provides a GUI for model management and local CPU-only inference.
All processing is done locally on your machine without requiring any cloud services or GPU.
"""
import os
import sys
import platform
import threading
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# Import UI components
from ui.main_window import MainWindow
from ui.resources import get_icon
from ui.styles import LIGHT_STYLESHEET, DARK_STYLESHEET
import config
from model_manager import ModelManager
from inference import InferenceEngine

class ServerThread(QThread):
    """Thread for running the API server in the background."""
    server_started = pyqtSignal()
    server_error = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def run(self):
        """Run the server."""
        try:
            # Import here to avoid circular imports
            import uvicorn
            from server import app

            uvicorn.run(
                app,
                host=self.host,
                port=self.port
            )
            self.server_started.emit()
        except Exception as e:
            self.server_error.emit(str(e))

class BitNetDesktop:
    """Main desktop application class."""
    def __init__(self):
        """Initialize the desktop application."""
        # Create application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("BitNet.cpp Desktop")
        self.app.setQuitOnLastWindowClosed(False)  # Allow app to run in system tray

        # Set application style
        self.app.setStyle("Fusion")

        # Set up model manager and inference engine
        self.model_manager = ModelManager()
        self.inference_engine = InferenceEngine(self.model_manager)

        # Create main window
        self.main_window = MainWindow(self.model_manager, self.inference_engine)
        self.main_window.setWindowIcon(get_icon())

        # Set up system tray
        self.setup_system_tray()

        # Start server in background
        self.start_server()

    def setup_system_tray(self):
        """Set up system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(get_icon())

        # Create tray menu
        tray_menu = QMenu()

        # Add actions
        show_action = QAction("Show", self.app)
        show_action.triggered.connect(self.main_window.show)
        tray_menu.addAction(show_action)

        hide_action = QAction("Hide", self.app)
        hide_action.triggered.connect(self.main_window.hide)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.quit)
        tray_menu.addAction(quit_action)

        # Set tray menu
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Show message
        self.tray_icon.showMessage(
            "BitNet.cpp Desktop",
            "Application is running in the system tray",
            QSystemTrayIcon.Information,
            2000
        )

    def start_server(self):
        """Start the API server in the background."""
        self.server_thread = ServerThread(config.API_HOST, config.API_PORT)
        self.server_thread.server_started.connect(self.on_server_started)
        self.server_thread.server_error.connect(self.on_server_error)
        self.server_thread.start()

    def on_server_started(self):
        """Handle server started event."""
        print(f"Server started on {config.API_HOST}:{config.API_PORT}")

    def on_server_error(self, error):
        """Handle server error event."""
        print(f"Server error: {error}")
        QMessageBox.critical(
            self.main_window,
            "Server Error",
            f"Failed to start server: {error}"
        )

    def run(self):
        """Run the application."""
        self.main_window.show()
        return self.app.exec_()

    def quit(self):
        """Quit the application."""
        self.app.quit()

if __name__ == "__main__":
    app = BitNetDesktop()
    sys.exit(app.run())
