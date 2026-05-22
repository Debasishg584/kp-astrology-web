from datetime import datetime
import re
from src.core_transit import DivineTransitEngine


class BirthDailyPrediction:
    """
    🔱 DAILY PREDICTION ENGINE (BIRTH CHART)
    
    Implements the 'Stability Formula' for deterministic daily predictions.
    Properly parses chart_data.json format:
      - house_significators: [{house: "H1", L1: "...", L2: "...", L3: "...", L4: "..."}, ...]
      - planet_significators: [{planet: "Sun", Source_Row: "1, 2, 3", Result_Row: "6, 12"}, ...]
      - vimshottari_dasa_full: nested MD → AD → PD with dd-mm-yyyy dates
      - Transit Engine: keys = Sun/Mon/Mar/Mer/Jup/Ven/Sat/Rah/Ket
    """
    
    # Short-to-Full planet name mapping (Transit Engine uses short names)
    SHORT_TO_FULL = {
        "Sun": "Sun", "Mon": "Moon", "Mar": "Mars", "Mer": "Mercury",
        "Jup": "Jupiter", "Ven": "Venus", "Sat": "Saturn", 
        "Rah": "Rahu", "Ket": "Ketu",
        # Also map full names to themselves for safe normalization
        "Moon": "Moon", "Mars": "Mars", "Mercury": "Mercury",
        "Jupiter": "Jupiter", "Venus": "Venus", "Saturn": "Saturn",
        "Rahu": "Rahu", "Ketu": "Ketu"
    }
    FULL_TO_SHORT = {
        "Sun": "Sun", "Moon": "Mon", "Mars": "Mar", "Mercury": "Mer",
        "Jupiter": "Jup", "Venus": "Ven", "Saturn": "Sat",
        "Rahu": "Rah", "Ketu": "Ket"
    }
    
    # Major transit planets (higher weight)
    MAJOR_TRANSIT = {"Jupiter", "Saturn", "Rahu", "Ketu"}
    
    # Sign offsets for absolute longitude calculation
    SIGN_OFFSETS = {
        "Aries": 0, "Taurus": 30, "Gemini": 60, "Cancer": 90,
        "Leo": 120, "Virgo": 150, "Libra": 180, "Scorpio": 210,
        "Sagittarius": 240, "Capricorn": 270, "Aquarius": 300, "Pisces": 330
    }
    
    # Special aspects per planet (house-offset from planet's position)
    # Saturn: 3rd, 7th, 10th | Jupiter: 5th, 7th, 9th | Mars: 4th, 7th, 8th
    SPECIAL_ASPECTS = {
        "Saturn":  [3, 7, 10],
        "Jupiter": [5, 7, 9],
        "Mars":    [4, 7, 8]
    }
    
    # Cuspal aspect orb: 3°20' = 3.333...°
    ASPECT_ORB = 3.0 + 20.0/60.0  # 3.333 degrees
    
    def __init__(self, chart_data):
        self.chart_data = chart_data
        self.transit_engine = DivineTransitEngine(chart_data)
        
        # Parse data into usable structures
        self.house_significators = self._parse_house_significators()
        self.planet_source_houses = self._parse_planet_significators()
        self.cusp_longitudes = self._get_cusp_longitudes()
        
        # Bounds — Tuned for Naked Truth output
        self.K_DESTRUCTION = 0.7   # Aggressive destruction [was 0.5]
        self.EM_ENVIRONMENT = 1.2  # Higher environmental pressure [was 1.1]

    def _normalize_name(self, name):
        """Normalize any planet name (short/full) to the FULL name used in planet_significators."""
        if not name:
            return name
        return self.SHORT_TO_FULL.get(name, name)

    # -------------------------------------------------------------------------
    # CUSP LONGITUDE PARSING
    # -------------------------------------------------------------------------
    
    def _parse_cusp_longitude(self, dms_str, sign):
        """Parse sign-relative DMS string (e.g. '12° 16\' 22"') + sign name → absolute degrees."""
        try:
            sign_offset = self.SIGN_OFFSETS.get(sign, 0)
            # Extract degrees, minutes, seconds from DMS string
            import re
            match = re.match(r"(\d+)\D+(\d+)\D+(\d+)", dms_str.replace('\u00b0', ' ').replace("'", ' ').replace('"', ' '))
            if match:
                deg = int(match.group(1))
                mins = int(match.group(2))
                secs = int(match.group(3))
                return sign_offset + deg + mins/60.0 + secs/3600.0
        except (ValueError, TypeError):
            pass
        return 0.0
    
    def _get_cusp_longitudes(self):
        """Parse all 12 cusp longitudes from chart_data → {1: abs_deg, 2: abs_deg, ...}"""
        cusps = {}
        for c in self.chart_data.get('house_cusps', []):
            cusp_num = c.get('cusp', 0)
            dms = c.get('longitude_dms', '')
            sign = c.get('sign', '')
            if cusp_num and dms and sign:
                cusps[cusp_num] = self._parse_cusp_longitude(dms, sign)
        return cusps
    
    # -------------------------------------------------------------------------
    # CUSPAL ASPECT CHECK
    # -------------------------------------------------------------------------
    
    def _get_cuspal_aspects(self, transits):
        """
        Check Saturn/Jupiter/Mars special aspects against cusp degrees.
        Returns dict: {house_number: [(planet, aspect_type), ...]}
        Only counts if aspect point is within 3°20' of cusp degree.
        """
        aspects_hitting = {h: [] for h in range(1, 13)}
        
        for planet_full, aspect_houses in self.SPECIAL_ASPECTS.items():
            short_key = self.FULL_TO_SHORT.get(planet_full, planet_full)
            pos = transits.get(short_key)
            if not pos:
                continue
            
            planet_lon = pos.get('longitude', 0)
            
            for offset in aspect_houses:
                # Aspect point = planet longitude + (offset-1)*30 degrees (approx)
                aspect_lon = (planet_lon + (offset - 1) * 30.0) % 360.0
                
                # Check against all 12 cusp degrees
                for h, cusp_lon in self.cusp_longitudes.items():
                    diff = abs(aspect_lon - cusp_lon)
                    if diff > 180:
                        diff = 360 - diff
                    if diff <= self.ASPECT_ORB:
                        aspects_hitting[h].append((planet_full, f"{offset}th"))
        
        return aspects_hitting
    
    # -------------------------------------------------------------------------
    # DOUBLE TRANSIT CHECK
    # -------------------------------------------------------------------------
    
    def _check_double_transit(self, transits):
        """
        Check if both Jupiter AND Saturn support a house
        (via transit position or star lord connection).
        Returns set of house numbers with Double Transit support.
        """
        jup_houses = set()
        sat_houses = set()
        
        # Jupiter's contributing houses
        jup_pos = transits.get('Jup')
        if jup_pos:
            jup_house = jup_pos.get('house', 0)
            if jup_house:
                jup_houses.add(jup_house)
            jup_sl = self._normalize_name(jup_pos.get('star_lord', ''))
            jup_houses.update(self._get_planet_houses(jup_sl))
        
        # Saturn's contributing houses
        sat_pos = transits.get('Sat')
        if sat_pos:
            sat_house = sat_pos.get('house', 0)
            if sat_house:
                sat_houses.add(sat_house)
            sat_sl = self._normalize_name(sat_pos.get('star_lord', ''))
            sat_houses.update(self._get_planet_houses(sat_sl))
        
        # Intersection: houses supported by BOTH
        return jup_houses & sat_houses

    def _parse_planet_list(self, raw_str):
        """Parse comma-separated planet string like 'Moon, Mars, Mercury' into list."""
        if not raw_str or raw_str.strip() == "-":
            return []
        return [p.strip() for p in raw_str.split(",") if p.strip() and p.strip() != "-"]

    def _parse_house_numbers(self, raw_str):
        """Parse house number string like '1, 2+, 3, 7' → [1, 2, 2, 3, 7].
        '+' means repeated signification (stronger), so we duplicate."""
        if not raw_str or raw_str.strip() == "-":
            return []
        houses = []
        for token in raw_str.split(","):
            token = token.strip()
            if not token or token == "-":
                continue
            # Count '+' for repeats
            plus_count = token.count("+")
            num_str = token.replace("+", "").strip()
            try:
                h = int(num_str)
                houses.extend([h] * (1 + plus_count))
            except ValueError:
                continue
        return houses

    def _parse_house_significators(self):
        """
        Parse house_significators from chart_data.
        Format: [{house: "H1", L1: "Moon, Mars", L2: "Sun", L3: "-", L4: "Venus"}, ...]
        Returns: {1: ["Moon", "Mars", "Sun", "Venus"], 2: [...], ...}
        """
        h_sigs = {}
        raw = self.chart_data.get('house_significators', [])
        for item in raw:
            try:
                house_str = item.get('house', '')
                h_num = int(house_str.replace('H', '').strip())
                planets = set()
                for level in ['L1', 'L2', 'L3', 'L4']:
                    planets.update(self._parse_planet_list(item.get(level, '')))
                h_sigs[h_num] = list(planets)
            except (ValueError, TypeError):
                continue
        return h_sigs

    def _parse_planet_significators(self):
        """
        Parse planet_significators from chart_data.
        Format: [{planet: "Sun", Source_Row: "1, 2, 3, 6, 11", Result_Row: "6, 12"}, ...]
        Returns: {planet: {source: [houses], result: [houses]}}
        """
        p_sigs = {}
        raw = self.chart_data.get('planet_significators', [])
        for item in raw:
            planet = item.get('planet', '')
            if not planet:
                continue
            p_sigs[planet] = {
                'source': self._parse_house_numbers(item.get('Source_Row', '')),
                'result': self._parse_house_numbers(item.get('Result_Row', ''))
            }
        return p_sigs

    def _get_planet_houses(self, planet_name):
        """Get houses a planet DELIVERS to (Result Row only — KP prediction rule).
        Normalizes planet name to handle both short ('Mar') and full ('Mars') keys."""
        full_name = self._normalize_name(planet_name)
        info = self.planet_source_houses.get(full_name, {})
        return set(info.get('result', []))

    # -------------------------------------------------------------------------
    # DASHA LOOKUP (Proper nested traversal)
    # -------------------------------------------------------------------------

    def _get_dasha_lords(self, target_date):
        """
        Find MD, AD, PD for the given target_date by traversing nested vimshottari_dasa_full.
        Date format in data: "dd-mm-yyyy" or "dd-mm-yyyy HH:MM"
        """
        dasas = self.chart_data.get('vimshottari_dasa_full', [])
        result = {"MD": None, "AD": None, "PD": None}
        
        def parse_date(date_str):
            """Parse date string, handling both 'dd-mm-yyyy' and 'dd-mm-yyyy HH:MM'."""
            date_str = date_str.strip()
            for fmt in ["%d-%m-%Y %H:%M", "%d-%m-%Y", "%d-%b-%Y"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        
        # Find MD
        for md in dasas:
            md_start = parse_date(md.get('start', ''))
            md_end = parse_date(md.get('end', ''))
            if not md_start or not md_end:
                continue
            if md_start <= target_date <= md_end:
                result["MD"] = md.get('lord')
                
                # Find AD within this MD
                for ad in md.get('sub_periods', []):
                    ad_start = parse_date(ad.get('start', ''))
                    ad_end = parse_date(ad.get('end', ''))
                    if not ad_start or not ad_end:
                        continue
                    if ad_start <= target_date <= ad_end:
                        result["AD"] = ad.get('lord')
                        
                        # Find PD within this AD
                        for pd in ad.get('sub_periods', []):
                            pd_start = parse_date(pd.get('start', ''))
                            pd_end = parse_date(pd.get('end', ''))
                            if not pd_start or not pd_end:
                                continue
                            if pd_start <= target_date <= pd_end:
                                result["PD"] = pd.get('lord')
                                break
                        break
                break
        
        return result

    # -------------------------------------------------------------------------
    # RETROGRADE BLOCK (KP Kill-Switch)
    # -------------------------------------------------------------------------

    # Rahu & Ketu are naturally retrograde (shadow planets) — exempt from kill-switch
    RETRO_EXEMPT = {"Rahu", "Ketu"}

    # Houses that indicate negativity for Sub-Lord Filter
    NEGATIVE_HOUSES = {6, 8, 12}
    
    def _get_retro_blocked(self, transits):
        """
        KP Rule: A planet whose TRANSIT Star Lord is Retrograde cannot
        deliver results. Returns dict {full_planet_name: retro_star_lord_name}.
        
        EXCEPTION: Rahu & Ketu are naturally retrograde (ছায়া গ্রহ).
        Their retrograde is their normal motion — they are NEVER blocked.
        If a planet's Star Lord is Rahu or Ketu, the kill-switch does NOT apply.
        
        HOST CHECK: Even though Rahu/Ketu are exempt from the kill-switch,
        if their HOST (sign lord or star lord) is retrograde in transit,
        their contribution is dampened (tracked separately).
        """
        blocked = {}
        for short_name, pos_data in transits.items():
            if not pos_data:
                continue
            full_name = self._normalize_name(short_name)
            star_lord_short = pos_data.get('star_lord', '')
            if not star_lord_short:
                continue
            star_lord_full = self._normalize_name(star_lord_short)
            
            # EXCEPTION: Rahu/Ketu are naturally retrograde — skip kill-switch
            if star_lord_full in self.RETRO_EXEMPT:
                continue
            
            # Look up star lord's own transit data to check retrograde
            sl_data = transits.get(star_lord_short)
            if sl_data and sl_data.get('is_retrograde', False):
                blocked[full_name] = star_lord_full
        return blocked
    
    def _get_rahu_ketu_dampened(self, transits):
        """
        Rahu/Ketu Host Check: If Rahu/Ketu's sign lord or star lord
        (their 'host') is retrograde in transit, their score is dampened.
        Returns dict: {full_planet_name: host_name} for planets that need 0.7x.
        """
        dampened = {}
        for short_name in ['Rah', 'Ket']:
            pos_data = transits.get(short_name)
            if not pos_data:
                continue
            full_name = self._normalize_name(short_name)
            
            # Check sign lord (host planet for the sign Rahu/Ketu is in)
            sign_lord_short = pos_data.get('sign_lord', '')
            if sign_lord_short:
                sl_data = transits.get(sign_lord_short)
                if sl_data and sl_data.get('is_retrograde', False):
                    sign_lord_full = self._normalize_name(sign_lord_short)
                    if sign_lord_full not in self.RETRO_EXEMPT:
                        dampened[full_name] = self._normalize_name(sign_lord_short)
                        continue
            
            # Check star lord (nakshatra lord)
            star_lord_short = pos_data.get('star_lord', '')
            if star_lord_short:
                star_data = transits.get(star_lord_short)
                if star_data and star_data.get('is_retrograde', False):
                    star_lord_full = self._normalize_name(star_lord_short)
                    if star_lord_full not in self.RETRO_EXEMPT:
                        dampened[full_name] = self._normalize_name(star_lord_short)
        
        return dampened

    # -------------------------------------------------------------------------
    # NATAL FREEZE (Temporary Promise Freeze)
    # -------------------------------------------------------------------------

    def _get_natal_frozen(self, transits):
        """
        Check each NATAL planet's birth-chart Star Lord.
        If that star lord is currently Retrograde in transit → planet is FROZEN.
        Returns dict {full_planet_name: natal_star_lord_name}.
        Rahu/Ketu star lords are exempt (naturally retrograde).
        """
        frozen = {}
        natal_planets = self.chart_data.get('planetary_positions', [])
        for p_info in natal_planets:
            planet = p_info.get('planet', '')
            natal_sl = p_info.get('star_lord', '')
            if not planet or not natal_sl:
                continue
            natal_sl_full = self._normalize_name(natal_sl)
            # Rahu/Ketu exempt
            if natal_sl_full in self.RETRO_EXEMPT:
                continue
            # Check if this natal star lord is retrograde in current transit
            sl_short = self.FULL_TO_SHORT.get(natal_sl_full, natal_sl)
            sl_transit = transits.get(sl_short)
            if sl_transit and sl_transit.get('is_retrograde', False):
                frozen[planet] = natal_sl_full
        return frozen

    # -------------------------------------------------------------------------
    # SCORING COMPONENTS
    # -------------------------------------------------------------------------

    def _get_np_score(self, house, natal_frozen=None):
        """
        Natal Promise (NP) Score. Max = 3.
        +1 if House CSL (sub lord) signifies this house
        +1 if >= 2 planets signify this house  
        +1 if house lord signifies this house
        
        NATAL FREEZE: If key significators are frozen (star lord retro in transit),
        apply 0.5x multiplier to the score.
        """
        if natal_frozen is None:
            natal_frozen = {}
        score = 0
        sigs = self.house_significators.get(house, [])
        
        # Check CSL (Cusp Sub Lord)
        cusp_info = next((c for c in self.chart_data.get('house_cusps', []) if c['cusp'] == house), None)
        if cusp_info:
            sub_lord = cusp_info.get('sub_lord', '')
            # If CSL signifies this house (its signification includes this house)
            csl_houses = self._get_planet_houses(sub_lord)
            if house in csl_houses:
                score += 1
            
            # If house lord signifies this house
            sign_lord = cusp_info.get('sign_lord', '')
            lord_houses = self._get_planet_houses(sign_lord)
            if house in lord_houses:
                score += 1
        
        # Strong signification: >= 2 planets signify this house
        if len(sigs) >= 2:
            score += 1
        
        score = min(3, score)
        
        # NATAL FREEZE: If CSL or sign lord is frozen → 0.5x penalty
        if cusp_info:
            csl_name = self._normalize_name(cusp_info.get('sub_lord', ''))
            lord_name = self._normalize_name(cusp_info.get('sign_lord', ''))
            if csl_name in natal_frozen or lord_name in natal_frozen:
                score *= 0.5
            
        return score

    def _get_dw_score(self, house, dasha_lords, retro_blocked=None):
        """
        Dasha Weights (DW) Score. Max = 3.
        +1 per Dasha Lord (MD, AD, PD) that signifies this house.
        Retro-blocked Dasha lords get 0.3 instead of 1.0 (severely penalized).
        """
        if retro_blocked is None:
            retro_blocked = {}
        score = 0
        
        for level in ['MD', 'AD', 'PD']:
            lord = dasha_lords.get(level)
            if not lord:
                continue
            planet_houses = self._get_planet_houses(lord)
            if house in planet_houses:
                # Check if this Dasha lord is retro-blocked in transit
                if self._normalize_name(lord) in retro_blocked:
                    score += 0.3  # Severely penalized — can't manifest externally
                else:
                    score += 1
        
        return min(3, score)

    def _get_ta_score(self, house, transits, retro_blocked=None):
        """
        Transit Aspects (TA) Score. Max = 3.
        Score based on planets transiting through the house.
        Major planets (Jupiter, Saturn, Rahu, Ketu) get higher weight.
        Star lord connections use normalized names.
        Retro-blocked planets contribute ZERO (Kill-Switch).
        Sub-Lord FILTER: if sub lord signifies 6/8/12 → TA × 0.5.
        Rahu/Ketu Host: if host retro → 0.7x dampening.
        """
        if retro_blocked is None:
            retro_blocked = {}
        rahu_ketu_dampened = self._get_rahu_ketu_dampened(transits) if hasattr(self, '_get_rahu_ketu_dampened') else {}
        score = 0.0
        
        for short_name, pos_data in transits.items():
            if not pos_data:
                continue
            
            full_name = self._normalize_name(short_name)
            
            # RETRO KILL-SWITCH: if this planet's star lord is retrograde → skip entirely
            if full_name in retro_blocked:
                continue
            
            # Dampening factor: 0.7 for Rahu/Ketu with retro host, 1.0 otherwise
            damp = 0.7 if full_name in rahu_ketu_dampened else 1.0
            
            transit_house = pos_data.get('house', 0)
            
            if transit_house == house:
                if full_name in self.MAJOR_TRANSIT:
                    score += 1.5 * damp
                else:
                    score += 0.5 * damp
            
            # Star lord connection — normalize the short key from transit engine
            star_lord = self._normalize_name(pos_data.get('star_lord', ''))
            star_lord_houses = self._get_planet_houses(star_lord)
            if house in star_lord_houses:
                if full_name in self.MAJOR_TRANSIT:
                    score += 0.5 * damp
                else:
                    score += 0.25 * damp
        
        # SUB-LORD FILTER: Sub Lord is a FILTER, not a bonus.
        # If ANY transit planet's star lord says 'yes' to this house, but its
        # sub lord signifies negative houses (6, 8, 12) → TA × 0.5 penalty.
        sub_lord_negative = False
        for short_name, pos_data in transits.items():
            if not pos_data:
                continue
            full_name = self._normalize_name(short_name)
            if full_name in retro_blocked:
                continue
            star_lord = self._normalize_name(pos_data.get('star_lord', ''))
            star_lord_houses = self._get_planet_houses(star_lord)
            if house in star_lord_houses:
                sub_lord = self._normalize_name(pos_data.get('sub_lord', ''))
                sub_lord_houses = self._get_planet_houses(sub_lord)
                # Sub lord says NO: signifies negative houses
                if sub_lord_houses & self.NEGATIVE_HOUSES:
                    sub_lord_negative = True
                    break
        
        if sub_lord_negative:
            score *= 0.5  # Star Lord says Yes, Sub Lord says No → halved
        
        return min(3.0, score)

    def _get_rp_score(self, house, rps, retro_blocked=None):
        """
        Ruling Planets (RP) Score. Max = 3.
        +1 per Ruling Planet that signifies this house.
        RP RETRO BLOCK: If an RP's transit star lord is retrograde,
        its contribution drops from 1.0 to 0.3 (delivery mechanism broken).
        """
        if retro_blocked is None:
            retro_blocked = {}
        score = 0
        
        for rp in rps:
            rp_full = self._normalize_name(rp)
            rp_houses = self._get_planet_houses(rp)
            if house in rp_houses:
                if rp_full in retro_blocked:
                    score += 0.3  # RP blocked — delivery mechanism broken
                else:
                    score += 1
                
        return min(3, score)

    def _get_daily_rps(self, transits, date):
        """Calculate proxy RPs for the day (Moon Star Lord + Day Lord + Asc Star Lord).
        All names normalized to full format for consistent lookup."""
        rps = []
        
        # 1. Moon Star Lord (from transit — short key, normalize)
        moon_data = transits.get('Mon')
        if moon_data:
            star_lord = self._normalize_name(moon_data.get('star_lord', ''))
            if star_lord:
                rps.append(star_lord)
        
        # 2. Day Lord (Vara) — already full names
        weekday = date.weekday()  # 0=Mon, 6=Sun
        day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
        rps.append(day_lords[weekday])
        
        # 3. Ascendant Star Lord (from natal chart — full names)
        cusp1 = next((c for c in self.chart_data.get('house_cusps', []) if c['cusp'] == 1), None)
        if cusp1:
            asc_star = self._normalize_name(cusp1.get('star_lord', ''))
            if asc_star:
                rps.append(asc_star)
        
        return list(set(rps))  # Unique

    # -------------------------------------------------------------------------
    # HOUSE THEME DESCRIPTIONS (KP Context)
    # -------------------------------------------------------------------------
    
    HOUSE_THEMES = {
        1: "Self, Health, Personality, New Beginnings",
        2: "Wealth, Family, Speech, Savings",
        3: "Courage, Siblings, Short Travels, Communication",
        4: "Home, Mother, Property, Education, Comfort",
        5: "Children, Romance, Creativity, Speculation",
        6: "Enemies, Disease, Debt, Service, Obstacles",
        7: "Marriage, Partnership, Business Deals",
        8: "Obstacles, Sudden Events, Inheritance, Transformation",
        9: "Luck, Father, Long Travel, Higher Education, Dharma",
        10: "Career, Status, Authority, Professional Success",
        11: "Gains, Income, Fulfillment of Desires, Friends",
        12: "Losses, Expenses, Foreign Travel, Isolation, Spiritual Growth"
    }

    FAVORABLE_HOUSES = {1, 2, 3, 4, 5, 7, 9, 10, 11}
    CHALLENGING_HOUSES = {6, 8, 12}

    # -------------------------------------------------------------------------
    # MAIN ENGINE
    # -------------------------------------------------------------------------

    def get_transit_scores(self, date):
        """
        Calculate all transit scores and structural data for a specific date.
        Returns a dictionary with all raw data needed for analysis/reporting.
        """
        # 1. Get Dasha Lords
        dasha_lords = self._get_dasha_lords(date)
        
        # 2. Get Transit Positions
        transits = self.transit_engine.get_all_planet_positions(date)
        
        # 3. Get Ruling Planets
        rps = self._get_daily_rps(transits, date)
        
        # 4. RETRO GATE — Compute blocked planets (KP Kill-Switch)
        retro_blocked = self._get_retro_blocked(transits)
        
        # 5. NATAL FREEZE — Check if natal promises are temporarily frozen
        natal_frozen = self._get_natal_frozen(transits)
        
        # 6. Calculate Base Structural Score for each house
        base_cls = {}
        details = {}
        
        # Pre-compute cuspal aspects (once, not per house)
        cuspal_aspects = self._get_cuspal_aspects(transits)
        
        for h in range(1, 13):
            np_score = self._get_np_score(h, natal_frozen)
            dw_score = self._get_dw_score(h, dasha_lords, retro_blocked)
            ta_score = self._get_ta_score(h, transits, retro_blocked)
            rp_score = self._get_rp_score(h, rps, retro_blocked)
            
            # Cuspal Aspect bonus (supportive modifier, max +1.0)
            aspect_bonus = min(1.0, len(cuspal_aspects.get(h, [])) * 0.25)
            ta_score = min(3.0, ta_score + aspect_bonus)
            
            # Stability Formula:
            # Base_CLS(H) = NP(H)*2.5 + DW(H)*2 + TA(H)*1.5 + RP(H)*2
            base = (np_score * 2.5) + (dw_score * 2.0) + (ta_score * 1.5) + (rp_score * 2.0)
            base_cls[h] = base
            
            details[h] = {
                "NP": np_score, "DW": dw_score, "TA": ta_score, "RP": rp_score, "Base": base
            }

        # 6. Calculate Destruction (Aggressive)
        # DD(H) = [Base_CLS(12th-from-H) / (Base_CLS(H) + 0.5)] * K
        # Also factor adjacent house pressure (if prior house is strong, it dampens)
        destruction = {}
        for h in range(1, 13):
            h12 = 12 if h == 1 else h - 1  # 12th from this house
            
            # Primary destruction: 12th-from-H pressure
            primary_dd = (base_cls[h12] / (base_cls[h] + 0.5)) * self.K_DESTRUCTION
            
            # Adjacent pressure: if the house BEFORE is strong and competing
            h_prev = 12 if h == 1 else h - 1
            if base_cls[h_prev] > base_cls[h] * 0.8:
                adjacent_penalty = (base_cls[h_prev] - base_cls[h] * 0.8) * 0.1
            else:
                adjacent_penalty = 0
            
            destruction[h] = primary_dd + adjacent_penalty

        # 7. Environmental Adjustment
        # CORRECTED FORMULA: Adjusted_CLS(H) = (Base_CLS(H) * DT - DD(H)) * EM
        # Double Transit boosts the BASE (possibility amplifier), then
        # Destruction subtracts, then Environment applies.
        adjusted_cls = {}
        double_transit_houses = self._check_double_transit(transits)
        for h in range(1, 13):
            dw = details[h]['DW']
            # No Dasha support = 0.7x penalty (internal only, no timing support)
            dasha_penalty = 1.0 if dw > 0 else 0.7
            # Double Transit: boost Base BEFORE destruction (event amplifier)
            dt_multiplier = 1.2 if h in double_transit_houses else 1.0
            boosted_base = base_cls[h] * dt_multiplier
            adj = (boosted_base - destruction[h]) * self.EM_ENVIRONMENT * dasha_penalty
            adjusted_cls[h] = max(0, adj)

        return {
            "date": date,
            "dasha_lords": dasha_lords,
            "transits": transits,
            "rps": rps,
            "base_cls": base_cls,
            "destruction": destruction,
            "adjusted_cls": adjusted_cls,
            "details": details,
            "retro_blocked": retro_blocked,
            "natal_frozen": natal_frozen,
            "double_transit_houses": double_transit_houses,
            "cuspal_aspects": cuspal_aspects
        }

    def get_prediction(self, date):
        """Generate Daily Prediction Report for a specific date."""
        # Use simple wrapper around the core logic
        data = self.get_transit_scores(date)
        
        # 9. Generate Report
        return self._generate_report(
            data["date"], 
            data["dasha_lords"], 
            data["transits"], 
            data["rps"], 
            data["base_cls"], 
            data["destruction"], 
            data["adjusted_cls"], 
            data["details"], 
            data["retro_blocked"], 
            data["natal_frozen"], 
            data["double_transit_houses"], 
            data["cuspal_aspects"]
        )

    # -------------------------------------------------------------------------
    # REPORT GENERATION
    # -------------------------------------------------------------------------

    def _generate_report(self, date, dasha, transits, rps, base, dest, adj, details, retro_blocked=None, natal_frozen=None, double_transit_houses=None, cuspal_aspects=None):
        """Generate a comprehensive, readable Daily Prediction Report."""
        if retro_blocked is None:
            retro_blocked = {}
        if natal_frozen is None:
            natal_frozen = {}
        if double_transit_houses is None:
            double_transit_houses = set()
        if cuspal_aspects is None:
            cuspal_aspects = {}
        lines = []
        
        # ---------- HEADER ----------
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_name = weekdays[date.weekday()]
        day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
        day_lord = day_lords[date.weekday()]
        
        lines.append("=" * 65)
        lines.append(f"  📅  DAILY PREDICTION REPORT")
        lines.append(f"  Date: {date.strftime('%d %B %Y')} ({day_name})")
        lines.append(f"  Day Lord: {day_lord}")
        lines.append("=" * 65)
        
        # ---------- DASHA CONTEXT ----------
        md = dasha.get('MD', '—')
        ad = dasha.get('AD', '—')
        pd = dasha.get('PD', '—')
        lines.append(f"\n🔱 RUNNING DASHA: {md} / {ad} / {pd}")
        
        # Show what houses Dasha Lords signify
        for level, lord in [("MD", md), ("AD", ad), ("PD", pd)]:
            if lord and lord != '—':
                houses = sorted(self._get_planet_houses(lord))
                if houses:
                    lines.append(f"   {level} ({lord}): Houses {', '.join(str(h) for h in houses)}")
        
        # ---------- RULING PLANETS ----------
        lines.append(f"\n🌟 RULING PLANETS: {', '.join(rps)}")
        
        # ---------- KEY TRANSITS (All 9 planets) ----------
        lines.append(f"\n🪐 KEY TRANSITS:")
        for short_name in ["Jup", "Sat", "Rah", "Ket", "Sun", "Mon", "Mar", "Ven", "Mer"]:
            pos = transits.get(short_name)
            if pos:
                full = self._normalize_name(short_name)
                # Planet's own retrograde marker — next to planet name
                p_retro = " (R)" if pos.get('is_retrograde') else ""
                planet_label = f"{full}{p_retro}"
                
                # Star lord's retrograde marker — separate [★R] indicator
                sl_short = pos.get('star_lord', '?')
                sl_data = transits.get(sl_short)
                sl_full = self._normalize_name(sl_short)
                sl_retro = " [★R]" if (sl_data and sl_data.get('is_retrograde') and sl_full not in self.RETRO_EXEMPT) else ""
                
                # Blocked marker
                blocked_marker = " ⛔" if full in retro_blocked else ""
                lines.append(f"   {planet_label:15s} → House {pos['house']:2d} [{pos['sign']}] Star: {sl_short}{sl_retro}{blocked_marker}")
                
                # Narrative line
                icons = {"Sun": "☀️", "Moon": "🌙", "Mercury": "🧠", "Venus": "🌸", "Mars": "⚡", "Jupiter": "✨", "Saturn": "🪐", "Rahu": "🌪️", "Ketu": "🔮"}
                icon = icons.get(full, "🔹")
                if full == "Saturn":
                    lines.append(f"     └ {icon} Saturn enforcing Dasha fruits via House {pos['house']}.")
                elif full == "Jupiter":
                    lines.append(f"     └ {icon} Jupiter expanding opportunities via House {pos['house']}.")
                elif full in ["Rahu", "Ketu"]:
                    lines.append(f"     └ {icon} {full} causing sudden shifts via House {pos['house']}.")
                elif full == "Mars":
                    lines.append(f"     └ {icon} Mars triggering decisive actions & energy spikes via House {pos['house']}.")
                elif full == "Sun":
                    lines.append(f"     └ {icon} Sun illuminating authority & visibility via House {pos['house']}.")
                elif full == "Venus":
                    lines.append(f"     └ {icon} Venus smoothing desires & relationships via House {pos['house']}.")
                elif full == "Mercury":
                    lines.append(f"     └ {icon} Mercury stimulating intellect & communications via House {pos['house']}.")
                elif full == "Moon":
                    lines.append(f"     └ {icon} Moon reflecting emotional fluctuations & sudden mind activity via House {pos['house']}.")
        
        # ---------- RETROGRADE BLOCK REPORT ----------
        if retro_blocked:
            lines.append(f"\n⛔ RETRO-BLOCKED PLANETS (Star Lord Retrograde → No External Delivery):")
            for planet, star_lord in retro_blocked.items():
                blocked_houses = sorted(self._get_planet_houses(planet))
                houses_str = ', '.join(str(h) for h in blocked_houses) if blocked_houses else 'None'
                lines.append(f"   {planet:10s} ← Star Lord {star_lord} (R) | Blocked Houses: {houses_str}")
        
        # ---------- NATAL FREEZE REPORT ----------
        if natal_frozen:
            lines.append(f"\n🧊 NATAL FREEZE (Birth Star Lord Retro in Transit → Promise Frozen 0.5x):")
            for planet, star_lord in natal_frozen.items():
                frozen_houses = sorted(self._get_planet_houses(planet))
                houses_str = ', '.join(str(h) for h in frozen_houses) if frozen_houses else 'None'
                lines.append(f"   {planet:10s} ← Natal Star Lord {star_lord} (R) | Frozen Houses: {houses_str}")
        
        # ---------- DOUBLE TRANSIT REPORT ----------
        if double_transit_houses:
            dt_list = ', '.join(f'H{h}' for h in sorted(double_transit_houses))
            lines.append(f"\n🪐🪐 DOUBLE TRANSIT (Jupiter + Saturn both support → 1.2x boost):")
            lines.append(f"   Active Houses: {dt_list}")
        
        # ---------- CUSPAL ASPECTS REPORT ----------
        has_aspects = any(v for v in cuspal_aspects.values())
        if has_aspects:
            lines.append(f"\n🎯 CUSPAL ASPECTS (Within 3°20' of cusp → +0.25 TA):")
            for h in range(1, 13):
                asp_list = cuspal_aspects.get(h, [])
                if asp_list:
                    asp_str = ', '.join(f'{p} {a}' for p, a in asp_list)
                    lines.append(f"   H{h}: {asp_str}")
        
        # ---------- HOUSE SCORES TABLE ----------
        lines.append(f"\n{'─' * 65}")
        lines.append(f"  {'HOUSE':<7} {'NP':>4} {'DW':>4} {'TA':>5} {'RP':>4} {'BASE':>6} {'DEST':>6} {'FINAL':>6}  STATUS")
        lines.append(f"{'─' * 65}")
        
        # Sort houses by adjusted score to find Top ranks
        sorted_houses = sorted(adj.items(), key=lambda x: x[1], reverse=True)
        top_houses = [pair[0] for pair in sorted_houses[:3] if pair[1] > 0]
        
        for h in range(1, 13):
            det = details[h]
            b = base[h]
            d = dest[h]
            a = adj[h]
            
            # Status Classification (Loophole #1 fix: require TA >= 1.0 for ACTIVE)
            has_transit_trigger = det['TA'] >= 1.0
            has_dasha_support = det['DW'] >= 1
            has_natal_promise = det['NP'] >= 2
            is_top = h in top_houses
            
            status = ""
            if a == 0:
                status = "  ─"
            elif is_top and has_natal_promise and has_dasha_support and has_transit_trigger:
                status = "  ✅ ACTIVE (External)"
            elif is_top and has_natal_promise and has_dasha_support:
                status = "  🧠 Internal Only"
            elif is_top and has_transit_trigger:
                status = "  ⚡ Transit Trigger"
            elif is_top:
                status = "  ⚠️ Mild"
            elif a >= 5.0:
                status = "  ⚠️ Mild"
            else:
                status = "  ─"
            
            lines.append(f"  H{h:<5} {det['NP']:>4.0f} {det['DW']:>4.0f} {det['TA']:>5.1f} {det['RP']:>4.0f} {b:>6.1f} {d:>6.1f} {a:>6.1f}{status}")
        
        lines.append(f"{'─' * 65}")
        
        # ---------- DAILY FORECAST NARRATIVE ----------
        lines.append(f"\n📖 DAILY FORECAST (HOUSE-BY-HOUSE DECODE):")
        lines.append(f"{'─' * 65}")
        
        # We will decode all 12 houses to give a complete picture
        for h in range(1, 13):
            det = details[h]
            a = adj[h]
            theme = self.HOUSE_THEMES.get(h, "")
            
            # Determine status string
            has_transit_trigger = det['TA'] >= 1.0
            has_dasha_support = det['DW'] >= 1
            has_natal_promise = det['NP'] >= 2
            is_top = h in top_houses
            
            status_symbol = ""
            status_text = ""
            
            if a == 0:
                status_symbol = "─"
                status_text = "Inactive / Dead"
            elif is_top and has_natal_promise and has_dasha_support and has_transit_trigger:
                status_symbol = "✅"
                status_text = "ACTIVE (External Event Likely)"
            elif is_top and has_natal_promise and has_dasha_support:
                status_symbol = "🧠"
                status_text = "Internal Focus Only (No Transit Trigger)"
            elif is_top and has_transit_trigger:
                status_symbol = "⚡"
                status_text = "Sudden Transit Trigger (Weak Base)"
            elif is_top or a >= 5.0:
                status_symbol = "⚠️"
                status_text = "Mild Background Energy"
            else:
                status_symbol = "─"
                status_text = "Inactive"

            lines.append(f"\n  {status_symbol} House {h} [{status_text}]")
            lines.append(f"     Themes: {theme}")
            
            # Add specific Dasha context if supported
            dasha_hitting = []
            for level in ['MD', 'AD', 'PD']:
                lord = dasha.get(level)
                if lord and h in self._get_planet_houses(lord):
                    dasha_hitting.append(f"{level}={lord}")
            
            if dasha_hitting:
                lines.append(f"     Dasha Support: {', '.join(dasha_hitting)}")
            
            # Add a brief decoding narrative based on scores
            if a == 0:
                reason = "Crushed by high destruction/friction" if dest[h] > base[h] * 0.5 else "Zero energy"
                lines.append(f"     Decode: Inactive today. {reason}.")
            elif "ACTIVE" in status_text:
                lines.append(f"     Decode: Highly supported by Dasha and triggered by Transit today. Real-world developments expected.")
            elif "Internal" in status_text:
                lines.append(f"     Decode: Strong base energy and Dasha support, but lacks a physical transit trigger today. Focus will be mental or planning-oriented.")
            elif "Trigger" in status_text:
                lines.append(f"     Decode: Weak overall promise, but a strong transit is passing through today causing temporary waves.")
            else:
                lines.append(f"     Decode: Humming in the background. Routine energy, no major shocks.")
            
        lines.append(f"\n{'─' * 65}")

        # Overall Day Rating (Loophole #4 fix: use per-house AVERAGES, not totals)
        avg_favorable = sum(adj.get(h, 0) for h in self.FAVORABLE_HOUSES) / len(self.FAVORABLE_HOUSES)
        avg_challenging = sum(adj.get(h, 0) for h in self.CHALLENGING_HOUSES) / len(self.CHALLENGING_HOUSES)
        
        # Count houses with ACTIVE external manifestation
        active_count = sum(1 for h in range(1, 13) 
                         if details[h]['DW'] >= 1 and details[h]['TA'] >= 1.0 and adj[h] > 0)
        
        lines.append(f"\n  📊 DAY BALANCE:")
        lines.append(f"     Avg Favorable:   {avg_favorable:.1f} (per house)")
        lines.append(f"     Avg Challenging:  {avg_challenging:.1f} (per house)")
        lines.append(f"     Active Houses:    {active_count}/12")
        
        ratio = avg_favorable / (avg_challenging + 0.1)
        if ratio > 2.5 and active_count >= 3:
            overall = "🟢 EXCELLENT — Multiple active external events. Highly productive."
        elif ratio > 2.0 and active_count >= 2:
            overall = "🟢 GOOD — Favorable conditions for progress."
        elif ratio > 1.5:
            overall = "🟡 MODERATE — Some progress possible, stay alert."
        elif ratio > 1.0:
            overall = "🟠 MIXED — Gains offset by obstacles. Cautious approach needed."
        elif ratio > 0.7:
            overall = "🟠 CHALLENGING — Expect resistance. Postpone major decisions."
        else:
            overall = "🔴 DIFFICULT — Defensive mode. Focus on damage control."
        
        lines.append(f"     Overall: {overall}")
        
        retro_count = len(retro_blocked) if retro_blocked else 0
        frozen_count = len(natal_frozen) if natal_frozen else 0
        dt_count = len(double_transit_houses) if double_transit_houses else 0
        lines.append(f"\n{'=' * 65}")
        lines.append(f"  🔱 UAKP V3.2 | K={self.K_DESTRUCTION} | EM={self.EM_ENVIRONMENT}")
        lines.append(f"  Retro-Blocked: {retro_count} | Natal-Frozen: {frozen_count} | DT Houses: {dt_count}")
        lines.append(f"  Engine: BirthDailyPrediction | KP Astrology System")
        lines.append(f"  Gates: [CLS] → [RP] → [Retro Kill] → [Sub-Lord Filter] → [DT]")
        lines.append(f"{'=' * 65}")
        
        return "\n".join(lines)
