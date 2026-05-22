import re
from typing import Dict, List, Set, Any

class DataConverter:
    # Sign offsets for converting relative to absolute longitude
    SIGN_OFFSETS = {
        "aries": 0, "taurus": 30, "gemini": 60, "cancer": 90,
        "leo": 120, "virgo": 150, "libra": 180, "scorpio": 210,
        "sagittarius": 240, "capricorn": 270, "aquarius": 300, "pisces": 330
    }
    
    @staticmethod
    def dms_to_float(dms_str):
        """Converts DMS string (e.g. 29° 23' 21") to float degree."""
        if not isinstance(dms_str, str): return 0.0
        # Try standard format: 29° 23' 21"
        match = re.match(r"(\d+)°\s*(\d+)'\s*(\d+)\"", dms_str)
        if match:
            d, m, s = map(int, match.groups())
            return d + m/60 + s/3600
        # Try alternate format: 29:23:21
        match2 = re.match(r"(\d+):(\d+):(\d+)", dms_str)
        if match2:
            d, m, s = map(int, match2.groups())
            return d + m/60 + s/3600
        # Try just degrees: 29.5
        try:
            return float(dms_str)
        except:
            return 0.0

    @staticmethod
    def get_sign_offset(sign_name: str) -> float:
        """Get the absolute degree offset for a zodiac sign."""
        if not sign_name:
            return 0.0
        sign_lower = sign_name.strip().lower()
        return DataConverter.SIGN_OFFSETS.get(sign_lower, 0.0)

    @staticmethod
    def get_absolute_longitude(data_obj) -> float:
        """
        RECTIFIED: Calculates ABSOLUTE longitude (0-360) by adding
        sign offset to relative longitude within sign.
        
        E.g., Sun at 13°26' in Virgo = 150° + 13.44° = 163.44°
        """
        # First try direct float keys that might already be absolute (0-360)
        # We include 'long', 'longitude', and 'lon' here because they are often
        # used to store absolute values, while 'longitude_dms' is relative.
        for key in ['abs_longitude', 'absolute_longitude', 'long', 'longitude', 'lon']:
            if key in data_obj:
                val = data_obj[key]
                if isinstance(val, (int, float)):
                    return float(val) % 360
                elif isinstance(val, str):
                    try:
                        return float(val) % 360
                    except:
                        pass
        
        # Get relative longitude within sign if no absolute key was found
        relative_long = 0.0
        
        # If no direct longitude, try DMS string
        if relative_long == 0.0:
            dms = data_obj.get('longitude_dms', '')
            if dms:
                relative_long = DataConverter.dms_to_float(dms)
        
        # Get sign offset and calculate absolute longitude
        sign = data_obj.get('sign', '')
        sign_offset = DataConverter.get_sign_offset(sign)
        
        absolute_long = (sign_offset + relative_long) % 360
        return absolute_long

    @staticmethod
    def convert_for_engine(chart_data):
        planets = []
        for p in chart_data.get('planetary_positions', []):
            # RECTIFIED: Calculate absolute longitude including sign offset
            p_long = DataConverter.get_absolute_longitude(p)
            planets.append({
                "name": p.get('planet', p.get('name', 'Unknown')),
                "long": p_long,
                "star": p.get('star_lord', p.get('star', '')),
                "sub": p.get('sub_lord', p.get('sub', '')),
                "sign": p.get('sign', '')
            })
        
        cusps = []
        for c in chart_data.get('house_cusps', []):
            # RECTIFIED: Calculate absolute longitude including sign offset
            c_long = DataConverter.get_absolute_longitude(c)
            cusps.append({
                "id": c.get('cusp', c.get('id', 0)),
                "long": c_long,
                "star": c.get('star_lord', c.get('star', '')),
                "sub": c.get('sub_lord', c.get('sub', '')),
                "sign": c.get('sign', ''),
                "sign_lord": c.get('sign_lord', '')
            })
        return planets, cusps


