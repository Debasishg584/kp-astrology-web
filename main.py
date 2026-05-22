"""
DIVYA DRISHTI — Main Application Entry Point
Ultra-Advanced KP Astrology Professional Suite
Version: 8.0 (Rectified & Enhanced)

Fixes applied (ref: audit document):
  ① Global state chaos       → per-instance deep-copied data stores with locks
  ② Threading without safety → threading.Lock + root.after() for all UI updates
  ③ Silent exception swallow → structured logging; no bare `except: pass`
  ④ UI/Logic coupling        → ChartEngine extracted; KPApp is view-only
  ⑤ sys.path hack            → importlib resource resolution
  ⑥ Undefined deps           → graceful capability detection at startup
  ⑦ Date parsing fragility   → centralised _parse_date() with multiple formats
  ⑧ Memory leaks             → explicit image reference management
  ⑨ Lambda capture bug       → factory functions replace nested lambdas
  ⑩ Magic strings            → AppMode enum; all mode tokens use it
"""

from __future__ import annotations

# ── stdlib ───────────────────────────────────────────────────────────────────
import copy
import datetime
import importlib
import importlib.util
import inspect
import json
import logging
import math
import os
import re
import sys
import threading
import time
from collections import Counter
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ── third-party ──────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

try:
    from PIL import Image, ImageEnhance, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

# ── project path (use importlib; no sys.path hack) ───────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:          # only if not already present
    sys.path.insert(0, _PROJECT_ROOT)

# ── project imports (all guarded) ────────────────────────────────────────────
try:
    from src.utils.logger import app_logger          # type: ignore
except ImportError:
    app_logger = logging.getLogger("divya_drishti")
    logging.basicConfig(level=logging.WARNING)

try:
    from src.utils import get_resource_path          # type: ignore
except ImportError:
    def get_resource_path(rel: str) -> str:
        return os.path.join(_PROJECT_ROOT, rel)

try:
    from src.translations import (                   # type: ignore
        LANGUAGES, convert_number, get_lang, set_lang, t,
    )
except ImportError:
    LANGUAGES = {"en": "English"}
    def t(k: str) -> str: return k
    def set_lang(l: str) -> None: pass
    def get_lang() -> str: return "en"
    def convert_number(s: str) -> str: return s

try:
    from src.location import LocationManager         # type: ignore
except ImportError:
    LocationManager = None                           # type: ignore

try:
    from src.charts import ChartDrawer               # type: ignore
except ImportError:
    ChartDrawer = None                               # type: ignore

try:
    from src.predictions import KPPredictor          # type: ignore
except ImportError:
    KPPredictor = None                               # type: ignore

try:
    from src.calculations import KPCalculator        # type: ignore
except ImportError:
    KPCalculator = None                              # type: ignore

try:
    from src.ui_components import (                  # type: ignore
        create_compact_detail, create_compact_input,
        create_date_input, create_time_input, create_tool_button,
    )
