import os
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
import math
from src.calculations import KPCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLEngine")

# Try importing Scikit-Learn (Graceful Fallback)
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import joblib
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("Scikit-learn not found. ML features will be disabled. Run 'pip install scikit-learn'")

class AstrologyMLEngine:
    """
    🔮 HYBRID AI ENGINE (Experimental)
    ==================================
    Integrates Machine Learning probabilities with Vedic Astrology Rules.
    
    Architecture:
    1. Feature Extractor: Converts Chart Data -> Numerical Vector
    2. Model Manager: Loads/Saves RandomForest Models (.pkl)
    3. Hybrid Predictor: Combines DivineDrishti Score + ML Probability
    """
    
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        if not os.path.exists(self.MODEL_DIR):
            os.makedirs(self.MODEL_DIR, exist_ok=True)
        self.kp = KPCalculator()
            
    def load_model(self, event_type: str):
        """Load a specific event model (e.g., 'marriage', 'job_loss')"""
        if not HAS_SKLEARN: return False
        
        model_path = os.path.join(self.MODEL_DIR, f"{event_type}_rf.pkl")
        scaler_path = os.path.join(self.MODEL_DIR, f"{event_type}_scaler.pkl")
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.models[event_type] = joblib.load(model_path)
                self.scalers[event_type] = joblib.load(scaler_path)
                logger.info(f"Loaded ML model for: {event_type}")
                return True
            except Exception as e:
                logger.error(f"Failed to load model {event_type}: {e}")
                return False
        return False

    # =========================================================================
    # 🕵️ DATA COLLECTION ENGINE (The First 'Hard Step')
    # =========================================================================
    def collect_training_data(self, chart_data: Dict, event_type: str, label: int):
        """
        Saves a verified case to 'training_data.csv'.
        label: 1 (Event Happened) or 0 (Event Denied)
        """
        data_file = os.path.join(self.MODEL_DIR, f"training_data_{event_type}.csv")
        
        # 1. Extract Features (The Vector)
        if event_type == "marriage":
            features = self.extract_features_marriage(chart_data)
        elif event_type == "death":
            features = self.extract_features_death(chart_data)
        elif event_type == "divorce":
            features = self.extract_features_divorce(chart_data)
        elif event_type == "widowhood":
            features = self.extract_features_widowhood(chart_data)
        elif event_type == "child_birth":
            features = self.extract_features_child_birth(chart_data)
        elif event_type == "job_start":
            features = self.extract_features_job_start(chart_data)
        elif event_type == "job_loss":
            features = self.extract_features_job_loss(chart_data)
        else:
            return False
            
        # 2. Add Label to Vector
        features.append(label)
        
        # 3. Save to CSV
        try:
            # Create header if file doesn't exist
            if not os.path.exists(data_file):
                # Placeholder headers - in production, these should be named properly
                headers = [f"f{i}" for i in range(len(features)-1)] + ["target"]
                with open(data_file, "w") as f:
                    f.write(",".join(headers) + "\n")
            
            # Append Row
            row_str = ",".join(map(str, features))
            with open(data_file, "a") as f:
                f.write(row_str + "\n")
            
            logger.info(f"Saved training data point for {event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to save training data: {e}")
            return False

    # =========================================================================
    # 🧮 REAL FEATURE EXTRACTION (No More Placeholders)
    # =========================================================================
    def _get_cyclic_features(self, angle_deg: float) -> List[float]:
        """Convert angle to [sin, cos] vector"""
        rad = math.radians(angle_deg)
        return [math.sin(rad), math.cos(rad)]

    def extract_features_marriage(self, chart_data: Dict) -> List[float]:
        """
        Converts a Birth Chart into a Normalized Vector for Random Forest.
        Uses Cyclic Encoding (Sin/Cos) for all angular features.
        """
        features = []
        
        try:
            # Helpers for safe extraction
            cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
            planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
            
            # --- Feature Group 1: The 7th House (Primary) ---
            # Rational: Strength of the 7th Cusp Sub-Lord determines the 'Promise'
            csl_7_name = cusps.get(7, {}).get('sub_lord', 'Saturn') # Default fallback
            csl_7_id = self._planet_to_int(csl_7_name)
            features.append(csl_7_id / 9.0) # Normalized Planet ID (0.0 - 1.0)
            
            # --- Feature Group 2: The Dasha Lords (Timing) ---
            # Current MD/AD/PD identities from the chart metadata or user selection
            md_name = chart_data.get('current_dasha', {}).get('md', 'Saturn')
            ad_name = chart_data.get('current_dasha', {}).get('ad', 'Saturn')
            features.append(self._planet_to_int(md_name) / 9.0)
            features.append(self._planet_to_int(ad_name) / 9.0)
            
            # --- Feature Group 3: Aspect Scores (Shadbala-lite) ---
            # Check if Mars or Saturn aspects 7th House (Malefic Influence)
            h7_lon = cusps.get(7, {}).get('longitude', 180.0)
            sat_lon = planets.get('Saturn', {}).get('full_degree', 0.0)
            mar_lon = planets.get('Mars', {}).get('full_degree', 0.0)
            
            features.append(self._calculate_aspect_strength(sat_lon, h7_lon)) # Saturn drishti
            features.append(self._calculate_aspect_strength(mar_lon, h7_lon)) # Mars drishti
            
            # --- Feature Group 4: Jupiter (The Karaka) - CYCLIC NORMALIZATION ---
            jup_lon = planets.get('Jupiter', {}).get('full_degree', 0.0)
            features.extend(self._get_cyclic_features(jup_lon)) # [Sin, Cos]
            features.append(1.0 if planets.get('Jupiter', {}).get('is_retro', False) else 0.0)
            
            # --- Feature Group 5: 2nd and 11th House (Network) ---
            # Are 2nd and 11th lords friends with 7th lord?
            l2 = self._planet_to_int(cusps.get(2, {}).get('sign_lord', 'Venus'))
            l7 = self._planet_to_int(cusps.get(7, {}).get('sign_lord', 'Mars'))
            l11 = self._planet_to_int(cusps.get(11, {}).get('sign_lord', 'Saturn'))
            
            features.append(abs(l2 - l7) / 9.0) 
            features.append(abs(l11 - l7) / 9.0)
            
            # --- NEW: TRANSIT FEATURES (MD/AD/PD/Sun/RPs) - CYCLIC NORMALIZATION ---
            transits = chart_data.get('transit_positions', {})
            birth_rps = chart_data.get('birth_rps', {})
            dasha = chart_data.get('current_dasha', {})
            
            # 6. Sun Transit
            features.extend(self._get_cyclic_features(transits.get('Sun', 0.0)))
            
            # 7. Dasha Lord Transits
            pd_name = dasha.get('pd', 'Saturn')
            features.extend(self._get_cyclic_features(transits.get(md_name, 0.0)))
            features.extend(self._get_cyclic_features(transits.get(ad_name, 0.0)))
            features.extend(self._get_cyclic_features(transits.get(pd_name, 0.0)))
            
            # 8. Ruling Planet Transits (Birth RPs in Transit)
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('asc_sign_lord', 'Mars'), 0.0)))
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('asc_star_lord', 'Mars'), 0.0)))
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('moon_sign_lord', 'Moon'), 0.0)))
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('moon_star_lord', 'Moon'), 0.0)))

            # --- NEW: SYNASTRY (DUAL-CHART) FEATURES ---
            # Requires 'spouse_planets' in chart_data (Planetary Positions of Spouse)
            spouse_planets = {p['planet']: p['full_degree'] for p in chart_data.get('spouse_planets', [])}
            
            if spouse_planets:
                # 9. Spouse Moon (Mind) - Cyclic
                s_moon = spouse_planets.get('Moon', 0.0)
                features.extend(self._get_cyclic_features(s_moon))
                
                # 10. Spouse Venus (Love) - Cyclic
                s_venus = spouse_planets.get('Venus', 0.0)
                features.extend(self._get_cyclic_features(s_venus))
                
                # 11. Synastry Interactions (Aspects - already distance based)
                p_sun = planets.get('Sun', {}).get('full_degree', 0.0)
                features.append(self._calculate_aspect_strength(p_sun, s_moon))
                
                # 12. 7th Lord (Person) vs Venus (Spouse) - Karmic Promise
                l7_name = cusps.get(7, {}).get('sign_lord', 'Venus')
                p_l7_pos = planets.get(l7_name, {}).get('full_degree', 0.0)
                features.append(self._calculate_aspect_strength(p_l7_pos, s_venus))
            else:
                # Pad features if no spouse data
                # 2 vectors (4 features) + 2 comparisons (2 features) = 6 features
                features.extend([0.0] * 6)

            # Pad to 60 features (Safe buffer)
            while len(features) < 60:
                features.append(0.0)
                
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            features = [0.0] * 60
            
        return features[:60]

    def _get_badhaka_house(self, asc_sign: str) -> int:
        """
        Returns the Badhaka (Obstacle) House based on Ascendant Sign.
        Movable (1,4,7,10) -> 11th
        Fixed (2,5,8,11) -> 9th
        Dual (3,6,9,12) -> 7th
        """
        movable = ["Aries", "Cancer", "Libra", "Capricorn"]
        fixed = ["Taurus", "Leo", "Scorpio", "Aquarius"]
        # Dual = ["Gemini", "Virgo", "Sagittarius", "Pisces"]
        
        if asc_sign in movable: return 11
        if asc_sign in fixed: return 9
        return 7 # Default to Dual rule if unknown

    def extract_features_death(self, chart_data: Dict) -> List[float]:
        """
        Features for Death Prediction (Timing & Longevity).
        Includes Cyclic Normalization for Angular Features.
        V2.0: Includes Gate Verdicts (1, 2, 4, 6).
        """
        features = []
        try:
            cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
            planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
            
            # 1. Longevity Determinants (8th House)
            csl_8 = cusps.get(8, {}).get('sub_lord', '') # No default
            features.append(self._planet_to_int(csl_8) / 9.0)
            
            # 2. Maraka Houses (2nd & 7th)
            csl_2 = cusps.get(2, {}).get('sub_lord', '')
            csl_7 = cusps.get(7, {}).get('sub_lord', '')
            features.append(self._planet_to_int(csl_2) / 9.0)
            features.append(self._planet_to_int(csl_7) / 9.0)
            
            # 3. Badhaka House (Dynamic)
            asc_sign = cusps.get(1, {}).get('sign', 'Aries')
            badhaka_house = self._get_badhaka_house(asc_sign)
            csl_badhaka = cusps.get(badhaka_house, {}).get('sub_lord', '') 
            features.append(self._planet_to_int(csl_badhaka) / 9.0)

            # 4. Running Dasha at Event Time
            dasha = chart_data.get('current_dasha', {})
            md = dasha.get('md', '')
            ad = dasha.get('ad', '')
            pd_lord = dasha.get('pd', '')
            
            features.append(self._planet_to_int(md) / 9.0)
            features.append(self._planet_to_int(ad) / 9.0)
            features.append(self._planet_to_int(pd_lord) / 9.0)
            
            # 5. Age Factor (Normalized)
            age = chart_data.get('analysis_age', 60.0) 
            features.append(min(age / 100.0, 1.0))
            
            # 6. Saturn & Jupiter (Natural Karakas) - CYCLIC
            sat_lon = planets.get('Saturn', {}).get('full_degree', 0.0)
            jup_lon = planets.get('Jupiter', {}).get('full_degree', 0.0)
            features.extend(self._get_cyclic_features(sat_lon))
            features.extend(self._get_cyclic_features(jup_lon))
            
            # 7. 8th House Occupants / Aspect
            h8_lon = cusps.get(8, {}).get('longitude', 240.0)
            features.append(self._calculate_aspect_strength(sat_lon, h8_lon))
            
            # --- NEW: TRANSIT FEATURES - CYCLIC ---
            transits = chart_data.get('transit_positions', {})
            birth_rps = chart_data.get('birth_rps', {})
            
            # 8. Sun Transit
            features.extend(self._get_cyclic_features(transits.get('Sun', 0.0)))
            
            # 9. Dasha Lord Transits
            md_name = dasha.get('md', 'Saturn')
            ad_name = dasha.get('ad', 'Saturn')
            pd_name = dasha.get('pd', 'Saturn')
            
            features.extend(self._get_cyclic_features(transits.get(md_name, 0.0)))
            features.extend(self._get_cyclic_features(transits.get(ad_name, 0.0)))
            features.extend(self._get_cyclic_features(transits.get(pd_name, 0.0)))
            
            # 10. Ruling Planet Transits
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('asc_sign_lord', 'Mars'), 0.0)))
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('asc_star_lord', 'Mars'), 0.0)))
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('moon_sign_lord', 'Moon'), 0.0)))
            features.extend(self._get_cyclic_features(transits.get(birth_rps.get('moon_star_lord', 'Moon'), 0.0)))
            
            # --- V2.0: GATE VERDICTS (Hybrid AI Bridge) ---
            # 1.0 = PASS (Danger), 0.0 = FAIL (Safe)
            gates = chart_data.get('gate_data', {})
            features.append(1.0 if gates.get('gate_1_status') else 0.0) 
            features.append(1.0 if gates.get('gate_2_status') else 0.0) 
            features.append(1.0 if gates.get('gate_4_status') else 0.0) 
            features.append(1.0 if gates.get('gate_6_status') else 0.0) 

            # V3.9: Saturn Protector (Feature 66)
            # 1.0 = PROTECTED, 0.0 = NORMAL
            features.append(1.0 if gates.get('gate_saturn_protector') else 0.0)

            # V4.0: Alpayu/Purnayu Yogas (Features 67-69)
            features.append(1.0 if gates.get('gate_alpayu_11') else 0.0)
            features.append(1.0 if gates.get('gate_danger_8_csl') else 0.0)
            features.append(1.0 if gates.get('gate_purnayu_sat') else 0.0)

            # Pad to 70 features (Buffer)
            while len(features) < 70:
                features.append(0.0)
                
        except Exception as e:
            logger.error(f"Death Feat Extract Error: {e}")
            features = [0.0] * 70
            
        return features[:70]

    def extract_features_divorce(self, chart_data: Dict) -> List[float]:
        """
        Features for Divorce/Separation Prediction.
        Focus: 6th (Legal), 8th (Break), 12th (Separation).
        """
        features = []
        try:
            cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
            planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
            
            # 1. 7th House (Relationship) & 6th House (Legal/Conflict)
            csl_7 = cusps.get(7, {}).get('sub_lord', 'Saturn')
            csl_6 = cusps.get(6, {}).get('sub_lord', 'Mars')
            features.append(self._planet_to_int(csl_7) / 9.0)
            features.append(self._planet_to_int(csl_6) / 9.0)
            
            # 2. 8th House (Break in ties) & 12th House (Separation)
            csl_8 = cusps.get(8, {}).get('sub_lord', 'Rahu')
            csl_12 = cusps.get(12, {}).get('sub_lord', 'Ketu')
            features.append(self._planet_to_int(csl_8) / 9.0)
            features.append(self._planet_to_int(csl_12) / 9.0)
            
            # 3. Dasha Lords
            dasha = chart_data.get('current_dasha', {})
            md = dasha.get('md', 'Saturn')
            ad = dasha.get('ad', 'Saturn')
            features.append(self._planet_to_int(md) / 9.0)
            features.append(self._planet_to_int(ad) / 9.0)
            
            # 4. Planetary Positions (Saturn/Mars/Rahu impact)
            sat_lon = planets.get('Saturn', {}).get('full_degree', 0.0)
            rah_lon = planets.get('Rahu', {}).get('full_degree', 0.0)
            h7_lon = cusps.get(7, {}).get('longitude', 180.0)
            
            # Aspect on 7th
            features.append(self._calculate_aspect_strength(sat_lon, h7_lon))
            features.append(self._calculate_aspect_strength(rah_lon, h7_lon))
            
            # 5. Transits
            transits = chart_data.get('transit_positions', {})
            features.extend(self._get_cyclic_features(transits.get('Sun', 0.0)))
            features.extend(self._get_cyclic_features(transits.get(md, 0.0)))
            features.extend(self._get_cyclic_features(transits.get(ad, 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Saturn', 0.0))) # Saturn Transit crucial
            features.extend(self._get_cyclic_features(transits.get('Jupiter', 0.0))) # Jupiter Transit (protection?)

            # Pad to 60
            while len(features) < 60: features.append(0.0)
            
        except Exception as e:
            logger.error(f"Divorce Feat Extract Error: {e}")
            features = [0.0] * 60
        return features[:60]

    def extract_features_widowhood(self, chart_data: Dict) -> List[float]:
        """
        Features for Widowhood (Spouse Death).
        Focus: Maraka houses for Spouse (Native's 1st and 8th).
        """
        features = []
        try:
            cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
            planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
            
            # 1. Spouse's Maraka Houses (Native H1 & H8)
            csl_1 = cusps.get(1, {}).get('sub_lord', 'Mars')
            csl_8 = cusps.get(8, {}).get('sub_lord', 'Saturn')
            features.append(self._planet_to_int(csl_1) / 9.0)
            features.append(self._planet_to_int(csl_8) / 9.0)
            
            # 2. Spouse's Longevity (Native H2 - 8th from 7th)
            csl_2 = cusps.get(2, {}).get('sub_lord', 'Venus')
            features.append(self._planet_to_int(csl_2) / 9.0)

            # 3. Dasha Lords
            dasha = chart_data.get('current_dasha', {})
            md = dasha.get('md', 'Saturn')
            ad = dasha.get('ad', 'Saturn')
            features.append(self._planet_to_int(md) / 9.0)
            features.append(self._planet_to_int(ad) / 9.0)
            
            # 4. Transits (Saturn over H1 or H8 often triggers)
            transits = chart_data.get('transit_positions', {})
            features.extend(self._get_cyclic_features(transits.get('Sun', 0.0)))
            features.extend(self._get_cyclic_features(transits.get(md, 0.0)))
            features.extend(self._get_cyclic_features(transits.get(ad, 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Saturn', 0.0)))
            
            # Pad to 60
            while len(features) < 60: features.append(0.0)

        except Exception as e:
            logger.error(f"Widowhood Feat Extract Error: {e}")
            features = [0.0] * 60
        return features[:60]

    def extract_features_child_birth(self, chart_data: Dict) -> List[float]:
        """
        Features for Child Birth Prediction.
        Focus: 5th House (Children), 2nd (Family Expansion), 11th (Gains).
        """
        features = []
        try:
            cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
            planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
            
            # 1. 5th House (Primary - Progeny)
            csl_5 = cusps.get(5, {}).get('sub_lord', 'Jupiter')
            features.append(self._planet_to_int(csl_5) / 9.0)
            
            # 2. 2nd House (Family) & 11th House (Fulfillment)
            csl_2 = cusps.get(2, {}).get('sub_lord', 'Venus')
            csl_11 = cusps.get(11, {}).get('sub_lord', 'Saturn')
            features.append(self._planet_to_int(csl_2) / 9.0)
            features.append(self._planet_to_int(csl_11) / 9.0)
            
            # 3. Jupiter (Karaka of Children, Putra Karaka)
            jup_lon = planets.get('Jupiter', {}).get('full_degree', 0.0)
            features.extend(self._get_cyclic_features(jup_lon))
            features.append(1.0 if planets.get('Jupiter', {}).get('is_retro', False) else 0.0)
            
            # 4. Dasha Lords
            dasha = chart_data.get('current_dasha', {})
            md = dasha.get('md', 'Saturn')
            ad = dasha.get('ad', 'Saturn')
            pd = dasha.get('pd', 'Saturn')
            features.append(self._planet_to_int(md) / 9.0)
            features.append(self._planet_to_int(ad) / 9.0)
            features.append(self._planet_to_int(pd) / 9.0)
            
            # 5. 5th Lord Position & Aspect
            l5_name = cusps.get(5, {}).get('sign_lord', 'Sun')
            l5_lon = planets.get(l5_name, {}).get('full_degree', 0.0)
            features.extend(self._get_cyclic_features(l5_lon))
            
            # 6. Transits
            transits = chart_data.get('transit_positions', {})
            features.extend(self._get_cyclic_features(transits.get('Sun', 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Jupiter', 0.0)))
            features.extend(self._get_cyclic_features(transits.get(md, 0.0)))
            features.extend(self._get_cyclic_features(transits.get(ad, 0.0)))
            
            # Pad to 60
            while len(features) < 60: features.append(0.0)
            
        except Exception as e:
            logger.error(f"Child Birth Feat Extract Error: {e}")
            features = [0.0] * 60
        return features[:60]

    def _planet_to_int(self, name: str) -> int:
        """Maps planet name to integer 0-8"""
        mapping = {"Ket": 0, "Ven": 1, "Sun": 2, "Mon": 3, "Mar": 4, 
                   "Rah": 5, "Jup": 6, "Sat": 7, "Mer": 8}
        # Handle full names
        name_map = {"Ketu": "Ket", "Venus": "Ven", "Sun": "Sun", "Moon": "Mon", 
                   "Mars": "Mar", "Rahu": "Rah", "Jupiter": "Jup", "Saturn": "Sat", "Mercury": "Mer"}
        short = name_map.get(name, name)
        return mapping.get(short, 4) # Default to 4 (Mars/Middle) if unknown

    def _calculate_aspect_strength(self, planet_lon: float, target_lon: float) -> float:
        """
        Calculates the strength of aspect (Trine/Square/Opposition).
        Returns a value between 0.0 (No Aspect) and 1.0 (Exact Aspect).
        Features Normalized Distance logic.
        """
        diff = abs(planet_lon - target_lon) % 360.0
        dist = min(diff, 360.0 - diff)
        
        # Define Aspect Orbs (Wide for Marriage Promise)
        # Conjunction (0), Opposition (180), Trine (120), Square (90)
        aspects = [0, 180, 120, 90]
        orb = 10.0 # Wide orb for promise
        
        score = 0.0
        for asp in aspects:
            d = abs(dist - asp)
            if d <= orb:
                # Linear decay: 1.0 at exact, 0.0 at orb limit
                s = (orb - d) / orb
                score = max(score, s)
                
        return score

    def predict_probability(self, event_type: str, chart_data: Dict) -> float:
        """
        Get the ML Probability Score (0% to 100%)
        Returns -1.0 if model not available.
        """
        if not HAS_SKLEARN: return -1.0
        
        if event_type not in self.models:
            if not self.load_model(event_type):
                return -1.0
                
        # 1. Extract Features
        if event_type == "marriage":
            feature_vector = self.extract_features_marriage(chart_data)
        elif event_type == "death":
            feature_vector = self.extract_features_death(chart_data)
        elif event_type == "divorce":
            feature_vector = self.extract_features_divorce(chart_data)
        elif event_type == "widowhood":
            feature_vector = self.extract_features_widowhood(chart_data)
        elif event_type == "child_birth":
            feature_vector = self.extract_features_child_birth(chart_data)
        elif event_type == "job_start":
            feature_vector = self.extract_features_job_start(chart_data)
        elif event_type == "job_loss":
            feature_vector = self.extract_features_job_loss(chart_data)
        else:
            return -1.0
            
        # 2. Scale Features
        try:
            X = np.array([feature_vector])
            # If feature size changed (40 -> 60), scaler will fail. 
            # We assume model is retrained if feature count changed.
            # But during dev, we might have mismatch.
            try:
                X_scaled = self.scalers[event_type].transform(X)
            except ValueError:
                logger.warning("Feature size mismatch. Model needs retraining.")
                return -1.0
            
            # 3. Predict Class Probabilities
            # [Probability_No, Probability_Yes]
            probs = self.models[event_type].predict_proba(X_scaled)
            success_prob = probs[0][1] * 100 # Convert to percentage
            
            return round(success_prob, 2)
            
        except Exception as e:
            logger.error(f"Prediction Error: {e}")
            return -1.0

    def train_model_from_csv(self, event_type: str):
        """
        🚀 THE REAL TRAINING ENGINE
        Reads 'training_data_{event_type}.csv' and builds a real Brain.
        """
        if not HAS_SKLEARN:
            logger.error("Cannot train: Scikit-learn missing.")
            return False

        csv_path = os.path.join(self.MODEL_DIR, f"training_data_{event_type}.csv")
        if not os.path.exists(csv_path):
            logger.error(f"Data file not found: {csv_path}")
            return False

        try:
            import pandas as pd
            logger.info(f"Loading data from {csv_path}...")
            
            # 1. Load Data
            df = pd.read_csv(csv_path)
            if len(df) < 20:
                logger.warning(f"Not enough data to learn ({len(df)} rows). Need at least 20.")
                return False

            # 2. Split Features (X) and Target (y)
            X = df.iloc[:, :-1].values # All cols except last
            y = df.iloc[:, -1].values  # Last col is label (0/1)

            # 3. Preprocessing
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # 4. Train Random Forest (The Brain)
            # n_estimators=100 (100 Decision Trees voting)
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_scaled, y)

            # 5. Save the Brain
            joblib.dump(clf, os.path.join(self.MODEL_DIR, f"{event_type}_rf.pkl"))
            joblib.dump(scaler, os.path.join(self.MODEL_DIR, f"{event_type}_scaler.pkl"))
            
            logger.info(f"✅ SUCCESS: Trained new model on {len(df)} charts at {datetime.now()}")
            return True

        except Exception as e:
            logger.error(f"Training Failed: {e}")
            return False



    def extract_features_job_start(self, chart_data: Dict) -> List[float]:
        """
        Features for Job/Career Start Prediction.
        Focus: 2nd (Wealth), 6th (Service), 10th (Career), 11th (Gains).
        """
        features = []
        try:
            cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
            planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
            
            # 1. 10th House (Primary - Career/Status)
            csl_10 = cusps.get(10, {}).get('sub_lord', 'Saturn')
            features.append(self._planet_to_int(csl_10) / 9.0)
            
            # 2. 2nd House (Wealth) & 6th House (Service) & 11th (Gains)
            csl_2 = cusps.get(2, {}).get('sub_lord', 'Venus')
            csl_6 = cusps.get(6, {}).get('sub_lord', 'Mars')
            csl_11 = cusps.get(11, {}).get('sub_lord', 'Jupiter')
            features.append(self._planet_to_int(csl_2) / 9.0)
            features.append(self._planet_to_int(csl_6) / 9.0)
            features.append(self._planet_to_int(csl_11) / 9.0)
            
            # 3. Saturn (Karaka of Profession)
            sat_lon = planets.get('Saturn', {}).get('full_degree', 0.0)
            features.extend(self._get_cyclic_features(sat_lon))
            
            # 4. Sun (Karaka of Authority/Govt)
            sun_lon = planets.get('Sun', {}).get('full_degree', 0.0)
            features.extend(self._get_cyclic_features(sun_lon))
            
            # 5. Dasha Lords
            dasha = chart_data.get('current_dasha', {})
            md = dasha.get('md', 'Saturn')
            ad = dasha.get('ad', 'Saturn')
            pd = dasha.get('pd', 'Saturn')
            features.append(self._planet_to_int(md) / 9.0)
            features.append(self._planet_to_int(ad) / 9.0)
            features.append(self._planet_to_int(pd) / 9.0)
            
            # 6. Transits for Job Start
            transits = chart_data.get('transit_positions', {})
            features.extend(self._get_cyclic_features(transits.get('Sun', 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Saturn', 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Jupiter', 0.0))) # Jupiter triggers events
            
            # 7. DASHAMSHA (D10) FEATURES - The Career Chart
            # We calculate D10 signs for key planets
            d10_chart = self.kp.calculate_dashamsha({p['planet']: p['full_degree'] for p in chart_data.get('planetary_positions', [])})
            
            # Feature: D10 Sign of 10th Lord (Status)
            l10_d10_sign = d10_chart.get(csl_10, "Aries")
            features.extend(self._get_cyclic_features(self.kp.ZODIAC.index(l10_d10_sign) * 30.0))
            
            # Feature: D10 Sign of Saturn (Profession Karaka)
            sat_d10_sign = d10_chart.get('Saturn', "Aries")
            features.extend(self._get_cyclic_features(self.kp.ZODIAC.index(sat_d10_sign) * 30.0))

            # Pad to 60
            while len(features) < 60: features.append(0.0)
            
        except Exception as e:
            logger.error(f"Job Start Feat Extract Error: {e}")
            features = [0.0] * 60
        return features[:60]

    def extract_features_job_loss(self, chart_data: Dict) -> List[float]:
        """
        Features for Job Loss/Termination Prediction.
        Focus: 5th (12th from 6th), 9th (12th from 10th), 8th (Change/Break), 12th (Loss).
        """
        features = []
        try:
            cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
            planets = {p['planet']: p for p in chart_data.get('planetary_positions', [])}
            
            # 1. Detrimental Houses (5, 9, 8, 12)
            csl_5 = cusps.get(5, {}).get('sub_lord', 'Sun')
            csl_9 = cusps.get(9, {}).get('sub_lord', 'Jupiter')
            csl_8 = cusps.get(8, {}).get('sub_lord', 'Rahu')
            csl_12 = cusps.get(12, {}).get('sub_lord', 'Ketu')
            
            features.append(self._planet_to_int(csl_5) / 9.0)
            features.append(self._planet_to_int(csl_9) / 9.0)
            features.append(self._planet_to_int(csl_8) / 9.0)
            features.append(self._planet_to_int(csl_12) / 9.0)
            
            # 2. 10th House (The Career itself being attacked)
            csl_10 = cusps.get(10, {}).get('sub_lord', 'Saturn')
            features.append(self._planet_to_int(csl_10) / 9.0)
            
            # 3. Dasha Lords
            dasha = chart_data.get('current_dasha', {})
            md = dasha.get('md', 'Saturn')
            ad = dasha.get('ad', 'Saturn')
            pd = dasha.get('pd', 'Saturn')
            features.append(self._planet_to_int(md) / 9.0)
            features.append(self._planet_to_int(ad) / 9.0)
            features.append(self._planet_to_int(pd) / 9.0)
            
            # 4. Transits for Job Loss
            transits = chart_data.get('transit_positions', {})
            # Saturn (Taskmaster), Nodes (Disruption), Mars (Severance)
            features.extend(self._get_cyclic_features(transits.get('Saturn', 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Rahu', 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Ketu', 0.0)))
            features.extend(self._get_cyclic_features(transits.get('Mars', 0.0)))
            
            # 5. DASHAMSHA (D10) FEATURES
            d10_chart = self.kp.calculate_dashamsha({p['planet']: p['full_degree'] for p in chart_data.get('planetary_positions', [])})
            
            # Feature: D10 Sign of 10th Lord (Career Stability)
            l10_name = cusps.get(10, {}).get('sub_lord', 'Saturn') # D1 Sub Lord
            l10_d10_sign = d10_chart.get(l10_name, "Aries")
            features.extend(self._get_cyclic_features(self.kp.ZODIAC.index(l10_d10_sign) * 30.0))
            
            # Feature: D10 Sign of 8th Lord (Breaks/Changes)
            l8_name = cusps.get(8, {}).get('sub_lord', 'Saturn')
            l8_d10_sign = d10_chart.get(l8_name, "Aries")
            features.extend(self._get_cyclic_features(self.kp.ZODIAC.index(l8_d10_sign) * 30.0))

            # Pad to 60
            while len(features) < 60: features.append(0.0)
            
        except Exception as e:
            logger.error(f"Job Loss Feat Extract Error: {e}")
            features = [0.0] * 60
        return features[:60]

# Singleton Instance
ml_engine = AstrologyMLEngine()
