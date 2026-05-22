from datetime import datetime
from .signification import ChartDecomposer
from .core_transit import DivineTransitEngine

# Sidereal Signs Mapping
SIGN_MAP = {0: "Aries", 1: "Taurus", 2: "Gemini", 3: "Cancer", 4: "Leo", 5: "Virgo",
            6: "Libra", 7: "Scorpio", 8: "Sagittarius", 9: "Capricorn", 10: "Aquarius", 11: "Pisces"}
SIGN_INDEX = {v: k for k, v in SIGN_MAP.items()}

class TitaniumAdvancedFilter:
    """Advanced filtering logic for exact KP predictions using retrogression and sub-lord denial."""
    
    # Negation Houses for different event types
    NEGATION_HOUSES = {
        "marriage": {1, 6, 10, 12},      # Denial houses for marriage
        "wealth": {5, 8, 12},            # Loss houses for wealth
        "career": {6, 8, 12},            # Obstruction houses for career
        "health": {6, 8, 12},            # Danger houses for health
        "child": {1, 4, 10, 12},         # Denial houses for progeny
        "general": {6, 8, 12}            # General negation houses
    }
    
    # Success Houses for different event types
    SUCCESS_HOUSES = {
        "marriage": {2, 7, 11},
        "wealth": {2, 6, 10, 11},
        "career": {2, 6, 10, 11},
        "health": {1, 5, 11},
        "child": {2, 5, 11},
        "general": {2, 5, 9, 11}
    }
    
    # Rahu/Ketu exemption
    RETRO_EXEMPT = {"Rahu", "Ketu", "Rah", "Ket"}
    
    @staticmethod
    def check_retrogression(planet_data: dict, transit_data: dict = None) -> tuple:
        """
        Rule 1: Retrogression Check (UAKP V3.2)
        Uses TRANSIT star lord retro check when transit_data is available.
        If transit star lord is retrograde → Kill-Switch (blocked).
        Rahu/Ketu exempt from kill-switch but dampened if host retro.
        """
        planet_name = planet_data.get('planet', '')
        
        if transit_data:
            # UAKP V3.2: Check transit star lord retro (the real kill-switch)
            star_lord = transit_data.get('star_lord', '')
            star_lord_full = star_lord  # Already short key from transit engine
            
            # Rahu/Ketu exemption
            if star_lord_full in TitaniumAdvancedFilter.RETRO_EXEMPT:
                return True, "CLEAR (Star Lord is Rahu/Ketu — exempt)"
            
            # Check if star lord is currently retrograde in transit
            is_star_lord_retro = transit_data.get('is_retrograde', False)
            # Actually we need to check the star lord's own transit data,
            # but that requires all transit data. Fall back to flag if available.
            star_lord_retro = planet_data.get('star_lord_is_retro', False)
            
            if star_lord_retro or is_star_lord_retro:
                return False, f"KILL-SWITCH (Transit Star Lord {star_lord} Retrograde)"
            return True, "CLEAR (Transit Star Lord Direct)"
        else:
            # Fallback: Natal retro check (legacy)
            is_retro = planet_data.get('is_retrograde', False)
            star_lord_retro = planet_data.get('star_lord_is_retro', False)
            
            if star_lord_retro:
                return False, "DELAYED/DENIED (Star Lord Retrograde)"
            if is_retro:
                return False, "DELAYED (Planet Retrograde)"
            return True, "CLEAR (No Retrogression)"
    
    @staticmethod
    def check_sub_lord_denial(sub_lord_houses: set, event_type: str = "general") -> tuple:
        """
        Rule 2: Sub-Lord Denial Check
        If sub-lord signifies negation houses more than success houses, it's a false promise.
        """
        negation = TitaniumAdvancedFilter.NEGATION_HOUSES.get(event_type, TitaniumAdvancedFilter.NEGATION_HOUSES["general"])
        success = TitaniumAdvancedFilter.SUCCESS_HOUSES.get(event_type, TitaniumAdvancedFilter.SUCCESS_HOUSES["general"])
        
        neg_hits = sub_lord_houses & negation
        pos_hits = sub_lord_houses & success
        
        if neg_hits and not pos_hits:
            return False, f"FALSE PROMISE (Sub-Lord Negation: {neg_hits})"
        elif len(neg_hits) > len(pos_hits):
            return False, f"WEAK PROMISE (Negation > Promise: {neg_hits} vs {pos_hits})"
        elif pos_hits and not neg_hits:
            return True, f"STRONG PROMISE (Pure Success: {pos_hits})"
        elif pos_hits and neg_hits:
            return True, f"MIXED (Promise with obstacles: {pos_hits} vs {neg_hits})"
        else:
            return None, "NEUTRAL (No clear indication)"
    
    @staticmethod
    def titanium_advanced_filter(planet_data: dict, sub_lord_houses: set, event_type: str = "general") -> dict:
        """
        Master Filter: Combines retrogression and sub-lord denial checks.
        Returns a comprehensive verdict.
        """
        result = {
            "status": "PENDING",
            "retro_check": None,
            "sub_lord_check": None,
            "final_verdict": "",
            "confidence": 0
        }
        
        # Rule 1: Retrogression Check
        retro_pass, retro_msg = TitaniumAdvancedFilter.check_retrogression(planet_data)
        result["retro_check"] = retro_msg
        
        if not retro_pass:
            result["status"] = "DENIED"
            result["final_verdict"] = retro_msg
            result["confidence"] = 20
            return result
        
        # Rule 2: Sub-Lord Denial Check
        sub_pass, sub_msg = TitaniumAdvancedFilter.check_sub_lord_denial(sub_lord_houses, event_type)
        result["sub_lord_check"] = sub_msg
        
        if sub_pass is False:
            result["status"] = "FALSE_PROMISE"
            result["final_verdict"] = sub_msg
            result["confidence"] = 30
        elif sub_pass is True:
            result["status"] = "SUCCESS"
            result["final_verdict"] = sub_msg
            result["confidence"] = 85 if "STRONG" in sub_msg else 65
        else:
            result["status"] = "NEUTRAL"
            result["final_verdict"] = sub_msg
            result["confidence"] = 50
        
        return result


