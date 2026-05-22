import re
from typing import Dict, List, Tuple, Any, Optional, Set
from datetime import datetime

# Import Divine Intelligence Components
try:
    from titanium_ai import (
        DivineDrishtiEngine, ChartDecomposer, SevenLayerAnalyzer,
        ConflictResolver, DivineScorer, PatternDetector
    )
    DIVINE_INTELLIGENCE_AVAILABLE = True
except ImportError:
    DIVINE_INTELLIGENCE_AVAILABLE = False


class UAKPRules:
    """
    🔱 Ultra-Advanced KP (UAKP) Universal Decision Engine
    
    DIVINE INTELLIGENCE UPGRADE:
    - Integrated with DivineDrishtiEngine for 7-layer analysis
    - Chart decomposition for atomic signification
    - Conflict resolution for contradictory indicators
    - Pattern detection for yoga recognition
    - Divine scoring for weighted confidence (0-100)
    """

    # Event Configuration (aligned with DivineDrishtiEngine)
    EVENT_CONFIG = {
        "marriage": {"cusp": 7, "promise": {2, 7, 11}, "denial": {1, 6, 10, 12}},
        "divorce": {"cusp": 7, "promise": {1, 6, 8, 12}, "denial": {2, 7, 11}},
        "child": {"cusp": 5, "promise": {2, 5, 11}, "denial": {1, 4, 10, 12}},
        "death": {"cusp": 8, "promise": {2, 7, 8, 12}, "denial": {5, 9, 11}},
        "job": {"cusp": 10, "promise": {2, 6, 10, 11}, "denial": {5, 8, 12}},
        "wealth": {"cusp": 2, "promise": {2, 6, 10, 11}, "denial": {5, 8, 12}},
        "hospital": {"cusp": 12, "promise": {6, 8, 12}, "denial": {5, 9, 11}},
        "court": {"cusp": 6, "promise": {6, 8, 12}, "denial": {5, 9, 11}},
        "vehicle": {"cusp": 4, "promise": {4, 11}, "denial": {3, 5, 9, 12}},
        "property": {"cusp": 4, "promise": {4, 11, 12}, "denial": {3, 5, 9}}
    }

    def __init__(self, chart_data: Dict):
        self.data = chart_data
        self.planet_sigs = {p['planet']: p for p in self.data.get('planet_significators', [])}
        self.cusps = {c['cusp']: c for c in self.data.get('house_cusps', [])}
        self.planets_data = {p['planet']: p for p in self.data.get('planetary_positions', [])}
        self.dob = self._parse_date(self.data.get('metadata', {}).get('dob', ''))
        
        # Initialize Divine Intelligence Components
        self.divine_engine = None
        self.decomposer = None
        self.analyzer = None
        self.resolver = None
        self.scorer = None
        self.pattern_detector = None
        
        if DIVINE_INTELLIGENCE_AVAILABLE:
            self._init_divine_components()

    def _init_divine_components(self):
        """Initialize all divine intelligence components."""
        try:
            self.divine_engine = DivineDrishtiEngine(self.data)
            self.decomposer = ChartDecomposer(self.data)
            self.analyzer = SevenLayerAnalyzer(self.data, self.decomposer)
            self.resolver = ConflictResolver(self.data, self.decomposer)
            self.scorer = DivineScorer()
            self.pattern_detector = PatternDetector(self.data, self.decomposer)
        except Exception as e:
            print(f"Warning: Divine components initialization failed: {e}")

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str: return None
        try:
            return datetime.strptime(date_str.split()[0], "%d-%m-%Y")
        except:
            return None

    def _calculate_age(self, target_date: datetime) -> float:
        if not self.dob: return 0.0
        delta = target_date - self.dob
        return delta.days / 365.25

    # =========================================================================
    # STEP 0: LIFE SPAN GATE (Pre-Event Validation)
    # =========================================================================
    def step0_life_span_gate(self, event_date: datetime, event_type: str = "general") -> Dict:
        """
        🔒 LIFE SPAN GATE: Silently check if event is possible within life span.
        
        This is a pre-filter for all event modules. If the event date falls
        beyond the predicted death window, the event possibility is marked LOW.
        
        Returns:
            {"passed": True/False, "reason": "...", "max_age": int}
        """
        if not self.dob or not event_date:
            return {"passed": True, "reason": "No DOB/Date to validate", "max_age": 120}
        
        # Import LifeSpanEngine dynamically to avoid circular imports
        try:
            import sys
            import os
            # Ensure the prediction/event path is in sys.path
            event_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prediction', 'event')
            if event_path not in sys.path:
                sys.path.insert(0, event_path)
            
            from life_span import LifeSpanEngine, LongevityCategory
            
            # Create a silent life span engine
            engine = LifeSpanEngine(self.data)
            
            # Run Gate 1 to get category
            engine.gate_1_structural_permit()
            category = engine.determine_category()
            
            # Determine max age based on category
            if category == LongevityCategory.ALPAYU:
                max_age = 33
            elif category == LongevityCategory.MADHYAYU:
                max_age = 66
            else:  # PURNAYU
                max_age = 100
            
            # Calculate event age
            event_age = self._calculate_age(event_date)
            
            # Check if event is beyond life span
            if event_age > max_age:
                return {
                    "passed": False,
                    "reason": f"Event at age {event_age:.1f} exceeds {category.value[2]} limit ({max_age} yrs)",
                    "max_age": max_age,
                    "category": category.value[2]
                }
            else:
                return {
                    "passed": True,
                    "reason": f"Event at age {event_age:.1f} within {category.value[2]} window",
                    "max_age": max_age,
                    "category": category.value[2]
                }
                
        except Exception as e:
            # If life span engine fails, allow event to proceed
            return {"passed": True, "reason": f"Life Span check skipped: {e}", "max_age": 120}

    def _get_source_row(self, planet: Optional[str]) -> List[int]:
        if not planet: return []
        row = self.planet_sigs.get(planet, {}).get('Source_Row', '')
        return [int(h) for h in re.findall(r'\d+', str(row))]

    def _get_result_row(self, planet: Optional[str]) -> List[int]:
        if not planet: return []
        row = self.planet_sigs.get(planet, {}).get('Result_Row', '')
        return [int(h) for h in re.findall(r'\d+', str(row))]

    def _get_planet_houses(self, planet: str, row_type: str = "both") -> Set[int]:
        """Get houses signified by a planet using decomposer if available."""
        if self.decomposer:
            return self.decomposer.get_planet_houses(planet, row_type)
        
        # Fallback to basic extraction
        result = set(self._get_result_row(planet))
        source = set(self._get_source_row(planet))
        
        if row_type == "result":
            return result
        elif row_type == "source":
            return source
        return result | source

    # =========================================================================
    # STEP 1: Birth Ruling Planet Audit
    # =========================================================================
    def step1_rp_scan(self, current_rps: List[str]) -> Dict:
        birth_rps = self.data.get('birth_ruling_planets', [])
        agreement = [p for p in birth_rps if p in current_rps]
        return {
            "Birth_RP": birth_rps,
            "Agreement_Count": len(agreement),
            "Status": "Strong" if len(agreement) >= 3 else "Moderate"
        }

    # =========================================================================
    # STEP 2: Longevity & Vitality Check (Enhanced with Divine Intelligence)
    # =========================================================================
    def step2_longevity_scan(self) -> Dict:
        """Enhanced longevity scan with divine intelligence."""
        dangerous_houses = [1, 3, 8]
        score = 0
        killers = {2, 7}
        exit_houses = {8, 12}
        life_givers = {1, 5, 9, 11}
        
        details = []
        
        for h in dangerous_houses:
            csl_name = self.cusps.get(h, {}).get('sub_lord')
            if not csl_name: continue
            
            res = set(self._get_result_row(csl_name))
            
            has_maraka = bool(res.intersection(killers))
            has_exit = bool(res.intersection(exit_houses))
            has_shield = bool(res.intersection(life_givers))
            
            if (has_maraka and has_exit) and not has_shield:
                score += 1
                details.append(f"House {h} CSL {csl_name} shows Maraka+Exit without Shield")
        
        # Determine category
        if score >= 2:
            category = "ALPAYU"
            age_range = (0, 33)
            risk = "HIGH"
        elif score == 1:
            category = "MADHYAYU"  
            age_range = (33, 66)
            risk = "MODERATE"
        else:
            category = "PURNAYU"
            age_range = (67, 120)
            risk = "LOW"
        
        # Get Maraka patterns if divine intelligence available
        maraka_patterns = []
        if self.pattern_detector:
            patterns = self.pattern_detector.detect_maraka_pattern()
            maraka_patterns = patterns
        
        return {
            "category": category,
            "age_range": age_range,
            "risk_level": risk,
            "details": details,
            "maraka_patterns": maraka_patterns,
            "legacy_verdict": f"{category} ({'High Risk' if risk == 'HIGH' else 'Medium' if risk == 'MODERATE' else 'Long Life'})"
        }

    # =========================================================================
    # STEP 3: Fortuna Point Mapping
    # =========================================================================
    def step3_fortuna_map(self) -> Dict:
        fortuna = self.data.get('fortuna_point', {})
        return {
            "Fortuna_Lord": fortuna.get('lord'),
            "Active_House": fortuna.get('house'),
            "Blessing": f"Sudden positive results through house {fortuna.get('house')}."
        }

    # =========================================================================
    # STEP 4: CSL Audit (Enhanced with 7-Layer Analysis)
    # =========================================================================
    def step4_csl_audit(self, target_house: int, success_houses: List[int], event_type: str = "general") -> Dict:
        """
        Enhanced CSL Audit with 7-layer divine analysis.
        """
        csl = self.cusps.get(target_house, {}).get('sub_lord')
        source = self._get_source_row(csl)
        result = self._get_result_row(csl)
        
        # Basic Promise/Delivery check
        has_promise = any(h in success_houses for h in source)
        has_delivery = any(h in success_houses for h in result)
        
        # Determine Consequence
        verdict = "Denied"
        quality = "None"
        
        if has_promise and has_delivery:
            verdict = "Confirmed"
            quality = "Stable & Strong (Rooted)"
        elif has_promise and not has_delivery:
            verdict = "Frustrated"
            quality = "Hopes Raised, Delivery Failed (Obstacle)"
        elif not has_promise and has_delivery:
            verdict = "Accidental"
            quality = "Unstable/Temporary (Windfall without Root)"
        else:
            verdict = "Denied"
            quality = "No Potential"

        result_dict = {
            "Target_CSL": csl,
            "Source_Promise": has_promise,
            "Result_Capability": has_delivery,
            "Verdict": verdict,
            "Quality": quality
        }
        
        # Enhanced: Add divine intelligence analysis if available
        if self.divine_engine and event_type in self.EVENT_CONFIG:
            try:
                promise_analysis = self.divine_engine.analyze_event_promise(event_type)
                result_dict["divine_analysis"] = {
                    "verdict": promise_analysis.get("verdict"),
                    "confidence": promise_analysis.get("confidence"),
                    "csl_houses": promise_analysis.get("csl_houses"),
                    "patterns_detected": promise_analysis.get("patterns", {}).get("net_effect")
                }
            except Exception:
                pass
        
        return result_dict

    # =========================================================================
    # STEP 5: Power Percentage (Enhanced with Divine Scoring)
    # =========================================================================
    def step5_power_percentage(self, planet: str, positive_houses: List[int]) -> Dict:
        """
        Enhanced power calculation with divine scoring integration.
        """
        src = self._get_source_row(planet)
        res = self._get_result_row(planet)
        
        # Source Score
        src_pos = len([h for h in src if h in positive_houses])
        src_neg = len([h for h in src if h in [8, 12]])
        src_total = max(1, src_pos + src_neg)
        src_power = (src_pos / src_total) * 100

        # Result Score
        res_pos = len([h for h in res if h in positive_houses])
        res_neg = len([h for h in res if h in [8, 12]])
        res_total = max(1, res_pos + res_neg)
        res_power = (res_pos / res_total) * 100
        
        # Weighted Average (Result matters more for final output)
        final_power = (src_power * 0.4) + (res_power * 0.6)
        
        # Get dignity score if resolver available
        dignity_score = 5  # Default
        if self.resolver:
            try:
                dignity_score = self.resolver.get_planet_dignity_score(planet)
            except:
                pass
        
        # Adjust power based on dignity
        dignity_multiplier = 1.0 + (dignity_score - 5) * 0.05
        adjusted_power = min(100, final_power * dignity_multiplier)
        
        return {
            "raw_power": round(final_power, 2),
            "adjusted_power": round(adjusted_power, 2),
            "source_power": round(src_power, 2),
            "result_power": round(res_power, 2),
            "dignity_score": dignity_score,
            "confidence_level": self._get_confidence_level(adjusted_power)
        }

    def _get_confidence_level(self, power: float) -> str:
        """Convert power to confidence level."""
        if power >= 80:
            return "DIVINE CERTAINTY"
        elif power >= 65:
            return "HIGH CONFIDENCE"
        elif power >= 50:
            return "MODERATE CONFIDENCE"
        elif power >= 35:
            return "LOW CONFIDENCE"
        else:
            return "WEAK INDICATION"

    # =========================================================================
    # STEP 6: Quantity Determination
    # =========================================================================
    def step6_quantity_check(self, target_house: int) -> str:
        csl_data = self.cusps.get(target_house, {})
        sign_type = csl_data.get('sign_type') 
        planet = csl_data.get('sub_lord')
        
        if sign_type == 'Dual' or planet == 'Mercury':
            return "Multiple/Plural (Multiple)"
        return "Single (Single)"

    # =========================================================================
    # STEP 7: Aspect Audit
    # =========================================================================
    def step7_aspect_audit(self, target_planet: str) -> List[str]:
        aspects = self.data.get('aspect_table', [])
        impacts = []
        for asp in aspects:
            if asp.get('to') == target_planet:
                nature = "Benefic" if asp.get('from') in ['Jupiter', 'Venus'] else "Malefic"
                impacts.append(f"{nature} aspect from {asp.get('from')}")
        return impacts

    # =========================================================================
    # STEP 8: Timing Engine (Enhanced with Age & Divine Validation)
    # =========================================================================
    def step8_timing_engine(self, dasha_planets: List[str], transit_planets: List[str], 
                           event_type: str = "General", event_date: datetime = None) -> Dict:
        """Enhanced timing validation with age check and divine analysis."""
        
        result = {
            "status": "PENDING",
            "age_check": None,
            "rp_check": None,
            "divine_check": None,
            "verdict": ""
        }
        
        # Age validation
        if event_date and self.dob:
            age = self._calculate_age(event_date)
            
            age_limits = {
                "Marriage": (18, 60),
                "Job": (18, 70),
                "Child": (18, 50),
                "Death": (0, 120),
                "Divorce": (18, 70)
            }
            
            min_age, max_age = age_limits.get(event_type, (0, 120))
            
            if age < min_age or age > max_age:
                result["age_check"] = f"FAILED: Age {age:.1f} outside range ({min_age}-{max_age})"
                result["status"] = "DENIED"
                result["verdict"] = f"Denied: Age {age:.1f} is outside valid window."
                return result
            else:
                result["age_check"] = f"PASSED: Age {age:.1f} within range ({min_age}-{max_age})"

        # RP Agreement check
        birth_rps = self.data.get('birth_ruling_planets', [])
        common = set(dasha_planets) & set(transit_planets) & set(birth_rps)
        
        if common:
            result["rp_check"] = f"STRONG: RP agreement with {list(common)}"
        else:
            result["rp_check"] = "WEAK: No RP agreement"
        
        # Divine analysis check (if available)
        if self.divine_engine and event_date:
            try:
                event_type_lower = event_type.lower()
                if event_type_lower in self.EVENT_CONFIG and len(dasha_planets) >= 3:
                    md, ad, pd = dasha_planets[0], dasha_planets[1], dasha_planets[2]
                    divine_result = self.divine_engine.divine_analysis(
                        event_type_lower, md, ad, pd, event_date
                    )
                    result["divine_check"] = {
                        "score": divine_result.get("divine_score"),
                        "confidence": divine_result.get("confidence_level"),
                        "layers_passed": divine_result.get("layer_analysis", {}).get("passed_layers")
                    }
            except Exception:
                pass
        
        # Final verdict
        if common:
            result["status"] = "CONFIRMED"
            result["verdict"] = f"Strong timing for event under influence of: {', '.join(common)}."
        else:
            result["status"] = "WAITING"
            result["verdict"] = "Time not yet ripe (Waiting for Transit Trigger)."
        
        return result

    # =========================================================================
    # STEP 9: Divine 7-Layer Analysis (NEW)
    # =========================================================================
    def step9_divine_analysis(self, event_type: str, md: str, ad: str, pd: str, 
                              event_date: datetime) -> Dict:
        """
        Full 7-layer divine analysis using DivineDrishtiEngine.
        """
        if not self.divine_engine:
            return {"error": "Divine Intelligence not available", "status": "UNAVAILABLE"}
        
        try:
            result = self.divine_engine.divine_analysis(event_type, md, ad, pd, event_date)
            return result
        except Exception as e:
            return {"error": str(e), "status": "FAILED"}

    # =========================================================================
    # STEP 10: Pattern Recognition (NEW)
    # =========================================================================
    def step10_pattern_scan(self, event_type: str = "general") -> Dict:
        """
        Detect yogas and special patterns relevant to the event.
        """
        if not self.pattern_detector:
            return {"status": "UNAVAILABLE", "patterns": []}
        
        try:
            patterns = self.pattern_detector.get_all_patterns(event_type)
            return {
                "status": "SUCCESS",
                "positive_yogas": patterns.get("positive_yogas", []),
                "negative_patterns": patterns.get("negative_patterns", []),
                "net_effect": patterns.get("net_effect", "NEUTRAL")
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    # =========================================================================
    # STEP 11: Conflict Resolution (NEW)
    # =========================================================================
    def step11_conflict_resolution(self, md: str, ad: str, pd: str, 
                                   event_type: str = "general") -> Dict:
        """
        Resolve contradictory indicators in the chart.
        """
        if not self.resolver:
            return {"status": "UNAVAILABLE"}
        
        config = self.EVENT_CONFIG.get(event_type, {"cusp": 7, "promise": {2, 7, 11}, "denial": {6, 8, 12}})
        
        try:
            report = self.resolver.generate_conflict_report(
                md, ad, pd, 
                config["promise"], 
                config["denial"], 
                config["cusp"]
            )
            return report
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    # =========================================================================
    # STEP 12: Quick Verdict (NEW)
    # =========================================================================
    def step12_quick_verdict(self, event_type: str, md: str, ad: str, pd: str) -> Tuple[bool, str]:
        """
        Quick verdict for filtering without full analysis.
        """
        if not self.divine_engine:
            # Fallback to basic check
            config = self.EVENT_CONFIG.get(event_type, {"promise": {2, 7, 11}})
            promise_houses = config["promise"]
            
            md_houses = self._get_planet_houses(md, "result")
            ad_houses = self._get_planet_houses(ad, "result")
            pd_houses = self._get_planet_houses(pd, "result")
            
            match_count = sum([
                bool(md_houses & promise_houses),
                bool(ad_houses & promise_houses),
                bool(pd_houses & promise_houses)
            ])
            
            if match_count >= 2:
                return True, "LIKELY"
            elif match_count == 1:
                return True, "POSSIBLE"
            else:
                return False, "UNLIKELY"
        
        return self.divine_engine.quick_verdict(event_type, md, ad, pd)

    # =========================================================================
    # LEGACY: Job Change Rules (Enhanced)
    # =========================================================================
    def apply_job_change_rules(self) -> Dict:
        """Enhanced job change analysis with divine intelligence."""
        audit = self.step4_csl_audit(10, [2, 6, 10, 11], "job")
        power = self.step5_power_percentage(str(audit['Target_CSL']), [2, 6, 10, 11])
        patterns = self.step10_pattern_scan("job")
        
        # Build comprehensive result
        result = {
            "csl_audit": audit,
            "power_analysis": power,
            "patterns": patterns,
            "verdict": "",
            "divine_score": None
        }
        
        # Add divine analysis if available
        if audit.get("divine_analysis"):
            result["divine_score"] = audit["divine_analysis"].get("confidence")
        
        # Generate verdict
        if audit['Verdict'] == "Confirmed":
            result["verdict"] = f"UAKP VERDICT: Confirmed ({power['adjusted_power']}% Power) - {audit['Quality']}"
        elif audit['Verdict'] == "Accidental":
            result["verdict"] = f"UAKP VERDICT: Unstable ({power['adjusted_power']}% Power) - {audit['Quality']}"
        elif audit['Verdict'] == "Frustrated":
            result["verdict"] = "UAKP VERDICT: Blocked - Promise exists but Delivery Fails."
        else:
            result["verdict"] = "UAKP VERDICT: Denied."
        
        return result

    # =========================================================================
    # DIVINE MASTER ANALYSIS (NEW - Primary Entry Point)
    # =========================================================================
    def divine_master_analysis(self, event_type: str, md: str, ad: str, pd: str,
                               event_date: datetime = None) -> Dict:
        """
        🔱 DIVINE MASTER ANALYSIS - Complete prediction analysis.
        
        This is the primary entry point for comprehensive prediction.
        Combines all steps into a single unified analysis.
        """
        result = {
            "event_type": event_type,
            "dasha": f"{md}-{ad}-{pd}",
            "event_date": event_date.strftime("%d-%m-%Y") if event_date else None,
            "steps": {},
            "divine_score": None,
            "final_verdict": "",
            "confidence_level": ""
        }
        
        # Get event config
        config = self.EVENT_CONFIG.get(event_type, {"cusp": 7, "promise": {2, 7, 11}, "denial": {6, 8, 12}})
        
        # Step 4: CSL Audit
        result["steps"]["csl_audit"] = self.step4_csl_audit(config["cusp"], list(config["promise"]), event_type)
        
        # Step 5: Power Percentage
        csl = result["steps"]["csl_audit"].get("Target_CSL")
        if csl:
            result["steps"]["power"] = self.step5_power_percentage(csl, list(config["promise"]))
        
        # Step 10: Pattern Scan
        result["steps"]["patterns"] = self.step10_pattern_scan(event_type)
        
        # Step 11: Conflict Resolution
        result["steps"]["conflicts"] = self.step11_conflict_resolution(md, ad, pd, event_type)
        
        # Step 9: Divine 7-Layer Analysis
        if event_date:
            result["steps"]["divine_analysis"] = self.step9_divine_analysis(event_type, md, ad, pd, event_date)
            
            if "divine_score" in result["steps"]["divine_analysis"]:
                result["divine_score"] = result["steps"]["divine_analysis"]["divine_score"]
                result["confidence_level"] = result["steps"]["divine_analysis"].get("confidence_level", "")
                result["final_verdict"] = result["steps"]["divine_analysis"].get("final_verdict", "")
        else:
            # Quick verdict without date
            is_likely, verdict = self.step12_quick_verdict(event_type, md, ad, pd)
            result["final_verdict"] = verdict
        
        return result
