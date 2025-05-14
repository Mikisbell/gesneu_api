# utils/safe_uuid.py
import uuid
import logging
from typing import Optional, Union, Any, List, Dict

logger = logging.getLogger(__name__)

class SafeUUID(uuid.UUID):
    """A UUID class that safely handles string methods like replace()."""
    
    def __new__(cls, *args, **kwargs):
        try:
            return super().__new__(cls, *args, **kwargs)
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Error creating UUID: {e}")
            # Return string if we can't make a UUID
            if args and isinstance(args[0], str):
                return args[0]
            return None
            
    def __str__(self):
        try:
            return str(super().__str__())
        except Exception as e:
            logger.warning(f"Error converting UUID to string: {e}")
            return ""
    
    # Define string methods to prevent AttributeError
    def replace(self, *args, **kwargs):
        """Handle string.replace() calls by first converting to string."""
        return str(self).replace(*args, **kwargs)
    
    def format(self, *args, **kwargs):
        """Handle string.format() calls by first converting to string."""
        return str(self).format(*args, **kwargs)
    
    def __getattr__(self, name):
        """Forward any unknown attribute access to the string representation."""
        try:
            return getattr(str(self), name)
        except (AttributeError, TypeError) as e:
            logger.warning(f"Error accessing attribute {name} on UUID: {e}")
            raise AttributeError(f"'SafeUUID' object has no attribute '{name}'")

# Monkey-patch the standard UUID class to add the replace method
# This will make existing UUIDs work with string operations
def patch_uuid_class():
    """Add string methods to the standard UUID class."""
    if not hasattr(uuid.UUID, 'replace'):
        def replace(self, *args, **kwargs):
            return str(self).replace(*args, **kwargs)
        uuid.UUID.replace = replace
    
    if not hasattr(uuid.UUID, 'format'):
        def format(self, *args, **kwargs):
            return str(self).format(*args, **kwargs)
        uuid.UUID.format = format

# Apply the patch when this module is imported
patch_uuid_class()
