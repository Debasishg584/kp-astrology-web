import json
import os
import logging
from typing import Dict, Any, Optional
from src.utils import get_resource_path  # type: ignore[import]

logger = logging.getLogger(__name__)

class DataManager:
    """Service class to handle all JSON loading, saving, and configuration management."""

    @staticmethod
    def load_json(filename: str, subfolder: str = "data") -> Dict[str, Any]:
        """Generic method to load a JSON file from the resources directory."""
        try:
            path = get_resource_path(os.path.join(subfolder, filename))
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            print(f"Error loading {filename}: {e}")
        return {}

    @staticmethod
    def save_json(data: Dict[str, Any], filename: str, subfolder: str = "data") -> bool:
        """Generic method to save data to a JSON file in the resources directory."""
        try:
            path = get_resource_path(os.path.join(subfolder, filename))
            # Ensure the directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            print(f"Error saving {filename}: {e}")
            return False

    @staticmethod
    def load_national_charts() -> Dict[str, Any]:
        """Load national and state charts from external JSON."""
        return DataManager.load_json("mundane_data.json")

    @staticmethod
    def get_chart_data_filename(mode: str) -> str:
        """Determine the chart data filename based on current app mode."""
        if mode == "mundane":
            return "chart_data(M).json"
        elif mode == "horary":
            return "chart_data(H).json"
        elif mode == "match_making":
            return "chart_data(CM).json"
        else:
            return "chart_data.json"
