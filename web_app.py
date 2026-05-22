import os
import sys

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
from flask import Flask, render_template, request, redirect, url_for

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

@app.route('/')
def index():
    if not ENGINE_LOADED:
        return f"<h3>Failed to load astrology engine from {PROD_PATH}</h3><p>Error: {_IMPORT_ERROR}</p>"
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    name = request.form.get('name', 'Anonymous')
    birth_date = request.form.get('birth_date', '')
    birth_time = request.form.get('birth_time', '')
    
    try:
        lat = float(request.form.get('latitude', '0.0'))
        lon = float(request.form.get('longitude', '0.0'))
    except ValueError:
        lat, lon = 0.0, 0.0
        
    tz = request.form.get('timezone', '+05:30')
    
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
        'language': 'en'
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
                result_text = predictor._poetic_interpretation(topic, promise_strength, rule["karaka"])
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
