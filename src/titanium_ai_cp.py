"""
═══════════════════════════════════════════════════════════════════════════════
TITENIUM AI — COUPLE MATCHMAKING  (UAKP Method)  v2.0
═══════════════════════════════════════════════════════════════════════════════

PHILOSOPHY
──────────
This is NOT traditional guna milan.
This is UAKP source-result chain analysis.

Matchmaking is about:  Source → Interaction → Result → Event Trigger

If that chain is unstable the relationship collapses, no matter how
"romantic" it looks on paper.

APPROACH
────────
1. Identify relationship houses  (2, 5, 7, 8, 11)
2. Cross-match Source & Result rows between partners
3. Detect destructive house overlays  (6→7, 8→2, 12→7 …)
4. Analyze event-activation timing   (MD-AD-PD)
5. Classify verdict:
      Sustainable Marriage | Attraction Only | Karmic Trap |
      Karmic Soulmate | Destructive Union | Timing Mismatch |
      Challenging but Viable | Insufficient Data

NEW in v2.0
───────────
6. POST-MARRIAGE DASHA ANALYSIS (if verdict == SUSTAINABLE_MARRIAGE
   or KARMIC_SOULMATE):
      • Year-by-year MD-AD scan for BOTH bride & groom
      • Detects harmony windows, conflict peaks, separation risk,
        child-birth windows, financial stress, renewal periods
      • Dual-chart overlay: when BOTH charts fire 6/8/12 simultaneously
        → "Danger Zone"; when BOTH fire 2/5/7/11 → "Golden Phase"
      • Narrative guidance per phase

NO SUGAR-COATING.  This is outcome prediction, not fairy tales.

Author   : Divya Drishti Development Team
Copyright: Protected under Divya Drishti software copyright
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json
import copy

# =============================================================================
# LANGUAGE SYSTEM (Tri-Language Support)
# =============================================================================
class LanguageSystem:
    _dict = {
        "EXECUTIVE SUMMARY": {"hi": "कार्यकारी सारांश", "bn": "নির্বাহী সারাংশ"},
        "VERDICT": {"hi": "निर्णय", "bn": "রায়"},
        "Sustainable Marriage": {"hi": "स्थायी विवाह", "bn": "টেকসই বিবাহ"},
        "Attraction Only (No Longevity)": {"hi": "केवल आकर्षण (कोई दीर्घायु नहीं)", "bn": "শুধুমাত্র আকর্ষণ (কোন দীর্ঘায়ু নেই)"},
        "Karmic Trap (Intense but Painful)": {"hi": "कार्मिक जाल (तीव्र लेकिन दर्दनाक)", "bn": "কর্মিক ফাঁদ (তীব্র তবে বেদনাদায়ক)"},
        "Karmic Soulmate (Intense & Supportive)": {"hi": "कार्मिक जीवनसाथी", "bn": "কর্মিক সোলমেট"},
        "Destructive Union (High Risk)": {"hi": "विनाशकारी संघ (उच्च जोखिम)", "bn": "ধ্বংসাত্মক মিলন (উচ্চ ঝুঁকি)"},
        "Timing Mismatch (Wrong Life Phase)": {"hi": "समय का बेमेल", "bn": "সময়ের অমিল"},
        "Challenging but Viable (Requires Effort)": {"hi": "चुनौतीपूर्ण लेकिन व्यवहार्य", "bn": "চ্যালেঞ্জিং কিন্তু কার্যকর"},
        "Insufficient Data": {"hi": "अपर्याप्त डेटा", "bn": "অপর্যাপ্ত ডেটা"},
        "Bidirectional Stability": {"hi": "द्विदिश स्थिरता", "bn": "দ্বিমুখী স্থিতিশীলতা"},
        "STABLE": {"hi": "स्थिर", "bn": "স্থিতিশীল"},
        "MODERATE": {"hi": "मध्यम", "bn": "মাঝারি"},
        "UNSTABLE": {"hi": "अस्थिर", "bn": "অস্থিতিশীল"},
        "SOURCE-RESULT CROSS-MATCHING": {"hi": "स्रोत-परिणाम क्रॉस-मैचिंग", "bn": "উৎস-ফলাফল ক্রস-ম্যাচিং"},
        "Direction": {"hi": "दिशा", "bn": "দিক"},
        "Quality": {"hi": "गुणवत्ता", "bn": "গুণমান"},
        "Score": {"hi": "स्कोर", "bn": "স্কোর"},
        "MULTI-LAYER COMPATIBILITY": {"hi": "बहु-स्तरीय संगतता", "bn": "মাল্টি-লেয়ার সামঞ্জस्य"},
        "PHYSICAL": {"hi": "शारीरिक", "bn": "শারীরিক"},
        "EMOTIONAL": {"hi": "भावनात्मक", "bn": "মানসিক"},
        "KARMIC": {"hi": "कार्मिक", "bn": "কর্মিক"},
        "DESTRUCTIVE OVERLAYS": {"hi": "विनाशकारी ओवरले", "bn": "ধ্বংসাত্মক ওভারলে"},
        "None detected.": {"hi": "कोई पता नहीं चला।", "bn": "কিছুই সনাক্ত হয়নি।"},
        "DASHA TIMING": {"hi": "दशा समय", "bn": "দশা সময়"},
        "Marriage prob": {"hi": "विवाह की संभावना", "bn": "বিবাহের সম্ভাবনা"},
        "Breakup risk": {"hi": "ब्रेकअप का जोखिम", "bn": "ব্রেকআপের ঝুঁকি"},
        "BRUTAL TRUTH": {"hi": "कड़वा सच", "bn": "নিষ্ঠুর সত্য"},
        "STRENGTHS": {"hi": "ताकत", "bn": "শক্তি"},
        "WEAKNESSES": {"hi": "कमजोरियां", "bn": "দুর্বলতা"},
        "DEAL-BREAKERS": {"hi": "समझौता-तोड़ने वाले", "bn": "চুক্তি-ভঙ্গকারী"},
        "None.": {"hi": "कोई नहीं।", "bn": "কোনটিই নয়।"},
        "POST-MARRIAGE DASHA TIMELINE": {"hi": "विवाह के बाद की दशा टाइमलाइन", "bn": "বিবাহ-পরবর্তী দশা টাইমলাইন"},
        "for_marriage": {"hi": "विवाह के लिए", "bn": "বিবাহের लिए"}
    }

    @staticmethod
    def get(text: str, lang: str = "en", **kwargs) -> str:
        if lang == "en" or text not in LanguageSystem._dict:
            res = text
        else:
            res = LanguageSystem._dict[text].get(lang, text)
        for k, v in kwargs.items():
            res = res.replace(f"{{{k}}}", str(v))
        return res

def t(text: str, lang: str = "en", **kwargs) -> str:
    return LanguageSystem.get(text, lang, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS — house semantics used across the engine
# ═══════════════════════════════════════════════════════════════════════════════

HOUSE_MEANINGS: Dict[int, str] = {
    1:  "Self / Identity",
    2:  "Family / Wealth",
    3:  "Communication / Siblings",
    4:  "Home / Peace",
    5:  "Romance / Children",
    6:  "Conflict / Health / Enemies",
    7:  "Marriage / Partnership",
    8:  "Transformation / Longevity",
    9:  "Dharma / Fortune",
    10: "Career / Status",
    11: "Desires / Gains / Fulfilment",
    12: "Loss / Separation / Spirituality",
}

# "12th from X destroys X" rule
DESTRUCTION_MAP: Dict[int, int] = {
    6: 7, 12: 1, 3: 4, 8: 9, 2: 3, 9: 10,
    4: 5, 10: 11, 5: 6, 11: 12, 7: 8, 1: 2,
}

# Planet index → canonical name
PLANET_ID_NAME: Dict[int, str] = {
    0: "Sun", 1: "Moon", 2: "Mars", 3: "Mercury",
    4: "Jupiter", 5: "Venus", 6: "Saturn", 7: "Rahu", 8: "Ketu",
}

# Post-marriage house groups
HARMONY_HOUSES    = {2, 5, 7, 11}   # golden phase when both charts fire these
CONFLICT_HOUSES   = {6, 8, 12}      # danger zone when both charts fire these
CHILDBIRTH_HOUSES = {2, 5, 11}      # traditional progeny indicators
WEALTH_HOUSES     = {2, 11}
SEPARATION_HOUSES = {6, 12}


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class CompatibilityVerdict(Enum):
    SUSTAINABLE_MARRIAGE    = "Sustainable Marriage"
    ATTRACTION_ONLY         = "Attraction Only (No Longevity)"
    KARMIC_TRAP             = "Karmic Trap (Intense but Painful)"
    KARMIC_SOULMATE         = "Karmic Soulmate (Intense & Supportive)"
    DESTRUCTIVE_UNION       = "Destructive Union (High Risk)"
    TIMING_MISMATCH         = "Timing Mismatch (Wrong Life Phase)"
    CHALLENGING_BUT_VIABLE  = "Challenging but Viable (Requires Effort)"
    INSUFFICIENT_DATA       = "Insufficient Data"


class RelationshipLayer(Enum):
    PHYSICAL  = "Physical"
    EMOTIONAL = "Emotional"
    KARMIC    = "Karmic"


class MatchQuality(Enum):
    FEEDS     = "Feeds (Stable Loop)"
    NEUTRAL   = "Neutral (No Strong Effect)"
    CONFLICTS = "Conflicts (Friction)"
    DESTROYS  = "Destroys (Active Harm)"
    OBSESSIVE = "Obsessive (Karmic Binding)"


# Post-marriage phase classifications
class MarriagePhaseType(Enum):
    GOLDEN_PHASE     = "Golden Phase"        # Both charts: 2/5/7/11 dominant
    HARMONY          = "Harmony Period"      # One chart strongly positive
    NEUTRAL          = "Neutral Passage"     # No strong signal either way
    TENSION          = "Tension Period"      # Mild conflict signals
    DANGER_ZONE      = "Danger Zone"         # Both charts: 6/8/12 dominant
    SEPARATION_RISK  = "Separation Risk"     # 6/12 in both, weak 7th
    CHILDBIRTH_WINDOW = "Childbirth Window"  # 2/5/11 strong in one or both
    FINANCIAL_STRESS = "Financial Stress"    # 2/11 afflicted, 6/8/12 active
    RENEWAL          = "Renewal Period"      # 1/9 active after conflict block


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HouseAnalysis:
    house_number:   int
    house_lord:     int
    cuspal_sub_lord: int
    star_lord:      int
    strength_score: float          # 0.0 – 1.0
    is_active:      bool
    is_beneficial:  bool
    is_destructive: bool
    notes:          List[str] = field(default_factory=list)


@dataclass
class SourceResultMatch:
    person_a_source:    Dict[int, List[int]]
    person_b_result:    Dict[int, List[int]]
    match_quality:      MatchQuality
    conflict_houses:    List[int]
    supportive_houses:  List[int]
    karmic_indicators:  List[str]
    stability_score:    float
    detailed_analysis:  str


@dataclass
class LayerCompatibility:
    layer:          RelationshipLayer
    is_compatible:  bool
    strength:       float
    key_indicators: List[str]
    warning_signs:  List[str]
    analysis:       str


@dataclass
class DashaEventTiming:
    current_md:          str
    current_ad:          str
    current_sd:          str
    marriage_probability: float
    breakup_risk:        float
    active_houses:       List[int]
    event_window:        Optional[Tuple[datetime, datetime]]
    timing_analysis:     str


# ── NEW v2.0 ──────────────────────────────────────────────────────────────────

@dataclass
class MarriagePhase:
    """One year/period entry in the post-marriage dasha timeline."""
    year_label:      str                # e.g. "Year 1 (2025)"
    groom_md:        str
    groom_ad:        str
    bride_md:        str
    bride_ad:        str
    groom_houses:    List[int]          # significated houses this AD
    bride_houses:    List[int]
    phase_type:      MarriagePhaseType
    harmony_score:   float             # 0.0 – 1.0
    conflict_score:  float             # 0.0 – 1.0
    highlights:      List[str]         # specific events to watch
    guidance:        str               # actionable narrative


@dataclass
class PostMarriageDashaReport:
    """Complete post-marriage timeline for both partners."""
    groom_name:       str
    bride_name:       str
    marriage_year:    int
    scan_years:       int              # how many years scanned
    phases:           List[MarriagePhase]
    golden_phases:    List[str]        # year labels of golden phases
    danger_zones:     List[str]        # year labels of danger zones
    childbirth_windows: List[str]      # year labels
    peak_harmony_year: Optional[str]
    peak_risk_year:   Optional[str]
    executive_summary: str


# ── Main report ───────────────────────────────────────────────────────────────

@dataclass
class CoupleMatchReport:
    person_a_name:   str
    person_b_name:   str
    generation_date: datetime

    verdict:         CompatibilityVerdict
    overall_score:   float

    a_to_b_match:    SourceResultMatch
    b_to_a_match:    SourceResultMatch
    bidirectional_stability: float

    physical_layer:  LayerCompatibility
    emotional_layer: LayerCompatibility
    karmic_layer:    LayerCompatibility

    person_a_relationship_houses: Dict[int, HouseAnalysis]
    person_b_relationship_houses: Dict[int, HouseAnalysis]
    destructive_overlays: List[Tuple[int, int, str]]

    person_a_timing: DashaEventTiming
    person_b_timing: DashaEventTiming
    relationship_timing_verdict: str

    strengths:            List[str]
    critical_weaknesses:  List[str]
    deal_breakers:        List[str]
    survival_requirements: List[str]

    executive_summary: str
    detailed_report:   str
    recommendations:   List[str]

    # v2.0 — populated only when verdict supports marriage
    post_marriage_dasha: Optional[PostMarriageDashaReport] = None

    person_a_chart_data: Optional[Dict] = None
    person_b_chart_data: Optional[Dict] = None

    def to_payload(self) -> Dict[str, Any]:
        """Convert this report object into the specific payload structure expected by CoupleCompatibilityEngine."""
        
        # Helper to format cross-match results
        def _fmt_cm(cm: SourceResultMatch) -> Dict:
            return {
                "quality":          cm.match_quality.value,
                "promise_score":    round(cm.stability_score * 0.8, 2),
                "delivery_score":   cm.stability_score,
                "supportive_houses": [f"H{h}" for h in cm.supportive_houses],
                "conflict_houses":   [f"H{h}" for h in cm.conflict_houses],
                "karmic_note":      "; ".join(cm.karmic_indicators),
            }

        # Helper to format layer results
        def _fmt_layer(l: LayerCompatibility) -> Dict:
            return {
                "status":   l.is_compatible,
                "strength": l.strength,
                "desc":     l.analysis,
            }

        # Format Dasha Timing
        dasha_payload = {
            self.person_a_name: {
                "MD": self.person_a_timing.current_md,
                "AD": self.person_a_timing.current_ad,
                "marriage_prob": int(self.person_a_timing.marriage_probability * 100),
                "breakup_risk":  int(self.person_a_timing.breakup_risk * 100),
                "note": self.person_a_timing.timing_analysis.split("\n")[0]
            },
            self.person_b_name: {
                "MD": self.person_b_timing.current_md,
                "AD": self.person_b_timing.current_ad,
                "marriage_prob": int(self.person_b_timing.marriage_probability * 100),
                "breakup_risk":  int(self.person_b_timing.breakup_risk * 100),
                "note": self.person_b_timing.timing_analysis.split("\n")[0]
            }
        }

        # Format Post-Marriage Dasha Timeline as storytelling narrative
        timeline_text = ""
        if self.post_marriage_dasha:
            pm = self.post_marriage_dasha
            lines = [pm.executive_summary]
            lines.append("")
            lines.append("═" * 79)
            lines.append(f"{'YEAR':<22} {'GROOM MD/AD':<22} {'BRIDE MD/AD':<22} {'PHASE'}")
            lines.append("─" * 79)
            for p in pm.phases:
                g_dash = f"{p.groom_md}/{p.groom_ad}"
                b_dash = f"{p.bride_md}/{p.bride_ad}"
                lines.append(f"{p.year_label:<22} {g_dash:<22} {b_dash:<22} {p.phase_type.value}")
            
            lines.append("")
            lines.append("═" * 79)
            lines.append("YEAR-BY-YEAR NARRATIVE")
            lines.append("═" * 79)
            for i, p in enumerate(pm.phases):
                year_num = i + 1
                lines.append(f"")
                lines.append(f"▸ {p.year_label}  ·  {p.phase_type.value.upper()}")
                lines.append(f"  {self.person_a_name}: {p.groom_md} Mahadasha / {p.groom_ad} Antardasha → Houses {p.groom_houses}")
                lines.append(f"  {self.person_b_name}: {p.bride_md} Mahadasha / {p.bride_ad} Antardasha → Houses {p.bride_houses}")
                lines.append(f"")
                for hl in p.highlights:
                    lines.append(f"  ★ {hl}")
                lines.append(f"")
                lines.append(f"  ✦ {p.guidance}")
                lines.append(f"  {'─' * 60}")
            timeline_text = "\n".join(lines)

        return {
            "person1_name":             self.person_a_name,
            "person2_name":             self.person_b_name,
            "overall_score":            self.overall_score,
            "bidirectional_stability":  self.bidirectional_stability,
            "verdict":                  self.verdict.value,
            "verdict_description":      self.executive_summary,
            "deal_breakers":            self.deal_breakers,
            "survival_requirements":    self.survival_requirements,
            "strengths":                self.strengths,
            "weaknesses":               self.critical_weaknesses,
            "recommendations":          self.recommendations,
            "detailed_report":          self.detailed_report,
            "cross_matching": {
                "a_to_b": _fmt_cm(self.a_to_b_match),
                "b_to_a": _fmt_cm(self.b_to_a_match),
            },
            "multi_layer": {
                "physical":  _fmt_layer(self.physical_layer),
                "emotional": _fmt_layer(self.emotional_layer),
                "karmic":    {
                    "intensity": self.karmic_layer.strength,
                    "origin":    self.karmic_layer.analysis.split("Origin: ")[1].split("\n")[0] if "Origin: " in self.karmic_layer.analysis else "Karmic",
                    "type":      self.karmic_layer.analysis.split("Type: ")[1].split("\n")[0] if "Type: " in self.karmic_layer.analysis else "Standard",
                    "debt_direction": self.karmic_layer.analysis.split("Debt Direction: ")[1].split("\n")[0] if "Debt Direction: " in self.karmic_layer.analysis else "Balanced",
                    "past_pattern":   self.karmic_layer.analysis.split("Past Pattern: ")[1].split("\n")[0] if "Past Pattern: " in self.karmic_layer.analysis else "",
                    "current_purpose": self.karmic_layer.analysis.split("Current Purpose: ")[1].split("\n")[0] if "Current Purpose: " in self.karmic_layer.analysis else "",
                }
            },
            "destructive_overlays": [o[2] for o in self.destructive_overlays],
            "dasha_timing": dasha_payload,
            "timeline_raw_text": timeline_text,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# POST-MARRIAGE DASHA ENGINE  (v2.0)
# ═══════════════════════════════════════════════════════════════════════════════

class PostMarriageDashaEngine:
    """
    Generates a year-by-year post-marriage dasha timeline by overlaying
    the MD-AD significator chains of both bride and groom.
    """

    def __init__(
        self,
        groom_chart: Dict,
        bride_chart: Dict,
        groom_name: str = "Groom",
        bride_name: str = "Bride",
    ) -> None:
        self.groom_chart = groom_chart
        self.bride_chart  = bride_chart
        self.groom_name   = groom_name
        self.bride_name   = bride_name

        # Pre-build significator lookup: planet → set of houses (Result + Source)
        self._groom_sigs = self._build_sig_map(groom_chart)
        self._bride_sigs  = self._build_sig_map(bride_chart)

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_date(s: str) -> Optional[datetime]:
        if not s or not isinstance(s, str):
            return None
        s = s.split()[0] if " " in s else s
        for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(s.strip(), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _build_sig_map(chart: Dict) -> Dict[str, List[int]]:
        """planet-name → [house numbers from both Source and Result Row]."""
        result: Dict[str, List[int]] = {}
        for entry in chart.get("planet_significators", []):
            name = entry.get("planet", "").strip().title()
            houses: set[int] = set()
            for row_key in ("Result_Row", "Source_Row"):
                row = entry.get(row_key, "")
                for tok in str(row).replace("+", "").split(","):
                    tok = tok.strip()
                    if tok.isdigit():
                        houses.add(int(tok))
            if name:
                result[name] = sorted(list(houses))
        return result

    def _houses_for_lord(self, lord: str, sig_map: Dict[str, List[int]]) -> List[int]:
        return list(sig_map.get(lord.strip().title(), []))

    def _classify_phase(
        self,
        groom_h: List[int],
        bride_h:  List[int],
    ) -> Tuple[MarriagePhaseType, float, float]:
        """Return (phase_type, harmony_score, conflict_score)."""
        g = set(groom_h)
        b = set(bride_h)
        combined = g | b

        def calculate_weighted_score(h_set: set[int], target_group: set[int]) -> float:
            match = h_set & target_group
            base = len(match) / len(target_group) if target_group else 0
            if 7 in match: base *= 1.2
            return min(1.0, base)

        harmony_g  = calculate_weighted_score(g, HARMONY_HOUSES)
        harmony_b  = calculate_weighted_score(b, HARMONY_HOUSES)
        conflict_g = calculate_weighted_score(g, CONFLICT_HOUSES)
        conflict_b = calculate_weighted_score(b, CONFLICT_HOUSES)

        # Stricter harmony thresholds: BOTH charts must fire strongly
        both_harmony  = harmony_g > 0.5 and harmony_b > 0.5
        both_conflict = conflict_g > 0.4 and conflict_b > 0.4

        harmony_score  = (harmony_g + harmony_b) / 2.0
        conflict_score = (conflict_g + conflict_b) / 2.0

        sep_risk = (bool(g & SEPARATION_HOUSES) and bool(b & SEPARATION_HOUSES) and 7 not in combined)
        # Childbirth window requires BOTH charts to fire progeny houses
        childbirth_g = bool(g & CHILDBIRTH_HOUSES)
        childbirth_b = bool(b & CHILDBIRTH_HOUSES)
        is_childbirth_window = (childbirth_g and childbirth_b and 5 in combined)

        fin_stress = (not bool(g & WEALTH_HOUSES) and not bool(b & WEALTH_HOUSES) and
                      bool(g & CONFLICT_HOUSES) and bool(b & CONFLICT_HOUSES))

        renewal = bool(combined & {1, 9}) and conflict_score < 0.25 and harmony_score > 0.4

        # Danger / Separation — only when STRONG conflict in BOTH charts
        if both_conflict and conflict_score > 0.55:
            if sep_risk: return MarriagePhaseType.SEPARATION_RISK, harmony_score, conflict_score
            return MarriagePhaseType.DANGER_ZONE, harmony_score, conflict_score
        # Golden Phase — ONLY when both charts STRONGLY fire harmony AND minimal conflict
        if both_harmony and harmony_score > 0.7 and conflict_score < 0.3:
            return MarriagePhaseType.GOLDEN_PHASE, harmony_score, conflict_score
        # Childbirth window
        if is_childbirth_window and harmony_score >= conflict_score:
            return MarriagePhaseType.CHILDBIRTH_WINDOW, harmony_score, conflict_score
        # Financial stress
        if fin_stress:
            return MarriagePhaseType.FINANCIAL_STRESS, harmony_score, conflict_score
        # Renewal
        if renewal:
            return MarriagePhaseType.RENEWAL, harmony_score, conflict_score
        # Harmony — good but not golden
        if harmony_score > conflict_score + 0.15:
            return MarriagePhaseType.HARMONY, harmony_score, conflict_score
        # Tension
        if conflict_score > harmony_score + 0.15:
            return MarriagePhaseType.TENSION, harmony_score, conflict_score

        return MarriagePhaseType.NEUTRAL, harmony_score, conflict_score



    @staticmethod
    def _build_highlights(
        phase_type: MarriagePhaseType,
        groom_h: List[int],
        bride_h:  List[int],
        groom_name: str,
        bride_name: str,
    ) -> List[str]:
        h = []
        g, b = set(groom_h), set(bride_h)

        # Phase-specific primary narrative
        phase_headlines = {
            MarriagePhaseType.GOLDEN_PHASE:
                f"The stars align for {groom_name} and {bride_name} — houses 2, 5, 7 and 11 fire together in both charts. "
                f"This is a rare and powerful convergence: partnership (7th), family growth (2nd), romance (5th), and shared fulfilment (11th) all resonate simultaneously.",
            MarriagePhaseType.DANGER_ZONE:
                f"A turbulent passage opens. Houses 6, 8 and 12 activate in both charts — bringing conflict, hidden tensions and emotional exhaustion. "
                f"What simmers beneath the surface may erupt. This is the period that tests whether the bond can withstand pressure.",
            MarriagePhaseType.SEPARATION_RISK:
                f"⚠ The 6th and 12th houses dominate while the 7th house of partnership goes dark. In both charts, the cosmic signature points toward distance — "
                f"emotional, physical, or legal. This is the most critical juncture in the marriage timeline.",
            MarriagePhaseType.CHILDBIRTH_WINDOW:
                f"The progeny houses (2nd, 5th, 11th) light up across both charts. For those who desire children, this is a structurally supported window — "
                f"the cosmic architecture favours new creation, whether a child, a creative project, or a new venture.",
            MarriagePhaseType.FINANCIAL_STRESS:
                f"Wealth houses (2nd, 11th) go quiet while stress houses activate. The financial fabric of the relationship faces strain — "
                f"budgets tighten, investments disappoint, and money becomes a source of friction rather than security.",
            MarriagePhaseType.RENEWAL:
                f"After the storm, the 1st and 9th houses rise — self-renewal meets higher purpose. This is an invitation to rebuild on new terms, "
                f"not a return to old patterns but a chance to forge something more mature and self-aware.",
            MarriagePhaseType.HARMONY:
                f"A supportive undercurrent runs through this period. One chart leads with positive energy while the other anchors it — "
                f"progress is organic, communication flows, and minor frictions resolve naturally.",
            MarriagePhaseType.TENSION:
                f"Low-grade friction builds. Unresolved issues may resurface disguised as new arguments. "
                f"The period calls for deliberate patience — what is suppressed now will compound later.",
            MarriagePhaseType.NEUTRAL:
                f"A quiet interlude — the cosmic weather is neither pushing forward nor pulling back. "
                f"This is a maintenance window: consolidate gains, nurture routines, and avoid forcing major changes.",
        }
        headline = phase_headlines.get(phase_type)
        if headline:
            h.append(headline)

        # Specific house activations
        if 8 in g or 8 in b:
            who = []
            if 8 in g: who.append(groom_name)
            if 8 in b: who.append(bride_name)
            h.append(f"The 8th house of transformation activates for {' and '.join(who)} — expect deep inner shifts, confrontations with hidden fears, and tests of resilience.")

        if 5 in g and 5 in b:
            h.append(f"The 5th house glows in both charts — romantic reconnection, creative synergy, and playful intimacy return to the foreground.")

        if 10 in g or 10 in b:
            who = []
            if 10 in g: who.append(groom_name)
            if 10 in b: who.append(bride_name)
            h.append(f"Career and public life surge for {' and '.join(who)} (10th house active) — professional demands may compete with domestic attention.")

        if 9 in g or 9 in b:
            h.append("The 9th house of dharma and fortune rises — spiritual growth, travel, or connection with mentors and elders may shape this period.")

        if 4 in g and 4 in b:
            h.append("The 4th house activates in both charts — home, property, and emotional security become central themes.")

        # Specific Life Events Prediction (UAKP Rules)
        for name, houses in [(groom_name, g), (bride_name, b)]:
            if not houses:
                continue
                
            # 1. Property Purchase: 4 + 11 + 12
            if 4 in houses and 11 in houses and 12 in houses:
                h.append(f"Property Investment: {name} shows strong indicators (4+11+12) for buying property or real estate.")
            elif 4 in houses and 11 in houses and 2 not in houses:
                h.append(f"Property/Home: {name} shows favorable indicators (4+11) for property acquisition.")
                
            # 2. Vehicle Purchase: 4 + 11 + 2
            if 4 in houses and 11 in houses and 2 in houses:
                h.append(f"Vehicle Purchase: {name} shows exact indicators (4+11+2) for purchasing a car or major vehicle.")
                
            # 3. Loan / Debt: 6 + 11 (borrowing) or 6 + 8 (debt trap)
            if 6 in houses and 11 in houses:
                h.append(f"Borrowing/Loan: {name} shows indicators (6+11) of receiving a loan or financing.")
            if 6 in houses and 8 in houses:
                h.append(f"Debt Warning: {name} shows indicators (6+8) of falling into a debt trap or struggling with liabilities.")
                
            # 4. Loan Repayment: 5 (12th from 6) + 12 or 11
            if 5 in houses and (12 in houses or 11 in houses) and 6 not in houses:
                h.append(f"Loan Repayment: {name} shows favorable indicators (5+11/12) for closing debts or repaying loans.")
                
            # 5. Travel: 3 (short), 9+12 (long/foreign)
            if 3 in houses and 9 not in houses and 12 not in houses:
                h.append(f"Short Travel: {name} indicates frequent short journeys or domestic travel (3rd house).")
            if 9 in houses and 12 in houses:
                h.append(f"Long/Foreign Travel: {name} shows strong indicators (9+12) for foreign journeys or long-distance relocation.")
                
            # 6. Expenses vs Savings
            if 12 in houses and 8 in houses:
                h.append(f"Heavy Expenses: {name} faces potential heavy, unexpected financial expenses or losses (8+12).")
            if 2 in houses and 11 in houses and 12 not in houses and 8 not in houses:
                h.append(f"Savings Growth: {name} shows excellent potential for cash accumulation and bank balance growth (2+11).")

        # 7. Childbirth Specifics (Combined check)
        combined = g | b
        if 5 in combined:
            if 2 in combined and 11 in combined and not (8 in combined or 12 in combined):
                h.append("Childbirth (Normal): Highly favorable window for natural childbirth and family growth (2+5+11).")
            elif 5 in combined and 8 in combined and 12 in combined:
                h.append("Childbirth (Medical/IVF): Window indicates childbirth through medical intervention, surgery, or IVF (5+8+12).")
        
        if 4 in combined and 8 in combined and 12 in combined and 5 not in combined:
            h.append("Childbirth (Obstacles): Warning for childbirth issues, delays, or potential medical complications regarding progeny (4+8+12).")

        return h if h else ["A standard period with no dominant astrological signatures — the relationship continues on its natural trajectory."]

    def _build_guidance(self, phase_type: MarriagePhaseType, year_offset: int = 0,
                        g_md: str = "", g_ad: str = "", b_md: str = "", b_ad: str = "") -> str:
        """Build year-specific guidance narrative incorporating dasha lord context."""
        # Dasha lord personality archetypes for richer narratives
        lord_themes = {
            "Sun":     "authority, ego, recognition",
            "Moon":    "emotions, nurturing, intuition",
            "Mars":    "action, conflict, passion",
            "Mercury": "communication, intellect, adaptability",
            "Jupiter": "wisdom, expansion, generosity",
            "Venus":   "love, comfort, luxury",
            "Saturn":  "discipline, restriction, endurance",
            "Rahu":    "obsession, ambition, unconventional desire",
            "Ketu":    "detachment, spirituality, sudden release",
        }
        g_ad_theme = lord_themes.get(g_ad, "mixed energies")
        b_ad_theme = lord_themes.get(b_ad, "mixed energies")

        year_label = f"Year {year_offset + 1}" if year_offset >= 0 else "this period"

        guidance_map = {
            MarriagePhaseType.GOLDEN_PHASE: (
                f"This is your peak period in {year_label}. The groom's {g_ad} Antardasha brings {g_ad_theme}, "
                f"while the bride's {b_ad} Antardasha channels {b_ad_theme}. Together, these create a powerful "
                f"synergy for deepening commitment. Use this window for milestone decisions — home purchases, "
                f"family expansion, or long-term investments. The cosmic architecture supports you both; "
                f"don't squander this alignment in petty disputes."
            ),
            MarriagePhaseType.HARMONY: (
                f"In {year_label}, the groom operates under {g_ad}'s influence ({g_ad_theme}) while the bride "
                f"moves through {b_ad} ({b_ad_theme}). One chart leads with warmth while the other provides "
                f"stable support. Progress happens organically — keep communication open, nurture what's growing, "
                f"and resist the temptation to amplify small frictions into lasting grievances."
            ),
            MarriagePhaseType.NEUTRAL: (
                f"{year_label} is a quiet passage. The groom's {g_ad} and bride's {b_ad} periods create neither "
                f"strong currents nor counter-forces. This is a maintenance window: strengthen daily rituals, "
                f"consolidate earlier gains, and build the routines that will carry you through turbulent years ahead."
            ),
            MarriagePhaseType.TENSION: (
                f"Friction builds in {year_label}. The groom's {g_ad} period ({g_ad_theme}) may clash with "
                f"the bride's {b_ad} energy ({b_ad_theme}). Avoid major decisions under emotional pressure. "
                f"Old wounds may resurface in new disguises — address them honestly rather than suppressing them. "
                f"Quality time and deliberate patience are your best tools."
            ),
            MarriagePhaseType.DANGER_ZONE: (
                f"⚠ {year_label} activates destructive houses in both charts simultaneously. The groom's {g_ad} "
                f"({g_ad_theme}) and bride's {b_ad} ({b_ad_theme}) create a volatile cocktail. Disagreements that "
                f"escalate now can leave permanent scars. Seek mediation early. Avoid financial risks, major "
                f"relocations, or family confrontations. If professional counselling is available, this is the year to use it."
            ),
            MarriagePhaseType.SEPARATION_RISK: (
                f"⚠ CRITICAL: {year_label} shows separation indicators active in both charts while marriage house "
                f"energy is absent. The groom's {g_ad} period ({g_ad_theme}) and bride's {b_ad} ({b_ad_theme}) "
                f"pull in incompatible directions. Do NOT make irreversible decisions in anger. Physical distance — "
                f"travel, work — can provide temporary relief. Karmic analysis suggests this may be a passage, not an ending, "
                f"but only conscious effort ensures return."
            ),
            MarriagePhaseType.CHILDBIRTH_WINDOW: (
                f"The progeny houses light up in {year_label}. The groom's {g_ad} ({g_ad_theme}) and bride's "
                f"{b_ad} ({b_ad_theme}) together create a fertile cosmic window. If children are desired, this is "
                f"structurally the right time. Even if parenthood is not planned, this energy supports 'birthing' "
                f"creative projects, new ventures, or businesses with equal force."
            ),
            MarriagePhaseType.FINANCIAL_STRESS: (
                f"Financial pressure defines {year_label}. The groom's {g_ad} period ({g_ad_theme}) and bride's "
                f"{b_ad} ({b_ad_theme}) leave wealth houses unsupported while stress houses activate. Avoid "
                f"speculative investments and large expenditures. Review budgets together. Financial disputes "
                f"between partners can become relationship fault-lines — consider separating finances temporarily "
                f"if tension rises."
            ),
            MarriagePhaseType.RENEWAL: (
                f"After difficulty, {year_label} brings renewal. The groom's {g_ad} ({g_ad_theme}) and bride's "
                f"{b_ad} ({b_ad_theme}) activate the 1st and 9th houses — self-renewal meets higher purpose. "
                f"This is not a return to the past; it is an invitation to rebuild something more mature. "
                f"Recommit consciously, on new terms, not out of habit or fear."
            ),
        }
        return guidance_map.get(phase_type, "Monitor the period, maintain open dialogue, and prioritise emotional honesty.")

    # ── main scanner ──────────────────────────────────────────────────────────

    def generate(
        self,
        marriage_year: int,
        scan_years: int = 15,
    ) -> PostMarriageDashaReport:
        """
        Scan 'scan_years' worth of MD-AD periods starting from marriage_year.
        Returns a PostMarriageDashaReport with per-year phase analysis.
        """
        phases:             List[MarriagePhase] = []
        golden_phases:      List[str] = []
        danger_zones:       List[str] = []
        childbirth_windows: List[str] = []
        year_cursor        = marriage_year

        # Flatten both dasha trees into (lord_md, lord_ad, start_date, end_date) tuples
        groom_periods = self._flatten_dasa(self.groom_chart, marriage_year, scan_years)
        bride_periods  = self._flatten_dasa(self.bride_chart, marriage_year, scan_years)

        # Pair them year by year
        for year_offset in range(scan_years):
            target_year = marriage_year + year_offset
            label = f"Year {year_offset + 1} ({target_year})"

            # Use mid-year date to find the dominant MD/AD for that year
            mid_year_dt = datetime(target_year, 7, 1)
            g_entry = self._find_entry_for_date(groom_periods, mid_year_dt)
            b_entry = self._find_entry_for_date(bride_periods, mid_year_dt)

            if not g_entry or not b_entry:
                continue

            g_md, g_ad = g_entry
            b_md, b_ad = b_entry

            g_houses = self._houses_for_lord(g_ad, self._groom_sigs)
            b_houses  = self._houses_for_lord(b_ad, self._bride_sigs)

            # Fall back to MD if AD is empty
            if not g_houses:
                g_houses = self._houses_for_lord(g_md, self._groom_sigs)
            if not b_houses:
                b_houses = self._houses_for_lord(b_md, self._bride_sigs)

            phase_type, harmony_score, conflict_score = self._classify_phase(
                g_houses, b_houses
            )

            highlights = self._build_highlights(
                phase_type, g_houses, b_houses, self.groom_name, self.bride_name
            )
            guidance = self._build_guidance(phase_type, year_offset=year_offset,
                                             g_md=g_md, g_ad=g_ad, b_md=b_md, b_ad=b_ad)

            phase = MarriagePhase(
                year_label    = label,
                groom_md      = g_md,
                groom_ad      = g_ad,
                bride_md      = b_md,
                bride_ad      = b_ad,
                groom_houses  = g_houses,
                bride_houses  = b_houses,
                phase_type    = phase_type,
                harmony_score = round(harmony_score, 2),
                conflict_score= round(conflict_score, 2),
                highlights    = highlights,
                guidance      = guidance,
            )
            phases.append(phase)

            if phase_type == MarriagePhaseType.GOLDEN_PHASE:
                golden_phases.append(label)
            elif phase_type in (MarriagePhaseType.DANGER_ZONE, MarriagePhaseType.SEPARATION_RISK):
                danger_zones.append(label)
            elif phase_type == MarriagePhaseType.CHILDBIRTH_WINDOW:
                childbirth_windows.append(label)

        peak_harmony = max(phases, key=lambda p: p.harmony_score, default=None)
        peak_risk    = max(phases, key=lambda p: p.conflict_score, default=None)

        summary = self._build_executive_summary(
            phases, golden_phases, danger_zones, childbirth_windows,
            peak_harmony, peak_risk
        )

        return PostMarriageDashaReport(
            groom_name        = self.groom_name,
            bride_name        = self.bride_name,
            marriage_year     = marriage_year,
            scan_years        = scan_years,
            phases            = phases,
            golden_phases     = golden_phases,
            danger_zones      = danger_zones,
            childbirth_windows= childbirth_windows,
            peak_harmony_year = peak_harmony.year_label if peak_harmony else None,
            peak_risk_year    = peak_risk.year_label    if peak_risk    else None,
            executive_summary = summary,
        )

    # ── dasha tree helpers ────────────────────────────────────────────────────

    @staticmethod
    def _flatten_dasa(
        chart: Dict,
        from_year: int,
        scan_years: int,
    ) -> List[Tuple[str, str, datetime, datetime]]:
        """
        Returns list of (md_lord, ad_lord, start_date, end_date).
        """
        result: List[Tuple[str, str, datetime, datetime]] = []
        from_dt = datetime(from_year, 1, 1)
        to_dt   = datetime(from_year + scan_years, 1, 1)
        
        for md in chart.get("vimshottari_dasa_full", []):
            md_lord = md.get("lord", "")
            for ad in md.get("sub_periods", []):
                ad_lord = ad.get("lord", "")
                s = PostMarriageDashaEngine._parse_date(ad.get("start", ""))
                e = PostMarriageDashaEngine._parse_date(ad.get("end", ""))
                if not s or not e:
                    continue
                # Overlap check
                if e < from_dt or s >= to_dt:
                    continue
                result.append((md_lord, ad_lord, s, e))
        return result

    @staticmethod
    def _find_entry_for_date(
        entries: List[Tuple[str, str, datetime, datetime]],
        target_dt: datetime,
    ) -> Optional[Tuple[str, str]]:
        """Return (md_lord, ad_lord) whose date range exactly covers 'target_dt'."""
        for md, ad, s, e in entries:
            if s <= target_dt <= e:
                return md, ad
        return None

    # ── summary builder ───────────────────────────────────────────────────────

    def _build_executive_summary(
        self,
        phases:             List[MarriagePhase],
        golden_phases:      List[str],
        danger_zones:       List[str],
        childbirth_windows: List[str],
        peak_harmony:       Optional[MarriagePhase],
        peak_risk:          Optional[MarriagePhase],
    ) -> str:
        scan_years = len(phases)
        start_year = phases[0].year_label.split('(')[1].rstrip(')') if phases else 'N/A'
        
        lines = [
            f"POST-MARRIAGE DASHA OVERVIEW — {self.groom_name} & {self.bride_name}",
            f"What follows is a {scan_years}-year forensic scan beginning from the marriage year {start_year}.",
            f"Each year is classified by overlaying the Mahadasha-Antardasha significator chains of both charts.",
            "",
        ]
        
        # Build narrative overview paragraph
        total = len(phases)
        phase_counts = {}
        for p in phases:
            phase_counts[p.phase_type.value] = phase_counts.get(p.phase_type.value, 0) + 1
        
        dominant = max(phase_counts, key=phase_counts.get) if phase_counts else "Mixed"
        dominant_pct = round(phase_counts.get(dominant, 0) / total * 100) if total else 0
        
        overview = (
            f"Across {total} years, the dominant energy is '{dominant}' ({dominant_pct}% of the timeline). "
        )
        if golden_phases:
            overview += f"Golden phases appear in {len(golden_phases)} year(s): {', '.join(golden_phases)}. "
        else:
            overview += "No golden phases (peak alignment) were detected in this scan window. "
        if danger_zones:
            overview += f"Danger zones surface in {len(danger_zones)} year(s): {', '.join(danger_zones)}. "
        if childbirth_windows:
            overview += f"Childbirth-supportive windows open in {len(childbirth_windows)} year(s): {', '.join(childbirth_windows)}."
        
        lines.append(overview)
        lines.append("")
        
        if peak_harmony:
            lines.append(
                f"Peak Harmony:  {peak_harmony.year_label}  "
                f"({self.groom_name} MD:{peak_harmony.groom_md}/AD:{peak_harmony.groom_ad}  |  "
                f"{self.bride_name} MD:{peak_harmony.bride_md}/AD:{peak_harmony.bride_ad})  "
                f"— Harmony score {peak_harmony.harmony_score:.2f}"
            )
        if peak_risk:
            lines.append(
                f"Peak Risk:     {peak_risk.year_label}  "
                f"— Conflict score {peak_risk.conflict_score:.2f}  [{peak_risk.phase_type.value}]"
            )

        lines += [
            "",
            "PHASE LEGEND:",
            "  Golden Phase      → Invest, commit, expand — the cosmos supports bold moves.",
            "  Harmony Period    → Steady growth; don't take it for granted.",
            "  Neutral Passage   → Maintenance mode; consolidate, don't push.",
            "  Tension Period    → Address friction early before it calcifies.",
            "  Danger Zone       → Seek mediation; postpone irreversible decisions.",
            "  Separation Risk   → ⚠ Critical — professional guidance needed immediately.",
            "  Childbirth Window → Structurally favoured for conception or new ventures.",
            "  Financial Stress  → Tighten budgets; avoid speculation and joint debt.",
            "  Renewal Period    → Rebuild on new terms after difficulty.",
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# CORE ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class UakpCoupleAnalyzer:
    """
    UAKP Couple Matchmaking Engine v2.0

    Implements the Source → Interaction → Result → Event Trigger chain
    and, for viable matches, a full post-marriage dasha timeline.
    """

    RELATIONSHIP_HOUSES = [2, 5, 7, 8, 11]
    MARRIAGE_HOUSES     = [2, 7, 11]
    LOVE_HOUSES         = [5, 7]
    SEXUAL_BONDING_HOUSES = [8]
    DESTRUCTIVE_HOUSES  = [6, 8, 12]

    # Verdicts that warrant post-marriage analysis
    MARRIAGE_VERDICTS = {
        CompatibilityVerdict.SUSTAINABLE_MARRIAGE,
        CompatibilityVerdict.KARMIC_SOULMATE,
        CompatibilityVerdict.CHALLENGING_BUT_VIABLE,
        CompatibilityVerdict.TIMING_MISMATCH,
        CompatibilityVerdict.DESTRUCTIVE_UNION,
        CompatibilityVerdict.KARMIC_TRAP,
        CompatibilityVerdict.ATTRACTION_ONLY,
    }
    
    PLANET_NAME_TO_ID = {v: k for k, v in PLANET_ID_NAME.items()}

    def __init__(self) -> None:
        self.analysis_cache: Dict = {}

    def _normalize_v11_data(self, chart: Dict) -> Dict:
        """
        Adapts V11 engine export to the internal format expected by the analyzer.
        Maps names to IDs and extracts current dasha info from the full tree.
        """
        if not chart: return {}
        if "house_lords" in chart and "current_mahadasha" in chart:
            return chart # Already normalized or legacy format

        # 1. Rebuild House Lords / Star Lords / Sub Lords from V11 house_cusps
        house_lords      = {}
        star_lords       = {}
        cuspal_sub_lords = {}
        
        for cusp_data in chart.get("house_cusps", []):
            h_num = cusp_data.get("cusp")
            if h_num:
                house_lords[h_num]      = self.PLANET_NAME_TO_ID.get(cusp_data.get("sign_lord"), -1)
                star_lords[h_num]       = self.PLANET_NAME_TO_ID.get(cusp_data.get("star_lord"), -1)
                cuspal_sub_lords[h_num] = self.PLANET_NAME_TO_ID.get(cusp_data.get("sub_lord"), -1)
        
        # 2. Rebuild Planet Info from planetary_positions
        planets_data = {}
        for p_pos in chart.get("planetary_positions", []):
            name = p_pos.get("planet")
            if name in self.PLANET_NAME_TO_ID:
                pid = self.PLANET_NAME_TO_ID[name]
                # In V11, we might need to derive exaltation etc. if not present
                # For now, we seed minimal required flags to avoid 0.00 scores
                planets_data[pid] = {
                    "is_exalted": False, "is_own_sign": False, "is_debilitated": False
                }
                planets_data[name] = planets_data[pid] # dual access

        # 3. Detect Current Dasha from full tree
        now = datetime.now()
        cur_md, cur_ad, cur_sd = "Unknown", "Unknown", "Unknown"
        md_pid, ad_pid, sd_pid = -1, -1, -1
        
        def _get_dt(s: str) -> Optional[datetime]:
            for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y"):
                try: return datetime.strptime(s, fmt)
                except: continue
            return None

        for md in chart.get("vimshottari_dasa_full", []):
            s_md, e_md = _get_dt(md.get("start", "")), _get_dt(md.get("end", ""))
            if s_md and e_md and s_md <= now <= e_md:
                cur_md = md.get("lord", "")
                md_pid = self.PLANET_NAME_TO_ID.get(cur_md, -1)
                for ad in md.get("sub_periods", []):
                    s_ad, e_ad = _get_dt(ad.get("start", "")), _get_dt(ad.get("end", ""))
                    if s_ad and e_ad and s_ad <= now <= e_ad:
                        cur_ad = ad.get("lord", "")
                        ad_pid = self.PLANET_NAME_TO_ID.get(cur_ad, -1)
                        for sd in ad.get("sub_periods", []):
                            s_sd, e_sd = _get_dt(sd.get("start", "")), _get_dt(sd.get("end", ""))
                            if s_sd and e_sd and s_sd <= now <= e_sd:
                                cur_sd = sd.get("lord", "")
                                sd_pid = self.PLANET_NAME_TO_ID.get(cur_sd, -1)
        
        # 4. Integrate back
        norm = copy.deepcopy(chart)
        norm.update({
            "house_lords":      house_lords,
            "star_lords":       star_lords,
            "cuspal_sub_lords": cuspal_sub_lords,
            "planets":          planets_data,
            "current_mahadasha":       cur_md,
            "current_antardasha":      cur_ad,
            "current_pratyantardasha": cur_sd,
            "md_lord_planet":          md_pid,
            "ad_lord_planet":          ad_pid,
            "sd_lord_planet":          sd_pid,
        })
        return norm

    # ═══════════════════════════════════════════════════════════════════════════
    # HOUSE ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════

    def analyze_relationship_house(
        self,
        house_num: int,
        chart_data: Dict,
        context: str = "general",
    ) -> HouseAnalysis:
        house_lord      = chart_data.get("house_lords", {}).get(house_num, 0)
        cuspal_sub_lord = chart_data.get("cuspal_sub_lords", {}).get(house_num, 0)
        star_lord       = chart_data.get("star_lords", {}).get(house_num, 0)

        strength_score = self._calculate_house_strength(
            house_num, house_lord, cuspal_sub_lord, star_lord, chart_data
        )

        notes = []
        house_note_map = {
            7:  "Marriage / Partnership — primary relationship indicator",
            5:  "Love / Romance — emotional attraction",
            8:  "Sexual bonding / Transformation — intensity & durability",
            2:  "Family continuation — long-term stability",
            11: "Fulfilment of desires — relationship satisfaction",
            6:  "Conflict / Litigation — destroys 7th house",
            12: "Loss / Separation — destroys 1st house",
        }
        if house_num in house_note_map:
            notes.append(house_note_map[house_num])

        return HouseAnalysis(
            house_number    = house_num,
            house_lord      = house_lord,
            cuspal_sub_lord = cuspal_sub_lord,
            star_lord       = star_lord,
            strength_score  = strength_score,
            is_active       = strength_score > 0.5,
            is_beneficial   = house_num in self.RELATIONSHIP_HOUSES,
            is_destructive  = house_num in self.DESTRUCTIVE_HOUSES,
            notes           = notes,
        )

    def _calculate_house_strength(
        self,
        house_num:      int,
        house_lord:     int,
        cuspal_sub_lord: int,
        star_lord:      int,
        chart_data:     Dict,
    ) -> float:
        strength  = 0.0
        planets   = chart_data.get("planets", {})

        def pdata(pid: int) -> Dict:
            if pid in planets:
                return planets[pid]
            name = PLANET_ID_NAME.get(pid)
            return planets.get(name, {}) if name else {}

        # Weights: CSL 60 %, star lord 30 %, house lord 10 %
        for pid, w_ex, w_own, w_deb, w_def in [
            (cuspal_sub_lord, 0.60, 0.45, 0.15, 0.30),
            (star_lord,       0.30, 0.22, 0.08, 0.15),
            (house_lord,      0.10, 0.07, 0.03, 0.05),
        ]:
            pd = pdata(pid)
            if pd:
                if   pd.get("is_exalted"):     strength += w_ex
                elif pd.get("is_own_sign"):    strength += w_own
                elif pd.get("is_debilitated"): strength += w_deb
                else:                          strength += w_def

        return min(strength, 1.0)

    def detect_destructive_overlays(
        self,
        a_houses: Dict[int, HouseAnalysis],
        b_houses: Dict[int, HouseAnalysis],
    ) -> List[Tuple[int, int, str]]:
        overlays: List[Tuple[int, int, str]] = []

        for destructor, victim in DESTRUCTION_MAP.items():
            for src_houses, tgt_houses, direction in [
                (a_houses, b_houses, "A→B"),
                (b_houses, a_houses, "B→A"),
            ]:
                src = src_houses.get(destructor)
                tgt = tgt_houses.get(victim)
                if src and tgt and src.is_active and tgt.is_beneficial:
                    overlays.append((
                        destructor, victim,
                        f"[{direction}] {destructor}H (str {src.strength_score:.2f}) "
                        f"destroys {victim}H (str {tgt.strength_score:.2f}) — "
                        f"conflict in {HOUSE_MEANINGS.get(victim, f'H{victim}')}."
                    ))

        # Critical pair check
        critical = [(6, 7, "Conflict vs Marriage"), (8, 2, "Transformation vs Family"),
                    (12, 7, "Loss vs Marriage"), (12, 1, "Loss vs Self")]
        for h1, h2, meaning in critical:
            ah1 = a_houses.get(h1)
            bh2 = b_houses.get(h2)
            if (ah1 and bh2 and ah1.is_active and bh2.is_active
                    and ah1.strength_score > 0.6 and bh2.strength_score > 0.6):
                overlays.append((h1, h2, f"CRITICAL: {meaning}"))

        return overlays

    # ═══════════════════════════════════════════════════════════════════════════
    # SOURCE-RESULT CROSS-MATCHING
    # ═══════════════════════════════════════════════════════════════════════════

    def cross_match_source_result(
        self,
        a_chart: Dict,
        b_chart: Dict,
        direction: str = "a_to_b",
    ) -> SourceResultMatch:
        src_chart = a_chart if direction == "a_to_b" else b_chart
        res_chart = b_chart if direction == "a_to_b" else a_chart
        prefix    = "Person A wants, Person B gives" if direction == "a_to_b" else "Person B wants, Person A gives"

        source_row = self._extract_source_row(src_chart)
        # Fix: The interaction logic matches A's source (expectations) against B's Chart
        # No separate extraction of B's result row here; _evaluate_signification_match handles looked-up logic.
        result_row = source_row 

        conflict_houses:   List[int] = []
        supportive_houses: List[int] = []
        karmic_indicators: List[str] = []
        match_scores:      List[float] = []

        for h in self.RELATIONSHIP_HOUSES:
            mq = self._evaluate_signification_match(
                source_row.get(h, []), result_row.get(h, []), h, res_chart
            )
            score_map = {"FEEDS": 1.0, "NEUTRAL": 0.5, "CONFLICTS": 0.2,
                         "DESTROYS": 0.0, "OBSESSIVE": 0.3}
            match_scores.append(score_map.get(mq, 0.5))
            if mq in ("CONFLICTS", "DESTROYS"):
                conflict_houses.append(h)
            elif mq == "FEEDS":
                supportive_houses.append(h)
            elif mq == "OBSESSIVE":
                karmic_indicators.append(f"House {h}: karmic obsession")

        stability = sum(match_scores) / len(match_scores) if match_scores else 0.0

        # Unified linkage bonus
        r7  = set(result_row.get(7, []))
        r2  = set(result_row.get(2, []))
        r11 = set(result_row.get(11, []))
        if r7 and ((r7 & r2) or (r7 & r11)):
            stability = min(1.0, stability * 1.3)
            karmic_indicators.append("Unified Linkage: 7H tied to 2H/11H.")

        if stability > 0.7:     quality = MatchQuality.FEEDS
        elif stability > 0.5:   quality = MatchQuality.NEUTRAL
        elif stability > 0.3:   quality = MatchQuality.CONFLICTS
        elif karmic_indicators: quality = MatchQuality.OBSESSIVE
        else:                   quality = MatchQuality.DESTROYS

        parts = [prefix]
        if supportive_houses:
            parts.append(f"\n✓ Supportive (H{supportive_houses}): desires align with delivery")
        if conflict_houses:
            parts.append(f"\n✗ Conflict   (H{conflict_houses}): expectations don't match reality")
        if karmic_indicators:
            parts.append(f"\n⚠ Karmic: {'; '.join(karmic_indicators)}")

        return SourceResultMatch(
            person_a_source   = source_row if direction == "a_to_b" else result_row,
            person_b_result   = result_row if direction == "a_to_b" else source_row,
            match_quality     = quality,
            conflict_houses   = conflict_houses,
            supportive_houses = supportive_houses,
            karmic_indicators = karmic_indicators,
            stability_score   = round(stability, 3),
            detailed_analysis = "\n".join(parts),
        )

    def _extract_source_row(self, chart: Dict) -> Dict[int, List[int]]:
        row: Dict[int, List[int]] = {}
        for h in range(1, 13):
            csl = chart.get("cuspal_sub_lords", {}).get(h, 0)
            stl = chart.get("star_lords", {}).get(h, 0)
            row[h] = [x for x in [csl, stl] if x]
        return row

    def _extract_result_row(self, chart: Dict) -> Dict[int, List[int]]:
        return self._extract_source_row(chart)  # same structure, semantics differ by context

    def _get_weighted_planet_significations(
        self,
        planet_num: int,
        chart: Dict,
    ) -> Dict[int, float]:
        weights: Dict[int, float] = {}
        name = PLANET_ID_NAME.get(planet_num, "")

        for entry in chart.get("planet_significators", []):
            if entry.get("planet", "").strip().title() == name.title():
                for row_key, w in [("Result_Row", 1.0), ("Source_Row", 0.7)]:
                    for tok in str(entry.get(row_key, "")).replace("+", "").split(","):
                        tok = tok.strip()
                        if tok.isdigit():
                            h = int(tok)
                            weights[h] = max(weights.get(h, 0.0), w)
                break

        if not weights:
            for store, w in [
                ("cuspal_sub_lords", 1.0),
                ("star_lords",       0.5),
                ("house_lords",      0.2),
            ]:
                for h, pid in chart.get(store, {}).items():
                    if pid == planet_num:
                        weights[h] = max(weights.get(h, 0.0), w)

        return weights

    def _evaluate_signification_match(
        self,
        source_sigs: List[int],
        result_sigs: List[int],
        house_num:   int,
        result_chart: Dict,
    ) -> str:
        if not source_sigs or not result_sigs:
            return "NEUTRAL"

        destructor: Optional[int] = None
        for d, v in DESTRUCTION_MAP.items():
            if v == house_num:
                destructor = d
                break

        result_weights: Dict[int, float] = {}
        for pid in filter(None, result_sigs):
            for h, w in self._get_weighted_planet_significations(pid, result_chart).items():
                result_weights[h] = max(result_weights.get(h, 0.0), w)

        if house_num in [8, 12]:
            return "OBSESSIVE"

        first_result = [result_sigs[0]] if result_sigs else []
        overlap_strong = any(p in first_result for p in set(source_sigs) & set(result_sigs))
        destructor_w   = result_weights.get(destructor, 0.0) if destructor else 0.0
        support_w      = result_weights.get(house_num, 0.0)

        if destructor_w >= 0.4 and destructor_w > support_w:
            return "DESTROYS" if house_num in self.MARRIAGE_HOUSES else (
                "CONFLICTS" if destructor_w >= 0.6 else "NEUTRAL"
            )

        if support_w >= 0.5 or overlap_strong:
            return "FEEDS"
        return "NEUTRAL"

    # ═══════════════════════════════════════════════════════════════════════════
    # MULTI-LAYER COMPATIBILITY
    # ═══════════════════════════════════════════════════════════════════════════

    def assess_physical_layer(
        self,
        a_chart: Dict, b_chart: Dict,
        a_houses: Dict[int, HouseAnalysis],
        b_houses: Dict[int, HouseAnalysis],
    ) -> LayerCompatibility:
        key, warn, scores = [], [], []

        for label, houses, chart in [("Person A", a_houses, a_chart), ("Person B", b_houses, b_chart)]:
            h7 = houses.get(7)
            if h7:
                scores.append(h7.strength_score)
                (key if h7.strength_score > 0.6 else warn).append(
                    f"{label}: {'Strong' if h7.strength_score > 0.6 else 'Weak'} 7th house"
                )
            for planet_id, planet_label in [(5, "Venus"), (2, "Mars")]:
                pd = chart.get("planets", {}).get(planet_id, {})
                if pd.get("is_exalted") or pd.get("is_own_sign"):
                    key.append(f"{label}: Strong {planet_label}")
                    scores.append(0.8)
                elif pd.get("is_debilitated"):
                    warn.append(f"{label}: Weak {planet_label}")
                    scores.append(0.2)

        strength = sum(scores) / len(scores) if scores else 0.5
        compat   = strength > 0.6
        return LayerCompatibility(
            layer           = RelationshipLayer.PHYSICAL,
            is_compatible   = compat,
            strength        = round(strength, 3),
            key_indicators  = key,
            warning_signs   = warn,
            analysis        = (
                "Physical attraction layer is STRONG — foundation for mutual attraction exists."
                if compat else
                "Physical attraction layer is WEAK — limited capacity for mutual draw."
            ),
        )

    def assess_emotional_layer(
        self,
        a_chart: Dict, b_chart: Dict,
        a_houses: Dict[int, HouseAnalysis],
        b_houses: Dict[int, HouseAnalysis],
    ) -> LayerCompatibility:
        key, warn, scores = [], [], []

        for label, houses, chart in [("Person A", a_houses, a_chart), ("Person B", b_houses, b_chart)]:
            h5 = houses.get(5)
            if h5:
                scores.append(h5.strength_score)
                (key if h5.strength_score > 0.6 else warn).append(
                    f"{label}: {'Strong' if h5.strength_score > 0.6 else 'Weak'} 5th house"
                )
            moon = chart.get("planets", {}).get(1, {})
            if moon.get("is_exalted") or moon.get("is_own_sign"):
                key.append(f"{label}: Strong Moon (emotional stability)");  scores.append(0.8)
            elif moon.get("is_debilitated"):
                warn.append(f"{label}: Weak Moon (volatility)");             scores.append(0.2)
            h4 = houses.get(4)
            if h4 and h4.strength_score > 0.6:
                key.append(f"{label}: Strong 4th house (emotional peace)");  scores.append(h4.strength_score)

        base = sum(scores) / len(scores) if scores else 0.5
        mult = 1.0

        for label, chart, houses in [("Person A", a_chart, a_houses), ("Person B", b_chart, b_houses)]:
            moon_sigs = self._get_planet_house_significations(1, chart)
            h5l       = chart.get("house_lords", {}).get(5, 0)
            h5_sigs   = self._get_planet_house_significations(h5l, chart) if h5l else []
            all_sigs  = moon_sigs + h5_sigs
            if 6 in all_sigs:
                warn.append(f"{label}: Emotional needs tied to conflict (6H)")
                mult *= 0.9
            if 8 in all_sigs:
                warn.append(f"{label}: Trauma intensity possible (8H)")
                mult *= 0.85
            if 2 in all_sigs or 11 in all_sigs:
                key.append(f"{label}: Emotional stability via 2H/11H buffer")
                mult *= 1.15  # Stabilized multiplier (prev 1.2)

        strength = round(min(1.0, base * mult), 3)
        compat   = strength > 0.6
        return LayerCompatibility(
            layer           = RelationshipLayer.EMOTIONAL,
            is_compatible   = compat,
            strength        = strength,
            key_indicators  = key,
            warning_signs   = warn,
            analysis        = (
                "Emotional bonding layer STRONG — deep connection possible."
                if compat else
                "Emotional bonding layer WEAK or TOXIC — healthy integration is difficult."
            ),
        )

    def assess_karmic_layer(
        self,
        a_chart: Dict, b_chart: Dict,
        a_houses: Dict[int, HouseAnalysis],
        b_houses: Dict[int, HouseAnalysis],
        a_to_b_stability: float = 0.5,
        b_to_a_stability: float = 0.5,
        person_a_name: str = "Person A",
        person_b_name: str = "Person B",
    ) -> LayerCompatibility:
        key, warn = [], []

        def gs(h_dict: Dict[int, HouseAnalysis], n: int) -> float:
            h = h_dict.get(n)
            return h.strength_score if h else 0.0

        linked = {
            h for h in self.RELATIONSHIP_HOUSES + self.DESTRUCTIVE_HOUSES
            if (gs(a_houses, h) + gs(b_houses, h)) / 2 > 0.4
        }

        kscore = min(1.0,
            0.4 * (8 in linked) +
            0.3 * (12 in linked) +
            0.2 * (6 in linked)
        )

        a_rahu = set(self._get_planet_house_significations(7, a_chart))
        b_rahu = set(self._get_planet_house_significations(7, b_chart))
        rahu_link = bool({1, 5, 7, 8} & (a_rahu | b_rahu))
        if rahu_link: kscore = min(1.0, kscore + 0.3)

        if (8 in linked or 12 in linked) and rahu_link:  origin = "PAST LIFE CONNECTION"
        elif kscore > 0.5:                                origin = "KARMIC (UNCLEAR ORIGIN)"
        else:                                             origin = "NEW IN THIS LIFE"

        weak_7  = gs(a_houses, 7) < 0.5 and gs(b_houses, 7) < 0.5
        strong_7 = not weak_7
        strong_5 = gs(a_houses, 5) > 0.5
        low_68   = 6 not in linked and 8 not in linked

        if   kscore < 0.3:                              ktype = "NEW_RELATIONSHIP"
        elif 8 in linked and 12 in linked and weak_7:  ktype = "OBSESSIVE_LOOP";     warn.append("Addiction loop risk")
        elif 6 in linked and (7 in linked or 8 in linked): ktype = "DEBT";           warn.append("Karmic debt repayment")
        elif strong_7 and strong_5 and 11 in linked and low_68: ktype = "SOULMATE";  key.append("Supportive continuity")
        elif 8 in linked and strong_7:                 ktype = "TRANSFORMATIONAL";   key.append("Growth-oriented pain")
        else:                                           ktype = "GENERAL_KARMIC"

        if   a_to_b_stability < b_to_a_stability - 0.1: debt = f"{person_a_name} is paying karmic debt"
        elif b_to_a_stability < a_to_b_stability - 0.1: debt = f"{person_b_name} is paying karmic debt"
        else:                                            debt = "BALANCED (Mutual Exchange)"

        hs = {h: (gs(a_houses, h) + gs(b_houses, h)) / 2 for h in [5, 6, 7, 8, 12]}
        top_h = max(hs, key=lambda x: hs[x]) if hs else 0
        patterns: Dict[int, Tuple[str, str]] = {
            6:  ("Conflict / Betrayal / Power struggle.",
                 "Resolution through forgiveness; learn not to exploit imbalances."),
            8:  ("Sudden loss / trauma / abandonment. Intense severing without closure.",
                 "Release obsession; find closure through transformation."),
            12: ("Separation / distance / unfinished closure. External forces divided you.",
                 "Complete the emotional loop; mature into surrender without clinging."),
        }
        if top_h in patterns:
            past, purpose = patterns[top_h]
        elif hs.get(5, 0) > 0.6 and hs.get(7, 0) > 0.6:
            past    = "Romantic connection that couldn't complete in a prior cycle."
            purpose = "Fulfil the unlived timeline; build structural support for the bond."
        else:
            past    = "General unfinished business; minor overlaps seeking resolution."
            purpose = "Clear residual attachments; determine if you choose each other in *this* life."

        analysis = (
            f"Karmic Score: {kscore:.2f}  ({'High' if kscore > 0.6 else 'Moderate' if kscore > 0.3 else 'Low'})\n"
            f"Origin: {origin}\nType: {ktype}\nDebt Direction: {debt}\n\n"
            f"Past Pattern: {past}\nCurrent Purpose: {purpose}"
        )
        return LayerCompatibility(
            layer           = RelationshipLayer.KARMIC,
            is_compatible   = kscore < 0.7,
            strength        = round(kscore, 3),
            key_indicators  = key,
            warning_signs   = warn,
            analysis        = analysis,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # DASHA TIMING
    # ═══════════════════════════════════════════════════════════════════════════

    def analyze_relationship_timing(
        self,
        chart: Dict,
        person_name: str = "Person",
    ) -> DashaEventTiming:
        cur_md = chart.get("current_mahadasha", "Unknown")
        cur_ad = chart.get("current_antardasha", "Unknown")
        cur_sd = chart.get("current_pratyantardasha", "Unknown")

        md_h = self._get_planet_house_significations(chart.get("md_lord_planet", 0), chart)
        ad_h = self._get_planet_house_significations(chart.get("ad_lord_planet", 0), chart)
        sd_h = self._get_planet_house_significations(chart.get("sd_lord_planet", 0), chart)
        active = list(set(md_h + ad_h + sd_h))

        def marriage_score(houses: List[int]) -> float:
            return (0.6 * (7 in houses) + 0.2 * (2 in houses) + 0.2 * (11 in houses))

        raw_m = (marriage_score(md_h) * 0.5 +
                 marriage_score(ad_h) * 0.3 +
                 marriage_score(sd_h) * 0.2)

        linked = any(7 in hh and (2 in hh or 11 in hh) for hh in [md_h, ad_h, sd_h])
        m_prob = raw_m if linked else raw_m * 0.4

        def break_score(houses: List[int]) -> float:
            return sum(1 for h in self.DESTRUCTIVE_HOUSES if h in houses) / len(self.DESTRUCTIVE_HOUSES)

        b_risk = (break_score(md_h) * 0.5 +
                  break_score(ad_h) * 0.3 +
                  break_score(sd_h) * 0.2)

        parts = []
        parts.append(f"● {cur_md} Mahadasha: House significance {md_h}")
        parts.append(f"● {cur_ad} Antardasha: House significance {ad_h}")
        if cur_sd != "Unknown":
            parts.append(f"● {cur_sd} Pratyantar: House significance {sd_h}")
        parts.append("")
        
        if m_prob > 0.6:
            parts.append(f"✓ FAVORABLE for marriage. Linkage={'YES' if linked else 'WEAK'}. Score: {m_prob:.2f}")
        elif m_prob > 0.3:
            parts.append(f"~ MODERATE for marriage. Score: {m_prob:.2f}")
        else:
            parts.append(f"✗ UNFAVORABLE for marriage. Marriage Houses (2,7,11) presence too weak ({m_prob:.2f}).")
        
        if b_risk > 0.6:
            parts.append(f"⚠ HIGH breakup risk ({b_risk:.2f}). Destructive houses {self.DESTRUCTIVE_HOUSES} heavily activated.")
        elif b_risk > 0.3:
            parts.append(f"⚠ MODERATE conflict potential ({b_risk:.2f}).")

        return DashaEventTiming(
            current_md           = cur_md,
            current_ad           = cur_ad,
            current_sd           = cur_sd,
            marriage_probability = round(m_prob, 3),
            breakup_risk         = round(b_risk, 3),
            active_houses        = active,
            event_window         = None,
            timing_analysis      = "\n\n".join(parts),
        )

    def _get_planet_house_significations(self, planet_num: int, chart: Dict) -> List[int]:
        sigs: set = set()
        for store in ("house_lords", "star_lords", "cuspal_sub_lords"):
            for h, pid in chart.get(store, {}).items():
                if pid == planet_num:
                    sigs.add(h)
        return list(sigs)

    # ═══════════════════════════════════════════════════════════════════════════
    # VERDICT
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_final_verdict(
        self,
        a_to_b:      SourceResultMatch,
        b_to_a:      SourceResultMatch,
        physical:    LayerCompatibility,
        emotional:   LayerCompatibility,
        karmic:      LayerCompatibility,
        overlays:    List[Tuple[int, int, str]],
        a_timing:    DashaEventTiming,
        b_timing:    DashaEventTiming,
    ) -> CompatibilityVerdict:
        avg_stab  = (a_to_b.stability_score + b_to_a.stability_score) / 2
        imbalance = abs(a_to_b.stability_score - b_to_a.stability_score)
        bi_stab   = avg_stab - imbalance * 0.8
        toxic_asym = imbalance > 0.4
        critical   = any("CRITICAL" in o[2] for o in overlays)
        timing_ok  = (a_timing.marriage_probability > 0.5 and
                      b_timing.marriage_probability > 0.5 and
                      a_timing.breakup_risk < 0.5 and
                      b_timing.breakup_risk < 0.5)
        is_karmic       = karmic.strength > 0.65
        karmic_trap     = is_karmic and bi_stab < 0.45
        karmic_soulmate = is_karmic and emotional.is_compatible and bi_stab > 0.5

        if karmic_trap:     return CompatibilityVerdict.KARMIC_TRAP
        if karmic_soulmate: return CompatibilityVerdict.KARMIC_SOULMATE

        # Destructive Union: ONLY when structural stability is genuinely broken
        # Critical overlays with low stability = truly destructive
        if critical and bi_stab < 0.5:
            return CompatibilityVerdict.DESTRUCTIVE_UNION
        if bi_stab < 0.3:
            return CompatibilityVerdict.DESTRUCTIVE_UNION

        # Challenging but Viable: structural issues exist but fixable
        if critical or bi_stab < 0.45:
            return CompatibilityVerdict.CHALLENGING_BUT_VIABLE

        # Timing Gate: poor timing should NOT produce Destructive Union
        # when structural stability is acceptable
        if not timing_ok:
            if bi_stab > 0.55:
                return CompatibilityVerdict.TIMING_MISMATCH
            return CompatibilityVerdict.CHALLENGING_BUT_VIABLE

        # Sustainable Marriage: strong across all dimensions
        if (physical.is_compatible and emotional.is_compatible
                and bi_stab > 0.6 and len(overlays) <= 2):
            return CompatibilityVerdict.SUSTAINABLE_MARRIAGE

        # High stability with mixed layers
        if bi_stab > 0.6 and (physical.is_compatible or emotional.is_compatible):
            return CompatibilityVerdict.SUSTAINABLE_MARRIAGE

        if physical.is_compatible and not emotional.is_compatible:
            return CompatibilityVerdict.ATTRACTION_ONLY

        if bi_stab > 0.5:
            return CompatibilityVerdict.CHALLENGING_BUT_VIABLE

        return CompatibilityVerdict.INSUFFICIENT_DATA

    # ═══════════════════════════════════════════════════════════════════════════
    # BRUTAL TRUTH, SUMMARIES, RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def _generate_brutal_truth(
        self,
        verdict:   CompatibilityVerdict,
        a_to_b:    SourceResultMatch,
        b_to_a:    SourceResultMatch,
        physical:  LayerCompatibility,
        emotional: LayerCompatibility,
        karmic:    LayerCompatibility,
        overlays:  List[Tuple[int, int, str]],
        a_timing:  DashaEventTiming,
        b_timing:  DashaEventTiming,
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        strengths, weaknesses, deal_breakers, survival = [], [], [], []

        if physical.is_compatible:  strengths.append("Physical attraction exists.")
        if emotional.is_compatible: strengths.append("Emotional connection possible.")
        if a_to_b.stability_score > 0.6: strengths.append("A's needs align with B's delivery.")
        if b_to_a.stability_score > 0.6: strengths.append("B's needs align with A's delivery.")
        if not overlays:            strengths.append("No critical destructive overlays.")

        if not physical.is_compatible:  weaknesses.append("Weak physical attraction.")
        if not emotional.is_compatible: weaknesses.append("Emotional disconnect.")
        if a_to_b.stability_score < 0.4: weaknesses.append("Person A chronically unsatisfied.")
        if b_to_a.stability_score < 0.4: weaknesses.append("Person B chronically unsatisfied.")
        if len(a_to_b.conflict_houses) > 2: weaknesses.append(f"Multiple A→B conflicts: H{a_to_b.conflict_houses}")
        if len(b_to_a.conflict_houses) > 2: weaknesses.append(f"Multiple B→A conflicts: H{b_to_a.conflict_houses}")

        for _, _, exp in overlays:
            if "CRITICAL" in exp: deal_breakers.append(exp)
        if karmic.strength > 0.7:
            deal_breakers.append("Heavy karmic: intensity ≠ love. Most cannot survive this.")
        if a_timing.breakup_risk > 0.7 or b_timing.breakup_risk > 0.7:
            deal_breakers.append("Dasha period highly destructive — even good matches fail.")
        if len(a_to_b.conflict_houses) > 4 and len(b_to_a.conflict_houses) > 4:
            deal_breakers.append("Systematic incompatibility — not fixable by therapy alone.")

        survival_map = {
            CompatibilityVerdict.SUSTAINABLE_MARRIAGE: [
                "Maintain active expectation alignment.", "Monitor dasha transitions proactively."
            ],
            CompatibilityVerdict.ATTRACTION_ONLY: [
                "Accept the physical limit; don't force commitment.", "Seek emotional compatibility elsewhere."
            ],
            CompatibilityVerdict.KARMIC_TRAP: [
                "Intensity ≠ love — maintain this awareness.", "Strong boundaries; exit strategy ready.",
                "Therapy / spiritual guidance essential."
            ],
            CompatibilityVerdict.DESTRUCTIVE_UNION: [
                "STRONG RECOMMENDATION: Avoid or exit.", "If proceeding: legal & financial protections mandatory.",
                "Maintain independent identity at all costs."
            ],
            CompatibilityVerdict.TIMING_MISMATCH: [
                "Wait for both charts to show favorable periods.", "Build foundation now; don't formalize yet."
            ],
            CompatibilityVerdict.CHALLENGING_BUT_VIABLE: [
                "Sustained conscious effort is non-negotiable.", "Couples counselling from the start.",
                "Revisit compatibility every 2–3 years as dashas shift."
            ],
            CompatibilityVerdict.KARMIC_SOULMATE: [
                "Honour the depth; don't take the bond for granted.", "Karmic pull can turn possessive — watch for it.",
                "Grounding practices (shared rituals, therapy) prevent obsession loops."
            ],
        }
        survival = survival_map.get(verdict, ["Proceed with full awareness."])
        return strengths, weaknesses, deal_breakers, survival

    def _generate_executive_summary(
        self,
        a: str, b: str,
        verdict: CompatibilityVerdict,
        stability: float,
        lang: str = "en"
    ) -> str:
        # Stability-level descriptor
        if stability > 0.75:
            stab_desc = f"remarkably strong structural stability ({stability:.2f})"
            stab_word = "STRONG"
        elif stability > 0.6:
            stab_desc = f"solid foundational stability ({stability:.2f})"
            stab_word = "STABLE"
        elif stability > 0.4:
            stab_desc = f"moderate stability with visible cracks ({stability:.2f})"
            stab_word = "MODERATE"
        else:
            stab_desc = f"fragile foundations ({stability:.2f})"
            stab_word = "UNSTABLE"

        # Verdict-specific narrative paragraphs
        narrative_map = {
            CompatibilityVerdict.SUSTAINABLE_MARRIAGE: (
                f"The charts of {a} and {b} tell a story of alignment. Their Source-Result chains "
                f"complement each other — what one promises, the other delivers. Destructive overlays "
                f"are either absent or manageable, and the current dasha timing supports formalisation. "
                f"This does not guarantee happiness — no chart can promise that — but it means the cosmic "
                f"architecture is not working against you. With {stab_desc}, the structural "
                f"foundation is strong enough to weather the storms that every marriage inevitably faces."
            ),
            CompatibilityVerdict.ATTRACTION_ONLY: (
                f"Between {a} and {b}, the physical pull is real — but it is the only thing that is. "
                f"Beneath the surface attraction lies insufficient emotional depth and structural support. "
                f"The bidirectional stability reads {stability:.2f}, which tells a clear story: this "
                f"connection is built for chemistry, not for commitment. Force it into marriage and you "
                f"will discover that desire alone cannot carry the weight of a shared life."
            ),
            CompatibilityVerdict.KARMIC_TRAP: (
                f"The connection between {a} and {b} burns with intensity — but intensity is not love. "
                f"Heavy 8th and 12th house involvement creates a magnetic pull that most people mistake "
                f"for destiny. It is, in fact, karmic debt being serviced through emotional suffering. "
                f"The bidirectional stability at {stability:.2f} confirms that the structural foundations "
                f"cannot support the weight of this obsession. Most people destroy themselves trying to "
                f"make this work. The few who survive do so by redefining the relationship entirely."
            ),
            CompatibilityVerdict.KARMIC_SOULMATE: (
                f"What exists between {a} and {b} is rare and powerful — an intense karmic bond "
                f"anchored by genuine emotional and structural resonance. The connection is real, the "
                f"pull is authentic, and the foundation (stability: {stability:.2f}) can support it. "
                f"But every karmic soulmate pairing carries a shadow: the same intensity that creates "
                f"breathtaking intimacy can, unchecked, turn into possessive obsession. Conscious "
                f"practice and mutual respect are not optional — they are the price of admission."
            ),
            CompatibilityVerdict.DESTRUCTIVE_UNION: (
                f"The forensic analysis of {a} and {b}'s charts reveals critical structural fractures. "
                f"This is not a relationship that struggles — it is one that actively damages both parties. "
                f"With bidirectional stability at {stability:.2f}, the architecture predicts escalating "
                f"conflict: legal battles, financial destruction, emotional devastation, or all three. "
                f"This cannot be fixed by trying harder, loving more, or waiting longer."
            ),
            CompatibilityVerdict.TIMING_MISMATCH: (
                f"The structural compatibility between {a} and {b} is not the problem — the timing is. "
                f"With {stab_desc}, the foundation is sound, but the current dasha periods "
                f"are misaligned. One or both charts are in a life phase that does not support partnership "
                f"formalisation. Force it now and you create unnecessary problems from a match that could "
                f"work beautifully in a different season. Patience is the strategic choice."
            ),
            CompatibilityVerdict.CHALLENGING_BUT_VIABLE: (
                f"The charts of {a} and {b} do not tell a simple story. Significant friction exists — "
                f"mismatches in emotional wavelength, timing pressures, or layer incompatibilities create "
                f"real obstacles. But with {stab_desc}, there are no absolute structural "
                f"deal-breakers. Success is possible, but it demands sustained, conscious effort from "
                f"both parties. Enter with clear eyes: this relationship will require more work than most, "
                f"and the work never fully stops."
            ),
            CompatibilityVerdict.INSUFFICIENT_DATA: (
                f"The chart data for {a} and {b} is incomplete or the pattern too ambiguous for "
                f"definitive classification. Additional analysis with verified birth data is recommended."
            ),
        }

        desc = narrative_map.get(verdict, "")
        v_val = t(verdict.value, lang)
        bi_title = t("Bidirectional Stability", lang)

        W = "═" * 79
        return (
            f"{desc}\n\n"
            f"{bi_title}: {stability:.2f}/1.00  [{stab_word}]"
        )

    def _generate_detailed_report(
        self,
        a: str, b: str,
        verdict: CompatibilityVerdict,
        a_to_b: SourceResultMatch,
        b_to_a: SourceResultMatch,
        physical: LayerCompatibility,
        emotional: LayerCompatibility,
        karmic: LayerCompatibility,
        overlays: List[Tuple[int, int, str]],
        a_timing: DashaEventTiming,
        b_timing: DashaEventTiming,
        strengths: List[str],
        weaknesses: List[str],
        deal_breakers: List[str],
    ) -> str:
        lang = getattr(self, 'language', 'en')
        W = "═" * 79
        sections = []

        q_t = t("Quality", lang)
        s_t = t("Score", lang)
        dir_t = t("Direction", lang)
        
        sections.append(
            f"{W}\n1. {t('SOURCE-RESULT CROSS-MATCHING', lang)}\n{W}\n\n"
            f"{dir_t}: {a} → {b}\n"
            f"{q_t}: {a_to_b.match_quality.value}  |  {s_t}: {a_to_b.stability_score:.2f}\n"
            f"{a_to_b.detailed_analysis}\n\n---\n\n"
            f"{dir_t}: {b} → {a}\n"
            f"{q_t}: {b_to_a.match_quality.value}  |  {s_t}: {b_to_a.stability_score:.2f}\n"
            f"{b_to_a.detailed_analysis}"
        )

        sections.append(
            f"{W}\n2. {t('MULTI-LAYER COMPATIBILITY', lang)}\n{W}\n\n"
            f"A) {t('PHYSICAL', lang)}  Status: {'✓' if physical.is_compatible else '✗'}  "
            f"Strength: {physical.strength:.2f}\n{physical.analysis}\n\n"
            f"B) {t('EMOTIONAL', lang)} Status: {'✓' if emotional.is_compatible else '✗'}  "
            f"Strength: {emotional.strength:.2f}\n{emotional.analysis}\n\n"
            f"C) {t('KARMIC', lang)}    Intensity: {karmic.strength:.2f}\n{karmic.analysis}"
        )

        overlay_txt = "\n".join(f"• {e}" for _, _, e in overlays) if overlays else f"✓ {t('None detected.', lang)}"
        sections.append(f"{W}\n3. {t('DESTRUCTIVE OVERLAYS', lang)}\n{W}\n\n{overlay_txt}")

        m_prob = t("Marriage prob", lang)
        b_risk = t("Breakup risk", lang)
        sections.append(
            f"{W}\n4. {t('DASHA TIMING', lang)}\n{W}\n\n"
            f"{a}: MD={a_timing.current_md} AD={a_timing.current_ad}  "
            f"{m_prob}={a_timing.marriage_probability:.0%}  {b_risk}={a_timing.breakup_risk:.0%}\n"
            f"{a_timing.timing_analysis}\n\n---\n\n"
            f"{b}: MD={b_timing.current_md} AD={b_timing.current_ad}  "
            f"{m_prob}={b_timing.marriage_probability:.0%}  {b_risk}={b_timing.breakup_risk:.0%}\n"
            f"{b_timing.timing_analysis}"
        )

        def bullet(lst): return "\n".join(f"• {x}" for x in lst) if lst else f"• {t('None.', lang)}"
        sections.append(
            f"{W}\n5. {t('BRUTAL TRUTH', lang)}\n{W}\n\n"
            f"{t('STRENGTHS', lang)}:\n{bullet(strengths)}\n\n"
            f"{t('WEAKNESSES', lang)}:\n{bullet(weaknesses)}\n\n"
            f"{t('DEAL-BREAKERS', lang)}:\n{bullet(deal_breakers)}"
        )

        return "\n\n".join(sections)

    def _generate_recommendations(
        self,
        verdict: CompatibilityVerdict,
        strengths: List[str],
        weaknesses: List[str],
        deal_breakers: List[str],
    ) -> List[str]:
        rec_map = {
            CompatibilityVerdict.SUSTAINABLE_MARRIAGE: [
                "Proceed with formalization when both are ready.",
                "Regular expectation alignment check-ins.",
                "Build support systems for difficult dasha transitions.",
                "Don't take stability for granted.",
            ],
            CompatibilityVerdict.ATTRACTION_ONLY: [
                "Keep casual; do not force commitment.",
                "Be honest — don't manufacture false expectations.",
                "Seek emotional compatibility elsewhere for long-term goals.",
            ],
            CompatibilityVerdict.KARMIC_TRAP: [
                "PROCEED WITH EXTREME CAUTION.",
                "Professional therapy from day one.",
                "Strong personal boundaries; clear exit strategy.",
                "Intensity is not the same as healthy love — repeat this daily.",
            ],
            CompatibilityVerdict.KARMIC_SOULMATE: [
                "Honour the depth; formalize when timing aligns.",
                "Watch for obsessive patterns — address early.",
                "Grounding rituals and shared practices essential.",
            ],
            CompatibilityVerdict.DESTRUCTIVE_UNION: [
                "STRONG RECOMMENDATION: Do not proceed.",
                "If already involved: develop exit strategy now.",
                "Legal and financial protections mandatory if proceeding.",
            ],
            CompatibilityVerdict.TIMING_MISMATCH: [
                "Wait for both charts to show favorable periods.",
                "Use current phase for foundation-building, not commitment.",
                "Re-evaluate timing every 6 months.",
            ],
            CompatibilityVerdict.CHALLENGING_BUT_VIABLE: [
                "Enter with clear eyes — this will require sustained work.",
                "Couples counselling before and after marriage.",
                "Revisit compatibility as dashas shift every 2–3 years.",
            ],
        }
        return rec_map.get(verdict, ["Proceed with full awareness and professional guidance."])

    def _calculate_overall_score(
        self,
        bi_stab: float,
        physical: LayerCompatibility,
        emotional: LayerCompatibility,
        karmic: LayerCompatibility,
    ) -> float:
        return round(min(1.0, max(0.0,
            bi_stab          * 0.40 +
            physical.strength  * 0.20 +
            emotional.strength * 0.25 +
            (1.0 - karmic.strength) * 0.15
        )), 3)

    def _generate_timing_verdict(self, a: DashaEventTiming, b: DashaEventTiming) -> str:
        if a.marriage_probability > 0.5 and b.marriage_probability > 0.5 and \
           a.breakup_risk < 0.6 and b.breakup_risk < 0.6:
            return "FAVORABLE — Both charts support formalization."
        if a.breakup_risk > 0.6 or b.breakup_risk > 0.6:
            return "DANGEROUS — High breakup risk in one or both charts."
        return "UNFAVORABLE — Timing not supportive for commitment."

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN ORCHESTRATION
    # ═══════════════════════════════════════════════════════════════════════════

    def analyze_couple_compatibility(
        self,
        person_a_name: str,
        person_b_name: str,
        person_a_chart: Dict,
        person_b_chart: Dict,
        include_raw_data: bool = False,
        marriage_year: Optional[int] = None,
        post_marriage_scan_years: int = 15,
    ) -> CoupleMatchReport:
        """
        Main entry point.

        Parameters
        ──────────
        person_a_name           : Groom / partner A name
        person_b_name           : Bride / partner B name
        person_a_chart          : Complete UAKP chart dict for A
        person_b_chart          : Complete UAKP chart dict for B
        include_raw_data        : Include raw chart dicts in report
        marriage_year           : Year of marriage for post-marriage scan.
                                  Defaults to current year if verdict supports marriage.
        post_marriage_scan_years: How many years to scan (default 15)

        Returns
        ───────
        CoupleMatchReport — complete analysis including post-marriage dasha
        if verdict is in {SUSTAINABLE_MARRIAGE, KARMIC_SOULMATE,
        CHALLENGING_BUT_VIABLE, TIMING_MISMATCH}.
        """
        # Step 0 — Normalize V11 data
        person_a_chart = self._normalize_v11_data(person_a_chart)
        person_b_chart = self._normalize_v11_data(person_b_chart)

        # Step 1 — House analysis
        a_houses = {h: self.analyze_relationship_house(h, person_a_chart, "a") for h in range(1, 13)}
        b_houses = {h: self.analyze_relationship_house(h, person_b_chart, "b") for h in range(1, 13)}

        # Step 2 — Cross-matching
        a_to_b = self.cross_match_source_result(person_a_chart, person_b_chart, "a_to_b")
        b_to_a = self.cross_match_source_result(person_a_chart, person_b_chart, "b_to_a")
        bi_stab = (a_to_b.stability_score + b_to_a.stability_score) / 2

        # Step 3 — Destructive overlays
        overlays = self.detect_destructive_overlays(a_houses, b_houses)

        # Step 4 — Layers
        physical  = self.assess_physical_layer(person_a_chart, person_b_chart, a_houses, b_houses)
        emotional = self.assess_emotional_layer(person_a_chart, person_b_chart, a_houses, b_houses)
        karmic    = self.assess_karmic_layer(
            person_a_chart, person_b_chart, a_houses, b_houses,
            a_to_b.stability_score, b_to_a.stability_score,
            person_a_name, person_b_name,
        )

        # Step 5 — Timing
        a_timing = self.analyze_relationship_timing(person_a_chart, person_a_name)
        b_timing = self.analyze_relationship_timing(person_b_chart, person_b_name)

        # Step 6 — Verdict
        verdict = self.generate_final_verdict(
            a_to_b, b_to_a, physical, emotional, karmic, overlays, a_timing, b_timing
        )

        # Step 7 — Brutal truth
        strengths, weaknesses, deal_breakers, survival = self._generate_brutal_truth(
            verdict, a_to_b, b_to_a, physical, emotional, karmic, overlays, a_timing, b_timing
        )

        
        # EXTRACT LANGUAGE FROM CHART METADATA OR DEFAULT TO EN
        self.language = person_a_chart.get('metadata', {}).get('language', 'en')
        
        # Step 8 — Reports
        exec_summary = self._generate_executive_summary(person_a_name, person_b_name, verdict, bi_stab, lang=self.language)
        detail_report = self._generate_detailed_report(
            person_a_name, person_b_name, verdict,
            a_to_b, b_to_a, physical, emotional, karmic,
            overlays, a_timing, b_timing,
            strengths, weaknesses, deal_breakers,
        )
        recommendations = self._generate_recommendations(verdict, strengths, weaknesses, deal_breakers)
        overall_score   = self._calculate_overall_score(bi_stab, physical, emotional, karmic)
        timing_verdict  = self._generate_timing_verdict(a_timing, b_timing)

        # Step 9 — POST-MARRIAGE DASHA ANALYSIS (v2.0)
        post_marriage_dasha: Optional[PostMarriageDashaReport] = None

        if verdict in self.MARRIAGE_VERDICTS:
            m_year = marriage_year or datetime.now().year
            try:
                pm_engine = PostMarriageDashaEngine(
                    groom_chart = person_a_chart,
                    bride_chart  = person_b_chart,
                    groom_name   = person_a_name,
                    bride_name   = person_b_name,
                )
                post_marriage_dasha = pm_engine.generate(
                    marriage_year  = m_year,
                    scan_years     = post_marriage_scan_years,
                )
            except Exception as e:
                # Non-fatal: report proceeds without post-marriage data
                post_marriage_dasha = None

        return CoupleMatchReport(
            person_a_name                = person_a_name,
            person_b_name                = person_b_name,
            generation_date              = datetime.now(),
            verdict                      = verdict,
            overall_score                = overall_score,
            a_to_b_match                 = a_to_b,
            b_to_a_match                 = b_to_a,
            bidirectional_stability      = round(bi_stab, 3),
            physical_layer               = physical,
            emotional_layer              = emotional,
            karmic_layer                 = karmic,
            person_a_relationship_houses = a_houses,
            person_b_relationship_houses = b_houses,
            destructive_overlays         = overlays,
            person_a_timing              = a_timing,
            person_b_timing              = b_timing,
            relationship_timing_verdict  = timing_verdict,
            strengths                    = strengths,
            critical_weaknesses          = weaknesses,
            deal_breakers                = deal_breakers,
            survival_requirements        = survival,
            executive_summary            = exec_summary,
            detailed_report              = detail_report,
            recommendations              = recommendations,
            post_marriage_dasha          = post_marriage_dasha,
            person_a_chart_data          = person_a_chart if include_raw_data else None,
            person_b_chart_data          = person_b_chart if include_raw_data else None,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def export_report_to_json(report: CoupleMatchReport, filepath: str) -> None:
    """Export the report to a JSON file."""
    def pm_phase_to_dict(p: MarriagePhase) -> Dict:
        return {
            "year_label":    p.year_label,
            "groom_md":      p.groom_md,
            "groom_ad":      p.groom_ad,
            "bride_md":      p.bride_md,
            "bride_ad":      p.bride_ad,
            "groom_houses":  p.groom_houses,
            "bride_houses":  p.bride_houses,
            "phase_type":    p.phase_type.value,
            "harmony_score": p.harmony_score,
            "conflict_score":p.conflict_score,
            "highlights":    p.highlights,
            "guidance":      p.guidance,
        }

    pm: Optional[Dict] = None
    if report.post_marriage_dasha:
        pm_r = report.post_marriage_dasha
        pm = {
            "groom_name":         pm_r.groom_name,
            "bride_name":         pm_r.bride_name,
            "marriage_year":      pm_r.marriage_year,
            "scan_years":         pm_r.scan_years,
            "golden_phases":      pm_r.golden_phases,
            "danger_zones":       pm_r.danger_zones,
            "childbirth_windows": pm_r.childbirth_windows,
            "peak_harmony_year":  pm_r.peak_harmony_year,
            "peak_risk_year":     pm_r.peak_risk_year,
            "executive_summary":  pm_r.executive_summary,
            "phases": [pm_phase_to_dict(p) for p in pm_r.phases],
        }

    out = {
        "person_a_name":            report.person_a_name,
        "person_b_name":            report.person_b_name,
        "generation_date":          report.generation_date.isoformat(),
        "verdict":                  report.verdict.value,
        "overall_score":            report.overall_score,
        "bidirectional_stability":  report.bidirectional_stability,
        "executive_summary":        report.executive_summary,
        "detailed_report":          report.detailed_report,
        "strengths":                report.strengths,
        "critical_weaknesses":      report.critical_weaknesses,
        "deal_breakers":            report.deal_breakers,
        "survival_requirements":    report.survival_requirements,
        "recommendations":          report.recommendations,
        "post_marriage_dasha":      pm,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


def print_report_summary(report: CoupleMatchReport) -> None:
    """Print the complete report to console."""
    W = "═" * 79
    print(report.executive_summary)
    print("\n")
    print(report.detailed_report)

    print(f"\n\n{W}\nSURVIVAL REQUIREMENTS\n{W}")
    for r in report.survival_requirements:
        print(f"• {r}")

    print(f"\n{W}\nRECOMMENDATIONS\n{W}")
    for r in report.recommendations:
        print(f"• {r}")

    # ── POST-MARRIAGE DASHA ──────────────────────────────────────────────────
    pm = report.post_marriage_dasha
    if pm:
        print(f"\n\n{W}")
        print("POST-MARRIAGE DASHA TIMELINE")
        print(f"{W}\n")
        print(pm.executive_summary)
        print(f"\n{'-'*79}")
        print(f"{'YEAR':<22} {'GROOM MD/AD':<22} {'BRIDE MD/AD':<22} {'PHASE':<24} {'H':<6} {'C':<6}")
        print("-" * 79)
        for p in pm.phases:
            g_dash = f"{p.groom_md}/{p.groom_ad}"
            b_dash = f"{p.bride_md}/{p.bride_ad}"
            print(
                f"{p.year_label:<22} {g_dash:<22} {b_dash:<22} "
                f"{p.phase_type.value:<24} {p.harmony_score:<6.2f} {p.conflict_score:<6.2f}"
            )
        print(f"\n{'-'*79}\nDETAILED PHASE NARRATIVES\n{'-'*79}")
        for p in pm.phases:
            print(f"\n▸ {p.year_label}  [{p.phase_type.value}]")
            print(f"  Groom: {p.groom_md} MD / {p.groom_ad} AD  → Houses {p.groom_houses}")
            print(f"  Bride : {p.bride_md} MD / {p.bride_ad} AD  → Houses {p.bride_houses}")
            for hl in p.highlights:
                print(f"  ★ {hl}")
            print(f"  ✦ Guidance: {p.guidance}")
        print(f"\n{W}")


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
═══════════════════════════════════════════════════════════════════════════════
TITENIUM AI — COUPLE MATCHMAKING  (UAKP Method)  v2.0
═══════════════════════════════════════════════════════════════════════════════

Requires chart data from the UAKP calculation engine.

Usage:
    analyzer = UakpCoupleAnalyzer()
    report = analyzer.analyze_couple_compatibility(
        person_a_name           = "Groom Name",
        person_b_name           = "Bride Name",
        person_a_chart          = chart_data_groom,
        person_b_chart          = chart_data_bride,
        marriage_year           = 2025,          # optional; defaults to current year
        post_marriage_scan_years= 20,            # optional; default 15
    )
    print_report_summary(report)

    # If report.post_marriage_dasha is not None, full timeline is available.
    # export_report_to_json(report, "output.json")

Chart data must contain:
  - house_lords          : {1: planet_id, …, 12: planet_id}
  - cuspal_sub_lords     : {1: planet_id, …, 12: planet_id}
  - star_lords           : {1: planet_id, …, 12: planet_id}
  - planets              : {planet_id: {is_exalted, is_own_sign, is_debilitated, …}}
  - planet_significators : [{planet, Result_Row, Source_Row}, …]
  - vimshottari_dasa_full: [{lord, start, end, sub_periods:[{lord,start,end}]}, …]
  - current_mahadasha / current_antardasha / current_pratyantardasha
  - md_lord_planet / ad_lord_planet / sd_lord_planet

═══════════════════════════════════════════════════════════════════════════════
""")