class SevenLayerAnalyzer:
    """
    🔱 SEVEN LAYER ANALYZER: Multi-layer divine verification system.
    """
    
    def __init__(self, chart_data, decomposer=None):
        self.chart_data = chart_data
        self.decomposer = decomposer or ChartDecomposer(chart_data)
        self.cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
        self.planets_data = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
        self.planet_sigs = {p['planet']: p for p in chart_data.get('planet_significators', [])}
        # Create transit engine instance for ephemeris calculations
        try:
            self._transit_engine = DivineTransitEngine(chart_data)
        except Exception:
            self._transit_engine = None
    
    # Rahu/Ketu exemption set
    RETRO_EXEMPT = {"Rahu", "Ketu"}
    # Negative houses for Sub-Lord Filter
    NEGATIVE_HOUSES = {6, 8, 12}
    # Name normalization map
    NAME_MAP = {
        'Sun': 'Sun', 'Mon': 'Moon', 'Mar': 'Mars', 'Mer': 'Mercury',
        'Jup': 'Jupiter', 'Ven': 'Venus', 'Sat': 'Saturn',
        'Rah': 'Rahu', 'Ket': 'Ketu',
        'Moon': 'Moon', 'Mars': 'Mars', 'Mercury': 'Mercury',
        'Jupiter': 'Jupiter', 'Venus': 'Venus', 'Saturn': 'Saturn',
        'Rahu': 'Rahu', 'Ketu': 'Ketu'
    }
    MAJOR_TRANSIT = {"Jupiter", "Saturn", "Rahu", "Ketu"}
    
    def _normalize(self, name):
        return self.NAME_MAP.get(name, name)
    
    def _get_planet_houses(self, planet_name):
        """Get houses signified by a planet from planet_significators."""
        for sig in self.chart_data.get('planet_significators', []):
            p = sig.get('planet', '')
            if self._normalize(p) == self._normalize(planet_name):
                houses = set()
                for key in ['Source_Row', 'Result_Row']:
                    val = sig.get(key, '')
                    if isinstance(val, str):
                        for part in val.replace(',', ' ').split():
                            try: houses.add(int(part))
                            except ValueError: pass
                    elif isinstance(val, (list, tuple)):
                        houses.update(int(x) for x in val if str(x).isdigit())
                return houses
        return set()
    
    def layer_1_csl_promise(self, cusp_num, promise_houses, denial_houses):
        """Layer 1: CSL Promise Check"""
        csl = self.cusps.get(cusp_num, {}).get('sub_lord', '')
        if not csl:
            return False, 0, f"CSL for cusp {cusp_num} not found"
        
        csl_houses = self.decomposer.get_planet_houses(csl, 'both')
        
        promise_hit = csl_houses & promise_houses
        denial_hit = csl_houses & denial_houses
        
        if promise_hit and not denial_hit:
            return True, 25, f"CSL {csl} STRONG PROMISE: {list(promise_hit)}"
        elif promise_hit and denial_hit:
            if len(promise_hit) >= len(denial_hit):
                return True, 15, f"CSL {csl} MIXED but positive: Promise {list(promise_hit)} vs Denial {list(denial_hit)}"
            else:
                return False, 5, f"CSL {csl} MIXED but negative: Denial stronger"
        elif denial_hit and not promise_hit:
            return False, 0, f"CSL {csl} DENIED: {list(denial_hit)}"
        else:
            return None, 10, f"CSL {csl} NEUTRAL: No clear indication"
    
    def layer_2_signification_intersection(self, planets, target_houses, min_intersection=2):
        """Layer 2: Check signification intersection of MD/AD/PD lords with target houses."""
        total_score, matches = self.decomposer.get_atomic_intersection(planets, target_houses)
        valid_planets = len([m for m in matches if m['score'] >= 5])
        
        if valid_planets >= min_intersection:
            return True, min(total_score, 20), f"INTERSECTION CONFIRMED ({valid_planets}/3): {[m['planet'] for m in matches]}"
        elif valid_planets == 1:
            return None, 10, f"WEAK INTERSECTION (1/3): {matches[0]['planet'] if matches else 'None'}"
        else:
            return False, 0, "NO INTERSECTION: Target houses not signified"
    
    def layer_3_dasha_analysis(self, md, ad, pd, event_houses):
        """Layer 3: Dasha lordship deep analysis."""
        md_houses = self.decomposer.get_planet_houses(md, 'result')
        ad_houses = self.decomposer.get_planet_houses(ad, 'result')
        pd_houses = self.decomposer.get_planet_houses(pd, 'result')
        
        md_match = bool(md_houses & event_houses)
        ad_match = bool(ad_houses & event_houses)
        pd_match = bool(pd_houses & event_houses)
        
        match_count = sum([md_match, ad_match, pd_match])
        
        if match_count == 3:
            return True, 20, f"TRIPLE LOCK: MD({md}):{list(md_houses & event_houses)} AD({ad}):{list(ad_houses & event_houses)} PD({pd}):{list(pd_houses & event_houses)}"
        elif match_count == 2:
            return True, 15, f"DOUBLE LOCK ({match_count}/3)"
        elif match_count == 1:
            return None, 8, f"WEAK ({match_count}/3)"
        else:
            return False, 0, "NO DASHA MATCH"
    
    def layer_4_transit_check(self, event_date, target_signs):
        """
        Layer 4: UAKP V3.2 Full Transit Check.
        Uses DivineTransitEngine for real ephemeris positions.
        Checks ALL 9 planets for:
          - House position match with event houses
          - Star lord connection to event houses
          - Sub-Lord Filter: sub lord signifies 6/8/12 → penalty
          - Rahu/Ketu host dampening (0.7×)
        """
        if not self._transit_engine:
            # Fallback to legacy Sun-only check
            return self._legacy_transit_check(event_date, target_signs)
        
        try:
            transits = self._transit_engine.get_all_planet_positions(event_date)
        except Exception:
            return self._legacy_transit_check(event_date, target_signs)
        
        # Convert target_signs (indices) to target houses
        # target_signs are sign indices but we need to check house signification
        score = 0.0
        details = []
        sub_lord_warning = False
        
        # Build retro-blocked and rahu-ketu dampened sets
        retro_blocked = set()
        rk_dampened = set()
        for short_name, pos_data in transits.items():
            if not pos_data:
                continue
            full_name = self._normalize(short_name)
            star_lord_short = pos_data.get('star_lord', '')
            star_lord_full = self._normalize(star_lord_short)
            
            # Kill-Switch: star lord is retro (Rahu/Ketu exempt)
            if star_lord_full not in self.RETRO_EXEMPT:
                sl_data = transits.get(star_lord_short)
                if sl_data and sl_data.get('is_retrograde', False):
                    retro_blocked.add(full_name)
            
            # Rahu/Ketu host check
            if full_name in {'Rahu', 'Ketu'}:
                sign_lord_short = pos_data.get('sign_lord', '')
                if sign_lord_short:
                    host_data = transits.get(sign_lord_short)
                    if host_data and host_data.get('is_retrograde', False):
                        host_full = self._normalize(sign_lord_short)
                        if host_full not in self.RETRO_EXEMPT:
                            rk_dampened.add(full_name)
        
        # Check each transit planet for event house support
        for short_name, pos_data in transits.items():
            if not pos_data:
                continue
            full_name = self._normalize(short_name)
            
            if full_name in retro_blocked:
                details.append(f"{full_name}: BLOCKED (star lord retro)")
                continue
            
            damp = 0.7 if full_name in rk_dampened else 1.0
            transit_sign_idx = pos_data.get('sign_index', -1)
            
            # Check sign match with target signs
            if transit_sign_idx in target_signs:
                planet_score = (1.5 if full_name in self.MAJOR_TRANSIT else 0.5) * damp
                score += planet_score
                details.append(f"{full_name} in target sign {SIGN_MAP.get(transit_sign_idx, '?')} (+{planet_score:.1f})")
            
            # Star lord connection
            star_lord = self._normalize(pos_data.get('star_lord', ''))
            star_lord_houses = self._get_planet_houses(star_lord)
            # Convert target_signs to houses via chart cusps
            for h in range(1, 13):
                cusp_sign = self.cusps.get(h, {}).get('sign', '')
                cusp_sign_idx = SIGN_INDEX.get(cusp_sign, -1)
                if cusp_sign_idx in target_signs and h in star_lord_houses:
                    star_score = (0.5 if full_name in self.MAJOR_TRANSIT else 0.25) * damp
                    score += star_score
                    
                    # Sub-Lord Filter: check if sub lord signifies negative houses
                    sub_lord = self._normalize(pos_data.get('sub_lord', ''))
                    sub_lord_houses = self._get_planet_houses(sub_lord)
                    if sub_lord_houses & self.NEGATIVE_HOUSES:
                        sub_lord_warning = True
                    break
        
        # Apply Sub-Lord Filter penalty
        if sub_lord_warning:
            score *= 0.5
        
        score = min(score, 15)  # Cap at 15 for layer scoring
        passed = score >= 3.0
        
        blocked_str = f" | Retro-Blocked: {len(retro_blocked)}" if retro_blocked else ""
        sub_str = " | Sub-Lord Filter: TA×0.5" if sub_lord_warning else ""
        rk_str = f" | RK Dampened: {len(rk_dampened)}" if rk_dampened else ""
        msg = f"TRANSIT V3.2: Score={score:.1f}{blocked_str}{sub_str}{rk_str}"
        
        return passed, min(int(score), 15), msg
    
    def _legacy_transit_check(self, event_date, target_signs):
        """Fallback: Hardcoded Sun sign check (no ephemeris)."""
        d, m = event_date.day, event_date.month
        sun_sign = -1
        if m == 4: sun_sign = 0 if d >= 14 else 11
        elif m == 5: sun_sign = 1 if d >= 15 else 0
        elif m == 6: sun_sign = 2 if d >= 15 else 1
        elif m == 7: sun_sign = 3 if d >= 16 else 2
        elif m == 8: sun_sign = 4 if d >= 17 else 3
        elif m == 9: sun_sign = 5 if d >= 17 else 4
        elif m == 10: sun_sign = 6 if d >= 17 else 5
        elif m == 11: sun_sign = 7 if d >= 16 else 6
        elif m == 12: sun_sign = 8 if d >= 16 else 7
        elif m == 1: sun_sign = 9 if d >= 14 else 8
        elif m == 2: sun_sign = 10 if d >= 13 else 9
        elif m == 3: sun_sign = 11 if d >= 15 else 10
        
        if sun_sign in target_signs:
            return True, 15, f"SUN TRANSIT in {SIGN_MAP.get(sun_sign, sun_sign)} (legacy)"
        else:
            return False, 0, f"Sun in {SIGN_MAP.get(sun_sign, sun_sign)} - NOT in target (legacy)"
    
    def layer_5_retrogression_check(self, planets):
        """
        Layer 5: UAKP V3.2 Retrogression Check.
        Checks if dasha lords' TRANSIT star lords are retrograde (Kill-Switch).
        Uses real transit data when available.
        """
        if not self._transit_engine:
            return self._legacy_retro_check(planets)
        
        try:
            transits = self._transit_engine.get_all_planet_positions(datetime.now())
        except Exception:
            return self._legacy_retro_check(planets)
        
        blocked = []
        clear = []
        for planet in planets:
            full = self._normalize(planet)
            # Find this planet in transits
            short_key = None
            for sk in transits:
                if self._normalize(sk) == full:
                    short_key = sk
                    break
            
            if not short_key or not transits.get(short_key):
                clear.append(planet)
                continue
            
            pos = transits[short_key]
            star_lord_short = pos.get('star_lord', '')
            star_lord_full = self._normalize(star_lord_short)
            
            # Rahu/Ketu exemption
            if star_lord_full in self.RETRO_EXEMPT:
                clear.append(f"{planet}(exempt)")
                continue
            
            # Check star lord's transit retro status
            sl_data = transits.get(star_lord_short)
            if sl_data and sl_data.get('is_retrograde', False):
                blocked.append(f"{planet}←{star_lord_full}(R)")
            else:
                clear.append(planet)
        
        if not blocked:
            return True, 10, f"NO RETRO BLOCK: All dasha lords clear [{', '.join(clear)}]"
        elif len(blocked) <= 1:
            return None, 5, f"MINOR BLOCK: {blocked[0]} | Clear: {', '.join(clear)}"
        else:
            return False, 0, f"MAJOR BLOCK: {', '.join(blocked)}"
    
    def _legacy_retro_check(self, planets):
        """Fallback: Natal retrogression check."""
        retro_count = 0
        retro_planets = []
        for planet in planets:
            p_data = self.planets_data.get(planet, {})
            if p_data.get('is_retrograde', False):
                retro_count += 1
                retro_planets.append(planet)
        if retro_count == 0:
            return True, 10, "NO RETROGRESSION: Timing clear (legacy)"
        elif retro_count == 1:
            return None, 5, f"MINOR DELAY: {retro_planets[0]} retrograde (legacy)"
        else:
            return False, 0, f"MAJOR DELAY: {retro_planets} retrograde (legacy)"
    
    def layer_8_double_transit(self, event_date, event_houses):
        """
        Layer 8: UAKP V3.2 Double Transit Check.
        If BOTH Jupiter and Saturn support the same event house
        (via house position or star lord connection) → 1.2× confidence boost.
        """
        if not self._transit_engine:
            return None, 5, "Double Transit: ephemeris not available"
        
        try:
            transits = self._transit_engine.get_all_planet_positions(event_date)
        except Exception:
            return None, 5, "Double Transit: calculation failed"
        
        jup_data = transits.get('Jup')
        sat_data = transits.get('Sat')
        if not jup_data or not sat_data:
            return None, 5, "Double Transit: Jupiter/Saturn data missing"
        
        # Get houses supported by Jupiter
        jup_houses = set()
        jup_house = jup_data.get('house', 0)
        if jup_house: jup_houses.add(jup_house)
        jup_sl = self._normalize(jup_data.get('star_lord', ''))
        jup_houses |= self._get_planet_houses(jup_sl)
        
        # Get houses supported by Saturn
        sat_houses = set()
        sat_house = sat_data.get('house', 0)
        if sat_house: sat_houses.add(sat_house)
        sat_sl = self._normalize(sat_data.get('star_lord', ''))
        sat_houses |= self._get_planet_houses(sat_sl)
        
        # Check intersection with event houses
        dt_houses = jup_houses & sat_houses & event_houses
        
        if dt_houses:
            return True, 10, f"DOUBLE TRANSIT CONFIRMED: Jupiter+Saturn both support H{list(dt_houses)}"
        else:
            return None, 5, f"Double Transit: No common support (Jup→{list(jup_houses & event_houses)}, Sat→{list(sat_houses & event_houses)})"
    
    def layer_6_yoga_check(self, event_type):
        """Layer 6: Special yoga/combination detection."""
        yogas = []
        moon_data = self.planets_data.get('Mon', {})
        jup_data = self.planets_data.get('Jup', {})
        
        if moon_data and jup_data:
            moon_sign_idx = SIGN_INDEX.get(moon_data.get('sign', ''), -1)
            jup_sign_idx = SIGN_INDEX.get(jup_data.get('sign', ''), -1)
            if moon_sign_idx >= 0 and jup_sign_idx >= 0:
                diff = abs(moon_sign_idx - jup_sign_idx)
                if diff in [0, 3, 6, 9]:
                    yogas.append("GAJAKESARI")
        
        if event_type in ["marriage", "love", "beauty"]:
            venus_data = self.planets_data.get('Ven', {})
            if moon_data and venus_data and moon_data.get('sign') == venus_data.get('sign'):
                yogas.append("MOON-VENUS UNION")
        
        if event_type in ["wealth", "income", "money"]:
            h2_lord = self.cusps.get(2, {}).get('sign_lord', '')
            h11_lord = self.cusps.get(11, {}).get('sign_lord', '')
            h2_houses = self.decomposer.get_planet_houses(h2_lord, 'both')
            h11_houses = self.decomposer.get_planet_houses(h11_lord, 'both')
            if 11 in h2_houses or 2 in h11_houses:
                yogas.append("DHANA YOGA")
        
        if yogas:
            return True, 10, f"YOGAS DETECTED: {', '.join(yogas)}"
        else:
            return None, 5, "No special yogas detected"
    
    def layer_7_temporal_correlation(self, event_date, event_type):
        """Layer 7: Temporal pattern matching."""
        dob_str = self.chart_data.get('metadata', {}).get('dob', '')
        if not dob_str:
            return None, 5, "DOB not available for temporal check"
        
        try:
            dob = datetime.strptime(dob_str, "%d-%m-%Y")
            age_at_event = (event_date - dob).days // 365
            
            age_ranges = {
                "marriage": (18, 60), "child": (18, 50), "death": (0, 120),
                "job": (18, 70), "wealth": (18, 80), "divorce": (18, 70)
            }
            min_age, max_age = age_ranges.get(event_type, (0, 120))
            
            if min_age <= age_at_event <= max_age:
                return True, 10, f"AGE VALID: {age_at_event} years (in range {min_age}-{max_age})"
            else:
                return False, 0, f"AGE INVALID: {age_at_event} years (expected {min_age}-{max_age})"
        except:
            return None, 5, "Temporal check skipped"
    
    def run_full_analysis(self, cusp_num, promise_houses, denial_houses, 
                          md, ad, pd, event_date, target_signs, event_type):
        """Run all 8 layers (7 original + Double Transit) and return comprehensive analysis."""
        results = []
        total_score = 0
        passed_layers = 0
        
        # Sequentially running layers...
        l1 = self.layer_1_csl_promise(cusp_num, promise_houses, denial_houses)
        results.append({"layer": 1, "name": "CSL_PROMISE", "passed": l1[0], "score": l1[1], "details": l1[2]})
        total_score += l1[1]
        if l1[0]: passed_layers += 1
        
        l2 = self.layer_2_signification_intersection([md, ad, pd], promise_houses)
        results.append({"layer": 2, "name": "INTERSECTION", "passed": l2[0], "score": l2[1], "details": l2[2]})
        total_score += l2[1]
        if l2[0]: passed_layers += 1
        
        l3 = self.layer_3_dasha_analysis(md, ad, pd, promise_houses)
        results.append({"layer": 3, "name": "DASHA", "passed": l3[0], "score": l3[1], "details": l3[2]})
        total_score += l3[1]
        if l3[0]: passed_layers += 1
        
        l4 = self.layer_4_transit_check(event_date, target_signs)
        results.append({"layer": 4, "name": "TRANSIT", "passed": l4[0], "score": l4[1], "details": l4[2]})
        total_score += l4[1]
        if l4[0]: passed_layers += 1
        
        l5 = self.layer_5_retrogression_check([md, ad, pd])
        results.append({"layer": 5, "name": "RETRO", "passed": l5[0], "score": l5[1], "details": l5[2]})
        total_score += l5[1]
        if l5[0]: passed_layers += 1
        
        l6 = self.layer_6_yoga_check(event_type)
        results.append({"layer": 6, "name": "YOGA", "passed": l6[0], "score": l6[1], "details": l6[2]})
        total_score += l6[1]
        if l6[0]: passed_layers += 1
        
        l7 = self.layer_7_temporal_correlation(event_date, event_type)
        results.append({"layer": 7, "name": "TEMPORAL", "passed": l7[0], "score": l7[1], "details": l7[2]})
        total_score += l7[1]
        if l7[0]: passed_layers += 1
        
        # Layer 8: UAKP V3.2 Double Transit
        l8 = self.layer_8_double_transit(event_date, promise_houses)
        results.append({"layer": 8, "name": "DOUBLE_TRANSIT", "passed": l8[0], "score": l8[1], "details": l8[2]})
        total_score += l8[1]
        if l8[0]: passed_layers += 1
        
        final_verdict = "CONFIRMED" if passed_layers >= 6 else "LIKELY" if passed_layers >= 4 else "WEAK" if passed_layers >= 2 else "DENIED"
        
        return {
            "layers": results,
            "total_score": total_score,
            "passed_layers": passed_layers,
            "total_layers": 8,
            "final_verdict": final_verdict,
            "confidence": min(total_score, 100),
            "engine_version": "UAKP V3.2"
        }


