import os
import sys

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path (str): Relative path to the resource (e.g., "data/cities.csv")
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In development, use the current working directory or script directory
        # We assume the script is running from the project root in dev mode
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def _UA_round(number, ndigits=0):
    """Robust rounding that handles potential None or invalid types."""
    if number is None: return 0
    try:
        if ndigits == 0:
            return int(round(float(number)))
        return round(float(number), ndigits)
    except (ValueError, TypeError):
        return 0
