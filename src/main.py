"""Main entry point for the application"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from pathlib import Path
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger

logger = setup_logger()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Military Training Plan")
    app.setOrganizationName("Military Training")
    
    # Set application icon
    try:
        base_path = Path(__file__).parent.parent
        icon_path = base_path / "resources" / "icons" / "logo.jpg"
        if not icon_path.exists():
            icon_path = base_path / "logo.jpg"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            logger.info(f"Application icon set from: {icon_path}")
    except Exception as e:
        logger.warning(f"Could not set application icon: {e}")
    
    # Show splash screen
    splash = None
    try:
        base_path = Path(__file__).parent.parent
        logo_path = base_path / "resources" / "icons" / "logo.jpg"
        if not logo_path.exists():
            logo_path = base_path / "logo.jpg"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            # Scale if too large
            if pixmap.width() > 400 or pixmap.height() > 400:
                pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
            splash = QSplashScreen(pixmap)
            splash.show()
            app.processEvents()
    except Exception as e:
        logger.warning(f"Could not show splash screen: {e}")
    
    # Create default user if needed
    from src.services.auth_service import AuthService
    from src.services.file_service import FileService
    
    file_service = FileService()
    auth_service = AuthService(file_service)
    
    # Check if any users exist, if not create default
    users = file_service.load_all_users()
    if not users:
        logger.info("No users found, creating default user")
        auth_service.create_user("admin", "admin", "Administrator")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Close splash screen
    if splash:
        splash.finish(window)
    
    logger.info("Application started")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

