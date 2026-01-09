"""Internationalization support"""

import json
from pathlib import Path
from typing import Dict, Optional

# Default language
DEFAULT_LANGUAGE = "vi"
SUPPORTED_LANGUAGES = ["vi", "en"]

# Translation cache
_translations: Dict[str, Dict[str, str]] = {}
_current_language = DEFAULT_LANGUAGE


def load_translations(language: str = DEFAULT_LANGUAGE) -> Dict[str, str]:
    """Load translations for a language"""
    if language in _translations:
        return _translations[language]
    
    # Find translation file
    base_path = Path(__file__).parent.parent.parent
    translation_file = base_path / "resources" / "translations" / f"{language}.json"
    
    if not translation_file.exists():
        # Fallback to default
        if language != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        return {}
    
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        _translations[language] = translations
        return translations
    except Exception as e:
        print(f"Error loading translations: {e}")
        return {}


def set_language(language: str):
    """Set current language"""
    global _current_language
    if language in SUPPORTED_LANGUAGES:
        _current_language = language
        load_translations(language)


def get_language() -> str:
    """Get current language"""
    return _current_language


def tr(key: str, default: Optional[str] = None) -> str:
    """Translate a key"""
    translations = load_translations(_current_language)
    return translations.get(key, default or key)


# Initialize translations
load_translations(DEFAULT_LANGUAGE)

