# utils/uuid_utils.py
import uuid
import logging
from typing import Optional, Union, Any

logger = logging.getLogger(__name__)

def safe_uuid(value: Optional[Union[str, uuid.UUID]]) -> Optional[uuid.UUID]:
    """Convert a string to UUID safely, or return the UUID if it's already a UUID.
    Return None if input is None or invalid."""
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Failed to convert value '{value}' to UUID: {e}")
        return None

def safe_str_uuid(value: Optional[Union[str, uuid.UUID]]) -> Optional[str]:
    """Convert a UUID to string safely, or return the string if it's already a string.
    Return None if input is None."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return str(value)
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Failed to convert UUID '{value}' to string: {e}")
        return None

def safe_dict_uuid_to_str(data: dict) -> dict:
    """Recursively convert all UUID values in a dict to strings."""
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, uuid.UUID):
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = safe_dict_uuid_to_str(value)
        elif isinstance(value, list):
            result[key] = [
                str(item) if isinstance(item, uuid.UUID) 
                else safe_dict_uuid_to_str(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result