class ConflictResolver:
    """🔱 CONFLICT RESOLVER: Handles contradictory chart indicators intelligently."""
    
    PLANET_STRENGTH = {"Sun": 7, "Mon": 6, "Mar": 6, "Mer": 5, "Jup": 8, "Ven": 7, "Sat": 6, "Rah": 5, "Ket": 4}
    EXALTATION = {
        "Sun": "Aries", "Mon": "Taurus", "Mar": "Capricorn", "Mer": "Virgo",
        "Jup": "Cancer", "Ven": "Pisces", "Sat": "Libra", "Rah": "Gemini", "Ket": "Sagittarius"
    }
    DEBILITATION = {
        "Sun": "Libra", "Mon": "Scorpio", "Mar": "Cancer", "Mer": "Pisces",
        "Jup": "Capricorn", "Ven": "Virgo", "Sat": "Aries", "Rah": "Sagittarius", "Ket": "Gemini"
    }
    
    def __init__(self, chart_data, decomposer=None):
        self.chart_data = chart_data
        self.decomposer = decomposer or ChartDecomposer(chart_data)
        self.planets_data = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
    
    def get_planet_dignity_score(self, planet):
        """Calculate planet dignity score based on sign placement."""
        p_data = self.planets_data.get(planet, {})
        sign = p_data.get('sign', '')
        base_strength = self.PLANET_STRENGTH.get(planet, 5)
        
        if sign == self.EXALTATION.get(planet):
            return base_strength + 3
        elif sign == self.DEBILITATION.get(planet):
            return base_strength - 3
        else:
            return base_strength
    
    def resolve_planet_conflict(self, planet1, planet2):
        """Resolve conflict between two planets."""
        score1 = self.get_planet_dignity_score(planet1)
        score2 = self.get_planet_dignity_score(planet2)
        
        if score1 > score2: return planet1, f"{planet1} wins (dignity {score1} vs {score2})"
        elif score2 > score1: return planet2, f"{planet2} wins (dignity {score2} vs {score1})"
        else:
            return (planet1, f"{planet1} wins (natural strength)") if self.PLANET_STRENGTH.get(planet1, 5) >= self.PLANET_STRENGTH.get(planet2, 5) else (planet2, f"{planet2} wins (natural strength)")
    
    def resolve_house_conflict(self, promise_houses, denial_houses, csl_houses):
        """Resolve conflict between promise and denial houses based on CSL."""
        csl_promise = csl_houses & promise_houses
        csl_denial = csl_houses & denial_houses
        
        if csl_promise and not csl_denial: return "PROMISE", f"CSL confirms promise: {list(csl_promise)}"
        elif csl_denial and not csl_promise: return "DENIAL", f"CSL confirms denial: {list(csl_denial)}"
        elif csl_promise and csl_denial:
            if len(csl_promise) >= len(csl_denial): return "MIXED_POSITIVE", f"CSL leans positive: {len(csl_promise)} promise vs {len(csl_denial)} denial"
            else: return "MIXED_NEGATIVE", f"CSL leans negative: {len(csl_denial)} denial vs {len(csl_promise)} promise"
        else:
            if len(promise_houses) > len(denial_houses): return "WEAK_PROMISE", "More promise indicators"
            elif len(denial_houses) > len(promise_houses): return "WEAK_DENIAL", "More denial indicators"
            else: return "NEUTRAL", "Equal promise and denial"

    def generate_conflict_report(self, md, ad, pd, promise_houses, denial_houses, cusp_num):
        """Generate comprehensive conflict analysis report."""
        report = {"conflicts_detected": [], "resolutions": [], "final_verdict": "", "confidence_adjustment": 0}
        
        csl = self.decomposer.get_cusp_sub_lord(cusp_num)
        csl_houses = self.decomposer.get_planet_houses(csl, 'both')
        house_verdict, house_reason = self.resolve_house_conflict(promise_houses, denial_houses, csl_houses)
        
        if "MIXED" in house_verdict:
            report["conflicts_detected"].append("House promise/denial conflict")
            report["resolutions"].append(house_reason)
            report["confidence_adjustment"] -= 10
        
        dasha_lords = [md, ad, pd]
        weak_lords = []
        for lord in dasha_lords:
            if self.get_planet_dignity_score(lord) < 4:
                weak_lords.append(lord)
        
        if weak_lords:
            report["conflicts_detected"].append(f"Weak dasha lords: {weak_lords}")
            report["confidence_adjustment"] -= len(weak_lords) * 5
        
        if "DENIAL" in house_verdict: report["final_verdict"] = "EVENT_BLOCKED"
        elif "PROMISE" in house_verdict: report["final_verdict"] = "EVENT_CONFIRMED"
        elif "NEUTRAL" in house_verdict: report["final_verdict"] = "EVENT_UNCERTAIN"
        else: report["final_verdict"] = "EVENT_POSSIBLE"
        
        return report


