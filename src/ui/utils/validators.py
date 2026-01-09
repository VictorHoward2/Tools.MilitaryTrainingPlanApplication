"""Input validators"""

from PySide6.QtGui import QValidator
from typing import Optional


class SubjectNameValidator(QValidator):
    """Validator for subject names"""
    
    def validate(self, input_text: str, pos: int):
        """Validate subject name"""
        if not input_text.strip():
            return QValidator.Intermediate, input_text, pos
        
        if len(input_text.strip()) < 1:
            return QValidator.Invalid, input_text, pos
        
        return QValidator.Acceptable, input_text, pos


class DurationValidator(QValidator):
    """Validator for duration values"""
    
    def validate(self, input_text: str, pos: int):
        """Validate duration"""
        if not input_text:
            return QValidator.Intermediate, input_text, pos
        
        try:
            value = float(input_text)
            if value < 0 or value > 24:
                return QValidator.Invalid, input_text, pos
            return QValidator.Acceptable, input_text, pos
        except ValueError:
            return QValidator.Invalid, input_text, pos

