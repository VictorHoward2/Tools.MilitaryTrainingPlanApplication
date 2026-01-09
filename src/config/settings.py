"""Application settings"""

from pathlib import Path
from typing import Optional
import json


class Settings:
    """Application settings manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings"""
        if config_file is None:
            base_path = Path(__file__).parent.parent.parent
            config_file = base_path / "src" / "data" / "settings.json"
        
        self.config_file = Path(config_file)
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Load settings from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save_settings(self):
        """Save settings to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set setting value"""
        self.settings[key] = value
        self.save_settings()
    
    def get_language(self) -> str:
        """Get current language"""
        return self.get("language", "vi")
    
    def set_language(self, language: str):
        """Set current language"""
        self.set("language", language)