class DivineScorer:
    """🔱 DIVINE SCORER: Weighted confidence calculation system."""
    
    def __init__(self):
        self.score_breakdown = {}
    
    def calculate_divine_score(self, layer_results, conflict_report=None):
        self.score_breakdown = {
            "csl_alignment": 0, "dasha_match": 0, "transit_trigger": 0,
            "house_strength": 0, "yoga_bonus": 0, "layer_passage": 0, 
            "double_transit": 0, "deductions": 0
        }
        
        for layer in layer_results.get("layers", []):
            if layer["name"] == "CSL_PROMISE": self.score_breakdown["csl_alignment"] = min(layer["score"], 25)
            elif layer["name"] == "DASHA": self.score_breakdown["dasha_match"] = min(layer["score"], 20)
            elif layer["name"] == "TRANSIT": self.score_breakdown["transit_trigger"] = min(layer["score"], 15)
            elif layer["name"] == "INTERSECTION": self.score_breakdown["house_strength"] = min(layer["score"], 15)
            elif layer["name"] == "YOGA": self.score_breakdown["yoga_bonus"] = min(layer["score"], 10)
            elif layer["name"] == "DOUBLE_TRANSIT": self.score_breakdown["double_transit"] = min(layer["score"], 10)
        
        passed = layer_results.get("passed_layers", 0)
        self.score_breakdown["layer_passage"] = min(passed * 2, 16)  # Max 8 layers × 2
        
        if conflict_report:
            self.score_breakdown["deductions"] = conflict_report.get("confidence_adjustment", 0)
        
        total = sum(v for k, v in self.score_breakdown.items() if k != "deductions")
        total += self.score_breakdown["deductions"]
        
        return max(0, min(100, total))

    def get_confidence_level(self, score):
        if score >= 80: return "DIVINE CERTAINTY"
        elif score >= 65: return "HIGH CONFIDENCE"
        elif score >= 50: return "MODERATE CONFIDENCE"
        elif score >= 35: return "LOW CONFIDENCE"
        elif score >= 20: return "WEAK INDICATION"
        else: return "VERY WEAK / UNLIKELY"
    
    def get_score_breakdown_string(self):
        lines = ["📊 DIVINE SCORE BREAKDOWN:"]
        for k, v in self.score_breakdown.items():
            if k == "deductions" and v < 0:
                lines.append(f"   Deductions: {v}")
            elif k != "deductions":
                lines.append(f"   {k.replace('_', ' ').title()}: +{v}")
        return "\n".join(lines)


