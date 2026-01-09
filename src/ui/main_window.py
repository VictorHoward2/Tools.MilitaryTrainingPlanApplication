"""Main application window"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QToolBar,
    QStatusBar, QStackedWidget, QMessageBox, QLabel, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QPixmap
from pathlib import Path
from src.services.auth_service import AuthService
from src.services.file_service import FileService
from src.services.subject_service import SubjectService
from src.services.schedule_service import ScheduleService
from src.ui.dialogs.login_dialog import LoginDialog
from src.ui.widgets.subject_manager import SubjectManager
from src.ui.widgets.schedule_creator import ScheduleCreator
from src.ui.widgets.schedule_viewer import ScheduleViewer
from src.ui.widgets.progress_tracker import ProgressTracker
from src.utils.logger import setup_logger
from src.utils.i18n import tr

logger = setup_logger()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, parent=None):
        """Initialize main window"""
        super().__init__(parent)
        
        # Initialize services
        self.file_service = FileService()
        self.auth_service = AuthService(self.file_service)
        self.subject_service = SubjectService(self.file_service)
        self.schedule_service = ScheduleService(self.file_service, self.subject_service)
        
        # Check authentication
        if not self.check_authentication():
            self.close()
            return
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        logger.info("Main window initialized")
    
    def set_window_icon(self):
        """Set window icon from logo"""
        try:
            # Try to load icon from resources/icons
            base_path = Path(__file__).parent.parent.parent.parent
            icon_path = base_path / "resources" / "icons" / "logo.jpg"
            
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                logger.info(f"Window icon set from: {icon_path}")
            else:
                # Try alternative locations
                alt_path = base_path / "logo.jpg"
                if alt_path.exists():
                    self.setWindowIcon(QIcon(str(alt_path)))
                    logger.info(f"Window icon set from: {alt_path}")
        except Exception as e:
            logger.warning(f"Could not set window icon: {e}")
    
    def check_authentication(self) -> bool:
        """Check if user is authenticated"""
        if not self.auth_service.is_authenticated():
            dialog = LoginDialog(self.auth_service, self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return False
        return True
    
    def setup_ui(self):
        """Setup UI components"""
        self.setWindowTitle(tr("app_name"))
        self.setMinimumSize(1200, 800)
        
        # Set window icon
        self.set_window_icon()
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create and add widgets
        self.subject_manager = SubjectManager(self.subject_service)
        self.stacked_widget.addWidget(self.subject_manager)
        
        self.schedule_creator = ScheduleCreator(
            self.schedule_service, self.subject_service
        )
        self.schedule_creator.schedule_created.connect(self.on_schedule_created)
        self.stacked_widget.addWidget(self.schedule_creator)
        
        self.schedule_viewer = ScheduleViewer(self.schedule_service)
        self.stacked_widget.addWidget(self.schedule_viewer)
        
        self.progress_tracker = ProgressTracker(self.schedule_service)
        self.stacked_widget.addWidget(self.progress_tracker)
        
        # Show subject manager by default
        self.stacked_widget.setCurrentWidget(self.subject_manager)
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        logout_action = QAction("&Logout", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        subjects_action = QAction("&Subjects", self)
        subjects_action.setShortcut("Ctrl+1")
        subjects_action.triggered.connect(lambda: self.show_view(0))
        view_menu.addAction(subjects_action)
        
        create_schedule_action = QAction("&Create Schedule", self)
        create_schedule_action.setShortcut("Ctrl+2")
        create_schedule_action.triggered.connect(lambda: self.show_view(1))
        view_menu.addAction(create_schedule_action)
        
        view_schedule_action = QAction("&View Schedule", self)
        view_schedule_action.setShortcut("Ctrl+3")
        view_schedule_action.triggered.connect(lambda: self.show_view(2))
        view_menu.addAction(view_schedule_action)
        
        progress_action = QAction("&Progress", self)
        progress_action.setShortcut("Ctrl+4")
        progress_action.triggered.connect(lambda: self.show_view(3))
        view_menu.addAction(progress_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # View actions
        subjects_action = QAction("Subjects", self)
        subjects_action.triggered.connect(lambda: self.show_view(0))
        toolbar.addAction(subjects_action)
        
        create_schedule_action = QAction("Create Schedule", self)
        create_schedule_action.triggered.connect(lambda: self.show_view(1))
        toolbar.addAction(create_schedule_action)
        
        view_schedule_action = QAction("View Schedule", self)
        view_schedule_action.triggered.connect(lambda: self.show_view(2))
        toolbar.addAction(view_schedule_action)
        
        progress_action = QAction("Progress", self)
        progress_action.triggered.connect(lambda: self.show_view(3))
        toolbar.addAction(progress_action)
        
        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_current_view)
        toolbar.addAction(refresh_action)
    
    def setup_statusbar(self):
        """Setup status bar"""
        self.statusBar().showMessage("Ready")
        
        # Show current user
        user = self.auth_service.get_current_user()
        if user:
            user_text = f"User: {user.username}"
            if user.full_name:
                user_text += f" ({user.full_name})"
            self.statusBar().addPermanentWidget(QLabel(user_text))
    
    def show_view(self, index: int):
        """Show view by index"""
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
            
            # Update status
            view_names = ["Subjects", "Create Schedule", "View Schedule", "Progress"]
            if index < len(view_names):
                self.statusBar().showMessage(f"View: {view_names[index]}")
    
    def refresh_current_view(self):
        """Refresh current view"""
        current_widget = self.stacked_widget.currentWidget()
        
        if isinstance(current_widget, SubjectManager):
            current_widget.load_subjects()
        elif isinstance(current_widget, ScheduleViewer):
            current_widget.load_schedules()
        elif isinstance(current_widget, ProgressTracker):
            current_widget.load_schedules()
        
        self.statusBar().showMessage("Refreshed", 2000)
    
    def on_schedule_created(self, schedule):
        """Handle schedule created"""
        # Switch to schedule viewer and refresh
        self.show_view(2)
        self.schedule_viewer.load_schedules()
        self.statusBar().showMessage("Schedule created successfully", 3000)
    
    def logout(self):
        """Logout user"""
        reply = QMessageBox.question(
            self, "Logout", "Bạn có chắc chắn muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.auth_service.logout()
            self.close()
            # Restart login
            dialog = LoginDialog(self.auth_service, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Recreate window
                from src.main import main
                main()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About",
            f"{tr('app_name')}\n\n"
            f"Version: 1.0.0\n"
            f"Author: Victor Howard\n\n"
            f"Ứng dụng hỗ trợ giảng viên quân đội quản lý các môn học và thời khóa biểu."
        )
    
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(
            self, "Exit", "Bạn có chắc chắn muốn thoát?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