class ChartDecomposer:
    """
    🔱 CHART DECOMPOSER: Breaks ANY chart complexity into atomic signification units.
    
    DECOMPOSITION LAYERS:
    1. Planet → Star Lord → Sub Lord → Sub-Sub Lord
    2. House Cusp → Star Lord → Sub Lord  
    3. Result Row → Individual Houses
    4. Source Row → Ownership/Occupation/Aspect
    """
    
    def __init__(self, chart_data):
        self.chart_data = chart_data
        self.planet_sigs = {p['planet']: p for p in chart_data.get('planet_significators', [])}
        self.cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
        self.planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
        
        # Atomic signification matrix (9 planets x 12 houses)
        self.sig_matrix = [[0.0 for _ in range(12)] for _ in range(9)]
        self.planet_names = ["Sun", "Mon", "Mar", "Mer", "Jup", "Ven", "Sat", "Rah", "Ket"]
        
        # Build the matrix on initialization
        self._build_signification_matrix()
    
    def _parse_row(self, row_str):
        """Parse Source/Result Row string to set of house numbers."""
        if not row_str or not isinstance(row_str, str):
            return set()
        return set(int(h) for h in re.findall(r'\d+', row_str))
    
    def _build_signification_matrix(self):
        """Build 9x12 signification strength matrix for all planets."""
        for i, planet in enumerate(self.planet_names):
            sig = self.planet_sigs.get(planet, {})
            
            # Primary significations from Result Row (strongest - weight 1.0)
            result_houses = self._parse_row(sig.get('Result_Row', ''))
            for h in result_houses:
                if 1 <= h <= 12:
                    self.sig_matrix[i][h-1] += 1.0
            
            # Secondary significations from Source Row (medium - weight 0.7)
            source_houses = self._parse_row(sig.get('Source_Row', ''))
            for h in source_houses:
                if 1 <= h <= 12:
                    self.sig_matrix[i][h-1] += 0.7
    
    def get_planet_houses(self, planet, row_type="result"):
        """Get houses signified by a planet. row_type: 'result', 'source', or 'both'."""
        sig = self.planet_sigs.get(planet, {})
        if row_type == "result":
            return self._parse_row(sig.get('Result_Row', ''))
        elif row_type == "source":
            return self._parse_row(sig.get('Source_Row', ''))
        else:
            result = self._parse_row(sig.get('Result_Row', ''))
            source = self._parse_row(sig.get('Source_Row', ''))
            return result | source
    
    def get_house_significators(self, house_num):
        """Get all planets signifying a specific house with strength scores."""
        significators = []
        for i, planet in enumerate(self.planet_names):
            strength = self.sig_matrix[i][house_num - 1]
            if strength > 0:
                significators.append({
                    "planet": planet,
                    "strength": strength,
                    "is_primary": strength >= 1.0
                })
        return sorted(significators, key=lambda x: x['strength'], reverse=True)
    
    def get_cusp_sub_lord(self, cusp_num):
        """Get the Sub Lord of a specific cusp."""
        cusp = self.cusps.get(cusp_num, {})
        return cusp.get('sub_lord', '')
    
    def get_star_lord(self, planet):
        """Get the Star Lord of a planet."""
        p_data = self.planets.get(planet, {})
        return p_data.get('star_lord', '')
    
    def get_sub_lord(self, planet):
        """Get the Sub Lord of a planet."""
        p_data = self.planets.get(planet, {})
        return p_data.get('sub_lord', '')
    
    def decompose_planet(self, planet):
        """
        Full atomic decomposition of a planet's signification chain.
        Returns: dict with all levels of signification
        """
        p_data = self.planets.get(planet, {})
        sig = self.planet_sigs.get(planet, {})
        
        star_lord = p_data.get('star_lord', '')
        sub_lord = p_data.get('sub_lord', '')
        
        star_lord_houses = self.get_planet_houses(star_lord, 'both') if star_lord else set()
        sub_lord_houses = self.get_planet_houses(sub_lord, 'both') if sub_lord else set()
        
        return {
            "planet": planet,
            "sign": p_data.get('sign', ''),
            "star_lord": star_lord,
            "sub_lord": sub_lord,
            "planet_result_houses": self.get_planet_houses(planet, 'result'),
            "planet_source_houses": self.get_planet_houses(planet, 'source'),
            "star_lord_houses": star_lord_houses,
            "sub_lord_houses": sub_lord_houses,
            "all_signified_houses": self.get_planet_houses(planet, 'both') | star_lord_houses | sub_lord_houses,
            "is_retrograde": p_data.get('is_retrograde', False)
        }
    
    def get_atomic_intersection(self, planets, target_houses):
        """
        Find atomic-level intersection between planets and target houses.
        Returns strength score and matching details.
        """
        total_score = 0
        matches = []
        
        for planet in planets:
            decomp = self.decompose_planet(planet)
            
            # Check each level
            planet_result_match = decomp['planet_result_houses'] & target_houses
            planet_source_match = decomp['planet_source_houses'] & target_houses
            star_match = decomp['star_lord_houses'] & target_houses
            sub_match = decomp['sub_lord_houses'] & target_houses
            
            planet_score = 0
            level_details = []
            
            if planet_result_match:
                planet_score += len(planet_result_match) * 10
                level_details.append(f"Result:{list(planet_result_match)}")
            if planet_source_match:
                planet_score += len(planet_source_match) * 7
                level_details.append(f"Source:{list(planet_source_match)}")
            if star_match:
                planet_score += len(star_match) * 5
                level_details.append(f"Star:{list(star_match)}")
            if sub_match:
                planet_score += len(sub_match) * 3
                level_details.append(f"Sub:{list(sub_match)}")
            
            if planet_score > 0:
                matches.append({
                    "planet": planet,
                    "score": planet_score,
                    "details": " | ".join(level_details)
                })
                total_score += planet_score
        
        return total_score, matches
