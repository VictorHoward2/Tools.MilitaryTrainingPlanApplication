"""UI helper functions"""

from PySide6.QtWidgets import QMessageBox
from typing import Optional


def show_error(parent, title: str, message: str):
    """Show error message"""
    QMessageBox.critical(parent, title, message)


def show_info(parent, title: str, message: str):
    """Show info message"""
    QMessageBox.information(parent, title, message)


def show_warning(parent, title: str, message: str):
    """Show warning message"""
    QMessageBox.warning(parent, title, message)


def confirm(parent, title: str, message: str) -> bool:
    """Show confirmation dialog"""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No
    )
    return reply == QMessageBox.Yes

