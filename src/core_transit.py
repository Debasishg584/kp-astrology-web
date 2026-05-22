import os
import re
import datetime
from .utils import get_resource_path
from .core_math import calculate_kp_ayanamsa

# Swiss Ephemeris for Transit Calculations
try:
    import swisseph as swe # type: ignore
    try:
        from src.swisseph_backend import SwissEphBackend
        SwissEphBackend.initialize()
    except ImportError:
        pass
    SWISSEPH_AVAILABLE = True
except ImportError:
    swe = None
    SWISSEPH_AVAILABLE = False


class DivineTransitEngine:
    """
    🔱 DIVINE TRANSIT ENGINE: Swiss Ephemeris Powered Transit Calculations
    
    Uses ephemeris files (seas_18.se1, semo_18.se1, sepl_18.se1) for:
    1. Precise planetary positions for any date
    2. Transit house placement (Whole Sign or Cusp-based)
    3. Nakshatra/Star Lord transit detection
    4. Planetary aspect calculations (conjunction, opposition, trine, square, sextile)
    5. Moon phase and transit speed analysis
    """
    
    # Planet IDs for Swiss Ephemeris
    PLANET_IDS = {
        "Sun": 0, "Mon": 1, "Moon": 1, "Mar": 4, "Mars": 4,
        "Mer": 2, "Mercury": 2, "Jup": 5, "Jupiter": 5,
        "Ven": 3, "Venus": 3, "Sat": 6, "Saturn": 6,
        "Rah": 10, "Rahu": 10, "Ket": -1, "Ketu": -1  # Ketu = Rahu + 180
    }
    
    # Nakshatra Lords (27 stars)
    NAKSHATRA_LORDS = [
        "Ket", "Ven", "Sun", "Mon", "Mar", "Rah", "Jup", "Sat", "Mer"
    ] * 3  # Repeat for 27 nakshatras
    
    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    # Sign Lords (for sign_lord output)
    SIGN_LORDS = {
        "Aries": "Mar", "Taurus": "Ven", "Gemini": "Mer", "Cancer": "Mon",
        "Leo": "Sun", "Virgo": "Mer", "Libra": "Ven", "Scorpio": "Mar",
        "Sagittarius": "Jup", "Capricorn": "Sat", "Aquarius": "Sat", "Pisces": "Jup"
    }
    
    # Vimshottari Dasha years (for sub-lord calculation)
    VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # Ket, Ven, Sun, Mon, Mar, Rah, Jup, Sat, Mer
    VIMSHOTTARI_TOTAL = 120
    
    def __init__(self, chart_data):
        self.chart_data = chart_data
        self.cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
        self.asc_sign = self.cusps.get(1, {}).get('sign', 'Aries')
        
        # Get asc sign index
        self.asc_sign_idx = 0
        for i, s in enumerate(self.SIGNS):
            if s == self.asc_sign or s[:3] == self.asc_sign[:3]:
                self.asc_sign_idx = i
                break
    
    def get_julian_day(self, date):
        """Convert datetime to Julian Day."""
        if not SWISSEPH_AVAILABLE:
            return 0
        return swe.julday(date.year, date.month, date.day, 12.0)
    
    def get_planet_position(self, planet, date):
        """
        Get planet position (longitude) for a given date.
        Returns: dict with longitude, sign, house, star_lord, is_retrograde
        """
        if not SWISSEPH_AVAILABLE:
            return None
        
        jd = self.get_julian_day(date)
        
        # KP Nirayana: Calculate ayanamsa for this date
        aya = calculate_kp_ayanamsa(date.year, date.month, date.day)
        
        # Handle Ketu (opposite of Rahu)
        if planet in ["Ket", "Ketu"]:
            rahu_pos = swe.calc_ut(jd, 10)  # Mean Node
            lon_tropical = (rahu_pos[0][0] + 180) % 360
            speed = -abs(rahu_pos[0][3])  # Ketu always retrograde
        elif planet in self.PLANET_IDS:
            pid = self.PLANET_IDS[planet]
            if pid >= 0:
                pos = swe.calc_ut(jd, pid)
                lon_tropical = pos[0][0]
                speed = pos[0][3]
            else:
                return None
        else:
            return None
        
        # Apply KP Nirayana correction: Sidereal = Tropical - Ayanamsa
        lon = (lon_tropical - aya) % 360
        
        # Calculate derived values
        sign_idx = int(lon / 30)
        sign = self.SIGNS[sign_idx]
        sign_lord = self._get_sign_lord(sign)
        house = self._longitude_to_house(lon)
        star_lord = self._get_nakshatra_lord(lon)
        sub_lord = self._get_sub_lord(lon)
        is_retro = speed < 0
        
        return {
            "longitude": lon,
            "sign": sign,
            "sign_index": sign_idx,
            "sign_lord": sign_lord,
            "house": house,
            "star_lord": star_lord,
            "sub_lord": sub_lord,
            "is_retrograde": is_retro,
            "speed": speed
        }
    
    def _longitude_to_house(self, longitude):
        """Convert longitude to house number using Whole Sign Houses."""
        transit_sign_idx = int(longitude / 30)
        house = ((transit_sign_idx - self.asc_sign_idx) % 12) + 1
        return house
    
    def _get_nakshatra_lord(self, longitude):
        """Get Nakshatra lord for a given longitude."""
        nak_span = 13.333333
        nak_idx = int(longitude / nak_span) % 27
        return self.NAKSHATRA_LORDS[nak_idx]
    
    def _get_sign_lord(self, sign):
        """Get sign lord (short key) for a given sign name."""
        return self.SIGN_LORDS.get(sign, '')
    
    def _get_sub_lord(self, longitude):
        """
        Get KP Sub Lord for a given longitude.
        Each 13°20' nakshatra is divided into 9 unequal sub-divisions
        proportional to Vimshottari Dasha periods.
        """
        nak_span = 13.333333  # 13°20' in decimal degrees
        # Position within the current nakshatra (0 to 13.333...)
        nak_idx = int(longitude / nak_span) % 27
        pos_in_nak = longitude % nak_span
        
        # Sub lord order starts from the nakshatra lord and cycles through 9 lords
        start_lord_idx = nak_idx % 9  # Which lord this nakshatra belongs to
        
        # Calculate sub-division boundaries proportional to dasha years
        cumulative = 0.0
        for i in range(9):
            lord_idx = (start_lord_idx + i) % 9
            sub_span = (self.VIMSHOTTARI_YEARS[lord_idx] / self.VIMSHOTTARI_TOTAL) * nak_span
            cumulative += sub_span
            if pos_in_nak < cumulative:
                return self.NAKSHATRA_LORDS[lord_idx]
        
        return self.NAKSHATRA_LORDS[start_lord_idx]  # Fallback
    
    def get_all_planet_positions(self, date):
        """Get all planet positions for a date."""
        positions = {}
        planet_list = ["Sun", "Mon", "Mar", "Mer", "Jup", "Ven", "Sat", "Rah", "Ket"]
        
        for planet in planet_list:
            pos = self.get_planet_position(planet, date)
            if pos:
                positions[planet] = pos
        
        return positions
    
    def check_transit_in_houses(self, date, planet, target_houses):
        """
        Check if planet is transiting through target houses on the date.
        Returns: (is_in_target, house_number, details)
        """
        pos = self.get_planet_position(planet, date)
        if not pos:
            return False, 0, "No ephemeris"
        
        house = pos["house"]
        if house in target_houses:
            return True, house, f"{planet} in House {house} ({pos['sign']})"
        return False, house, f"{planet} in House {house} - not in target"
    
    def check_transit_in_star(self, date, planet, target_star_lords):
        """
        Check if planet is transiting through star of target lords.
        Returns: (is_in_target, star_lord, details)
        """
        pos = self.get_planet_position(planet, date)
        if not pos:
            return False, "", "No ephemeris"
        
        star = pos["star_lord"]
        if star in target_star_lords:
            return True, star, f"{planet} in {star}'s star"
        return False, star, f"{planet} in {star}'s star - not in target"
    
    def check_conjunction(self, date, planet1, planet2, orb=10):
        """
        Check if two planets are in conjunction (same degree ± orb).
        Returns: (is_conjunct, degree_diff, details)
        """
        pos1 = self.get_planet_position(planet1, date)
        pos2 = self.get_planet_position(planet2, date)
        
        if not pos1 or not pos2:
            return False, 0, "No ephemeris"
        
        diff = abs(pos1["longitude"] - pos2["longitude"])
        if diff > 180:
            diff = 360 - diff
        
        if diff <= orb:
            return True, diff, f"{planet1}-{planet2} CONJUNCTION ({diff:.1f}°)"
        return False, diff, f"{planet1}-{planet2} apart ({diff:.1f}°)"
    
    def check_aspect(self, date, planet1, planet2, aspect_type="all", orb=10):
        """
        Check planetary aspects.
        aspect_type: 'conjunction', 'opposition', 'trine', 'square', 'sextile', 'all'
        """
        pos1 = self.get_planet_position(planet1, date)
        pos2 = self.get_planet_position(planet2, date)
        
        if not pos1 or not pos2:
            return None
        
        diff = abs(pos1["longitude"] - pos2["longitude"])
        if diff > 180:
            diff = 360 - diff
        
        aspects = {
            "conjunction": (0, orb),
            "opposition": (180, orb),
            "trine": (120, orb),
            "square": (90, orb),
            "sextile": (60, orb)
        }
        
        detected = []
        for asp_name, (exact, tolerance) in aspects.items():
            if aspect_type == "all" or aspect_type == asp_name:
                if abs(diff - exact) <= tolerance:
                    detected.append({
                        "aspect": asp_name,
                        "orb": abs(diff - exact),
                        "benefic": asp_name in ["trine", "sextile", "conjunction"]
                    })
        
        return detected
    
    def calculate_transit_score(self, date, md, ad, pd, death_houses=None, life_houses=None):
        """
        Calculate comprehensive transit score for a date.
        
        Returns: (score, details_list)
        """
        if not SWISSEPH_AVAILABLE:
            return 0, ["No SwissEph available"]
        
        if death_houses is None:
            death_houses = {2, 7, 8, 12}
        if life_houses is None:
            life_houses = {1, 5, 9, 11}
        
        score = 0
        details = []
        
        # Get all positions
        positions = self.get_all_planet_positions(date)
        
        # Get death-signifying planets from chart data
        death_planets = set()
        for p, sig in self.chart_data.get('planet_significators', []):
            if isinstance(sig, dict):
                result = sig.get('Result_Row', '')
                result_houses = set(int(h) for h in re.findall(r'\d+', str(result)))
                if result_houses & death_houses:
                    death_planets.add(p if isinstance(p, str) else sig.get('planet', ''))
        
        dasha_lords = [md, ad, pd]
        unique_lords = set(dasha_lords)
        
        # 1. Check Dasha Lords in Death Houses
        for lord in unique_lords:
            if lord in positions:
                house = positions[lord]["house"]
                if house == 12:
                    score += 30
                    details.append(f"{lord}@12H")
                elif house == 8:
                    score += 25
                    details.append(f"{lord}@8H")
                elif house in {2, 7}:
                    score += 20
                    details.append(f"{lord}@{house}H")
        
        # 2. Check MD-AD Conjunction in Death House
        if md in positions and ad in positions and md != ad:
            is_conj, diff, _ = self.check_conjunction(date, md, ad, orb=10)
            if is_conj:
                md_house = positions[md]["house"]
                if md_house == 12:
                    score += 30
                    details.append("MD-AD-CONJ@12H!")
                elif md_house in death_houses:
                    score += 20
                    details.append(f"MD-AD-CONJ@{md_house}H")
        
        # 3. Check Star Lord Transit
        for lord in unique_lords:
            if lord in positions:
                star = positions[lord]["star_lord"]
                if star in death_planets or star in unique_lords:
                    score += 15
                    details.append(f"{lord}_STAR={star}")
        
        # 4. Moon in Maraka
        if "Mon" in positions:
            moon_house = positions["Mon"]["house"]
            if moon_house in {2, 7}:
                score += 15
                details.append(f"MOON@{moon_house}H")
        
        # 5. Sun in 8/12
        if "Sun" in positions:
            sun_house = positions["Sun"]["house"]
            if sun_house in {8, 12}:
                score += 20
                details.append(f"SUN@{sun_house}H")
        
        # 6. Planets in 12th count
        planets_in_12 = sum(1 for p in positions.values() if p["house"] == 12)
        if planets_in_12 >= 3:
            score += 25
            details.append(f"{planets_in_12}_IN_12H!")
        elif planets_in_12 >= 2:
            score += 15
            details.append(f"{planets_in_12}_IN_12H")
        
        # 7. Life House Protection
        planets_in_5 = sum(1 for p in positions.values() if p["house"] == 5)
        if planets_in_5:
            score -= 20
            details.append("5H_SHIELD")
        
        return score, details
    
    def get_transit_summary(self, date, planets=None):
        """Get formatted transit summary for a date."""
        if planets is None:
            planets = ["Sun", "Mon", "Mar", "Mer", "Jup", "Ven", "Sat", "Rah", "Ket"]
        
        positions = self.get_all_planet_positions(date)
        
        lines = [f"🌟 DIVINE TRANSIT: {date.strftime('%d-%m-%Y')}"]
        lines.append("-" * 40)
        
        for planet in planets:
            if planet in positions:
                p = positions[planet]
                retro = " (R)" if p["is_retrograde"] else ""
                lines.append(f"  {planet:3}: {p['sign']:12} H{p['house']:2} Star={p['star_lord']}{retro}")
        
        return "\n".join(lines)
