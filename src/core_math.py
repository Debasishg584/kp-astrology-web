# src/core_math.py
import math

# --- Constants ---
J2000 = 2451545.0
EPSILON = 23.439291 

# KP Constants
NAKSHATRA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# --- Utilities ---
def normalize_angle(angle):
    angle = angle % 360
    return angle + 360 if angle < 0 else angle

def decimal_to_dms(decimal_deg):
    d = int(decimal_deg)
    m_full = abs(decimal_deg - d) * 60
    m = int(m_full)
    s = int((m_full - m) * 60)
    return d, m, s

# --- Calculations ---
def calculate_julian_day(year, month, day, hour, minute, second, timezone_offset):
    if month <= 2: year -= 1; month += 12
    A = int(year / 100); B = 2 - A + int(A / 4)
    day_frac = day + (hour + minute/60.0 + second/3600.0) / 24.0
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day_frac + B - 1524.5 - (timezone_offset / 24.0)
    return jd

def calculate_gmst(jd):
    jd_0 = math.floor(jd - 0.5) + 0.5
    T = (jd_0 - J2000) / 36525.0
    gmst_0 = 6.697374558 + (2400.051336 * T) + (0.000025862 * T**2)
    gmst_0 = gmst_0 % 24
    ut_hours = (jd - jd_0) * 24.0
    gmst = gmst_0 + (ut_hours * 1.00273790935)
    return normalize_angle(gmst * 15)

def calculate_lst(gmst_deg, longitude):
    return normalize_angle(gmst_deg + longitude)

def calculate_kp_ayanamsa(year, month, day):
    """
    Calculate KP Ayanamsa.
    Attempt dynamic swisseph import and get true Krishnamurti Ayanamsa.
    Otherwise fall back to corrected linear KP formula.
    """
    try:
        import swisseph as swe
        if hasattr(swe, 'set_sid_mode'):
            # Calculate Julian Day for midday UT to get daily ayanamsa
            jd = swe.julday(year, month, day, 12.0)
            swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
            return float(swe.get_ayanamsa_ut(jd))
    except Exception:
        pass

    # Corrected linear KP formula fallback:
    # J2000 value ~23.760240, precession ~50.2388475" per year
    days_in_year = 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
    dec_year = year + (month - 1) / 12 + (day - 1) / days_in_year
    return 23.760240 + (dec_year - 2000) * (50.2388475 / 3600.0)

def get_placidus_cusps(lst, latitude):
    """
    Calculate House Cusps.
    Primary: MC and Ascendant using rigorous trigonometry.
    Secondary: Intermediate cusps using Porphyry system (standard fallback).
    
    Note: Full Placidus iteration is complex and unstable without a solver.
    Porphyry is a robust and historically accepted alternative when 
    rigorous Placidus is unavailable.
    """
    cusps = {}
    ramc = math.radians(lst)
    lat_rad = math.radians(latitude)
    obl_rad = math.radians(EPSILON)

    # 1. Calculate MC (Midheaven) - Cusp 10
    # Formula: tan(MC) = tan(RAMC) / cos(epsilon)
    # y = sin(RAMC), x = cos(RAMC) * cos(epsilon)
    mc_rad = math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(obl_rad))
    mc_deg = normalize_angle(math.degrees(mc_rad))
    cusps[10] = mc_deg
    cusps[4] = normalize_angle(mc_deg + 180)

    # 2. Calculate Ascendant (Lagna) - Cusp 1
    # Formula: tan(Asc) = cos(RAMC) / -(sin(RAMC)*cos(eps) + tan(lat)*sin(eps))
    top = math.cos(ramc)
    bottom = - ((math.sin(ramc) * math.cos(obl_rad)) + (math.tan(lat_rad) * math.sin(obl_rad)))
    asc_rad = math.atan2(top, bottom)
    asc_deg = normalize_angle(math.degrees(asc_rad))
    cusps[1] = asc_deg
    cusps[7] = normalize_angle(asc_deg + 180)

    # 3. Intermediate Cusps (Porphyry System)
    # Trisect the quadrants formed by MC and Ascendant
    
    # Quadrant 1: Cusp 10 to Cusp 1
    span_10_1 = (cusps[1] - cusps[10]) % 360
    cusps[11] = normalize_angle(cusps[10] + span_10_1 / 3.0)
    cusps[12] = normalize_angle(cusps[10] + 2 * span_10_1 / 3.0)

    # Quadrant 2: Cusp 1 to Cusp 4
    span_1_4 = (cusps[4] - cusps[1]) % 360
    cusps[2] = normalize_angle(cusps[1] + span_1_4 / 3.0)
    cusps[3] = normalize_angle(cusps[1] + 2 * span_1_4 / 3.0)

    # Opposite Houses
    cusps[5] = normalize_angle(cusps[11] + 180)
    cusps[6] = normalize_angle(cusps[12] + 180)
    cusps[8] = normalize_angle(cusps[2] + 180)
    cusps[9] = normalize_angle(cusps[3] + 180)

    return cusps

def get_sub_lord_info(longitude):
    nak_span = 13.333333333333334
    nak_index = int(longitude / nak_span) % 27
    nak_name = NAKSHATRAS[nak_index]
    star_lord = NAKSHATRA_LORDS[nak_index % 9]
    
    deg_in_sec = (longitude - (int(longitude / nak_span) * nak_span)) * 3600
    curr_idx = nak_index % 9
    acc = 0.0
    sub_lord = star_lord
    
    for _ in range(9):
        p = NAKSHATRA_LORDS[curr_idx % 9]
        span = (DASA_YEARS[p] / 120.0) * 48000.0
        if deg_in_sec < (acc + span - 0.01):
            sub_lord = p; break
        acc += span; curr_idx += 1
    return nak_name, star_lord, sub_lord