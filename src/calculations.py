# src/calculations.py

from datetime import datetime, timedelta

# Import Core Math - CRITICAL: No silent fallback allowed
# If this fails, the application MUST crash with a clear error
try:
    from src.core_math import (
        calculate_julian_day, calculate_gmst, calculate_lst, 
        calculate_kp_ayanamsa, get_placidus_cusps, decimal_to_dms,
        get_sub_lord_info, normalize_angle
    )
    CORE_MATH_AVAILABLE = True
except ImportError as e:
    CORE_MATH_AVAILABLE = False
    _CORE_MATH_ERROR = str(e)
    # Fail-fast: Raise immediately with clear error message
    raise ImportError(
        f"CRITICAL ERROR: Core math module (src/core_math.py) failed to load.\n"
        f"The software CANNOT calculate accurate astrological positions without this module.\n"
        f"Technical details: {_CORE_MATH_ERROR}\n"
        f"Please ensure 'src/core_math.py' exists and has no syntax errors."
    )

class KPCalculator:
    """
    KP Engine Class. 
    This is what main.py imports.
    """

    def __init__(self):
        self.SIGN_LORDS = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
            "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
            "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        self.ASPECTS = [(0,8,"Conjunction"), (60,6,"Sextile"), (90,6,"Square"), (120,6,"Trine"), (180,6,"Opposition")]
        self.PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        self.DASA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        self.DASA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
        self.ZODIAC = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    # --- CORE WRAPPERS (This makes the class work) ---
    def decimal_to_dms(self, d): return decimal_to_dms(d)
    def get_sub_lord_info(self, l): return get_sub_lord_info(l)
    def get_julian_day(self, *args): return calculate_julian_day(*args)
    def get_gmst(self, jd): return calculate_gmst(jd)
    def get_lst(self, gmst, lon): return calculate_lst(gmst, lon)
    def get_kp_ayanamsa(self, *args): return calculate_kp_ayanamsa(*args)
    def get_placidus_cusps(self, lst, lat): return get_placidus_cusps(lst, lat)

    # --- ASTROLOGICAL LOGIC ---
    def get_zodiac_sign(self, lon):
        s = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return s[int(lon/30)%12], lon%30

    def get_sign_lord(self, s): return self.SIGN_LORDS.get(s, "-")

    def calculate_aspects(self, planets):
        res = []
        p_names = list(planets.keys())
        for i in range(len(p_names)):
            for j in range(i+1, len(p_names)):
                p1, p2 = p_names[i], p_names[j]
                if p1 in ["Rahu","Ketu"] or p2 in ["Rahu","Ketu"]: continue
                l1, l2 = planets[p1], planets[p2]
                d = abs(l1-l2); d = 360-d if d>180 else d
                for ang, orb, nam in self.ASPECTS:
                    if abs(d-ang) <= orb:
                        res.append({"p1":p1, "p2":p2, "aspect":nam, "angle":ang, "orb":round(abs(d-ang),2)})
                        break
        return res

    def get_house_significators(self, planets, cusps):
        h_occ = {i:[] for i in range(1,13)}
        for p, l in planets.items():
            sel=12
            for h in range(1,13):
                nxt = cusps[h+1] if h<12 else cusps[1]
                if (nxt<cusps[h] and (l>=cusps[h] or l<nxt)) or (nxt>cusps[h] and cusps[h]<=l<nxt): sel=h; break
            h_occ[sel].append(p)
        
        p_star = {p: self.get_sub_lord_info(l)[1] for p,l in planets.items()}
        h_lord = {h: self.SIGN_LORDS[self.get_zodiac_sign(l)[0]] for h,l in cusps.items()}
        
        sigs = {}
        for h in range(1,13):
            l1 = [p for p,s in p_star.items() if s in h_occ[h]]
            l2 = h_occ[h]
            l3 = [p for p,s in p_star.items() if s == h_lord[h]]
            l4 = [h_lord[h]]
            sigs[h] = {"L1":", ".join(l1) or "-","L2":", ".join(l2) or "-","L3":", ".join(l3) or "-","L4":", ".join(l4)}
        return sigs

    def get_bhavasphuta_significators(self, planets, cusps):
        p_occ = {}; p_own = {p: [] for p in self.PLANET_ORDER}
        for p in self.PLANET_ORDER: p_occ[p] = "-"
        for p, l in planets.items():
            sel=12
            for h in range(1,13):
                nxt = cusps[h+1] if h<12 else cusps[1]
                if (nxt<cusps[h] and (l>=cusps[h] or l<nxt)) or (nxt>cusps[h] and cusps[h]<=l<nxt): sel=h; break
            p_occ[p] = str(sel)
        for h, l in cusps.items():
            lord = self.SIGN_LORDS[self.get_zodiac_sign(l)[0]]
            if lord in p_own: p_own[lord].append(str(h))
        
        data = {}
        for p in self.PLANET_ORDER:
            if p not in planets: continue
            _, star, sub = self.get_sub_lord_info(planets[p])
            data[p] = {
                'P_Occ': p_occ.get(p,"-"), 'P_Own': ",".join(p_own.get(p,[])),
                'Star': star, 'S_Occ': p_occ.get(star,"-"), 'S_Own': ",".join(p_own.get(star,[])),
                'Sub': sub, 'Sub_Occ': p_occ.get(sub,"-"), 'Sub_Own': ",".join(p_own.get(sub,[]))
            }
        return data

    def get_planet_significators(self, planets, cusps):
        # Fallback compatibility method if needed
        return self.get_bhavasphuta_significators(planets, cusps)

    def add_years(self, d, y): return d + timedelta(days=y*365.2425)
    
    def get_dasa_balance(self, moon_long, birth_date):
        nak_span = 13.333333333333
        idx = int(moon_long/nak_span); lord = self.DASA_LORDS[idx%9]
        rem = nak_span - (moon_long - (idx*nak_span))
        bal = (rem/nak_span) * self.DASA_YEARS[lord]
        return lord, bal, self.add_years(birth_date, bal)

    def get_sub_periods(self, parent, duration, start):
        res = []; curr = start; start_idx = self.DASA_LORDS.index(parent)
        for i in range(9):
            sl = self.DASA_LORDS[(start_idx+i)%9]
            dur = (duration * self.DASA_YEARS[sl]) / 120.0
            end = self.add_years(curr, dur)
            res.append({"Lord":sl, "Start":curr, "End":end, "Duration":dur})
            curr = end
        return res

    def calculate_dashamsha(self, planets):
        """
        Calculates D10 (Dashamsha) Sign Placements.
        Odd Signs: Count from same sign.
        Even Signs: Count from 9th sign.
        """
        d10_positions = {}
        for p, data in planets.items():
            lon = data['longitude'] if isinstance(data, dict) else data
            
            # 1. Determine Sign (0-11)
            sign_idx = int(lon / 30)
            sign_num = sign_idx + 1
            
            # 2. Degree within sign (0-30)
            deg_in_sign = lon % 30
            
            # 3. D10 Part (0-9)
            part = int(deg_in_sign / 3.0)
            
            # 4. Calculate D10 Sign Index (0-11)
            if sign_num % 2 != 0: # Odd Sign
                d10_sign_idx = (sign_idx + part) % 12
            else: # Even Sign
                # Start from 9th house from current sign
                start_idx = (sign_idx + 8) % 12
                d10_sign_idx = (start_idx + part) % 12
                
            d10_positions[p] = self.ZODIAC[d10_sign_idx]
            
        return d10_positions