"""Login dialog"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from src.services.auth_service import AuthService


class LoginDialog(QDialog):
    """Login dialog for user authentication"""
    
    def __init__(self, auth_service: AuthService, parent=None):
        """Initialize login dialog"""
        super().__init__(parent)
        self.auth_service = auth_service
        self.setWindowTitle("Đăng nhập")
        self.setModal(True)
        self.setFixedSize(300, 150)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Tên đăng nhập:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Mật khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.clicked.connect(self.handle_login)
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus and enter key
        self.username_input.setFocus()
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập")
            return
        
        if not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu")
            return
        
        if self.auth_service.login(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng")
            self.password_input.clear()
            self.password_input.setFocus()

