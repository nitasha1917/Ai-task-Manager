"""
Input Validation: Validates and sanitizes all user inputs.
Provides security and data integrity checks.
"""

import re
from typing import Any, Optional, List, Dict, Union
from utils.logger import app_logger


class ValidationError(ValueError):
    """Custom exception for validation errors."""
    pass


class Validator:
    """Input validation utility class."""
    
    @staticmethod
    def validate_string(
        value: Any,
        field_name: str = "value",
        min_length: int = 1,
        max_length: int = 10000,
        allow_empty: bool = False
    ) -> str:
        """
        Validate and sanitize string input.
        
        Args:
            value: Value to validate
            field_name: Name of the field (for error messages)
            min_length: Minimum string length
            max_length: Maximum string length
            allow_empty: Whether to allow empty strings
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string, got {type(value).__name__}")
        
        # Strip whitespace
        value = value.strip()
        
        # Check if empty
        if not value and not allow_empty:
            raise ValidationError(f"{field_name} cannot be empty")
        
        # Check length
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters")
        
        # Remove potentially harmful characters (but allow normal text)
        # Remove null bytes and control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\t')
        
        app_logger.debug(f"Validated string: {field_name}")
        return value
    
    @staticmethod
    def validate_integer(
        value: Any,
        field_name: str = "value",
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        """
        Validate integer input.
        
        Args:
            value: Value to validate
            field_name: Name of the field
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated integer
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be an integer, got {type(value).__name__}")
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"{field_name} must not exceed {max_value}")
        
        app_logger.debug(f"Validated integer: {field_name} = {int_value}")
        return int_value
    
    @staticmethod
    def validate_float(
        value: Any,
        field_name: str = "value",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        """
        Validate float input.
        
        Args:
            value: Value to validate
            field_name: Name of the field
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated float
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a number, got {type(value).__name__}")
        
        if min_value is not None and float_value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and float_value > max_value:
            raise ValidationError(f"{field_name} must not exceed {max_value}")
        
        app_logger.debug(f"Validated float: {field_name} = {float_value}")
        return float_value
    
    @staticmethod
    def validate_email(value: str) -> str:
        """
        Validate email address.
        
        Args:
            value: Email address to validate
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: If validation fails
        """
        value = Validator.validate_string(value, "email", max_length=254)
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValidationError("Invalid email address format")
        
        app_logger.debug(f"Validated email: {value}")
        return value
    
    @staticmethod
    def validate_list(
        value: Any,
        field_name: str = "value",
        item_type: type = str,
        min_items: int = 0,
        max_items: int = 1000
    ) -> List:
        """
        Validate list input.
        
        Args:
            value: List to validate
            field_name: Name of the field
            item_type: Expected type of list items
            min_items: Minimum number of items
            max_items: Maximum number of items
            
        Returns:
            Validated list
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be a list")
        
        if len(value) < min_items:
            raise ValidationError(f"{field_name} must have at least {min_items} items")
        
        if len(value) > max_items:
            raise ValidationError(f"{field_name} must not exceed {max_items} items")
        
        # Validate item types if specified
        if item_type:
            for i, item in enumerate(value):
                if not isinstance(item, item_type):
                    raise ValidationError(
                        f"{field_name}[{i}] must be {item_type.__name__}, "
                        f"got {type(item).__name__}"
                    )
        
        app_logger.debug(f"Validated list: {field_name} with {len(value)} items")
        return value
    
    @staticmethod
    def validate_dict(
        value: Any,
        field_name: str = "value",
        required_keys: Optional[List[str]] = None,
        allowed_keys: Optional[List[str]] = None
    ) -> Dict:
        """
        Validate dictionary input.
        
        Args:
            value: Dictionary to validate
            field_name: Name of the field
            required_keys: List of required keys
            allowed_keys: List of allowed keys (if None, all keys allowed)
            
        Returns:
            Validated dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a dictionary")
        
        # Check required keys
        if required_keys:
            missing_keys = set(required_keys) - set(value.keys())
            if missing_keys:
                raise ValidationError(f"{field_name} missing required keys: {missing_keys}")
        
        # Check allowed keys
        if allowed_keys:
            extra_keys = set(value.keys()) - set(allowed_keys)
            if extra_keys:
                raise ValidationError(f"{field_name} has unexpected keys: {extra_keys}")
        
        app_logger.debug(f"Validated dictionary: {field_name} with {len(value)} keys")
        return value
    
    @staticmethod
    def validate_goal(goal: str) -> str:
        """
        Validate study goal input.
        
        Args:
            goal: Study goal text
            
        Returns:
            Validated goal
            
        Raises:
            ValidationError: If validation fails
        """
        return Validator.validate_string(
            goal,
            "study_goal",
            min_length=5,
            max_length=2000
        )
    
    @staticmethod
    def validate_study_duration(days: Union[int, float]) -> int:
        """
        Validate study duration in days.
        
        Args:
            days: Number of days
            
        Returns:
            Validated number of days
            
        Raises:
            ValidationError: If validation fails
        """
        return Validator.validate_integer(
            days,
            "study_duration",
            min_value=1,
            max_value=365
        )
    
    @staticmethod
    def validate_hours_per_day(hours: Union[int, float]) -> float:
        """
        Validate daily study hours.
        
        Args:
            hours: Number of hours per day
            
        Returns:
            Validated hours per day
            
        Raises:
            ValidationError: If validation fails
        """
        return Validator.validate_float(
            hours,
            "hours_per_day",
            min_value=0.5,
            max_value=12.0
        )
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal and other attacks.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and dangerous characters
        filename = re.sub(r'[/\\:<>"|?*]', '', filename)
        # Remove leading/trailing dots
        filename = filename.strip('.')
        # Limit length
        filename = filename[:255]
        return filename


# Convenience functions
def validate_string(value: str, **kwargs) -> str:
    """Validate string input."""
    return Validator.validate_string(value, **kwargs)


def validate_integer(value: int, **kwargs) -> int:
    """Validate integer input."""
    return Validator.validate_integer(value, **kwargs)


def validate_float(value: float, **kwargs) -> float:
    """Validate float input."""
    return Validator.validate_float(value, **kwargs)


def validate_goal(goal: str) -> str:
    """Validate study goal."""
    return Validator.validate_goal(goal)
