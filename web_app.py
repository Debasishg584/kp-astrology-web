import os
import sys
from unittest.mock import MagicMock

# Headless mock for Tkinter to allow running GUI-dependent code on a server
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['tkinter.commondialog'] = MagicMock()
sys.modules['tkinter.font'] = MagicMock()
sys.modules['_tkinter'] = MagicMock()


# Dynamically add path to load Swiss Ephemeris and engine libraries
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, "main.py")):
    PROD_PATH = BASE_DIR
else:
    PROD_PATH = r"E:\kp_astrology_softwarer_final(gravity)"

if PROD_PATH not in sys.path:
    sys.path.insert(0, PROD_PATH)
    sys.path.insert(0, os.path.join(PROD_PATH, "src"))

import datetime
from flask import Flask, request, jsonify, send_from_directory

# Guarded imports from production codebase
try:
    from main import ChartEngine, AppMode
    from src.predictions import KPPredictor, KP_RULES
    from src.titanium_ai import MarriageWidowedForensics
    from src.swisseph_backend import SwissEphBackend
    ENGINE_LOADED = True
except ImportError as exc:
    ENGINE_LOADED = False
    _IMPORT_ERROR = str(exc)

# Centralized Swiss Ephemeris path initialization
if ENGINE_LOADED:
    try:
        import swisseph as swe
        # Point swisseph to ephemeris folder
        swe.set_ephe_path(os.path.join(PROD_PATH, "ephe"))
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    except Exception:
        pass


app = Flask(__name__, static_folder="frontend/dist", static_url_path="")
app.secret_key = "divya_drishti_secret_key_987654"

def translate_planet(name, lang=None):
    clean_name = str(name).strip()
    key = f"p_{clean_name}"
    from src.translations import t
    res = t(key, lang=lang)
    return res if res != key else name

def translate_sign_name(name, lang=None):
    clean_name = str(name).strip()
    from src.translations import translate_sign
    return translate_sign(clean_name, lang=lang)

