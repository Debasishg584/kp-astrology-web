"""
Data validation pipeline for chart input data.
Ensures garbage data never reaches the Swiss Ephemeris calculation engine.
"""
import re
import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when chart input data fails validation."""
    pass


class ChartInputValidator:
    """
    Validates birth chart input data before it reaches the calculation engine.
    
    Usage:
        validator = ChartInputValidator()
        errors = validator.validate_birth_input(date_str, time_str, lat, lon, tz_str)
        if errors:
            raise ValidationError("; ".join(errors))
    """

    DATE_PATTERN = re.compile(r'^(\d{1,2})-(\d{1,2})-(\d{4})$')
    TIME_PATTERN = re.compile(r'^(\d{1,2}):(\d{2}):(\d{2})$')
    TZ_PATTERN = re.compile(r'^[+-]?\d{1,2}:\d{2}$')

    @staticmethod
    def validate_birth_input(
        date_str: str,
        time_str: str,
        lat: float,
        lon: float,
        tz_str: str
    ) -> List[str]:
        """
        Validate all birth chart inputs. Returns a list of error messages.
        Empty list means all inputs are valid.
        """
        errors: List[str] = []

        # Date validation
        if not date_str or not date_str.strip():
            errors.append("Date of birth is required")
        else:
            m = ChartInputValidator.DATE_PATTERN.match(date_str.strip())
            if not m:
                errors.append(f"Invalid date format '{date_str}'. Expected DD-MM-YYYY")
            else:
                dd, mm, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if mm < 1 or mm > 12:
                    errors.append(f"Month {mm} is out of range (1-12)")
                if dd < 1 or dd > 31:
                    errors.append(f"Day {dd} is out of range (1-31)")
                if yy < 1 or yy > 2200:
                    errors.append(f"Year {yy} is out of range (1-2200)")

        # Time validation
        if not time_str or not time_str.strip():
            errors.append("Time of birth is required")
        else:
            m = ChartInputValidator.TIME_PATTERN.match(time_str.strip())
            if not m:
                errors.append(f"Invalid time format '{time_str}'. Expected HH:MM:SS")
            else:
                hh, mi, ss = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if hh < 0 or hh > 23:
                    errors.append(f"Hour {hh} is out of range (0-23)")
                if mi < 0 or mi > 59:
                    errors.append(f"Minute {mi} is out of range (0-59)")
                if ss < 0 or ss > 59:
                    errors.append(f"Second {ss} is out of range (0-59)")

        # Latitude validation
        if lat < -90.0 or lat > 90.0:
            errors.append(f"Latitude {lat} is out of range (-90 to 90)")

        # Longitude validation
        if lon < -180.0 or lon > 180.0:
            errors.append(f"Longitude {lon} is out of range (-180 to 180)")

        # Timezone validation
        if not tz_str or not tz_str.strip():
            errors.append("Timezone is required")
        else:
            tz_clean = tz_str.strip()
            if not ChartInputValidator.TZ_PATTERN.match(tz_clean):
                # Allow timezone names like "Asia/Kolkata" as well
                if '/' not in tz_clean:
                    errors.append(f"Invalid timezone format '{tz_str}'. Expected +HH:MM or -HH:MM or Region/City")

        if errors:
            logger.warning(f"Input validation failed: {errors}")

        return errors

    @staticmethod
    def validate_chart_data(data: Dict[str, Any]) -> List[str]:
        """
        Validate calculated chart data before it is used for predictions.
        Ensures planets and cusps exist and contain valid numbers.
        """
        errors: List[str] = []

        if not isinstance(data, dict):
            return ["Chart data is not a dictionary"]

        # Check planets
        planets = data.get("planets", {})
        if not planets:
            errors.append("No planetary positions found in chart data")
        else:
            required_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            for p in required_planets:
                if p not in planets:
                    errors.append(f"Missing planet: {p}")
                else:
                    val = planets[p]
                    if not isinstance(val, (int, float)):
                        errors.append(f"Planet {p} has non-numeric longitude: {val}")
                    elif val < 0 or val >= 360:
                        errors.append(f"Planet {p} longitude {val} out of range (0-360)")

        # Check cusps
        cusps = data.get("cusps", {})
        if not cusps:
            errors.append("No house cusps found in chart data")
        else:
            for i in range(1, 13):
                key = i
                if key not in cusps and str(key) not in cusps:
                    errors.append(f"Missing cusp for house {i}")

        # Check ayanamsa
        aya = data.get("ayanamsa", None)
        if aya is None:
            errors.append("Ayanamsa value is missing")
        elif not isinstance(aya, (int, float)):
            errors.append(f"Ayanamsa is not numeric: {aya}")
        elif aya < 20 or aya > 30:
            errors.append(f"Ayanamsa {aya} is suspicious (expected 20-30 for current era)")

        if errors:
            logger.warning(f"Chart data validation failed: {errors}")

        return errors

    @staticmethod
    def validate_horary_number(num: int) -> List[str]:
        """Validate KP horary number (1-249)."""
        errors: List[str] = []
        if not isinstance(num, int):
            errors.append(f"Horary number must be an integer, got {type(num).__name__}")
        elif num < 1 or num > 249:
            errors.append(f"Horary number {num} is out of range (1-249)")
        return errors
