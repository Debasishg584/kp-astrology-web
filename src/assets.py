# src/assets.py

"""
KP Astrology Asset Manager
Theme: Geruya (Saffron/Spiritual Orange)
"""

# ==========================================
# 1. THEME CONFIGURATION (GERUYA / SAFFRON)
# ==========================================
THEME = {
    "app_bg": "#FFF3E0",       # Light Saffron Cream (Main Background)
    "panel_bg": "#FFE0B2",     # Soft Orange (Input Panels)
    "header_bg": "#FF9800",    # Deep Gerua (Header Banner)
    "header_fg": "#FFFFFF",    # White Text
    "button_bg": "#EF6C00",    # Dark Saffron (Buttons)
    "button_fg": "#FFFFFF",    # White Button Text
    "button_active": "#E65100",# Darker Orange on Hover
    "chart_bg": "#FFFFFF",     # Pure White Chart Background for contrast
    "chart_lines": "#5D4037",  # Dark Brown lines (looks good with Saffron)
    "highlight": "#D84315",    # Red-Orange highlight
    "text_main": "#3E2723"     # Dark Coffee Text
}

FONTS = {
    "zodiac_symbol": ("Segoe UI Symbol", 14, "bold"), 
    "planet_symbol": ("Segoe UI Symbol", 15, "bold"),
    "cusp_text":     ("Arial", 9, "bold"),
    "label":         ("Arial", 9),
    "header":        ("Arial", 12, "bold"),
    "button":        ("Arial", 10, "bold")
}

# ==========================================
# 2. ZODIAC SIGNS (Colorful Backgrounds)
# ==========================================
ZODIAC_DATA = {
    "Aries":       {"symbol": "♈", "color": "#FFCDD2"}, # Red tint
    "Taurus":      {"symbol": "♉", "color": "#C8E6C9"}, # Green tint
    "Gemini":      {"symbol": "♊", "color": "#BBDEFB"}, # Blue tint
    "Cancer":      {"symbol": "♋", "color": "#F8BBD0"}, # Pink tint
    "Leo":         {"symbol": "♌", "color": "#FFE0B2"}, # Orange tint
    "Virgo":       {"symbol": "♍", "color": "#DCEDC8"}, # Earth tint
    "Libra":       {"symbol": "♎", "color": "#E1BEE7"}, # Air tint
    "Scorpio":     {"symbol": "♏", "color": "#EF9A9A"}, # Mars tint
    "Sagittarius": {"symbol": "♐", "color": "#FFF9C4"}, # Jupiter tint
    "Capricorn":   {"symbol": "♑", "color": "#CFD8DC"}, # Saturn tint
    "Aquarius":    {"symbol": "♒", "color": "#B2EBF2"}, # Saturn/Air tint
    "Pisces":      {"symbol": "♓", "color": "#D1C4E9"}, # Jupiter tint
}

# ==========================================
# 3. PLANETS (Real Unicode Symbols)
# ==========================================
PLANET_DATA = {
    "Sun":     {"symbol": "☉", "color": "#D50000"}, # Red
    "Moon":    {"symbol": "☾", "color": "#000000"}, # Black
    "Mars":    {"symbol": "♂", "color": "#B71C1C"}, # Dark Red
    "Mercury": {"symbol": "☿", "color": "#2E7D32"}, # Dark Green
    "Jupiter": {"symbol": "♃", "color": "#F57F17"}, # Gold/Orange
    "Venus":   {"symbol": "♀", "color": "#C2185B"}, # Magenta
    "Saturn":  {"symbol": "♄", "color": "#212121"}, # Black
    "Rahu":    {"symbol": "☊", "color": "#4A148C"}, # Indigo
    "Ketu":    {"symbol": "☋", "color": "#3E2723"}, # Brown
    "Uranus":  {"symbol": "♅", "color": "#0277BD"},
    "Neptune": {"symbol": "♆", "color": "#4527A0"},
    "Pluto":   {"symbol": "♇", "color": "#263238"},
}