def translate_nakshatra(name, lang=None):
    clean_name = str(name).strip().replace(" ", "")
    key = f"nak_{clean_name}"
    from src.translations import t
    res = t(key, lang=lang)
    return res if res != key else name

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    if not ENGINE_LOADED:
        return jsonify({"error": f"Failed to load astrology engine: {_IMPORT_ERROR}"}), 500
        
    data = request.get_json() or {}
    name = data.get('name', 'Anonymous')
    birth_date = data.get('birth_date', '')
    birth_time = data.get('birth_time', '')
    try:
        lat = float(data.get('latitude', '0.0'))
        lon = float(data.get('longitude', '0.0'))
    except (ValueError, TypeError):
        lat, lon = 0.0, 0.0
    tz = data.get('timezone', '+05:30')
    lang = data.get('lang', 'en')
    
    # Use production ChartEngine to perform calculations
    engine = ChartEngine()
    try:
        p1 = engine._calculate_one(birth_date, birth_time, lat, lon, tz, AppMode.BIRTH)
        exported = engine.build_export(p1)
    except Exception as e:
        return jsonify({"error": f"Calculation Error: {str(e)}"}), 400
        
    # Calculate Rasi and Bhava Chalit placements for visual chart drawing
    SIGN_NAMES = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    asc_sign = exported['house_cusps'][0]['sign']
    asc_sign_idx = SIGN_NAMES.index(asc_sign) + 1 if asc_sign in SIGN_NAMES else 1

    rasi_occupancy = {}
    for p in exported['planetary_positions']:
        p_name = p['planet']
        p_sign = p['sign']
        if p_sign in SIGN_NAMES:
            rasi_occupancy[p_name] = SIGN_NAMES.index(p_sign) + 1
        else:
            rasi_occupancy[p_name] = 1

    bhava_occupancy = {}
    try:
        bh = engine.calc.get_bhavasphuta_significators(p1["planets"], p1["cusps"])
        for p, details in bh.items():
            bhava_occupancy[p] = int(details.get("P_Occ", "1"))
    except Exception:
        # Fallback to rasi house if Bhava Chalit fails
        for p_name, sign_idx in rasi_occupancy.items():
            bhava_occupancy[p_name] = (sign_idx - asc_sign_idx) % 12 + 1

    cusp_sign_indices = []
    for c in exported['house_cusps']:
        c_sign = c['sign']
        cusp_sign_indices.append(SIGN_NAMES.index(c_sign) + 1 if c_sign in SIGN_NAMES else 1)

    # Let's perform backend translation of variables so React gets fully-translated data
    from src.translations import t, convert_number
    
    # Translate planetary positions
    translated_planets = []
    for p in exported['planetary_positions']:
        translated_planets.append({
            'planet': translate_planet(p['planet'], lang=lang),
            'longitude': p['longitude'],
            'longitude_dms': convert_number(p['longitude_dms'], lang=lang),
            'sign': translate_sign_name(p['sign'], lang=lang),
            'nakshatra': translate_nakshatra(p['nakshatra'], lang=lang),
            'star_lord': translate_planet(p['star_lord'], lang=lang),
            'sub_lord': translate_planet(p['sub_lord'], lang=lang)
        })
        
    # Translate house cusps
    translated_cusps = []
    for c in exported['house_cusps']:
        translated_cusps.append({
            'cusp': convert_number(c['cusp'], lang=lang),
            'longitude': c['longitude'],
            'longitude_dms': convert_number(c['longitude_dms'], lang=lang),
            'sign': translate_sign_name(c['sign'], lang=lang),
            'sign_lord': translate_planet(c['sign_lord'], lang=lang),
            'star_lord': translate_planet(c['star_lord'], lang=lang),
            'sub_lord': translate_planet(c['sub_lord'], lang=lang)
        })
        
    # Translate planet significators
    translated_significators = []
    for s in exported['planet_significators']:
        translated_significators.append({
            'planet': translate_planet(s['planet'], lang=lang),
            'Source_Row': convert_number(s['Source_Row'], lang=lang),
            'Result_Row': convert_number(s['Result_Row'], lang=lang)
        })

    # Prepare response data
    response_data = {
        'name': name,
        'birth_date': convert_number(birth_date, lang=lang),
        'birth_time': convert_number(birth_time, lang=lang),
        'latitude': convert_number(str(lat), lang=lang),
        'longitude': convert_number(str(lon), lang=lang),
        'timezone': convert_number(tz, lang=lang),
        'chart': {
            'planetary_positions': translated_planets,
            'house_cusps': translated_cusps,
            'planet_significators': translated_significators
        },
        'asc_sign_idx': asc_sign_idx,
        'rasi_occupancy': rasi_occupancy,
        'bhava_occupancy': bhava_occupancy,
        'cusp_sign_indices': cusp_sign_indices,
        # Pass translated text for all translation keys of interest
        'translations': {
            'app_title': t('app_title', lang=lang),
            'report_birth_summary': t('report_birth_summary', lang=lang),
            'name_label': t('name', lang=lang),
            'dob_label': t('dob_label', lang=lang),
            'tob_label': t('tob_label', lang=lang),
            'lat_label': t('lat_label', lang=lang),
            'lon_label': t('lon_label', lang=lang),
            'tz_label': t('tz_label', lang=lang),
            'report_visual_kundli': t('report_visual_kundli', lang=lang),
            'report_north_diamond': t('report_north_diamond', lang=lang),
            'report_south_box': t('report_south_box', lang=lang),
            'report_rasi_chart': t('report_rasi_chart', lang=lang),
            'report_bhava_chart': t('report_bhava_chart', lang=lang),
            'report_planet_pos': t('report_planet_pos', lang=lang),
            'report_house_cusp': t('report_house_cusp', lang=lang),
            'report_planet_sig': t('report_planet_sig', lang=lang),
            'col_planet': t('col_planet', lang=lang),
            'col_longitude': t('col_longitude', lang=lang),
            'col_sign': t('col_sign', lang=lang),
            'col_nakshatra': t('col_nakshatra', lang=lang),
            'col_star_lord': t('col_star_lord', lang=lang),
            'col_sub_lord': t('col_sub_lord', lang=lang),
            'col_cusp': t('col_cusp', lang=lang),
            'col_sign_lord': t('col_sign_lord', lang=lang),
            'report_source_row': t('report_source_row', lang=lang),
            'report_result_row': t('report_result_row', lang=lang),
            'report_back_btn': t('report_back_btn', lang=lang),
            'report_cta_title': t('report_cta_title', lang=lang),
            'report_cta_sub': t('report_cta_sub', lang=lang),
            'report_cta_desc': t('report_cta_desc', lang=lang),
            'report_cta_btn': t('report_cta_btn', lang=lang),
        }
    }
    return jsonify(response_data)


@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json() or {}
    contact_name = data.get('contact_name', '')
    contact_whatsapp = data.get('contact_whatsapp', '')
    contact_subject = data.get('contact_subject', '')
    contact_message = data.get('contact_message', '')
    
    log_line = f"[{datetime.datetime.now()}] Name: {contact_name}, WhatsApp: {contact_whatsapp}, Subject: {contact_subject}, Message: {contact_message}\n"
    print("=== NEW CONTACT INQUIRY RECEIVED ===")
    print(log_line)
    
    try:
        log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "contact_queries.txt"), "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"Error saving contact query: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
        
    return jsonify({"success": True})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if path.startswith("api/"):
        return jsonify({"error": "Not Found"}), 404
    # Serve index.html from React dist folder
    return send_from_directory(app.static_folder, "index.html")


if __name__ == '__main__':
    print("Starting Divya Drishti Local REST API & React Server...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host='127.0.0.1', port=5000, debug=True)
