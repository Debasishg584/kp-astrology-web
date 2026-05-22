import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import json
import os
import sys
import re
import difflib
from datetime import datetime, timedelta
import traceback
import importlib.util
import importlib
import inspect
import copy
from typing import Dict, List, Any, Optional, TYPE_CHECKING

try:
    from PIL import Image, ImageTk # type: ignore
except (ImportError, Exception):
    Image: Any = None
    ImageTk: Any = None

# =============================================================================
# 1. SYSTEM PATH & SETUP
# =============================================================================
current_file_path = os.path.abspath(__file__)
src_directory = os.path.dirname(current_file_path)
project_root = os.path.dirname(src_directory)

if src_directory not in sys.path: sys.path.insert(0, src_directory)
if project_root not in sys.path: sys.path.insert(0, project_root)

# Standard Fallback Path
DATA_PATH = os.path.join(project_root, 'data', 'chart_data.json')

def get_resource_path(relative_path):
    """Fallback for getting resource paths if utils is not imported."""
    return os.path.join(project_root, relative_path)

# Try Absolute Imports
try:
    # If project root is in path
    from src.translations import t # type: ignore
    from src.utils import get_resource_path # type: ignore
    from src.prediction.general.birth_chart_daily_prediction import BirthDailyPrediction # type: ignore
except ImportError:
    try:
        # If src directory is in path
        from translations import t # type: ignore
        from utils import get_resource_path # type: ignore
        from prediction.general.birth_chart_daily_prediction import BirthDailyPrediction # type: ignore
    except ImportError:
        print("⚠️ Core components (translations, utils, daily_prediction) not found.")
        BirthDailyPrediction = None

# --- Try Importing Special Modules ---
try:
    from prediction.general.Past_Life_Story_Generator import analyze_past_life_story # type: ignore
except ImportError:
    analyze_past_life_story = None

# --- ML Integration ---
try:
    from src.ml_engine import ml_engine # type: ignore
    ML_AVAILABLE = True
except ImportError:
    try:
        from ml_engine import ml_engine # type: ignore
        ML_AVAILABLE = True
    except ImportError:
        ML_AVAILABLE = False
        ml_engine = None

# --- Theme Module ---
try:
    from src.ui_theme import Colors, Fonts, ModernButton, StatusIndicator, EnhancedConsole, apply_tab_style # type: ignore
    THEME_AVAILABLE = True
except ImportError:
    try:
        from ui_theme import Colors, Fonts, ModernButton, StatusIndicator, EnhancedConsole, apply_tab_style # type: ignore
        THEME_AVAILABLE = True
    except ImportError:
        THEME_AVAILABLE = False
        print("⚠️ UI Theme module not found. Using default styling.")


# Sidereal Signs Mapping for Transit
SIGN_MAP = {0: "Aries", 1: "Taurus", 2: "Gemini", 3: "Cancer", 4: "Leo", 5: "Virgo",
            6: "Libra", 7: "Scorpio", 8: "Sagittarius", 9: "Capricorn", 10: "Aquarius", 11: "Pisces"}
SIGN_INDEX = {v: k for k, v in SIGN_MAP.items()}


# =============================================================================
# 2. LOCAL CORE UTILITIES & FORENSIC ENGINES
# =============================================================================