class PatternDetector:
    """🔱 PATTERN DETECTOR: Yoga and special combination recognition."""
    
    def __init__(self, chart_data, decomposer=None):
        self.chart_data = chart_data
        self.decomposer = decomposer or ChartDecomposer(chart_data)
        self.planets_data = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
        self.cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
    
    def detect_gajakesari(self):
        moon = self.planets_data.get('Mon', {})
        jupiter = self.planets_data.get('Jup', {})
        if not moon or not jupiter: return None
        
        moon_idx = SIGN_INDEX.get(moon.get('sign', ''), -1)
        jup_idx = SIGN_INDEX.get(jupiter.get('sign', ''), -1)
        
        if moon_idx >= 0 and jup_idx >= 0:
            diff = (jup_idx - moon_idx) % 12
            if diff in [0, 3, 6, 9]:
                return {"yoga": "GAJAKESARI", "strength": "STRONG" if diff == 0 else "MODERATE", 
                        "effect": "Wisdom, fame, and prosperity", "planets": ["Mon", "Jup"]}
        return None
    
    def detect_dhana_yogas(self):
        yogas = []
        h2_lord = self.cusps.get(2, {}).get('sign_lord', '')
        h11_lord = self.cusps.get(11, {}).get('sign_lord', '')
        
        h2_houses = self.decomposer.get_planet_houses(h2_lord, 'both')
        h11_houses = self.decomposer.get_planet_houses(h11_lord, 'both')
        
        if 11 in h2_houses: yogas.append({"yoga": "DHANA YOGA (2-11)", "strength": "STRONG", "effect": "Wealth accumulation", "planets": [h2_lord]})
        if 2 in h11_houses: yogas.append({"yoga": "DHANA YOGA (11-2)", "strength": "STRONG", "effect": "Financial gains", "planets": [h11_lord]})
        
        h5_lord = self.cusps.get(5, {}).get('sign_lord', '')
        h9_lord = self.cusps.get(9, {}).get('sign_lord', '')
        h5_houses = self.decomposer.get_planet_houses(h5_lord, 'both')
        h9_houses = self.decomposer.get_planet_houses(h9_lord, 'both')
        
        if (2 in h5_houses or 11 in h5_houses) and (2 in h9_houses or 11 in h9_houses):
            yogas.append({"yoga": "LAKSHMI YOGA", "strength": "VERY STRONG", "effect": "Great fortune", "planets": [h5_lord, h9_lord]})
        return yogas

    def detect_maraka_pattern(self):
        patterns = []
        h2_lord = self.cusps.get(2, {}).get('sign_lord', '')
        h7_lord = self.cusps.get(7, {}).get('sign_lord', '')
        death_houses = {8, 12}
        
        h2_houses = self.decomposer.get_planet_houses(h2_lord, 'both')
        h7_houses = self.decomposer.get_planet_houses(h7_lord, 'both')
        
        if h2_houses & death_houses: patterns.append({"pattern": "MARAKA (2nd Lord)", "strength": "ACTIVE", "planets": [h2_lord], "houses": list(h2_houses & death_houses)})
        if h7_houses & death_houses: patterns.append({"pattern": "MARAKA (7th Lord)", "strength": "ACTIVE", "planets": [h7_lord], "houses": list(h7_houses & death_houses)})
        return patterns

    def detect_kemadruma(self):
        moon = self.planets_data.get('Mon', {})
        if not moon: return None
        moon_idx = SIGN_INDEX.get(moon.get('sign', ''), -1)
        if moon_idx < 0: return None
        
        prev, next_s = (moon_idx - 1) % 12, (moon_idx + 1) % 12
        planets_in_adj = any(SIGN_INDEX.get(d.get('sign', ''), -1) in [prev, next_s] for p, d in self.planets_data.items() if p != 'Mon')
        
        if not planets_in_adj:
            return {"yoga": "KEMADRUMA", "strength": "MODERATE", "effect": "Emotional isolation", "planets": ["Mon"]}
        return None

    def get_all_patterns(self, event_type="general"):
        all_patterns = {"positive_yogas": [], "negative_patterns": [], "net_effect": "NEUTRAL"}
        
        gajakesari = self.detect_gajakesari()
        if gajakesari: all_patterns["positive_yogas"].append(gajakesari)
        
        if event_type in ["wealth", "money", "income", "job", "business"]:
            all_patterns["positive_yogas"].extend(self.detect_dhana_yogas())
        
        if event_type in ["death", "life", "health", "hospital"]:
            all_patterns["negative_patterns"].extend(self.detect_maraka_pattern())
        
        kemadruma = self.detect_kemadruma()
        if kemadruma: all_patterns["negative_patterns"].append(kemadruma)
        
        pos, neg = len(all_patterns["positive_yogas"]), len(all_patterns["negative_patterns"])
        if pos > neg: all_patterns["net_effect"] = "POSITIVE"
        elif neg > pos: all_patterns["net_effect"] = "NEGATIVE"
        return all_patterns
