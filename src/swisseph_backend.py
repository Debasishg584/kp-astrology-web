import os
try:
    import swisseph as swe # type: ignore
except ImportError:
    swe = None

from src.utils import get_resource_path

class SwissEphBackend:
    _is_initialized = False

    @classmethod
    def is_available(cls):
        """Check if Swiss Ephemeris module is functional."""
        return swe is not None

    @staticmethod
    def initialize():
        """Centralized initialization for Swiss Ephemeris."""
        if swe and not SwissEphBackend._is_initialized:
            try:
                # Use robust resource path
                full_path = get_resource_path('ephe')
                
                # Check different possible locations for ephe
                if not os.path.exists(full_path):
                    # Fallback to local 'ephe' if get_resource_path fails
                    full_path = os.path.abspath('ephe')
                
                if os.path.exists(full_path):
                    swe.set_ephe_path(full_path)
                
                # Set default SID mode (KP standard)
                swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
                SwissEphBackend._is_initialized = True
            except Exception as e:
                from src.utils.logger import app_logger
                app_logger.error(f"Swiss Ephemeris initialization failed: {e}")

    def __init__(self, ephe_path="ephe"):
        SwissEphBackend.initialize()
        if swe:
            self.planet_map = {
                "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
                "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
                "Venus": swe.VENUS, "Saturn": swe.SATURN,
                "Rahu": swe.MEAN_NODE, "Uranus": swe.URANUS,
                "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
            }

    def calculate_kp_ayanamsa(self, year, month, day):
        """
        Calculate KP Ayanamsa using Swiss Ephemeris.
        
        Uses swe.SIDM_KRISHNAMURTI for official Krishnamurti Ayanamsa.
        Falls back to manual calculation if Swiss Ephemeris fails.
        """
        if swe:
            try:
                jd = swe.julday(year, month, day, 12.0)
                swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
                return float(swe.get_ayanamsa_ut(jd))
            except Exception:
                pass
        
        # Fallback: Corrected manual calculation with leap year correction
        days_in_year = 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
        dec_year = year + (month - 1) / 12 + (day - 1) / days_in_year
        return 23.760240 + (dec_year - 2000) * (50.2388475 / 3600.0)

    def get_julian_day(self, year, month, day, hour, minute, timezone, second=0):
        dec_hour = hour + (minute / 60.0) + (second / 3600.0) - timezone
        return swe.julday(year, month, day, dec_hour)

    def get_all_positions(self, jd, lat, lon, year, month, day):
        # Wrapper for backward compatibility
        extended_planets, cusps, ayanamsa = self.get_extended_positions(jd, lat, lon, year, month, day)
        # Convert detailed planets back to simple {name: lon} dict
        simple_planets = {name: data['longitude'] for name, data in extended_planets.items()}
        return simple_planets, cusps, ayanamsa

    def get_extended_positions(self, jd, lat, lon, year, month, day):
        if not swe: return {}, {}, 0.0
        
        try:
            swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
            ayanamsa = swe.get_ayanamsa_ut(jd)
        except Exception:
            ayanamsa = self.calculate_kp_ayanamsa(year, month, day)
        
        # Planets
        planets = {}
        for name, pid in self.planet_map.items():
            res = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
            trop = res[0][0]
            speed = res[0][3]
            sid = (trop - ayanamsa) % 360
            planets[name] = {
                "longitude": sid,
                "speed": speed,
                "is_retrograde": speed < 0
            }
            
        # Ketu Logic (Always opposite Rahu, same speed/retro status)
        rahu = planets["Rahu"]
        planets["Ketu"] = {
            "longitude": (rahu["longitude"] + 180) % 360,
            "speed": rahu["speed"],
            "is_retrograde": rahu["is_retrograde"]
        }

        # Houses
        cusps_trop, _ = swe.houses(jd, lat, lon, b'P')
        cusps = {}
        
        # Handle tuple index issue (0-11 vs 0-12)
        if len(cusps_trop) == 13:
            for i in range(1, 13):
                cusps[i] = (cusps_trop[i] - ayanamsa) % 360
        else:
            for i in range(12):
                cusps[i+1] = (cusps_trop[i] - ayanamsa) % 360
            
        return planets, cusps, ayanamsa