import pandas as pd
from datetime import datetime
import pytz
import os
from src.utils import get_resource_path

class LocationManager:
    """
    Manages location lookups from the cities.csv database.
    Handles City Search and Timezone Offset calculations.
    """

    def __init__(self, csv_path="data/cities.csv"):
        """
        Initialize by loading the cities database.
        """
        # robust path handling
        # robust path handling
        if not os.path.isabs(csv_path):
            csv_path = get_resource_path(csv_path)

        try:
            # Load specific columns to save memory, or load all if needed
            # Based on your file structure: name, latitude, longitude, timezone, country_name
            self.df = pd.read_csv(csv_path)
            
            # Ensure city names are string type for searching
            self.df['name'] = self.df['name'].astype(str)
            
            print(f"Location Database Loaded: {len(self.df)} cities found.")
            
        except FileNotFoundError:
            print(f"CRITICAL ERROR: {csv_path} not found.")
            self.df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading location database: {e}")
            self.df = pd.DataFrame()

    def search_city(self, city_name):
        """
        Search for a city by name (Case-Insensitive).
        Returns the first best match as a dictionary.
        """
        if self.df.empty:
            return None
        
        # 1. Try Exact Match First (Case Insensitive)
        exact_match = self.df[self.df['name'].str.lower() == city_name.lower()]
        if not exact_match.empty:
            return exact_match.iloc[0].to_dict()
            
        # 2. Try 'Contains' Match
        mask = self.df['name'].str.contains(city_name, case=False, na=False)
        results = self.df[mask]
        
        if not results.empty:
            # Return the first result found
            # In a full GUI, you might return list(results.to_dict('records')) to show a dropdown
            return results.iloc[0].to_dict()
            
        return None

    def get_timezone_offset(self, timezone_str, date_obj=None):
        """
        Converts a timezone string (e.g., 'Asia/Kolkata') to a float offset (e.g., 5.5).
        
        IMPORTANT: This accounts for Daylight Saving Time (DST) if a date_obj is provided.
        If date_obj is None, it uses the current date.
        """
        try:
            if pd.isna(timezone_str) or not timezone_str:
                return 0.0
                
            tz = pytz.timezone(timezone_str)
            
            # If no date provided, use current time
            if date_obj is None:
                target_dt = datetime.now()
            else:
                target_dt = date_obj

            # We must localize the naive datetime (wall time) to the specific timezone
            # to correctly determine if DST was active at that specific moment.
            if target_dt.tzinfo is None:
                # "localize" assumes the time passed IS the local time in that zone
                localized_dt = tz.localize(target_dt)
            else:
                # If already aware, convert to target zone
                localized_dt = target_dt.astimezone(tz)

            # Calculate offset in seconds and convert to hours
            offset_seconds = localized_dt.utcoffset().total_seconds()
            offset_hours = offset_seconds / 3600.0
            
            return offset_hours

        except pytz.UnknownTimeZoneError:
            print(f"Error: Unknown timezone '{timezone_str}'")
            return 0.0
        except Exception as e:
            print(f"Timezone calc error: {e}")
            return 0.0

# Example Usage Helper
if __name__ == "__main__":
    # Test the module
    loc = LocationManager("data/cities.csv")
    city = loc.search_city("New York")
    if city:
        print(f"Found: {city['name']}, {city['country_name']}")
        print(f"Lat: {city['latitude']}, Lon: {city['longitude']}")
        print(f"Timezone: {city['timezone']}")
        
        # Test Offset for a specific date (e.g., Summer in NY = DST active)
        test_date = datetime(2023, 7, 1, 12, 0, 0) 
        offset = loc.get_timezone_offset(city['timezone'], test_date)
        print(f"Offset on {test_date}: {offset}")