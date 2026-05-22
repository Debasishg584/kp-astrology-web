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
    PROD_PATH = r"C:\kp_astrology_softwarer_final(gravity)"

if PROD_PATH not in sys.path:
    sys.path.insert(0, PROD_PATH)
    sys.path.insert(0, os.path.join(PROD_PATH, "src"))

import datetime
from flask import Flask, render_template, request, redirect, url_for, session

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


app = Flask(__name__)
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

def translate_aspect(name, lang=None):
    clean_name = str(name).strip().replace(" ", "_")
    mapping = {
        "Conjunction": "asp_Conjunction",
        "Sextile": "asp_Sextile",
        "Square": "asp_Square",
        "Trine": "asp_Trine",
        "Opposition": "asp_Opposition",
        "KP (P-P)": "asp_KP_PP",
        "KP (P-H)": "asp_KP_PH",
        "Vedic (P-P)": "asp_Vedic_PP",
        "Vedic (P-H)": "asp_Vedic_PH",
        "Casts Drishti": "asp_Casts_Drishti",
        "7th House Drishti": "asp_7th_House_Drishti",
        "4th House Drishti": "asp_4th_House_Drishti",
        "8th House Drishti": "asp_8th_House_Drishti",
        "3rd House Drishti": "asp_3rd_House_Drishti",
        "10th House Drishti": "asp_10th_House_Drishti",
        "5th House Drishti": "asp_5th_House_Drishti",
        "9th House Drishti": "asp_9th_House_Drishti",
        "Benefic": "qual_Benefic",
        "Malefic": "qual_Malefic",
        "Neutral": "qual_Neutral"
    }
    key = mapping.get(name) or mapping.get(clean_name)
    if key:
        from src.translations import t
        return t(key, lang=lang)
    return name

@app.context_processor
def inject_translations():
    from src.translations import t, convert_number
    lang = request.args.get('lang')
    if lang in ['en', 'hi', 'bn']:
        session['lang'] = lang
    else:
        lang = session.get('lang', 'en')
    
    def translate_helper(key, **kwargs):
        return t(key, lang=lang, **kwargs)
    
    def number_helper(val):
        return convert_number(val, lang=lang)
    
    def planet_helper(name):
        return translate_planet(name, lang=lang)
    
    def sign_helper(name):
        return translate_sign_name(name, lang=lang)
    
    def nakshatra_helper(name):
        return translate_nakshatra(name, lang=lang)
    
    def aspect_helper(name):
        return translate_aspect(name, lang=lang)
    
    return dict(
        current_lang=lang,
        t=translate_helper,
        n=number_helper,
        tp=planet_helper,
        ts=sign_helper,
        tn=nakshatra_helper,
        ta=aspect_helper
    )

@app.route('/')
def index():
    if not ENGINE_LOADED:
        return f"<h3>Failed to load astrology engine from {PROD_PATH}</h3><p>Error: {_IMPORT_ERROR}</p>"
    return render_template('index.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if not ENGINE_LOADED:
        return f"<h3>Failed to load astrology engine</h3>"
        
    lang = session.get('lang', 'en')
    
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')
        birth_date = request.form.get('birth_date', '')
        birth_time = request.form.get('birth_time', '')
        try:
            lat = float(request.form.get('latitude', '0.0'))
            lon = float(request.form.get('longitude', '0.0'))
        except ValueError:
            lat, lon = 0.0, 0.0
        tz = request.form.get('timezone', '+05:30')
        
        # Save to session
        session['last_calc_data'] = {
            'name': name,
            'birth_date': birth_date,
            'birth_time': birth_time,
            'latitude': lat,
            'longitude': lon,
            'timezone': tz
        }
    else:
        # GET request: load from session
        calc_data = session.get('last_calc_data')
        if not calc_data:
            return redirect(url_for('index'))
            
        name = calc_data.get('name', 'Anonymous')
        birth_date = calc_data.get('birth_date', '')
        birth_time = calc_data.get('birth_time', '')
        lat = calc_data.get('latitude', 0.0)
        lon = calc_data.get('longitude', 0.0)
        tz = calc_data.get('timezone', '+05:30')

    # Use production ChartEngine to perform calculations
    engine = ChartEngine()
    try:
        p1 = engine._calculate_one(birth_date, birth_time, lat, lon, tz, AppMode.BIRTH)
        exported = engine.build_export(p1)
    except Exception as e:
        return f"<h3>Calculation Error</h3><p>{str(e)}</p><a href='/'>Go back</a>"
        
    # Inject metadata for Titanium Forensic Engines
    exported['metadata'] = {
        'dob': birth_date,
        'language': lang
    }
    
    # Run predictions dynamically
    predictor = KPPredictor(exported)
    
    categories = {
        "WHO_AM_I": [
            "Past Life Karma", "Past Life Nature", "Karmic Debt", 
            "Purpose of Rebirth", "Native Nature", "Fear & Subconscious", "Spirituality"
        ],
        "FAMILY": [
            "Father Nature", "Mother Nature", "Sibling Nature", 
            "Friends Nature", "Spouse Nature", "Vastu", "Buy House", "Buy Vehicle"
        ],
        "KNOWLEDGE": [
            "School Success", "Higher Education", "Skills", "Weakness"
        ],
        "WORK": [
            "Interview", "Profession", "Promotion", "Bank Balance", "Speculation"
        ]
    }
    
    predictions_results = {}
    for cat_name, topics in categories.items():
        predictions_results[cat_name] = {}
        for topic in topics:
            rule = KP_RULES.get(topic)
            if rule:
                promise_strength = predictor._check_promise(rule["pos"], rule["neg"], p1["cusps"], engine.calc)
                result_text = predictor._poetic_interpretation(topic, promise_strength, rule["karaka"], lang=lang)
                predictions_results[cat_name][topic] = result_text

    # Run Marriage and Divorce Forensic calculations
    try:
        forensics = MarriageWidowedForensics(exported)
        marriage_report = forensics.calculate_timing_report()
    except Exception:
        marriage_report = {
            "Promise": "Unable to calculate marriage promise.",
            "Event_Windows": []
        }

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

    return render_template(
        'report.html',
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        lat=lat,
        lon=lon,
        tz=tz,
        chart=exported,
        predictions=predictions_results,
        marriage=marriage_report,
        asc_sign_idx=asc_sign_idx,
        rasi_occupancy=rasi_occupancy,
        bhava_occupancy=bhava_occupancy,
        cusp_sign_indices=cusp_sign_indices
    )


@app.route('/contact', methods=['POST'])
def contact():
    contact_name = request.form.get('contact_name', '')
    contact_email = request.form.get('contact_email', '')
    contact_subject = request.form.get('contact_subject', '')
    contact_message = request.form.get('contact_message', '')
    
    # Save the query to a local text file and print it to Flask console
    log_line = f"[{datetime.datetime.now()}] Name: {contact_name}, Email: {contact_email}, Subject: {contact_subject}, Message: {contact_message}\n"
    print("=== NEW CONTACT INQUIRY RECEIVED ===")
    print(log_line)
    print("====================================")
    
    try:
        log_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "contact_queries.txt"), "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"Error saving contact query: {e}")
        
    return redirect(url_for('index') + '?contact_success=true#contact')


if __name__ == '__main__':
    print("Starting Divya Drishti Local Web App...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host='127.0.0.1', port=5000, debug=True)
