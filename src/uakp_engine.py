import logging
from typing import Dict, List, Set, Any, Optional
# pyre-ignore
from src.signification import DataConverter

# 🔱 UAKP CORE MAPPINGS
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# 🔱 UAKP CO-LORDSHIP MAPPING (V3.2)
# Aquarius = Saturn + Rahu
# Scorpio = Mars + Ketu
CO_LORDS = {
    "Aquarius": ["Saturn", "Rahu"],
    "Scorpio": ["Mars", "Ketu"]
}

class UAKPEngine(object):
    """
    🔱 ULTRA-ADVANCED KP (UAKP) BASE ENGINE
    
    Provides foundational logical structures for all rectified prediction engines.
    """
    
    VALID_PLANETS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
    
    def __init__(self, data: Dict[str, Any]) -> None:
        self.raw_data: Dict[str, Any] = data
        self.planets: Dict[str, Dict[str, Any]] = {}
        self.cusps: Dict[int, Dict[str, Any]] = {}
        self._sig_cache: Dict[str, Set[int]] = {}
        self.errors: List[str] = []
        
        self._load_cusps()
        self._load_planets()
        self._resolve_node_agents()

    def _normalize_name(self, name: Optional[str]) -> Optional[str]:
        if not name: return None
        n = str(name).strip().title()
        abbrev = {
            "Rah": "Rahu", "Ket": "Ketu", "Mer": "Mercury", 
            "Ven": "Venus", "Jup": "Jupiter", "Sat": "Saturn", 
            "Mar": "Mars", "Mon": "Moon"
        }
        return abbrev.get(n, n)

    def _load_cusps(self):
        cusp_data_raw = self.raw_data.get('house_cusps', [])
        if not cusp_data_raw:
            cusp_data_raw = self.raw_data.get('cusps', {})
            
        # Robustness: Handle both list of dicts and dict of dicts/values
        if isinstance(cusp_data_raw, dict):
            # If it's a dict like {1: {data}, 2: {data}}, we want the values
            # If it's a dict like {1: long, 2: long}, we'll need to wrap them
            cusp_data = []
            for cid, cval in cusp_data_raw.items():
                if isinstance(cval, dict):
                    if 'cusp' not in cval and 'id' not in cval:
                        cval['cusp'] = cid
                    cusp_data.append(cval)
                else:
                    # Basic longitude float fallback
                    cusp_data.append({'cusp': cid, 'longitude': cval})
        else:
            cusp_data = cusp_data_raw

        if len(cusp_data) < 12:
            logging.warning(f"DATA WARNING: Found only {len(cusp_data)} cusps.")
            
        for c in cusp_data:
            cid_raw = c.get('cusp') or c.get('id') or 0
            cid = int(cid_raw)
            if not cid: continue
            
            try:
                fdeg = DataConverter.get_absolute_longitude(c)
            except Exception as e:
                logging.error(f"Error parsing cusp {cid} degree: {e}")
                fdeg = 0.0

            self.cusps[cid] = {
                'id': cid,
                'sign': c.get('sign'),
                'sub_lord': self._normalize_name(c.get('sub_lord', c.get('sub'))),
                'sign_lord': self._normalize_name(c.get('sign_lord', c.get('lord'))),
                'full_degree': fdeg
            }

    def _load_planets(self):
        planet_data_raw = self.raw_data.get('planetary_positions', [])
        if not planet_data_raw:
            planet_data_raw = self.raw_data.get('planets', {})
            
        if isinstance(planet_data_raw, dict):
            planet_data = []
            for p_name, p_val in planet_data_raw.items():
                if isinstance(p_val, dict):
                    if 'planet' not in p_val and 'name' not in p_val:
                        p_val['planet'] = p_name
                    planet_data.append(p_val)
                else:
                    # Basic longitude float fallback
                    planet_data.append({'planet': p_name, 'longitude': p_val})
        else:
            planet_data = planet_data_raw

        for p in planet_data:
            if not isinstance(p, dict): continue
            raw_name = p.get('planet', p.get('name'))
            name = self._normalize_name(raw_name)
            if name:
                try:
                    fdeg = DataConverter.get_absolute_longitude(p)
                except Exception as e:
                    logging.error(f"Error parsing planet {name} degree: {e}")
                    fdeg = 0.0

                house_occ = self._calculate_placidus_house(fdeg)
                
                self.planets[name] = {
                    'name': name,
                    'sign': p.get('sign'),
                    'full_degree': fdeg,
                    'star_lord': self._normalize_name(p.get('star_lord', p.get('star'))),
                    'sub_lord': self._normalize_name(p.get('sub_lord', p.get('sub'))),
                    'is_retro': p.get('is_retrograde', False),
                    'house_occ': house_occ,
                    'owned_houses': [], 
                    'is_node': name in {"Rahu", "Ketu"},
                    'agents': set() # type: Set[str]
                }

        for cid, cdata in self.cusps.items():
            sign = cdata.get('sign')
            if not sign: continue
            
            primary_lord = SIGN_LORDS.get(sign)
            lords = [primary_lord] if primary_lord else []
            if sign in CO_LORDS:
                for cl in CO_LORDS[sign]:
                    if cl not in lords:
                        lords.append(cl)
            
            for lord in lords:
                normalized_lord = self._normalize_name(lord)
                if normalized_lord and normalized_lord in self.planets:
                    # At this point, normalized_lord is guaranteed to be a str and in self.planets
                    n_lord: str = normalized_lord
                    p_entry = self.planets[n_lord]
                    if 'owned_houses' not in p_entry or p_entry['owned_houses'] is None:
                        p_entry['owned_houses'] = []
                    # pyre-ignore
                    p_entry['owned_houses'].append(cid)

    def _calculate_placidus_house(self, planet_deg: float) -> int:
        if not self.cusps: return 1
        for i in range(1, 13):
            next_i = (i % 12) + 1
            cusp_curr_val = self.cusps.get(i, {}).get('full_degree')
            cusp_next_val = self.cusps.get(next_i, {}).get('full_degree')
            
            if cusp_curr_val is None or cusp_next_val is None:
                continue
            
            # pyre-ignore
            c_curr: float = float(cusp_curr_val)
            # pyre-ignore
            c_next: float = float(cusp_next_val)
            
            dist_p = (planet_deg - c_curr) % 360
            span = (c_next - c_curr) % 360
            if dist_p < span: return i
        return 1

    def get_cusp_data(self, house_id: int) -> Optional[Dict[str, Any]]:
        return self.cusps.get(house_id)

    def _resolve_node_agents(self):
        for name, pdata in self.planets.items():
            if pdata['is_node']:
                sign_val = pdata.get('sign')
                if not sign_val or not isinstance(sign_val, str):
                    continue
                
                primary_dispositor = SIGN_LORDS.get(sign_val)
                if primary_dispositor:
                    norm_agent = self._normalize_name(primary_dispositor)
                    if norm_agent:
                        pdata['agents'].add(norm_agent)

    def get_planetary_strength(self, planet_name: str) -> float:
        """
        🔱 CENTRALIZED DIGNITY ENGINE (V6.0)
        Calculates normalized strength (0-100) based on Exaltation, Ownership, and Debilitation.
        """
        p = self.planets.get(planet_name)
        if not p: return 50.0
        
        strength = 50.0
        sign = p.get('sign')
        
        # 🔱 DIGNITY DATABASE
        dignities = {
            "Sun": {"Ex": "Aries", "Own": ["Leo"], "Deb": "Libra"},
            "Moon": {"Ex": "Taurus", "Own": ["Cancer"], "Deb": "Scorpio"},
            "Mars": {"Ex": "Capricorn", "Own": ["Aries", "Scorpio"], "Deb": "Cancer"},
            "Mercury": {"Ex": "Virgo", "Own": ["Gemini", "Virgo"], "Deb": "Pisces"},
            "Jupiter": {"Ex": "Cancer", "Own": ["Sagittarius", "Pisces"], "Deb": "Capricorn"},
            "Venus": {"Ex": "Pisces", "Own": ["Taurus", "Libra"], "Deb": "Virgo"},
            "Saturn": {"Ex": "Libra", "Own": ["Capricorn", "Aquarius"], "Deb": "Aries"},
            "Rahu": {"Ex": "Taurus", "Own": ["Aquarius"], "Deb": "Scorpio"}, # KP Co-lordship logic
            "Ketu": {"Ex": "Scorpio", "Own": ["Scorpio"], "Deb": "Taurus"}    # KP Co-lordship logic
        }
        
        rules = dignities.get(planet_name)
        if rules and sign:
            ex = rules.get("Ex")
            own = rules.get("Own")
            deb = rules.get("Deb")
            
            if sign == ex: 
                strength += 25
            elif own and sign in own:
                strength += 15
            elif sign == deb: 
                strength -= 25
            
        return strength

    def get_significators(self, planet_name: Optional[str], visited: Optional[Set[str]] = None) -> Set[int]:
        normalized_name = self._normalize_name(planet_name)
        if not normalized_name or normalized_name not in self.planets: return set()
        
        # narrow type for Pyre
        n_name = str(normalized_name)
        
        if n_name in self._sig_cache: return self._sig_cache[n_name]
        
        v_set = visited if visited is not None else set()
        if n_name in v_set: return set()
        v_set.add(n_name)
        
        p = self.planets[n_name]
        houses = {p['house_occ']} if p['house_occ'] else set()
        houses.update(p['owned_houses'])
        if p['is_node']:
            for agent in p['agents']:
                houses.update(self.get_significators(agent, v_set))
                
        if len(v_set) == 1: self._sig_cache[n_name] = houses
        return houses

    def analyze_4_step(self, planet_name: str) -> Dict[str, Set[int]]:
        normalized_name = self._normalize_name(planet_name)
        if not normalized_name or normalized_name not in self.planets:
            return {'L1': set(), 'L2': set(), 'L3': set(), 'L4': set()}
        
        # narrow type for Pyre
        n_name = str(normalized_name)
        p = self.planets[n_name]
        star = p['star_lord']
        sub = p['sub_lord']
        l1 = self.get_significators(normalized_name)
        l2 = self.get_significators(star) if star else set()
        l3 = self.get_significators(sub) if sub else set()
        l4 = set()
        if sub and sub in self.planets:
            # narrow type for Pyre
            s_name: str = sub
            sub_star = self.planets[s_name]['star_lord']
            l4 = self.get_significators(sub_star) if sub_star else set()
        return {'L1': l1, 'L2': l2, 'L3': l3, 'L4': l4}

    def evaluate_promise_deliver(
        self,
        planet_name: str,
        positive_houses: Set[int],
        negative_houses: Set[int],
        topic_label: str = "this matter"
    ) -> Dict[str, Any]:
        """
        🔱 PROMISE vs DELIVER EVALUATOR (V8.0)

        KP Rule: Star Lord (L2) = Promise/Source/Reason
                 Sub Lord  (L3) = Deliver/Result/Outcome
                 Deliver > Promise (Sub Lord is final decision-maker)

        Args:
            planet_name: The CSL or planet to evaluate
            positive_houses: Houses that support the topic
            negative_houses: Houses that oppose the topic
            topic_label: Human-readable label for narrative generation

        Returns:
            Structured dict with promise_score, deliver_score, combined_score,
            verdict, explanation (plain English), and technical_details.
        """
        steps = self.analyze_4_step(planet_name)
        promise_houses = steps['L2']   # Star Lord significations
        deliver_houses = steps['L3']   # Sub Lord significations

        # Score each row against positive/negative house sets
        promise_pos = len(promise_houses & positive_houses)
        promise_neg = len(promise_houses & negative_houses)
        deliver_pos = len(deliver_houses & positive_houses)
        deliver_neg = len(deliver_houses & negative_houses)

        promise_score = promise_pos - promise_neg
        deliver_score = deliver_pos - deliver_neg

        # Deliver > Promise: weight deliver at 1.5x
        combined = promise_score + (deliver_score * 1.5)

        # Derive verdict from Deliver row (it's the final judge)
        if deliver_score > 0 and promise_score > 0:
            verdict = "STRONGLY FAVORABLE"
        elif deliver_score > 0 and promise_score <= 0:
            verdict = "FAVORABLE (Outcome overrides weak source)"
        elif deliver_score == 0 and promise_score > 0:
            verdict = "PROMISING BUT UNCERTAIN (Source is strong, outcome unclear)"
        elif deliver_score < 0 and promise_score > 0:
            verdict = "BLOCKED (Source promises, but outcome denied)"
        elif deliver_score < 0 and promise_score <= 0:
            verdict = "UNFAVORABLE"
        else:
            verdict = "NEUTRAL"

        # --- Human-readable explanation ---
        p_houses_str = ", ".join(str(h) for h in sorted(promise_houses)) if promise_houses else "none"
        d_houses_str = ", ".join(str(h) for h in sorted(deliver_houses)) if deliver_houses else "none"
        pos_str = ", ".join(str(h) for h in sorted(positive_houses))
        neg_str = ", ".join(str(h) for h in sorted(negative_houses)) if negative_houses else "none"

        # Build explanation based on verdict
        if "STRONGLY FAVORABLE" in verdict:
            explanation = (
                f"Both the source and outcome strongly support {topic_label}. "
                f"The conditions that create this opportunity (houses {p_houses_str}) align well "
                f"with the final result (houses {d_houses_str}), producing a clear positive outcome."
            )
        elif "FAVORABLE" in verdict:
            explanation = (
                f"The final outcome for {topic_label} is positive, even though the initial conditions are modest. "
                f"The Sub Lord delivers through houses {d_houses_str}, confirming a favorable result."
            )
        elif "PROMISING BUT UNCERTAIN" in verdict:
            explanation = (
                f"There is a strong underlying potential for {topic_label} (source houses: {p_houses_str}), "
                f"but the final outcome depends on timing and transit activation. "
                f"The Sub Lord's significations ({d_houses_str}) are neutral — results may vary."
            )
        elif "BLOCKED" in verdict:
            explanation = (
                f"Although there is a clear desire and source energy for {topic_label} "
                f"(houses {p_houses_str}), the Sub Lord blocks full realization "
                f"through opposing houses {d_houses_str}. Delays or partial denial are likely."
            )
        elif "UNFAVORABLE" in verdict:
            explanation = (
                f"Both the source conditions and the final outcome are challenging for {topic_label}. "
                f"The significations point toward houses associated with obstacles ({d_houses_str}), "
                f"suggesting this area faces inherent difficulties."
            )
        else:
            explanation = (
                f"The indicators for {topic_label} are mixed. "
                f"Neither strong support nor clear opposition is present in the current configuration."
            )

        technical = (
            f"CSL={planet_name} | "
            f"Promise(L2)={list(sorted(promise_houses))} → score {promise_score} | "
            f"Deliver(L3)={list(sorted(deliver_houses))} → score {deliver_score} | "
            f"Combined={combined:.1f} | "
            f"Positive houses={list(sorted(positive_houses))} | "
            f"Negative houses={list(sorted(negative_houses))}"
        )

        return {
            "planet": planet_name,
            "promise_houses": sorted(promise_houses),
            "deliver_houses": sorted(deliver_houses),
            "promise_score": promise_score,
            "deliver_score": deliver_score,
            # pyre-ignore[6]
            "combined_score": round(float(combined), 2),
            "verdict": verdict,
            "explanation": explanation,
            "technical_details": technical
        }

    def calculate_tension(self, positive_houses: Set[int], negative_houses: Set[int], activated_houses: Set[int]) -> float:
        """
        🔱 UAKP CONFLICT DETECTION (V7.0)
        Calculates the 'Tension Index' (0-1.0) between contradictory house sets.
        A high tension index indicates that reality could branch into either state.
        """
        pos_signal = len(activated_houses & positive_houses)
        neg_signal = len(activated_houses & negative_houses)
        
        if pos_signal == 0 or neg_signal == 0:
            return 0.0
            
        # Tension is highest when signals are equal and strong
        total_signal = pos_signal + neg_signal
        balance = 1.0 - abs(pos_signal - neg_signal) / total_signal
        
        # Scale by total signal strength (more houses = more certainty of conflict)
        intensity = min(1.0, total_signal / 4.0)
        
        return balance * intensity

