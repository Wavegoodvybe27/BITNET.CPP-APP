"""
Resources package for the BitNet.cpp desktop application.
"""
import base64
import os
from PyQt5.QtGui import QIcon, QPixmap
from io import BytesIO
from .icon import ICON_DATA

def get_icon():
    """Get the application icon."""
    icon_data = base64.b64decode(ICON_DATA)
    pixmap = QPixmap()
    pixmap.loadFromData(icon_data)
    return QIcon(pixmap)
