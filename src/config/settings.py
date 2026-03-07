"""Application settings"""

from pathlib import Path
from typing import Optional, Dict
import json

from ..utils.season_schedule import (
    DEFAULT_SUMMER_START_MONTH, DEFAULT_SUMMER_START_DAY,
    DEFAULT_SUMMER_END_MONTH, DEFAULT_SUMMER_END_DAY,
)


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
    
    # Season (summer/winter) date range
    def get_summer_start_month(self) -> int:
        return int(self.get("summer_start_month", DEFAULT_SUMMER_START_MONTH))
    
    def get_summer_start_day(self) -> int:
        return int(self.get("summer_start_day", DEFAULT_SUMMER_START_DAY))
    
    def get_summer_end_month(self) -> int:
        return int(self.get("summer_end_month", DEFAULT_SUMMER_END_MONTH))
    
    def get_summer_end_day(self) -> int:
        return int(self.get("summer_end_day", DEFAULT_SUMMER_END_DAY))
    
    def set_summer_range(self, start_month: int, start_day: int, end_month: int, end_day: int):
        """Set summer season date range (rest of year is winter)."""
        self.set("summer_start_month", start_month)
        self.set("summer_start_day", start_day)
        self.set("summer_end_month", end_month)
        self.set("summer_end_day", end_day)

    # Schedule times per season (stored as "HH:MM", optional overrides)
    _TIME_KEYS = ("morning_start", "morning_end", "break_start", "break_end", "afternoon_start", "afternoon_end")

    def get_season_time(self, season: str, key: str) -> Optional[str]:
        """Get time override for season (e.g. 'summer', 'morning_start') -> '06:30' or None."""
        k = f"{season}_{key}"
        return self.get(k)

    def set_season_time(self, season: str, key: str, value: str):
        """Set time override (value = 'HH:MM')."""
        self.set(f"{season}_{key}", value)

    def get_all_season_times(self, season: str) -> Dict[str, Optional[str]]:
        """Get all time overrides for a season as dict key -> 'HH:MM' (missing keys = use default)."""
        return {k: self.get(f"{season}_{k}") for k in self._TIME_KEYS}

    def set_all_season_times(self, season: str, times: Dict[str, str]):
        """Set all time overrides for a season (times: key -> 'HH:MM')."""
        for k in self._TIME_KEYS:
            if k in times and times[k]:
                self.set(f"{season}_{k}", times[k])

