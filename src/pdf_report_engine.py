"""
DIVYA DRISHTI — Premium PDF Report Engine (International Professional Edition v3.0)
===================================================================================
Building on v2.0 with major enhancements:
  1. Full navy gradient cover page with sunburst decoration
  2. Ruling Planets (RP) computation and professional display
  3. DOB, TOB, POB with coordinates on cover card
  4. Watermark on every content page
  5. Table of Contents with dotted leaders
  6. Professional disclaimer page
  7. Decorative dividers between major sections
  8. Enhanced page chrome (header bar + ornamental footer)

Previous fixes (v2.0) preserved:
  1. Markdown ** rendering bug — fully fixed with robust regex
  2. Rahu/Ketu house detection — reads actual house from chart_data
  3. Moon Nakshatra source — reads from planetary_positions, not hardcoded
  4. Signature on same page — no wasted blank page
  5. metadata key fixes — handles missing 'mode', 'ruling_planets'
  6. house_significators key fix — uses 'L1','L2','L3','L4' correctly
  7. dasa duration format — handles '19.00 yrs' string correctly
  8. Chapter colored headers — Blue>Teal>Purple cycling on content
  9. Rahu/Ketu axis house fix — correctly shows H8/H2 not H2/H2
 10. Page overflow guard — prevents content going into footer area
"""

import os
import re
import math
import datetime
from typing import Any, Dict, List, cast
from fpdf import FPDF  # type: ignore

try:
    from src.utils import get_resource_path  # type: ignore
except ImportError:
    def get_resource_path(p):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), p)


# ─── Design Token System v4.0 (2 Primary + 1 Accent) ───────────────────────
class Colors:
    # ── Primary Palette ──
    PRIMARY       = (18, 38, 84)     # Deep Navy — chapter headers, key UI
    PRIMARY_MED   = (52, 78, 140)    # Slate Blue — section sub-headers
    PRIMARY_LIGHT = (232, 237, 252)  # Pale blue — zebra rows, section bg

    # ── Accent (Gold — cover & TOC accents only) ──
    ACCENT        = (184, 142, 20)
    ACCENT_DIM    = (140, 106, 14)
    ACCENT_PALE   = (250, 243, 210)

    # ── Cover-page dark backgrounds ──
    NAVY          = (8, 12, 28)
    NAVY_MED      = (16, 22, 50)

    # ── Status ──
    GREEN_DARK    = (5, 118, 58)
    SUCCESS_BG    = (225, 248, 235)
    RED           = (185, 38, 38)
    DANGER_BG     = (255, 232, 232)
    AMBER         = (176, 126, 0)
    WARN_BG       = (255, 247, 220)

    # ── Neutrals ──
    WHITE         = (255, 255, 255)
    BODY_TEXT     = (22, 22, 28)      # v5: darker for better contrast
    DARK_GREY     = (55, 55, 65)
    MUTED         = (115, 120, 135)
    RULE          = (210, 215, 228)  # Hairlines, table separators
    XLIGHT        = (248, 249, 253)  # v5: lighter zebra for modern feel
    WATERMARK     = (220, 220, 228)

    # ── Legacy aliases — kept for cover-page methods ──
    GOLD          = (184, 142, 20)
    GOLD_LIGHT    = (230, 190, 70)
    GOLD_PALE     = (250, 243, 210)
    GOLD_DIM      = (140, 106, 14)
    GOLD_CHAMPAGNE = (250, 243, 210)
    GOLD_DARK     = (110, 82, 12)
    BLACK         = (30, 30, 38)
    MID_GREY      = (115, 120, 135)
    LIGHT_GREY    = (210, 215, 228)
    XLIGHT_GREY   = (245, 246, 250)
    BLUE          = (18, 38, 84)
    BLUE_LIGHT    = (232, 237, 252)
    TEAL          = (18, 38, 84)
    TEAL_LIGHT    = (245, 246, 250)
    PURPLE        = (18, 38, 84)
    PURPLE_LIGHT  = (232, 237, 252)
    ROSE          = (185, 38, 38)
    CREAM         = (255, 255, 255)
    WARM_WHITE    = (255, 255, 255)
    NAVY_LIGHT    = (28, 36, 72)

    # Unified section accent — single, no cycling
    SECTION           = (18, 38, 84)
    SECTION_BG        = (232, 237, 252)
    SECTION_COLORS    = [(18, 38, 84)] * 4
    SECTION_BG_COLORS = [(232, 237, 252)] * 4


# ─── Spacing Scale v5.0 ───────────────────────────────────────────────────────
SP_SECTION_GAP = 12   # mm before chapter header (v5: +2 breathing room)
SP_BLOCK_GAP   = 8    # mm between content blocks (v5: +2)
SP_TABLE_ROW_H = 8.0  # mm table data row height (v5: +0.5 readability)
SP_TABLE_HDR_H = 9.0  # mm table header row height (v5: +0.5)
SP_LINE_H      = 6.2  # mm body line height (v5: ≈1.5 × 10pt)
SP_PARA_GAP    = 3.0  # mm gap between prose paragraphs (v5: new)


# ─── Markdown Cleaner ────────────────────────────────────────────────────────
def strip_markdown(text: str) -> str:
    """Remove ALL markdown markers from text — used for plain rendering."""
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    return text.strip()


def parse_markdown_parts(text: str):
    """
    Parse markdown inline tokens into list of (style, content) tuples.
    Handles: ***bold italic***, **bold**, *italic*, plain text.
    FIX: Handles edge cases like '**SPECIAL INSIGHT: **' correctly.
    """
    # First clean up malformed markers like '** ' at end
    text = re.sub(r'\*\*\s*\*\*', '', text)   # empty bold: ** **
    text = re.sub(r'\*\s*\*', '', text)         # empty italic: * *

    pattern = re.compile(r'(\*{3}(.+?)\*{3}|\*{2}(.+?)\*{2}|\*(.+?)\*)')
    parts = []
    last_end = 0

    for match in pattern.finditer(text):
        start, end = match.span()
        if start > last_end:
            parts.append(("", "".join(text[j] for j in range(last_end, start))))
        if match.group(2):
            parts.append(("BI", match.group(2)))
        elif match.group(3):
            parts.append(("B", match.group(3)))
        elif match.group(4):
            parts.append(("I", match.group(4)))
        last_end = end

    if last_end < len(text):
        parts.append(("", "".join(text[j] for j in range(last_end, len(text)))))

    return parts if parts else [("", text)]


class _AlignedRow(list):
    """A list subclass that carries per-column alignment metadata for _render_table."""
    def __init__(self, data: list, aligns: list):
        super().__init__(data)
        self._col_aligns = aligns