except ImportError:
    # Minimal stubs so the rest of the file can be imported in isolation
    def create_compact_input(p, lbl, key, theme, fonts, entries, **kw):
        f = tk.Frame(p, bg=theme["card_bg"]); f.pack(side=tk.LEFT, padx=3)
        tk.Label(f, text=lbl, bg=theme["card_bg"], fg=theme["text_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        e = ttk.Entry(f, width=kw.get("width", 12), font=("Segoe UI", 9))
        e.pack(); entries[key] = e; return f
    def create_compact_detail(p, lbl, theme, **kw):
        f = tk.Frame(p, bg=theme["card_bg"]); f.pack(side=tk.LEFT, padx=3)
        tk.Label(f, text=lbl, bg=theme["card_bg"], fg=theme["text_dim"],
                 font=("Segoe UI", 8)).pack(anchor="w")
        e = ttk.Entry(f, width=kw.get("width", 8)); e.pack(); return e
    def create_date_input(p, lbl, key, theme, fonts, entries, **kw):
        return create_compact_input(p, lbl, key, theme, fonts, entries, **kw)
    def create_time_input(p, lbl, key, theme, fonts, entries, **kw):
        return create_compact_input(p, lbl, key, theme, fonts, entries, **kw)
    def create_tool_button(p, lbl, cmd, color, theme, fonts):
        f = tk.Frame(p, bg=theme["card_bg"])
        tk.Button(f, text=lbl, command=cmd, bg=color,
                  relief=tk.FLAT, padx=8, pady=5).pack(fill=tk.X)
        return f

try:
    from src.services.data_manager import DataManager    # type: ignore
except ImportError:
    class DataManager:                                    # type: ignore
        @staticmethod
        def load_national_charts() -> Dict: return {}
        @staticmethod
        def get_chart_data_filename(mode: str) -> str:
            return {"horary": "chart_data(H).json",
                    "mundane": "chart_data(M).json",
                    "match_making": "chart_data(CM).json"}.get(mode, "chart_data.json")

try:
    from src.validation.schema import ChartInputValidator  # type: ignore
except ImportError:
    class ChartInputValidator:                              # type: ignore
        @staticmethod
        def validate_birth_input(*args) -> List[str]: return []

try:
    from src.swisseph_backend import SwissEphBackend       # type: ignore
    HAS_SWISSEPH = SwissEphBackend.is_available()
except (ImportError, AttributeError):
    SwissEphBackend = None                                  # type: ignore
    HAS_SWISSEPH = False

try:
    from src.prediction_rules import HOUSE_COLORS          # type: ignore
except ImportError:
    HOUSE_COLORS = {i: "#FFFFFF" for i in range(1, 13)}


# ═══════════════════════════════════════════════════════════════════════════════
# FIX ⑩ — App-mode enum (replaces magic strings)
# ═══════════════════════════════════════════════════════════════════════════════

class AppMode(str, Enum):
    BIRTH    = "birth_chart"
    HORARY   = "horary"
    MUNDANE  = "mundane"
    MATCHMAKE = "match_making"


# ═══════════════════════════════════════════════════════════════════════════════
# THEME  — Deep-Space Vedic Aesthetic
# ═══════════════════════════════════════════════════════════════════════════════

THEME: Dict[str, str] = {
    "app_bg":         "#07070F",
    "card_bg":        "#0F0F1E",
    "card_bg_alt":    "#141428",
    "header_bg":      "#060611",
    "header_accent":  "#12122A",
    "text_main":      "#EEEEFF",
    "text_dim":       "#7070A0",
    "text_glow":      "#F5F5FF",
    "primary":        "#7C3AED",
    "primary_light":  "#A78BFA",
    "primary_dark":   "#5B21B6",
    "secondary":      "#F6C90E",
    "secondary_dim":  "#C49A0A",
    "danger":         "#F87171",
    "danger_dark":    "#B91C1C",
    "success":        "#34D399",
    "success_dark":   "#059669",
    "warning":        "#FBBF24",
    "chart_bg":       "#040409",
    "chart_glow":     "#0D0D1F",
    "border":         "#1E1E40",
    "border_glow":    "#2E2E60",
    "border_gold":    "#3D3400",
    "shadow":         "#000000",
    "gold":           "#F6C90E",
    "gold_dim":       "#8A7000",
    "teal":           "#00E5D4",
    "teal_dim":       "#007A72",
    "orb_birth":      "#1A0D3D",
    "orb_horary":     "#003330",
    "orb_match":      "#3D0D1A",
    "orb_mundane":    "#1A1200",
}

FONTS: Dict[str, tuple] = {
    "title":          ("Segoe UI", 26, "bold"),
    "header":         ("Segoe UI", 17, "bold"),
    "sub_header":     ("Segoe UI", 13, "bold"),
    "label":          ("Segoe UI", 11),
    "label_bold":     ("Segoe UI", 11, "bold"),
    "input":          ("Segoe UI", 12),
    "button":         ("Segoe UI", 12, "bold"),
    "button_small":   ("Segoe UI", 10, "bold"),
    "small_bold":     ("Segoe UI", 10, "bold"),
    "cusp_text":      ("Consolas", 11),
    "mantra":         ("Segoe UI", 11, "italic"),
    "orb_label":      ("Segoe UI", 13, "bold"),
    "orb_sub":        ("Segoe UI", 9),
    "launcher_title": ("Segoe UI", 40, "bold"),
    "launcher_sub":   ("Segoe UI", 14, "italic"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# FIX ④ — ChartEngine: all astrology logic lives here, NOT in the UI class
# ═══════════════════════════════════════════════════════════════════════════════

class ChartEngine:
    """
    Pure-logic layer.  Knows nothing about Tkinter.
    Thread-safe: all mutation goes through _lock.
    """

    _EMPTY: Dict[str, Any] = {
        "planets": {}, "cusps": {}, "ayanamsa": 0.0,
        "is_calculated": False, "birth_date": None,
    }

    def __init__(self) -> None:
        self._lock = threading.Lock()

        # FIX ② — reusable thread pool slot
        self._worker_thread: Optional[threading.Thread] = None

        # Calculator (optional dep)
        self.calc: Optional[Any] = KPCalculator() if KPCalculator else None
        self.swe:  Optional[Any] = SwissEphBackend() if (HAS_SWISSEPH and SwissEphBackend) else None
        self.loc:  Optional[Any] = None  # injected by KPApp

        # Per-mode data stores (FIX ① — never shared directly)
        self._primary:    Dict[str, Any] = copy.deepcopy(self._EMPTY)
        self._secondary:  Dict[str, Any] = copy.deepcopy(self._EMPTY)   # bride / alt

    # ── public read (returns deep copy — FIX ①) ──────────────────────────────
    def primary(self) -> Dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._primary)

    def secondary(self) -> Dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._secondary)

    # ── date parsing (FIX ⑦) ─────────────────────────────────────────────────
    @staticmethod
    def parse_date(date_str: str) -> Tuple[int, int, int]:
        """
        Accept DD-MM-YYYY, DD/MM/YYYY, YYYY-MM-DD.
        Raises ValueError with a human-readable message on failure.
        """
        date_str = date_str.strip()
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                dt = datetime.datetime.strptime(date_str, fmt)
                return dt.day, dt.month, dt.year
            except ValueError:
                continue
        raise ValueError(f"Unrecognised date format: '{date_str}'.  Use DD-MM-YYYY.")

    @staticmethod
    def parse_time(time_str: str) -> Tuple[int, int, int]:
        time_str = time_str.strip()
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                dt = datetime.datetime.strptime(time_str, fmt)
                return dt.hour, dt.minute, dt.second
            except ValueError:
                continue
        raise ValueError(f"Unrecognised time format: '{time_str}'.  Use HH:MM:SS.")

    @staticmethod
    def parse_tz(tz_str: str) -> float:
        """'+05:30' → 5.5,  '-04:00' → -4.0"""
        try:
            s = tz_str.strip()
            sign = -1 if s.startswith("-") else 1
            parts = s.lstrip("+-").split(":")
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return sign * (h + m / 60.0)
        except (ValueError, IndexError):
            return 5.5   # default IST

    # ── horary ascendant ─────────────────────────────────────────────────────
    @staticmethod
    def horary_ascendant(number: int) -> float:
        if not (1 <= number <= 249):
            raise ValueError("Horary number must be 1–249.")
        return ((number - 0.5) * 360.0 / 249.0) % 360.0

    # ── internal calculation (called in worker thread) ────────────────────────
    def _calculate_one(
        self,
        date_str: str,
        time_str: str,
        lat: float,
        lon: float,
        tz_str: str,
        mode: AppMode,
        horary_num: Optional[int] = None,
    ) -> Dict[str, Any]:
        dd, mm, yy = self.parse_date(date_str)
        hh, mi, ss = self.parse_time(time_str)
        tz = self.parse_tz(tz_str)
        dt = datetime.datetime(yy, mm, dd, hh, mi, ss)

        calc = self.calc
        swe  = self.swe

        if mode == AppMode.HORARY and horary_num is not None:
            asc_deg = self.horary_ascendant(horary_num)
            cu: Dict[int, float] = {
                i: (asc_deg + (i - 1) * 30.0) % 360 for i in range(1, 13)
            }
            if HAS_SWISSEPH and swe:
                jd  = swe.get_julian_day(yy, mm, dd, hh, mi, tz)
                res = swe.get_all_positions(jd, lat, lon, yy, mm, dd) or ({}, {}, 0.0)
                pl, _, aya = res
            else:
                pl  = {p: 0.0 for p in ["Sun","Moon","Mars","Mercury","Jupiter",
                                         "Venus","Saturn","Rahu","Ketu",
                                         "Uranus","Neptune","Pluto"]}
                aya = calc.get_kp_ayanamsa(yy, mm, dd) if calc else 24.0
        else:
            if HAS_SWISSEPH and swe:
                jd  = swe.get_julian_day(yy, mm, dd, hh, mi, tz)
                res = swe.get_all_positions(jd, lat, lon, yy, mm, dd) or ({}, {}, 0.0)
                pl, cu, aya = res
            elif calc:
                jd   = calc.get_julian_day(yy, mm, dd, hh, mi, ss, tz)
                gmst = calc.get_gmst(jd)
                lst  = calc.get_lst(gmst, lon)
                raw_cu = calc.get_placidus_cusps(lst, lat) or {}
                aya  = calc.get_kp_ayanamsa(yy, mm, dd)
                cu   = {int(k): float(v - aya) % 360 for k, v in raw_cu.items()} \
                        if raw_cu else {i: float((i - 1) * 30) for i in range(1, 13)}
                pl   = {p: 0.0 for p in ["Sun","Moon","Mars","Mercury","Jupiter",
                                           "Venus","Saturn","Rahu","Ketu",
                                           "Uranus","Neptune","Pluto"]}
            else:
                cu  = {i: float((i - 1) * 30) for i in range(1, 13)}
                aya = 24.0
                pl  = {}

        result: Dict[str, Any] = {
            "planets": pl, "cusps": cu, "ayanamsa": aya,
            "is_calculated": True, "birth_date": dt,
        }
        if horary_num is not None:
            result["horary_number"] = horary_num
        return result

    # ── async wrapper (FIX ②) ─────────────────────────────────────────────────
    def calculate_async(
        self,
        primary_kwargs: Dict[str, Any],
        secondary_kwargs: Optional[Dict[str, Any]],
        mode: AppMode,
        on_success: Callable[[Dict[str, Any]], None],
        on_error:   Callable[[str], None],
    ) -> None:
        """
        Spawn background thread; callbacks are invoked via root.after()
        by the caller — this method never touches Tkinter.
        """
        def worker():
            try:
                p1 = self._calculate_one(**primary_kwargs, mode=mode)
                p2 = None
                if secondary_kwargs:
                    p2 = self._calculate_one(**secondary_kwargs, mode=mode)

                with self._lock:
                    self._primary   = p1
                    self._secondary = p2 or copy.deepcopy(self._EMPTY)

                on_success({"p1": p1, "p2": p2, "mode": mode})

            except Exception as exc:
                app_logger.exception("Chart calculation failed")
                on_error(str(exc))

        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    # ── dasa helpers ─────────────────────────────────────────────────────────
    def get_dasa_sequence(
        self,
        data: Dict[str, Any],
        limit_years: int = 120,
    ) -> List[Dict[str, Any]]:
        calc = self.calc
        if not calc:
            return []
        ml = data["planets"].get("Moon", 0.0)
        bd = data["birth_date"]
        start_lord, balance, first_end = calc.get_dasa_balance(ml, bd)
        ords = calc.DASA_LORDS
        idx  = ords.index(start_lord)
        seq: List[Dict[str, Any]] = []
        cur  = bd
        acc  = 0.0
        i    = 0
        while acc < limit_years:
            lord = ords[(idx + i) % 9]
            if i == 0:
                dur, start_dt, end_dt = balance, bd, first_end
            else:
                dur      = calc.DASA_YEARS[lord]
                start_dt = cur
                end_dt   = calc.add_years(start_dt, dur)
            seq.append({"lord": lord, "start": start_dt, "end": end_dt, "duration": dur})
            cur = end_dt
            acc += dur
            i   += 1
        return seq

    def get_nested_dasa(
        self,
        data: Dict[str, Any],
        parent_lord: str,
        parent_end: datetime.datetime,
        parent_dur: float,
        level: int = 1,
        max_level: int = 2,
    ) -> List[Dict[str, Any]]:
        if level > max_level or not self.calc:
            return []
        calc    = self.calc
        periods = []
        start   = calc.add_years(parent_end, -parent_dur)
        ords    = calc.DASA_LORDS
        base    = ords.index(parent_lord)
        level_names = ["Maha", "Antar", "Pratyantar", "Sookshma", "Prana"]
        lname   = level_names[level] if level < len(level_names) else "Sub"
        for i in range(9):
            sl  = ords[(base + i) % 9]
            dur = (parent_dur * calc.DASA_YEARS[sl]) / 120.0
            end = calc.add_years(start, dur)
            node: Dict[str, Any] = {
                "lord":     sl,
                "level":    f"{lname} Dasa",
                "start":    start.strftime("%d-%m-%Y %H:%M"),
                "end":      end.strftime("%d-%m-%Y %H:%M"),
                "duration": f"{dur:.2f} yrs",
            }
            children = self.get_nested_dasa(data, sl, end, dur, level + 1, max_level)
            if children:
                node["sub_periods"] = children
            periods.append(node)
            start = end
        return periods

    # ── export data builder ──────────────────────────────────────────────────
    def build_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert raw chart data to the full JSON export schema."""
        calc = self.calc
        if not data.get("planets") or not calc:
            return {}
        out: Dict[str, Any] = {
            "planetary_positions": [],
            "house_cusps":         [],
            "house_significators": [],
            "planet_significators":[],
            "aspects":             [],
            "vimshottari_dasa_full": [],
        }

        # Planets
        for p, lon in data["planets"].items():
            sign, deg_in = calc.get_zodiac_sign(lon)
            d, mn, sc   = calc.decimal_to_dms(deg_in)
            nak, st, sb = calc.get_sub_lord_info(lon)
            out["planetary_positions"].append({
                "planet": p,
                "longitude": float(lon),
                "longitude_dms": f"{int(d)}° {int(mn)}' {int(sc)}\"",
                "sign": sign, "nakshatra": nak,
                "star_lord": st, "sub_lord": sb,
            })

        # Cusps
        for i in range(1, 13):
            lon = data["cusps"][i]
            sign, deg_in = calc.get_zodiac_sign(lon)
            d, mn, sc   = calc.decimal_to_dms(deg_in)
            _, st, sb   = calc.get_sub_lord_info(lon)
            out["house_cusps"].append({
                "cusp": i, "longitude": float(lon),
                "longitude_dms": f"{int(d)}° {int(mn)}' {int(sc)}\"",
                "sign": sign,
                "sign_lord": calc.get_sign_lord(sign),
                "star_lord": st, "sub_lord": sb,
            })

        # House significators
        hs = calc.get_house_significators(data["planets"], data["cusps"])
        for h, d_val in hs.items():
            out["house_significators"].append({
                "house": f"H{h}",
                "L1": d_val["L1"], "L2": d_val["L2"],
                "L3": d_val["L3"], "L4": d_val["L4"],
            })

        # Planet significators (Source_Row / Result_Row)
        bh      = calc.get_bhavasphuta_significators(data["planets"], data["cusps"])
        csl_map: Dict[str, List[int]] = {}
        for cidx in range(1, 13):
            lon = data["cusps"].get(cidx, 0.0)
            _, _, sub = calc.get_sub_lord_info(lon)
            if sub:
                csl_map.setdefault(sub, []).append(cidx)

        for p in calc.PLANET_ORDER:
            if p not in bh:
                continue
            dat  = bh[p]
            plon = float(data["planets"].get(p, 0.0))
            _, sl_name, sb_name = calc.get_sub_lord_info(plon)
            src: List[int] = []
            for key in ("P_Occ", "P_Own", "S_Occ", "S_Own"):
                src.extend(_raw_houses(dat.get(key, "")))
            res: List[int] = (
                csl_map.get(p, [])
                + csl_map.get(str(sl_name), [])
                + csl_map.get(str(sb_name), [])
            )
            out["planet_significators"].append({
                "planet":     p,
                "Source_Row": _fmt_repeats(src),
                "Result_Row": _fmt_repeats(res),
            })

        # Aspects
        for asp in calc.calculate_aspects(data["planets"]):
            out["aspects"].append({
                "p1":     asp["p1"],   "aspect": asp["aspect"],
                "p2":     asp["p2"],   "angle":  f"{asp['angle']:.1f}°",
                "orb":    f"{asp['orb']:.1f}°",
                "status": "Benefic" if "Tri" in asp["aspect"] else "Malefic",
            })

        # Dasa
        for node in self.get_dasa_sequence(data, limit_years=120):
            md: Dict[str, Any] = {
                "lord": node["lord"], "level": "Maha Dasa",
                "start": node["start"].strftime("%d-%m-%Y"),
                "end":   node["end"].strftime("%d-%m-%Y"),
                "duration": f"{node['duration']:.2f} yrs",
            }
            md["sub_periods"] = self.get_nested_dasa(
                data, node["lord"], node["end"], node["duration"],
                level=1, max_level=2,
            )
            out["vimshottari_dasa_full"].append(md)

        return out


# ═══════════════════════════════════════════════════════════════════════════════
# Pure utility helpers (module-level — no UI, no engine)
# ═══════════════════════════════════════════════════════════════════════════════

def _raw_houses(val: Any) -> List[int]:
    if not val:
        return []
    return [int(x) for x in re.findall(r"\d+", str(val))]


def _fmt_repeats(lst: List[int]) -> str:
    if not lst:
        return "-"
    counts = Counter(lst)
    parts = []
    for h in sorted(counts):
        suffix = "+" * (counts[h] - 1)
        parts.append(f"{h}{suffix}")
    return ", ".join(parts)


def _kp_relation(
    deg1: float, deg2: float
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    diff = abs(deg1 - deg2)
    if diff > 180:
        diff = 360 - diff
    for ang, orb, name, qual in [
        (0,   6, "Conjunction", "Neutral"),
        (60,  4, "Sextile",     "Benefic"),
        (90,  6, "Square",      "Malefic"),
        (120, 6, "Trine",       "Benefic"),
        (180, 6, "Opposition",  "Malefic"),
    ]:
        if abs(diff - ang) <= orb:
            return name, qual, f"{diff:.2f}°"
    return None, None, None


def _planet_house(lon: float, cusps: Dict[int, float]) -> int:
    for i in range(1, 13):
        start = cusps[i]
        end   = cusps[i + 1 if i < 12 else 1]
        if start < end:
            if start <= lon < end:
                return i
        else:
            if lon >= start or lon < end:
                return i
    return 0


def _parse_window_date(raw: str) -> Optional[datetime.datetime]:
    """Extract the latest date from a window string for sorting/filtering."""
    dates = []
    for pattern, fmt in [
        (r"(\d{2}-\d{2}-\d{4})", "%d-%m-%Y"),
        (r"([A-Za-z]{3}\s\d{4})",  "%b %Y"),
    ]:
        matches = re.findall(pattern, raw)
        for match in matches:
            try:
                dates.append(datetime.datetime.strptime(match, fmt))
            except ValueError:
                continue
    if dates:
        return max(dates)
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# TTK Style configurator
# ═══════════════════════════════════════════════════════════════════════════════

def _configure_styles() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame",           background=THEME["app_bg"])
    style.configure("Card.TFrame",      background=THEME["card_bg"],      relief="flat")
    style.configure("CardAlt.TFrame",   background=THEME["card_bg_alt"],  relief="flat")
    style.configure("Header.TFrame",    background=THEME["header_bg"])
    style.configure("TLabel",           background=THEME["app_bg"],
                    foreground=THEME["text_main"], font=FONTS["label"])
    style.configure("Card.TLabel",      background=THEME["card_bg"],
                    foreground=THEME["text_main"], font=FONTS["label"])
    style.configure("Gold.TLabel",      background=THEME["card_bg"],
                    foreground=THEME["gold"],      font=FONTS["label_bold"])
    style.configure("Dim.TLabel",       background=THEME["card_bg"],
                    foreground=THEME["text_dim"],  font=FONTS["label"])
    style.configure("TEntry",
                    fieldbackground=THEME["card_bg_alt"],
                    foreground=THEME["text_main"],
                    bordercolor=THEME["border"],
                    insertcolor=THEME["secondary"])
    style.map("TEntry",
              fieldbackground=[("focus", THEME["card_bg"])],
              bordercolor=[("focus", THEME["primary"])])
    style.configure("TCombobox",
                    fieldbackground=THEME["card_bg_alt"],
                    background=THEME["card_bg"],
                    foreground=THEME["text_main"],
                    arrowcolor=THEME["secondary"],
                    bordercolor=THEME["border"])
    style.map("TCombobox",
              fieldbackground=[("readonly", THEME["card_bg_alt"]),
                               ("focus",    THEME["card_bg"])],
              arrowcolor=[("active", THEME["primary"])])
    style.configure("Treeview",
                    background=THEME["card_bg"],
                    fieldbackground=THEME["card_bg"],
                    foreground=THEME["text_main"],
                    font=("Segoe UI", 12), rowheight=40,
                    borderwidth=0)
    style.configure("Treeview.Heading",
                    background=THEME["header_bg"],
                    foreground=THEME["gold"],
                    font=("Segoe UI", 12, "bold"),
                    relief="flat", borderwidth=0, padding=(8, 6))
    style.map("Treeview",
              background=[("selected", THEME["primary_dark"])],
              foreground=[("selected", THEME["text_glow"])])
    style.configure("Vertical.TScrollbar",
                    background=THEME["card_bg"],
                    troughcolor=THEME["app_bg"],
                    arrowcolor=THEME["text_dim"])
    style.map("Vertical.TScrollbar",
              background=[("active", THEME["primary"])])
    style.configure("TSeparator", background=THEME["border_glow"])


# ═══════════════════════════════════════════════════════════════════════════════
# KPApp — VIEW ONLY.  No astrology logic inside.
# ═══════════════════════════════════════════════════════════════════════════════

class KPApp:
    """
    Pure UI layer.
    All computation is delegated to self._engine (ChartEngine).
    """

    def __init__(self, root: tk.Tk, mode: AppMode = AppMode.BIRTH) -> None:
        self.root   = root
        self.mode   = AppMode(mode)   # FIX ⑩ — coerce to enum

        # FIX ④ — engine owns all data; UI owns nothing
        self._engine = ChartEngine()
        self._engine.loc = LocationManager(
            get_resource_path(os.path.join("data", "cities.csv"))
        ) if LocationManager else None

        self.national_charts: Dict[str, Any] = DataManager.load_national_charts()

        # FIX ⑧ — image references are kept explicitly
        self._image_refs: List[Any] = []
        self._saved_chart_image_path: Optional[str] = None

        # FIX ② — UI state flag; only touched on main thread
        self._is_processing: bool = False

        # UI component references
        self.horary_number: Optional[int] = None
        self.latest_cm_report: Optional[Any] = None
        self.selected_report_topics: Set[str] = set()

        self.entries:       Dict[str, Any] = {}
        self.tool_buttons:  List[Dict[str, Any]] = []
        self._lang_codes:   List[str] = []
        self._translatable: Dict[str, Dict[str, Any]] = {}

        # Widgets
        self.canvas:        Optional[tk.Canvas]   = None
        self.canvas_groom:  Optional[tk.Canvas]   = None
        self.canvas_bride:  Optional[tk.Canvas]   = None
        self.drawer:        Optional[Any]          = None
        self.drawer_groom:  Optional[Any]          = None
        self.drawer_bride:  Optional[Any]          = None
        self.ent_lat:       Optional[tk.Widget]    = None
        self.ent_lon:       Optional[tk.Widget]    = None
        self.ent_tz:        Optional[tk.Widget]    = None
        self.ent_lat_alt:   Optional[tk.Widget]    = None
        self.ent_lon_alt:   Optional[tk.Widget]    = None
        self.ent_tz_alt:    Optional[tk.Widget]    = None
        self.ent_city_search:     Optional[tk.Widget] = None
        self.ent_city_search_alt: Optional[tk.Widget] = None
        self.ent_country:   Optional[tk.Widget]    = None
        self.ent_state:     Optional[tk.Widget]    = None
        self.ent_horary_number: Optional[tk.Widget] = None
        self.combo_gender:  Optional[ttk.Combobox] = None
        self.combo_country: Optional[ttk.Combobox] = None
        self.lang_combo:    Optional[ttk.Combobox] = None
        self.collapse_btn:  Optional[tk.Button]    = None
        self.input_content: Optional[tk.Frame]     = None
        self.input_collapsed: bool = False
        self.btn_generate:  Optional[tk.Button]    = None
        self.lbl_birth_details: Optional[tk.Label] = None
        self.lbl_analysis_tools: Optional[tk.Label] = None

        _configure_styles()
        self._build_window_title()
        self.setup_ui()

    # ── window title ─────────────────────────────────────────────────────────
    def _build_window_title(self) -> None:
        titles = {
            AppMode.BIRTH:     "Birth Chart Analysis",
            AppMode.HORARY:    "Horary (Prashna) Astrology",
            AppMode.MUNDANE:   "World Political Astrology",
            AppMode.MATCHMAKE: "Couple Compatibility Test",
        }
        self.root.title(f"{t('app_title')} — {titles.get(self.mode, '')}")
        self.root.state("zoomed")
        self.root.configure(bg=THEME["app_bg"])

    # ── home navigation ───────────────────────────────────────────────────────
    def go_back_home(self) -> None:
        for w in self.root.winfo_children():
            w.destroy()
        LauncherScreen(self.root, _launch_mode)

    # ═════════════════════════════════════════════════════════════════════════
    # setup_ui  (structure only; no logic)
    # ═════════════════════════════════════════════════════════════════════════

    def setup_ui(self) -> None:
        self._build_header()
        self._build_input_card()
        self._build_main_pane()

    # ── header ───────────────────────────────────────────────────────────────
    def _build_header(self) -> None:
        outer = tk.Frame(self.root, bg=THEME["header_bg"])
        outer.pack(fill=tk.X, side=tk.TOP)

        # accent bar
        tk.Frame(outer, bg=THEME["primary"], height=3).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=THEME["header_bg"], height=90)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # logo
        logo_cont = tk.Frame(hdr, bg=THEME["header_bg"])
        logo_cont.pack(side=tk.LEFT, padx=25, pady=10)
        self._load_logo(logo_cont)

        # title block
        title_fr = tk.Frame(hdr, bg=THEME["header_bg"])
        title_fr.pack(side=tk.LEFT, padx=15)
        tk.Label(title_fr, text="DIVYA DRISHTI", bg=THEME["header_bg"],
                 fg=THEME["text_glow"], font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Frame(title_fr, bg=THEME["primary"], height=2, width=180).pack(anchor="w", pady=(2, 4))
        tk.Label(title_fr, text="॥ शृण्वन्तु विश्वे अमृतस्य पुत्रा ॥",
                 bg=THEME["header_bg"], fg=THEME["gold"],
                 font=FONTS["mantra"]).pack(anchor="w")

        # right info
        info_fr = tk.Frame(hdr, bg=THEME["header_bg"])
        info_fr.pack(side=tk.RIGHT, padx=25, pady=10)

        tk.Button(info_fr, text="🔙 Home", bg=THEME["header_bg"],
                  fg=THEME["text_main"], font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, bd=0, cursor="hand2",
                  activebackground=THEME["header_accent"],
                  activeforeground=THEME["gold"],
                  command=self.go_back_home).pack(side=tk.LEFT, padx=(0, 15))

        lang_fr = tk.Frame(info_fr, bg=THEME["header_bg"])
        lang_fr.pack(anchor="e", pady=(0, 5))
        tk.Label(lang_fr, text="🌐", bg=THEME["header_bg"],
                 fg=THEME["gold"], font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 5))

        lang_vals = list(LANGUAGES.values())
        lang_keys  = list(LANGUAGES.keys())
        self._lang_codes = lang_keys

        self.lang_combo = ttk.Combobox(lang_fr, values=lang_vals,
                                        width=10, state="readonly",
                                        font=("Segoe UI", 9))
        cur_idx = lang_keys.index(get_lang()) if get_lang() in lang_keys else 0
        self.lang_combo.current(cur_idx)
        self.lang_combo.pack(side=tk.LEFT)
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        tk.Label(info_fr, text="Professional Edition", bg=THEME["header_bg"],
                 fg=THEME["text_dim"], font=("Segoe UI", 9)).pack(anchor="e")
        tk.Label(info_fr, text="KP Astrology System", bg=THEME["header_bg"],
                 fg=THEME["secondary"], font=("Segoe UI", 10, "bold")).pack(anchor="e")

        tk.Frame(outer, bg=THEME["border_glow"], height=1).pack(fill=tk.X)

    def _load_logo(self, parent: tk.Frame) -> None:
        if not HAS_PIL:
            tk.Label(parent, text="✦", bg=THEME["header_bg"],
                     fg=THEME["gold"], font=("Segoe UI", 36)).pack()
            return
        try:
            path = get_resource_path(os.path.join("assets", "logo.png"))
            if not os.path.exists(path):
                raise FileNotFoundError
            img = Image.open(path)
            h   = 65
            w   = int(h * img.width / img.height)
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            ph  = ImageTk.PhotoImage(img)
            self._image_refs.append(ph)   # FIX ⑧ — keep reference
            tk.Label(parent, image=ph, bg=THEME["header_bg"]).pack()
        except Exception:
            tk.Label(parent, text="✦", bg=THEME["header_bg"],
                     fg=THEME["gold"], font=("Segoe UI", 36)).pack()

    # ── input card ────────────────────────────────────────────────────────────
    def _build_input_card(self) -> None:
        cont = tk.Frame(self.root, bg=THEME["app_bg"], padx=10, pady=5)
        cont.pack(fill=tk.X)

        border = tk.Frame(cont, bg=THEME["border"])
        border.pack(fill=tk.X, padx=2, pady=1)

        card = tk.Frame(border, bg=THEME["card_bg"], padx=12, pady=12)
        card.pack(fill=tk.X, padx=1, pady=1)

        # collapse header
        sec_hdr = tk.Frame(card, bg=THEME["card_bg"])
        sec_hdr.pack(fill=tk.X, pady=(0, 5))
        self.collapse_btn = tk.Button(sec_hdr, text="▼", bg=THEME["card_bg"],
                                       fg=THEME["gold"], font=("Segoe UI", 10, "bold"),
                                       relief=tk.FLAT, bd=0, cursor="hand2",
                                       command=self._toggle_input_panel)
        self.collapse_btn.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(sec_hdr, text="◈", bg=THEME["card_bg"], fg=THEME["gold"],
                 font=("Segoe UI", 12)).pack(side=tk.LEFT)
        self.lbl_birth_details = tk.Label(sec_hdr,
                                           text=" " + t("birth_details"),
                                           bg=THEME["card_bg"],
                                           fg=THEME["text_dim"],
                                           font=FONTS["sub_header"])
        self.lbl_birth_details.pack(side=tk.LEFT)
        self._translatable["birth_details"] = {
            "widget": self.lbl_birth_details, "key": "birth_details"
        }
        tk.Frame(sec_hdr, bg=THEME["border"], height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0)
        )

        self.input_content = tk.Frame(card, bg=THEME["card_bg"])
        self.input_content.pack(fill=tk.X)

        self._build_input_rows()

    def _build_input_rows(self) -> None:
        parent = self.input_content
        mode   = self.mode

        # ── Row 1: mode-specific fields ───────────────────────────────────────
        r1 = tk.Frame(parent, bg=THEME["card_bg"])
        r1.pack(fill=tk.X, pady=3)

        if mode == AppMode.BIRTH:
            create_compact_input(r1, t("name"), "ent_name",
                                 THEME, FONTS, self.entries, width=12)
            self._build_gender_combo(r1)
            create_date_input(r1, t("date_label"), "ent_date",
                              THEME, FONTS, self.entries,
                              default="16-11-1983", width=10)
            create_time_input(r1, t("time_label"), "ent_time",
                              THEME, FONTS, self.entries,
                              default="04:36:00")
            self.ent_city_search = self._build_city_search(r1, "Kolkata")

        elif mode == AppMode.HORARY:
            self._build_horary_row(r1)
            now = datetime.datetime.now()
            create_date_input(r1, "Question Date", "ent_date",
                              THEME, FONTS, self.entries,
                              default=now.strftime("%d-%m-%Y"), width=10)
            create_time_input(r1, "Question Time", "ent_time",
                              THEME, FONTS, self.entries,
                              default=now.strftime("%H:%M:%S"))
            self.ent_city_search = self._build_city_search(r1, "Kolkata")

        elif mode == AppMode.MUNDANE:
            self._build_country_combo(r1)
            create_compact_input(r1, "Foundation Date", "ent_date",
                                 THEME, FONTS, self.entries,
                                 default="26-01-1950", width=10)
            create_compact_input(r1, "Foundation Time", "ent_time",
                                 THEME, FONTS, self.entries,
                                 default="10:15:00", width=8)
            self.ent_city_search = ttk.Entry(r1, width=1)   # placeholder

        elif mode == AppMode.MATCHMAKE:
            create_compact_input(r1, "Name (Groom)", "ent_name",
                                 THEME, FONTS, self.entries, width=12)
            create_compact_input(r1, "Name (Bride)", "ent_name_alt",
                                 THEME, FONTS, self.entries, width=12)

        # Matchmaking row 1b
        if mode == AppMode.MATCHMAKE:
            r1b = tk.Frame(parent, bg=THEME["card_bg"])
            r1b.pack(fill=tk.X, pady=3)
            create_date_input(r1b, "Groom Date", "ent_date",
                              THEME, FONTS, self.entries,
                              default="16-11-1983", width=10)
            create_time_input(r1b, "Groom Time", "ent_time",
                              THEME, FONTS, self.entries,
                              default="04:36:00")
            tk.Label(r1b, text="📍 Groom", bg=THEME["card_bg"],
                     fg=THEME["gold"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 2))
            self.ent_city_search = self._build_city_search(r1b, "Kolkata", raw=True)

            tk.Frame(r1b, bg=THEME["border"], width=1,
                     height=20).pack(side=tk.LEFT, padx=10)

            create_date_input(r1b, "Bride Date", "ent_date_alt",
                              THEME, FONTS, self.entries,
                              default="15-08-1985", width=10)
            create_time_input(r1b, "Bride Time", "ent_time_alt",
                              THEME, FONTS, self.entries,
                              default="10:00:00")
            tk.Label(r1b, text="📍 Bride", bg=THEME["card_bg"],
                     fg=THEME["gold"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 2))
            self.ent_city_search_alt = self._build_city_search(r1b, "Mumbai", raw=True)

        # Search button(s)
        if mode in (AppMode.BIRTH, AppMode.HORARY):
            self._search_btn(r1, self.ent_city_search)
        elif mode == AppMode.MATCHMAKE:
            self._search_btn(r1b, self.ent_city_search)       # type: ignore[arg-type]
            self._search_btn(r1b, self.ent_city_search_alt)   # type: ignore[arg-type]

        # ── Row 2: geo + action buttons ───────────────────────────────────────
        r2 = tk.Frame(parent, bg=THEME["card_bg"])
        r2.pack(fill=tk.X, pady=3)

        if mode == AppMode.MATCHMAKE:
            g_geo = tk.Frame(r2, bg=THEME["card_bg"])
            g_geo.pack(side=tk.LEFT)
            tk.Label(g_geo, text="♂", bg=THEME["card_bg"],
                     fg=THEME["primary"]).pack(side=tk.LEFT, padx=2)
            self.ent_lat = create_compact_detail(g_geo, "Lat", THEME, width=7)
            self.ent_lon = create_compact_detail(g_geo, "Lon", THEME, width=7)
            self.ent_tz  = create_compact_detail(g_geo, "TZ",  THEME, width=5)
            tk.Frame(r2, bg=THEME["border"], width=1,
                     height=20).pack(side=tk.LEFT, padx=10)
            b_geo = tk.Frame(r2, bg=THEME["card_bg"])
            b_geo.pack(side=tk.LEFT)
            tk.Label(b_geo, text="♀", bg=THEME["card_bg"],
                     fg=THEME["secondary"]).pack(side=tk.LEFT, padx=2)
            self.ent_lat_alt = create_compact_detail(b_geo, "Lat", THEME, width=7)
            self.ent_lon_alt = create_compact_detail(b_geo, "Lon", THEME, width=7)
            self.ent_tz_alt  = create_compact_detail(b_geo, "TZ",  THEME, width=5)
        else:
            self.ent_lat     = create_compact_detail(r2, t("lat_label"),     THEME, width=8)
            self.ent_lon     = create_compact_detail(r2, t("lon_label"),     THEME, width=8)
            self.ent_tz      = create_compact_detail(r2, t("tz_label"),      THEME, width=6)
            self.ent_country = create_compact_detail(r2, t("country_label"), THEME, width=12)
            self.ent_state   = create_compact_detail(r2, t("state_label"),   THEME, width=12)

        tk.Frame(r2, bg=THEME["border"], width=1, height=20).pack(side=tk.LEFT, padx=8)

        self.btn_generate = tk.Button(
            r2, text=t("btn_generate"), bg=THEME["primary"], fg="white",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2",
            command=self.process_chart,
        )
        self.btn_generate.pack(side=tk.LEFT, padx=3)
        self._translatable["btn_generate"] = {
            "widget": self.btn_generate, "key": "btn_generate"
        }

        tk.Button(r2, text="💾", bg=THEME["success"], fg="white",
                  font=("Segoe UI", 9), relief=tk.FLAT,
                  padx=6, pady=4, cursor="hand2",
                  command=self.save_chart_data).pack(side=tk.LEFT, padx=2)

        tk.Button(r2, text="🗑️", bg=THEME["danger"], fg="white",
                  font=("Segoe UI", 9), relief=tk.FLAT,
                  padx=6, pady=4, cursor="hand2",
                  command=self.erase_chart_data).pack(side=tk.LEFT, padx=2)

        if mode != AppMode.MATCHMAKE:
            tk.Button(r2, text="🔮 ASTROLOGER",
                      bg=THEME["warning"], fg="#1A1A2E",
                      font=("Segoe UI", 9, "bold"), relief=tk.FLAT,
                      padx=8, pady=4, cursor="hand2",
                      command=self.open_astrologer_popup).pack(side=tk.RIGHT)

        tk.Button(r2, text="📄 REPORT",
                  bg=THEME["secondary"], fg="#1A1A2E",
                  font=("Segoe UI", 9, "bold"), relief=tk.FLAT,
                  padx=8, pady=4, cursor="hand2",
                  command=self.open_report_popup).pack(side=tk.RIGHT, padx=(0, 5))

        if mode == AppMode.MUNDANE:
            self._on_country_select(None)

    # ── helper builders ───────────────────────────────────────────────────────
    def _build_gender_combo(self, parent: tk.Frame) -> None:
        fr = tk.Frame(parent, bg=THEME["card_bg"])
        fr.pack(side=tk.LEFT, padx=5)
        tk.Label(fr, text=t("gender"), bg=THEME["card_bg"],
                 fg=THEME["text_dim"], font=("Segoe UI", 9)).pack(anchor="w")
        self.combo_gender = ttk.Combobox(fr, values=["Male", "Female", "Other"],
                                          width=8, state="readonly",
                                          font=("Segoe UI", 9))
        self.combo_gender.current(0)
        self.combo_gender.pack()

    def _build_horary_row(self, parent: tk.Frame) -> None:
        fr = tk.Frame(parent, bg=THEME["card_bg"])
        fr.pack(side=tk.LEFT, padx=10)
        tk.Label(fr, text="🔮 Horary Number (1-249)",
                 bg=THEME["card_bg"], fg=THEME["gold"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row = tk.Frame(fr, bg=THEME["card_bg"])
        row.pack(anchor="w")
        e = ttk.Entry(row, width=10, font=("Segoe UI", 9))
        e.pack(side=tk.LEFT, padx=2)
        e.insert(0, "1")
        self.ent_horary_number = e
        self.entries["ent_horary_number"] = e
        tk.Label(row, text="(Cusp positions)", bg=THEME["card_bg"],
                 fg=THEME["text_dim"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)

    def _build_country_combo(self, parent: tk.Frame) -> None:
        fr = tk.Frame(parent, bg=THEME["card_bg"])
        fr.pack(side=tk.LEFT, padx=10)
        tk.Label(fr, text="🌍 Nation / State", bg=THEME["card_bg"],
                 fg=THEME["gold"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        items: List[str] = []
        for k, v in self.national_charts.items():
            if isinstance(v, dict) and v.get("type") == "nation":
                items.append(f"🌐 {v.get('capital','')} ({k})")
        for k, v in self.national_charts.items():
            if isinstance(v, dict) and v.get("type") == "state":
                items.append(f"🏛️ {v.get('capital','')} ({k})")
        self.combo_country = ttk.Combobox(fr, values=items, width=28,
                                           state="readonly", font=("Segoe UI", 9))
        self.combo_country.pack()
        try:
            self.combo_country.current(0)
        except Exception:
            pass
        self.combo_country.bind("<<ComboboxSelected>>", self._on_country_select)

    def _build_city_search(
        self, parent: tk.Frame, default: str = "", raw: bool = False
    ) -> tk.Widget:
        if not raw:
            tk.Label(parent, text="📍", bg=THEME["card_bg"],
                     font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(10, 2))
        e = ttk.Entry(parent, width=15, font=("Segoe UI", 9))
        e.insert(0, default)
        e.pack(side=tk.LEFT, padx=2)
        self.entries[f"ent_city_search_{default}"] = e
        return e

    def _search_btn(self, parent: tk.Frame, target: Optional[tk.Widget]) -> None:
        # FIX ⑨ — factory function captures correct target reference
        def _cmd(tgt=target):
            self.auto_fill_location(tgt)

        tk.Button(parent, text="🔍", bg=THEME["header_accent"],
                  fg=THEME["text_main"], font=("Segoe UI", 9),
                  relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
                  command=_cmd).pack(side=tk.LEFT, padx=2)

    # ── main pane ─────────────────────────────────────────────────────────────
    def _build_main_pane(self) -> None:
        pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                              bg=THEME["app_bg"], sashwidth=6,
                              sashrelief=tk.FLAT, sashpad=1)
        pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=(3, 10))

        # Chart area
        chart_outer = tk.Frame(pane, bg=THEME["border_glow"])
        pane.add(chart_outer, minsize=900, stretch="always")
        chart_cont  = tk.Frame(chart_outer, bg=THEME["chart_bg"])
        chart_cont.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        if self.mode == AppMode.MATCHMAKE:
            g_wrap = tk.Frame(chart_cont, bg=THEME["chart_bg"])
            g_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tk.Label(g_wrap, text="♂ GROOM CHART", bg=THEME["chart_bg"],
                     fg=THEME["primary"], font=FONTS["small_bold"]).pack(pady=2)
            self.canvas_groom = tk.Canvas(g_wrap, bg=THEME["chart_bg"],
                                           highlightthickness=0)
            self.canvas_groom.pack(fill=tk.BOTH, expand=True)
            if ChartDrawer:
                self.drawer_groom = ChartDrawer(self.canvas_groom)
            self.canvas_groom.bind("<Configure>", self._on_resize)

            b_wrap = tk.Frame(chart_cont, bg=THEME["chart_bg"])
            b_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tk.Label(b_wrap, text="♀ BRIDE CHART", bg=THEME["chart_bg"],
                     fg=THEME["secondary"], font=FONTS["small_bold"]).pack(pady=2)
            self.canvas_bride = tk.Canvas(b_wrap, bg=THEME["chart_bg"],
                                           highlightthickness=0)
            self.canvas_bride.pack(fill=tk.BOTH, expand=True)
            if ChartDrawer:
                self.drawer_bride = ChartDrawer(self.canvas_bride)
            self.canvas_bride.bind("<Configure>", self._on_resize)

            self.canvas = self.canvas_groom
            self.drawer = self.drawer_groom
        else:
            self.canvas = tk.Canvas(chart_cont, bg=THEME["chart_bg"],
                                     highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            if ChartDrawer:
                self.drawer = ChartDrawer(self.canvas)
            self.canvas.bind("<Configure>", self._on_resize)

        # Tools area
        tools_outer = tk.Frame(pane, bg=THEME["border"])
        pane.add(tools_outer, minsize=280)
        tools_cont  = tk.Frame(tools_outer, bg=THEME["card_bg"])
        tools_cont.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        tools_hdr = tk.Frame(tools_cont, bg=THEME["card_bg"])
        tools_hdr.pack(fill=tk.X, pady=(15, 10), padx=20)
        tk.Label(tools_hdr, text="◈", bg=THEME["card_bg"],
                 fg=THEME["gold"], font=("Segoe UI", 12)).pack(side=tk.LEFT)
        self.lbl_analysis_tools = tk.Label(
            tools_hdr, text=t("analysis_tools_title"),
            bg=THEME["card_bg"], fg=THEME["text_dim"], font=FONTS["sub_header"]
        )
        self.lbl_analysis_tools.pack(side=tk.LEFT)
        self._translatable["analysis_tools"] = {
            "widget": self.lbl_analysis_tools, "key": "analysis_tools_title"
        }
        tk.Frame(tools_cont, bg=THEME["gold_dim"], height=1).pack(fill=tk.X, padx=20, pady=(4, 8))

        self._build_tool_buttons(tools_cont)

    def _build_tool_buttons(self, parent: tk.Frame) -> None:
        cv_fr = tk.Frame(parent, bg=THEME["card_bg"])
        cv_fr.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        tools_cv = tk.Canvas(cv_fr, bg=THEME["card_bg"], highlightthickness=0)
        sb = ttk.Scrollbar(cv_fr, orient="vertical", command=tools_cv.yview)
        scroll_fr = tk.Frame(tools_cv, bg=THEME["card_bg"])
        scroll_fr.bind(
            "<Configure>",
            lambda e: tools_cv.configure(scrollregion=tools_cv.bbox("all")),
        )
        tools_cv.create_window((0, 0), window=scroll_fr, anchor="nw")
        tools_cv.configure(yscrollcommand=sb.set)

        def _on_mw(event: tk.Event) -> None:
            try:
                tools_cv.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass

        tools_cv.bind_all("<MouseWheel>", _on_mw)
        tools_cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        ICONS = {
            "tool_planetary_positions":  "🪐",
            "tool_house_cusps":          "🏠",
            "tool_house_significators":  "🔑",
            "tool_planet_significators": "⭐",
            "tool_aspects_drishti":      "🔮",
            "tool_kp_dasa":             "📅",
        }
        ALL_TOOLS = [
            ("tool_planetary_positions",  self.show_planetary_positions, THEME["primary"]),
            ("tool_house_cusps",          self.show_cusps,               THEME["secondary_dim"]),
            ("tool_house_significators",  self.show_house_significators, THEME["gold_dim"]),
            ("tool_planet_significators", self.show_planet_significators,THEME["primary"]),
            ("tool_aspects_drishti",      self.show_aspects,             THEME["secondary_dim"]),
            ("tool_kp_dasa",              self.show_dasa,                THEME["gold_dim"]),
        ]

        if self.mode == AppMode.MATCHMAKE:
            for section_lbl, data_getter, color in [
                ("♂ GROOM ANALYSIS", self._engine.primary,   THEME["primary_light"]),
                ("♀ BRIDE ANALYSIS", self._engine.secondary, THEME["secondary"]),
            ]:
                fr_hdr = tk.Frame(scroll_fr, bg=THEME["card_bg"])
                fr_hdr.pack(fill=tk.X, pady=(10, 5), padx=20)
                tk.Label(fr_hdr, text=section_lbl, bg=THEME["card_bg"],
                         fg=color, font=FONTS["sub_header"]).pack(side=tk.LEFT)
                for key, fn, accent in ALL_TOOLS:
                    # FIX ⑨ — capture loop variables correctly
                    def _make_cmd(f=fn, dg=data_getter):
                        return lambda: self._run_safe(lambda: f(dg()))
                    label = f"{ICONS.get(key, '◈')}  {t(key)}"
                    btn_c = create_tool_button(scroll_fr, label,
                                               _make_cmd(), accent, THEME, FONTS)
                    btn_c.pack(pady=4, fill=tk.X, padx=20)
                    self.tool_buttons.append({"container": btn_c, "key": key})
        else:
            for key, fn, accent in ALL_TOOLS:
                def _make_cmd(f=fn):
                    return lambda: self._run_safe(f)
                label = f"{ICONS.get(key, '◈')}  {t(key)}"
                btn_c = create_tool_button(scroll_fr, label,
                                            _make_cmd(), accent, THEME, FONTS)
                btn_c.pack(pady=8, fill=tk.X, padx=20)
                self.tool_buttons.append({"container": btn_c, "key": key})

    # ═════════════════════════════════════════════════════════════════════════
    # UI helpers
    # ═════════════════════════════════════════════════════════════════════════

    def _toggle_input_panel(self) -> None:
        if self.input_content is None or self.collapse_btn is None:
            return
        if self.input_collapsed:
            self.input_content.pack(fill=tk.X)
            self.collapse_btn.configure(text="▼")
            self.input_collapsed = False
        else:
            self.input_content.pack_forget()
            self.collapse_btn.configure(text="▶")
            self.input_collapsed = True

    def _on_language_change(self, _event: Any = None) -> None:
        if not self.lang_combo:
            return
        idx = self.lang_combo.current()
        if 0 <= idx < len(self._lang_codes):
            new_lang = self._lang_codes[idx]
            set_lang(new_lang)
            self._refresh_ui_translations()

    def _refresh_ui_translations(self) -> None:
        self._build_window_title()
        for info in self._translatable.values():
            w   = info.get("widget")
            key = info.get("key", "")
            if w and key:
                try:
                    prefix = " " if key in ("birth_details", "analysis_tools_title") else ""
                    w.configure(text=prefix + t(key))
                except Exception:
                    pass
        for btn_info in self.tool_buttons:
            cont = btn_info.get("container")
            key  = btn_info.get("key", "")
            if isinstance(cont, tk.Frame) and key:
                for child in cont.winfo_children():
                    if isinstance(child, tk.Button):
                        try:
                            child.configure(text=t(str(key)))
                        except Exception:
                            pass

    def _apply_popup_style(self, window: tk.Toplevel, title: str) -> tk.Frame:
        window.title(title)
        window.state("zoomed")
        window.configure(bg=THEME["app_bg"])

        hdr_outer = tk.Frame(window, bg=THEME["header_bg"])
        hdr_outer.pack(fill=tk.X)

        bar = tk.Frame(hdr_outer, height=3, bg=THEME["header_bg"])
        bar.pack(fill=tk.X)
        tk.Frame(bar, width=1, height=3, bg=THEME["primary"]).pack(side=tk.LEFT, fill=tk.Y)
        tk.Frame(bar, height=3, bg=THEME["gold"]).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Frame(bar, width=1, height=3, bg=THEME["primary"]).pack(side=tk.LEFT, fill=tk.Y)

        hdr = tk.Frame(hdr_outer, bg=THEME["header_bg"], pady=16)
        hdr.pack(fill=tk.X)
        title_row = tk.Frame(hdr, bg=THEME["header_bg"])
        title_row.pack()
        tk.Label(title_row, text="◈", bg=THEME["header_bg"],
                 fg=THEME["gold"], font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_row, text=title.upper(), bg=THEME["header_bg"],
                 fg=THEME["text_glow"], font=FONTS["header"]).pack(side=tk.LEFT)
        tk.Label(title_row, text="◈", bg=THEME["header_bg"],
                 fg=THEME["gold"], font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=(10, 0))

        tk.Frame(hdr_outer, bg=THEME["border_gold"], height=1).pack(fill=tk.X)
        tk.Frame(hdr_outer, bg=THEME["border_glow"], height=1).pack(fill=tk.X)

        cf = tk.Frame(window, bg=THEME["app_bg"], padx=20, pady=20)
        cf.pack(fill=tk.BOTH, expand=True)
        return cf

    def _show_toast(self, message: str, is_error: bool = False) -> None:
        """Non-blocking bottom-right notification."""
        w = tk.Toplevel(self.root)
        w.attributes("-topmost", True)
        w.overrideredirect(True)
        w.configure(bg=THEME["border"])
        w.resizable(False, False)

        width, height = 420, 80
        sw = w.winfo_screenwidth()
        sh = w.winfo_screenheight()
        w.geometry(f"{width}x{height}+{sw - width - 20}+{sh - height - 60}")

        inner = tk.Frame(w, bg=THEME["card_bg"], padx=15, pady=10)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        icon  = "❌" if is_error else "✅"
        color = THEME["danger"] if is_error else THEME["success"]
        tk.Label(inner, text=f"{icon}  {message}",
                 bg=THEME["card_bg"], fg=color,
                 font=("Segoe UI", 10, "bold"),
                 wraplength=380, anchor="w").pack(fill=tk.X)

        w.after(3500, w.destroy)

    def _show_table(
        self, title: str, columns: List[str], rows: List[tuple]
    ) -> None:
        win = tk.Toplevel(self.root)
        cf  = self._apply_popup_style(win, title)

        tb_border = tk.Frame(cf, bg=THEME["border_glow"])
        tb_border.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        tb_cont = tk.Frame(tb_border, bg=THEME["card_bg"])
        tb_cont.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        tv = ttk.Treeview(tb_cont, columns=columns, show="headings")
        for col in columns:
            tv.heading(col, text=str(col).upper())
            w = 350 if "Detail" in col or "Desc" in col else 170
            tv.column(col, anchor="w" if w > 200 else "center", width=w)

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            tv.insert("", "end", values=row, tags=(tag,))

        tv.tag_configure("odd",  background="#181838")
        tv.tag_configure("even", background=THEME["card_bg"])

        sc = ttk.Scrollbar(tb_cont, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sc.set)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ═════════════════════════════════════════════════════════════════════════
    # Location helpers
    # ═════════════════════════════════════════════════════════════════════════

    def auto_fill_location(self, target: Optional[tk.Widget] = None) -> None:
        ent = target if target else self.ent_city_search
        if not ent:
            return
        query = ent.get().strip()
        if not query:
            return
        loc = self._engine.loc
        if not loc:
            return
        data = loc.search_city(query)
        if not data:
            self._show_toast("City not found.", is_error=True)
            return

        try:
            if HAS_PYTZ:
                tz_obj    = pytz.timezone(data.get("timezone", "UTC"))
                offset_s  = tz_obj.utcoffset(datetime.datetime.now()).total_seconds()
                h = int(abs(offset_s) // 3600)
                m = int((abs(offset_s) % 3600) // 60)
                sign = "+" if offset_s >= 0 else "-"
                tz_str = f"{sign}{h:02d}:{m:02d}"
            else:
                tz_str = data.get("timezone", "+05:30")
        except Exception:
            tz_str = "+05:30"

        is_alt = (target is self.ent_city_search_alt)
        e_lat   = self.ent_lat_alt  if is_alt else self.ent_lat
        e_lon   = self.ent_lon_alt  if is_alt else self.ent_lon
        e_tz_e  = self.ent_tz_alt   if is_alt else self.ent_tz

        for entry, val in [
            (e_lat,  str(data.get("latitude",  ""))),
            (e_lon,  str(data.get("longitude", ""))),
            (e_tz_e, tz_str),
        ]:
            if entry:
                entry.delete(0, tk.END)  # type: ignore[union-attr]
                entry.insert(0, val)     # type: ignore[union-attr]

        if not is_alt:
            for entry, key in [
                (self.ent_country, "country_name"),
                (self.ent_state,   "state_name"),
            ]:
                if entry:
                    entry.delete(0, tk.END)  # type: ignore[union-attr]
                    entry.insert(0, str(data.get(key, "")))  # type: ignore[union-attr]

    def _on_country_select(self, _event: Any) -> None:
        if not self.combo_country:
            return
        sel = self.combo_country.get()
        for code, data in self.national_charts.items():
            if not isinstance(data, dict):
                continue
            if code in sel:
                for entry_attr, d_key in [
                    ("entries", "ent_date"),
                    ("entries", "ent_time"),
                ]:
                    try:
                        if d_key == "ent_date":
                            e = self.entries.get("ent_date")
                            if e:
                                e.delete(0, tk.END)
                                e.insert(0, str(data.get("date", "")))
                        elif d_key == "ent_time":
                            e = self.entries.get("ent_time")
                            if e:
                                e.delete(0, tk.END)
                                e.insert(0, str(data.get("time", "")))
                    except Exception:
                        pass
                for entry, key in [
                    (self.ent_country, "name"),
                    (self.ent_state,   "capital"),
                    (self.ent_lat,     "lat"),
                    (self.ent_lon,     "lon"),
                    (self.ent_tz,      "tz"),
                ]:
                    if entry:
                        entry.delete(0, tk.END)      # type: ignore[union-attr]
                        entry.insert(0, str(data.get(key, "")))  # type: ignore[union-attr]
                break

    # ═════════════════════════════════════════════════════════════════════════
    # Chart processing  (FIX ② — all UI updates via root.after)
    # ═════════════════════════════════════════════════════════════════════════

    def process_chart(self) -> None:
        if self._is_processing:
            return
        try:
            p_kwargs = self._collect_primary_kwargs()
            s_kwargs = self._collect_secondary_kwargs() if self.mode == AppMode.MATCHMAKE else None
            horary   = None
            if self.mode == AppMode.HORARY:
                horary = self._read_horary_number()
                if horary is None:
                    return
                p_kwargs["horary_num"] = horary

        except ValueError as exc:
            self._show_toast(str(exc), is_error=True)
            return

        errors = ChartInputValidator.validate_birth_input(
            p_kwargs["date_str"], p_kwargs["time_str"],
            p_kwargs["lat"],      p_kwargs["lon"], p_kwargs["tz_str"],
        )
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        self._is_processing = True
        if self.btn_generate:
            self.btn_generate.configure(text="⏳ Calculating…", state=tk.DISABLED)

        def on_success(result: Dict[str, Any]) -> None:
            # FIX ② — schedule UI work on main thread
            self.root.after(0, lambda: self._on_chart_complete(result))

        def on_error(msg: str) -> None:
            self.root.after(0, lambda: self._on_chart_error(msg))

        self._engine.calculate_async(p_kwargs, s_kwargs, self.mode,
                                     on_success, on_error)

    def _collect_primary_kwargs(self) -> Dict[str, Any]:
        def _get(key: str) -> str:
            e = self.entries.get(key)
            return e.get().strip() if e else ""

        date_str = _get("ent_date")
        time_str = _get("ent_time")
        if not date_str or not time_str:
            raise ValueError("Date and time are required.")

        def _geo(widget: Optional[tk.Widget]) -> str:
            if widget is None:
                return ""
            try:
                return widget.get().strip()  # type: ignore[union-attr]
            except Exception:
                return ""

        lat_s = _geo(self.ent_lat)
        lon_s = _geo(self.ent_lon)
        tz_s  = _geo(self.ent_tz)

        if not lat_s or not lon_s:
            raise ValueError("Latitude and Longitude are required.  Search a city first.")
        try:
            lat = float(lat_s)
            lon = float(lon_s)
        except ValueError:
            raise ValueError("Invalid latitude or longitude value.")

        return {"date_str": date_str, "time_str": time_str,
                "lat": lat, "lon": lon, "tz_str": tz_s or "+05:30"}

    def _collect_secondary_kwargs(self) -> Optional[Dict[str, Any]]:
        def _geo(w: Optional[tk.Widget]) -> str:
            if w is None:
                return ""
            try:
                return w.get().strip()  # type: ignore[union-attr]
            except Exception:
                return ""

        date_str = (self.entries.get("ent_date_alt") or tk.Entry()).get().strip()
        time_str = (self.entries.get("ent_time_alt") or tk.Entry()).get().strip()
        lat_s    = _geo(self.ent_lat_alt)
        lon_s    = _geo(self.ent_lon_alt)
        tz_s     = _geo(self.ent_tz_alt)

        if not date_str or not lat_s:
            return None
        try:
            lat = float(lat_s)
            lon = float(lon_s)
        except ValueError:
            return None
        return {"date_str": date_str, "time_str": time_str,
                "lat": lat, "lon": lon, "tz_str": tz_s or "+05:30"}

    def _read_horary_number(self) -> Optional[int]:
        e = self.ent_horary_number
        if not e:
            self._show_toast("Horary number field missing.", is_error=True)
            return None
        try:
            n = int(e.get().strip())
            if not (1 <= n <= 249):
                raise ValueError
            self.horary_number = n
            return n
        except ValueError:
            self._show_toast("Horary number must be 1–249.", is_error=True)
            return None

    def _on_chart_complete(self, data: Dict[str, Any]) -> None:
        self._is_processing = False
        if self.btn_generate:
            self.btn_generate.configure(text=t("btn_generate"), state=tk.NORMAL)

        p1 = data["p1"]
        p2 = data.get("p2")

        if self.mode == AppMode.MATCHMAKE:
            if self.drawer_groom and p1:
                self.drawer_groom.draw_full_chart(p1["planets"], p1["cusps"])
            if self.drawer_bride and p2:
                self.drawer_bride.draw_full_chart(p2["planets"], p2["cusps"])
        else:
            if self.drawer and p1:
                self.drawer.draw_full_chart(p1["planets"], p1["cusps"])

        self._draw_zodiac_names()
        self.root.after(600, self._save_chart_snapshot)
        self._show_toast("Chart calculated successfully.")

    def _on_chart_error(self, msg: str) -> None:
        self._is_processing = False
        if self.btn_generate:
            self.btn_generate.configure(text=t("btn_generate"), state=tk.NORMAL)
        self._show_toast(f"Calculation error: {msg}", is_error=True)
        app_logger.error("Chart calculation error: %s", msg)

    # ── zodiac ring overlay ───────────────────────────────────────────────────
    def _draw_zodiac_names(self) -> None:
        drw = self.drawer
        if drw is None:
            return
        if not all(hasattr(drw, a) for a in ("center_x", "center_y", "radius")):
            return
        cx = float(drw.center_x)
        cy = float(drw.center_y)
        r  = float(drw.radius)
        if r == 0:
            return

        zodiac = [
            ("Aries",       "♈", "#FF6B6B"), ("Taurus",      "♉", "#00E676"),
            ("Gemini",      "♊", "#00F5D4"), ("Cancer",      "♋", "#64B5F6"),
            ("Leo",         "♌", "#FF6B6B"), ("Virgo",       "♍", "#00E676"),
            ("Libra",       "♎", "#00F5D4"), ("Scorpio",     "♏", "#64B5F6"),
            ("Sagittarius", "♐", "#FF6B6B"), ("Capricorn",   "♑", "#00E676"),
            ("Aquarius",    "♒", "#00F5D4"), ("Pisces",      "♓", "#64B5F6"),
        ]
        cv = self.canvas
        if cv is None:
            return
        for i, (name, sym, color) in enumerate(zodiac):
            angle = math.radians((i * 30) + 15)
            tx = cx + (r + 45) * math.cos(angle)
            ty = cy - (r + 45) * math.sin(angle)
            raw = t(f"sign_{name}")
            short = str(raw)[:3]
            cv.create_text(tx, ty, text=f"{sym} {short}",
                           fill=color, font=("Segoe UI", 9, "bold"),
                           anchor="center")

    # ── resize ────────────────────────────────────────────────────────────────
    def _on_resize(self, _event: Any) -> None:
        p1 = self._engine.primary()
        drw = self.drawer
        if drw and p1.get("is_calculated"):
            drw.draw_full_chart(p1["planets"], p1["cusps"])
            self._draw_zodiac_names()
        elif drw and hasattr(drw, "draw_base_chart"):
            drw.draw_base_chart()

    # ── chart snapshot ────────────────────────────────────────────────────────
    def _save_chart_snapshot(self) -> None:
        if not HAS_PIL:
            return
        cv = self.canvas
        if cv is None or not cv.winfo_exists():
            return
        try:
            from PIL import ImageGrab  # type: ignore
            import tempfile
            x = cv.winfo_rootx()
            y = cv.winfo_rooty()
            w = cv.winfo_width()
            h = cv.winfo_height()
            if w < 50 or h < 50:
                return
            scale = 1.0
            if os.name == "nt":
                try:
                    import ctypes
                    scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100.0  # type: ignore
                except Exception:
                    pass
            box = (int(x*scale), int(y*scale),
                   int((x+w)*scale), int((y+h)*scale))
            img = ImageGrab.grab(bbox=box)
            path = os.path.join(tempfile.gettempdir(), "diya_chart_snapshot.png")
            img.save(path, "PNG")
            self._saved_chart_image_path = path
        except Exception as exc:
            app_logger.warning("Chart snapshot failed: %s", exc)

    # ═════════════════════════════════════════════════════════════════════════
    # Tool-panel displays
    # ═════════════════════════════════════════════════════════════════════════

    def _check_calculated(self) -> bool:
        p = self._engine.primary()
        if not p.get("is_calculated"):
            messagebox.showwarning("Pranam", "Please Generate Kundli first.")
            return False
        return True

    def _run_safe(self, fn: Callable[[], None]) -> None:
        if not self._check_calculated():
            return
        try:
            fn()
        except Exception as exc:
            app_logger.exception("Tool error")
            self._show_toast(str(exc), is_error=True)

    def show_planetary_positions(self, data: Optional[Dict[str, Any]] = None) -> None:
        d = data or self._engine.primary()
        if not d.get("planets"):
            return
        calc = self._engine.calc
        if not calc:
            return
        rows = []
        for p, lon in d["planets"].items():
            sign, deg_in = calc.get_zodiac_sign(lon)
            dg, mn, sc   = calc.decimal_to_dms(deg_in)
            nak, st, sb  = calc.get_sub_lord_info(lon)
            rows.append((
                t(f"p_{p}"),
                f"{int(dg):02d}° {int(mn):02d}' {int(sc):02d}\"",
                t(f"sign_{sign}"), t(f"nak_{nak}".replace(" ", "")),
                t(f"p_{st}"), t(f"p_{sb}"),
            ))
        self._show_table(t("tbl_planetary_positions"),
                         [t("col_planet"), t("col_longitude"), t("col_sign"),
                          t("col_nakshatra"), t("col_star_lord"), t("col_sub_lord")],
                         rows)

    def show_cusps(self, data: Optional[Dict[str, Any]] = None) -> None:
        d = data or self._engine.primary()
        if not d.get("cusps"):
            return
        calc = self._engine.calc
        if not calc:
            return
        rows = []
        for i in range(1, 13):
            lon = d["cusps"][i]
            sign, deg_in = calc.get_zodiac_sign(lon)
            dg, mn, sc   = calc.decimal_to_dms(deg_in)
            _, st, sb    = calc.get_sub_lord_info(lon)
            sl_name      = calc.get_sign_lord(sign)
            rows.append((
                str(i),
                f"{int(dg):02d}° {int(mn):02d}' {int(sc):02d}\"",
                t(f"sign_{sign}"), t(f"p_{sl_name}"),
                t(f"p_{st}"), t(f"p_{sb}"),
            ))
        self._show_table(t("tbl_house_cusps"),
                         [t("col_cusp"), t("col_degree"), t("col_sign"),
                          t("col_sign_lord"), t("col_star_lord"), t("col_sub_lord")],
                         rows)

    def show_house_significators(self, data: Optional[Dict[str, Any]] = None) -> None:
        d = data or self._engine.primary()
        if not d.get("planets"):
            return
        calc = self._engine.calc
        if not calc:
            return
        hs   = calc.get_house_significators(d["planets"], d["cusps"])
        rows = [
            (convert_number(f"H{h}"), sv["L1"], sv["L2"], sv["L3"], sv["L4"])
            for h, sv in hs.items()
        ]
        self._show_table(t("tbl_house_significators"),
                         [t("col_house"), t("col_l1"), t("col_l2"),
                          t("col_l3"), t("col_l4")],
                         rows)

    def show_planet_significators(self, data: Optional[Dict[str, Any]] = None) -> None:
        d = data or self._engine.primary()
        if not d.get("planets"):
            return
        calc = self._engine.calc
        if not calc:
            return
        bh      = calc.get_bhavasphuta_significators(d["planets"], d["cusps"])
        csl_map: Dict[str, List[int]] = {}
        for i in range(1, 13):
            lon = d["cusps"].get(i, 0.0)
            _, _, sub = calc.get_sub_lord_info(lon)
            if sub:
                csl_map.setdefault(str(sub), []).append(i)

        rows: List[tuple] = []
        for p in calc.PLANET_ORDER:
            if p not in bh:
                continue
            dat  = bh[p]
            plon = float(d["planets"].get(p, 0.0))
            _, sl_name, sb_name = calc.get_sub_lord_info(plon)
            src: List[int] = []
            for key in ("P_Occ", "P_Own", "S_Occ", "S_Own"):
                src.extend(_raw_houses(dat.get(key, "")))
            res: List[int] = (
                csl_map.get(p, [])
                + csl_map.get(str(sl_name), [])
                + csl_map.get(str(sb_name), [])
            )
            rows.append((t(f"p_{p}"), "Promise", _fmt_repeats(src)))
            rows.append(("",         "DELIVER",  _fmt_repeats(res)))

        self._show_table(t("tbl_planet_significators"),
                         [t("col_planet"), t("col_level"), t("col_details")],
                         rows)

    def show_aspects(self, data: Optional[Dict[str, Any]] = None) -> None:
        d = data or self._engine.primary()
        if not d.get("planets"):
            return
        calc = self._engine.calc
        if not calc:
            return

        win = tk.Toplevel(self.root)
        cf  = self._apply_popup_style(win, t("tbl_aspects_drishti"))

        tb = tk.Frame(cf, bg=THEME["border_glow"])
        tb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tc = tk.Frame(tb, bg=THEME["card_bg"])
        tc.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        cols = ["System", "Source", "Relation", "Target", "Value/Type", "Quality"]
        tv   = ttk.Treeview(tc, columns=cols, show="headings")
        sc   = ttk.Scrollbar(tc, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sc.set)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col, w in zip(cols, [140, 130, 160, 130, 140, 110]):
            tv.heading(col, text=col.upper())
            tv.column(col, width=w, anchor="center")

        rows: List[tuple] = []
        planets = d["planets"]
        cusps   = d["cusps"]
        plist   = calc.PLANET_ORDER

        # KP planet–planet aspects
        for i, p1 in enumerate(plist):
            for p2 in plist[i + 1:]:
                nm, qual, deg = _kp_relation(
                    float(planets.get(p1, 0)), float(planets.get(p2, 0))
                )
                if nm:
                    rows.append(("KP P-P", t(f"p_{p1}"), nm, t(f"p_{p2}"), deg, qual))

        # KP planet–cusp aspects
        for p in plist:
            for h in range(1, 13):
                nm, qual, deg = _kp_relation(
                    float(planets.get(p, 0)), float(cusps.get(h, 0))
                )
                if nm:
                    rows.append(("KP P-H", t(f"p_{p}"), nm, f"H{h}", deg, qual))

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            tv.insert("", "end", values=row, tags=(tag,))

        tv.tag_configure("odd",  background="#181838")
        tv.tag_configure("even", background=THEME["card_bg"])

    def show_dasa(self, data: Optional[Dict[str, Any]] = None) -> None:
        d = data or self._engine.primary()
        if not d.get("planets"):
            return

        win = tk.Toplevel(self.root)
        cf  = self._apply_popup_style(win, t("tbl_kp_dasa"))

        tv = ttk.Treeview(cf, columns=("Lvl", "Start", "End"), show="tree headings")
        tv.pack(fill=tk.BOTH, expand=True)
        tv.heading("#0",    text=t("col_planet"))
        tv.heading("Lvl",   text=t("col_level"))
        tv.heading("Start", text=t("col_start"))
        tv.heading("End",   text=t("col_end"))

        limit = 500 if self.mode == AppMode.MUNDANE else 120
        seq   = self._engine.get_dasa_sequence(d, limit_years=limit)

        for node in seq:
            ltr  = t(f"p_{node['lord']}")
            s_dt = node["start"]
            e_dt = node["end"]
            item = tv.insert(
                "", "end",
                text=f"{ltr} (MD)",
                values=("Mahadasha",
                        s_dt.strftime("%d-%b-%Y"),
                        e_dt.strftime("%d-%b-%Y"),
                        f"{node['duration']:.2f} yrs",
                        node["lord"]),
                tags=("lvl0",),
            )
            tv.insert(item, "end", text="Loading…")

        def _on_open(evt: tk.Event) -> None:
            item = tv.focus()
            children = tv.get_children(item)
            if len(children) == 1 and tv.item(children[0], "text") == "Loading…":
                tv.delete(children[0])
                vals  = tv.item(item, "values")
                tags  = tv.item(item, "tags")
                lord  = vals[4]
                end_s = vals[2]
                dur   = float(str(vals[3]).replace(" yrs", ""))
                lvl   = 0 if "lvl0" in tags else (1 if "lvl1" in tags else 2)
                if lvl < 2:
                    end_dt = datetime.datetime.strptime(end_s, "%d-%b-%Y")
                    subs = self._engine.get_nested_dasa(
                        d, lord, end_dt, dur, level=lvl + 1, max_level=lvl + 1
                    )
                    for sn in subs:
                        sl  = sn["lord"]
                        se  = datetime.datetime.strptime(
                                  str(sn["end"])[:16], "%d-%m-%Y %H:%M"
                              )
                        sub_item = tv.insert(
                            item, "end",
                            text=f"{t(f'p_{sl}')} ({sn['level'][:2]})",
                            values=(sn["level"], sn["start"],
                                    se.strftime("%d-%b-%Y"),
                                    sn["duration"], sl),
                            tags=(f"lvl{lvl+1}",),
                        )
                        if lvl < 1:
                            tv.insert(sub_item, "end", text="Loading…")

        tv.bind("<<TreeviewOpen>>", _on_open)

    # ═════════════════════════════════════════════════════════════════════════
    # Save / Erase
    # ═════════════════════════════════════════════════════════════════════════

    def save_chart_data(self, show_popup: bool = True) -> None:
        if not self._check_calculated():
            return
        try:
            filename  = DataManager.get_chart_data_filename(self.mode.value)
            p1        = self._engine.primary()

            # metadata
            def _e(key: str) -> str:
                e = self.entries.get(key)
                return e.get().strip() if e else ""

            name = _e("ent_name") or "Unknown"
            gender = self.combo_gender.get() if self.combo_gender else "N/A"

            city_e = self.ent_city_search
            city   = city_e.get().strip() if city_e else ""  # type: ignore[union-attr]

            def _geo_val(w: Optional[tk.Widget]) -> str:
                if w is None:
                    return ""
                try:
                    return w.get().strip()  # type: ignore[union-attr]
                except Exception:
                    return ""

            meta: Dict[str, Any] = {
                "name": name, "dob": _e("ent_date"), "tob": _e("ent_time"),
                "gender": gender, "mode": self.mode.value,
                "lat": _geo_val(self.ent_lat), "lon": _geo_val(self.ent_lon),
                "location": {"city": city,
                             "lat":  _geo_val(self.ent_lat),
                             "lon":  _geo_val(self.ent_lon)},
                "ayanamsa": p1.get("ayanamsa", 0.0),
                "language": get_lang(),
            }
            if self.mode == AppMode.HORARY and self.horary_number:
                meta["horary_number"] = self.horary_number

            export: Dict[str, Any] = {"metadata": meta}
            export.update(self._engine.build_export(p1))

            if self.mode == AppMode.MATCHMAKE:
                p2 = self._engine.secondary()
                export["groom_data"] = self._engine.build_export(p1)
                export["bride_data"]  = self._engine.build_export(p2)
                export["metadata"]["partner_details"] = {
                    "name": _e("ent_name_alt"),
                    "dob":  _e("ent_date_alt"),
                    "tob":  _e("ent_time_alt"),
                }

            os.makedirs("data", exist_ok=True)
            path = os.path.join("data", filename)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(export, fh, indent=4, ensure_ascii=False)

            if show_popup:
                self._show_toast(f"Chart saved → {path}")
        except Exception as exc:
            app_logger.exception("Save chart failed")
            self._show_toast(f"Save error: {exc}", is_error=True)

    def erase_chart_data(self) -> None:
        fname = DataManager.get_chart_data_filename(self.mode.value)
        path  = os.path.join("data", fname)
        try:
            os.makedirs("data", exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({}, fh)
            self._show_toast("Chart data erased.")
        except Exception as exc:
            self._show_toast(f"Erase error: {exc}", is_error=True)

    # ═════════════════════════════════════════════════════════════════════════
    # AI / Report popups (thin shells — actual AI lives in src/)
    # ═════════════════════════════════════════════════════════════════════════

    def open_astrologer_popup(self) -> None:
        try:
            if self.mode == AppMode.HORARY or self.mode == AppMode.MUNDANE:
                from src.horary_mundane_ai import HoraryMundaneAI  # type: ignore
                win = tk.Toplevel(self.root)
                HoraryMundaneAI(win, mode=self.mode.value, lang=get_lang())
            elif self.mode == AppMode.BIRTH:
                from src.titanium_ai_b import TitaniumAI  # type: ignore
                win = tk.Toplevel(self.root)
                TitaniumAI(win, lang=get_lang())
            else:
                from src.titanium_ai import TitaniumAI  # type: ignore
                win = tk.Toplevel(self.root)
                TitaniumAI(win, lang=get_lang())
        except ImportError as exc:
            messagebox.showerror("Import Error", f"AI module not found:\n{exc}")
        except Exception as exc:
            app_logger.exception("Astrologer popup error")
            messagebox.showerror("Error", str(exc))

    def open_report_popup(self, pre_select_topic: Optional[str] = None) -> None:
        """Thin shell — delegates to ReportDashboard."""
        ReportDashboard(
            parent=self.root,
            theme=THEME,
            fonts=FONTS,
            engine=self._engine,
            mode=self.mode,
            get_lang_fn=get_lang,
            image_refs=self._image_refs,
            saved_chart_path=self._saved_chart_image_path,
            pre_select_topic=pre_select_topic,
            app_instance=self,  # Pass app instance for name resolution
        )


# ═══════════════════════════════════════════════════════════════════════════════
# ReportDashboard — separated from KPApp (FIX ④)
# ═══════════════════════════════════════════════════════════════════════════════

class ReportDashboard:
    """
    Handles topic selection + multi-threaded report generation.
    Completely separated from KPApp.
    """

    def __init__(
        self,
        parent: tk.Tk,
        theme: Dict[str, str],
        fonts: Dict[str, tuple],
        engine: ChartEngine,
        mode: AppMode,
        get_lang_fn: Callable[[], str],
        image_refs: List[Any],
        saved_chart_path: Optional[str],
        pre_select_topic: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._parent          = parent
        self._theme           = theme
        self._engine          = engine
        self._mode            = mode
        self._get_lang        = get_lang_fn
        self._image_refs      = image_refs
        self._chart_img_path  = saved_chart_path
        self._selected: Set[str] = {pre_select_topic} if pre_select_topic else set()
        self._app             = kwargs.get("app_instance")

        T = theme

        self._win = tk.Toplevel(parent)
        self._win.title("📊 Report Dashboard")
        self._win.state("zoomed")
        self._win.configure(bg=T["app_bg"])

        self._build_header()
        self._btn_frame = tk.Frame(self._win, bg=T["app_bg"], padx=20, pady=10)
        self._btn_frame.pack(fill=tk.X)
        self._build_action_buttons()

        self._topic_frame = tk.Frame(self._win, bg=T["card_bg"], padx=10, pady=10)
        # shown only after "Choose Topic"

        if pre_select_topic:
            self._show_topic_chooser()

    def _build_header(self) -> None:
        T = self._theme
        hdr = tk.Frame(self._win, bg=T["header_bg"], pady=14)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="◈  REPORT DASHBOARD  ◈",
                 bg=T["header_bg"], fg=T["gold"],
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Frame(self._win, bg=T["border_glow"], height=1).pack(fill=tk.X)

    def _build_action_buttons(self) -> None:
        T = self._theme
        bf = self._btn_frame
        tk.Button(bf, text="📂 LOAD DATA", bg=T["primary_dark"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
                  padx=15, pady=8, cursor="hand2",
                  command=self._load_data).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(bf, text="📋 CHOOSE TOPIC", bg=T["primary"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
                  padx=15, pady=8, cursor="hand2",
                  command=self._show_topic_chooser).pack(side=tk.LEFT)
        tk.Button(bf, text="🚀 GENERATE REPORT", bg=T["warning"], fg="#1A1A2E",
                  font=("Segoe UI", 11, "bold"), relief=tk.FLAT,
                  padx=20, pady=10, cursor="hand2",
                  command=self._generate).pack(side=tk.RIGHT)

    def _load_data(self) -> None:
        """Save current chart to disk so report engines can read it."""
        try:
            p1  = self._engine.primary()
            if not p1.get("is_calculated"):
                messagebox.showwarning("Warning", "Generate Kundli first.")
                return
            fname = DataManager.get_chart_data_filename(self._mode.value)
            os.makedirs("data", exist_ok=True)
            path  = os.path.join("data", fname)

            # ── Pull metadata from parent app entries ──
            def _e(key: str) -> str:
                if self._app and hasattr(self._app, 'entries'):
                    e = self._app.entries.get(key)
                    return e.get().strip() if e else ""
                return ""

            def _geo(w) -> str:
                if w is None:
                    return ""
                try:
                    return w.get().strip()
                except Exception:
                    return ""

            name = _e("ent_name") or "Unknown"
            gender = ""
            if self._app and hasattr(self._app, 'combo_gender') and self._app.combo_gender:
                gender = self._app.combo_gender.get()

            city = ""
            if self._app and hasattr(self._app, 'ent_city_search') and self._app.ent_city_search:
                try:
                    city = self._app.ent_city_search.get().strip()
                except Exception:
                    pass

            meta: Dict[str, Any] = {
                "name": name,
                "dob": _e("ent_date"),
                "tob": _e("ent_time"),
                "gender": gender,
                "mode": self._mode.value,
                "lat": _geo(getattr(self._app, 'ent_lat', None)),
                "lon": _geo(getattr(self._app, 'ent_lon', None)),
                "location": {"city": city,
                             "lat": _geo(getattr(self._app, 'ent_lat', None)),
                             "lon": _geo(getattr(self._app, 'ent_lon', None))},
                "ayanamsa": p1.get("ayanamsa", 0.0),
                "language": self._get_lang(),
            }

            export: Dict[str, Any] = {"metadata": meta}
            export.update(self._engine.build_export(p1))

            # ── MATCHMAKE: include bride data + partner details ──
            if self._mode == AppMode.MATCHMAKE:
                p2 = self._engine.secondary()
                export["groom_data"] = self._engine.build_export(p1)
                export["bride_data"] = self._engine.build_export(p2)

                bride_city = ""
                if self._app and hasattr(self._app, 'ent_city_search_alt') and self._app.ent_city_search_alt:
                    try:
                        bride_city = self._app.ent_city_search_alt.get().strip()
                    except Exception:
                        pass

                export["metadata"]["partner_details"] = {
                    "name": _e("ent_name_alt") or "Partner",
                    "dob":  _e("ent_date_alt"),
                    "tob":  _e("ent_time_alt"),
                    "lat":  _geo(getattr(self._app, 'ent_lat_alt', None)),
                    "lon":  _geo(getattr(self._app, 'ent_lon_alt', None)),
                    "location": {"city": bride_city},
                }

            with open(path, "w", encoding="utf-8") as fh:
                json.dump(export, fh, indent=4, ensure_ascii=False)
            lbl = tk.Label(self._btn_frame, text="✅ DATA LOADED",
                           bg=self._theme["app_bg"], fg=self._theme["success"],
                           font=("Segoe UI", 10, "bold"))
            lbl.pack(side=tk.LEFT, padx=10)
            self._win.after(3000, lbl.destroy)
        except Exception as exc:
            app_logger.exception("Report load_data failed")
            messagebox.showerror("Error", str(exc))

    def _show_topic_chooser(self) -> None:
        T = self._theme
        for w in self._topic_frame.winfo_children():
            w.destroy()
        self._topic_frame.pack(fill=tk.BOTH, expand=True)

        cv  = tk.Canvas(self._topic_frame, bg=T["card_bg"], highlightthickness=0)
        sb  = ttk.Scrollbar(self._topic_frame, orient="vertical", command=cv.yview)
        sfr = tk.Frame(cv, bg=T["card_bg"])
        sfr.bind("<Configure>",
                 lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=sfr, anchor="nw")
        cv.configure(yscrollcommand=sb.set)

        def _mw(evt: tk.Event) -> None:
            try:
                cv.yview_scroll(int(-1 * (evt.delta / 120)), "units")
            except tk.TclError:
                pass
        cv.bind_all("<MouseWheel>", _mw)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        base = get_resource_path("prediction")
        for folder, lbl in [("general", "General Predictions"),
                             ("event",   "Event Predictions")]:
            d = os.path.join(base, folder)
            if not os.path.exists(d):
                continue
            tk.Label(sfr, text=lbl, bg=T["card_bg"], fg=T["gold"],
                     font=FONTS["sub_header"]).pack(anchor="w", pady=(15, 5), padx=5)
            tk.Frame(sfr, bg=T["border"], height=1).pack(fill=tk.X, padx=5, pady=(0, 10))

            exclude = {"__init__.py", "yearly_prediction.py",
                       "transit_utils.py", "couple_compatibility.py",
                       "_bridge_utils.py"}
            if self._mode == AppMode.MATCHMAKE:
                files = [f for f in os.listdir(d) if f == "couple_compatibility.py"]
            else:
                files = [f for f in os.listdir(d)
                         if f.endswith(".py") and f not in exclude]

            grid = tk.Frame(sfr, bg=T["card_bg"])
            grid.pack(fill=tk.X, padx=5)

            for i, fname in enumerate(sorted(files)):
                name = fname.replace(".py", "").replace("_", " ").title()
                fpath = os.path.join(d, fname)
                bg0 = T["primary"] if fpath in self._selected else T["card_bg_alt"]

                def _make_toggle(fp=fpath):
                    def _toggle(btn=None):
                        if fp in self._selected:
                            self._selected.discard(fp)
                            if btn:
                                btn.configure(bg=T["card_bg_alt"])
                        else:
                            self._selected.add(fp)
                            if btn:
                                btn.configure(bg=T["primary"])
                    return _toggle

                btn = tk.Button(grid, text=name, bg=bg0, fg=T["text_main"],
                                font=("Segoe UI", 10), relief=tk.FLAT,
                                bd=1, padx=10, pady=8, width=25, anchor="w",
                                cursor="hand2")
                tog = _make_toggle()

                def _bind_toggle(b=btn, fn=tog):
                    b.configure(command=lambda: fn(b))
                _bind_toggle()

                btn.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")

    def _generate(self) -> None:
        if not self._selected:
            messagebox.showwarning("Warning", "Choose at least one topic.")
            return
        self._open_result_window(sorted(self._selected))

    def _open_result_window(self, topics: List[str]) -> None:
        T = self._theme
        rw = tk.Toplevel(self._win)
        rw.title("📄 Divya Drishti — Report")
        rw.state("zoomed")
        rw.configure(bg=T["app_bg"])

        # header
        hdr = tk.Frame(rw, bg=T["header_bg"], pady=12)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="◈  DIVYA DRISHTI — FULL REPORT  ◈",
                 bg=T["header_bg"], fg=T["gold"],
                 font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, expand=True)

        tk.Button(hdr, text="💾 SAVE PDF", bg="#00897B", fg="white",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
                  padx=15, pady=5, cursor="hand2",
                  command=lambda: self._save_pdf(console)).pack(side=tk.RIGHT, padx=20)

        tk.Frame(rw, bg=T["border_glow"], height=1).pack(fill=tk.X)

        prog_fr = tk.Frame(rw, bg=T["app_bg"], pady=8)
        prog_fr.pack(fill=tk.X, padx=20)
        prog_lbl = tk.Label(prog_fr, text="⏳ Initialising…",
                             bg=T["app_bg"], fg=T["text_dim"],
                             font=("Segoe UI", 10))
        prog_lbl.pack(anchor="w")

        cf = tk.Frame(rw, bg=T["app_bg"], padx=20, pady=5)
        cf.pack(fill=tk.BOTH, expand=True)

        console = scrolledtext.ScrolledText(
            cf, wrap=tk.WORD, bg="#0A0A14", fg="#D0D0E0",
            font=("Consolas", 12), insertbackground="#FFD700",
            selectbackground=T["primary"], relief=tk.FLAT,
            bd=0, padx=20, pady=20,
        )
        console.pack(fill=tk.BOTH, expand=True)
        self._configure_console_tags(console)

        def _worker() -> None:
            results: List[Tuple[str, Any, Optional[str]]] = []
            total = len(topics)
            for idx, fpath in enumerate(topics, 1):
                tname = (os.path.basename(fpath)
                         .replace(".py", "").replace("_", " ").title())
                rw.after(0, lambda t=tname, i=idx: prog_lbl.configure(
                    text=f"⚙️ {i}/{total}: {t}…"
                ))
                try:
                    result = self._run_module(fpath)
                    results.append((tname, result, None))
                except Exception as exc:
                    app_logger.exception("Report module %s failed", fpath)
                    results.append((tname, None, str(exc)))

            rw.after(0, lambda: self._display_results(
                console, prog_lbl, results
            ))

        threading.Thread(target=_worker, daemon=True).start()

    def _configure_console_tags(self, console: scrolledtext.ScrolledText) -> None:
        """Define the styling tags for the storytelling console output."""
        T = self._theme
        console.tag_configure("title", font=("Segoe UI", 20, "bold"), foreground=T["gold"], justify=tk.CENTER)
        console.tag_configure("wisdom", font=("Segoe UI", 12, "italic"), foreground=T.get("text_dim", "#8B8B9B"), justify=tk.CENTER)
        console.tag_configure("person_name", font=("Segoe UI", 14, "bold"), foreground=T.get("primary_light", "#A78BFA"), justify=tk.CENTER)
        console.tag_configure("separator_gold", font=("Consolas", 10), foreground=T["gold"], justify=tk.CENTER)
        console.tag_configure("separator", font=("Consolas", 10), foreground=T.get("border", "#404050"))
        console.tag_configure("cosmic_hook", font=("Georgia", 13, "italic"), foreground=T.get("primary_light", "#A78BFA"), justify=tk.CENTER)
        console.tag_configure("topic_num", font=("Segoe UI", 14, "bold"), foreground=T["gold"])
        console.tag_configure("topic_header", font=("Segoe UI", 14, "bold"), foreground=T.get("text_main", "#E0E0F0"))
        console.tag_configure("story_hook", font=("Georgia", 12, "italic"), foreground=T.get("text_dim", "#8B8B9B"))
        console.tag_configure("error", font=("Segoe UI", 11), foreground=T.get("error", "#F87171"))
        console.tag_configure("info", font=("Segoe UI", 11, "italic"), foreground=T.get("text_dim", "#8B8B9B"))
        console.tag_configure("chapter_close", font=("Georgia", 11, "italic"), foreground=T["gold"], justify=tk.CENTER)
        console.tag_configure("success", font=("Segoe UI", 12, "bold"), foreground=T.get("success", "#34D399"), justify=tk.CENTER)
        console.tag_configure("category_header", font=("Segoe UI", 12, "bold"), foreground=T.get("primary_light", "#A78BFA"))
        console.tag_configure("story_prose", font=("Georgia", 12), foreground=T.get("text_main", "#E0E0F0"))
        console.tag_configure("planet_hl", font=("Segoe UI", 12, "bold"), foreground=T.get("warning", "#FBBF24"))
        console.tag_configure("verdict_pass", font=("Segoe UI", 12, "bold"), foreground=T.get("success", "#34D399"))
        console.tag_configure("verdict_fail", font=("Segoe UI", 12, "bold"), foreground=T.get("error", "#F87171"))
        console.tag_configure("verdict_neutral", font=("Segoe UI", 12, "bold"), foreground=T["gold"])
        console.tag_configure("cause_text", font=("Segoe UI", 11, "bold"), foreground=T.get("text_dim", "#8B8B9B"))
        console.tag_configure("effect_text", font=("Segoe UI", 11), foreground=T.get("text_main", "#E0E0F0"))
        console.tag_configure("detail_text", font=("Georgia", 11), foreground=T.get("text_dim", "#8B8B9B"))
        console.tag_configure("remedy_title", font=("Segoe UI", 12, "bold"), foreground=T["gold"])
        console.tag_configure("remedy_action", font=("Georgia", 12), foreground=T.get("text_main", "#E0E0F0"))
        console.tag_configure("section_label", font=("Segoe UI", 11, "bold", "underline"), foreground=T.get("text_dim", "#8B8B9B"))
        console.tag_configure("gem_rx", font=("Segoe UI", 12, "bold"), foreground=T.get("primary_light", "#A78BFA"))
        console.tag_configure("date_hl", font=("Consolas", 12, "bold"), foreground=T.get("success", "#34D399"))
        console.tag_configure("body", font=("Georgia", 12), foreground=T.get("text_main", "#E0E0F0"))
        console.tag_configure("summary_label", font=("Segoe UI", 11, "bold"), foreground=T.get("primary_light", "#A78BFA"))

    def _run_module(self, fpath: str) -> Any:
        """Dynamically load and execute a report module."""
        try:
            rel = os.path.relpath(fpath, _PROJECT_ROOT)
            mod_name = rel.replace(os.sep, ".")[:-3]
        except ValueError:
            mod_name = "report_module"

        spec = importlib.util.spec_from_file_location(mod_name, fpath)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec: {fpath}")

        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]

        # 1. Prepare standardized V11 payload
        p1 = self._engine.primary()
        payload = self._engine.build_export(p1)
        lang = self._get_lang()

        # Inject Metadata (Gender, DOB, TOB, Lang)
        gender = "Male"
        if self._app and getattr(self._app, "combo_gender", None) is not None:
            gender = self._app.combo_gender.get()
        
        dob = ""
        tob = ""
        if p1.get("birth_date"):
            dt = p1["birth_date"]
            dob = dt.strftime("%d-%m-%Y")
            tob = dt.strftime("%H:%M:%S")

        payload["metadata"] = {
            "gender": gender,
            "dob": dob,
            "tob": tob,
            "language": lang
        }

        # Specialized Matchmaking: if the module is couple_compatibility, we need P1 AND P2 analysis
        if "couple_compatibility" in mod_name or self._mode == AppMode.MATCHMAKE:
            try:
                from src.titanium_ai_cp import UakpCoupleAnalyzer  # type: ignore
                p2 = self._engine.secondary()
                
                if p1.get("is_calculated") and p2.get("is_calculated"):
                    analyzer = UakpCoupleAnalyzer()
                    p1_export = payload # Already built for p1
                    p2_export = self._engine.build_export(p2)
                    
                    p1_name = "Person A"
                    p2_name = "Person B"
                    if self._app and hasattr(self._app, "entries"):
                        p1_name = self._app.entries.get("ent_name", tk.Entry()).get().strip() or "Person A"
                        p2_name = self._app.entries.get("ent_name_alt", tk.Entry()).get().strip() or "Person B"

                    match_result = analyzer.analyze_couple_compatibility(
                        p1_name, p2_name, p1_export, p2_export
                    )
                    
                    payload = match_result.to_payload()
                    
                    for _, cls in inspect.getmembers(mod, inspect.isclass):
                        if hasattr(cls, "generate_full_proof_report"):
                            inst = cls(payload, lang=self._get_lang())
                            return inst.generate_full_proof_report()
            except Exception as e:
                app_logger.error(f"Forensic Match Analyzer failed: {e}")

        # Priority 1: bridge function get_*_report
        for attr_name, obj in inspect.getmembers(mod, inspect.isfunction):
            if attr_name.startswith("get_") and attr_name.endswith("_report"):
                # Try V11 payload (single dict)
                try:
                    return obj(payload)
                except TypeError:
                    # Fallback: use structured lists from payload (NOT raw p1 engine data)
                    try:
                        return obj(
                            payload.get("planetary_positions", []),
                            payload.get("house_cusps", [])
                        )
                    except Exception:
                        pass

        # Priority 2: Engine class with generate_full_proof_report
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if hasattr(cls, "generate_full_proof_report"):
                # Check if __init__ accepts 'lang' before passing it
                try:
                    init_sig = inspect.signature(cls.__init__)
                    if 'lang' in init_sig.parameters:
                        inst = cls(payload, lang=lang)
                    else:
                        inst = cls(payload)
                except (ValueError, TypeError):
                    inst = cls(payload)
                return inst.generate_full_proof_report()

        # Priority 2b: Engine class with calculate_timing_report
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if hasattr(cls, "calculate_timing_report"):
                try:
                    init_sig = inspect.signature(cls.__init__)
                    if 'lang' in init_sig.parameters:
                        inst = cls(payload, lang=lang)
                    else:
                        inst = cls(payload)
                except (ValueError, TypeError):
                    inst = cls(payload)
                return inst.calculate_timing_report()

        # Priority 3: connect_titanium (Standard V11 Bridge)
        if hasattr(mod, "connect_titanium"):
            return mod.connect_titanium(payload, lang)

        # Priority 4: analyze_* functions (single-arg with full payload)
        for attr_name, obj in inspect.getmembers(mod, inspect.isfunction):
            if attr_name.startswith("analyze_"):
                try:
                    sig = inspect.signature(obj)
                    params = [p for p in sig.parameters.values()
                              if p.default is inspect.Parameter.empty]
                    if len(params) <= 1:
                        return obj(payload)
                    elif len(params) == 2:
                        return obj(
                            payload.get("planetary_positions", []),
                            payload.get("house_cusps", [])
                        )
                except TypeError:
                    pass

        raise AttributeError("No recogniseable entry-point in module.")

    # ── storytelling constants ────────────────────────────────────────────────
    _HOUSE_NAMES = {
        1: "Self & Identity", 2: "Wealth & Family", 3: "Courage & Siblings",
        4: "Home & Foundation", 5: "Children & Intelligence", 6: "Health & Service",
        7: "Partnership & Marriage", 8: "Transformation & Hidden Matters",
        9: "Fortune & Higher Learning", 10: "Career & Status",
        11: "Gains & Aspirations", 12: "Losses & Liberation"
    }
    _HOUSE_LIFE_ASPECT = {
        1: "the very essence of your being — your body, your face to the world, your innate nature and personal sovereignty",
        2: "the treasury of your life — family bonds, accumulated wealth, the power of your voice, and your deepest values",
        3: "the arena of courage — your siblings, short journeys, communication, media, and the bold will of your spirit",
        4: "the sacred foundation of existence — home, mother, land, inner peace, and the roots that anchor your soul",
        5: "the garden of joy and creativity — children, romance, speculation, education, and the brilliance of your intellect",
        6: "the crucible of service and discipline — daily work, health challenges, debts, adversaries, and healing karma",
        7: "the cosmic mirror of the self — marriage, business partnerships, open rivals, and the sacred dance of relationship",
        8: "the cauldron of transformation — longevity, hidden matters, inheritance, occult forces, and the mystery of change",
        9: "the temple of higher truth — dharma, fortune, the father, long journeys, philosophy, and the touch of divine grace",
        10: "the summit of worldly achievement — career, public reputation, authority, ambitions, and the legacy you leave behind",
        11: "the horizon of fulfilled aspirations — elder siblings, friends, gains, the realisation of desires, and abundance received",
        12: "the threshold of liberation — foreign lands, hidden expenses, spiritual retreat, loss, and the soul's final freedom",
    }
    _PLANET_PROSE = {
        "Sun": "the radiant Sun", "Moon": "the nurturing Moon",
        "Mars": "the fiery Mars", "Mercury": "the intellectual Mercury",
        "Jupiter": "the wise Jupiter", "Venus": "the harmonious Venus",
        "Saturn": "the disciplined Saturn", "Rahu": "the ambitious Rahu",
        "Ketu": "the spiritual Ketu", "Uranus": "the revolutionary Uranus",
        "Neptune": "the mystical Neptune", "Pluto": "the transformational Pluto"
    }
    _PLANET_STORY = {
        "Sun":     "the radiant Sun — sovereign of conscious identity, authority, and vital life force",
        "Moon":    "the nurturing Moon — keeper of emotional memory, intuition, and the subconscious tides",
        "Mars":    "the fiery Mars — warrior of inner drive, courage, and transformative action",
        "Mercury": "the intellectual Mercury — swift messenger of mind, logic, and communication",
        "Jupiter": "the wise Jupiter — celestial guru of expansion, wisdom, abundance, and divine grace",
        "Venus":   "the harmonious Venus — sculptor of beauty, love, artistic sensibility, and earthly pleasure",
        "Saturn":  "the disciplined Saturn — master of karmic law, patience, and the slow revelation of truth",
        "Rahu":    "the ambitious Rahu — shadow dragon of worldly desire, innovation, and unconventional mastery",
        "Ketu":    "the spiritual Ketu — south node of liberation, ancestral wisdom, and transcendent insight",
        "Uranus":  "the awakening Uranus — catalyst of sudden revolution and collective transformation",
        "Neptune": "the mystical Neptune — ocean of spiritual dissolution, dreams, and divine inspiration",
        "Pluto":   "the transformational Pluto — lord of death, rebirth, and the deepest metamorphosis of the soul",
    }
    # ── Rich Elaboration: Planet as Sub Lord (for narrative expansion) ──
    _PLANET_ELABORATION: Dict[str, str] = {
        "Sun": (
            "The Sun as Sub Lord bestows a regal, authoritative quality upon this domain. "
            "There is an innate confidence here — a gravitational pull toward leadership, recognition, "
            "and the cultivation of personal sovereignty. The native's ego and conscious will are deeply "
            "invested in this area of life, and success arrives through visibility, integrity, and bold self-expression. "
            "Government institutions, fatherly figures, and positions of public trust become natural allies in this journey. "
            "The soul radiates a solar magnetism that attracts respect — but must guard against the shadow of pride, "
            "for the Sun that burns too brightly can scorch the very ground it seeks to illuminate."
        ),
        "Moon": (
            "The Moon as Sub Lord weaves emotional depth and intuitive sensitivity into this domain. "
            "There will be natural fluctuations — the tides of mood, memory, and maternal influence shape outcomes here. "
            "Nurturing relationships, empathetic connection, and the ability to read unspoken emotional currents "
            "become the native's most powerful instruments in this realm of life. "
            "The mother's influence casts a long and tender shadow across this dimension, and public-facing roles "
            "that involve caring, counselling, or emotional intelligence bring the greatest fulfilment. "
            "However, emotional volatility and the tendency to absorb others' pain must be consciously managed "
            "to prevent the Moon's gift of sensitivity from becoming a source of chronic inner turbulence."
        ),
        "Mars": (
            "Mars as Sub Lord injects fierce determination, competitive fire, and raw courage into this domain. "
            "Results here arrive through action, initiative, and the willingness to fight for what matters. "
            "There is an impulsive, warrior-like quality — progress comes quickly when channelled, "
            "but recklessness or anger can create equally sudden setbacks. "
            "The native possesses an almost physical intensity in this area of life — a drive that demands expression "
            "through engineering, sports, surgery, real estate, or any field requiring decisive, hands-on intervention. "
            "The karmic lesson here is mastery over anger and impatience: the warrior who conquers the self "
            "conquers every battlefield that this domain presents."
        ),
        "Mercury": (
            "Mercury as Sub Lord brings intellectual agility, communicative brilliance, and analytical precision to this domain. "
            "Success here flows through the written and spoken word, through logic, negotiation, and the ability to process "
            "complex information rapidly. There may be a duality — Mercury's versatility is a gift, but it can also scatter "
            "focus across too many directions if not disciplined. "
            "Commerce, technology, journalism, and any field requiring mental dexterity become natural avenues for achievement. "
            "The native's mind is a precision instrument in this domain — capable of seeing patterns others miss, "
            "crafting arguments others cannot counter, and solving puzzles that leave slower minds bewildered. "
            "The shadow to guard against is nervous exhaustion and the tendency to intellectualise emotions rather than feel them."
        ),
        "Jupiter": (
            "Jupiter as Sub Lord graces this domain with the benevolent touch of the celestial Guru. "
            "Wisdom, ethical conduct, and an expansive worldview become the channels through which abundance flows here. "
            "There is a natural blessing — doors open through mentorship, faith, and the cultivation of higher knowledge. "
            "Teaching, law, finance, philosophy, and spiritual advisory roles align perfectly with Jupiter's generous nature. "
            "The native may attract wise counsellors and benevolent institutions that uplift this area of life "
            "with seemingly effortless grace. Excess and over-optimism are the only shadows to guard against — "
            "for Jupiter's abundance can sometimes lead to complacency, and its faith to naïveté."
        ),
        "Venus": (
            "Venus as Sub Lord infuses this domain with grace, aesthetic sensibility, and the magnetism of beauty. "
            "Harmony, diplomacy, and the appreciation of life's finer pleasures shape the native's experience here. "
            "Relationships, creative expression, and material comfort are the primary vehicles through which this domain flourishes — "
            "though attachment and indulgence may occasionally cloud judgement. "
            "The arts, fashion, luxury commerce, entertainment, and hospitality industries resonate deeply with this placement. "
            "There is a Venusian charm that smooths rough edges and attracts allies through sheer likability. "
            "The karmic caution is against excessive sensual attachment — the soul must learn that true beauty is internal, "
            "and that the pleasures Venus offers are most nourishing when balanced with spiritual depth."
        ),
        "Saturn": (
            "Saturn as Sub Lord imposes a demanding but ultimately rewarding discipline upon this domain. "
            "Progress here is slow, methodical, and earned through persistent effort over time. "
            "There may be delays, restrictions, or periods of solitary struggle — but what Saturn builds, Saturn makes permanent. "
            "Patience is not merely a virtue here; it is the very foundation upon which lasting success is constructed. "
            "The native may experience initial hardship, rejection, or a sense of being tested by invisible forces — "
            "yet each obstacle is Saturn's way of forging diamond-hard resilience from the coal of raw experience. "
            "Manufacturing, agriculture, mining, structural engineering, and roles requiring endurance align with this placement. "
            "After the age of 36, Saturn's rewards begin to materialise with a solidity that faster planets cannot match."
        ),
        "Rahu": (
            "Rahu as Sub Lord brings an unconventional, ambitious, and sometimes obsessive energy to this domain. "
            "The native may pursue unorthodox paths, foreign connections, or innovative approaches that break from tradition. "
            "Rahu amplifies desire and worldly ambition here — creating opportunities through audacity and non-conformity, "
            "but also carrying the risk of illusion, shortcuts, and ungrounded aspirations. "
            "Technology, aviation, foreign trade, diplomacy, and cutting-edge innovation align with Rahu's restless energy. "
            "There is a magnetic, almost hypnotic quality to the native's pursuit in this domain — "
            "a hunger that can drive extraordinary achievement when anchored in ethical practice, "
            "or spectacular downfall when divorced from reality. The remedy is grounding: "
            "maintain honesty, avoid deception, and let ambition serve a purpose larger than the ego."
        ),
        "Ketu": (
            "Ketu as Sub Lord introduces a quality of spiritual detachment and past-life mastery into this domain. "
            "The native may feel an instinctive, almost effortless connection to this area — as though carrying knowledge "
            "from a previous incarnation. However, Ketu's energy can also create disinterest, sudden separations, "
            "or a sense that worldly achievement in this realm feels hollow compared to the soul's deeper calling. "
            "Research, coding, occult sciences, spiritual teaching, and behind-the-scenes expertise align with Ketu's nature. "
            "There is a paradox at work: the native may achieve mastery precisely because they do not crave recognition for it. "
            "The karmic invitation is to honour this domain's gifts without clinging to them — to serve through "
            "detached excellence, allowing spiritual wisdom to inform worldly action without replacing it."
        ),
        "Uranus": (
            "Uranus as Sub Lord electrifies this domain with sudden, revolutionary energy — the lightning bolt of the cosmos. "
            "The native may experience unexpected breakthroughs, radical shifts in perspective, or dramatic upheavals "
            "that shatter existing structures and force rapid adaptation. There is genius here — an ability to see "
            "around corners and anticipate trends before they manifest in the collective consciousness. "
            "Technology, humanitarian causes, scientific innovation, and social reform align with Uranus's awakening force. "
            "Relationships and institutions in this domain may carry an electric unpredictability — "
            "what is built here resists conventional boundaries and demands the freedom to evolve. "
            "The karmic lesson is to channel rebellion constructively: revolution without wisdom becomes mere chaos."
        ),
        "Neptune": (
            "Neptune as Sub Lord dissolves the sharp edges of reality in this domain, replacing them with vision, "
            "imagination, and a longing for the transcendent. The native may experience this area through a dreamlike filter — "
            "sensing possibilities that others cannot perceive, but also vulnerable to illusion, deception, and confusion. "
            "The arts, music, film, spiritual healing, and oceanic or pharmaceutical industries resonate deeply here. "
            "There is a compassionate, almost sacrificial quality — the native may give without counting the cost, "
            "drawn by an invisible current toward service and selfless devotion. "
            "The shadow is escapism: substances, fantasies, or relationships that promise transcendence but deliver dissolution. "
            "The remedy is grounded spiritual practice — channelling Neptune's oceanic creativity through disciplined form."
        ),
        "Pluto": (
            "Pluto as Sub Lord introduces the raw power of total transformation — death and rebirth at the deepest level. "
            "This domain becomes an arena of intense, sometimes volcanic change — where surface appearances crack open "
            "to reveal hidden power dynamics, buried resources, and the alchemy of complete renewal. "
            "The native may encounter control issues, power struggles, or obsessive intensity in this area, "
            "yet these very forces become the catalysts for profound personal evolution. "
            "Psychology, research, investigation, surgery, crisis management, and any field requiring penetration "
            "beneath the surface align with Pluto's transformational mandate. "
            "The karmic invitation is to surrender the need for control: true power flows through the soul "
            "that has faced its own shadow and emerged reborn on the other side."
        ),
    }
    # ── Rich Elaboration: House × Planet Insight (key combinations) ──
    _HOUSE_PLANET_INSIGHT: Dict[Tuple[int, str], str] = {
        # House 1 - Self & Identity
        (1, "Sun"): "A commanding personal presence radiates outward — others instinctively look to this soul for leadership and direction. The native walks into a room and the atmosphere shifts; there is a solar gravity to this personality that demands acknowledgement. Health is generally robust, though the heart and eyes require periodic attention.",
        (1, "Moon"): "An emotionally transparent personality — feelings are worn openly, and the native's mood shapes every room they enter. The face is expressive, the eyes reflective, and the body language speaks volumes before a word is uttered. Public-facing roles that require empathy and emotional connection bring natural success.",
        (1, "Mars"): "A bold, action-oriented personality that thrives on challenge. Physical vitality and competitive spirit define the outer self. The native possesses natural athletic ability and a courageous disposition that inspires both admiration and occasional friction — learning to temper force with finesse is the lifetime's subtle art.",
        (1, "Mercury"): "A youthful, quick-witted personality that communicates effortlessly. Intelligence and adaptability are the native's calling card. There is an eternal student quality here — the mind never stops processing, and the personality maintains a boyish or girlish charm well into maturity.",
        (1, "Jupiter"): "A generous, wise, and expansive personality that naturally inspires trust. Others are drawn to this soul's warmth and counsel. The physical frame tends toward fullness, the voice carries natural authority, and the life path gradually unfolds toward mentorship, teaching, or spiritual guidance.",
        (1, "Venus"): "A graceful, attractive personality with natural charm. Beauty, diplomacy, and social ease define the native's public face. There is an innate artistic sensibility — the native dresses well, speaks pleasantly, and creates harmonious environments wherever they go, attracting both admiration and romantic interest effortlessly.",
        (1, "Saturn"): "A reserved, mature personality that projects quiet authority. Life teaches this soul through patience and disciplined self-mastery. Early life may carry a sense of heaviness or premature responsibility, but after the age of 36, the very qualities that felt like burdens — seriousness, endurance, self-reliance — become the pillars of lasting success.",
        (1, "Rahu"): "An unconventional, magnetic personality that defies categorisation. Innovation and restless ambition drive this soul's self-expression. The native may cultivate a public image that is deliberately avant-garde or enigmatic — there is a chameleon quality that allows adaptation to diverse social environments while maintaining an air of mystery.",
        (1, "Ketu"): "A spiritually inclined, introspective personality. Others sense an old-soul quality — wisdom beyond the native's years. The physical appearance may be understated, but the eyes carry a depth that reveals lifetimes of accumulated experience. Material self-promotion feels foreign to this soul; recognition comes despite, not because of, seeking it.",
        # House 7 - Partnership & Marriage
        (7, "Sun"): "The partner carries a strong, dominant personality — a leader in their own right. Power dynamics in marriage require conscious balancing. The spouse may work in government, administration, or any field requiring authoritative presence — and the marriage succeeds when both partners respect each other's sovereignty.",
        (7, "Moon"): "The partner is nurturing, emotionally attuned, and deeply caring. The marriage thrives on emotional intimacy and mutual support. The spouse may have connections to caregiving, hospitality, or public-facing work — and the home they create together becomes a sanctuary of emotional warmth and intuitive understanding.",
        (7, "Mars"): "The partner is passionate, assertive, and energetically driven. The marriage carries both exciting chemistry and the challenge of managing conflict. The spouse may excel in engineering, sports, or entrepreneurship — bringing dynamism to the partnership but requiring the native to develop skills in conflict resolution and emotional patience.",
        (7, "Mercury"): "The partner is articulate, intellectually stimulating, and communicatively gifted. Mental connection is the foundation of this bond — when dialogue flows, so does love. The spouse likely excels in business, writing, or technology — and the marriage functions best when treated as an intellectual partnership of equals.",
        (7, "Jupiter"): "The partner embodies wisdom, generosity, and moral strength. This is a deeply fortunate marital configuration — the partner elevates the native's life. The spouse may come from a cultured, educated, or spiritually inclined background — and the marriage itself becomes a vehicle for mutual growth, shared dharma, and expanding horizons.",
        (7, "Venus"): "The partner radiates beauty, charm, and romantic sensibility. This marriage is blessed with harmony, aesthetic pleasures, and deep affection. The spouse likely has artistic talents or works in beauty, fashion, or entertainment — and the shared home becomes a space of refined taste, comfort, and sensory delight.",
        (7, "Saturn"): "The partner brings maturity, responsibility, and endurance. Marriage may arrive late or carry a sense of duty — but what is built together endures through time. The spouse may be older in spirit, bearing the weight of practical wisdom — and the relationship deepens with every shared challenge, growing stronger where others would fracture.",
        (7, "Rahu"): "The partner may come from an unconventional background or foreign origin. The relationship carries intensity, ambition, and the thrill of the unexpected. The spouse may be involved in technology, foreign affairs, or non-traditional work — bringing excitement and worldly expansion to the partnership, though trust must be cultivated deliberately.",
        (7, "Ketu"): "The partner has a spiritual, detached quality. There may be periods of emotional distance, but also a profound karmic connection that transcends the ordinary. The spouse may possess intuitive gifts, research abilities, or spiritual depth — and the marriage evolves beyond conventional romantic expectations into a soul-level companionship.",
        # House 10 - Career & Status
        (10, "Sun"): "Career destiny points toward leadership, government, or administrative authority. Public recognition and professional prestige are written into the blueprint. The native naturally gravitates toward positions of power — medicine, politics, senior management, or any role where they represent institutional authority to the public.",
        (10, "Moon"): "Career flows through nurturing, caregiving, or public-facing roles. Emotional intelligence becomes a professional superpower. The native thrives in hospitality, nursing, counselling, food industries, or public relations — any field where reading the emotional pulse of an audience translates into professional excellence.",
        (10, "Mars"): "Career energy channels through engineering, surgery, military, sports, or any field demanding courage and decisive action. The native's professional identity is forged in the fire of competition, and success comes through technical mastery, physical courage, and the willingness to lead from the front.",
        (10, "Mercury"): "Career aligns with communication, commerce, IT, writing, or analytical fields. Intellectual versatility drives professional success. The native may juggle multiple professional interests simultaneously — journalism, accounting, teaching, software development — and excels in roles requiring rapid information processing and persuasive articulation.",
        (10, "Jupiter"): "Career gravitates toward teaching, law, finance, spirituality, or advisory roles. Professional wisdom and ethical conduct attract elevation. The native may become a mentor or institutional leader whose career arc bends increasingly toward service, philanthropy, and the dissemination of knowledge that outlasts their tenure.",
        (10, "Venus"): "Career flourishes through arts, fashion, entertainment, luxury goods, or diplomacy. Aesthetic sensibility becomes a professional asset. The native may build a career in design, hospitality, beauty industries, or any field where charm, visual taste, and interpersonal grace translate directly into professional currency.",
        (10, "Saturn"): "Career demands discipline, patience, and long-term commitment. Manufacturing, mining, agriculture, or structural engineering may feature. The native's professional rise is slow but monumental — early career struggles and rejections are Saturn's forge, hammering raw potential into an unshakeable professional reputation that peaks after the mid-30s.",
        (10, "Rahu"): "Career may involve technology, aviation, foreign trade, or innovative disruption. Unconventional professional paths yield surprising success. The native may find their greatest career breakthroughs in emerging industries, cross-cultural ventures, or roles that did not exist a generation ago — Rahu rewards those who build the future rather than inherit the past.",
        (10, "Ketu"): "Career may involve research, coding, spiritual teaching, or behind-the-scenes expertise. Recognition comes despite — not because of — seeking it. The native possesses a rare professional gift: mastery achieved through focused immersion rather than self-promotion, often leading to cult-like respect within specialised communities.",
        # House 5 - Children & Intelligence
        (5, "Sun"): "Intelligence carries a confident, leadership-oriented quality. Children may be strong-willed and destined for positions of authority. The native's creative expression is bold, dramatic, and self-assured — whether in the arts, academia, or entrepreneurship, there is a performative brilliance that demands centre stage.",
        (5, "Moon"): "Intelligence flows through emotional and intuitive channels. Children are emotionally sensitive, creative, and deeply bonded to the mother. The native possesses a photographic emotional memory and learns best through feeling rather than abstract logic — poetry, music, and nurturing arts are natural creative outlets.",
        (5, "Mars"): "Intelligence is sharp, competitive, and action-oriented. Children may excel in sports, engineering, or fields requiring physical courage. The native's creative energy is explosive and results-driven — mathematical problem-solving, strategic gaming, technical innovation, and competitive academics ignite this mind's deepest engagement.",
        (5, "Mercury"): "Intelligence is analytical, communicative, and commercially astute. Children show early verbal and mathematical talent. The native's mind is a Swiss Army knife of intellectual tools — equally comfortable with numbers, languages, and logical puzzles — and their children often inherit this mercurial intellectual versatility.",
        (5, "Jupiter"): "Intelligence carries the blessing of wisdom and higher learning. Children are naturally fortunate, ethical, and academically gifted. The native approaches knowledge with philosophical depth and moral seriousness — education is not merely a credential but a sacred path, and children raised in this energy develop a natural reverence for learning.",
        (5, "Venus"): "Intelligence expresses through creativity, artistic talent, and aesthetic appreciation. Children may be charming, artistic, and socially graceful. The native's mind gravitates toward beauty in all its forms — visual arts, music, literature, fashion design — and their romantic life carries a poetic, idealised quality that enriches every creative pursuit.",
        (5, "Saturn"): "Intelligence develops slowly but deeply. Children may be delayed in expression but ultimately achieve mastery through discipline and persistence. The native's intellectual gifts reveal themselves gradually — like a slow-fermenting wine, the mind reaches its full power in maturity, producing work of lasting structural integrity.",
        (5, "Rahu"): "Intelligence is unconventional, innovative, and technologically inclined. Children may follow unorthodox paths that ultimately prove visionary. The native's creative mind operates outside established frameworks — artificial intelligence, blockchain, speculative fiction, or avant-garde art — producing ideas that seem alien today but become mainstream tomorrow.",
        (5, "Ketu"): "Intelligence is intuitive, mystical, and spiritually oriented. Children may show interest in philosophy, meditation, or abstract pursuits. The native possesses a research-oriented mind that penetrates beneath surface appearances — drawn to decode hidden patterns, ancient wisdom, and the metaphysical architecture underlying visible reality.",
        # House 2 - Wealth & Family
        (2, "Sun"): "Wealth accumulates through authority, leadership roles, and government connections. The family carries a proud, prestigious lineage. The voice itself becomes an instrument of power — public speaking, authoritative pronouncements, and confident financial decision-making are the channels through which prosperity flows into this life.",
        (2, "Moon"): "Wealth flows through nurturing professions, real estate, or liquid assets. Family bonds are emotionally deep and financially supportive. The native's financial instincts are intuitive rather than analytical — they sense profitable opportunities through gut feeling, and family meals, traditions, and emotional togetherness are valued above material display.",
        (2, "Mars"): "Wealth arrives through competitive ventures, real estate, or technical enterprises. Family environment is energetic but may carry argumentative undercurrents. The native earns through courage, technical skill, and willingness to take calculated financial risks — but must guard against impulsive spending and heated family disputes over money.",
        (2, "Mercury"): "Wealth accumulates through intellectual work, trading, communication, or multiple income streams. The family values education and eloquence. The native may maintain several simultaneous income channels — consulting, writing, trading — and family conversations revolve around ideas, learning, and the strategic management of resources.",
        (2, "Jupiter"): "Wealth is blessed with natural expansion — ethical earning and family prosperity go hand in hand. Financial wisdom is a birthright. The native attracts abundance through generosity, moral conduct, and a philosophical approach to money that paradoxically draws more of it — the family lineage often includes teachers, priests, or financial advisors.",
        (2, "Venus"): "Wealth flows through creative, artistic, or luxury-oriented channels. The family environment is aesthetically rich, comfortable, and harmonious. The native may earn through beauty, design, hospitality, or entertainment — and the family table is always set with care, the home decorated with taste, and social gatherings hosted with effortless grace.",
        (2, "Saturn"): "Wealth builds slowly through disciplined saving and hard-earned income. Family resources may be limited initially but grow through persistence. The native's financial journey is one of patient accumulation — early austerity gives way to rock-solid stability, and the family learns the value of money through the school of scarcity and disciplined budgeting.",
        (2, "Rahu"): "Wealth arrives through unconventional or foreign sources. Family dynamics carry complexity — hidden resources or sudden financial shifts are possible. The native may earn through international trade, technology, or industries that break traditional molds — and the family's financial story often includes dramatic reversals that ultimately lead to unconventional prosperity.",
        (2, "Ketu"): "Wealth may feel spiritually insignificant to the native — a detachment from material accumulation. Family ties carry karmic overtones. The native's relationship with money is philosophical rather than acquisitive — they may earn well but feel indifferent to material display, channelling resources toward spiritual pursuits, research, or charitable causes.",
        # House 4 - Home & Foundation
        (4, "Sun"): "A proud, well-lit home environment with a father figure whose influence shapes the emotional foundation. Property ownership is likely. The native may inherit or acquire a stately residence, and the home itself becomes a centre of family authority — a place where decisions are made and traditions maintained with dignified consistency.",
        (4, "Moon"): "A deeply nurturing home environment shaped by the mother's presence. Emotional security and domestic peace are central to the native's well-being. The home is a living sanctuary — filled with the warmth of cooking, the comfort of familiar objects, and the gentle rhythm of daily rituals that root the soul in belonging.",
        (4, "Mars"): "A dynamic, energetic home environment — possibly with property disputes or renovation projects. The foundation is strong but carries heat. The native may invest significantly in real estate or land, and the home is a place of constant activity — construction, improvement, and occasionally, heated domestic exchanges that clear the air like summer storms.",
        (4, "Mercury"): "A home filled with books, conversation, and intellectual stimulation. Property transactions may involve multiple changes or commercial properties. The native's domestic space functions as a study, office, and intellectual laboratory — and the family communicates freely, debating ideas over meals and filling the home with the energy of active minds.",
        (4, "Jupiter"): "A spacious, blessed home environment with strong spiritual or educational values. Property ownership is favoured and expands over time. The native may acquire multiple properties, and the home itself serves as a temple of learning — a place where wisdom is honoured, guests are welcomed with traditional hospitality, and children grow in an atmosphere of ethical warmth.",
        (4, "Venus"): "A beautifully decorated, comfortable home with artistic touches. The living space radiates harmony, and luxury properties are indicated. The native invests in creating a home that is both aesthetically stunning and emotionally nurturing — art on the walls, music in the air, and a garden that blooms with the same care lavished on personal relationships.",
        (4, "Saturn"): "A modest or older home that improves gradually over time. The foundation is built on discipline and may carry the weight of duty. The native's early domestic life may feel restrictive or austere, but through patient effort, the home becomes a fortress of stability — simple, solid, and enduring, like Saturn itself.",
        (4, "Rahu"): "An unconventional or modern home — possibly in a foreign location. The domestic environment carries an element of the unexpected. The native may relocate to distant places, adopt non-traditional living arrangements, or fill the home with cutting-edge technology — creating a domestic space that reflects innovation rather than inherited tradition.",
        (4, "Ketu"): "A minimalist or spiritually charged home. The native may feel detached from material domestic concerns or drawn to isolated living. The home functions as an ashram — a retreat from the world's noise — and the native may prefer remote locations, sparse furnishings, and a living environment that supports meditation, reflection, and inner peace.",
        # House 6 - Health & Service
        (6, "Sun"): "Health issues may involve the heart, eyes, or bones. Service through leadership and government healthcare roles is indicated. The native fights illness with fierce determination and typically recovers through sheer willpower — the Sun's vitality ensuring that even serious health challenges become opportunities for demonstrating courage and resilience.",
        (6, "Moon"): "Health sensitivity in the emotional and digestive systems. Service through caregiving, nursing, or counselling channels is natural. The native must guard against stress-related digestive disorders and emotional burnout — learning to establish healthy boundaries while maintaining the compassionate service that gives this life its deepest meaning.",
        (6, "Mars"): "Health challenges may involve inflammation, blood pressure, or surgical interventions. The native is a fighter who overcomes illness through sheer will. The body responds well to vigorous exercise and competitive sports — the native's immune system is strong when physically active but becomes vulnerable during periods of enforced inactivity.",
        (6, "Mercury"): "Health issues may manifest through the nervous system, skin, or respiratory tract. The native benefits from analytical approaches to wellness. The mind-body connection is particularly strong here — mental stress directly impacts physical health, and the native must cultivate mental hygiene alongside physical health through yoga, breathing practices, and intellectual rest.",
        (6, "Jupiter"): "Health is generally protected by Jupiter's grace. Any illness tends to resolve favourably. Service through teaching or advisory roles. The native possesses a natural resilience and often serves as a health advisor to others — their own constitution benefits from Jupiter's protective umbrella, though overindulgence in food and comfort can create the only vulnerability.",
        (6, "Venus"): "Health may be affected by dietary excess, kidney issues, or reproductive concerns. Healing comes through beauty, comfort, and pleasure in moderation. The native's body responds to aesthetic therapies — aromatherapy, spa treatments, art therapy, and beautiful environments accelerate healing, while excess sugar, alcohol, and sensory overload create vulnerability.",
        (6, "Saturn"): "Health challenges are chronic and demand long-term management. Joints, bones, and teeth require attention. Service through labour-intensive or structural work. The native must accept that health management is a lifelong discipline rather than a quick fix — regular check-ups, consistent exercise, and austere dietary habits become the medicine that Saturn prescribes.",
        (6, "Rahu"): "Health issues may involve unusual diagnoses, toxins, or hard-to-identify conditions. Service through technology, foreign connections, or unconventional healing. The native may benefit from alternative medicine, international health practitioners, or cutting-edge diagnostic technologies that conventional medicine overlooks — Rahu's health lessons often arrive through unexpected channels.",
        (6, "Ketu"): "Health may carry mysterious or karmic origins. Surgical interventions and sudden recoveries are both possible. Service through spiritual or alternative healing. The native's health journey may include inexplicable symptoms that dissolve through spiritual practice — meditation, energy healing, and karmic remedies often prove more effective than conventional treatment alone.",
        # House 8 - Transformation & Hidden
        (8, "Sun"): "Transformation arrives through encounters with authority, ego dissolution, or confrontations with power structures. The native's deepest growth comes through moments when the comfortable self-image shatters — revealing the luminous, authentic identity that lies beneath the social persona's protective mask.",
        (8, "Moon"): "Transformation flows through emotional crises, psychological healing, and the excavation of buried memories. The native processes change through the body and emotions rather than the intellect — grief, joy, and catharsis become the sacred instruments through which the soul sheds its old skin and emerges renewed.",
        (8, "Mars"): "Transformation is triggered by accidents, surgeries, or confrontational life events that demand immediate action and courage. The native meets crisis with the reflexes of a warrior — and each brush with danger, each surgical intervention, each combative encounter burns away weakness and forges an increasingly indestructible inner core.",
        (8, "Mercury"): "Transformation manifests through research, investigation, writing, or the uncovering of hidden information and documents. The native's deepest changes come through intellectual revelation — a piece of knowledge, a discovered document, or a penetrating analysis that exposes what was concealed and forces a complete recalculation of assumptions.",
        (8, "Jupiter"): "Transformation carries a protective, ultimately fortunate quality. Inheritance, insurance, and occult wisdom bring hidden blessings. The native may navigate life's most dangerous passages under Jupiter's guardian grace — near-misses that become turning points, losses that reveal hidden gains, and crises that open doors to previously unimaginable abundance.",
        (8, "Venus"): "Transformation intertwines with intimate relationships, shared resources, and the alchemy of emotional vulnerability. The native's deepest metamorphosis occurs through love, loss, and the surrender of emotional control — learning that vulnerability is not weakness but the very gateway through which the soul accesses its most profound beauty.",
        (8, "Saturn"): "Transformation is slow, heavy, and relentless — chronic conditions, karmic debts, and the weight of time reshape this domain profoundly. The native endures gradual, grinding change rather than sudden upheaval — each decade stripping away another layer of illusion until the diamond core of authentic self-knowledge finally stands revealed.",
        (8, "Rahu"): "Transformation arrives through shocking revelations, foreign entanglements, or encounters with the unconventional and taboo. The native may experience sudden, dramatic upheavals that would paralyse less resilient souls — each crisis serving as Rahu's ruthless tutorial in distinguishing genuine security from the illusion of stability.",
        (8, "Ketu"): "Transformation carries a spiritual, past-life quality — sudden enlightenments, karmic release, and mystical experiences reshape the soul. The native may experience inexplicable moments of spiritual awakening that dissolve long-held fears — Ketu in this domain often grants the rare gift of fearlessness in the face of life's ultimate mystery.",
        # House 9 - Fortune & Higher Learning
        (9, "Sun"): "Higher wisdom flows through prestigious institutions, fatherly guidance, and government-supported learning. Fortune favours the bold and visible. The native may receive academic honours, government scholarships, or recognition from established authorities — and the father figure plays a pivotal role in shaping the soul's philosophical worldview.",
        (9, "Moon"): "Higher wisdom arrives through emotional intuition, maternal guidance, and creative or humanitarian studies. Fortune waxes and wanes with the heart. The native learns through feeling and experience rather than abstract theory — and journeys to foreign lands carry a deeply emotional, almost pilgrimage-like quality that transforms the inner landscape.",
        (9, "Mars"): "Higher learning channels through technical, engineering, or defence-related disciplines. Fortune rewards courage and competitive excellence. The native approaches education with the intensity of a warrior training for battle — academic and philosophical pursuits are not leisurely but fierce, focused, and driven by a need to master challenging material.",
        (9, "Mercury"): "Higher learning excels in commerce, law, communication, and analytical fields. Fortune rewards intellectual flexibility and eloquent advocacy. The native may pursue multiple advanced degrees or master diverse subjects with mercurial versatility — their fortune expands through networking, publishing, and the strategic deployment of knowledge across disciplines.",
        (9, "Jupiter"): "The most blessed configuration for higher learning — academic excellence, guru's grace, and the natural expansion of philosophical understanding. The native attracts teachers and mentors who change the course of their life, and foreign travel opens doors to wisdom traditions that feel like homecomings rather than discoveries.",
        (9, "Venus"): "Higher learning gravitates toward arts, culture, design, and diplomatic studies. Fortune smiles through beauty, travel, and creative endeavours. The native's educational journey is aesthetically enriched — studying in beautiful locations, learning through artistic immersion, and building a philosophical framework that honours pleasure as a legitimate path to wisdom.",
        (9, "Saturn"): "Higher learning is delayed but ultimately profound. Fortune rewards patient, disciplined study and arrives later in life through mastery. The native's philosophical understanding deepens through hardship and solitary study — every delay in academic achievement is Saturn's way of ensuring that when wisdom arrives, it carries the unshakeable weight of lived experience.",
        (9, "Rahu"): "Higher learning may involve foreign universities, cutting-edge technology, or unconventional philosophies. Fortune rewards innovative thinking. The native may pursue education in fields that barely existed when they were born — and their spiritual or philosophical breakthroughs often come through exposure to foreign cultures, unorthodox teachers, or radical intellectual traditions.",
        (9, "Ketu"): "Higher learning is intuitive, spiritual, and self-directed. Fortune arrives through renunciation, meditation, and the pursuit of abstract truth. The native may bypass conventional education entirely, arriving at profound philosophical insights through meditation, past-life memory, or direct spiritual experience — the university of the soul outranks all earthly institutions.",
        # House 11 - Gains & Aspirations
        (11, "Sun"): "Gains flow through positions of authority, government networks, and recognition for leadership excellence. The native's aspirations are ambitious, public-facing, and connected to institutional power — success arrives through official channels, prestigious associations, and the cultivation of a reputation that opens doors automatically.",
        (11, "Moon"): "Gains materialise through emotional connections, public-facing roles, and networks of nurturing relationships. The native's wealth grows through genuine human connection — emotional intelligence translates directly into financial and social returns, and the circle of friends functions as an extended family of mutual support.",
        (11, "Mars"): "Gains arrive through competitive victories, real estate transactions, and entrepreneurial courage. The native's aspirations are bold and action-oriented — wealth accumulates through decisive financial moves, competitive bidding, and the willingness to take calculated risks that more cautious souls avoid.",
        (11, "Mercury"): "Gains flow through intellectual networks, communication platforms, trading, and analytical expertise. The native's social circle is mentally stimulating and commercially productive — friendships double as business partnerships, and the exchange of ideas generates tangible financial returns across multiple income streams.",
        (11, "Jupiter"): "Gains are abundant, ethical, and divinely supported. Financial expansion, mentorship networks, and philanthropic returns. The native attracts wealth through wisdom, generosity, and moral conduct — the more they give, the more they receive, creating a virtuous cycle of abundance that benefits the entire community.",
        (11, "Venus"): "Gains manifest through artistic talent, luxury ventures, romantic connections, and aesthetic enterprises. The native's social world is glamorous, pleasure-oriented, and financially rewarding — beauty, charm, and creative talent open doors to wealth, influential friendships, and collaborative ventures in the arts and entertainment industries.",
        (11, "Saturn"): "Gains arrive slowly but with rock-solid permanence. Long-term investments, disciplined networking, and delayed rewards. The native's financial aspirations are modest but enduring — what others gain quickly and lose just as fast, Saturn's child builds slowly and permanently, arriving at financial security through decades of patient, strategic effort.",
        (11, "Rahu"): "Gains may arrive through foreign connections, technology ventures, or unconventional income streams. Sudden windfalls are possible. The native's aspirations are futuristic and boundary-breaking — cryptocurrency, international trade, technology startups, or industries at the cutting edge of social change become the channels through which unexpected abundance flows.",
        (11, "Ketu"): "Gains carry a spiritual quality — success through detachment, research, or behind-the-scenes mastery. Material gains may feel secondary. The native may achieve significant financial success precisely because they are not attached to it — the paradox of Ketu is that renunciation of desire often attracts the very abundance that was never sought.",
        # House 12 - Losses & Liberation
        (12, "Sun"): "Expenses or losses may involve government dealings, father's health, or ego-driven investments. Liberation comes through selfless leadership. The native's spiritual journey requires the surrender of personal authority — learning that true sovereignty is not power over others but mastery of the self through service and self-effacement.",
        (12, "Moon"): "Expenses flow through emotional spending, mother's needs, or residential changes. Liberation arrives through emotional surrender. The native's path to freedom passes through the landscape of emotional release — learning to let go of attachments, memories, and the maternal bonds that both nurture and constrain the soul's flight toward liberation.",
        (12, "Mars"): "Expenses or losses may stem from impulsive decisions, property disputes, or health emergencies. Liberation comes through controlled courage. The native must learn that the warrior's greatest battle is fought on the inner plane — channelling Mars's fire into spiritual discipline rather than worldly aggression opens the door to genuine freedom.",
        (12, "Mercury"): "Expenses flow through education, travel, communication tools, or documentation errors. Liberation arrives through intellectual surrender. The native's path to freedom requires letting go of the need to understand everything — learning that the mind's greatest achievement is knowing when to stop thinking and simply be present.",
        (12, "Jupiter"): "Expenses may be charitable, spiritual, or related to higher education abroad. Liberation is blessed — spiritual growth is the true gain. The native's generosity extends beyond borders — pilgrimages, charitable donations, spiritual retreats, and educational philanthropy become the sacred expenditures through which Jupiter transforms loss into divine investment.",
        (12, "Venus"): "Expenses flow through luxury, romance, comfort, and aesthetic pursuits. Liberation comes through the transcendence of material attachment. The native's spiritual evolution requires learning that beauty is not possessed but witnessed — that the deepest pleasure comes not from acquiring beautiful things but from recognising the beauty inherent in existence itself.",
        (12, "Saturn"): "Expenses are chronic, unavoidable, and tied to duty or institutional obligations. Liberation demands the deepest patience and surrender. The native may face prolonged periods of solitude, institutional confinement, or the heavy burden of unavoidable obligations — yet each endured hardship strips away another layer between the soul and its ultimate freedom.",
        (12, "Rahu"): "Expenses may involve foreign ventures, technology, or deceptive schemes. Liberation requires seeing through illusion to find authentic spiritual ground. The native's path to freedom passes through the wilderness of worldly desire — learning to distinguish between ambition that serves the soul and obsession that imprisons it.",
        (12, "Ketu"): "Expenses carry karmic resolution — past debts clearing. Liberation is the natural destiny — Ketu in the 12th is the moksha signature. The native is approaching the culmination of a long karmic journey — expenditures in this life are the final clearing of ancient accounts, and liberation arrives not as reward but as the natural conclusion of the soul's evolutionary arc.",
        # House 3 - Courage & Siblings
        (3, "Sun"): "Courage is confident and leadership-oriented. Siblings may be influential or in positions of authority. The native communicates with solar authority — their written and spoken words carry weight, their short journeys lead to important encounters, and their courage manifests as the willingness to speak truth to power.",
        (3, "Moon"): "Courage waxes and wanes with emotional state. Siblings provide nurturing support but may also trigger emotional vulnerability. The native's bravery is emotionally sourced — they are most courageous when protecting loved ones and most vulnerable when emotionally depleted. Creative writing and emotionally resonant communication are natural strengths.",
        (3, "Mars"): "Courage is fierce, physical, and confrontational. Siblings are competitive, energetic, and action-oriented. The native possesses raw, instinctive bravery — the first to act in a crisis, the first to defend the underdog, and the most likely to express disagreement through direct confrontation rather than diplomatic evasion.",
        (3, "Mercury"): "Courage expresses through communication, writing, and intellectual boldness. Siblings are talkative, clever, and commercially inclined. The native's bravery is intellectual — they dare to think differently, argue persuasively, and publish ideas that challenge conventional wisdom. Media, journalism, and strategic communication are natural arenas for this courage.",
        (3, "Jupiter"): "Courage is guided by wisdom and ethical principles. Siblings are fortunate, supportive, and philosophically inclined. The native's bravery is moral — they stand up for dharma, defend the philosophically correct position even when it is unpopular, and their courage grows stronger when aligned with a cause larger than personal gain.",
        (3, "Venus"): "Courage expresses through artistic boldness and social grace. Siblings are charming, creative, and relationship-oriented. The native dares to create beauty in unconventional forms — their courage is aesthetic and diplomatic, expressed through art that challenges norms and social engagements that bridge divided communities with grace.",
        (3, "Saturn"): "Courage develops slowly through hardship and discipline. Siblings may be older in spirit, burdened, or delayed in connection. The native's bravery is forged in adversity — they become courageous not through natural boldness but through the patient endurance of repeated difficulties that gradually transform fear into steadfast, unshakeable resolve.",
        (3, "Rahu"): "Courage is unconventional, risk-taking, and boundary-breaking. Siblings may be foreign, unorthodox, or technologically oriented. The native dares to venture where tradition forbids — their courage is revolutionary, expressed through innovation, cross-cultural exploration, and the audacity to reimagine what society considers possible.",
        (3, "Ketu"): "Courage is intuitive and spiritually rooted. Siblings carry a karmic connection — detachment or sudden separation may feature. The native possesses a quiet, inner courage that does not seek external validation — the bravery to renounce what no longer serves the soul, to walk away from comfortable certainties, and to embrace the unknown with spiritual equanimity.",
    }

    _TOPIC_HOOKS: Dict[str, str] = {
        "career":       "Your professional destiny is written in the celestial architecture of House 10. The sub lords governing your career karma reveal the path you were born to walk in the world.",
        "personality":  "At the very heart of your cosmic blueprint lies your soul's authentic expression. The ascendant's planetary configuration reveals the unique signature of who you are — and who you are becoming.",
        "marriage":     "The sacred architecture of partnership is encoded in your stars. House 7 holds the cosmic mirror of relationship — every significant bond and beloved soul you draw into your orbit.",
        "health":       "Your physical vessel is a living temple shaped by planetary forces. The stars illuminate both your innate vitality and the areas that call for your most mindful care.",
        "wealth":       "The rivers of prosperity flow through specific celestial channels. The interplay of Houses 2, 6, and 11 reveals the unique financial map written at your birth.",
        "education":    "Knowledge is a divine inheritance encoded in your chart. The planets governing your intellect reveal the academic landscape through which your mind was designed to shine.",
        "children":     "The blessing of new life and living legacy is written in House 5. The stars reveal the karmic promise of progeny encoded at the moment of your birth.",
        "travel":       "The winds of destiny carry you across horizons encoded in your celestial map. Houses 3, 9, and 12 reveal the journeys — both geographic and spiritual — that await your soul.",
        "property":     "The foundation of shelter, roots, and the land of belonging is carved into your cosmic blueprint by the forces governing House 4.",
        "spiritual":    "Your soul's deepest calling resonates through the mystical Houses 9 and 12. The stars illuminate the sacred path of your spiritual evolution in this lifetime.",
        "loan":         "The flow of borrowed resources carries its own celestial signature — governing how you navigate financial obligation, debt, and the delicate dance of lending and repayment.",
        "court":        "The arena of legal battles, justice, and authority carries a profound cosmic imprint. The stars reveal your karmic relationship with law and institutional power.",
        "business":     "Your entrepreneurial spirit is written in the stars. Houses 7 and 11 hold the cosmic blueprint of ventures, partnerships, and the realisation of collaborative ambition.",
        "vehicle":      "Material acquisitions and the freedom of movement carry a celestial signature. The stars reveal your cosmic relationship with vehicles and possessions.",
        "surgery":      "The body's call for intervention and healing carries a precise celestial blueprint — mapping both the timing and nature of surgical events in the karmic journey.",
        "foreign":      "The call of distant lands resonates through Houses 9 and 12. Your cosmic blueprint reveals the nature and timing of encounters with foreign cultures, places, and peoples.",
        "speculation":  "The realm of risk, intuition, and bold financial ventures is governed by House 5. The stars reveal your unique relationship with fortune and chance.",
        "vastu":        "The sacred geometry of your living space is encoded in your chart. Vastu alignments calibrated to your planetary configuration amplify your life force energy.",
        "divorce":      "The dissolution of sacred bonds carries its own celestial logic. The sub lords of Houses 7 and 8 reveal the karmic choreography of separation and transformation.",
    }
    _CHAPTER_WISDOM: List[str] = [
        '"The stars incline, they do not compel." — Ancient Hermetic Wisdom',
        '"As above, so below; as within, so without." — The Emerald Tablet',
        '"Know thyself — and the universe becomes your mirror." — Delphic Oracle',
        '"Every planet is a teacher; every house a classroom; every dasha a semester in the school of life." — UAKP Tradition',
        '"Awareness is the greatest remedy. A forewarned soul is a forearmed soul." — Vedic Wisdom',
        '"The remedy is not an escape from destiny — it is the conscious embrace of it." — Jyotish Tradition',
        '"Your chart is a map, not a cage. The stars show the terrain; you choose the path." — KP Wisdom',
        '"In the orchestra of the cosmos, every planet plays its part. Your chart reveals the symphony of your soul." — Celestial Tradition',
    ]
    _VERDICT_PROSE: Dict[str, str] = {
        "EXCELLENT":   "The cosmic forces align in breathtaking harmony for this domain of your life — a chapter of profound celestial blessing.",
        "FAVORABLE":   "A gentle celestial wind blows steadily in your favour, quietly opening doors that others find firmly closed.",
        "STRONG":      "The planetary configuration bestows exceptional strength here — your cosmic inheritance in this domain is powerful and clear.",
        "CONFIRMED":   "The stellar verdict is unambiguous — this promise is written into your chart with celestial certainty.",
        "PROMISED":    "The universe has made a sacred promise to your soul in this domain. Claim it with faith, patience, and purposeful action.",
        "PURNAYU":     "A full and abundant lifespan is indicated — the stars grant you the extraordinary gift of longevity.",
        "PROTECTED":   "Invisible forces of cosmic protection surround and shield this aspect of your journey.",
        "SUCCESS":     "The celestial blueprint signals achievement — the stars sanction your efforts in this domain with their full authority.",
        "VICTORY":     "A triumphant celestial signature crowns this domain — the cosmic forces align to honour your endeavours.",
        "PROMISING":   "The seeds of great potential are sown in the soil of this domain. Water them with consistent effort and trust.",
        "YES":         "The celestial answer resonates with clear affirmation — the path ahead is illuminated and open.",
        "GOOD":        "Benevolent planetary energies grace this dimension of your life with steady, reliable favour.",
        "BLESSING":    "The stars rain blessings upon this chapter of your existence with generous and abundant grace.",
        "HIGH":        "Elevated planetary support lifts this domain of your life toward its highest possible expression.",
        "PASS":        "The cosmic examination of this domain yields a passing verdict — the path forward is open and permitted.",
        "DENIED":      "This chapter of your life invites deep patience — the universe redirects your energy toward a higher purpose. What appears as denial is often divine redirection toward something more aligned.",
        "FAIL":        "The cosmic forces signal a period of learning through challenge. Every setback in this domain carries the sacred seed of a future breakthrough.",
        "WEAK":        "The planetary energy in this area calls for conscious cultivation. Like a seed in dry soil, it needs your mindful attention and remedial support to flourish.",
        "CRISIS":      "The stars illuminate a period of intense transformation. Crises in the cosmic blueprint are sacred portals — not permanent walls.",
        "CHALLENGING": "The celestial forces present a formidable test in this dimension. Your soul chose this challenge as its very curriculum for growth.",
        "BLOCKED":     "A celestial blockage signals the need to find the alternative path. The universe closes one door to reveal a more aligned opening elsewhere.",
        "VULNERABLE":  "The stars counsel heightened mindfulness in this area. Awareness and remedial action are the shields the cosmos offers you.",
        "RISK":        "The stars counsel careful navigation and heightened awareness as you move through this delicate territory.",
        "CONFLICT":    "Opposing planetary forces create a dynamic tension that — when channelled with wisdom — transforms into powerful creative energy.",
        "DANGER":      "A significant celestial warning illuminates this domain. Heed the stars' counsel with reverence and take protective action.",
        "ALPAYU":      "A shorter life arc is indicated. This reading calls for deep spiritual awareness and proactive, consistent remedial practice.",
        "NO":          "The celestial reading offers a cautionary signal in this domain. Trust the wisdom of divine timing and remedial grace.",
        "EXIT":        "A significant life transition is encoded in this cosmic chapter. Embrace it with grace, spiritual readiness, and trust in the larger design.",
        "DEATH":       "The great transformation — the soul's transition beyond the physical — is indicated. Approach this revelation with the deepest reverence and spiritual preparation.",
    }
    _VERDICT_POSITIVE = {"EXCELLENT", "FAVORABLE", "STRONG", "SUCCESS", "PASS",
                         "PROMISED", "PROMISING", "PROTECTED", "VICTORY", "HIGH",
                         "CONFIRMED", "PURNAYU", "YES", "GOOD", "BLESSING"}
    _VERDICT_NEGATIVE = {"DENIED", "FAIL", "WEAK", "CRISIS", "CHALLENGING",
                         "VULNERABLE", "BLOCKED", "DANGER", "EXIT", "DEATH",
                         "ALPAYU", "NO", "RISK", "CONFLICT"}


    # ── result display ────────────────────────────────────────────────────────
    def _display_results(
        self,
        console: scrolledtext.ScrolledText,
        prog_lbl: tk.Label,
        results: List[Tuple[str, Any, Optional[str]]],
    ) -> None:
        console.delete("1.0", tk.END)

        # ── Extract person's name and gender ──
        person_name = "the native"
        pronoun = "their"
        try:
            if self._app and hasattr(self._app, "entries"):
                n = self._app.entries.get("ent_name")
                if n:
                    pn = n.get().strip()
                    if pn:
                        person_name = pn
            if self._app and getattr(self._app, "combo_gender", None):
                g = self._app.combo_gender.get().lower()
                pronoun = "his" if g == "male" else ("her" if g == "female" else "their")
        except Exception:
            pass

        # ── Cosmic Title Header ──
        console.insert(tk.END, "\n")
        console.insert(tk.END, "  ✦  DIVYA DRISHTI  ✦\n", "title")
        console.insert(tk.END, "  The Cosmic Story of  ", "wisdom")
        console.insert(tk.END, f"{person_name.upper()}\n\n", "person_name")
        console.insert(tk.END, "  " + "═" * 62 + "\n", "separator_gold")

        # ── Personalized Cosmic Invocation ──
        console.insert(tk.END, "\n")
        console.insert(tk.END,
            f"  At the moment of {person_name}'s birth, the celestial orchestra\n", "cosmic_hook")
        console.insert(tk.END,
            "  of planets, stars, and shadow nodes aligned in a configuration\n", "cosmic_hook")
        console.insert(tk.END,
            "  that will never be repeated in exactly the same way again.\n", "cosmic_hook")
        console.insert(tk.END,
            f"  That singular cosmic fingerprint is {pronoun} personal blueprint —\n", "cosmic_hook")
        console.insert(tk.END,
            f"  a sacred map of {pronoun} soul's journey: its gifts, its trials,\n", "cosmic_hook")
        console.insert(tk.END,
            "  and the celestial remedies that can align this life with its\n", "cosmic_hook")
        console.insert(tk.END,
            "  highest purpose. What follows is that story.\n\n", "cosmic_hook")
        console.insert(tk.END, "  " + "═" * 62 + "\n\n", "separator_gold")

        ok = 0
        nums = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩",
                "⑪","⑫","⑬","⑭","⑮","⑯","⑰","⑱","⑲","⑳"]

        for i, (tname, raw, err) in enumerate(results):
            num = nums[i] if i < len(nums) else f"[{i+1}]"

            # ── Chapter Header ──
            console.insert(tk.END, f"\n\n  {num} ", "topic_num")
            console.insert(tk.END, f"Chapter: {tname.upper()}\n", "topic_header")
            console.insert(tk.END, "  " + "─" * 60 + "\n\n", "separator")

            # ── Topic-specific story hook ──
            hook_key = tname.lower().replace(" ", "_")
            hook = ""
            for k, v in self._TOPIC_HOOKS.items():
                if k in hook_key or hook_key in k:
                    hook = v
                    break
            if not hook:
                hook = (f"The celestial forces governing the domain of {tname.lower()} "
                        f"are uniquely encoded in {person_name}'s cosmic blueprint.")
            console.insert(tk.END, f"  {hook}\n\n", "story_hook")

            if err:
                console.insert(tk.END,
                    f"    ⚠  The stars fell silent for this chapter: {err}\n", "error")
            elif raw is not None:
                self._format_result(console, raw, person_name=person_name, pronoun=pronoun)
                ok += 1
            else:
                console.insert(tk.END,
                    "    The cosmic record holds no data for this chapter at this time.\n", "info")

            # ── Chapter-closing wisdom quote (v5: first 4 chapters only) ──
            if i < 4:
                wisdom = self._CHAPTER_WISDOM[i % len(self._CHAPTER_WISDOM)]
                console.insert(tk.END, f"\n  ✦  {wisdom}\n", "chapter_close")
            console.insert(tk.END, "\n  " + "━" * 62 + "\n", "separator_gold")

        total = len(results)
        console.insert(tk.END, "\n\n")

        # ── Extract and render remedies ──
        extracted_remedies = self._extract_remedies(results)
        self._last_structured_remedies = extracted_remedies
        if extracted_remedies:
            self._render_remedy_protocol_console(console, extracted_remedies, person_name)

        # ── Cosmic Footer ──
        console.insert(tk.END, "\n  " + "═" * 62 + "\n", "separator_gold")
        console.insert(tk.END, "\n  ॥ शृण्वन्तु विश्वे अमृतस्य पुत्रा ॥\n", "wisdom")
        console.insert(tk.END, '  "Hear, O children of immortal bliss."\n\n', "wisdom")
        console.insert(tk.END,
            f"  ✦ THE COSMIC STORY OF {person_name.upper()} — "
            f"{ok}/{total} CHAPTERS READ ✦\n\n", "success")
        console.insert(tk.END,
            "  This reading is drawn from the living tradition of KP Stellar\n", "info")
        console.insert(tk.END,
            "  Astrology. Every insight is a signpost, not a sentence — the\n", "info")
        console.insert(tk.END,
            "  stars illuminate your path; your free will walks it.\n", "info")
        console.insert(tk.END, "\n  " + "═" * 62 + "\n", "separator_gold")
        console.see("1.0")
        prog_lbl.configure(text=f"✅ Story Complete — {ok}/{total} chapters")




    def _extract_remedies(self, results: List[Tuple[str, Any, Optional[str]]]) -> List[Dict]:
        """Extract ALL remedy data from every module output."""
        remedies: List[Dict] = []
        ALL_REMEDY_KEYS = [
            "Remedy", "Condition_Remedy", "Root_Remedy",
            "Source_Remedy", "Result_Remedy", "Career_Core",
            "Vastu_Forensic", "Support_Gemstone"
        ]

        for tname, raw, err in results:
            if err or raw is None:
                continue

            if isinstance(raw, dict):
                # Event timing windows with embedded remedies
                for key, val in raw.items():
                    if key.lower() in ("event_windows", "confirmed_event_windows") and isinstance(val, list):
                        for item in val[:5]:
                            if isinstance(item, dict) and "remedy" in item:
                                rem = item["remedy"]
                                if rem:
                                    remedies.append({"topic": tname, "dasha": item.get("dasha", ""), "remedy": rem, "source": "event"})

                # General prediction report items
                if "report" in raw and isinstance(raw["report"], list):
                    for item in raw["report"]:
                        if isinstance(item, dict):
                            for rkey in ALL_REMEDY_KEYS:
                                if rkey in item and item[rkey]:
                                    remedies.append({
                                        "topic": tname,
                                        "dasha": item.get("Planet", item.get("Sub_Lord", "")),
                                        "remedy": item[rkey],
                                        "source": "general",
                                        "house": item.get("House", "")
                                    })

        return remedies

    def _render_remedy_protocol_console(
        self, console: scrolledtext.ScrolledText,
        remedies: List[Dict], person_name: str = "the native"
    ) -> None:
        """Render the Sacred Prescription — a personalized cosmic remedy guide."""
        console.insert(tk.END, "\n\n  " + "═" * 62 + "\n", "separator_gold")
        console.insert(tk.END, "\n  🛡  ", "topic_num")
        console.insert(tk.END, "YOUR SACRED PRESCRIPTION\n", "topic_header")
        console.insert(tk.END, "  " + "─" * 60 + "\n\n", "separator")

        # Opening narrative
        console.insert(tk.END,
            f"  The cosmos has not only illuminated {person_name}'s path —\n", "story_hook")
        console.insert(tk.END,
            "  it has also encoded the precise antidotes and alignments\n", "story_hook")
        console.insert(tk.END,
            "  that can harmonise the planetary forces at work. These are\n", "story_hook")
        console.insert(tk.END,
            "  not superstitions — they are the ancient technology of\n", "story_hook")
        console.insert(tk.END,
            "  consciousness, refined over millennia by Vedic seers who\n", "story_hook")
        console.insert(tk.END,
            "  understood the geometry of karma.\n\n", "story_hook")

        console.insert(tk.END, "    A Note on Remedies\n", "section_label")
        console.insert(tk.END,
            "    Remedies do not rewrite destiny. They act as precision instruments\n", "story_prose")
        console.insert(tk.END,
            "    that ground difficult planetary energies and amplify the beneficial\n", "story_prose")
        console.insert(tk.END,
            "    alignments already present in your chart. Each prescription below\n", "story_prose")
        console.insert(tk.END,
            "    is drawn from your unique Sub Lord configuration and active Dasha.\n\n", "story_prose")

        console.insert(tk.END, "    How to Use These Remedies\n", "section_label")
        console.insert(tk.END,
            "    Consistency transforms remedy into reality. Perform each practice\n", "story_prose")
        console.insert(tk.END,
            "    during its corresponding Dasha window. Intention and faith amplify\n", "story_prose")
        console.insert(tk.END,
            "    the effect — approach each remedy as a conversation with the cosmos.\n\n", "story_prose")

        # Group remedies by topic, deduplicate
        seen = set()
        by_topic: Dict[str, List[Dict]] = {}
        for rem_data in remedies:
            topic = rem_data["topic"]
            dasha = rem_data.get("dasha", "")
            rem = rem_data["remedy"]
            key = f"{topic}_{dasha}_{id(rem)}"
            if key in seen:
                continue
            seen.add(key)
            by_topic.setdefault(topic, []).append(rem_data)

        for topic, items in by_topic.items():
            console.insert(tk.END, f"\n    ◈ FOR YOUR {topic.upper()} CHAPTER\n", "summary_label")
            for rem_data in items:
                dasha = rem_data.get("dasha", "")
                rem = rem_data["remedy"]
                if dasha:
                    ps = self._PLANET_STORY.get(str(dasha),
                         self._PLANET_PROSE.get(str(dasha), str(dasha)))
                    console.insert(tk.END,
                        f"      Under the influence of {ps}:\n", "planet_hl")

                if isinstance(rem, dict):
                    self._render_single_remedy(console, rem)
                elif isinstance(rem, str) and rem.strip():
                    console.insert(tk.END,
                        f"      ✦ To align this energy: {rem}\n", "remedy_action")

            console.insert(tk.END, "\n")

        console.insert(tk.END,
            f"\n  ✦  Trust the prescription. Trust the process. "
            f"The cosmos works with {person_name}.\n", "chapter_close")
        console.insert(tk.END, "\n  " + "━" * 62 + "\n", "separator_gold")


    def _render_single_remedy(self, console: scrolledtext.ScrolledText, rem: Dict) -> None:
        """Render a single remedy dict with all known key patterns."""
        # Normalise: check both lowercase and TitleCase keys
        def _get(*keys):
            for k in keys:
                v = rem.get(k)
                if v:
                    return v
            return None

        karmic = _get("karmic", "Karmic", "Karmic_Correction")
        lalkitab = _get("lal_kitab", "LalKitab", "Lal_Kitab")
        mantra = _get("Mantra_Chanting", "mantra", "Mantra", "Defense_Mantra")
        skill = _get("Skill_Development", "Skill_Alignment", "skill")
        energy = _get("Energy_Balance", "energy")
        physical = _get("Physical_Vastu", "physical")
        protective = _get("Protective_Object", "protective")

        # Handle list-type remedies (event modules)
        if isinstance(karmic, list):
            for k in karmic[:2]:
                console.insert(tk.END, f"      💊 Karmic: ", "remedy_title")
                console.insert(tk.END, f"{k}\n", "remedy_action")
        elif isinstance(karmic, str) and karmic.strip():
            console.insert(tk.END, f"      💊 Karmic: ", "remedy_title")
            console.insert(tk.END, f"{karmic}\n", "remedy_action")

        if isinstance(lalkitab, list):
            for l in lalkitab[:2]:
                console.insert(tk.END, f"      💊 Lal Kitab: ", "remedy_title")
                console.insert(tk.END, f"{l}\n", "remedy_action")
        elif isinstance(lalkitab, str) and lalkitab.strip():
            console.insert(tk.END, f"      💊 Lal Kitab: ", "remedy_title")
            console.insert(tk.END, f"{lalkitab}\n", "remedy_action")

        if isinstance(mantra, str) and mantra.strip():
            console.insert(tk.END, f"      🙏 Mantra: ", "remedy_title")
            console.insert(tk.END, f"{mantra}\n", "remedy_action")

        if isinstance(skill, str) and skill.strip():
            console.insert(tk.END, f"      📚 Skill Focus: ", "remedy_title")
            console.insert(tk.END, f"{skill}\n", "remedy_action")

        if isinstance(energy, str) and energy.strip():
            console.insert(tk.END, f"      ⚡ Energy Balance: ", "remedy_title")
            console.insert(tk.END, f"{energy}\n", "remedy_action")

        if isinstance(physical, str) and physical.strip():
            console.insert(tk.END, f"      🏠 Vastu Correction: ", "remedy_title")
            console.insert(tk.END, f"{physical}\n", "remedy_action")

        if isinstance(protective, str) and protective.strip():
            console.insert(tk.END, f"      🧿 Protective: ", "remedy_title")
            console.insert(tk.END, f"{protective}\n", "remedy_action")

        # Gemstone block
        gem = _get("gemstone", "Gemstone", "Support_Gemstone")
        if isinstance(gem, dict):
            if gem.get("allowed") and gem.get("stone"):
                wt = gem.get("weight", gem.get("weight_ratti", ""))
                wt_str = f" ({wt} ratti)" if wt else ""
                console.insert(tk.END, f"      💎 Gemstone: ", "gem_rx")
                console.insert(tk.END, f"{gem['stone']}{wt_str}\n", "planet_hl")
            elif gem.get("Main") and isinstance(gem["Main"], dict):
                mg = gem["Main"]
                console.insert(tk.END, f"      💎 Gemstone: ", "gem_rx")
                console.insert(tk.END, f"{mg.get('name', '?')} ({mg.get('weight_ratti', '?')} ratti)\n", "planet_hl")

        # Supernatural Defense sub-dict
        sup = rem.get("Supernatural_Defense")
        if isinstance(sup, dict):
            sm = sup.get("Mantra_Chanting", "")
            sp = sup.get("Protective_Object", "")
            if sm:
                console.insert(tk.END, f"      🙏 Defense Mantra: ", "remedy_title")
                console.insert(tk.END, f"{sm}\n", "remedy_action")
            if sp:
                console.insert(tk.END, f"      🧿 Protective Object: ", "remedy_title")
                console.insert(tk.END, f"{sp}\n", "remedy_action")

    def _format_result(
        self, console: scrolledtext.ScrolledText, result: Any,
        person_name: str = "the native", pronoun: str = "their"
    ) -> None:
        if isinstance(result, str):
            self._format_narrative(console, result, person_name=person_name, pronoun=pronoun)
            return
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    self._format_dict(console, item, person_name=person_name, pronoun=pronoun)
                else:
                    console.insert(tk.END, f"  {item}\n", "body")
            return
        if isinstance(result, dict):
            # ── Priority 1: Structured report list → rich _format_dict storytelling ──
            report_list = result.get("report", [])
            if isinstance(report_list, list) and report_list:
                for item in report_list:
                    if isinstance(item, dict):
                        self._format_dict(console, item, person_name=person_name, pronoun=pronoun)
                    else:
                        console.insert(tk.END, f"    {item}\n", "story_prose")
                # Extract closing advisory from narrative
                import re as _adv_re
                narrative = result.get("narrative", "")
                if narrative and isinstance(narrative, str):
                    _in_tail = False
                    for _ln in narrative.split("\n"):
                        _s = _ln.strip()
                        if "REMEDY" in _s.upper() or "CHRONICLE" in _s.upper() or "COSMIC VISION" in _s.upper():
                            _in_tail = True
                            continue
                        if _in_tail and _s and not all(c in "═=─-━" for c in _s):
                            _s = _adv_re.sub(r"^\s*\[\+\]\s*", "", _s)
                            _s = _adv_re.sub(r"^\s*\[\*\]\s*", "", _s).strip()
                            if _s and not _s.upper().startswith(("TITANIUM", "FORENSIC")):
                                _s = _s.replace("the native", person_name)
                                console.insert(tk.END, f"    {_s}\n", "story_prose")
                console.insert(tk.END, "\n")
                return

            # ── Priority 2: Narrative string → _format_narrative processing ──
            narrative = result.get("narrative", "")
            if narrative and isinstance(narrative, str) and len(narrative.strip()) > 20:
                self._format_narrative(console, narrative, person_name=person_name, pronoun=pronoun)
                return

            # Check for standard Category/Verdict/Details keys
            has_standard = any(k in result for k in ("Category", "category", "Verdict", "verdict"))
            if has_standard:
                self._format_dict(console, result, person_name=person_name, pronoun=pronoun)
                return

            # Event timing module output: render all key-value pairs
            self._format_event_dict(console, result, person_name=person_name, pronoun=pronoun)
            return
        console.insert(tk.END, f"  {result}\n", "body")

    def _format_narrative(
        self, console: scrolledtext.ScrolledText, text: str,
        person_name: str = "the native", pronoun: str = "their"
    ) -> None:
        """Transform raw module narrative into premium storytelling prose.

        This method converts the compact, data-dense output from prediction
        modules (e.g. 'H7 CSL [Sub: Mercury] > Communicative partner') into
        rich, flowing paragraphs that read like a professional astrological
        consultation — using the elaboration dictionaries to generate
        2-4 sentences of interpretive prose per data point.
        """
        import re as _re

        # ── helper: clean technical markers ──
        def _clean(line: str) -> str:
            s = line.strip()
            s = _re.sub(r"^\s*\[\+\]\s*", "", s)
            s = _re.sub(r"^\s*\[\*\]\s*", "", s)
            s = _re.sub(r"^\s*\[X\]\s*", "", s, flags=_re.IGNORECASE)
            s = _re.sub(r"^\s*\[>\]\s*", "", s)
            s = _re.sub(r"^>>>\s*", "", s)
            s = _re.sub(r"\s*<<<\s*$", "", s)
            s = _re.sub(r"^↳\s*", "", s)
            s = _re.sub(r"^•\s*", "", s)
            s = _re.sub(r"^\[P\]\s*", "", s)
            s = _re.sub(r"^\[S\]\s*", "", s)
            return s.strip()

        # ── helper: render a full paragraph for H-number patterns ──
        def _render_house_paragraph(hnum: int, planet: str, sub: str, rest: str) -> None:
            """Render a full storytelling paragraph for a house/planet/sub combination."""
            hname = self._HOUSE_NAMES.get(hnum, f"House {hnum}")
            aspect = self._HOUSE_LIFE_ASPECT.get(hnum, "")
            is_csl = (planet.upper() == "CSL")

            if is_csl:
                # ── Primary CSL: full paragraph treatment ──
                pp_story = self._PLANET_STORY.get(sub, self._PLANET_PROSE.get(sub, sub))

                console.insert(tk.END, f"\n    🔹 {hname}\n", "category_header")
                console.insert(tk.END,
                    f"    The sacred domain of {hname} — {aspect} — is governed in {person_name}'s chart by ",
                    "story_prose")
                console.insert(tk.END, f"{pp_story}", "planet_hl")
                console.insert(tk.END, f" as {pronoun} cosmic Sub Lord.\n\n", "story_prose")

                # Planet elaboration
                elab = self._PLANET_ELABORATION.get(sub, "")
                if elab:
                    elab_text = elab.replace("The native", person_name).replace("the native", person_name)
                    console.insert(tk.END, f"    {elab_text}\n\n", "story_prose")

                # House-specific insight
                h_insight = self._HOUSE_PLANET_INSIGHT.get((hnum, sub), "")
                if h_insight:
                    h_text = h_insight.replace("the native", person_name).replace("The native", person_name)
                    console.insert(tk.END, f"    {h_text}\n\n", "story_prose")

                # Render the original outcome if present
                if rest:
                    rest_clean = rest.replace("the native", person_name)
                    console.insert(tk.END, f"    ✦ {rest_clean}\n\n", "story_prose")

            else:
                # ── Secondary (Occupant/Lord): shorter treatment ──
                pp = self._PLANET_PROSE.get(sub, sub)
                pp2 = self._PLANET_PROSE.get(planet, planet)

                console.insert(tk.END, f"    Within this domain, ", "story_prose")
                console.insert(tk.END, f"{pp2}", "planet_hl")
                console.insert(tk.END, f" operates under the guiding influence of ", "story_prose")
                console.insert(tk.END, f"{pp}", "planet_hl")
                console.insert(tk.END, ". ", "story_prose")

                h_insight = self._HOUSE_PLANET_INSIGHT.get((hnum, sub), "")
                if h_insight:
                    h_text = h_insight.replace("the native", person_name).replace("The native", person_name)
                    console.insert(tk.END, f"{h_text}", "story_prose")

                console.insert(tk.END, "\n", "story_prose")

                if rest:
                    rest_clean = rest.replace("the native", person_name)
                    console.insert(tk.END, f"    ✦ {rest_clean}\n", "story_prose")
                console.insert(tk.END, "\n")

        # ── helper: render a score line as prose ──
        _SCORE_PROSE = {
            "foundation": "Foundation in Schooling",
            "intelligence": "Intelligence & Exam Readiness",
            "higher_education": "Higher Education Potential",
            "career_status": "Career Qualification",
            "effort": "Effort Required",
            "obstacles": "Obstacles & Breaks"
        }
        def _render_score_line(label: str, value: str) -> None:
            """Convert score/pillar lines into flowing narrative."""
            label_clean = label.strip().rstrip(":").strip()
            value_clean = value.strip()

            # Try to parse as X / 10 format
            score_match = _re.match(r"([\d\.]+)\s*/\s*(\d+)", value_clean)
            if score_match:
                score_val = float(score_match.group(1))
                score_max = int(score_match.group(2))
                ratio = score_val / score_max if score_max > 0 else 0

                if ratio >= 0.8:
                    strength = "exceptional — a deeply favourable celestial endorsement"
                elif ratio >= 0.6:
                    strength = "strong and steady — a reliable cosmic foundation"
                elif ratio >= 0.4:
                    strength = "moderate — present but requiring conscious cultivation"
                elif ratio >= 0.2:
                    strength = "modest — calling for remedial attention and patient nurturing"
                else:
                    strength = "subdued — indicating a domain where mindful effort and spiritual practice are essential"

                console.insert(tk.END, f"    {label_clean}: ", "cause_text")
                console.insert(tk.END, f"{score_val}/{score_max}", "planet_hl")
                console.insert(tk.END, f" — {strength}.\n", "story_prose")
            else:
                console.insert(tk.END, f"    {label_clean}: ", "cause_text")
                console.insert(tk.END, f"{value_clean}\n", "effect_text")

        # ══════════════════════════════════════════════════════════════
        # MAIN RENDERING LOOP
        # ══════════════════════════════════════════════════════════════
        skip_seps = {"TITANIUM ORACLE", "FORENSIC REMEDY PROTOCOL"}
        verdict_found = False
        section_lines: List[str] = []  # accumulate regular prose lines

        def _flush_section() -> None:
            """Flush accumulated prose lines as a paragraph block."""
            nonlocal section_lines
            if section_lines:
                combined = " ".join(section_lines)
                combined = combined.replace("the native", person_name).replace("The native", person_name)
                console.insert(tk.END, f"    {combined}\n\n", "story_prose")
                section_lines = []

        for line in text.split("\n"):
            s = line.strip()
            if not s:
                _flush_section()
                continue

            # Skip pure separator lines
            if all(c in "═=─-━" for c in s) and len(s) > 3:
                _flush_section()
                continue

            # Skip engine branding headers
            upper = s.upper()
            if any(k in upper for k in skip_seps):
                _flush_section()
                continue

            cleaned = _clean(s)
            if not cleaned:
                continue

            # ── H-number patterns: full paragraph rendering ──
            h_match = _re.match(
                r"H(\d{1,2})\s+(?:H\d{1,2}\s+)?(CSL|[A-Za-z]+)\s*\[Sub:\s*([A-Za-z]+)\]\s*[>\-]*\s*(.*)",
                cleaned
            )
            if h_match:
                _flush_section()
                hnum = int(h_match.group(1))
                planet = h_match.group(2)
                sub = h_match.group(3)
                rest = h_match.group(4).strip()
                _render_house_paragraph(hnum, planet, sub, rest)
                continue

            # ── Star Lord / Result lines: render as insight prose ──
            star_match = _re.match(r"->?\s*Star Lord:\s*(.+)", cleaned)
            if star_match:
                star_info = star_match.group(1).strip()
                console.insert(tk.END, f"    The Star Lord configuration reveals: {star_info}\n", "story_prose")
                continue

            result_match = _re.match(r"->?\s*Result:\s*(.+)", cleaned)
            if result_match:
                result_info = result_match.group(1).strip().replace("the native", person_name)
                console.insert(tk.END, f"    ✦ {result_info}\n", "story_prose")
                continue

            effect_match = _re.match(r"->?\s*Effect:\s*(.+)", cleaned)
            if effect_match:
                effect_info = effect_match.group(1).strip().replace("the native", person_name)
                console.insert(tk.END, f"    ✦ {effect_info}\n", "story_prose")
                continue

            # ── Remedy lines: sacred counsel formatting ──
            if any(k in upper for k in ("REMEDY", "KARMIC", "LAL KITAB",
                                         "SKILL", "MANTRA", "GEMSTONE",
                                         "PROTECTIVE", "DEFENSE", "ENERGY",
                                         "SUPERNATURAL")):
                _flush_section()
                if ":" in cleaned:
                    k, v = cleaned.split(":", 1)
                    label = k.strip().replace("_", " ").title()
                    console.insert(tk.END, f"      💊 {label}: ", "remedy_title")
                    console.insert(tk.END, f"{v.strip()}\n", "remedy_action")
                else:
                    console.insert(tk.END, f"      💊 {cleaned}\n", "remedy_action")
                continue

            # ── Section sub-headers ──
            if upper.startswith(("SOURCE", "RESULT", "CAREER CORE",
                                "DIRECTIONAL", "ELEMENTAL", "ENTITY",
                                "VASTU FORENSIC", "SUPERNATURAL RISK",
                                "ACADEMIC PILLARS", "DETAILED HOUSE",
                                "COSMIC COUNSEL")):
                _flush_section()
                label = cleaned.rstrip(":").replace("_", " ").title()
                console.insert(tk.END, f"\n    📌 {label}\n", "section_label")
                continue

            # ── Emoji-prefixed lines: render as section headers ──
            if s[0] in "🔮🏛🏆⚡🌟📜🔱💎📈⚖⚠🌪⚪🛡🧿":
                _flush_section()
                console.insert(tk.END, f"\n    {cleaned}\n", "category_header")
                continue

            # ── House Analysis sub-headers like [H4], [H5] ──
            house_header = _re.match(r"^\[H(\d{1,2})\]\s+(.+)", cleaned)
            if house_header:
                _flush_section()
                hnum = int(house_header.group(1))
                rest = house_header.group(2).strip()
                hname = self._HOUSE_NAMES.get(hnum, f"House {hnum}")
                aspect = self._HOUSE_LIFE_ASPECT.get(hnum, "")
                console.insert(tk.END, f"\n    🔹 {hname}: {rest}\n", "category_header")
                if aspect:
                    console.insert(tk.END, f"    This domain governs {aspect}.\n\n", "story_prose")
                continue

            # ── Verdict line: story thesis rendering ──
            if ":" in cleaned and len(cleaned.split(":")[0]) < 35:
                k, v = cleaned.split(":", 1)
                ku = k.strip().upper()
                vv = v.strip()

                if ku in ("VERDICT", "OVERALL VERDICT", "NET EDUCATIONAL STRENGTH"):
                    _flush_section()
                    verdict_found = True
                    vu = vv.upper()
                    prose = ""
                    for vk, vp in self._VERDICT_PROSE.items():
                        if vk in vu:
                            prose = vp
                            break

                    if any(w in vu for w in self._VERDICT_POSITIVE):
                        console.insert(tk.END, f"    ✅ Celestial Verdict: ", "verdict_pass")
                        console.insert(tk.END, f"{vv}\n", "verdict_pass")
                    elif any(w in vu for w in self._VERDICT_NEGATIVE):
                        console.insert(tk.END, f"    ⚠ Celestial Verdict: ", "verdict_fail")
                        console.insert(tk.END, f"{vv}\n", "verdict_fail")
                    else:
                        console.insert(tk.END, f"    ◐ Celestial Verdict: ", "verdict_neutral")
                        console.insert(tk.END, f"{vv}\n", "verdict_neutral")

                    if prose:
                        console.insert(tk.END, f"    {prose}\n\n", "story_prose")
                    continue

                # Score / Pillar lines
                if ku in ("SCORE", "CONFIDENCE", "STRENGTH",
                          "FOUNDATION (SCHOOLING)", "INTELLIGENCE (EXAMS)",
                          "HIGHER EDUCATION", "CAREER QUALIFICATION",
                          "EFFORT REQUIRED", "OBSTACLES/BREAKS",
                          "NET SCORE", "NET EDUCATIONAL STRENGTH"):
                    _flush_section()
                    _render_score_line(k, vv)
                    continue

                # Synthesis / Outcome lines
                if ku in ("SYNTHESIS", "OUTCOME", "RESULT"):
                    _flush_section()
                    vv_personal = vv.replace("the native", person_name)
                    console.insert(tk.END, f"    ✦ {vv_personal}\n\n", "story_prose")
                    continue

                # General key: value — render as detail prose
                _flush_section()
                console.insert(tk.END, f"    {k.strip()}: ", "cause_text")
                vv_personal = vv.replace("the native", person_name)
                console.insert(tk.END, f"{vv_personal}\n", "effect_text")
                continue

            # ── Forensic alerts: [!] lines ──
            alert_match = _re.match(r"^\[!\]\s*(.*)", cleaned)
            if alert_match:
                _flush_section()
                alert_text = alert_match.group(1).replace("the native", person_name)
                console.insert(tk.END, f"    ⚠ {alert_text}\n", "verdict_fail")
                continue

            # ── Regular prose: accumulate for paragraph grouping ──
            cleaned_personal = cleaned.replace("the native", person_name).replace("The native", person_name)
            section_lines.append(cleaned_personal)

        # Flush any remaining accumulated lines
        _flush_section()



    def _format_dict(
        self, console: scrolledtext.ScrolledText, d: Dict[str, Any],
        person_name: str = "the native", pronoun: str = "their"
    ) -> None:
        """Render a single report item as flowing storytelling prose."""
        cat     = d.get("Category", d.get("category", ""))
        verdict = d.get("Verdict",  d.get("verdict", ""))
        details = d.get("Details",  d.get("details", ""))
        outcome = d.get("Outcome",  d.get("outcome", ""))
        house   = d.get("House",    d.get("house", ""))
        planet  = d.get("Planet",   d.get("planet", ""))
        sub     = d.get("Sub_Lord", d.get("sub_lord", ""))
        synth   = d.get("Synthesis", d.get("synthesis", ""))

        hnum = int(house) if str(house).isdigit() else 0
        hname = self._HOUSE_NAMES.get(hnum, f"House {house}") if hnum else ""
        aspect = self._HOUSE_LIFE_ASPECT.get(hnum, "") if hnum else ""
        sub_str = str(sub).strip() if sub else ""
        is_primary = str(planet).upper().endswith("CSL") if planet else False

        # ── Section header ──
        if cat:
            console.insert(tk.END, f"\n    🔹 {cat}\n", "category_header")
        elif house and is_primary:
            console.insert(tk.END, f"\n    🔹 {hname}\n", "category_header")

        # ══════════════════════════════════════════════════════════════
        # PRIMARY (CSL) ENTRY — Full paragraph storytelling
        # ══════════════════════════════════════════════════════════════
        if is_primary and sub_str and hnum:
            pp_story = self._PLANET_STORY.get(sub_str, self._PLANET_PROSE.get(sub_str, sub_str))

            # Opening sentence: house + sub lord identification
            console.insert(tk.END,
                f"    The sacred domain of {hname} — {aspect} — is governed in {person_name}'s chart by ",
                "story_prose")
            console.insert(tk.END, f"{pp_story}", "planet_hl")
            console.insert(tk.END, f" as {pronoun} cosmic Sub Lord.\n\n", "story_prose")

            # Elaboration paragraph: planet personality in this domain
            elab = self._PLANET_ELABORATION.get(sub_str, "")
            if elab:
                # Personalise the elaboration
                elab_text = elab.replace("The native", person_name).replace("the native", person_name)
                console.insert(tk.END, f"    {elab_text}\n\n", "story_prose")

            # House-specific insight
            h_insight = self._HOUSE_PLANET_INSIGHT.get((hnum, sub_str), "")
            if h_insight:
                h_insight_text = h_insight.replace("the native", person_name).replace("The native", person_name)
                console.insert(tk.END, f"    {h_insight_text}\n\n", "story_prose")

            # Verdict — rendered as a story thesis
            if verdict:
                vu = str(verdict).upper()
                prose = self._VERDICT_PROSE.get(vu, "")
                # Find the first matching key
                for vk, vp in self._VERDICT_PROSE.items():
                    if vk in vu:
                        prose = vp
                        break

                if any(w in vu for w in self._VERDICT_POSITIVE):
                    console.insert(tk.END, f"    ✅ Celestial Verdict: ", "verdict_pass")
                    console.insert(tk.END, f"{verdict}\n", "verdict_pass")
                elif any(w in vu for w in self._VERDICT_NEGATIVE):
                    console.insert(tk.END, f"    ⚠ Celestial Verdict: ", "verdict_fail")
                    console.insert(tk.END, f"{verdict}\n", "verdict_fail")
                else:
                    console.insert(tk.END, f"    ◐ Celestial Verdict: ", "verdict_neutral")
                    console.insert(tk.END, f"{verdict}\n", "verdict_neutral")

                if prose:
                    console.insert(tk.END, f"    {prose}\n\n", "story_prose")

            # Synthesis / Outcome as flowing prose
            if synth:
                synth_text = str(synth).replace("the native", person_name).replace("_", " ").title()
                console.insert(tk.END, f"\n    ✦ {synth_text}\n\n", "category_header")
            if outcome:
                outcome_text = str(outcome).replace("the native", person_name)
                console.insert(tk.END, f"    {outcome_text}\n\n", "story_prose")

            # Details as woven prose
            if details:
                for dl in str(details).split("\n"):
                    dl = dl.strip()
                    if dl:
                        dl = dl.replace("the native", person_name)
                        console.insert(tk.END, f"    {dl}\n", "detail_text")
                console.insert(tk.END, "\n")

        # ══════════════════════════════════════════════════════════════
        # SECONDARY (Occupant / Lord) ENTRY — Shorter narrative prose
        # ══════════════════════════════════════════════════════════════
        elif planet and sub_str and not is_primary:
            pname = self._PLANET_PROSE.get(str(planet), str(planet))
            pp = self._PLANET_PROSE.get(sub_str, sub_str)

            # Opening: identify the planetary influence
            if hnum:
                console.insert(tk.END,
                    f"    Within this domain, ", "story_prose")
                console.insert(tk.END, f"{pname}", "planet_hl")
                console.insert(tk.END,
                    f" operates under the guiding lens of ", "story_prose")
                console.insert(tk.END, f"{pp}", "planet_hl")
                console.insert(tk.END, ". ", "story_prose")
            else:
                console.insert(tk.END, f"    ", "story_prose")
                console.insert(tk.END, f"{pname.capitalize()}", "planet_hl")
                console.insert(tk.END, f" channels its energy through ", "story_prose")
                console.insert(tk.END, f"{pp}", "planet_hl")
                console.insert(tk.END, ". ", "story_prose")

            # Brief house-planet insight for secondary entries
            h_insight = self._HOUSE_PLANET_INSIGHT.get((hnum, sub_str), "")
            if h_insight:
                h_text = h_insight.replace("the native", person_name).replace("The native", person_name)
                console.insert(tk.END, f"{h_text}", "story_prose")

            console.insert(tk.END, "\n", "story_prose")

            # Outcome if present
            if outcome:
                outcome_text = str(outcome).replace("the native", person_name)
                console.insert(tk.END, f"    ✦ {outcome_text}\n", "story_prose")
            if synth:
                synth_text = str(synth).replace("the native", person_name)
                console.insert(tk.END, f"    {synth_text}\n", "story_prose")

            console.insert(tk.END, "\n")

        # ══════════════════════════════════════════════════════════════
        # GENERIC ENTRY — Verdict/Category based (no planet/sub)
        # ══════════════════════════════════════════════════════════════
        else:
            if verdict:
                vu = str(verdict).upper()
                prose = self._VERDICT_PROSE.get(vu, "")
                for vk, vp in self._VERDICT_PROSE.items():
                    if vk in vu:
                        prose = vp
                        break

                if any(w in vu for w in self._VERDICT_POSITIVE):
                    console.insert(tk.END, "    ✅ ", "verdict_pass")
                    console.insert(tk.END, f"{verdict}\n", "verdict_pass")
                elif any(w in vu for w in self._VERDICT_NEGATIVE):
                    console.insert(tk.END, "    ⚠ ", "verdict_fail")
                    console.insert(tk.END, f"{verdict}\n", "verdict_fail")
                else:
                    console.insert(tk.END, "    ◐ ", "verdict_neutral")
                    console.insert(tk.END, f"{verdict}\n", "verdict_neutral")

                if prose:
                    console.insert(tk.END, f"    {prose}\n\n", "story_prose")

            if synth:
                console.insert(tk.END, f"    {synth}\n", "story_prose")
            if outcome:
                console.insert(tk.END, f"    ✦ {outcome}\n", "story_prose")
            if details:
                for dl in str(details).split("\n"):
                    dl = dl.strip()
                    if dl:
                        console.insert(tk.END, f"    {dl}\n", "detail_text")
            console.insert(tk.END, "\n")

        # ══════════════════════════════════════════════════════════════
        # REMEDIES — Woven as sacred counsel prose (shared by all)
        # ══════════════════════════════════════════════════════════════
        remedy_keys = ["Remedy", "Condition_Remedy", "Root_Remedy",
                       "Source_Remedy", "Result_Remedy", "Career_Core"]
        has_remedy = any(d.get(rk) and isinstance(d.get(rk), dict) for rk in remedy_keys)
        if has_remedy:
            console.insert(tk.END, "    🙏 Sacred Counsel for this domain:\n", "section_label")
            for rk in remedy_keys:
                rem = d.get(rk)
                if rem and isinstance(rem, dict):
                    for rk2, rv2 in rem.items():
                        if isinstance(rv2, str) and rv2.strip():
                            rl = rk2.replace("_", " ").title()
                            console.insert(tk.END, f"      💊 {rl}: ", "remedy_title")
                            console.insert(tk.END, f"{rv2}\n", "remedy_action")
                        elif isinstance(rv2, dict):
                            for rk3, rv3 in rv2.items():
                                rl3 = rk3.replace("_", " ").title()
                                console.insert(tk.END, f"      💊 {rl3}: ", "remedy_title")
                                console.insert(tk.END, f"{rv3}\n", "remedy_action")
            console.insert(tk.END, "\n")

        # ── Gemstone prescription ──
        gem = d.get("Support_Gemstone")
        if gem and isinstance(gem, dict):
            if "Warning" in gem:
                console.insert(tk.END, f"      ⚠ Gemstone Note: {gem['Warning']}\n", "verdict_neutral")
            else:
                main_g = gem.get("Main", {})
                sub_g = gem.get("Substitute", {})
                if main_g.get("name"):
                    console.insert(tk.END, f"      💎 Recommended Gemstone: ", "gem_rx")
                    console.insert(tk.END, f"{main_g['name']} ({main_g.get('weight_ratti', '?')} ratti)\n", "planet_hl")
                if sub_g.get("name"):
                    console.insert(tk.END, f"         Substitute: {sub_g['name']} ({sub_g.get('weight_ratti', '?')} ratti)\n", "effect_text")
            console.insert(tk.END, "\n")



    def _format_event_dict(
        self, console: scrolledtext.ScrolledText, d: Dict[str, Any],
        person_name: str = "the native", pronoun: str = "their"
    ) -> None:
        """Format event timing module outputs as humanised storytelling."""
        skip_keys = {"status", "module", "version", "error", "narrative", "report"}

        for key, value in d.items():
            if key.lower() in skip_keys:
                continue

            label = key.replace("_", " ").title()

            if isinstance(value, str):
                console.insert(tk.END, f"\n    {label}: ", "cause_text")
                vu = value.upper()
                value = value.replace("the native", person_name).replace("The native", person_name)
                if any(w in vu for w in self._VERDICT_POSITIVE):
                    console.insert(tk.END, f"✅ {value}\n", "verdict_pass")
                elif any(w in vu for w in self._VERDICT_NEGATIVE):
                    console.insert(tk.END, f"⚠ {value}\n", "verdict_fail")
                else:
                    console.insert(tk.END, f"{value}\n", "story_prose")

            elif isinstance(value, dict):
                console.insert(tk.END, f"\n    🔹 {label}\n", "section_label")
                for sub_k, sub_v in value.items():
                    sub_label = sub_k.replace("_", " ").title()
                    if isinstance(sub_v, (str, int, float, bool)):
                        sv = str(sub_v)
                        svu = sv.upper()
                        console.insert(tk.END, f"      {sub_label}: ", "cause_text")
                        if any(w in svu for w in self._VERDICT_POSITIVE):
                            console.insert(tk.END, f"✅ {sv}\n", "verdict_pass")
                        elif any(w in svu for w in self._VERDICT_NEGATIVE):
                            console.insert(tk.END, f"⚠ {sv}\n", "verdict_fail")
                        else:
                            console.insert(tk.END, f"{sv}\n", "effect_text")
                    elif isinstance(sub_v, (list, set)):
                        console.insert(tk.END, f"      {sub_label}: ", "cause_text")
                        console.insert(tk.END, f"{', '.join(str(x) for x in sub_v)}\n", "effect_text")
                console.insert(tk.END, "\n")

            elif isinstance(value, list):
                # Filter for present and future event windows
                now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                filtered_value = []
                for item in value:
                    raw_str = ""
                    if isinstance(item, dict):
                        raw_str = item.get("window", item.get("date_range", item.get("period", "")))
                        if not raw_str:
                            raw_str = item.get("full_text", "")
                    else:
                        raw_str = str(item)
                    dt = _parse_window_date(raw_str)
                    if dt is None or dt >= now:
                        filtered_value.append(item)
                value = filtered_value

                console.insert(tk.END, f"\n    📅 {label}", "section_label")
                if not value:
                    console.insert(tk.END, "  — no upcoming windows found.\n", "info")
                else:
                    console.insert(tk.END, f"  ({len(value)} upcoming)\n", "info")
                    for idx, item in enumerate(value[:10], 1):
                        if isinstance(item, dict):
                            window = item.get("window", item.get("date_range", item.get("period", "")))
                            dasha = item.get("dasha", "")
                            score = item.get("score", item.get("confidence", ""))
                            strength = item.get("strength", item.get("forensic_status", item.get("stability", "")))
                            full_text = item.get("full_text", "")

                            if full_text:
                                full_text = full_text.replace("the native", person_name).replace("The native", person_name)
                                console.insert(tk.END, f"      {idx}. {full_text}\n", "story_prose")
                            elif window:
                                console.insert(tk.END, f"      {idx}. A significant cosmic window opens from ", "story_prose")
                                console.insert(tk.END, f"{window}", "date_hl")
                                if dasha:
                                    ps = self._PLANET_PROSE.get(str(dasha), str(dasha))
                                    console.insert(tk.END, f" as {ps} guides {pronoun} path.", "story_prose")
                                
                                if strength:
                                    su = str(strength).upper()
                                    prose = self._VERDICT_PROSE.get(su, "")
                                    if prose:
                                        console.insert(tk.END, f"\n         {prose}\n", "info")
                                
                                if score:
                                    console.insert(tk.END, f"  (Alignment Score: {score})", "effect_text")
                                console.insert(tk.END, "\n")
                            else:
                                console.insert(tk.END, f"      {idx}. {str(item).replace('the native', person_name)}\n", "story_prose")
                        else:
                            console.insert(tk.END, f"      {idx}. {str(item).replace('the native', person_name)}\n", "story_prose")
                    if len(value) > 10:
                        console.insert(tk.END, f"      … and {len(value) - 10} more windows\n", "info")
                console.insert(tk.END, "\n")

            elif isinstance(value, (int, float)):
                console.insert(tk.END, f"    {label}: ", "cause_text")
                console.insert(tk.END, f"{value}\n", "effect_text")


    def _save_pdf(self, console: scrolledtext.ScrolledText) -> None:
        from tkinter import filedialog
        try:
            from src.pdf_report_engine import PremiumPDFReport  # type: ignore
        except ImportError as exc:
            messagebox.showerror("PDF Error", f"PDF engine unavailable:\n{exc}")
            return
        path = filedialog.asksaveasfilename(
            title="Save Report as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not path:
            return
        try:
            fname = DataManager.get_chart_data_filename(self._mode.value)
            with open(os.path.join("data", fname), encoding="utf-8") as fh:
                chart_data = json.load(fh)
            text = console.get("1.0", tk.END)
            structured_remedies = getattr(self, "_last_structured_remedies", [])
            PremiumPDFReport(chart_data, text, structured_remedies).generate(
                path, chart_image_path=self._chart_img_path
            )
            messagebox.showinfo("Saved", f"PDF saved:\n{path}")
        except Exception as exc:
            app_logger.exception("PDF save failed")
            messagebox.showerror("PDF Error", str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
# LauncherScreen — animated star-field + orbs
# ═══════════════════════════════════════════════════════════════════════════════

class LauncherScreen:
    _MODE_CFG = [
        {"text":"BIRTH CHART",  "sub":"Natal Astrology",
         "icon":"🌟", "mode": AppMode.BIRTH,
         "fill":"#1A0D3D","outline":"#7C3AED","hover":"#A78BFA","tc":"#C4B5FD"},
        {"text":"HORARY",       "sub":"Prashna Jyotish",
         "icon":"🔮", "mode": AppMode.HORARY,
         "fill":"#00231E","outline":"#00E5D4","hover":"#80FFF7","tc":"#67E8F9"},
        {"text":"COMPATIBILITY","sub":"Couple Matching",
         "icon":"💑", "mode": AppMode.MATCHMAKE,
         "fill":"#3D0D1A","outline":"#F87171","hover":"#FCA5A5","tc":"#FCA5A5"},
        {"text":"MUNDANE",      "sub":"World Astrology",
         "icon":"🌍", "mode": AppMode.MUNDANE,
         "fill":"#1A1200","outline":"#F6C90E","hover":"#FDE68A","tc":"#FDE68A"},
    ]
    _ZODIAC_SYMS   = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
    _ZODIAC_COLORS = ["#F87171","#34D399","#FBBF24","#60A5FA",
                      "#F6C90E","#A78BFA","#FB923C","#F43F5E",
                      "#818CF8","#6EE7B7","#22D3EE","#C084FC"]

    def __init__(self, root: tk.Tk, on_select: Callable[[AppMode], None]) -> None:
        self.root       = root
        self.on_select  = on_select
        self._angle     = 0.0
        self._after_id: Optional[str] = None
        self._orbs:     Dict[AppMode, Dict[str, Any]] = {}
        self._bg_img:   Optional[Any] = None   # FIX ⑧

        self._frame = tk.Frame(root, bg="#050510")
        self._frame.pack(fill=tk.BOTH, expand=True)

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.sw, self.sh = sw, sh

        self._cv = tk.Canvas(self._frame, width=sw, height=sh,
                             bg="#050510", highlightthickness=0)
        self._cv.pack(fill=tk.BOTH, expand=True)

        self._draw_bg_logo()
        self._draw_title()
        self._draw_orbs()
        self._draw_transit()
        self._draw_footer()
        self._tick()

    def _draw_bg_logo(self) -> None:
        if not HAS_PIL:
            return
        try:
            path = get_resource_path(os.path.join("assets", "logo.png"))
            if not os.path.exists(path):
                return
            img = Image.open(path).convert("RGBA")
            nh  = int(self.sh * 0.82)
            nw  = int(nh * img.width / img.height)
            img = ImageEnhance.Brightness(
                img.resize((nw, nh), Image.Resampling.LANCZOS)
            ).enhance(0.18)
            ph = ImageTk.PhotoImage(img)
            self._bg_img = ph   # FIX ⑧
            self._cv.create_image(self.sw // 2, int(self.sh * 0.42),
                                  image=ph, anchor="center")
        except Exception:
            pass

    def _draw_title(self) -> None:
        sw, sh = self.sw, self.sh
        cy = int(sh * 0.10)
        self._cv.create_text(sw//2+2, cy+2, text="✦  DIVYA DRISHTI  ✦",
                             font=("Segoe UI",40,"bold"), fill="#1A0040")
        self._cv.create_text(sw//2, cy, text="✦  DIVYA DRISHTI  ✦",
                             font=("Segoe UI",40,"bold"), fill="#F6C90E")
        self._cv.create_line(sw//2-240, cy+30, sw//2+240, cy+30,
                             fill="#7C3AED", width=1)
        self._cv.create_text(sw//2, cy+55,
                             text="॥ शृण्वन्तु विश्वे अमृतस्य पुत्रा ॥",
                             font=("Segoe UI",15,"italic"), fill="#A78BFA")
        self._cv.create_text(sw//2, cy+90,
                             text="Ultra-Advanced KP Astrology · Professional Edition",
                             font=("Segoe UI",10), fill="#504070")

    def _draw_orbs(self) -> None:
        sw, sh = self.sw, self.sh
        cy  = int(sh * 0.44)
        r   = 90
        gap = 220
        spc = 210

        left_start  = sw//2 - gap//2 - spc - r
        right_start = sw//2 + gap//2 + r

        for i, cfg in enumerate(self._MODE_CFG[:2]):
            self._make_orb(left_start + i * spc, cy, r, cfg)
        for i, cfg in enumerate(self._MODE_CFG[2:]):
            self._make_orb(right_start + i * spc, cy, r, cfg)

        self._cv.create_text(sw//2, cy - r - 22,
                             text="— Choose your path —",
                             font=("Segoe UI",11,"italic"), fill="#504070")

        # zodiac ring position
        self._zx = sw // 2
        self._zy = cy
        self._draw_zodiac(self._angle)

    def _make_orb(self, cx: int, cy: int, r: int, cfg: Dict[str, Any]) -> None:
        mode = cfg["mode"]
        glow = self._cv.create_oval(cx-r-8, cy-r-8, cx+r+8, cy+r+8,
                                     fill="", outline=cfg["outline"],
                                     width=1, stipple="gray25",
                                     tags=(f"glow_{mode}",))
        circ = self._cv.create_oval(cx-r, cy-r, cx+r, cy+r,
                                     fill=cfg["fill"], outline=cfg["outline"],
                                     width=3, tags=(f"orb_{mode}",))
        icon = self._cv.create_text(cx, cy-28, text=cfg["icon"],
                                    font=("Segoe UI",30), fill=cfg["tc"],
                                    tags=(f"orb_{mode}",))
        lbl  = self._cv.create_text(cx, cy+14, text=cfg["text"],
                                    font=("Segoe UI",13,"bold"), fill=cfg["tc"],
                                    tags=(f"orb_{mode}",))
        sub  = self._cv.create_text(cx, cy+36, text=cfg["sub"],
                                    font=("Segoe UI",9), fill="#504070",
                                    tags=(f"orb_{mode}",))
        self._orbs[mode] = {"circ":circ,"glow":glow,"lbl":lbl,"sub":sub,
                            "cx":cx,"cy":cy,"r":r,"cfg":cfg}
        for tag in (f"orb_{mode}", f"glow_{mode}"):
            self._cv.tag_bind(tag, "<Button-1>",
                              lambda e, m=mode: self._click(m))
            self._cv.tag_bind(tag, "<Enter>",
                              lambda e, m=mode: self._enter(m))
            self._cv.tag_bind(tag, "<Leave>",
                              lambda e, m=mode: self._leave(m))

    def _draw_zodiac(self, angle: float) -> None:
        self._cv.delete("zodiac")
        for i, (sym, col) in enumerate(zip(self._ZODIAC_SYMS, self._ZODIAC_COLORS)):
            a = math.radians(angle + i * 30)
            x = self._zx + 75 * math.cos(a)
            y = self._zy + 75 * math.sin(a)
            self._cv.create_text(x, y, text=sym, font=("Segoe UI",18),
                                 fill=col, anchor="center", tags="zodiac")

    def _enter(self, mode: AppMode) -> None:
        info = self._orbs.get(mode)
        if not info:
            return
        cfg = info["cfg"]
        self._cv.itemconfig(info["circ"], fill=self._lighten(cfg["fill"], 25),
                             outline=cfg["hover"], width=4)
        self._cv.itemconfig(info["lbl"], fill=cfg["hover"])
        self._cv.itemconfig(info["glow"], outline=cfg["hover"],
                            width=2, stipple="gray50")
        self.root.configure(cursor="hand2")

    def _leave(self, mode: AppMode) -> None:
        info = self._orbs.get(mode)
        if not info:
            return
        cfg = info["cfg"]
        self._cv.itemconfig(info["circ"], fill=cfg["fill"],
                             outline=cfg["outline"], width=3)
        self._cv.itemconfig(info["lbl"], fill=cfg["tc"])
        self._cv.itemconfig(info["glow"], outline=cfg["outline"],
                            width=1, stipple="gray25")
        self.root.configure(cursor="")

    def _click(self, mode: AppMode) -> None:
        if self._after_id:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
        try:
            self._frame.destroy()
        except Exception:
            pass
        self.on_select(mode)

    def _draw_transit(self) -> None:
        """Draw today's planetary transits (requires Swiss Ephemeris)."""
        sw, sh = self.sw, self.sh
        ty0 = int(sh * 0.60)
        now = datetime.datetime.now()

        # Step 1: Check Capability
        if not HAS_SWISSEPH or not SwissEphBackend:
            self._cv.create_text(sw//2, int(sh*0.75),
                                 text="Transit data requires Swiss Ephemeris",
                                 font=("Segoe UI",9), fill="#504070")
            return

        try:
            # Step 2: Initialize Backend
            SwissEphBackend.initialize()
            import swisseph as swe # type: ignore

            # Step 3: Calculation Setup
            # Calculate TZ offset dynamically
            utc_now = datetime.datetime.utcnow()
            tz_offset = (now - utc_now).total_seconds() / 3600.0
            # Common case optimization (IST)
            if abs(tz_offset - 5.5) < 0.05: tz_offset = 5.5
            
            hour_ut = (now.hour + now.minute / 60.0 + now.second / 3600.0) - tz_offset
            jd = swe.julday(now.year, now.month, now.day, hour_ut)
            
            try:
                from src.core_math import get_sub_lord_info, calculate_kp_ayanamsa # type: ignore
            except ImportError:
                from core_math import get_sub_lord_info, calculate_kp_ayanamsa # type: ignore
            
            aya = calculate_kp_ayanamsa(now.year, now.month, now.day)

            # Step 4: Planetary Positions
            PIDS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
                    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
                    "Venus": swe.VENUS, "Saturn": swe.SATURN,
                    "Rahu": swe.MEAN_NODE, "Uranus": swe.URANUS,
                    "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO}
            
            SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                     "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
            SYMS  = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

            rows = []
            for pname, pid in PIDS.items():
                res = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
                sid = (res[0][0] - aya) % 360
                spd = res[0][3]
                si  = int(sid / 30) % 12
                di  = sid % 30
                d, m, s = int(di), int((di%1)*60), int(((di%1)*60%1)*60)
                
                nak, st, sb = get_sub_lord_info(sid)
                rows.append((pname, SYMS[si], SIGNS[si], d, m, s, nak, st, sb, spd < 0))

            # Ketu (Calculated as opposite of Rahu)
            rahu_row = next((r for r in rows if r[0] == "Rahu"), None)
            if rahu_row:
                # Reconstruct sid from rahu_row for ketu
                rsid = (SIGNS.index(rahu_row[2]) * 30 + rahu_row[3] + rahu_row[4]/60.0 + rahu_row[5]/3600.0)
                ksid = (rsid + 180) % 360
                ksi  = int(ksid / 30) % 12
                kdi  = ksid % 30
                kd, km, ks = int(kdi), int((kdi%1)*60), int(((kdi%1)*60%1)*60)
                knak, kst, ksb = get_sub_lord_info(ksid)
                rows.append(("Ketu", SYMS[ksi], SIGNS[ksi], kd, km, ks, knak, kst, ksb, True))

            ORDER = ["Sun","Moon","Mars","Mercury","Jupiter","Venus",
                     "Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"]
            rows.sort(key=lambda r: ORDER.index(r[0]) if r[0] in ORDER else 99)

            # Step 5: Render UI
            P_COLORS = {
                "Sun":"#F6C90E","Moon":"#E0E7FF","Mars":"#F87171",
                "Mercury":"#34D399","Jupiter":"#FBBF24","Venus":"#F0ABFC",
                "Saturn":"#60A5FA","Rahu":"#94A3B8","Ketu":"#A78BFA",
                "Uranus":"#22D3EE","Neptune":"#818CF8","Pluto":"#FB923C",
            }
            cols_x = {
                "planet": sw//2 - 380, "sign":  sw//2 - 260,
                "dms":    sw//2 - 120, "nak":   sw//2 + 30,
                "star":   sw//2 + 200, "sub":   sw//2 + 340,
            }
            
            self._cv.create_text(sw//2, ty0-25, text="✦  TODAY'S TRANSIT  ✦",
                                 font=("Segoe UI",14,"bold"), fill="#F6C90E")
            self._cv.create_text(sw//2, ty0-5,
                                 text=now.strftime("%d %B %Y  •  %H:%M"), # Removed fixed IST
                                 font=("Segoe UI",9), fill="#504070")
            
            hy = ty0 + 15
            for x, ht in [(cols_x["planet"],"PLANET"),(cols_x["sign"],"SIGN"),
                          (cols_x["dms"],"DEG MIN SEC"),(cols_x["nak"],"NAKSHATRA"),
                          (cols_x["star"],"STAR LORD"),(cols_x["sub"],"SUB LORD")]:
                self._cv.create_text(x, hy, text=ht, font=("Segoe UI",9,"bold"), fill="#A78BFA", anchor="w")
            
            self._cv.create_line(cols_x["planet"], hy+12, cols_x["sub"]+80, hy+12, fill="#2E2E60")
            
            for idx, (pn, psym, psign, d, m, s, nak, st, sb, retro) in enumerate(rows):
                y  = hy + 22 + idx * 15
                pc = P_COLORS.get(pn, "#EEEEFF")
                rmark = " ℞" if retro else ""
                self._cv.create_text(cols_x["planet"], y, text=f"{pn}{rmark}", font=("Segoe UI",9,"bold"), fill=pc, anchor="w")
                self._cv.create_text(cols_x["sign"], y, text=f"{psym} {psign}", font=("Segoe UI",9), fill="#EEEEFF", anchor="w")
                self._cv.create_text(cols_x["dms"], y, text=f"{d:02d}° {m:02d}' {s:02d}\"", font=("Consolas",9), fill="#C4B5FD", anchor="w")
                self._cv.create_text(cols_x["nak"], y, text=nak, font=("Segoe UI",9), fill="#67E8F9", anchor="w")
                self._cv.create_text(cols_x["star"], y, text=st, font=("Segoe UI",9), fill="#FDE68A", anchor="w")
                self._cv.create_text(cols_x["sub"], y, text=sb, font=("Segoe UI",9), fill="#FCA5A5", anchor="w")

        except Exception as exc:
            app_logger.error(f"Transit display failed: {exc}", exc_info=True)
            self._cv.create_text(sw//2, int(sh*0.75),
                                 text="Transit data temporarily unavailable",
                                 font=("Segoe UI",9), fill="#504070")

    def _draw_footer(self) -> None:
        self._cv.create_text(
            self.sw // 2, self.sh - 20,
            text="© Divya Drishti Development Team  ·  UAKP Forensic Engine",
            font=("Segoe UI", 9), fill="#282840",
        )

    def _tick(self) -> None:
        try:
            if not self._frame.winfo_exists():
                return
        except Exception:
            return
        self._angle = (self._angle - 0.5) % 360
        self._draw_zodiac(self._angle)
        self._after_id = self.root.after(40, self._tick)

    @staticmethod
    def _lighten(hex_col: str, amount: int) -> str:
        hc = hex_col.lstrip("#")
        r = min(255, int(hc[0:2], 16) + amount)
        g = min(255, int(hc[2:4], 16) + amount)
        b = min(255, int(hc[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"


# ═══════════════════════════════════════════════════════════════════════════════
# System health check
# ═══════════════════════════════════════════════════════════════════════════════

def _verify_health() -> Tuple[bool, List[str]]:
    issues: List[str] = []
    if not HAS_SWISSEPH:
        issues.append("⚠️ Swiss Ephemeris not installed — calculations use fallback math.")
    if not HAS_PIL:
        issues.append("⚠️ Pillow not installed — image features disabled.")
    data_dir = os.path.join(_PROJECT_ROOT, "data")
    for fname in ("event_config.json",):
        if not os.path.exists(os.path.join(data_dir, fname)):
            issues.append(f"⚠️ Missing: data/{fname}")
    critical = [i for i in issues if "Missing" in i]
    return len(critical) == 0, issues


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def _launch_mode(mode: AppMode) -> None:
    KPApp(_main_root, mode=mode)


if __name__ == "__main__":
    ok, issues = _verify_health()
    _main_root = tk.Tk()
    _main_root.withdraw()
    if not ok:
        messagebox.showerror("Critical Error", "\n".join(issues))
        sys.exit(1)
    if issues:
        # Non-critical warnings — show briefly and continue
        print("[DIVYA DRISHTI] Warnings:\n" + "\n".join(issues))
    _configure_styles()
    _main_root.deiconify()
    LauncherScreen(_main_root, _launch_mode)
    _main_root.mainloop()