"""
CUSP-INTERLINK ENGINE - BHAV SANDHI HANDLING
UAKP Logic: Planets at cusp boundaries belong to BOTH houses

When a planet is within 2 degrees of a cusp boundary (bhav sandhi), it carries the 
significations of BOTH adjacent houses. This is critical for accurate predictions.

Example: If Mars is at 29.58 degrees of House 4 (cusp 5 is at 0.5 degrees), Mars belongs to 
BOTH House 4 AND House 5.
"""

import re
from typing import Dict, List, Tuple, Optional, Set


class CuspInterlinkEngine:
    """
    CUSP-INTERLINK LOGIC ENGINE
    
    Handles planets at bhav sandhi (cusp boundaries) by:
    1. Detecting if a planet is within SANDHI_ORB of any cusp
    2. Assigning multiple houses to such planets
    3. Tracking cusp sub-lord connections across houses
    """
    
    SANDHI_ORB = 2.0  # Degrees within cusp boundary (Strict setting)
    
    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    def __init__(self, cusps: Dict):
        """
        Initialize with cusp data.
        
        Args:
            cusps: Dict of cusp data {cusp_num: {sign, longitude_dms, sub_lord, ...}}
        """
        self.cusps = cusps
        self.cusp_degrees = self._build_cusp_degrees()
    
    def _parse_longitude(self, lon_str: str) -> float:
        """Parse longitude string like '29 deg 23 min 21 sec' to decimal degrees."""
        if not lon_str or not isinstance(lon_str, str):
            return 0.0
        
        # Try DMS format: 29° 23' 21"
        match = re.match(r"(\d+)[°]\s*(\d+)[\']\s*(\d+)[\"]*", lon_str)
        if match:
            d, m, s = map(int, match.groups())
            return d + m/60 + s/3600
        
        # Try alternate format with symbols
        match2 = re.match(r"(\d+)\s*(\d+)\s*(\d+)", lon_str)
        if match2:
            d, m, s = map(int, match2.groups())
            return d + m/60 + s/3600
        
        # Try decimal
        try:
            return float(lon_str)
        except Exception:
            return 0.0
    
    def _get_sign_offset(self, sign: str) -> float:
        """Get absolute degree offset for a zodiac sign."""
        sign_lower = sign.lower().strip() if sign else ""
        for i, s in enumerate(self.SIGNS):
            if s.lower() == sign_lower or s.lower()[:3] == sign_lower[:3]:
                return i * 30
        return 0.0
    
    def _build_cusp_degrees(self) -> Dict[int, float]:
        """Build dict of absolute cusp degrees {cusp_num: absolute_degree}."""
        cusp_degrees = {}
        
        for cusp_num in range(1, 13):
            cusp_data = self.cusps.get(cusp_num, {})
            
            # Try to get absolute longitude
            if 'absolute_longitude' in cusp_data:
                cusp_degrees[cusp_num] = float(cusp_data['absolute_longitude']) % 360
                continue
            
            # Calculate from sign + longitude_dms
            sign = cusp_data.get('sign', '')
            lon_dms = cusp_data.get('longitude_dms', '0')
            
            sign_offset = self._get_sign_offset(sign)
            relative_deg = self._parse_longitude(lon_dms)
            
            cusp_degrees[cusp_num] = (sign_offset + relative_deg) % 360
        
        return cusp_degrees
    
    def is_bhav_sandhi(self, planet_longitude: float) -> Tuple[bool, Optional[int], float]:
        """
        Check if planet is at bhav sandhi (cusp boundary).
        
        Returns:
            (is_sandhi, cusp_number, orb_from_cusp)
        """
        planet_longitude = planet_longitude % 360
        
        for cusp_num, cusp_deg in self.cusp_degrees.items():
            diff = abs(planet_longitude - cusp_deg)
            if diff > 180:
                diff = 360 - diff
            
            if diff <= self.SANDHI_ORB:
                return True, cusp_num, diff
        
        return False, None, 999.0
    
    def get_planet_house_placidus(self, planet_longitude: float) -> int:
        """
        Get primary house using Placidus cusp boundaries.
        
        Returns:
            House number (1-12)
        """
        planet_longitude = planet_longitude % 360
        
        # Sort cusps by degree for proper boundary detection
        sorted_cusps = sorted(self.cusp_degrees.items(), key=lambda x: x[1])
        
        for i in range(12):
            current_cusp = sorted_cusps[i][0]
            current_deg = sorted_cusps[i][1]
            next_deg = sorted_cusps[(i + 1) % 12][1]
            
            # Handle wrap-around at 360/0
            if next_deg < current_deg:
                if planet_longitude >= current_deg or planet_longitude < next_deg:
                    return current_cusp
            else:
                if current_deg <= planet_longitude < next_deg:
                    return current_cusp
        
        return 1  # Default fallback
    
    def get_planet_houses_with_sandhi(self, planet_longitude: float) -> List[int]:
        """
        Get ALL houses a planet belongs to (including bhav sandhi).
        
        Returns:
            List of house numbers (1 or 2 houses)
        """
        primary_house = self.get_planet_house_placidus(planet_longitude)
        houses = [primary_house]
        
        is_sandhi, cusp_num, orb = self.is_bhav_sandhi(planet_longitude)
        
        if is_sandhi and cusp_num:
            # Determine which house is on the other side of the cusp
            cusp_deg = self.cusp_degrees.get(cusp_num, 0)
            planet_longitude = planet_longitude % 360
            
            # If planet is BEFORE the cusp, add previous house
            # If planet is AFTER the cusp, add next house
            if planet_longitude < cusp_deg:
                # Planet is before cusp - belongs to previous house too
                prev_house = cusp_num - 1 if cusp_num > 1 else 12
                if prev_house not in houses:
                    houses.append(prev_house)
            else:
                # Planet is after cusp - belongs to this cusp's house
                if cusp_num not in houses:
                    houses.append(cusp_num)
        
        return sorted(houses)
    
    def get_cusp_interlink(self, house_num: int) -> Dict:
        """
        Get cusp-interlink data for a specific house.
        """
        cusp_data = self.cusps.get(house_num, {})
        sub_lord = cusp_data.get('sub_lord', '')
        
        return {
            'cusp': house_num,
            'sub_lord': sub_lord,
            'cusp_degree': self.cusp_degrees.get(house_num, 0)
        }
    
    def analyze_planet_sandhi(self, planet_name: str, planet_longitude: float) -> Dict:
        """
        Full sandhi analysis for a planet.
        """
        primary_house = self.get_planet_house_placidus(planet_longitude)
        is_sandhi, cusp_num, orb = self.is_bhav_sandhi(planet_longitude)
        all_houses = self.get_planet_houses_with_sandhi(planet_longitude)
        
        return {
            'planet': planet_name,
            'longitude': planet_longitude,
            'primary_house': primary_house,
            'is_bhav_sandhi': is_sandhi,
            'sandhi_cusp': cusp_num,
            'sandhi_orb': round(orb, 2) if is_sandhi else None,
            'all_houses': all_houses,
            'house_count': len(all_houses)
        }


def get_cusp_interlink_engine(cusps: Dict) -> CuspInterlinkEngine:
    """Factory function to create CuspInterlinkEngine."""
    return CuspInterlinkEngine(cusps)