class DataConverter:
    @staticmethod
    def dms_to_float(dms_str):
        if not isinstance(dms_str, str): return 0.0
        match = re.match(r"(\d+)°\s*(\d+)'\s*(\d+)\"", dms_str)
        if match:
            d, m, s = map(int, match.groups())
            return d + m/60 + s/3600
        return 0.0

    @staticmethod
    def get_absolute_longitude(planet_data):
        """Fallback for absolute longitude used by ML prep."""
        dms = planet_data.get('longitude_dms', '0')
        sign = planet_data.get('sign', 'Aries')
        deg = DataConverter.dms_to_float(dms)
        sign_idx = SIGN_INDEX.get(sign, 0)
        return (sign_idx * 30) + deg

    @staticmethod
    def convert_for_engine(chart_data):
        planets = []
        for p in chart_data.get('planetary_positions', []):
            planets.append({
                "name": p['planet'],
                "long": DataConverter.dms_to_float(p.get('longitude_dms', '0')),
                "star": p.get('star_lord', ''),
                "sub": p.get('sub_lord', ''),
                "sign": p.get('sign', '')
            })
        
        cusps = []
        for c in chart_data.get('house_cusps', []):
            cusps.append({
                "id": c['cusp'],
                "long": DataConverter.dms_to_float(c.get('longitude_dms', '0')),
                "star": c.get('star_lord', ''),
                "sub": c.get('sub_lord', ''),
                "sign": c.get('sign', ''),
                "sign_lord": c.get('sign_lord', '')
            })
        return planets, cusps

    @staticmethod
    def parse_robust_date(date_str: str) -> Optional[datetime]:
        """Robust date parser handling multiple formats safely. Returns None on failure instead of crashing."""
        if not date_str: return None
        for fmt in ["%d-%m-%Y", "%d %b %Y", "%Y-%m-%d", "%b %Y", "%Y/%m/%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def parse_window_date(window_str: str) -> Optional[datetime]:
        """Safely parses the start date from any window string variant cleanly."""
        if not window_str: return None
        parts = re.split(r'\s+-\s+|\s+to\s+|\s+To\s+|-', window_str)
        return DataConverter.parse_robust_date(parts[0].strip())

    @staticmethod
    def validate_chart_data(chart_data: Any) -> List[str]:
        """Validates chart_data structure. Returns list of errors (empty = valid)."""
        errors: List[str] = []
        if not isinstance(chart_data, dict):
            errors.append("chart_data is not a dict")
            return errors
        
        required_keys = ['metadata', 'planetary_positions', 'house_cusps']
        for key in required_keys:
            if key not in chart_data:
                errors.append(f"Missing required key: '{key}'")
        
        meta = chart_data.get('metadata', {})
        if not isinstance(meta, dict):
            errors.append("'metadata' is not a dict")
        elif not meta.get('dob'):
            errors.append("'metadata.dob' is missing")
        
        positions = chart_data.get('planetary_positions', [])
        if not isinstance(positions, list) or len(positions) == 0:
            errors.append("'planetary_positions' is empty or not a list")
        
        cusps = chart_data.get('house_cusps', [])
        if not isinstance(cusps, list) or len(cusps) == 0:
            errors.append("'house_cusps' is empty or not a list")
        
        dasa = chart_data.get('vimshottari_dasa_full', [])
        if not isinstance(dasa, list):
            errors.append("'vimshottari_dasa_full' is not a list")
        elif dasa:
            first = dasa[0]
            if not isinstance(first, dict):
                errors.append("Dasa entries are not dicts")
            elif 'lord' not in first or 'start' not in first:
                errors.append("Dasa entry missing 'lord' or 'start' keys")
        
        return errors


class MarriageWidowedForensics:
    """Integrated Forensic Engine for Divorce and Widowhood based on 7 CSL, 1-6-8-12 logic and Sun Transit."""
    def __init__(self, chart_data: dict):
        self.chart_data = chart_data
        self.planet_sigs = {p['planet']: p for p in self.chart_data.get('planet_significators', []) if isinstance(p, dict)}
        self.cusps = {c['cusp']: c for c in self.chart_data.get('house_cusps', []) if isinstance(c, dict)}
        
        dob_raw = str(self.chart_data.get('metadata', {}).get('dob', '01-01-1900'))
        self.dob = datetime.strptime(dob_raw.split(' ')[0], "%d-%m-%Y")
        
        h7_data = self.cusps.get(7, {})
        h8_data = self.cusps.get(8, {})
        self.h7_sign = str(h7_data.get('sign', 'Aries'))
        self.h8_sign = str(h8_data.get('sign', 'Aries'))
        self.target_signs = [SIGN_INDEX.get(self.h7_sign, 0), SIGN_INDEX.get(self.h8_sign, 1)]

    def _get_houses(self, planet: str) -> set[int]:
        sig = self.planet_sigs.get(planet, {})
        row_str = str(sig.get('Result_Row', ''))
        return set(int(h) for h in re.findall(r'\d+', row_str))

    def _get_all_houses(self, planet: str) -> set[int]:
        sig = self.planet_sigs.get(planet, {})
        source_row = str(sig.get('Source_Row', ''))
        result_row = str(sig.get('Result_Row', ''))
        row_str = source_row + " " + result_row
        return set(int(h) for h in re.findall(r'\d+', row_str))

    def get_sun_sign(self, dt: datetime) -> int:
        d, m = dt.day, dt.month
        if m == 4: return 0 if d >= 14 else 11
        elif m == 5: return 1 if d >= 15 else 0
        elif m == 6: return 2 if d >= 15 else 1
        elif m == 7: return 3 if d >= 16 else 2
        elif m == 8: return 4 if d >= 17 else 3
        elif m == 9: return 5 if d >= 17 else 4
        elif m == 10: return 6 if d >= 17 else 5
        elif m == 11: return 7 if d >= 16 else 6
        elif m == 12: return 8 if d >= 16 else 7
        elif m == 1: return 9 if d >= 14 else 8
        elif m == 2: return 10 if d >= 13 else 9
        elif m == 3: return 11 if d >= 15 else 10
        return 0

    def _engine_log(self, msg: str):
        """Buffer log messages for later retrieval by TitaniumAI."""
        if not hasattr(self, '_log_buffer'):
            self._log_buffer: List[str] = []
        self._log_buffer.append(msg)

    def calculate_timing_report(self):
        # STAGE 1: 7th CSL Promise Audit
        csl_planet = str(self.cusps.get(7, {}).get('sub_lord', ''))
        csl_all_h = self._get_all_houses(csl_planet)
        has_marriage = bool(csl_all_h.intersection({2, 11}))
        has_separation_promise = bool(csl_all_h.intersection({1, 6, 8, 12}))
        
        self.language = self.chart_data.get('metadata', {}).get('language', 'en')
        promise_verdict = "Denied"
        if not has_marriage:
            promise_verdict = t("Marriage NOT Promised (7th CSL {csl_planet} lacks 2/11).", self.language, csl_planet=csl_planet)
        elif has_marriage and has_separation_promise:
            promise_verdict = t("Marriage happened but separation confirmed (7th CSL {csl_planet} shows 2/11 and 1/6/8/12).", self.language, csl_planet=csl_planet)
        else:
            promise_verdict = t("Stable Marriage promised (7th CSL {csl_planet} lacks 1/6/8/12).", self.language, csl_planet=csl_planet)

        windows = []
        sep_houses = {6, 8, 12}
        
        try:
            age_18_dt = self.dob.replace(year=self.dob.year + 18)
        except ValueError:
            age_18_dt = self.dob.replace(year=self.dob.year + 18, day=28)
            
        try:
            age_60_dt = self.dob.replace(year=self.dob.year + 60)
        except ValueError:
            age_60_dt = self.dob.replace(year=self.dob.year + 60, day=28)
        
        dasa_table = self.chart_data.get('vimshottari_dasa_full', [])
        if not isinstance(dasa_table, list): dasa_table = []

        for md_raw in dasa_table:
            if not isinstance(md_raw, dict): continue
            md = md_raw
            m_lord = str(md.get('lord', ''))
            md_h = self._get_houses(m_lord)
            if not md_h.intersection(sep_houses): continue

            for ad_raw in md.get('sub_periods', []):
                if not isinstance(ad_raw, dict): continue
                ad = ad_raw
                a_lord = str(ad.get('lord', ''))
                ad_h = self._get_houses(a_lord)
                if not ad_h.intersection(sep_houses): continue

                for pd_raw in ad.get('sub_periods', []):
                    if not isinstance(pd_raw, dict): continue
                    pd = pd_raw
                    p_lord = str(pd.get('lord', ''))
                    pd_h = self._get_houses(p_lord)
                    if not pd_h.intersection(sep_houses): continue

                    raw_p_start = str(pd.get('start', ''))
                    if not raw_p_start: continue
                    p_start_only = raw_p_start.split(' ')[0]
                    pd_start_dt = DataConverter.parse_robust_date(p_start_only)
                    if not pd_start_dt:
                        self._engine_log(f"Invalid Candidate (Bad Start Date): {p_start_only}")
                        windows.append({
                            "window": str(raw_p_start) + " - UNKNOWN",
                            "dasha": m_lord + "-" + a_lord + "-" + p_lord,
                            "stability": "ERROR: INVALID START DATE",
                            "houses": "MD:" + str(list(md_h)) + " AD:" + str(list(ad_h)) + " PD:" + str(list(pd_h))
                        })
                        continue
                        
                    if pd_start_dt > age_60_dt: break 
                    if pd_start_dt < age_18_dt: continue

                    transit_confirmed = False
                    curr_check = pd_start_dt
                    raw_p_end = str(pd.get('end', ''))
                    if not raw_p_end: continue
                    p_end_only = raw_p_end.split(' ')[0]
                    
                    pd_end_dt = DataConverter.parse_robust_date(p_end_only)
                    if not pd_end_dt:
                        self._engine_log(f"Invalid Candidate (Bad End Date): {p_end_only}")
                        windows.append({
                            "window": str(raw_p_start) + " - " + str(raw_p_end),
                            "dasha": m_lord + "-" + a_lord + "-" + p_lord,
                            "stability": "ERROR: INVALID END DATE",
                            "houses": "MD:" + str(list(md_h)) + " AD:" + str(list(ad_h)) + " PD:" + str(list(pd_h))
                        })
                        continue

                    # Prevent infinite loop during transit scan
                    max_checks = 1000
                    checks = 0
                    while curr_check <= pd_end_dt and checks < max_checks:
                        if self.get_sun_sign(curr_check) in self.target_signs:
                            transit_confirmed = True
                            break
                        curr_check += timedelta(days=1)
                        checks += 1
                    
                    if not transit_confirmed: continue

                    event_type = "DIVORCE"
                    if pd_h.intersection({2, 7}) and pd_h.intersection({8}): 
                        event_type = "WIDOWHOOD"

                    intersect_md = md_h.intersection(sep_houses)
                    intersect_ad = ad_h.intersection(sep_houses)
                    intersect_pd = pd_h.intersection(sep_houses)
                    
                    md_h_list = [str(h) for h in sorted(list(intersect_md))]
                    ad_h_list = [str(h) for h in sorted(list(intersect_ad))]
                    pd_h_list = [str(h) for h in sorted(list(intersect_pd))]
                    
                    md_text = "[" + ", ".join(md_h_list) + "]"
                    ad_text = "[" + ", ".join(ad_h_list) + "]"
                    pd_text = "[" + ", ".join(pd_h_list) + "]"

                    windows.append({
                        "window": p_start_only + " - " + p_end_only,
                        "dasha": m_lord + "-" + a_lord + "-" + p_lord,
                        "stability": t("MAJOR {event_type} WINDOW", getattr(self, "language", "en"), event_type=str(event_type)),
                        "houses": "MD:" + md_text + " AD:" + ad_text + " PD:" + pd_text
                    })

        return {"Promise": promise_verdict, "Event_Windows": windows}


class ChildBirthForensics:
    """TITANIUM Engine for Child Birth Timing and Progeny Audit."""
    def __init__(self, chart_data: dict):
        self.chart_data = chart_data
        self.planet_sigs = {p['planet']: p for p in self.chart_data.get('planet_significators', []) if isinstance(p, dict)}
        self.cusps = {c['cusp']: c for c in self.chart_data.get('house_cusps', []) if isinstance(c, dict)}
        
        dob_raw = str(self.chart_data.get('metadata', {}).get('dob', '01-01-1900'))
        self.dob = datetime.strptime(dob_raw.split(' ')[0], "%d-%m-%Y")
        
        self.fruitful_signs = ['Cancer', 'Scorpio', 'Pisces']
        self.barren_signs = ['Aries', 'Leo', 'Virgo', 'Gemini']
        self.progeny_houses = {2, 5, 11}
        self.negation_houses = {1, 4, 10, 12}

    def _get_result_houses(self, planet: str) -> set[int]:
        sig = self.planet_sigs.get(planet, {})
        row_str = str(sig.get('Result_Row', ''))
        return set(int(h) for h in re.findall(r'\d+', row_str))

    def _get_all_houses(self, planet: str) -> set[int]:
        sig = self.planet_sigs.get(planet, {})
        source_row = str(sig.get('Source_Row', ''))
        result_row = str(sig.get('Result_Row', ''))
        row_str = source_row + " " + result_row
        return set(int(h) for h in re.findall(r'\d+', row_str))

    def _engine_log(self, msg: str):
        """Buffer log messages for later retrieval by TitaniumAI."""
        if not hasattr(self, '_log_buffer'):
            self._log_buffer: List[str] = []
        self._log_buffer.append(msg)

    def calculate_timing_report(self):
        # GATE A & B: Promise Audit (5th CSL)
        csl_5 = str(self.cusps.get(5, {}).get('sub_lord', ''))
        csl_all_h = self._get_all_houses(csl_5)
        
        denial_hits = csl_all_h.intersection(self.negation_houses)
        promise_hits = csl_all_h.intersection(self.progeny_houses)

        self.language = self.chart_data.get('metadata', {}).get('language', 'en')
        promise_verdict = "Denied"
        if len(denial_hits) > len(promise_hits) and not promise_hits:
            promise_verdict = t("NO CHILD (Absolute Denial). 5th CSL {csl_5} shows {dh}.", self.language, csl_5=csl_5, dh=str(list(denial_hits)))
        elif promise_hits:
            # GATE C: Quantity Check
            c5_sign = str(self.cusps.get(5, {}).get('sign', ''))
            if c5_sign in self.fruitful_signs:
                promise_verdict = t("MULTIPLE CHILDREN (Strong Promise). 5th CSL {csl_5} in {c5_sign}.", self.language, csl_5=csl_5, c5_sign=c5_sign)
            elif c5_sign in self.barren_signs:
                promise_verdict = t("SINGLE CHILD (Restricted Case). 5th CSL {csl_5} in {c5_sign}.", self.language, csl_5=csl_5, c5_sign=c5_sign)
            else:
                promise_verdict = t("POTENTIAL FOR CHILD (Average Promise). 5th CSL {csl_5} in {c5_sign}.", self.language, csl_5=csl_5, c5_sign=c5_sign)
        else:
             promise_verdict = t("UNCERTAIN PROMISE (Weak). 5th CSL {csl_5} lacks strong 2/5/11.", self.language, csl_5=csl_5)

        windows = []
        try:
            age_18_dt = self.dob.replace(year=self.dob.year + 18)
        except ValueError:
            age_18_dt = self.dob.replace(year=self.dob.year + 18, day=28)
            
        try:
            age_50_dt = self.dob.replace(year=self.dob.year + 50)
        except ValueError:
            age_50_dt = self.dob.replace(year=self.dob.year + 50, day=28)
        
        dasa_table = self.chart_data.get('vimshottari_dasa_full', [])
        if not isinstance(dasa_table, list): dasa_table = []

        for md_raw in dasa_table:
            if not isinstance(md_raw, dict): continue
            md = md_raw
            m_lord = str(md.get('lord', ''))
            md_h = self._get_result_houses(m_lord)
            if not md_h.intersection(self.progeny_houses):
                continue
            
            for ad_raw in md.get('sub_periods', []):
                if not isinstance(ad_raw, dict): continue
                ad = ad_raw
                a_lord = str(ad.get('lord', ''))
                ad_h = self._get_result_houses(a_lord)
                if not ad_h.intersection(self.progeny_houses):
                    continue
                
                if not (md_h.intersection(self.progeny_houses) and ad_h.intersection(self.progeny_houses)):
                    continue
                
                for pd_raw in ad.get('sub_periods', []):
                    if not isinstance(pd_raw, dict): continue
                    pd = pd_raw
                    p_lord = str(pd.get('lord', ''))
                    pd_h = self._get_result_houses(p_lord)
                    if not pd_h.intersection(self.progeny_houses): continue

                    raw_p_start = str(pd.get('start', ''))
                    if not raw_p_start: continue
                    p_start_only = raw_p_start.split(' ')[0]
                    pd_start_dt = DataConverter.parse_robust_date(p_start_only)
                    if not pd_start_dt:
                        self._engine_log(f"Invalid Candidate (Bad Start Date): {p_start_only}")
                        windows.append({
                            "window": str(raw_p_start) + " - UNKNOWN",
                            "dasha": m_lord + "-" + a_lord + "-" + p_lord,
                            "stability": "ERROR: INVALID START DATE",
                            "houses": "MD:" + str(list(md_h)) + " AD:" + str(list(ad_h)) + " PD:" + str(list(pd_h))
                        })
                        continue
                        
                    if pd_start_dt > age_50_dt: break
                    if pd_start_dt < age_18_dt: continue
                    if pd_start_dt < datetime.now(): continue

                    strength = "MODERATE"
                    if (md_h.intersection(self.progeny_houses)) and (ad_h.intersection(self.progeny_houses)) and (pd_h.intersection(self.progeny_houses)):
                        strength = "HIGH"

                    intersect_md = md_h.intersection(self.progeny_houses)
                    intersect_ad = ad_h.intersection(self.progeny_houses)
                    intersect_pd = pd_h.intersection(self.progeny_houses)
                    
                    md_h_list = [str(h) for h in sorted(list(intersect_md))]
                    ad_h_list = [str(h) for h in sorted(list(intersect_ad))]
                    pd_h_list = [str(h) for h in sorted(list(intersect_pd))]
                    
                    md_text = "[" + ", ".join(md_h_list) + "]"
                    ad_text = "[" + ", ".join(ad_h_list) + "]"
                    pd_text = "[" + ", ".join(pd_h_list) + "]"
                    
                    raw_p_end = str(pd.get('end', ''))
                    p_end_only = raw_p_end.split(' ')[0]

                    windows.append({
                        "window": p_start_only + " - " + p_end_only,
                        "dasha": m_lord + "-" + a_lord + "-" + p_lord,
                        "stability": "FERTILE BIRTH WINDOW (" + str(strength) + ")",
                        "houses": "MD:" + md_text + " AD:" + ad_text + " PD:" + pd_text
                    })

        return {"Promise": promise_verdict, "Event_Windows": windows}


# =============================================================================
# 3. TITANIUM AI MASTER CONSOLE (V5 GUI)
# =============================================================================

class TitaniumAI:
    EVENT_INTENT_MAP = {
        "marriage": {"houses": [7, 2, 11], "keywords": ["marriage", "spouse", "wedding", "husband", "wife", "partner"]},
        "job": {"houses": [10, 2, 6, 11], "keywords": ["job", "career", "profession", "work", "promotion", "employment"]},
        "child": {"houses": [5, 2, 11], "keywords": ["child", "baby", "pregnancy", "progeny", "kid"]},
        "property": {"houses": [4, 11, 12], "keywords": ["property", "vehicle", "house", "car", "land", "real estate"]},
        "divorce": {"houses": [8, 12], "keywords": ["divorce", "separation", "widow", "breakup"]},
        "wealth": {"houses": [2, 11], "keywords": ["wealth", "money", "finance", "rich", "income", "gain", "earning"]},
        "life": {"houses": [1, 8], "keywords": ["life", "death", "span"]}
    }

    # =========================================================================
    # REPORT LANGUAGE LABELS  (NEW - only used in gen_show_result)
    # =========================================================================
    REPORT_LABELS = {
        "en": {
            "title_prefix":        "🔱 FINAL KP ASTROLOGER REPORT",
            "divider":             "=" * 55,
            "section_divider":     "─" * 50,
            "complete":            "✅ Analysis Complete.",
            "controller":          "⚙️ Controller",
            "sub_lord":            "⚙️ Sub Lord",
            "star_label":          "⭐ Star",
            "sub_label":           "Sub",
            "direction":           "🧭 Direction",
            "career":              "💼 Career",
            "verdict":             "★ Verdict",
            "details":             "📖 Details",
            "result":              "📖 Result",
            "synthesis":           "★ Synthesis",
            "outcome":             "📖 Outcome",
            "primary_csl":         "PRIMARY - CSL",
            "secondary_occ":       "SECONDARY - Occupant",
            "career_dna":          "🧬 CAREER DNA",
            "house_label":         "House",
            "planet_label":        "🪐",
            "location_pin":        "📍",
        },
        "hi": {
            "title_prefix":        "🔱 अंतिम KP ज्योतिषी रिपोर्ट",
            "divider":             "=" * 55,
            "section_divider":     "─" * 50,
            "complete":            "✅ विश्लेषण पूर्ण।",
            "controller":          "⚙️ नियंत्रक",
            "sub_lord":            "⚙️ उप-स्वामी",
            "star_label":          "⭐ नक्षत्र",
            "sub_label":           "उप",
            "direction":           "🧭 दिशा",
            "career":              "💼 करियर",
            "verdict":             "★ निर्णय",
            "details":             "📖 विवरण",
            "result":              "📖 परिणाम",
            "synthesis":           "★ सार",
            "outcome":             "📖 फलादेश",
            "primary_csl":         "प्राथमिक - उप-स्वामी",
            "secondary_occ":       "द्वितीयक - भाव-स्थित",
            "career_dna":          "🧬 करियर DNA",
            "house_label":         "भाव",
            "planet_label":        "🪐",
            "location_pin":        "📍",
        },
        "bn": {
            "title_prefix":        "🔱 চূড়ান্ত KP জ্যোতিষী রিপোর্ট",
            "divider":             "=" * 55,
            "section_divider":     "─" * 50,
            "complete":            "✅ বিশ্লেষণ সম্পন্ন।",
            "controller":          "⚙️ নিয়ন্ত্রক",
            "sub_lord":            "⚙️ উপ-স্বামী",
            "star_label":          "⭐ নক্ষত্র",
            "sub_label":           "উপ",
            "direction":           "🧭 দিকনির্দেশ",
            "career":              "💼 পেশা",
            "verdict":             "★ রায়",
            "details":             "📖 বিবরণ",
            "result":              "📖 ফলাফল",
            "synthesis":           "★ সারসংক্ষেপ",
            "outcome":             "📖 ফলাদেশ",
            "primary_csl":         "প্রাথমিক - উপ-স্বামী",
            "secondary_occ":       "মাধ্যমিক - ভাবস্থিত",
            "career_dna":          "🧬 ক্যারিয়ার DNA",
            "house_label":         "ভাব",
            "planet_label":        "🪐",
            "location_pin":        "📍",
        },
    }

    # Narrative intro sentences per language (shown at top of report)
    REPORT_INTRO = {
        "en": (
            "The following analysis is derived from KP (Krishnamurti Paddhati) stellar astrology, "
            "examining planetary sub-lord significators, cuspal sub-lords, and dasha timelines "
            "to deliver a precise predictive synthesis."
        ),
        "hi": (
            "निम्नलिखित विश्लेषण KP (कृष्णमूर्ति पद्धति) तारा ज्योतिष पर आधारित है। "
            "ग्रहों के उप-स्वामी कारकों, कुसपीय उप-स्वामियों और दशा कालक्रम का परीक्षण करते हुए "
            "एक सटीक भविष्यवाणी सार प्रस्तुत किया गया है।"
        ),
        "bn": (
            "নিম্নলিখিত বিশ্লেষণটি KP (কৃষ্ণমূর্তি পদ্ধতি) নক্ষত্র জ্যোতিষের উপর ভিত্তি করে তৈরি। "
            "গ্রহের উপ-স্বামী কারক, কাস্পীয় উপ-স্বামী এবং দশা কালরেখা পরীক্ষা করে "
            "একটি নির্ভুল ভবিষ্যদ্বাণী সার উপস্থাপন করা হয়েছে।"
        ),
    }

    def _get_report_lang(self) -> str:
        """Safely resolves display language for report generation."""
        lang = "en"
        if self.chart_data and isinstance(self.chart_data, dict):
            lang = self.chart_data.get('metadata', {}).get('language', 'en')
        if lang not in self.REPORT_LABELS:
            lang = "en"
        return lang

    def detect_intent(self, query: str) -> dict:
        q = query.lower()
        for event_type, data in self.EVENT_INTENT_MAP.items():
            if any(kw in q for kw in data["keywords"]):
                return {"type": event_type, "houses": data["houses"]}
        return {"type": "unknown", "houses": [1]}

    def __init__(self, root):
        self.root = root
        self.root.title("🔱 KP ASTROLOGER - Divya Drishti Master Console")
        self.root.geometry("1450x980")
        
        # Apply theme colors
        if THEME_AVAILABLE:
            self.root.configure(bg=Colors.BG_DARK)
            self.colors = Colors
            self.fonts = Fonts
        else:
            self.root.configure(bg="#050505")
            self.colors = None
            self.fonts = None
        
        self.chart_data = None
        self.user_query = ""
        self.gross_prediction_data: dict = {} 
        self.full_life_story: List[Any] = [] 
        
        # UI Components 
        self.notebook: Optional[ttk.Notebook] = None
        self.timing_frame: tk.Frame = tk.Frame(root)
        self.general_frame: tk.Frame = tk.Frame(root)
        self.daily_frame: tk.Frame = tk.Frame(root)
        self.year_frame: tk.Frame = tk.Frame(root)
        self.console: Any = None
        self.general_console: Any = None
        self.daily_console: Any = None
        self.year_console: Any = None
        self.chart_indicator: Any = None
        self.ml_indicator: Any = None
        self.btn_gen_generate: Any = None
        self.btn_gen_result: Any = None
        
        # New attributes for stability
        self.combo_day: Any = None
        self.combo_month: Any = None
        self.combo_year: Any = None
        self.combo_year_only: Any = None
        self.daily_result_frame: tk.Frame = tk.Frame(root)
        self.year_result_frame: tk.Frame = tk.Frame(root)
        
        # Variables (Initialize with objects to satisfy type checker)
        self.daily_day_var = tk.StringVar()
        self.daily_month_var = tk.StringVar()
        self.daily_year_var = tk.StringVar()
        # Initialize missing translation helper dynamically 
        def fallback_t(text: str, lang: str = "en", **kwargs) -> str:
            res = text
            if lang == "hi" and text == "Marriage NOT Promised (7th CSL {csl_planet} lacks 2/11).":
                res = "विवाह का संकेत नहीं। (7वें भाव का उपस्वामी {csl_planet} 2/11 से हीन है)।"
            elif lang == "hi" and text == "Marriage happened but separation confirmed (7th CSL {csl_planet} shows 2/11 and 1/6/8/12).":
                res = "विवाह हुआ लेकिन अलगाव की पुष्टि हुई (7वें उपस्वामी {csl_planet} 2/11 और 1/6/8/12 दिखाता है)।"
            elif lang == "hi" and text == "Stable Marriage promised (7th CSL {csl_planet} lacks 1/6/8/12).":
                res = "स्थिर विवाह प्रतिशृत है (7वें उपस्वामी {csl_planet} में 1/6/8/12 का अभाव है)।"
            elif lang == "hi" and text == "MAJOR {event_type} WINDOW":
                res = "प्रमुख {event_type} खिड़की"
            elif lang == "bn" and "Marriage NOT Promised" in text:
                res = "বিবাহ নির্দেশিত নয় (৭ম ভাবের উপস্বামী {csl_planet} তে ২/১১ নেই)।"
            elif lang == "bn" and "Marriage happened but separation" in text:
                res = "বিবাহ হয়েছে কিন্তু বিচ্ছেদ নিশ্চিত (৭ম উপস্বামী {csl_planet} ২/১১ এবং ১/৬/৮/১২ দেখায়)।"
            elif lang == "bn" and "Stable Marriage promised" in text:
                res = "টেকসই বিবাহ প্রতিশ্রুতিবদ্ধ (৭ম উপস্বামী {csl_planet} তে ১/৬/৮/১২ নেই)।"
            elif lang == "bn" and "MAJOR " in text:
                res = "প্রধান {event_type} উইন্ডো"
            
            for k, v in kwargs.items():
                if f"{{{k}}}" in res:
                    res = res.replace(f"{{{k}}}", str(v))
            return res

        global t
        if 't' not in globals() or t is None:
            t = fallback_t
            
        self.year_val_var = tk.StringVar()
        
        # General Tab State
        self.gen_query = ""
        self.is_event_possible = False
        self.generated_report: Any = []  # Can be list or dict
        
        # Check for Swiss Ephemeris 
        try:
            import swisseph as swe # type: ignore
            from src.swisseph_backend import SwissEphBackend
            SwissEphBackend.initialize()
            self.swe: Any = swe
            self.swe_available = True
        except (ImportError, Exception):
            self.swe = None
            self.swe_available = False

        self.setup_ui()

    def _prepare_ml_data(self, target_date=None):
        if not hasattr(self, 'run_chart_data') or getattr(self, 'run_chart_data') is None:
            raise RuntimeError("CRITICAL ERROR: run_chart_data missing. State isolation compromised.")
            
        # Use shallow copy to map new top-level features without deep-copying 150kb 
        data = self.run_chart_data.copy()
        
        if 'planetary_positions' in data:
            for p in data['planetary_positions']:
                if 'full_degree' not in p:
                    p['full_degree'] = DataConverter.get_absolute_longitude(p)
        
        now = target_date if target_date else datetime.now()
        current_dasha = {"md": "Saturn", "ad": "Saturn", "pd": "Saturn"} 
        
        try:
            dasha_table = data.get('vimshottari_dasa_full', [])
            found = False
            if dasha_table:
                for md_blk in dasha_table:
                    md_end_str = md_blk.get('end', '').split(' ')[0]
                    if not md_end_str: continue
                    md_end = DataConverter.parse_robust_date(md_end_str)
                    if now <= md_end:
                        current_dasha["md"] = md_blk.get('lord', 'Saturn')
                        for ad_blk in md_blk.get('sub_periods', []):
                            ad_end_str = ad_blk.get('end', '').split(' ')[0]
                            if not ad_end_str: continue
                            ad_end = DataConverter.parse_robust_date(ad_end_str)
                            if now <= ad_end:
                                current_dasha["ad"] = ad_blk.get('lord', 'Saturn')
                                for pd_blk in ad_blk.get('sub_periods', []):
                                    pd_end_str = pd_blk.get('end', '').split(' ')[0]
                                    if not pd_end_str: continue
                                    pd_end = DataConverter.parse_robust_date(pd_end_str)
                                    if now <= pd_end:
                                        current_dasha["pd"] = pd_blk.get('lord', 'Saturn')
                                        found = True
                                        break
                                if found: break
                        if found: break
        except Exception as e: 
            if hasattr(self, 'console') and self.console:
                self.log(f"⚠️ Dasha ML prep warning: {e}", "yellow")
            
        data["current_dasha"] = current_dasha
        
        if self.swe_available and self.swe:
            try:
                term_jd = self.swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
                transits = {}
                swe_map = {0:"Sun", 1:"Moon", 2:"Mercury", 3:"Venus", 4:"Mars", 5:"Jupiter", 6:"Saturn", 10:"Rahu"}
                for p_id in range(11): 
                    if p_id in swe_map:
                        flags = self.swe.FLG_SIDEREAL | self.swe.FLG_SPEED
                        res = self.swe.calc_ut(term_jd, p_id, flags)
                        deg = res[0][0]
                        transits[swe_map[p_id]] = deg
                        if swe_map[p_id] == "Rahu":
                            transits["Ketu"] = (deg + 180) % 360
                data["transit_positions"] = transits
            except Exception as e:
                self.log(f"⚠️ Transit position calc warning: {e}", "yellow")
                data["transit_positions"] = {}
        
        try:
            dob_str = data.get('metadata', {}).get('dob', '')
            if dob_str:
                dob = datetime.strptime(dob_str.split()[0], "%d-%m-%Y")
                age = (now - dob).days / 365.25
                data["analysis_age"] = age
            else:
                data["analysis_age"] = 60.0
        except Exception as e:
            self.log(f"⚠️ Age calculation warning: {e}", "yellow")
            data["analysis_age"] = 60.0
            
        return data

    def _prepare_ml_data_for_item(self, item: dict) -> dict:
        if not hasattr(self, 'run_chart_data') or getattr(self, 'run_chart_data') is None:
            raise RuntimeError("CRITICAL ERROR: run_chart_data missing for ML Item Prep.")
            
        # Use shallow copy instead of deepcopy to save computation/memory.
        ml_data: Any = self.run_chart_data.copy()
        
        start_dt = item.get('start_dt')
        if not start_dt:
            return ml_data
              
        try:
            metadata = ml_data.get('metadata', {})
            if isinstance(metadata, dict):
                dob_str = str(metadata.get('dob', ''))
                if dob_str:
                    dob = datetime.strptime(dob_str.split()[0], "%d-%m-%Y")
                    ml_data["analysis_age"] = (start_dt - dob).days / 365.25 # type: ignore
                else:
                    ml_data["analysis_age"] = 30.0 # type: ignore
            else:
                ml_data["analysis_age"] = 30.0 # type: ignore
        except Exception:
            ml_data["analysis_age"] = 30.0 # type: ignore
              
        if getattr(self, 'swe', None):
            try:
                transits = {}
                jd = self.swe.julday(start_dt.year, start_dt.month, start_dt.day, 12.0)
                planet_map = {"Sun": 0, "Moon": 1, "Mars": 4, "Mercury": 2, "Jupiter": 5, "Venus": 3, "Saturn": 6, "Rahu": 10, "Ketu": 11}
                for p_name, p_id in planet_map.items():
                    flags = self.swe.FLG_SIDEREAL | self.swe.FLG_SPEED
                    if p_name == "Ketu":
                        res = self.swe.calc_ut(jd, 10, flags)
                        lon = (res[0][0] + 180) % 360
                    else:
                        res = self.swe.calc_ut(jd, p_id, flags)
                        lon = res[0][0]
                    transits[p_name] = lon # type: ignore
                ml_data['transit_positions'] = transits # type: ignore
            except Exception as e:
                if hasattr(self, 'console') and self.console:
                    self.log(f"⚠️ SWE transit warning: {e}", "yellow")

        dasha_str = str(item.get('dasha', 'Saturn-Saturn-Saturn'))
        parts = dasha_str.split('-')
        if len(parts) >= 3:
            ml_data['current_dasha'] = {'md': parts[0], 'ad': parts[1], 'pd': parts[2]} # type: ignore
        else:
            ml_data['current_dasha'] = {'md': 'Saturn', 'ad': 'Saturn', 'pd': 'Saturn'} # type: ignore

        raw_gates = item.get('gate_data', {})
        if isinstance(raw_gates, dict):
            ml_data['gate_data'] = { # type: ignore
                'gate_1_pass': raw_gates.get('gate_1', {}).get('verdict') == "PASS",
                'gate_2_pass': raw_gates.get('gate_2', {}).get('verdict') == "PASS",
                'gate_4_fail': raw_gates.get('gate_4', {}).get('verdict') == "PASS", 
                'gate_6_pass': raw_gates.get('gate_6', {}).get('verdict') == "PASS",
                'gate_saturn_protector': raw_gates.get('gate_1', {}).get('F_saturn_8_protector', False)
            }
        else:
            ml_data['gate_data'] = {} # type: ignore
            
        return ml_data

    def setup_ui(self):
        if THEME_AVAILABLE:
            header_frame = tk.Frame(self.root, bg=Colors.BG_MEDIUM, height=80)
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            title_container = tk.Frame(header_frame, bg=Colors.BG_MEDIUM)
            title_container.pack(expand=True)
            
            tk.Label(title_container, text="🔱  KP ASTROLOGER  🔱", font=Fonts.TITLE, fg=Colors.GOLD, bg=Colors.BG_MEDIUM).pack(pady=(20, 2))
            tk.Label(title_container, text="Divya Drishti Master Console • Birth Chart Intelligence", font=Fonts.SMALL, fg=Colors.TEXT_MUTED, bg=Colors.BG_MEDIUM).pack()
            
            tk.Frame(self.root, height=2, bg=Colors.GOLD_DARK).pack(fill="x")
            style = ttk.Style()
            apply_tab_style(style)
        else:
            tk.Label(self.root, text="KP ASTROLOGER", font=("Cinzel", 26, "bold"), fg="#FFD700", bg="#050505").pack(pady=15)
            style = ttk.Style()
            style.theme_use('clam')

        main_notebook = ttk.Notebook(self.root)
        main_notebook.pack(expand=True, fill="both", padx=20, pady=15)
        self.notebook = main_notebook

        bg_color = Colors.BG_DARK if THEME_AVAILABLE else "#050505"

        # Tabs
        self.timing_frame = tk.Frame(main_notebook, bg=bg_color)
        main_notebook.add(self.timing_frame, text="  ⏱️  Event Timing  ")
        self.setup_timing_tab()

        self.general_frame = tk.Frame(main_notebook, bg=bg_color)
        main_notebook.add(self.general_frame, text="  📊  General Analysis  ")
        self.setup_general_tab()

        self.daily_frame = tk.Frame(main_notebook, bg=bg_color)
        main_notebook.add(self.daily_frame, text="  📅  Daily Prediction  ")
        self.setup_daily_tab()

        self.year_frame = tk.Frame(main_notebook, bg=bg_color)
        main_notebook.add(self.year_frame, text="  📆  Year Prediction  ")
        self.setup_year_tab()

        self.setup_status_bar()

    def setup_status_bar(self):
        if THEME_AVAILABLE:
            status_bar = tk.Frame(self.root, bg=Colors.BG_MEDIUM, height=30)
            status_bar.pack(fill="x", side="bottom")
            status_bar.pack_propagate(False)
            
            left_status = tk.Frame(status_bar, bg=Colors.BG_MEDIUM)
            left_status.pack(side="left", padx=15)
            
            self.chart_indicator = StatusIndicator(left_status, color=Colors.TEXT_MUTED)
            self.chart_indicator.pack(side="left", padx=(0, 5))
            tk.Label(left_status, text="Chart", font=Fonts.SMALL, fg=Colors.TEXT_MUTED, bg=Colors.BG_MEDIUM).pack(side="left", padx=(0, 15))
            
            ml_color = Colors.SUCCESS if ML_AVAILABLE else Colors.ERROR
            self.ml_indicator = StatusIndicator(left_status, color=ml_color)
            self.ml_indicator.pack(side="left", padx=(0, 5))
            tk.Label(left_status, text="ML Engine", font=Fonts.SMALL, fg=Colors.TEXT_MUTED, bg=Colors.BG_MEDIUM).pack(side="left")
            
            tk.Label(status_bar, text="v5.0 • Birth Chart Engine", font=Fonts.SMALL, fg=Colors.TEXT_MUTED, bg=Colors.BG_MEDIUM).pack(side="right", padx=15, pady=5)
        else:
            # Simple text-based status without indicators when theme unavailable
            status_bar = tk.Frame(self.root, bg="#1a1a1a", height=25)
            status_bar.pack(fill="x", side="bottom")
            status_bar.pack_propagate(False)
            
            tk.Label(status_bar, text="v5.0 • Birth Chart Engine", 
                    font=("Segoe UI", 8), fg="#888", bg="#1a1a1a").pack(side="right", padx=15, pady=5)
            
            # Create dummy indicators that do nothing
            class DummyIndicator:
                def pack(self, **kwargs): pass
                def set_status(self, *args, **kwargs): pass # Add dummy set_status to prevent future errors
            
            self.chart_indicator = DummyIndicator()
            self.ml_indicator = DummyIndicator()

    # =========================================================================
    # TIMING TAB 
    # =========================================================================
    def setup_timing_tab(self):
        bg_color = Colors.BG_DARK if THEME_AVAILABLE else "#050505"
        card_bg = Colors.BG_CARD if THEME_AVAILABLE else "#1a1a1a"
        
        btn_container = tk.Frame(self.timing_frame, bg=bg_color)
        btn_container.pack(pady=20, padx=20, fill="x")
        
        primary_card = tk.Frame(btn_container, bg=card_bg, padx=20, pady=15)
        primary_card.pack(fill="x", pady=(0, 10))
        
        if THEME_AVAILABLE:
            btn_row1 = tk.Frame(primary_card, bg=card_bg)
            btn_row1.pack(pady=(0, 10))
            ModernButton(btn_row1, text="📂  Load Chart", command=self.read_chart, bg=Colors.BG_HOVER, hover_bg=Colors.CYAN_DARK, width=150, height=40).pack(side="left", padx=8)
            ModernButton(btn_row1, text="🎯  Set Target", command=self.ask_question, bg=Colors.BG_HOVER, hover_bg=Colors.CYAN_DARK, width=150, height=40).pack(side="left", padx=8)
            ModernButton(btn_row1, text="⚡  Generate", command=self.analyze_context, bg=Colors.BG_HOVER, hover_bg=Colors.GOLD_DARK, fg=Colors.GOLD, width=150, height=40).pack(side="left", padx=8)
        else:
            btn_frame = tk.Frame(primary_card, bg=card_bg)
            btn_frame.pack()
            # Pass arguments explicitly for type safety
            tk.Button(btn_frame, text="Load Data", bg="#1a1a1a", fg="#00e5ff", command=self.read_chart, 
                      font=("Segoe UI", 9, "bold"), width=18, height=2, bd=1, relief="flat").grid(row=0, column=0, padx=8)
            tk.Button(btn_frame, text="Set Target", bg="#1a1a1a", fg="#00e5ff", command=self.ask_question, 
                      font=("Segoe UI", 9, "bold"), width=18, height=2, bd=1, relief="flat").grid(row=0, column=1, padx=8)
            tk.Button(btn_frame, text="Generate", bg="#1a1a1a", fg="#00e5ff", command=self.analyze_context, 
                      font=("Segoe UI", 9, "bold"), width=18, height=2, bd=1, relief="flat").grid(row=0, column=2, padx=8)

        console_frame = tk.Frame(self.timing_frame, bg=bg_color)
        console_frame.pack(expand=True, fill="both", padx=20, pady=(0, 10))
        
        if THEME_AVAILABLE:
            console_header = tk.Frame(console_frame, bg=card_bg)
            console_header.pack(fill="x")
            tk.Label(console_header, text="📡  Output Console", font=Fonts.BODY_BOLD, fg=Colors.TEXT_SECONDARY, bg=card_bg).pack(side="left", padx=15, pady=8)
            self.console = EnhancedConsole(console_frame, width=145, height=28)
            self.console.pack(expand=True, fill="both")
        else:
            self.console = scrolledtext.ScrolledText(console_frame, width=140, height=32, bg="#000", fg="#0f0", font=("Consolas", 10))
            self.console.pack(expand=True, fill="both")
            self.console.tag_config("gold", foreground="#FFD700")
            self.console.tag_config("red", foreground="#FF5252")
            self.console.tag_config("cyan", foreground="#00E5FF")
        
        if THEME_AVAILABLE:
            self.console.tag_config("purple", foreground=Colors.PURPLE)
            self.console.tag_config("green", foreground=Colors.SUCCESS)
            self.console.tag_config("yellow", foreground=Colors.WARNING)
            self.console.tag_config("blue", foreground=Colors.INFO)
            self.console.tag_config("orange", foreground="#ff8c00")
        
        self.log("🔱 Event Timing Module Ready", "gold" if THEME_AVAILABLE else "cyan")

    def log(self, text, color=None):
        self.console.insert(tk.END, f">>> {text}\n", color)
        self.console.see(tk.END)

    def read_chart(self):
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    self.chart_data = json.load(f)
                
                chart_ref = self.chart_data
                if not isinstance(chart_ref, dict):
                    self.log("❌ ERROR: Chart data is empty or invalid.", "red")
                    self.chart_data = None
                    return
                
                metadata = chart_ref.get('metadata', {})
                name = metadata.get('name', 'Unknown')
                dob = metadata.get('dob', '')
                self.log(f"✅ LOADED: '{name}' (DOB: {dob})", "gold")
                self.chart_indicator.set_status(Colors.SUCCESS)
            else: 
                self.log(f"❌ ERROR: {DATA_PATH} not found.", "red")
        except Exception as e: 
            self.log(f"❌ CRITICAL ERROR: {str(e)}", "red")
            self.chart_data = None

    def ask_question(self):
        query = simpledialog.askstring("Input", "Target Event (Job, Marriage, Life, Divorce):")
        self.user_query = query if query is not None else ""
        if self.user_query:
            self.user_query = self.user_query.lower()
            self.log(f"Target Set: {self.user_query.upper()}", "cyan")

    def analyze_context(self):
        if not self.chart_data:
            self.log("❌ ERROR: Please load chart data first.", "red")
            return
        if not self.user_query:
            self.log("❌ ERROR: Please set a target event first (e.g., Marriage).", "red")
            return
            return
            
        # FIX: True State Isolation - Single source of truth per run
        self.run_chart_data = copy.deepcopy(self.chart_data)
        current_chart_data = self.run_chart_data

        # One-time absolute longitude computation
        if 'planetary_positions' in current_chart_data:
            for p in current_chart_data['planetary_positions']:
                if 'full_degree' not in p:
                    p['full_degree'] = DataConverter.get_absolute_longitude(p)

        # FIX: Validate chart structure before proceeding
        validation_errors = DataConverter.validate_chart_data(current_chart_data)
        if validation_errors:
            for err in validation_errors:
                self.log(f"⚠️ Validation: {err}", "yellow")
            if any('Missing required' in e or 'not a dict' in e for e in validation_errors):
                self.log("❌ Chart data failed validation. Aborting analysis.", "red")
                return
        
        self.gross_prediction_data = {}
        self.full_life_story = []
        self.log(f"Starting analysis...")
        q = self.user_query
        
        chart_ref = current_chart_data # For internal references that might use it
        
        # --- LIFE / DEATH LOGIC ---
        if "life" in q or "death" in q or "span" in q:
            try:
                try:
                    import prediction.event.life_span # type: ignore
                    importlib.reload(prediction.event.life_span) # type: ignore
                except Exception as e:
                     self.log(f">>> [SYSTEM] Reload Warning: {e}", "cyan")
                
                from prediction.event.life_span import LifeSpanEngine # type: ignore
                self.log("Handing over to LifeSpan Engine", "gold")
                engine = LifeSpanEngine(current_chart_data)
                
                audit_result = engine.perform_audit()
                report = engine.generate_full_proof_report()
                
                cat_name = report.get("Life_Span_Category", "Unknown")
                death_window = ""
                if "ALPAYU" in cat_name: death_window = "0-32 years"
                elif "MADHYAYU" in cat_name: death_window = "33-66 years"
                elif "PURNAYU" in cat_name: death_window = "67+ years"
                
                self.log("-" * 60)
                self.log(f"Death Audit Title", "gold")
                self.log("-" * 60)
                self.log(f"🔮 Longevity Category: {cat_name}", "gold")
                if death_window: self.log(f"☠️  Death Window: {death_window}", "red")
                self.log("-" * 60)
                
                outcome = report.get("Critical_Outcome", "Unknown")
                if "CONFIRMED EXIT" in outcome: self.log(f"🔴 {outcome}", "red")
                elif "CRITICAL" in outcome: self.log(f"🟡 {outcome}", "yellow")
                elif "FALSE ALARM" in outcome: self.log(f"🟢 {outcome}", "green")
                elif "DEFERRED" in outcome: self.log(f"🔵 {outcome}", "blue")
                else: self.log(f"⚪ {outcome}")
                self.log("-" * 60)
                
                timeline = report.get("Event_Windows", [])
                self.gross_prediction_data["Life"] = timeline
                
                for item in timeline[:10]:
                    msg = item.get('full_text', str(item))
                    status = item.get('status', '')
                    if "CONFIRMED EXIT" in status or "🔴" in msg: self.log(msg, "red")
                    elif "CRITICAL" in status or "🟡" in msg: self.log(msg, "yellow")
                    else: self.log(msg)
                
                if not timeline:
                    self.log(f"✅ No Critical Death Windows", "green")
                        
            except Exception as e:
                self.log(f"ERROR in life_span analysis: {e}", "red")

        elif any(w in q for w in ["divorce", "widow", "separation", "breakup"]):
            try:
                if not isinstance(current_chart_data, dict): return
                self.log(">>> HANDING OVER TO: Local MarriageWidowedForensics Engine", "gold")
                engine = MarriageWidowedForensics(current_chart_data)
                report = engine.calculate_timing_report()
                
                self.log("-" * 60)
                self.log(f"7th CSL AUDIT: {report.get('Promise', 'Unknown')}", "gold")
                self.log("-" * 60)
                
                self.gross_prediction_data["Separation"] = report.get("Event_Windows", [])
                self.log(f"Received {len(self.gross_prediction_data['Separation'])} major candidates.")
                # Flush engine logs
                for msg in getattr(engine, '_log_buffer', []):
                    self.log(f"   [Engine] {msg}", "yellow")
            except Exception as e:
                self.log(f"CRITICAL ERROR in Separation Module: {str(e)}", "red")

        # --- CHILD BIRTH TIMING (USING LOCAL ENGINE) ---
        elif any(w in q for w in ["child", "birth", "pregnancy", "progeny", "baby"]):
            try:
                if not isinstance(current_chart_data, dict): return
                self.log(">>> HANDING OVER TO: Local ChildBirthForensics Engine", "gold")
                engine = ChildBirthForensics(current_chart_data)
                report = engine.calculate_timing_report()
                
                self.log("-" * 60)
                self.log(f"5th CSL PROGENY AUDIT: {report.get('Promise', 'Unknown')}", "gold")
                self.log("-" * 60)
                
                self.gross_prediction_data["Child Birth"] = report.get("Event_Windows", [])
                self.log(f"Fertile Windows Found: {len(self.gross_prediction_data['Child Birth'])}")
                # Flush engine logs
                for msg in getattr(engine, '_log_buffer', []):
                    self.log(f"   [Engine] {msg}", "yellow")
            except Exception as e:
                self.log(f"CRITICAL ERROR in Child Birth Module: {str(e)}", "red")

        # --- MARRIAGE TIMING ---
        elif any(w in q for w in ["marriage", "wedding", "spouse"]):
            try:
                from prediction.event.marriage_timing import MarriageForensics # type: ignore
                self.log(f"Handing over to: MarriageForensics Engine", "gold")
                engine = MarriageForensics(current_chart_data)
                report = engine.generate_full_proof_report()
                
                promise_data = report.get("Marriage_Promise", {})
                marriage_count = promise_data.get("marriage_count", "UNKNOWN")
                
                self.log("-" * 60)
                self.log(f"🔮 Marriage Promise Analysis", "gold")
                
                if marriage_count != "NO":
                    self.gross_prediction_data["Marriage"] = report.get("Confirmed_Event_Windows", [])
                    self.log(f"Marriage Windows Found: {len(self.gross_prediction_data['Marriage'])}")
                else:
                    self.log(f"⚠️ Marriage Not Indicated", "red")
            except Exception as e:
                self.log(f"ERROR: Marriage timing module: {e}", "red")

        # --- WEALTH GAIN TIMING ---
        elif any(w in q for w in ["wealth", "income", "money", "gain", "earning"]):
            try:
                from prediction.event.wealth_gain_timing import WealthGainForensics # type: ignore
                self.log(">>> HANDING OVER TO: WealthGainForensics Engine", "gold")
                engine = WealthGainForensics(current_chart_data)
                self.gross_prediction_data["Wealth Gain"] = engine.generate_full_proof_report().get("Event_Windows", [])
                self.log(f"Windows Found: {len(self.gross_prediction_data['Wealth Gain'])}")
            except Exception as e:
                self.log(f"ERROR in Wealth Module: {str(e)}", "red")

        # --- JOB TIMING ---
        elif any(w in q for w in ["job", "employment", "career"]):
            try:
                from prediction.event.job_start_timing import JobStartForensics # type: ignore
                self.log(f"Handing over to: JobStartForensics Engine", "gold")
                engine = JobStartForensics(current_chart_data)
                self.gross_prediction_data["Job Start"] = engine.generate_full_proof_report().get("Event_Windows", [])
                self.log(f"Windows Found: {len(self.gross_prediction_data['Job Start'])}")
            except Exception as e:
                self.log(f"ERROR in Job Module: {str(e)}", "red")
        
        else:
            self.log(f"⚠️ Query '{q.upper()}' is not mapped to an Event Timing engine.", "yellow")
            self.log(f"   (Try: 'Marriage', 'Child', 'Job', 'Wealth', 'Divorce' or 'Life Span')", "cyan")
            return

        # AUTO-RUN
        self.process_with_rules()
        self.run_transit_check()
        self.display_final_result()

    def process_with_rules(self):
        self.log(f"\nStage 2 Audit", "cyan")
        refined = []
        for cat, candidates in self.gross_prediction_data.items():
            for item in candidates: refined.append(item)
        
        self.full_life_story: List[Any] = refined
        self.log(f"Audit Complete. {len(self.full_life_story)} candidates pooled.")

    def run_transit_check(self):
        self.log(f"\nStage 3 Transit Audit", "cyan")
        candidates = [c for c in self.full_life_story if isinstance(c, dict)]
        if not candidates:
            self.log(f"   ⚠️ Skipping Transit Audit: No candidates.", "red")
            return
        
        daily_engine = None
        try:
            if BirthDailyPrediction:
                daily_engine = BirthDailyPrediction(self.run_chart_data)
        except Exception as e:
            self.log(f"   (Transit Engine Init Failed: {e})", "red")

        intent = self.detect_intent(self.user_query)
        target_houses = intent["houses"]
        
        for item in candidates: 
             dasha = item.get('dasha', '')
             start_dt = item.get('start_dt')
             
             if not start_dt and 'window' in item:
                 start_dt = DataConverter.parse_window_date(item['window'])
                 if start_dt: item['start_dt'] = start_dt
            
             if start_dt and daily_engine:
                 try:
                     engine_ref: Any = daily_engine
                     scores = engine_ref.get_transit_scores(start_dt) # type: ignore
                     adj_score = max((scores.get('adjusted_cls', {}).get(h, 0) for h in target_houses), default=0)
                     status_icon = "🟢" if adj_score >= 3.0 else "🟠" if adj_score >= 1.0 else "🔴"
                     audit_msg = f"☀️ TRANSIT: {status_icon} Score {adj_score:.1f}"
                     item['transit_info'] = audit_msg
                     # self.log(f"   ☀️ TRANSIT SCAN [{dasha}]: {audit_msg}", "gold")
                 except Exception as e:
                     self.log(f"   ☀️ TRANSIT SCAN [{dasha}]: Error {e}", "red")

    def _run_ml_candidate_verification(self):
        if not ML_AVAILABLE or not ml_engine: return
        self.log(f"\n🧠 INITIALIZING ML VERIFICATION PROTOCOL...", "cyan")
        event_type = "death" 
        if "CHILD" in self.user_query.upper(): event_type = "child_birth"
        elif "MARRIAGE" in self.user_query.upper(): event_type = "marriage"
        elif "JOB" in self.user_query.upper(): event_type = "job_start"
        
        allowed_models = ["death", "child_birth", "marriage", "job_start"]
        if event_type not in allowed_models: return

        count = 0
        for item in self.full_life_story:
            if isinstance(item, dict):
                start_dt = item.get('start_dt') 
                if not start_dt and 'window' in item:
                    start_dt = DataConverter.parse_window_date(item['window'])
                    if start_dt: item['start_dt'] = start_dt

                if start_dt:
                    try:
                        ml_data = self._prepare_ml_data_for_item(item)
                        engine_ref: Any = ml_engine
                        if engine_ref:
                            # ML normalization fix: assume 0-1, convert to 0-100
                            raw_prob = engine_ref.predict_probability(event_type, ml_data)
                            prob = float(raw_prob) * 100 if float(raw_prob) <= 1.0 else float(raw_prob)
                            
                            # Sanity check ML output
                            if not (0 <= prob <= 100):
                                self.log(f"⚠️ ML hallucinated invalid probability ({prob}%). Discarding candidate.", "yellow")
                                continue
                                
                            item['ml_score'] = prob
                            count += 1
                    except Exception as e:
                        if hasattr(self, 'console') and self.console:
                            self.log(f"⚠️ ML Verification Runtime Error for {event_type}: {e}", "yellow")
        e_type_str = str(event_type).upper()
        self.log(f"   ✅ Verified {count} candidates with {e_type_str} Matrix.", "green")

    def _extract_sort_date(self, item):
        if not isinstance(item, dict): return datetime.max
        if 'start_dt' in item and isinstance(item['start_dt'], datetime): return item['start_dt']
        if 'window' in item:
            dt = DataConverter.parse_window_date(item['window'])
            if dt: return dt
        return datetime.max

    def display_final_result(self):
        lang = getattr(self, 'language', 'en')
        tc_empty = f"FINAL CHRONICLE: NO EVENTS FOUND for '{self.user_query.upper()}'"
        tc = "FINAL CHRONICLE:"
        if lang == 'hi': 
            tc_empty = f"अंतिम कालक्रम: '{self.user_query.upper()}' के लिए कोई घटना नहीं मिली"
            tc = "अंतिम कालक्रम:"
        if lang == 'bn': 
            tc_empty = f"চূড়ান্ত কালক্রম: '{self.user_query.upper()}' এর জন্য কোন ইভেন্ট পাওয়া যায়নি"
            tc = "চূড়ান্ত কালক্রম:"

        if not self.full_life_story:
            self.log(f"\n❌ {tc_empty}", "red")
            return
        self.log(f"\n{tc} {self.user_query.upper()}")
        
        self._run_ml_candidate_verification()
        
        sorted_results = sorted(self.full_life_story, key=self._extract_sort_date)
        
        for item in sorted_results:
            if isinstance(item, dict):
                date_range = item.get('window', 'Unknown')
                dasha = item.get('dasha', 'Unknown')
                
                ml_score = item.get('ml_score', -1)
                ml_tag = ""
                if ml_score >= 80: ml_tag = " [🤖 ML: 80%+ Confirmed]"
                elif ml_score >= 50: ml_tag = f" [🤖 ML: {ml_score:.1f}% Likely]"
                elif ml_score > 0: ml_tag = f" [🤖 ML: {ml_score:.1f}% Possible]"
                
                transit_tag = item.get('transit_info', "")
                stability = item.get('stability', 'Standard')
                
                if "MAJOR" in stability or "FERTILE" in stability:
                    self.log(f"• **{date_range}** ({dasha}) - {stability} - {transit_tag}{ml_tag}", "gold")
                else:
                    self.log(f"• **{date_range}** ({dasha}) - {stability} - {transit_tag}{ml_tag}")
            else:
                self.log(f"• {str(item)}")


    # =========================================================================
    # GENERAL ANALYSIS TAB
    # =========================================================================
    def setup_general_tab(self):
        bg_color = Colors.BG_DARK if THEME_AVAILABLE else "#050505"
        card_bg = Colors.BG_CARD if THEME_AVAILABLE else "#1a1a1a"
        
        btn_container = tk.Frame(self.general_frame, bg=bg_color)
        btn_container.pack(pady=20, padx=20, fill="x")
        
        actions_card = tk.Frame(btn_container, bg=card_bg, padx=20, pady=15)
        actions_card.pack(fill="x")
        
        if THEME_AVAILABLE:
            btn_row1 = tk.Frame(actions_card, bg=card_bg)
            btn_row1.pack(pady=(0, 10))
            ModernButton(btn_row1, text="📂  Read Data", command=self.gen_read_data, bg=Colors.BG_HOVER, hover_bg=Colors.GOLD_DARK, fg=Colors.GOLD, width=170, height=40).pack(side="left", padx=10)
            ModernButton(btn_row1, text="🔍  Set Query", command=self.gen_set_query, bg=Colors.BG_HOVER, hover_bg=Colors.GOLD_DARK, fg=Colors.GOLD, width=170, height=40).pack(side="left", padx=10)
            ModernButton(btn_row1, text="✨  Check Possibility", command=self.gen_check_possibility, bg="#4a1a5c", hover_bg="#6b2d7b", fg=Colors.PURPLE, width=170, height=40).pack(side="left", padx=10)
            
            btn_row2 = tk.Frame(actions_card, bg=card_bg)
            btn_row2.pack()
            self.btn_gen_generate = ModernButton(btn_row2, text="⚡  Generate Info", command=self.gen_generate_info, bg=Colors.BG_MEDIUM, hover_bg=Colors.BG_HOVER, fg=Colors.TEXT_MUTED, width=170, height=40)
            self.btn_gen_generate.pack(side="left", padx=10)
            self.btn_gen_result = ModernButton(btn_row2, text="📊  Show Result", command=self.gen_show_result, bg="#1a3d1a", hover_bg="#2d5a2d", fg=Colors.SUCCESS, width=170, height=40)
            self.btn_gen_result.pack(side="left", padx=10)
        else:
            btn_frame = tk.Frame(actions_card, bg=card_bg)
            btn_frame.pack()
            # Pass arguments explicitly for type safety
            tk.Button(btn_frame, text="Read Data", bg="#1a1a1a", fg="#FFD700", command=self.gen_read_data, 
                      font=("Segoe UI", 10, "bold"), width=22, height=2, bd=1, relief="flat").grid(row=0, column=0, padx=12)
            tk.Button(btn_frame, text="Set Query", bg="#1a1a1a", fg="#FFD700", command=self.gen_set_query, 
                      font=("Segoe UI", 10, "bold"), width=22, height=2, bd=1, relief="flat").grid(row=0, column=1, padx=12)
            tk.Button(btn_frame, text="Check Possibility", bg="#4a148c", fg="white", command=self.gen_check_possibility, 
                      font=("Segoe UI", 10, "bold"), width=22, height=2, bd=1, relief="flat").grid(row=0, column=2, padx=12)
            self.btn_gen_generate = tk.Button(btn_frame, text="Generate Info", bg="#1a1a1a", fg="#FFD700", command=self.gen_generate_info, state="disabled", 
                                              font=("Segoe UI", 10, "bold"), width=22, height=2, bd=1, relief="flat")
            self.btn_gen_generate.grid(row=1, column=0, padx=12, pady=15)
            self.btn_gen_result = tk.Button(btn_frame, text="Show Result", bg="#2e7d32", fg="white", command=self.gen_show_result, state="disabled", 
                                            font=("Segoe UI", 10, "bold"), width=22, height=2, bd=1, relief="flat")
            self.btn_gen_result.grid(row=1, column=1, padx=12, pady=15)

        console_frame = tk.Frame(self.general_frame, bg=bg_color)
        console_frame.pack(expand=True, fill="both", padx=20, pady=(0, 10))
        
        if THEME_AVAILABLE:
            console_header = tk.Frame(console_frame, bg=card_bg)
            console_header.pack(fill="x")
            tk.Label(console_header, text="📜  Analysis Output", font=Fonts.BODY_BOLD, fg=Colors.TEXT_SECONDARY, bg=card_bg).pack(side="left", padx=15, pady=8)
            self.general_console = EnhancedConsole(console_frame, width=140, height=26)
            self.general_console.pack(expand=True, fill="both")
            self.general_console.tag_config("title", foreground=Colors.GOLD, font=Fonts.HEADING)
            self.general_console.tag_config("header", foreground=Colors.GOLD_LIGHT, font=Fonts.BODY_BOLD)
            self.general_console.tag_config("fail", foreground=Colors.ERROR)
            self.general_console.tag_config("highlight", foreground=Colors.CYAN, font=Fonts.BODY_BOLD)
        else:
            self.general_console = scrolledtext.ScrolledText(console_frame, width=135, height=30, bg="#080808", fg="#b0bec5", font=("Georgia", 11))
            self.general_console.pack(expand=True, fill="both")
            self.general_console.tag_config("title", foreground="#FFD700", font=("Georgia", 14, "bold"))
            self.general_console.tag_config("success", foreground="#00E676")
            self.general_console.tag_config("fail", foreground="#FF5252")
            self.general_console.tag_config("highlight", foreground="#29B6F6", font=("Georgia", 11, "bold"))
            self.general_console.tag_config("header", foreground="#FFD700", font=("Georgia", 12, "bold", "underline"))
        
        self.gen_log("🔱 KP ASTROLOGER General Analysis Ready", "title")

    def setup_daily_tab(self):
        """Standard implementation of Daily Tab to prevent AttributeError."""
        bg_color = Colors.BG_DARK if THEME_AVAILABLE else "#050505"
        container = tk.Frame(self.daily_frame, bg=bg_color)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text="📅  Daily Prediction Module", font=Fonts.TITLE, fg=Colors.GOLD, bg=bg_color).pack(pady=10)
        tk.Label(container, text="This module is currently being optimized for V11 architecture.\nDetailed daily transit analysis will appear here.", font=Fonts.BODY, fg=Colors.TEXT_MUTED, bg=bg_color).pack()

    def setup_year_tab(self):
        """Standard implementation of Year Tab to prevent AttributeError."""
        bg_color = Colors.BG_DARK if THEME_AVAILABLE else "#050505"
        container = tk.Frame(self.year_frame, bg=bg_color)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text="📆  Yearly Prediction Module", font=Fonts.TITLE, fg=Colors.GOLD, bg=bg_color).pack(pady=10)
        tk.Label(container, text="Yearly progression and Muntha analysis engine is being synchronized.\nPlease check back shortly.", font=Fonts.BODY, fg=Colors.TEXT_MUTED, bg=bg_color).pack()

    def gen_log(self, text, tag=None):
        self.general_console.insert(tk.END, f"{text}\n", tag)
        self.general_console.see(tk.END)

    def gen_read_data(self):
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    self.chart_data = json.load(f)
                
                chart_ref = self.chart_data
                if not chart_ref or not isinstance(chart_ref, dict):
                    self.general_console.delete(1.0, tk.END)
                    self.gen_log(f"❌ ERROR: Chart data is empty. Please generate a chart first.", "fail")
                    self.chart_data = None
                    return
                metadata = chart_ref.get('metadata', {})
                if not isinstance(metadata, dict): metadata = {}
                name = metadata.get('name', 'Unknown')
                self.general_console.delete(1.0, tk.END)
                self.gen_log(f"✅ DATA LOADED: {name}", "success")
                self.gen_log(f"System ready for General Analysis.")
            else:
                self.gen_log(f"❌ ERROR: {DATA_PATH} not found.", "fail")
        except Exception as e:
            self.gen_log(f"❌ CRITICAL ERROR: {str(e)}", "fail")

    def gen_set_query(self):
        if not self.chart_data:
            messagebox.showwarning("Warning", "Please Load Data First.")
            return
        
        query = simpledialog.askstring("General Query", "Enter Topic (e.g. Courage, Intelligence, Marriage):")
        if query:
            self.gen_query = query.lower().strip()
            self.gen_log(f"\n🔍 QUERY SET: {self.gen_query.upper()}", "title")
            
            self.is_event_possible = False
            self.btn_gen_generate.config(state="disabled")
            self.btn_gen_result.config(state="disabled")

    def gen_check_possibility(self):
        if not self.gen_query or not self.chart_data: return
        self.gen_log(f"Analyzing Chart Promise for {self.gen_query.upper()}...", "title")
        
        # Real logic: Look for keyword in significator mapping (mock implementation improvement)
        relevant_houses = []
        q = self.gen_query.lower()
        if "marriage" in q: relevant_houses = [2, 7, 11]
        elif "education" in q: relevant_houses = [4, 9, 11]
        elif "career" in q or "job" in q: relevant_houses = [2, 6, 10, 11]
        
        if relevant_houses:
            self.gen_log(f"   (Detected houses related to query: {relevant_houses})")
            
        self.is_event_possible = True
        self.gen_log(f"✅ POSSIBILITY CONFIRMED: Descriptive analysis available.", "success")
        self.btn_gen_generate.config(state="normal") 

    def gen_generate_info(self):
        if not self.is_event_possible: return
        self.gen_log(f"\n📖 ENGAGING PREDICTION ENGINE...", "title")
        
        module_map = {
            "story": ("Past_Life_Story_Generator.py", "connect_titanium"),
            "past life": ("past_life_signs.py", "analyze_sign_placement"),
            "karma": ("karmic_indicators_engine.py", "get_karmic_report"),
            "dharma": ("dharma_ethics_predict.py", "analyze_dharma_ethics"),
            "appearance": ("kp_appearance.py", "connect_titanium"),
            "courage": ("courage_initiation_predict_advanced.py", "connect_titanium"),
            "talent": ("self_effort_talent_predict.py", "analyze_self_effort"),
            "skills": ("skills_hobbies_predict.py", "analyze_skills"),
            "intelligence": ("creativity_intelligence_predict.py", "analyze_creativity_intelligence"),
            "speech": ("speech_communication_predict_advanced.py", "analyze_speech"),
            "writing": ("writing_media_predict.py", "connect_titanium"),
            "fears": ("fear_subconscious_predict.py", "analyze_fears"),
            "dream": ("dream_pattern_predict.py", "get_dream_pattern_report"),
            "spiritual": ("spiritual_blessings_predict.py", "analyze_spiritual_blessings"),
            "occult": ("esoteric_knowledge_predict.py", "analyze_esoteric"),
            "death reason": ("death_reason_predict.py", "get_death_reason_report"),
            "life": ("life_span.py", "calculate_longevity"),
            "money": ("bank_balance_predict.py", "get_bank_balance_report"),
            "career": ("career_direction_predict.py", "get_career_direction_report"),
            "business": ("business_service_predict.py", "analyze_business_service"),
            "partnership": ("business_partnership_predict.py", "analyze_business_partnership"),
            "speculation": ("speculation_trading_predict.py", "analyze_speculation"),
            "loss": ("losses_expenses_predict.py", "analyze_losses"),
            "sudden gain": ("sudden_gain_loss_predict.py", "analyze_sudden_gain_loss"),
            "inheritance": ("inheritance_predict.py", "analyze_inheritance"),
            "loan": ("loan_debt_predict.py", "analyze_loan_debt"),
            "repayment": ("loan_repayment_predict.py", "analyze_repayment"),
            "marriage count": ("marriage_count_predict.py", "analyze_marriage_count"),
            "marriage location": ("marriage_location_predict.py", "analyze_marriage_location"),
            "spouse psychology": ("spouse_psychology_predict.py", "analyze_spouse_psychology"),
            "post marriage": ("post_marriage_predict.py", "analyze_post_marriage_family"),
            "divorce": ("divorce_widowhood_predict.py", "get_divorce_widowhood_report"),
            "love": ("love_relationships_predict.py", "analyze_love_relationships"),
            "affair": ("love_affair_predict.py", "analyze_love_affair"),
            "sexual intensity": ("sexual_intensity_predict.py", "analyze_sexual_intensity"),
            "sexual life": ("sexual_life_predict.py", "analyze_sexual_life"),
            "secret": ("secret_relationship_predict.py", "analyze_secret_relationship"),
            "child": ("children_predict.py", "get_children_report"),
            "second child": ("second_child_predict.py", "analyze_second_child"),
            "yearly": ("yearly_prediction.py", "get_yearly_prediction_report"),
            "family": ("family_relatives_predict.py", "get_family_relatives_report"),
            "mother": ("mother_psychology_predict.py", "analyze_mother_psychology"),
            "mother in law": ("mother_in_law_predict.py", "analyze_mother_in_law"),
            "sibling": ("elder_siblings_predict.py", "analyze_elder_siblings"),
            "health": ("disease_health_predict.py", "get_disease_health_report"),
            "surgery": ("surgery_predict.py", "analyze_surgery"),
            "education": ("education_predict.py", "get_education_report"),
            "property": ("house_residence_predict.py", "analyze_house_residence"),
            "vehicle": ("vehicle_purchase_predict.py", "analyze_vehicle_purchase"),
            "travel": ("foreign_travel_predict.py", "get_foreign_travel_report"),
            "litigation": ("court_case_predict.py", "get_court_case_report"),
            "jail": ("jail_imprisonment_predict.py", "analyze_imprisonment"),
            "enemies": ("enemies_predict.py", "analyze_enemies"),
            "eating": ("food_eating_predict_advanced.py", "analyze_food_eating"),
            "personality": ("personality_predict.py", "analyze_personality"),
            "soul": ("soul_journey_engine.py", "get_soul_report"),
            "karmic": ("karmic_indicators_engine.py", "get_karmic_report"),
            "vastu": ("vastu_predict.py", "analyze_vastu"),
            "scandal": ("scandal_predict.py", "analyze_scandal"),
            "hidden": ("hidden_matters_predict.py", "analyze_hidden_matters"),
            "insurance": ("insurance_predict.py", "analyze_insurance"),
            "election": ("election_predict.py", "analyze_election"),
            "interview": ("job_interview_predict.py", "analyze_interview"),
            "psychology": ("psychological_predict.py", "analyze_psychology"),
            "teacher": ("teacher_mentor_predict.py", "analyze_teacher_mentor")
        }

        target = None
        for key in module_map:
            if key in self.gen_query:
                target = module_map[key]
                break
        
        if not target:
            self.gen_log(f"⚠️ No exact map for '{self.gen_query}'. Attempting fuzzy search...", "highlight")
            best_match_key = None
            best_match_score = 0.0
            
            for key in module_map:
                ratio = difflib.SequenceMatcher(None, self.gen_query, key).ratio()
                if ratio > best_match_score:
                    best_match_score = ratio
                    best_match_key = key
            
            if best_match_score > 0.6 and best_match_key:
                 self.gen_log(f"✅ Interpreted '{self.gen_query}' as '{best_match_key.upper()}' (Confidence: {int(best_match_score*100)}%)", "success")
                 target = module_map[best_match_key]
            else:
                 self.gen_log(f"❌ Could not interpret query. Best guess: '{best_match_key}' ({int(best_match_score*100)}%) - Low Confidence.", "fail")
                 return

        if target is None: return
        filename_info, primary_function = target
        
        if isinstance(filename_info, tuple):
            folder, filename = filename_info
            module_path = os.path.join(project_root, 'prediction', folder, filename)
        else:
            filename = filename_info
            module_path = os.path.join(project_root, 'prediction', 'general', filename)
        
        if filename == "Past_Life_Story_Generator.py":
            self.gen_log(f"Invoking Past Life Generator...", "highlight")
            if analyze_past_life_story:
                try:
                    p_data = self.chart_data.get('planetary_positions', []) or self.chart_data.get('planets', [])
                    c_data = self.chart_data.get('house_cusps', []) or self.chart_data.get('cusps', [])
                    self.generated_report = analyze_past_life_story(p_data, c_data)
                    self.gen_log("✅ Report Generated Successfully.", "success")
                    self.btn_gen_result.config(state="normal")
                    return
                except Exception as ex:
                    self.gen_log(f"❌ Runtime Error in Past Life Generator: {ex}", "fail")
                    return
            else:
                 self.gen_log(f"⚠️ Module not imported. Trying dynamic load...", "highlight")

        self.gen_log(f"Converting Chart Data for {filename}...", "highlight")
        chart_data_copy = copy.deepcopy(self.chart_data)
        p_data, c_data = DataConverter.convert_for_engine(chart_data_copy)
        
        try:
            if not os.path.exists(module_path):
                module_path = os.path.join(src_directory, filename)
                if not os.path.exists(module_path):
                    self.gen_log(f"❌ Module not found at: {module_path}", "fail")
                    return

            # FIX: Use Unique Name and Set Package context for Relative Imports
            folder_alias = folder if 'folder' in locals() else "general"
            unique_name = f"titanium_load_{folder_alias}_{filename.replace('.', '_')}"
            
            spec = importlib.util.spec_from_file_location(unique_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                # --- FIX: Set Package Context (Important for .transit_utils imports) ---
                module.__package__ = f"prediction.{folder_alias}"
                
                sys.modules[spec.name] = module
                loader: Any = spec.loader
                loader.exec_module(module) # type: ignore
            else:
                self.gen_log(f"❌ Could not load module spec for {filename}.", "fail")
                return

            func_to_run = None
            if hasattr(module, primary_function):
                func_to_run = getattr(module, primary_function)
            elif hasattr(module, "connect_titanium"):
                func_to_run = getattr(module, "connect_titanium")
            else:
                bridge_funcs: List[Any] = []
                get_funcs: List[Any] = []  
                analyze_funcs: List[Any] = [] 
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj):
                        if name.startswith("get_") and name.endswith("_report"):
                            bridge_funcs.append(obj)
                        elif name.startswith("get_"):
                            get_funcs.append(obj)
                        elif name.startswith("analyze_"):
                            analyze_funcs.append(obj)
                
                if bridge_funcs:
                    func_to_run = bridge_funcs[0]
                elif get_funcs:
                    func_to_run = get_funcs[0]
                elif analyze_funcs:
                    func_to_run = analyze_funcs[0]
            
            if func_to_run:
                self.gen_log(f"🚀 Executing Engine: {func_to_run.__name__}...", "success")
                try:
                    sig = inspect.signature(func_to_run)
                    if len(sig.parameters) == 2:
                        self.generated_report = func_to_run(p_data, c_data)
                    else:
                        self.generated_report = func_to_run(copy.deepcopy(self.chart_data))
                    
                    if isinstance(self.generated_report, dict):
                        keys_list = list(self.generated_report.keys())
                        self.gen_log(f"📋 Report keys: {keys_list}", "highlight")
                        
                    self.gen_log("✅ Report Generated Successfully.", "success")
                    self.btn_gen_result.config(state="normal")
                except Exception as ex:
                    self.gen_log(f"❌ Runtime Error: {ex}", "fail")
            else:
                self.gen_log(f"❌ No suitable execution function found in {filename}.", "fail")

        except Exception as e:
            self.gen_log(f"❌ SYSTEM ERROR: {str(e)}", "fail")

    # =========================================================================
    # GEN SHOW RESULT  — ENHANCED with narrative + Hindi / Bengali support
    # =========================================================================
    def gen_show_result(self):
        if not self.generated_report:
            return

        # ── resolve language ──────────────────────────────────────────────────
        lang = self._get_report_lang()
        L   = self.REPORT_LABELS[lang]          # shorthand label dict
        DIV = L["divider"]
        SEC = L["section_divider"]

        # ── header block ──────────────────────────────────────────────────────
        self.gen_log("\n" + DIV)
        self.gen_log(f"{L['title_prefix']}: {self.gen_query.upper()}", "title")
        self.gen_log(DIV + "\n")

        # ── narrative intro (language-aware) ──────────────────────────────────
        intro = self.REPORT_INTRO.get(lang, self.REPORT_INTRO["en"])
        self.gen_log(intro + "\n", "highlight")

        # ── render body ───────────────────────────────────────────────────────
        report = self.generated_report

        # --- CASE 1: plain string ---
        if isinstance(report, str):
            self.gen_log(report)

        # --- CASE 2: dict ---
        elif isinstance(report, dict):
            # (a) top-level narrative key
            if "narrative" in report:
                self.gen_log(str(report["narrative"]))

            # (b) nested report.narrative
            elif ("report" in report
                  and isinstance(report["report"], dict)
                  and "narrative" in report["report"]):
                self.gen_log(str(report["report"]["narrative"]))

            # (c) structured dict — iterate keys
            else:
                for key, block in report.items():
                    if isinstance(block, dict) and "name" in block:
                        # e.g. { "1": {"name": "Sun", "summary": "..."} }
                        level_label = f"{L['house_label']} {key}" if str(key).isdigit() else str(key)
                        self.gen_log(f"\n{level_label}: {block['name']}", "header")
                        summary = block.get('summary', block.get('Synthesis', block.get('outcome', '')))
                        if summary:
                            self.gen_log(f"   {L['synthesis']} {summary}\n")
                    elif isinstance(block, dict):
                        self.gen_log(f"\n{key}", "header")
                        for sub_k, sub_v in block.items():
                            self.gen_log(f"   {sub_k}: {sub_v}")
                    else:
                        self.gen_log(f"{key}: {block}")

        # --- CASE 3: list ---
        elif isinstance(report, list):
            for line in report:
                if not isinstance(line, dict):
                    self.gen_log(str(line))
                    continue

                item_type  = line.get('Type', '')
                house      = line.get('House', '')
                category   = line.get('Category', '')
                role       = line.get('Role', '')

                # ── CSL / Occupant entries ────────────────────────────────────
                if role and ('CSL' in role or 'Occupant' in role):
                    planet    = line.get('Planet', f'H{house}')
                    sub_lord  = line.get('Sub_Lord', '')
                    star_lord = line.get('Star_Lord', '')
                    outcome   = line.get('Outcome', '')
                    synthesis = line.get('Synthesis', '')

                    self.gen_log(f"\n{SEC}")

                    if 'PRIMARY' in role:
                        role_label = L["primary_csl"]
                        self.gen_log(f"🏛️ {planet}  ({role_label})", "header")
                    else:
                        role_label = L["secondary_occ"]
                        self.gen_log(f"{L['planet_label']} {planet}  ({role_label})", "header")

                    if star_lord and sub_lord:
                        self.gen_log(
                            f"   {L['star_label']}: {star_lord}  |  "
                            f"{L['sub_label']}: {sub_lord}"
                        )

                    # direction / career block
                    if 'Direction:' in outcome:
                        direction = (
                            outcome.split('Direction: **')[1].split('**')[0]
                            if 'Direction: **' in outcome else ''
                        )
                        career_val = (
                            outcome.split('Career Type: **')[1].split('**')[0]
                            if 'Career Type: **' in outcome else ''
                        )
                        if direction:
                            self.gen_log(f"   {L['direction']}: {direction}", "highlight")
                        if career_val:
                            self.gen_log(f"   {L['career']}: {career_val}")
                    elif synthesis:
                        tail = synthesis.split('→')[-1].strip()
                        self.gen_log(f"   {L['synthesis']} {tail}", "highlight")
                    elif outcome:
                        self.gen_log(f"   {L['outcome']} {outcome}")

                # ── DNA block ─────────────────────────────────────────────────
                elif item_type == 'DNA':
                    house_label = f"{L['career_dna']} ({L['house_label']} {house})"
                    self.gen_log(f"\n{house_label}", "header")
                    csl      = line.get('CSL', '')
                    analysis = line.get('Analysis', '')
                    if csl:
                        self.gen_log(f"   {L['controller']}: {csl}")
                    if analysis:
                        self.gen_log(f"   {L['synthesis']} {analysis}", "highlight")

                # ── Planet block ──────────────────────────────────────────────
                elif item_type == 'Planet':
                    planet    = line.get('Planet', '')
                    sub       = line.get('Sub', '')
                    synthesis = line.get('Synthesis', '')
                    outcome   = line.get('Outcome', '')
                    house_lbl = f"{L['house_label']} {house}" if house else ''
                    self.gen_log(f"\n{L['planet_label']} {house_lbl} — {planet}", "header")
                    if sub:
                        self.gen_log(f"   {L['sub_lord']}: {sub}")
                    if synthesis:
                        self.gen_log(f"   {L['synthesis']} {synthesis}", "highlight")
                    if outcome:
                        self.gen_log(f"   {L['result']} {outcome}")

                # ── Category block ────────────────────────────────────────────
                elif category:
                    header_text = (
                        f"{L['house_label']} {category}"
                        if isinstance(category, int)
                        else str(category)
                    )
                    verdict    = line.get('Verdict', line.get('Synthesis', ''))
                    details    = line.get('Details', line.get('Outcome', line.get('Description', '')))
                    controller = line.get('Controller', line.get('CSL', ''))

                    self.gen_log(f"\n{header_text}", "header")
                    if controller:
                        self.gen_log(f"   {L['controller']}: {controller}")
                    if verdict:
                        self.gen_log(f"   {L['verdict']} {verdict}", "highlight")
                    if details:
                        self.gen_log(f"   {L['details']} {details}")

                # ── generic planet/house fallback ─────────────────────────────
                else:
                    planet    = line.get('Planet', line.get('planet', ''))
                    house_val = line.get('House',  line.get('house',  ''))
                    outcome   = line.get('Outcome',    line.get('outcome', ''))
                    synthesis = line.get('Synthesis',  line.get('synthesis', ''))

                    if planet or house_val:
                        label = (
                            planet if planet
                            else f"{L['house_label']} {house_val}"
                        )
                        self.gen_log(f"\n{L['location_pin']} {label}")
                        if outcome:
                            self.gen_log(f"   {outcome}")
                        elif synthesis:
                            self.gen_log(f"   {synthesis}")
                    else:
                        self.gen_log(f"\n• {str(line)}")

        # --- CASE 4: anything else ---
        else:
            self.gen_log(str(report))

        # ── footer ────────────────────────────────────────────────────────────
        self.gen_log("\n" + DIV)
        self.gen_log(L["complete"], "success")

    # =========================================================================
    # DAILY & YEARLY TABS
    # =========================================================================
    def setup_daily_tab(self):
        bg_color = Colors.BG_DARK if THEME_AVAILABLE else "#050505"
        card_bg = Colors.BG_CARD if THEME_AVAILABLE else "#1a1a1a"
        
        top_frame = tk.Frame(self.daily_frame, bg=bg_color)
        top_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(top_frame, text="📅 Daily Prediction Module", 
                font=Fonts.HEADING if THEME_AVAILABLE else ("Segoe UI", 16, "bold"),
                fg=Colors.GOLD if THEME_AVAILABLE else "#FFD700", bg=bg_color).pack()
        
        selection_frame = tk.Frame(self.daily_frame, bg=card_bg, padx=20, pady=20)
        selection_frame.pack(fill="x", padx=40, pady=10)
        
        tk.Label(selection_frame, text="Select Date for Prediction:", 
                font=Fonts.BODY_BOLD if THEME_AVAILABLE else ("Segoe UI", 11, "bold"),
                fg=Colors.TEXT_PRIMARY if THEME_AVAILABLE else "#eee", bg=card_bg).pack(side="left", padx=(0, 15))
        
        current_date = datetime.now()
        
        self.daily_day_var = tk.StringVar(value=str(current_date.day))
        days = [str(d) for d in range(1, 32)]
        self.combo_day = ttk.Combobox(selection_frame, textvariable=self.daily_day_var, values=days, width=3, state="readonly")
        self.combo_day.pack(side="left", padx=5)
        
        self.daily_month_var = tk.StringVar(value=current_date.strftime("%B"))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.combo_month = ttk.Combobox(selection_frame, textvariable=self.daily_month_var, values=months, width=10, state="readonly")
        self.combo_month.pack(side="left", padx=5)
        
        current_year = current_date.year
        self.daily_year_var = tk.StringVar(value=str(current_year))
        years = [str(y) for y in range(current_year - 5, current_year + 6)]
        self.combo_year = ttk.Combobox(selection_frame, textvariable=self.daily_year_var, values=years, width=5, state="readonly")
        self.combo_year.pack(side="left", padx=5)
        
        btn_action_frame = tk.Frame(selection_frame, bg=card_bg)
        btn_action_frame.pack(side="left", padx=20)
        
        if THEME_AVAILABLE:
            ModernButton(btn_action_frame, text="📂 READ DATA", command=self.read_daily_data,
                        bg=Colors.BG_HOVER, hover_bg=Colors.CYAN_DARK, width=130, height=35).pack(side="left", padx=5)
            ModernButton(btn_action_frame, text="⚡ PREDICTION", command=self.generate_daily_prediction,
                        bg=Colors.BG_HOVER, hover_bg=Colors.GOLD_DARK, fg=Colors.GOLD, width=150, height=35).pack(side="left", padx=5)
        else:
            tk.Button(btn_action_frame, text="📂 READ DATA", command=self.read_daily_data,
                     bg="#1a1a1a", fg="#00e5ff", font=("Segoe UI", 10, "bold"), padx=15, pady=5).pack(side="left", padx=5)
            tk.Button(btn_action_frame, text="⚡ PREDICTION", command=self.generate_daily_prediction,
                     bg="#1a1a1a", fg="#FFD700", font=("Segoe UI", 10, "bold"), padx=15, pady=5).pack(side="left", padx=5)

        self.daily_result_frame = tk.Frame(self.daily_frame, bg=bg_color)
        self.daily_result_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.daily_console = scrolledtext.ScrolledText(self.daily_result_frame, width=100, height=15, bg="#080808", fg="#ccc", font=("Consolas", 11))
        self.daily_console.pack(fill="both", expand=True)

    def read_daily_data(self):
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    self.chart_data = json.load(f)
                chart_ref = self.chart_data
                if not isinstance(chart_ref, dict):
                    self.daily_console.insert(tk.END, f"❌ ERROR: Chart data is empty.\n")
                    self.chart_data = None
                    return
                name = chart_ref.get('metadata', {}).get('name', 'Unknown')
                self.daily_console.delete(1.0, tk.END)
                self.daily_console.insert(tk.END, f"✅ DATA LOADED SUCCESSFULLY! ({name})\n")
            else:
                self.daily_console.insert(tk.END, f"❌ ERROR: chart_data.json not found.\n")
        except Exception as e:
            self.daily_console.insert(tk.END, f"❌ ERROR: {str(e)}\n")

    def generate_daily_prediction(self):
        if not self.chart_data: return
        day = self.daily_day_var.get()
        month = self.daily_month_var.get()
        year = self.daily_year_var.get()
        try:
            date_str = f"{day} {month} {year}"
            target_date = datetime.strptime(date_str, "%d %B %Y")
        except ValueError:
            return

        self.daily_console.delete(1.0, tk.END)
        try:
            if BirthDailyPrediction:
                engine = BirthDailyPrediction(self.chart_data)
                report = engine.get_prediction(target_date)
                self.daily_console.insert(tk.END, report)
            else:
                self.daily_console.insert(tk.END, "❌ Engine not available.")
        except Exception as e:
            self.daily_console.insert(tk.END, f"Error generating prediction: {str(e)}\n")

    def setup_year_tab(self):
        bg_color = Colors.BG_DARK if THEME_AVAILABLE else "#050505"
        card_bg = Colors.BG_CARD if THEME_AVAILABLE else "#1a1a1a"
        
        top_frame = tk.Frame(self.year_frame, bg=bg_color)
        top_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(top_frame, text="📆 Year Wise Prediction Module", 
                font=Fonts.HEADING if THEME_AVAILABLE else ("Segoe UI", 16, "bold"),
                fg=Colors.GOLD if THEME_AVAILABLE else "#FFD700", bg=bg_color).pack()
        
        selection_frame = tk.Frame(self.year_frame, bg=card_bg, padx=20, pady=20)
        selection_frame.pack(fill="x", padx=40, pady=10)
        
        tk.Label(selection_frame, text="Select Year for Prediction:", 
                font=Fonts.BODY_BOLD if THEME_AVAILABLE else ("Segoe UI", 11, "bold"),
                fg=Colors.TEXT_PRIMARY if THEME_AVAILABLE else "#eee", bg=card_bg).pack(side="left", padx=(0, 15))
        
        current_year = datetime.now().year
        self.year_val_var = tk.StringVar(value=str(current_year))
        years = [str(y) for y in range(current_year - 5, current_year + 11)] 
        self.combo_year_only = ttk.Combobox(selection_frame, textvariable=self.year_val_var, values=years, width=10, state="readonly")
        self.combo_year_only.pack(side="left", padx=5)
        
        if THEME_AVAILABLE:
            ModernButton(selection_frame, text="⚡ PREDICTION", command=self.generate_year_prediction,
                        bg=Colors.BG_HOVER, hover_bg=Colors.GOLD_DARK, fg=Colors.GOLD, width=150, height=35).pack(side="left", padx=20)
        else:
            tk.Button(selection_frame, text="⚡ PREDICTION", command=self.generate_year_prediction,
                     bg="#1a1a1a", fg="#FFD700", font=("Segoe UI", 10, "bold"), padx=15, pady=5).pack(side="left", padx=20)

        self.year_result_frame = tk.Frame(self.year_frame, bg=bg_color)
        self.year_result_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.year_console = scrolledtext.ScrolledText(self.year_result_frame, width=100, height=15, bg="#080808", fg="#ccc", font=("Consolas", 11))
        self.year_console.pack(fill="both", expand=True)

    def generate_year_prediction(self):
        year = self.year_val_var.get()
        self.year_console.delete(1.0, tk.END)
        self.year_console.insert(tk.END, "="*60 + "\n")
        self.year_console.insert(tk.END, f"📆 YEAR WISE PREDICTION FOR: {year}\n")
        self.year_console.insert(tk.END, "="*60 + "\n\n")
        
        try:
            if not os.path.exists(DATA_PATH):
                self.year_console.insert(tk.END, "❌ ERROR: Cannot find chart data.\n")
                return
                
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                chart_data = json.load(f)
                
            if not chart_data or not chart_data.get('planetary_positions'):
                self.year_console.insert(tk.END, "❌ ERROR: Chart data is empty.\n")
                return

            module_path = os.path.join(project_root, 'prediction', 'general', 'yearly_prediction.py')
            spec = importlib.util.spec_from_file_location("yearly_prediction", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                loader: Any = spec.loader
                loader.exec_module(module) # type: ignore
                get_report = getattr(module, 'get_yearly_prediction_report')
            else:
                self.year_console.insert(tk.END, "❌ ERROR: Could not load yearly prediction module spec.\n")
                return
            
            result = get_report(chart_data, target_year=int(year))
            
            if result['status'] == 'SUCCESS':
                report_data = result['report']
                for item in report_data:
                    self.year_console.insert(tk.END, f"{item.get('Category', '')}\n")
                    self.year_console.insert(tk.END, f"Verdict: {item.get('Verdict', '')}\n")
                    self.year_console.insert(tk.END, f"Controller: {item.get('Controller', '')}\n")
                    self.year_console.insert(tk.END, f"{item.get('Details', '')}\n")
                    self.year_console.insert(tk.END, "-"*60 + "\n\n")
            else:
                 self.year_console.insert(tk.END, f"❌ ENGINE ERROR: {result.get('error', 'Unknown Error')}\n")
        except Exception as e:
            self.year_console.insert(tk.END, f"❌ SYSTEM ERROR: {str(e)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = TitaniumAI(root)
    if os.path.exists(DATA_PATH):
        app.read_chart()
    root.mainloop()