class PremiumPDFReport(FPDF):
    """
    Premium PDF report generator for Divya Drishti — International Professional Edition v5.0
    """

    def __init__(self, chart_data, report_text, structured_remedies=None):
        super().__init__()
        self.chart_data = cast(Dict[str, Any], chart_data or {})
        self.report_text = report_text or ""
        self._structured_remedies = structured_remedies or []
        self._current_chapter_idx = 0
        self._chart_image_path = None
        self._ruling_planets_text = None
        self._chapter_list = []       # For TOC
        self._toc_start_page = 0      # Page where TOC starts
        self._is_cover_page = False    # Track cover page for watermark skip
        self._ruling_planets_data = {} # Computed RP
        self._current_section_name = "Divya Drishti"  # v4.0: footer section tracker
        self._quote_count = 0           # v5.0: quote rotation limiter
        self._chapter_verdicts = []     # v5.0: for executive summary

        # ── Font Registration ──
        win_fonts = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        font_map = {
            "":   os.path.join(win_fonts, "segoeui.ttf"),
            "B":  os.path.join(win_fonts, "segoeuib.ttf"),
            "I":  os.path.join(win_fonts, "segoeuii.ttf"),
            "BI": os.path.join(win_fonts, "segoeuiz.ttf"),
        }
        if all(os.path.exists(p) for p in font_map.values()):
            self.add_font("SegoeUI", "",   font_map[""])
            self.add_font("SegoeUI", "B",  font_map["B"])
            self.add_font("SegoeUI", "I",  font_map["I"])
            self.add_font("SegoeUI", "BI", font_map["BI"])
            self._font_family = "SegoeUI"
        else:
            self._font_family = "Helvetica"

        # Single font family: SegoeUI throughout — no serif/sans mixing
        self._has_georgia = False

        self.set_auto_page_break(auto=True, margin=22)

        # Compute Ruling Planets
        self._ruling_planets_data = self._compute_ruling_planets()

    # ── Emoji / Unsupported Glyph Cleaner ─────────────────────────────────
    # Maps common emoji to ASCII-friendly text equivalents
    _EMOJI_MAP = {
        "\U0001f3af": "[*]", "\u26a1": ">>>", "\u2b50": "*", "\u2728": "*", "\U0001f4b0": "$",
        "\U0001f4c8": "^", "\U0001f3db": "[H]", "\U0001f31f": "*", "\u2696": "[=]", "\U0001f9ed": "[C]",
        "\U0001f4a1": "[i]", "\U0001f319": "[M]", "\U0001f531": "[T]", "\U0001f4dc": "[D]", "\U0001f575": "[S]",
        "\U0001f52e": "[P]", "\U0001f491": "[2]", "\U0001f30d": "[W]", "\U0001f6a8": "[!]", "\U0001f691": "[+]",
        "\u2705": "[OK]", "\u274c": "[X]", "\u26a0": "[!]", "\ufe0f": "",
        "\u25b8": ">", "\u25b9": ">", "\u25c8": "+", "\u25c6": "+", "\u25c7": "+",
        "\u2588": "=", "\u2591": ".", "\u26d4": "[X]", "\U0001f4ca": "[||]", "\u23f3": "[T]",
        "\U0001f4d0": "[A]", "\u2551": "|", "\u2500": "-",
        "\u2605": "*", "\u2606": "*", "\u2666": "+", "\u2660": "+", "\u2663": "+",
        "\u2665": "+", "\u2726": "*", "\u2727": "*", "\u25c9": "o", "\u25ce": "o",
        "\u25b6": ">", "\u25ba": ">", "\u25c0": "<", "\u25c4": "<",
        "\u2191": "^", "\u2193": "v", "\u2190": "<", "\u2192": ">",
        "\u2714": "[OK]", "\u2716": "[X]", "\u2611": "[OK]", "\u2612": "[X]",
        "\u2b06": "^", "\u2b07": "v", "\u2b05": "<", "\u27a1": ">",
        "\U0001f525": "[!]", "\U0001f4ab": "*", "\U0001f33f": "~", "\U0001fa90": "[P]",
        "\U0001f31e": "[Sun]", "\U0001f31b": "[Moon]", "\u2648": "Ari", "\u2649": "Tau",
        "\u264a": "Gem", "\u264b": "Can", "\u264c": "Leo", "\u264d": "Vir",
        "\u264e": "Lib", "\u264f": "Sco", "\u2650": "Sag", "\u2651": "Cap",
        "\u2652": "Aqu", "\u2653": "Pis",
    }

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Strip all emoji and unsupported Unicode glyphs from text.
        Replaces known emoji with ASCII equivalents, removes the rest.
        This prevents 'Font is missing glyph' warnings in FPDF.
        """
        if not text:
            return text
        # Replace known emoji with ASCII equivalents
        for emoji, replacement in PremiumPDFReport._EMOJI_MAP.items():
            text = text.replace(emoji, replacement)
        # Remove any remaining characters outside BMP (emoji range U+10000+)
        # and other problematic Unicode blocks
        cleaned = []
        for ch in text:
            cp = ord(ch)
            # Keep ASCII, Latin, Greek, Cyrillic, Devanagari, Bengali, and common symbols
            if cp < 0x2700:  # Below dingbats block — keep everything
                cleaned.append(ch)
            elif 0x2700 <= cp < 0x2800:  # Dingbats — selective keep
                if ch in '\u2713\u2717':  # Keep basic check/cross
                    cleaned.append(ch)
                # Skip other dingbats
            elif cp > 0xFFFF:  # Supplementary planes (emoji, etc.) — remove
                pass
            elif 0xFE00 <= cp <= 0xFE0F:  # Variation selectors — remove
                pass
            else:
                cleaned.append(ch)
        return ''.join(cleaned)

    # ── FIX: Helper — get planet house number from chart_data ──────────────
    def _get_planet_house(self, planet_name: str) -> int:
        """
        Determine which house a planet occupies based on its longitude
        vs house cusp longitudes. Returns house number 1-12.
        FIX: Used to correctly show Rahu in H8, Ketu in H2.
        """
        positions = self.chart_data.get("planetary_positions", [])
        cusps = self.chart_data.get("house_cusps", [])

        planet_lon = None
        for p in positions:
            if p.get("planet") == planet_name:
                dms = p.get("longitude_dms", "")
                planet_lon = self._dms_to_degrees(dms)
                break

        if planet_lon is None or not cusps:
            return 0
        from typing import cast  # type: ignore
        planet_lon = cast(float, planet_lon)

        cusp_lons = []
        for c in cusps:
            cusp_lons.append(self._dms_to_degrees(c.get("longitude_dms", "0")))

        # Find house: planet is in house N if between cusp N and cusp N+1
        for i in range(12):
            c_start = cusp_lons[i]
            c_end = cusp_lons[(i + 1) % 12]
            if c_start <= c_end:
                if c_start <= float(planet_lon) < c_end:  # type: ignore
                    return i + 1
            else:  # Wraps around 360
                if planet_lon >= c_start or planet_lon < c_end:  # type: ignore
                    return i + 1
        return 1

    def _dms_to_degrees(self, dms: str) -> float:
        """Convert '23 20' 27\"' to decimal degrees."""
        try:
            nums = re.findall(r'[\d.]+', dms)
            if len(nums) >= 3:
                return float(nums[0]) + float(nums[1])/60 + float(nums[2])/3600
            elif len(nums) == 1:
                return float(nums[0])
        except Exception:
            pass
        return 0.0

    # ── FIX: Get planet nakshatra from chart_data ──────────────────────────
    def _get_planet_nakshatra(self, planet_name: str) -> str:
        """
        FIX for Moon Nakshatra bug:
        Returns actual nakshatra from planetary_positions,
        not from hardcoded values.
        """
        for p in self.chart_data.get("planetary_positions", []):
            if p.get("planet") == planet_name:
                return p.get("nakshatra", "")
        return ""

    # ── Sign Lord Lookup ────────────────────────────────────────────────────
    _SIGN_LORDS = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
        "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
        "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
    }

    # ── Ruling Planets Computation ─────────────────────────────────────────
    def _compute_ruling_planets(self) -> Dict[str, str]:
        """
        Compute KP Ruling Planets from chart data.
        Returns dict with: Asc Sign Lord, Asc Star Lord,
        Moon Sign Lord, Moon Star Lord, Day Lord.
        """
        meta = self.chart_data.get("metadata", {})
        cusps = self.chart_data.get("house_cusps", [])
        positions = self.chart_data.get("planetary_positions", [])

        rp = {}

        # 1. Ascendant Lords (from Cusp 1)
        for c in cusps:
            if c.get("cusp") == 1:
                rp["Asc Sign Lord"] = c.get("sign_lord", "")
                rp["Asc Star Lord"] = c.get("star_lord", "")
                break

        # 2. Moon Lords — derive sign_lord from sign if not directly available
        for p in positions:
            if p.get("planet") in ("Moon", "Mon"):
                moon_sign_lord = p.get("sign_lord", "")
                if not moon_sign_lord:
                    moon_sign = p.get("sign", "")
                    moon_sign_lord = self._SIGN_LORDS.get(moon_sign, "")
                rp["Moon Sign Lord"] = moon_sign_lord
                rp["Moon Star Lord"] = p.get("star_lord", "")
                break

        # 3. Day Lord (from DOB weekday)
        dob = meta.get("dob", "")
        if dob:
            try:
                dt = datetime.datetime.strptime(dob, "%d-%m-%Y")
                # Monday=0 ... Sunday=6
                day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
                rp["Day Lord"] = day_lords[dt.weekday()]
            except Exception:
                pass

        return rp

    # ── Chapter Pre-scanner for TOC ────────────────────────────────────────
    def _prescan_chapters(self):
        """Pre-scan report text for chapter titles to build TOC."""
        if not self.report_text:
            return
        circle_nums = "\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468\u2469\u246a\u246b\u246c\u246d\u246e\u246f\u2470\u2471\u2472\u2473"
        lines = self.report_text.split("\n")
        self._chapter_list = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            for cn in circle_nums:
                if stripped.startswith(cn):
                    title = stripped[len(cn):].strip()
                    title = strip_markdown(title)
                    for ch in "\u2502\u250c\u2514\u2510\u2518\u2504":
                        title = title.replace(ch, "")
                    title = self._clean_text(title.strip())
                    if title:
                        self._chapter_list.append(title)
                    break

    # ─── Page Border, Header Bar & Watermark ─────────────────────────────
    def header(self):
        if self._is_cover_page:
            return

        # v4.0: Slim single top bar — no double borders, no corner flourishes
        self.set_fill_color(*Colors.PRIMARY)
        self.rect(0, 0, self.w, 5.5, style="F")
        self.set_font(self._font_family, "", 6.5)
        self.set_text_color(*Colors.ACCENT_PALE)
        self.set_xy(18, 0.6)
        self.cell(0, 4.2, "Divya Drishti  ·  KP Professional Analysis", align="L")

        # Watermark (faint rotated text)
        self._render_watermark()

    def _render_watermark(self):
        """Render faint rotated watermark. CRITICAL: save/restore XY."""
        saved_x, saved_y = self.get_x(), self.get_y()
        self.set_font(self._font_family, "B", 48)
        self.set_text_color(*Colors.WATERMARK)
        with self.rotation(33, self.w / 2, self.h / 2):
            self.set_xy(self.w / 2 - 60, self.h / 2 - 10)
            self.cell(120, 20, "Private & Confidential", align="C")
        self.set_xy(saved_x, saved_y)

    def footer(self):
        if self._is_cover_page:
            return

        # v4.0: Clean hairline rule + section name left, page number right
        rule_y = self.h - 13
        self.set_draw_color(*Colors.RULE)
        self.set_line_width(0.2)
        self.line(18, rule_y, self.w - 18, rule_y)

        # Left: current section/chapter name
        self.set_font(self._font_family, "", 7.5)
        self.set_text_color(*Colors.MUTED)
        self.set_xy(18, rule_y + 1.5)
        section_name = getattr(self, '_current_section_name', 'Divya Drishti')
        self.cell(self.w / 2 - 10, 6, self._clean_text(section_name[:55]), align="L")

        # Right: page number
        self.set_font(self._font_family, "B", 8)
        self.set_text_color(*Colors.PRIMARY)
        self.set_xy(self.w / 2, rule_y + 1.5)
        self.cell(self.w / 2 - 18, 6, f"Page  {self.page_no()}", align="R")

    # ─── Cover Page (International Professional Grade) ─────────────────────
    def _render_cover_page(self):
        self._is_cover_page = True
        self.set_auto_page_break(auto=False)
        self.add_page()

        meta = self.chart_data.get("metadata", {})
        name = meta.get("name", "Jataka")
        dob  = meta.get("dob", "")
        tob  = meta.get("tob", "")
        gender = meta.get("gender", "")
        mode_raw = meta.get("mode", meta.get("analysis_mode", "Birth Chart"))
        mode = str(mode_raw).replace("_", " ").title()
        location = meta.get("location", {})
        place = location.get("city", "") if isinstance(location, dict) else str(location)
        lat = str(meta.get("lat", location.get("lat", "") if isinstance(location, dict) else ""))
        lon = str(meta.get("lon", location.get("lon", "") if isinstance(location, dict) else ""))
        ayanamsa = meta.get("ayanamsa", "")

        pw = self.w
        ph = self.h
        cx = pw / 2

        # ── Full Navy Background ──
        self.set_fill_color(*Colors.NAVY)
        self.rect(0, 0, pw, ph, style="F")

        # ── Subtle Sunburst Rays ──
        self.set_draw_color(30, 38, 80)
        self.set_line_width(0.3)
        ray_cx, ray_cy = cx, 45
        for angle_deg in range(0, 360, 12):
            rad = math.radians(angle_deg)
            ex = ray_cx + 110 * math.cos(rad)
            ey = ray_cy + 110 * math.sin(rad)
            self.line(ray_cx, ray_cy, ex, ey)

        # ── Concentric Circles ──
        self.set_draw_color(25, 32, 68)
        self.set_line_width(0.2)
        for r in [88, 72, 58]:
            self.ellipse(cx - r, 45 - r, r * 2, r * 2, style="D")

        # ── Gold & Inner Borders ──
        self.set_draw_color(*Colors.GOLD)
        self.set_line_width(1.2)
        self.rect(5, 5, pw - 10, ph - 10)
        self.set_draw_color(*Colors.GOLD_DIM)
        self.set_line_width(0.3)
        self.rect(8, 8, pw - 16, ph - 16)

        # ── Logo ──
        y = 22
        logo_path = get_resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            logo_w = 44
            self.image(logo_path, x=cx - logo_w / 2, y=y, w=logo_w)
            y += 58
        else:
            y += 18

        # ── Diamond Chain Separator ──
        self.set_fill_color(*Colors.GOLD)
        diamond_y = y + 2
        for dx in [-20, -10, 0, 10, 20]:
            dcx = cx + dx
            sz = 2.2
            self.polygon([
                (dcx, diamond_y - sz), (dcx + sz, diamond_y),
                (dcx, diamond_y + sz), (dcx - sz, diamond_y),
            ], style="F")
        y += 10

        # ── Title ──
        self.set_y(y)
        self.set_font(self._font_family, "B", 36)
        self.set_text_color(*Colors.GOLD_LIGHT)
        self.cell(0, 16, "DIVYA DRISHTI", align="C", new_x="LMARGIN", new_y="NEXT")
        y = float(self.get_y())

        # ── Tagline — v5: 14pt regular, clearer hierarchy tier ──
        self.set_font(self._font_family, "", 14)
        self.set_text_color(130, 160, 210)
        self.cell(0, 9, "Complete Astrological Analysis Report", align="C", new_x="LMARGIN", new_y="NEXT")
        y = float(self.get_y()) + 3

        # ── Edition Badge ──
        badge_w = 68
        badge_h = 8
        badge_x = cx - badge_w / 2
        self.set_fill_color(*Colors.GOLD_DIM)
        self.set_draw_color(*Colors.GOLD)
        self.set_line_width(0.3)
        self.rect(badge_x, y, badge_w, badge_h, style="DF")
        self.set_font(self._font_family, "B", 8)
        self.set_text_color(*Colors.NAVY)
        self.set_xy(badge_x, y + 1)
        self.cell(badge_w, 6, "K P   P R O F E S S I O N A L   E D I T I O N", align="C")
        y += badge_h + 7

        # ── Gold Separator ──
        self.set_draw_color(*Colors.GOLD)
        self.set_line_width(0.8)
        self.line(35, y, pw - 35, y)
        y += 6

        # ── Birth Details Card ──
        card_x = 28
        card_w = pw - 56
        card_h = 82
        # Card background (slight gradient effect)
        self.set_fill_color(12, 16, 36)
        self.set_draw_color(*Colors.GOLD_DIM)
        self.set_line_width(0.5)
        self.rect(card_x, y, card_w, card_h, style="DF")

        # Card header
        self.set_fill_color(*Colors.GOLD_DIM)
        self.rect(card_x, y, card_w, 11, style="F")
        self.set_font(self._font_family, "B", 9)
        self.set_text_color(*Colors.NAVY)
        self.set_xy(card_x, y + 2)
        self.cell(card_w, 7, "Nativity Details", align="C")

        # Detail rows
        details_y = y + 16
        pob_str = place
        if lat and lon and lat != "" and lon != "":
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                lat_dir = "N" if lat_f >= 0 else "S"
                lon_dir = "E" if lon_f >= 0 else "W"
                pob_str = f"{place}  ({abs(lat_f):.4f}{lat_dir}, {abs(lon_f):.4f}{lon_dir})"
            except (ValueError, TypeError):
                pass

        ayanamsa_str = ""
        if ayanamsa:
            try:
                ayanamsa_str = f"{float(ayanamsa):.6f} (KP Ayanamsa)"
            except (ValueError, TypeError):
                ayanamsa_str = str(ayanamsa)

        detail_items = [
            ("Name",           name),
            ("Date of Birth",  dob),
            ("Time of Birth",  tob),
            ("Place of Birth", pob_str),
            ("Gender",         gender),
            ("Analysis Mode",  mode),
        ]
        if ayanamsa_str:
            detail_items.append(("Ayanamsa", ayanamsa_str))

        label_x = card_x + 8
        value_x = card_x + 52
        for label, value in detail_items:
            if not value:
                continue
            self.set_y(details_y)
            self.set_x(label_x)
            self.set_font(self._font_family, "B", 9)
            self.set_text_color(*Colors.GOLD_LIGHT)
            self.cell(42, 7, f"{label}:", align="L")
            self.set_x(value_x)
            self.set_font(self._font_family, "", 9)
            self.set_text_color(*Colors.WHITE)
            self.cell(card_w - 56, 7, self._clean_text(str(value)), align="L")
            details_y += 9

        y += card_h + 5

        # ── Partner Birth Details Card (Compatibility Mode) ──
        partner = meta.get("partner_details", {})
        if partner and partner.get("name"):
            p_card_h = 52
            # Check space
            if y + p_card_h > ph - 50:
                p_card_h = 42  # Compact
            self.set_fill_color(12, 16, 36)
            self.set_draw_color(*Colors.ROSE)
            self.set_line_width(0.5)
            self.rect(card_x, y, card_w, p_card_h, style="DF")

            # Card header
            self.set_fill_color(*Colors.ROSE)
            self.rect(card_x, y, card_w, 11, style="F")
            self.set_font(self._font_family, "B", 9)
            self.set_text_color(*Colors.WHITE)
            self.set_xy(card_x, y + 2)
            self.cell(card_w, 7, "Partner Details", align="C")

            p_details_y = y + 16
            p_loc = partner.get("location", {})
            p_place = p_loc.get("city", "") if isinstance(p_loc, dict) else ""
            p_lat = str(partner.get("lat", ""))
            p_lon = str(partner.get("lon", ""))
            p_pob = p_place
            if p_lat and p_lon and p_lat != "" and p_lon != "":
                try:
                    plf = float(p_lat)
                    plnf = float(p_lon)
                    p_pob = f"{p_place}  ({abs(plf):.4f}{'N' if plf >= 0 else 'S'}, {abs(plnf):.4f}{'E' if plnf >= 0 else 'W'})"
                except (ValueError, TypeError):
                    pass

            p_detail_items = [
                ("Name",           partner.get("name", "")),
                ("Date of Birth",  partner.get("dob", "")),
                ("Time of Birth",  partner.get("tob", "")),
                ("Place of Birth", p_pob),
            ]
            for label, value in p_detail_items:
                if not value:
                    continue
                self.set_y(p_details_y)
                self.set_x(label_x)
                self.set_font(self._font_family, "B", 9)
                self.set_text_color(*Colors.GOLD_LIGHT)
                self.cell(42, 7, f"{label}:", align="L")
                self.set_x(value_x)
                self.set_font(self._font_family, "", 9)
                self.set_text_color(*Colors.WHITE)
                self.cell(card_w - 56, 7, self._clean_text(str(value)), align="L")
                p_details_y += 9

            y += p_card_h + 5

        # ── Ruling Planets Card ──
        rp = self._ruling_planets_data
        if rp:
            rp_card_h = 32
            self.set_fill_color(16, 20, 42)
            self.set_draw_color(*Colors.PURPLE)
            self.set_line_width(0.4)
            self.rect(card_x, y, card_w, rp_card_h, style="DF")

            # RP header
            self.set_fill_color(*Colors.PURPLE)
            self.rect(card_x, y, card_w, 9, style="F")
            self.set_font(self._font_family, "B", 8)
            self.set_text_color(*Colors.WHITE)
            self.set_xy(card_x, y + 1.5)
            self.cell(card_w, 6, "Ruling Planets (KP)", align="C")

            # RP content (two columns)
            rp_y = y + 12
            rp_items = list(rp.items())
            col1_x = card_x + 6
            col2_x = card_x + card_w / 2 + 2
            for idx, (rp_key, rp_val) in enumerate(rp_items):
                rx = col1_x if idx < 3 else col2_x
                ry = rp_y + (idx % 3) * 6
                self.set_xy(rx, ry)
                self.set_font(self._font_family, "", 7.5)
                self.set_text_color(*Colors.GOLD_LIGHT)
                self.cell(32, 5, f"{rp_key}:", align="L")
                self.set_font(self._font_family, "B", 7.5)
                self.set_text_color(*Colors.WHITE)
                self.cell(30, 5, str(rp_val), align="L")

            y += rp_card_h + 3

        # ── Bottom Section ──
        # Report generation date
        self.set_y(ph - 42)
        self.set_font(self._font_family, "I", 8)
        self.set_text_color(*Colors.MID_GREY)
        gen_date = datetime.datetime.now().strftime("%d %B %Y, %H:%M IST")
        self.cell(0, 6, f"Report Generated: {gen_date}", align="C", new_x="LMARGIN", new_y="NEXT")

        # Ornamental rule with 6 diamonds
        orn_y = ph - 34
        self.set_draw_color(*Colors.GOLD)
        self.set_line_width(0.5)
        self.line(30, orn_y, cx - 22, orn_y)
        self.line(cx + 22, orn_y, pw - 30, orn_y)
        self.set_fill_color(*Colors.GOLD)
        for dx in [-16, -8, 0, 8, 16]:
            dcx = cx + dx
            sz = 1.8
            self.polygon([
                (dcx, orn_y - sz), (dcx + sz, orn_y),
                (dcx, orn_y + sz), (dcx - sz, orn_y),
            ], style="F")

        # Confidential stamp
        self.set_y(ph - 28)
        self.set_font(self._font_family, "B", 7)
        self.set_text_color(*Colors.GOLD_DIM)
        self.cell(0, 5, "Confidential  \u2014  For Personal Use Only", align="C")

        self._is_cover_page = False
        self.set_auto_page_break(auto=True, margin=22)

    # ─── Table of Contents ─────────────────────────────────────────────────
    def _render_table_of_contents(self):
        """Render TOC with chapter titles and dotted leaders."""
        if not self._chapter_list:
            return

        self.add_page()
        y = self.get_y() + 10
        self.set_y(y)

        # TOC Title
        self.set_font(self._font_family, "B", 18)
        self.set_text_color(*Colors.GOLD)
        self.cell(0, 12, "Table of Contents", align="C", new_x="LMARGIN", new_y="NEXT")

        # Gold underline
        self.set_draw_color(*Colors.GOLD)
        self.set_line_width(0.5)
        sep_y = self.get_y() + 2
        self.line(50, sep_y, self.w - 50, sep_y)
        self.set_y(sep_y + 8)

        # Chapter entries
        for idx, chapter_title in enumerate(self._chapter_list, 1):
            if self.get_y() > self.h - 25:
                self.add_page()

            color_idx = (idx - 1) % len(Colors.SECTION_COLORS)
            accent = Colors.SECTION_COLORS[color_idx]

            cy = self.get_y()
            # Number circle
            self.set_fill_color(*accent)
            ncx = 24
            ncy = cy + 3.5
            self.ellipse(ncx - 3.5, ncy - 3.5, 7, 7, style="F")
            self.set_font(self._font_family, "B", 7)
            self.set_text_color(*Colors.WHITE)
            self.set_xy(ncx - 3.5, ncy - 2.5)
            self.cell(7, 5, str(idx), align="C")

            # Chapter title
            self.set_xy(34, cy)
            self.set_font(self._font_family, "", 10)
            self.set_text_color(*Colors.DARK_GREY)
            title_str = self._clean_text(chapter_title[:70])
            title_w = self.get_string_width(title_str)
            self.cell(title_w + 2, 7, title_str, align="L")

            # Dotted leader
            dot_start_x = 36 + title_w + 4
            dot_end_x = self.w - 30
            if dot_start_x < dot_end_x:
                self.set_font(self._font_family, "", 8)
                self.set_text_color(*Colors.LIGHT_GREY)
                dots = " . " * int((dot_end_x - dot_start_x) / 6)
                self.set_xy(dot_start_x, cy)
                self.cell(dot_end_x - dot_start_x, 7, dots, align="L")

            self.set_y(cy + 10)

    # ─── Executive Summary (v5.0) ──────────────────────────────────────────
    def _render_executive_summary(self):
        """v5.0: One-page verdict overview grid — instant report snapshot."""
        if not self.report_text or not self._chapter_list:
            return

        self.add_page()
        y = self.get_y() + 6
        self.set_y(y)

        # Title
        self.set_font(self._font_family, "B", 16)
        self.set_text_color(*Colors.PRIMARY)
        self.cell(0, 10, "Executive Summary", align="C", new_x="LMARGIN", new_y="NEXT")

        # Subtitle
        self.set_font(self._font_family, "I", 9)
        self.set_text_color(*Colors.MUTED)
        self.cell(0, 6, "Quick overview of all chapters analyzed in this report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # Underline
        sep_y = self.get_y()
        self.set_draw_color(*Colors.PRIMARY)
        self.set_line_width(0.4)
        self.line(30, sep_y, self.w - 30, sep_y)
        self.ln(6)

        # Scan report text for verdict lines per chapter
        lines = self.report_text.split("\n")
        circle_nums = "\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468\u2469\u246a\u246b\u246c\u246d\u246e\u246f\u2470\u2471\u2472\u2473"
        current_chapter = ""
        chapter_idx = 0
        chapter_verdicts = []

        for line in lines:
            s = line.strip()
            if not s:
                continue
            # Detect chapter start
            for cn in circle_nums:
                if s.startswith(cn):
                    chapter_idx += 1
                    current_chapter = s[len(cn):].strip()
                    for ch_clean in "\u2502\u250c\u2514\u2510\u2518\u2504":
                        current_chapter = current_chapter.replace(ch_clean, "")
                    current_chapter = strip_markdown(current_chapter).strip()
                    break
            # Detect verdict
            sl = s.lower()
            if sl.startswith("verdict:") or "celestial verdict:" in sl:
                parts = s.split(":", 1)
                verdict_val = parts[1].strip() if len(parts) > 1 else s
                verdict_val = strip_markdown(verdict_val).strip()
                # Remove emoji markers
                for em in ["[OK]", "[X]", "[!]"]:
                    verdict_val = verdict_val.replace(em, "").strip()
                if current_chapter and verdict_val:
                    chapter_verdicts.append((chapter_idx, current_chapter, verdict_val))

        self._chapter_verdicts = chapter_verdicts

        if not chapter_verdicts:
            self.set_font(self._font_family, "I", 10)
            self.set_text_color(*Colors.MUTED)
            self.cell(0, 8, "No verdict data available for summary.", align="C")
            return

        # Render summary table
        headers = ["#", "Chapter", "Verdict"]
        col_widths = [12, 95, 63]
        x_start = 18

        # Header row
        self.set_fill_color(*Colors.PRIMARY)
        self.set_text_color(*Colors.WHITE)
        self.set_font(self._font_family, "B", 9)
        self.set_x(x_start)
        for j, h in enumerate(headers):
            self.cell(col_widths[j], SP_TABLE_HDR_H, h, border=0, align="L" if j > 0 else "C", fill=True)
        self.ln(SP_TABLE_HDR_H)

        # Data rows
        alternate = False
        seen_chapters = set()
        for idx, chap_name, verdict in chapter_verdicts:
            # Deduplicate — keep first verdict per chapter
            if chap_name in seen_chapters:
                continue
            seen_chapters.add(chap_name)

            if float(self.get_y()) > self.h - 18:
                self.add_page()

            fill_color = Colors.XLIGHT if alternate else Colors.WHITE
            self.set_fill_color(*fill_color)
            alternate = not alternate

            vu = verdict.upper()
            # Determine verdict color
            if any(w in vu for w in ["STRONG", "YES", "PROMISE", "PASS", "HIGH", "GOOD",
                                      "SUCCESS", "FAVORABLE", "CONFIRMED", "PROTECTED"]):
                v_color = Colors.GREEN_DARK
            elif any(w in vu for w in ["DENIED", "NO", "FAIL", "WEAK", "LOW",
                                        "CHALLENGING", "BLOCKED", "DANGER", "RISK"]):
                v_color = Colors.RED
            else:
                v_color = Colors.AMBER

            self.set_x(x_start)
            # Number
            self.set_font(self._font_family, "B", 9)
            self.set_text_color(*Colors.MUTED)
            self.cell(col_widths[0], SP_TABLE_ROW_H, str(idx), border=0, align="C", fill=True)
            # Chapter name
            self.set_font(self._font_family, "", 9)
            self.set_text_color(*Colors.BODY_TEXT)
            clean_name = self._clean_text(chap_name[:55]).title()
            self.cell(col_widths[1], SP_TABLE_ROW_H, clean_name, border=0, align="L", fill=True)
            # Verdict with color
            self.set_font(self._font_family, "B", 9)
            self.set_text_color(*v_color)
            self.cell(col_widths[2], SP_TABLE_ROW_H, self._clean_text(verdict[:35]), border=0, align="L", fill=True)

            # Row separator
            row_y = self.get_y() + SP_TABLE_ROW_H
            self.set_draw_color(*Colors.RULE)
            self.set_line_width(0.1)
            self.line(x_start, row_y, x_start + sum(col_widths), row_y)
            self.ln(SP_TABLE_ROW_H)

        # Bottom border
        self.set_draw_color(*Colors.PRIMARY)
        self.set_line_width(0.4)
        self.line(x_start, self.get_y(), x_start + sum(col_widths), self.get_y())
        self.ln(8)

        # Summary count
        pos = sum(1 for _, _, v in chapter_verdicts if any(
            w in v.upper() for w in ["STRONG", "YES", "PROMISE", "PASS", "GOOD", "SUCCESS", "FAVORABLE"]))
        neg = sum(1 for _, _, v in chapter_verdicts if any(
            w in v.upper() for w in ["DENIED", "NO", "FAIL", "WEAK", "BLOCKED", "DANGER"]))
        neu = len(seen_chapters) - pos - neg

        self.set_font(self._font_family, "", 9)
        self.set_text_color(*Colors.BODY_TEXT)
        summary = f"Positive: {pos}  |  Cautionary: {neg}  |  Neutral/Mixed: {neu}  |  Total Chapters: {len(seen_chapters)}"
        self.cell(0, 6, summary, align="C")
        self.ln(4)

    # ─── Markdown Rendering ─────────────────────────────────────────────────
    def _write_markdown_line(self, text: str, base_size: float = 10):
        """
        v4.0: Uses SP_LINE_H for consistent 1.45× line spacing.
        """
        parts = parse_markdown_parts(self._clean_text(text))
        for style, content in parts:
            if not content:
                continue
            self.set_font(self._font_family, style, base_size)
            self.write(SP_LINE_H, content)
        self.ln(SP_LINE_H)

    # ─── Chapter Header ─────────────────────────────────────────────────────
    def _render_chapter_header(self, chapter_num: int, title: str):
        """v4.0: Clean chapter header — left accent bar, Title Case, no bg fill."""
        if float(self.get_y()) > self.h - 35:
            self.add_page()

        self.ln(SP_SECTION_GAP)
        y = float(self.get_y())

        # Left accent bar (no background rectangle — removes clutter)
        self.set_fill_color(*Colors.PRIMARY)
        self.rect(18, y, 4, 16, style="F")

        # Chapter number badge
        badge_cx = 18 + 4 + 7.5
        badge_cy = y + 8
        self.set_fill_color(*Colors.PRIMARY)
        self.ellipse(badge_cx - 5, badge_cy - 5, 10, 10, style="F")
        self.set_font(self._font_family, "B", 7.5)
        self.set_text_color(*Colors.WHITE)
        self.set_xy(badge_cx - 5, badge_cy - 3.5)
        self.cell(10, 7, str(chapter_num), align="C")

        # Title — 14pt Bold, Title Case (not ALL CAPS)
        self.set_xy(badge_cx + 8, y + 2)
        self.set_font(self._font_family, "B", 14)
        self.set_text_color(*Colors.PRIMARY)
        clean_title = self._clean_text(strip_markdown(title)).title()
        self.cell(0, 12, clean_title, new_x="LMARGIN", new_y="NEXT")

        # Single underline (not double)
        y2 = self.get_y() + 1
        self.set_draw_color(*Colors.PRIMARY)
        self.set_line_width(0.5)
        self.line(18, y2, self.w - 18, y2)
        self.set_line_width(0.2)  # reset

        self.set_y(y2 + SP_BLOCK_GAP)
        self._current_chapter_idx = chapter_num
        self._current_section_name = strip_markdown(title).title()

    # ─── Section Sub-header ─────────────────────────────────────────────────
    def _render_section_header(self, title: str):
        if float(self.get_y()) > self.h - 25:
            self.add_page()

        y = self.get_y() + 3
        # Left 2pt rule instead of filled rect — lighter visual weight
        self.set_draw_color(*Colors.PRIMARY_MED)
        self.set_line_width(1.8)
        self.line(18, y, 18, y + 7)
        self.set_line_width(0.2)  # reset

        self.set_xy(23, y)
        self.set_font(self._font_family, "B", 10.5)
        self.set_text_color(*Colors.PRIMARY_MED)
        self.cell(0, 7, self._clean_text(strip_markdown(title)).title(), new_x="LMARGIN", new_y="NEXT")
        self.set_y(self.get_y() + 2)

    # ─── Key-Value ──────────────────────────────────────────────────────────
    def _render_key_value(self, key: str, value: str):
        self.set_x(20)
        self.set_font(self._font_family, "B", 9.5)
        self.set_text_color(*Colors.DARK_GREY)
        clean_key = self._clean_text(key)
        key_w = self.get_string_width(clean_key + ":  ") + 2
        self.cell(key_w, 5, f"{clean_key}:", align="L")
        self.set_font(self._font_family, "", 9.5)
        self.set_text_color(*Colors.BLACK)
        # FIX: strip remaining markdown from value
        clean_value = self._clean_text(strip_markdown(value))
        remaining_w = self.w - self.get_x() - self.r_margin - 5
        self.multi_cell(remaining_w, 5, clean_value, new_x="LMARGIN", new_y="NEXT")

    # ─── Verdict ────────────────────────────────────────────────────────────
    def _render_verdict(self, verdict_text: str):
        """v4.0: Clean 3-element verdict card — no drop shadow."""
        upper = verdict_text.upper()
        if any(w in upper for w in ["STRONG", "YES", "PROMISE", "PASS", "HIGH", "GOOD", "BENEFIC", "SUCCESS", "KARMA YOGA", "FAVORABLE", "FAVORABLE"]):
            status_color, bg_color = Colors.GREEN_DARK, Colors.SUCCESS_BG
        elif any(w in upper for w in ["DENIED", "NO ", "FAIL", "WEAK", "LOW", "MALEFIC", "CHALLENGING", "DO NOT", "UNCERTAIN"]):
            status_color, bg_color = Colors.RED, Colors.DANGER_BG
        else:
            status_color, bg_color = Colors.AMBER, Colors.WARN_BG

        y = float(self.get_y()) + 2
        if y > float(self.h) - 20.0:
            self.add_page()
            y = float(self.get_y()) + 2

        badge_x = 18
        badge_w = self.w - 36
        badge_h = 12

        # Badge body (no drop shadow)
        self.set_fill_color(*bg_color)
        self.set_draw_color(*status_color)
        self.set_line_width(0.3)
        self.rect(badge_x, y, badge_w, badge_h, style="DF")

        # Left status bar
        self.set_fill_color(*status_color)
        self.rect(badge_x, y, 4, badge_h, style="F")

        # "Verdict:" label
        self.set_xy(badge_x + 10, y + 2)
        self.set_font(self._font_family, "", 8)
        self.set_text_color(*Colors.MUTED)
        self.cell(20, 8, "Verdict:", align="L")

        # Verdict value
        self.set_font(self._font_family, "B", 10)
        self.set_text_color(*status_color)
        self.cell(0, 8, self._clean_text(strip_markdown(verdict_text)), align="L")
        self.set_y(y + badge_h + 3)

    # ─── Separator ──────────────────────────────────────────────────────────
    def _render_separator(self, style: str = "light"):
        """v4.0: Single hairline — no diamonds, no split lines."""
        y = float(self.get_y()) + 2
        self.set_line_width(0.2)
        if style in ("gold", "chapter_end"):
            self.set_draw_color(*Colors.ACCENT_DIM)
        else:
            self.set_draw_color(*Colors.RULE)
        self.line(18, y, self.w - 18, y)
        self.set_y(y + 3)

    # ─── Stat Highlight Card (v5.0) ──────────────────────────────────────────
    def _render_stat_highlight(self, label: str, value: str, color: tuple = None):
        """v5.0: Render a key metric as a compact colored highlight card."""
        if color is None:
            color = Colors.PRIMARY

        y = float(self.get_y()) + 1
        if y > float(self.h) - 18.0:
            self.add_page()
            y = float(self.get_y()) + 1

        card_x = 20
        card_w = self.w - 40
        card_h = 9

        # Determine bg color based on content
        vu = value.upper()
        if any(w in vu for w in ["0", "NONE", "NIL"]):
            bg = Colors.SUCCESS_BG
        elif any(w in vu for w in ["HIGH", "MAJOR", "DANGER", "TRAP"]):
            bg = Colors.DANGER_BG
            color = Colors.RED
        else:
            bg = Colors.WARN_BG
            color = Colors.AMBER

        self.set_fill_color(*bg)
        self.set_draw_color(*color)
        self.set_line_width(0.2)
        self.rect(card_x, y, card_w, card_h, style="DF")

        # Left accent bar
        self.set_fill_color(*color)
        self.rect(card_x, y, 3, card_h, style="F")

        # Label
        self.set_xy(card_x + 6, y + 1.5)
        self.set_font(self._font_family, "B", 9)
        self.set_text_color(*color)
        lbl_clean = self._clean_text(label)
        self.cell(50, 6, lbl_clean, align="L")

        # Value
        self.set_font(self._font_family, "B", 10)
        self.cell(0, 6, self._clean_text(value), align="R")
        self.set_xy(card_x, y + card_h + 1)
        self.set_y(y + card_h + 2)

    # ─── Report Complete Badge ───────────────────────────────────────────────
    def _render_report_complete(self, text: str):
        y = float(self.get_y()) + 5  # type: ignore
        if y > self.h - 30:  # type: ignore
            self.add_page()
            y = self.get_y() + 5

        badge_x = 25
        badge_w = self.w - 50
        badge_h = 14

        self.set_fill_color(230, 255, 240)
        self.set_draw_color(*Colors.GREEN_DARK)
        self.set_line_width(0.5)
        self.rect(badge_x, y, badge_w, badge_h, style="DF")
        self.set_xy(badge_x, y + 2)
        self.set_font(self._font_family, "B", 11)
        self.set_text_color(*Colors.GREEN_DARK)
        clean = strip_markdown(text)
        for ch in "\u2705\u274c\u2714\u2716\u2611\u2612":
            clean = clean.replace(ch, "")
        clean = clean.strip()
        self.cell(badge_w, 10, self._clean_text(clean), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_y(y + badge_h + 5)

    # ─── Main Content Parser ─────────────────────────────────────────────────
    def _render_report_body(self):
        """
        Parse report text and render with proper formatting.
        FIX: Markdown rendering, chapter colors, overflow guard.
        """
        if not self.report_text.strip():
            return

        lines = self.report_text.split("\n")
        chapter_num = 0

        # Circle numbers for chapter detection
        circle_nums = "\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468\u2469\u246a\u246b\u246c\u246d\u246e\u246f\u2470\u2471\u2472\u2473"

        skip_prefixes = [
            "Name:", "Date of Birth:", "Time of Birth:", "Place of Birth:",
            "Mode:", "Ruling Planets:", "Topics Analyzed:", "Generated:"
        ]

        i = 0
        l_lines = cast(List[str], lines)
        _in_event_section = False   # True when inside an Event Windows section
        _event_item_count = 0       # Count of event items rendered in current section
        _EVENT_WINDOW_CAP = 8       # Max event items to show per section
        while i < len(l_lines):
            raw_line = l_lines[i]  # type: ignore
            stripped  = cast(str, str(raw_line).strip())
            i += 1

            if not stripped:
                self.ln(SP_PARA_GAP)
                continue

            # ── Chapter start ──
            is_chapter = False
            for cn in circle_nums:
                if stripped.startswith(cn):
                    chapter_num += 1
                    s_stripped = cast(str, stripped)
                    title = "".join(s_stripped[j] for j in range(len(cn), len(s_stripped))).strip()
                    self._render_chapter_header(chapter_num, title)
                    is_chapter = True
                    break
            if is_chapter:
                continue

            # ── Skip cover metadata ──
            if chapter_num == 0:
                if any(stripped.startswith(p) for p in skip_prefixes):
                    continue
                if "DIYA DRISHTI" in stripped.upper() and (
                    "COMPLETE" in stripped.upper() or "REPORT" in stripped.upper()
                ):
                    continue

            # ── REPORT COMPLETE ──
            if "REPORT COMPLETE" in stripped.upper():
                self._render_report_complete(stripped)
                continue

            # ── Separator lines ──
            if len(stripped) >= 3 and all(c in " \u2500\u2501\u2550\u2554\u255a\u2557\u255d\u2551\u250c\u2514\u2510\u2518\u2502\u2504-_=" for c in stripped):
                if any(c in stripped for c in "\u2554\u255a\u2557\u255d\u2501\u2550"):
                    self._render_separator("gold")
                else:
                    self._render_separator("light")
                continue

            # ── Section keywords — detect Event Windows for cap ──
            section_kws = ["PROMISE ANALYSIS", "EVENT WINDOWS", "CONFIRMED EVENTS",
                           "SUMMARY", "CAUSE", "EFFECT", "CORE DHARMA", "KARMIC AXIS"]
            is_section = False
            for kw in section_kws:
                if kw in stripped.upper():
                    clean = stripped
                    for ch in "\u250c\u2514\u2510\u2518\u2502\u2500":
                        clean = clean.replace(ch, "")
                    clean = strip_markdown(clean).strip()
                    if clean:
                        self._render_section_header(clean)
                    # Track if entering event section
                    if "EVENT" in stripped.upper() or "WINDOW" in stripped.upper():
                        _in_event_section = True
                        _event_item_count = 0
                    else:
                        _in_event_section = False
                        _event_item_count = 0
                    is_section = True
                    break
            if is_section:
                continue

            # ── Event window cap: skip numbered items beyond cap ──
            if _in_event_section and re.match(r'^\s*\d+\.\s', stripped):
                _event_item_count += 1
                if _event_item_count > _EVENT_WINDOW_CAP:
                    # Emit the overflow note once, then skip the rest
                    if _event_item_count == _EVENT_WINDOW_CAP + 1:
                        # Count remaining items to report total skipped
                        remaining = sum(
                            1 for ln in l_lines[i:]
                            if re.match(r'^\s*\d+\.\s', ln.strip())
                        )
                        note = f"  ... and {remaining} more event windows not shown in this report."
                        self.set_x(20)
                        self.set_font(self._font_family, "I", 9)
                        self.set_text_color(*Colors.MID_GREY)
                        self.cell(0, 6, self._clean_text(note), new_x="LMARGIN", new_y="NEXT")
                        self.set_text_color(*Colors.BLACK)
                    continue  # Skip this item

            # ── Verdict ──
            if stripped.lower().startswith("verdict:"):
                s_stripped = cast(str, stripped)
                val = s_stripped.split(":", 1)[1].strip() if ":" in s_stripped else s_stripped
                self._render_verdict(val)
                continue

            # ── Key: Value pairs ──
            if ":" in stripped and not stripped.startswith(("\u27a4", "\u26a0", "\u2022", "-")):
                parts_kv = stripped.split(":", 1)
                raw_key  = parts_kv[0]
                raw_val  = parts_kv[1].strip() if len(parts_kv) > 1 else ""
                # Clean key
                for ch in "\u2502\u250c\u2514\u2510\u2518\u2504*":
                    raw_key = raw_key.replace(ch, "")
                raw_key = raw_key.strip()
                raw_key = self._clean_text(raw_key)
                if raw_key and len(raw_key) < 40 and raw_val:
                    # v5.0: Route critical metrics through stat highlight card
                    stat_keywords = {"TOTAL WINDOWS", "DEBT TRAP", "MAJOR DEBT",
                                     "TOTAL SCORE", "NET SCORE", "CONFIDENCE",
                                     "TOTAL EVENTS", "RISK SCORE", "NET EDUCATIONAL"}
                    if raw_key.upper() in stat_keywords or (
                            raw_val.strip().isdigit() and int(raw_val.strip()) > 5):
                        self._render_stat_highlight(raw_key, raw_val)
                    else:
                        self._render_key_value(raw_key, raw_val)
                    continue

            # ── ALL-CAPS sub-headings ──
            clean_line = stripped
            for ch in "\u2502\u250c\u2514\u2510\u2518\u2504":
                clean_line = clean_line.replace(ch, "")
            clean_line = strip_markdown(clean_line).strip()
            s_clean = cast(str, clean_line)
            if s_clean.isupper() and 3 < len(s_clean) < 70 and not any(c.isdigit() for c in "".join(s_clean[j] for j in range(min(len(s_clean), 3)))):
                # v5.0: Skip ALL-CAPS sub-headings that are just raw module branding
                if any(skip in s_clean for skip in ["TITANIUM ORACLE", "FORENSIC REMEDY"]):
                    continue
                if float(self.get_y()) > self.h - 20:
                    self.add_page()
                color_idx = max(0, (self._current_chapter_idx - 1) % len(Colors.SECTION_COLORS))
                self.set_x(18)
                self.set_font(self._font_family, "B", 10)
                self.set_text_color(*Colors.SECTION_COLORS[color_idx])
                # v5: Render as Title Case instead of ALL CAPS
                self.multi_cell(0, 5, self._clean_text(clean_line).title(), new_x="LMARGIN", new_y="NEXT")
                self.set_text_color(*Colors.BLACK)
                continue

            # ── Bullet lines ──
            if stripped.startswith(("\u27a4", "\u2022", "- ", "\u26a0")):
                bullet_text = str(stripped)
                for pfx in ["\u27a4 ", "\u2022 ", "- ", "\u26a0\ufe0f ", "\u26a0 "]:
                    if bullet_text.startswith(pfx):  # type: ignore
                        new_bullet = ""
                        for j in range(len(pfx), len(bullet_text)):
                            new_bullet += bullet_text[j]  # type: ignore
                        bullet_text = new_bullet
                        break
                if float(self.get_y()) > self.h - 15:
                    self.add_page()
                self.set_x(22)
                self.set_font(self._font_family, "", 9)
                self.set_text_color(*Colors.PRIMARY_MED)
                self.cell(5, SP_LINE_H, "\u2013")  # en-dash, more elegant than bullet
                self.set_text_color(*Colors.BODY_TEXT)
                self._write_markdown_line(bullet_text, base_size=9.5)
                continue

            # ── Normal text ──
            display = stripped
            for ch in "\u2502\u250c\u2514\u2510\u2518\u2504\u25c8":
                display = display.replace(ch, "")
            display = display.strip()

            # v5.0: Suppress repeated wisdom quotes after the first 2
            if display and display.startswith('"') and ('\u2014' in display or ' \u2014 ' in display):
                self._quote_count += 1
                if self._quote_count > 2:
                    continue  # Skip this quote
                # Render first 2 as styled italic blockquotes
                if float(self.get_y()) > self.h - 15:
                    self.add_page()
                self.set_x(28)
                self.set_font(self._font_family, "I", 9)
                self.set_text_color(*Colors.MUTED)
                self.multi_cell(self.w - 56, SP_LINE_H, self._clean_text(display), new_x="LMARGIN", new_y="NEXT")
                self.set_text_color(*Colors.BODY_TEXT)
                self.ln(2)
                continue

            if display:
                if float(self.get_y()) > self.h - 18:
                    self.add_page()
                # v4.0: plain body text, no per-line accent bar
                self.set_x(20)
                self.set_font(self._font_family, "", 10)
                self.set_text_color(*Colors.BODY_TEXT)
                self._write_markdown_line(display, base_size=10)

        self.ln(3)

    # ─── Signature — FIX: same page, not blank page ─────────────────────────
    def _render_signature(self):
        """
        FIX: Signature is placed on the LAST CONTENT page,
        not a separate blank page. Only creates new page if
        truly no space.
        """
        sign_path = get_resource_path(os.path.join("assets", "Sign.png"))
        if not os.path.exists(sign_path):
            return

        needed = 38
        if float(self.get_y()) > self.h - needed:
            self.add_page()

        # Gap
        self.ln(8)

        # Gold separator
        sep_y = self.get_y()
        self.set_draw_color(*Colors.GOLD)
        self.set_line_width(0.5)
        self.line(50, sep_y, self.w - 50, sep_y)
        self.ln(4)

        # Thanks text — centered
        self.set_font(self._font_family, "B", 10)
        self.set_text_color(*Colors.DARK_GREY)
        self.cell(0, 5, "Thanks & Regards", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # Signature image — centered
        sign_w = 25
        sign_x = (self.w - sign_w) / 2
        y_pos  = self.get_y()
        self.image(sign_path, x=sign_x, y=y_pos, w=sign_w)

        # Date
        self.set_y(y_pos + 13)
        self.set_font(self._font_family, "I", 8)
        self.set_text_color(*Colors.MID_GREY)
        gen_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        self.cell(0, 5, gen_date, align="C")

    # ─── Table Helper ────────────────────────────────────────────────────────
    def _render_table(self, title, headers, rows, col_widths=None, accent_color=None):
        """v4.0: Unified table style — section-style header, XLIGHT zebra, no NAVY dark bar."""
        if accent_color is None:
            accent_color = Colors.PRIMARY

        if float(self.get_y()) > self.h - 30:
            self.add_page()

        # Section-style title (left border + text, no dark NAVY block)
        y = self.get_y() + 4
        self.set_draw_color(*Colors.PRIMARY)
        self.set_line_width(2.0)
        self.line(18, y, 18, y + 8)
        self.set_line_width(0.2)  # reset
        self.set_xy(24, y)
        self.set_font(self._font_family, "B", 10.5)
        self.set_text_color(*Colors.PRIMARY)
        self.cell(0, 8, self._clean_text(title).title(), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        usable_w = self.w - 36
        if not col_widths:
            col_widths = [usable_w / len(headers)] * len(headers)

        x_start = 18

        # Header row — PRIMARY bg, white text, Title Case
        self.set_fill_color(*Colors.PRIMARY)
        self.set_text_color(*Colors.WHITE)
        self.set_font(self._font_family, "B", 9)
        self.set_x(x_start)
        for j, h in enumerate(cast(List[Any], headers)):
            self.cell(col_widths[j], SP_TABLE_HDR_H, self._clean_text(str(h)).title(), border=0, align="L", fill=True)
        self.ln(SP_TABLE_HDR_H)

        # Data rows — v5: XLIGHT zebra, BODY_TEXT, 9pt, left accent
        self.set_font(self._font_family, "", 9)
        alternate = False
        for row in rows:
            if float(self.get_y()) > float(self.h) - 18.0:
                self.add_page()
                # Re-draw header on overflow
                self.set_fill_color(*Colors.PRIMARY)
                self.set_text_color(*Colors.WHITE)
                self.set_font(self._font_family, "B", 9)
                self.set_x(x_start)
                for j, h in enumerate(cast(List[Any], headers)):
                    self.cell(col_widths[j], SP_TABLE_HDR_H, self._clean_text(str(h)).title(), border=0, align="L", fill=True)
                self.ln(SP_TABLE_HDR_H)
                self.set_font(self._font_family, "", 9)

            fill_color = Colors.XLIGHT if alternate else Colors.WHITE
            self.set_fill_color(*fill_color)
            alternate = not alternate
            self.set_text_color(*Colors.BODY_TEXT)
            self.set_x(x_start)
            for j, cell_val in enumerate(cast(List[Any], row)):
                val = str(cell_val) if cell_val else "-"
                num_align = getattr(row, '_col_aligns', None)
                a = (num_align[j] if num_align else "L")
                # Bold first column (label column)
                if j == 0:
                    self.set_font(self._font_family, "B", 9)
                else:
                    self.set_font(self._font_family, "", 9)
                self.cell(col_widths[j], SP_TABLE_ROW_H, self._clean_text(val), border=0, align=a, fill=True)
            row_y = self.get_y() + SP_TABLE_ROW_H
            self.set_draw_color(*Colors.RULE)
            self.set_line_width(0.1)
            self.line(x_start, row_y, x_start + sum(col_widths), row_y)
            self.ln(SP_TABLE_ROW_H)

        # Bottom border
        self.set_draw_color(*Colors.PRIMARY)
        self.set_line_width(0.4)
        self.line(x_start, self.get_y(), x_start + sum(col_widths), self.get_y())
        self.ln(6)

    # ─── Chart Image ─────────────────────────────────────────────────────────
    def _render_chart_image(self):
        if not self._chart_image_path or not os.path.exists(self._chart_image_path):
            return

        self.add_page()
        y = self.get_y() + 2

        self.set_fill_color(*Colors.PRIMARY)
        self.rect(15, y, 3, 9, style="F")
        self.set_xy(21, y)
        self.set_font(self._font_family, "B", 11)
        self.set_text_color(*Colors.PRIMARY)
        self.cell(0, 9, "Birth Chart (Kundli)", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        try:
            from PIL import Image as PILImage  # type: ignore
            pil_img    = PILImage.open(self._chart_image_path)
            iw, ih     = pil_img.size
            aspect     = ih / iw if iw > 0 else 0.75
            img_w      = self.w - 50
            img_h      = img_w * aspect
            avail_h    = float(self.h) - float(self.get_y()) - 35.0  # type: ignore
            if img_h > min(avail_h, 140):
                img_h = min(avail_h, 140)
                img_w = img_h / aspect
            img_x = (self.w - img_w) / 2
            img_y = self.get_y()
            self.set_draw_color(*Colors.GOLD_DIM)
            self.set_line_width(0.4)
            self.rect(img_x - 1, img_y - 1, img_w + 2, img_h + 2)
            self.image(self._chart_image_path, x=img_x, y=img_y, w=img_w, h=img_h)
            self.set_y(img_y + img_h + 5)
        except Exception as e:
            self.set_font(self._font_family, "I", 9)
            self.set_text_color(*Colors.MID_GREY)
            self.cell(0, 6, f"(Chart image unavailable: {e})", new_x="LMARGIN", new_y="NEXT")

    # ─── Ruling Planets (Enhanced v3.0) ──────────────────────────────────────
    def _render_ruling_planets(self):
        """
        Enhanced RP section with computed data + external text.
        """
        meta = self.chart_data.get("metadata", {})
        rp_text = meta.get("ruling_planets", "")
        if not rp_text and self._ruling_planets_text:
            rp_text = self._ruling_planets_text

        rp = self._ruling_planets_data

        if not rp and not rp_text:
            return

        if self.get_y() > self.h - 50:
            self.add_page()

        y = self.get_y() + 3
        self.set_draw_color(*Colors.PRIMARY_MED)
        self.set_line_width(1.8)
        self.line(15, y, 15, y + 9)
        self.set_line_width(0.2)  # reset
        self.set_xy(21, y)
        self.set_font(self._font_family, "B", 11)
        self.set_text_color(*Colors.PRIMARY_MED)
        self.cell(0, 11, "Ruling Planets (KP)", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # Computed RP table
        if rp:
            headers = ["Component", "Ruling Planet"]
            rows = [[k, v] for k, v in rp.items() if v]
            col_widths = [60, 60]
            x_start = 35

            # Header
            self.set_fill_color(*Colors.PRIMARY)
            self.set_text_color(*Colors.WHITE)
            self.set_font(self._font_family, "B", 9)
            self.set_x(x_start)
            for j, h in enumerate(headers):
                self.cell(col_widths[j], 8, h, border=0, align="C", fill=True)
            self.ln(8)

            # Rows
            self.set_font(self._font_family, "", 9)
            alt = False
            for row in rows:
                fill_c = Colors.PRIMARY_LIGHT if alt else Colors.WHITE
                self.set_fill_color(*fill_c)
                alt = not alt
                self.set_text_color(*Colors.BODY_TEXT)
                self.set_x(x_start)
                for j, val in enumerate(row):
                    self.cell(col_widths[j], 6.5, self._clean_text(str(val)), border=0, align="C", fill=True)
                self.ln(6.5)

            self.set_draw_color(*Colors.PURPLE)
            self.set_line_width(0.3)
            self.line(x_start, self.get_y(), x_start + sum(col_widths), self.get_y())
            self.ln(4)

        # External RP text if any
        if rp_text:
            self.set_x(20)
            self.set_font(self._font_family, "", 10)
            self.set_text_color(*Colors.BLACK)
            self.multi_cell(0, 6, str(rp_text), new_x="LMARGIN", new_y="NEXT")
            self.ln(4)

    # ─── Data Tables ─────────────────────────────────────────────────────────
    def _render_planetary_positions_table(self):
        positions = self.chart_data.get("planetary_positions", [])
        if not positions:
            return
        headers    = ["Planet", "Degree", "Sign", "Nakshatra", "Star Lord", "Sub Lord"]
        col_widths = [22, 28, 25, 35, 30, 30]
        # Col aligns: Planet=L, Degree=R, rest=L
        aligns = ["L", "R", "L", "L", "L", "L"]
        rows = []
        for p in positions:
            row = _AlignedRow([
                p.get("planet", ""),
                p.get("longitude_dms", ""),
                p.get("sign", ""),
                p.get("nakshatra", ""),
                p.get("star_lord", ""),
                p.get("sub_lord", ""),
            ], aligns)
            rows.append(row)
        self._render_table("Planetary Positions", headers, rows, col_widths, Colors.SECTION)

    def _render_house_cusps_table(self):
        cusps = self.chart_data.get("house_cusps", [])
        if not cusps:
            return
        headers    = ["Cusp", "Degree", "Sign", "Sign Lord", "Star Lord", "Sub Lord"]
        col_widths = [18, 28, 25, 28, 30, 30]
        aligns = ["C", "R", "L", "L", "L", "L"]
        rows = []
        for c_raw in cusps:
            from typing import Any, Dict, cast  # type: ignore
            c = cast(Dict[str, Any], c_raw)
            row = _AlignedRow([
                f"H{c.get('cusp', '')}",
                c.get("longitude_dms", ""),
                c.get("sign", ""),
                c.get("sign_lord", ""),
                c.get("star_lord", ""),
                c.get("sub_lord", ""),
            ], aligns)
            rows.append(row)
        self._render_table("House Cusps", headers, rows, col_widths, Colors.SECTION)

    def _render_house_significators_table(self):
        sigs = self.chart_data.get("house_significators", [])
        if not sigs:
            return
        headers    = ["House", "L1 (Occupant)", "L2 (Owner)", "L3 (Star Lord)", "L4 (Sub Lord)"]
        col_widths = [18, 42, 35, 40, 35]
        aligns = ["C", "L", "L", "L", "L"]
        rows = []
        for s in sigs:
            row = _AlignedRow([
                s.get("house", ""),
                s.get("L1", "-"),
                s.get("L2", "-"),
                s.get("L3", "-"),
                s.get("L4", "-"),
            ], aligns)
            rows.append(row)
        self._render_table("House Significators", headers, rows, col_widths, Colors.SECTION)

    def _render_planet_significators_table(self):
        sigs = self.chart_data.get("planet_significators", [])
        if not sigs:
            return
        headers    = ["Planet", "Source Row (Houses Signified)"]
        col_widths = [35, 135]
        aligns = ["L", "L"]
        rows = []
        for s_raw in sigs:
            from typing import Any, Dict, cast  # type: ignore
            s = cast(Dict[str, Any], s_raw)
            row = _AlignedRow([
                s.get("planet", ""),
                s.get("Source_Row", "-"),
            ], aligns)
            rows.append(row)
        self._render_table("Planet Significators (Source Row)", headers, rows, col_widths, Colors.SECTION)

    def _render_dasa_table(self):
        dasa_data = self.chart_data.get("vimshottari_dasa_full", [])
        if not dasa_data:
            return
        headers    = ["#", "Maha Dasa Lord", "Start Date", "End Date", "Duration"]
        col_widths = [12, 40, 40, 40, 38]
        aligns = ["C", "L", "C", "C", "R"]
        rows = []
        for idx, md in enumerate(dasa_data, 1):
            row = _AlignedRow([
                str(idx),
                md.get("lord", ""),
                md.get("start", ""),
                md.get("end", ""),
                str(md.get("duration", "")),
            ], aligns)
            rows.append(row)
        self._render_table("KP Vimshottari Dasa (Maha Dasa)", headers, rows, col_widths, Colors.SECTION)

    # ─── Decorative Divider ──────────────────────────────────────────────────
    def _render_decorative_divider(self):
        """v4.0: Clean double-line divider — PRIMARY + RULE hairlines, no diamonds."""
        if self.get_y() > self.h - 30:
            self.add_page()

        self.ln(8)
        y = self.get_y()

        self.set_draw_color(*Colors.PRIMARY)
        self.set_line_width(0.5)
        self.line(18, y, self.w - 18, y)

        self.set_draw_color(*Colors.RULE)
        self.set_line_width(0.2)
        self.line(18, y + 2.5, self.w - 18, y + 2.5)

        self.set_y(y + 10)

    # ─── Professional Disclaimer ─────────────────────────────────────────────
    def _render_disclaimer(self):
        """Standard astrological consulting disclaimer."""
        if self.get_y() > self.h - 60:
            self.add_page()

        self.ln(6)
        y = self.get_y()

        # Header
        self.set_fill_color(*Colors.NAVY)
        self.rect(15, y, self.w - 30, 10, style="F")
        self.set_fill_color(*Colors.GOLD_DIM)
        self.rect(15, y, 3, 10, style="F")
        self.set_xy(20, y + 1.5)
        self.set_font(self._font_family, "B", 9)
        self.set_text_color(*Colors.GOLD_LIGHT)
        self.cell(0, 7, "Disclaimer & Terms of Use", align="L")
        self.set_y(y + 14)

        disclaimer_text = (
            "This report is generated using the Krishnamurti Paddhati (KP) system of Vedic Astrology "
            "and is intended for educational and personal guidance purposes only. The predictions, analyses, "
            "and interpretations contained herein are based on astrological calculations and should not be "
            "construed as professional advice in legal, medical, financial, or any other domain.\n\n"
            "The accuracy of this report depends entirely on the correctness of the birth data provided "
            "(date, time, and place of birth). Even minor errors in input data can significantly alter results.\n\n"
            "The author and software developer(s) accept no liability for decisions made based on this report. "
            "Users are advised to exercise independent judgment and consult qualified professionals for specific needs.\n\n"
            "This report is confidential and is prepared exclusively for the individual named on the cover page. "
            "Unauthorized distribution, reproduction, or commercial use is strictly prohibited.\n\n"
            "Software: Divya Drishti KP Astrology Suite | Engine: Titanium AI v4.0"
        )

        self.set_font(self._font_family, "", 8)
        self.set_text_color(*Colors.MID_GREY)
        self.set_x(18)
        self.multi_cell(self.w - 36, 4.5, disclaimer_text, new_x="LMARGIN", new_y="NEXT")

        # Copyright line
        self.ln(3)
        self.set_font(self._font_family, "I", 7)
        self.set_text_color(*Colors.LIGHT_GREY)
        year = datetime.datetime.now().year
        self.cell(0, 5, f"Copyright {year} Divya Drishti. All rights reserved.", align="C")

    # ─── Company Logo (Small, Inline — between Signature & Disclaimer) ────
    def _render_company_logo(self):
        """
        Render the company logo (COLOGO.png) as a small centered image
        between the signature and the disclaimer section.
        """
        cologo_path = get_resource_path(os.path.join("assets", "COLOGO.png"))
        if not os.path.exists(cologo_path):
            return

        # Need space for logo (~40mm) + text below (~12mm)
        needed = 55
        if float(self.get_y()) > self.h - needed:
            self.add_page()

        self.ln(6)
        pw = self.w

        try:
            from PIL import Image as PILImage  # type: ignore
            pil_img = PILImage.open(cologo_path)
            iw, ih = pil_img.size
            aspect = ih / iw if iw > 0 else 1.5

            # Small logo — max 35mm wide
            img_w = min(35, pw - 80)
            img_h = img_w * aspect
            if img_h > 30:
                img_h = 30
                img_w = img_h / aspect

            img_x = (pw - img_w) / 2
            img_y = self.get_y()

            self.image(cologo_path, x=img_x, y=img_y, w=img_w, h=img_h)

            # Branding text below logo
            self.set_y(img_y + img_h + 2)
            self.set_font(self._font_family, "B", 8)
            self.set_text_color(*Colors.GOLD_DIM)
            self.cell(0, 5, "D I V Y A   D R I S H T I", align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_font(self._font_family, "I", 7)
            self.set_text_color(*Colors.MID_GREY)
            self.cell(0, 4, "KP Astrology Professional Suite", align="C", new_x="LMARGIN", new_y="NEXT")

        except Exception:
            # Fallback: just text branding
            self.set_font(self._font_family, "B", 10)
            self.set_text_color(*Colors.GOLD_DIM)
            self.cell(0, 6, "DIVYA DRISHTI", align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_font(self._font_family, "I", 8)
            self.set_text_color(*Colors.MID_GREY)
            self.cell(0, 5, "KP Astrology Professional Suite", align="C", new_x="LMARGIN", new_y="NEXT")

    # ─── Remedy Protocol ─────────────────────────────────────────────────────
    def _render_remedy_protocol(self):
        """Render consolidated forensic remedy protocol at the end of the report."""
        if not self._structured_remedies:
            return

        self.add_page()
        
        # Header
        self._current_chapter_idx += 1
        self._render_chapter_header(self._current_chapter_idx, "Forensic Remedy Protocol")

        self.ln(2)

        # Why follow this?
        self._render_section_header("Why follow these remedies?")
        self.set_x(20)
        self.set_font(self._font_family, "", 9.5)
        self.set_text_color(*Colors.DARK_GREY)
        text_why = (
            "Astrological remedies do not rewrite fate, but they act as a lightning rod to ground negative "
            "energies and amplify positive planetary alignments. The remedies prescribed below are mathematically "
            "calculated and forensically tailored to your specific active Mahadasha (MD) and Antardasha (AD)."
        )
        self.multi_cell(0, 5, text_why, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # When to perform?
        self._render_section_header("When to perform them?")
        self.set_x(20)
        self.set_font(self._font_family, "", 9.5)
        self.set_text_color(*Colors.DARK_GREY)
        text_when = (
            "Perform the specific remedy ONLY during the active Dasha window mentioned. "
            "Remedies are most effective when started on the day of the week ruled by the priority planet. "
            "If no specific dasha is mentioned, these act as general lifecycle remedies."
        )
        self.multi_cell(0, 5, text_when, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # Expected After-Effects
        self._render_section_header("Expected After-Effects")
        self.set_x(20)
        self.set_font(self._font_family, "", 9.5)
        self.set_text_color(*Colors.DARK_GREY)
        text_effects = (
            "When followed properly with discipline, these protocols help reduce sudden obstacles, "
            "bring clarity in decision-making, and ensure a smoother execution of events in your life. "
            "They balance the karmic axis required for the event's success."
        )
        self.multi_cell(0, 5, text_effects, new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

        # Specific Remedies
        self._render_separator("gold")
        self.ln(4)
        
        seen = set()
        for rem_data in self._structured_remedies:
            topic = rem_data["topic"]
            dasha = rem_data.get("dasha", "")
            rem = rem_data["remedy"]
            
            key = f"{topic}_{dasha}"
            if key in seen:
                continue
            seen.add(key)
            
            if float(self.get_y()) > self.h - 35:
                self.add_page()
                
            # Topic Header
            self.set_x(18)
            self.set_font(self._font_family, "B", 10.5)
            self.set_text_color(*Colors.SECTION)
            title = f"{topic.upper()}"
            if dasha:
                title += f" (Active Dasha: {dasha})"
            self.cell(0, 6, self._clean_text(title), new_x="LMARGIN", new_y="NEXT")
            
            # Formatter helper
            def _write_bullet(label: str, content: str, color: tuple):
                if not content: return
                self.set_x(22)
                self.set_font(self._font_family, "B", 9)
                self.set_text_color(*color)
                self.cell(25, 5, label + ":")
                self.set_font(self._font_family, "", 9.5)
                self.set_text_color(*Colors.BLACK)
                self.multi_cell(0, 5, self._clean_text(content), new_x="LMARGIN", new_y="NEXT")

            # Event Style
            if "karmic" in rem and isinstance(rem["karmic"], list):
                for k in rem["karmic"]:
                    _write_bullet("Karmic", k, Colors.NAVY)
            if "lal_kitab" in rem and isinstance(rem["lal_kitab"], list):
                for l in rem["lal_kitab"]:
                    _write_bullet("Lal Kitab", l, Colors.GREEN_DARK)
            if "gemstone" in rem and isinstance(rem["gemstone"], dict):
                gem = rem["gemstone"]
                if gem.get("allowed") and gem.get("stone"):
                    _write_bullet("Gemstone", f"{gem['stone']} ({gem.get('weight', '?')}ct)", Colors.PURPLE)
            
            # General Style
            if "Karmic" in rem and isinstance(rem["Karmic"], str):
                _write_bullet("Karmic", rem["Karmic"], Colors.NAVY)
            if "LalKitab" in rem and isinstance(rem["LalKitab"], str):
                _write_bullet("Lal Kitab", rem["LalKitab"], Colors.GREEN_DARK)
            if "Mantra_Chanting" in rem and isinstance(rem["Mantra_Chanting"], str):
                _write_bullet("Mantra", rem["Mantra_Chanting"], Colors.AMBER)
                
            self.ln(3)

        self._render_separator("light")
        self.ln(4)

    # ─── Main Generate ───────────────────────────────────────────────────────
    def generate(self, save_path, chart_image_path=None, ruling_planets_text=None):
        """
        Generate premium PDF report (International Professional Edition v3.0).
        Args:
            save_path: Where to save the PDF.
            chart_image_path: Optional kundli chart image path.
            ruling_planets_text: Optional ruling planets string.
        """
        self._chart_image_path    = chart_image_path
        self._ruling_planets_text = ruling_planets_text

        # Phase 1: Cover & Navigation
        self._render_cover_page()
        self._prescan_chapters()
        self._render_table_of_contents()
        self._render_executive_summary()  # v5.0: verdict overview after TOC

        # Phase 2: Chart Data
        self._render_chart_image()
        self._render_ruling_planets()
        self._render_planetary_positions_table()
        self._render_house_cusps_table()
        self._render_house_significators_table()
        self._render_planet_significators_table()
        self._render_dasa_table()

        # Phase 3: Analysis Content
        self._render_decorative_divider()
        self._render_report_body()

        # Phase 3.5: Remedies
        self._render_remedy_protocol()

        # Phase 4: Closing
        self._render_signature()
        self._render_company_logo()
        self._render_disclaimer()

        self.output(save_path)

