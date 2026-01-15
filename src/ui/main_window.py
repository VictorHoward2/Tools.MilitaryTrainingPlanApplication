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
from src.utils.i18n import tr, set_language, get_language, SUPPORTED_LANGUAGES

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
        
        # Store menu actions for language updates
        self.menu_actions = {}
        
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
        file_menu = menubar.addMenu(tr("file_menu"))
        self.menu_actions['file_menu'] = file_menu
        
        logout_action = QAction(tr("logout"), self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        self.menu_actions['logout'] = logout_action
        
        exit_action = QAction(tr("exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self.menu_actions['exit'] = exit_action
        
        # View menu
        view_menu = menubar.addMenu(tr("view_menu"))
        self.menu_actions['view_menu'] = view_menu
        
        subjects_action = QAction(tr("subjects"), self)
        subjects_action.setShortcut("Ctrl+1")
        subjects_action.triggered.connect(lambda: self.show_view(0))
        view_menu.addAction(subjects_action)
        self.menu_actions['subjects'] = subjects_action
        
        create_schedule_action = QAction(tr("create_schedule"), self)
        create_schedule_action.setShortcut("Ctrl+2")
        create_schedule_action.triggered.connect(lambda: self.show_view(1))
        view_menu.addAction(create_schedule_action)
        self.menu_actions['create_schedule'] = create_schedule_action
        
        view_schedule_action = QAction(tr("view_schedule"), self)
        view_schedule_action.setShortcut("Ctrl+3")
        view_schedule_action.triggered.connect(lambda: self.show_view(2))
        view_menu.addAction(view_schedule_action)
        self.menu_actions['view_schedule'] = view_schedule_action
        
        progress_action = QAction(tr("progress"), self)
        progress_action.setShortcut("Ctrl+4")
        progress_action.triggered.connect(lambda: self.show_view(3))
        view_menu.addAction(progress_action)
        self.menu_actions['progress'] = progress_action
        
        # Language menu
        language_menu = menubar.addMenu(tr("language"))
        self.menu_actions['language_menu'] = language_menu
        
        vi_action = QAction(tr("language_vietnamese"), self)
        vi_action.setCheckable(True)
        vi_action.setChecked(get_language() == "vi")
        vi_action.triggered.connect(lambda: self.change_language("vi"))
        language_menu.addAction(vi_action)
        self.menu_actions['vi'] = vi_action
        
        en_action = QAction(tr("language_english"), self)
        en_action.setCheckable(True)
        en_action.setChecked(get_language() == "en")
        en_action.triggered.connect(lambda: self.change_language("en"))
        language_menu.addAction(en_action)
        self.menu_actions['en'] = en_action
        
        # Help menu
        help_menu = menubar.addMenu(tr("help_menu"))
        self.menu_actions['help_menu'] = help_menu
        
        about_action = QAction(tr("about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        self.menu_actions['about'] = about_action
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar(tr("app_name"))
        self.addToolBar(toolbar)
        self.toolbar = toolbar
        
        # View actions
        subjects_action = QAction(tr("subjects"), self)
        subjects_action.triggered.connect(lambda: self.show_view(0))
        toolbar.addAction(subjects_action)
        self.menu_actions['toolbar_subjects'] = subjects_action
        
        create_schedule_action = QAction(tr("create_schedule"), self)
        create_schedule_action.triggered.connect(lambda: self.show_view(1))
        toolbar.addAction(create_schedule_action)
        self.menu_actions['toolbar_create_schedule'] = create_schedule_action
        
        view_schedule_action = QAction(tr("view_schedule"), self)
        view_schedule_action.triggered.connect(lambda: self.show_view(2))
        toolbar.addAction(view_schedule_action)
        self.menu_actions['toolbar_view_schedule'] = view_schedule_action
        
        progress_action = QAction(tr("progress"), self)
        progress_action.triggered.connect(lambda: self.show_view(3))
        toolbar.addAction(progress_action)
        self.menu_actions['toolbar_progress'] = progress_action
        
        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction(tr("refresh"), self)
        refresh_action.triggered.connect(self.refresh_current_view)
        toolbar.addAction(refresh_action)
        self.menu_actions['toolbar_refresh'] = refresh_action
    
    def setup_statusbar(self):
        """Setup status bar"""
        self.statusBar().showMessage(tr("ready"))
        
        # Show current user
        user = self.auth_service.get_current_user()
        if user:
            user_text = f"{tr('user')}: {user.username}"
            if user.full_name:
                user_text += f" ({user.full_name})"
            self.user_label = QLabel(user_text)
            self.statusBar().addPermanentWidget(self.user_label)
    
    def show_view(self, index: int):
        """Show view by index"""
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
            
            # Update status
            view_names = [tr("subjects"), tr("create_schedule"), tr("view_schedule"), tr("progress")]
            if index < len(view_names):
                self.statusBar().showMessage(f"{tr('view')}: {view_names[index]}")
    
    def refresh_current_view(self):
        """Refresh current view"""
        current_widget = self.stacked_widget.currentWidget()
        
        if isinstance(current_widget, SubjectManager):
            current_widget.load_subjects()
        elif isinstance(current_widget, ScheduleViewer):
            current_widget.load_schedules()
        elif isinstance(current_widget, ProgressTracker):
            current_widget.load_schedules()
        
        self.statusBar().showMessage(tr("refreshed"), 2000)
    
    def on_schedule_created(self, schedule):
        """Handle schedule created"""
        # Switch to schedule viewer and refresh
        self.show_view(2)
        self.schedule_viewer.load_schedules()
        self.statusBar().showMessage(tr("schedule_created_successfully"), 3000)
    
    def logout(self):
        """Logout user"""
        reply = QMessageBox.question(
            self, tr("logout"), tr("confirm_logout"),
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
            self, tr("about"),
            f"{tr('app_name')}\n\n"
            f"{tr('about_version')}\n"
            f"{tr('about_author')}\n\n"
            f"{tr('about_text')}"
        )
    
    def change_language(self, language: str):
        """Change application language"""
        if language in SUPPORTED_LANGUAGES:
            set_language(language)
            self.update_ui_language()
    
    def update_ui_language(self):
        """Update all UI text to current language"""
        # Update window title
        self.setWindowTitle(tr("app_name"))
        
        # Update menu bar
        if hasattr(self, 'menu_actions'):
            if 'file_menu' in self.menu_actions:
                self.menu_actions['file_menu'].setTitle(tr("file_menu"))
            if 'logout' in self.menu_actions:
                self.menu_actions['logout'].setText(tr("logout"))
            if 'exit' in self.menu_actions:
                self.menu_actions['exit'].setText(tr("exit"))
            if 'view_menu' in self.menu_actions:
                self.menu_actions['view_menu'].setTitle(tr("view_menu"))
            if 'subjects' in self.menu_actions:
                self.menu_actions['subjects'].setText(tr("subjects"))
            if 'create_schedule' in self.menu_actions:
                self.menu_actions['create_schedule'].setText(tr("create_schedule"))
            if 'view_schedule' in self.menu_actions:
                self.menu_actions['view_schedule'].setText(tr("view_schedule"))
            if 'progress' in self.menu_actions:
                self.menu_actions['progress'].setText(tr("progress"))
            if 'language_menu' in self.menu_actions:
                self.menu_actions['language_menu'].setTitle(tr("language"))
            if 'vi' in self.menu_actions:
                self.menu_actions['vi'].setText(tr("language_vietnamese"))
                self.menu_actions['vi'].setChecked(get_language() == "vi")
            if 'en' in self.menu_actions:
                self.menu_actions['en'].setText(tr("language_english"))
                self.menu_actions['en'].setChecked(get_language() == "en")
            if 'help_menu' in self.menu_actions:
                self.menu_actions['help_menu'].setTitle(tr("help_menu"))
            if 'about' in self.menu_actions:
                self.menu_actions['about'].setText(tr("about"))
            if 'toolbar_subjects' in self.menu_actions:
                self.menu_actions['toolbar_subjects'].setText(tr("subjects"))
            if 'toolbar_create_schedule' in self.menu_actions:
                self.menu_actions['toolbar_create_schedule'].setText(tr("create_schedule"))
            if 'toolbar_view_schedule' in self.menu_actions:
                self.menu_actions['toolbar_view_schedule'].setText(tr("view_schedule"))
            if 'toolbar_progress' in self.menu_actions:
                self.menu_actions['toolbar_progress'].setText(tr("progress"))
            if 'toolbar_refresh' in self.menu_actions:
                self.menu_actions['toolbar_refresh'].setText(tr("refresh"))
        
        # Update status bar
        self.statusBar().showMessage(tr("ready"))
        if hasattr(self, 'user_label'):
            user = self.auth_service.get_current_user()
            if user:
                user_text = f"{tr('user')}: {user.username}"
                if user.full_name:
                    user_text += f" ({user.full_name})"
                self.user_label.setText(user_text)
        
        # Update current view status
        current_index = self.stacked_widget.currentIndex()
        if current_index >= 0:
            view_names = [tr("subjects"), tr("create_schedule"), tr("view_schedule"), tr("progress")]
            if current_index < len(view_names):
                self.statusBar().showMessage(f"{tr('view')}: {view_names[current_index]}")
        
        # Update child widgets - they should reload their UI
        if hasattr(self, 'subject_manager') and hasattr(self.subject_manager, 'update_ui_language'):
            self.subject_manager.update_ui_language()
        elif hasattr(self, 'subject_manager'):
            self.subject_manager.load_subjects()
        if hasattr(self, 'schedule_viewer'):
            self.schedule_viewer.load_schedules()
        if hasattr(self, 'progress_tracker'):
            self.progress_tracker.load_schedules()
    
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(
            self, tr("exit"), tr("confirm_exit"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

