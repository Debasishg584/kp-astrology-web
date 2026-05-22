# -*- coding: utf-8 -*-
"""
Path Resolution Utility for PyInstaller Compatibility

This module provides a consistent way to resolve paths that works both:
1. During development (running from source)
2. When bundled as a PyInstaller executable

Usage:
    from src.path_utils import get_resource_path, get_user_data_path
    
    # Get path to bundled data file (read-only)
    csv_path = get_resource_path('data/cities.csv')
    
    # Get path to assets folder (read-only)
    assets_path = get_resource_path('assets')
    
    # Get path for saving user data (writable)
    user_file = get_user_data_path('chart_data.json')
"""

import os
import sys

def is_frozen():
    """Check if running as a PyInstaller bundle."""
    # In OneDir mode, only sys.frozen is set. _MEIPASS is strictly for OneFile mode.
    return getattr(sys, 'frozen', False)

def get_base_path():
    """
    Get the base path of the application.
    
    When running as a PyInstaller bundle (OneDir):
    - Resources are usually in the '_internal' folder next to the executable (PyInstaller v6+)
    - Or in the same folder as executable (older versions)
    
    When running from source:
    - Returns the project root directory.
    """
    if is_frozen():
        # Running as a PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # OneFile mode (not currently used but safe to handle)
            return sys._MEIPASS
        else:
            # OneDir mode
            # The executable is in the root app folder
            exe_dir = os.path.dirname(sys.executable)
            
            # Check for _internal folder (standard in PyInstaller 6+)
            internal_dir = os.path.join(exe_dir, '_internal')
            if os.path.exists(internal_dir):
                return internal_dir
            
            # Fallback to exe dir if _internal doesn't exist
            return exe_dir
    else:
        # Running from source - go up from src/ to project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_resource_path(relative_path):
    """
    Get the absolute path to a bundled resource file (READ-ONLY).
    """
    base_path = get_base_path()
    return os.path.join(base_path, relative_path)

def get_user_data_path(filename=None):
    """
    Get the path for user data files (WRITABLE).
    """
    if is_frozen():
        # Use AppData for installed application
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        user_data_dir = os.path.join(appdata, 'DivyaDrishti', 'data')
    else:
        # Use project data folder for development
        user_data_dir = os.path.join(get_base_path(), 'data')
    
    # Ensure directory exists
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir, exist_ok=True)
    
    if filename:
        return os.path.join(user_data_dir, filename)
    return user_data_dir

# Pre-computed common paths
BASE_PATH = get_base_path()
DATA_PATH = os.path.join(BASE_PATH, 'data')
ASSETS_PATH = os.path.join(BASE_PATH, 'assets')
EPHE_PATH = os.path.join(BASE_PATH, 'ephe')
PREDICTION_PATH = os.path.join(BASE_PATH, 'prediction')

# User data path (writable even when installed)
USER_DATA_PATH = get_user_data_path()
