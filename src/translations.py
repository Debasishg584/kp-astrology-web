"""
DIVYA DRISHTI - Translation System (i18n)
==========================================
Provides multi-language support for English, Hindi, and Bengali.
"""

# Available Languages
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "bn": "বাংলা"
}

# Global Language State
_current_lang = "en"

def set_lang(lang_code: str):
    """Set the current language. Use 'en', 'hi', or 'bn'."""
    global _current_lang
    if lang_code in LANGUAGES:
        _current_lang = lang_code

def get_lang() -> str:
    """Get the current language code."""
    return _current_lang

# Translation Dictionary
T = {
    # Generic
    "app_title": {"en": "Divya Drishti", "hi": "दिव्य दृष्टि", "bn": "দিব্য দৃষ্টি"},
    "name": {"en": "Name", "hi": "नाम", "bn": "নাম"},
    "gender": {"en": "Gender", "hi": "लिंग", "bn": "লিঙ্গ"},
    
    # Event Prediction Common
    "handing_over_to": {"en": ">>> HANDING OVER TO", "hi": ">>> इसे सौंपा जा रहा है", "bn": ">>> হস্তান্তর করা হচ্ছে"},
    "analyzing_context": {"en": "Analyzing Context", "hi": "सदर्भ का विश्लेषण", "bn": "প্রসঙ্গ বিশ্লেষণ"},
    "target_set": {"en": "TARGET SET", "hi": "लक्ष्य निर्धारित", "bn": "লক্ষ্য নির্ধারিত"},
    
    # --- Life Span / Death ---
    "life_span_handing_over": {"en": ">>> HANDING OVER TO: prediction/event/life_span.py (UAKP V3.8)", "hi": ">>> जीवन अवधि गणना को सौंपा जा रहा है (UAKP V3.8)", "bn": ">>> জীবনকাল গণনার কাছে হস্তান্তর করা হচ্ছে (UAKP V3.8)"},
    "death_audit_title": {"en": "☠️ UAKP V3.8 DEATH AUDIT - 6-GATE FORENSIC SYSTEM", "hi": "☠️ UAKP V3.8 मृत्यु लेखा परीक्षा - 6-गेट फोरेंसिक प्रणाली", "bn": "☠️ UAKP V3.8 মৃত্যু অডিট - 6-গেট ফরেনসিক সিস্টেম"},
    "longevity_category": {"en": "LONGEVITY CATEGORY", "hi": "दीर्घायु श्रेणी", "bn": "দীর্ঘায়ু বিভাগ"},
    "death_window_years": {"en": "Death Window (Cat): {start}-{end} years", "hi": "मृत्यु अवधि (श्रेणी): {start}-{end} वर्ष", "bn": "মৃত্যুর সময়কাল (বিভাগ): {start}-{end} বছর"},
    "active_scan_range": {"en": "Active Scan Range: {start}-{end} years (Age: {age})", "hi": "सक्रिय स्कैन रेंज: {start}-{end} वर्ष (आयु: {age})", "bn": "সক্রিয় স্ক্যান পরিসীমা: {start}-{end} বছর (বয়স: {age})"},
    "gate_1_title": {"en": "⚙️ GATE 1: STRUCTURAL PERMIT", "hi": "⚙️ गेट 1: संरचनात्मक अनुमति", "bn": "⚙️ গেট 1: কাঠামোগত অনুমতি"},
    "no_critical_death_windows": {"en": "No critical death windows detected in the scan range.", "hi": "स्कैन रेंज में कोई गंभीर मृत्यु अवधि नहीं मिली।", "bn": "স্ক্যান রেঞ্জে কোন গুরুতর মৃত্যুর সময়কাল পাওয়া যায়নি।"},

    # --- Marriage ---
    "marriage_promise_analysis": {"en": "MARRIAGE PROMISE ANALYSIS", "hi": "विवाह वचन विश्लेषण", "bn": "বিবাহ প্রতিশ্রুতি বিশ্লেষণ"},
    "marriage_count_no": {"en": "MARRIAGE COUNT: NO MARRIAGE", "hi": "विवाह संख्या: कोई विवाह नहीं", "bn": "বিবাহ সংখ্যা: বিবাহ নেই"},
    "marriage_count_single": {"en": "MARRIAGE COUNT: SINGLE MARRIAGE", "hi": "विवाह संख्या: एकल विवाह", "bn": "বিবাহ সংখ্যা: একটি বিবাহ"},
    "marriage_count_multiple": {"en": "MARRIAGE COUNT: MULTIPLE MARRIAGES", "hi": "विवाह संख्या: बहु विवाह", "bn": "বিবাহ সংখ্যা: একাধিক বিবাহ"},
    "marriage_windows_found": {"en": "Found {count} marriage timing windows.", "hi": "{count} विवाह समय खिड़कियां मिलीं।", "bn": "{count} টি বিবাহের সময় উইন্ডো পাওয়া গেছে।"},
    "marriage_not_indicated": {"en": "Marriage not indicated.", "hi": "विवाह का संकेत नहीं।", "bn": "বিবাহ নির্দেশিত নয়।"},
    
    # --- Child ---
    "child_birth_analysis": {"en": "CHILD/PROGENY ANALYSIS", "hi": "संतान/प्रजा विश्लेषण", "bn": "সন্তান/প্রজন্য় বিশ্লেষণ"},
    "child_possible": {"en": "CHILD/PROGENY: POSSIBLE", "hi": "संतान: संभव", "bn": "সন্তান: সম্ভব"},
    "child_not_possible": {"en": "CHILD/PROGENY: NOT POSSIBLE", "hi": "संतान: संभव नहीं", "bn": "সন্তান: সম্ভব নয়"},
    "fertile_windows_found": {"en": "Found {count} fertile windows.", "hi": "{count} उर्वर खिड़कियां मिलीं।", "bn": "{count} টি উর্বর উইন্ডো পাওয়া গেছে।"},

    # --- Wealth/Debt ---
    "wealth_promise_title": {"en": "WEALTH PROMISE", "hi": "धन वचन", "bn": "ধন প্রতিশ্রুতি"},
    "wealth_vulnerability": {"en": "WEALTH VULNERABILITY", "hi": "धन संवेदनशीलता", "bn": "ধন দুর্বলতা"},
    "debt_vulnerability": {"en": "DEBT VULNERABILITY", "hi": "ऋण संवेदनशीलता", "bn": "ঋণ দুর্বলতা"},
    "wealth_strong": {"en": "WEALTH: STRONGLY PROMISED", "hi": "धन: दृढ़ता से प्रतिशृत", "bn": "ধন: দৃঢ়ভাবে প্রতিশ্রুতিবদ্ধ"},
    "wealth_mixed": {"en": "WEALTH: MIXED (Gains with Obstacles)", "hi": "धन: मिश्रित (बाधाओं के साथ लाभ)", "bn": "ধন: মিশ্র (বাধা সহ লাভ)"},
    "wealth_weak": {"en": "WEALTH: WEAK PROMISE", "hi": "धन: कमजोर वचन", "bn": "ধন: দুর্বল প্রতিশ্রুতি"},

    # --- Job ---
    "job_promise_title": {"en": "JOB PROMISE", "hi": "नौकरी वचन", "bn": "চাকরি প্রতিশ্রুতি"},
    "job_vulnerability": {"en": "JOB VULNERABILITY", "hi": "नौकरी संवेदनशीलता", "bn": "চাকরি দুর্বলতা"},
    "job_strong": {"en": "JOB: STRONGLY PROMISED", "hi": "नौकरी: दृढ़ता से प्रतिशृत", "bn": "চাকরি: দৃঢ়ভাবে প্রতিশ্রুতিবদ্ধ"},
    "job_obstacles": {"en": "JOB: PROMISED (With Delays/Struggles)", "hi": "नौकरी: प्रतिशृत (देरी/संघर्ष के साथ)", "bn": "চাকরি: প্রতিশ্রুতিবদ্ধ (বিলম্ব/সংগ্রাম সহ)"},
    "job_weak": {"en": "JOB: WEAK PROMISE", "hi": "नौकरी: कमजोर वचन", "bn": "চাকরি: দুর্বল প্রতিশ্রুতি"},
    
    # --- Vehicle/Property ---
    "vehicle_analysis": {"en": "VEHICLE PURCHASE ANALYSIS", "hi": "वाहन खरीद विश्लेषण", "bn": "যানবাহন ক্রয় বিশ্লেষণ"},
    "property_analysis": {"en": "PROPERTY PURCHASE ANALYSIS", "hi": "संपत्ति खरीद विश्लेषण", "bn": "সম্পত্তি ক্রয় বিশ্লেষণ"},
    "purchase_promised": {"en": "PURCHASE: PROMISED", "hi": "खरीद: प्रतिशृत", "bn": "ক্রয়: প্রতিশ্রুতিবদ্ধ"},
    "purchase_blocked": {"en": "PURCHASE: BLOCKED", "hi": "खरीद: अवरुद्ध", "bn": "ক্রয়: অবরুদ্ধ"},
    "purchase_risky": {"en": "PURCHASE: RISKY", "hi": "खरीद: जोखिम भरा", "bn": "ক্রয়: ঝুঁকিপূর্ণ"},
    
    # --- UI Labels ---
    "date_label": {"en": "Date", "hi": "दिनांक", "bn": "তারিখ"},
    "time_label": {"en": "Time", "hi": "समय", "bn": "সময়"},
    "place_label": {"en": "Place", "hi": "स्थान", "bn": "স্থান"},
    "country_label": {"en": "Country", "hi": "देश", "bn": "দেশ"},
    "state_label": {"en": "State", "hi": "राज्य", "bn": "রাজ্য"},
    "lat_label": {"en": "Lat", "hi": "अक्षांश", "bn": "অক্ষাংশ"},
    "lon_label": {"en": "Lon", "hi": "देशांतर", "bn": "দ্রাঘিমা"},
    "tz_label": {"en": "TZ", "hi": "समय क्षेत्र", "bn": "সময় অঞ্চল"},
    "btn_generate": {"en": "✨ GENERATE", "hi": "✨ कुंडली बनाएं", "bn": "✨ কুণ্ডলী তৈরি করুন"},
    "btn_save": {"en": "💾 SAVE", "hi": "💾 सहेजें", "bn": "💾 সংরক্ষণ করুন"},
    "btn_reset": {"en": "🔁 RESET", "hi": "🔁 रीसेट", "bn": "🔁 রিসেট"},
    "btn_ai": {"en": "🔮 AI ASTROLOGER", "hi": "🔮 एआई ज्योतिषी", "bn": "🔮 এআই জ্যোতিষী"},
    "analysis_tools_title": {"en": " ANALYSIS TOOLS", "hi": " विश्लेषण उपकरण", "bn": " বিশ্লেষণ সরঞ্জাম"},
    
    # --- Court/Litigation ---
    "court_analysis": {"en": "COURT CASE / LITIGATION ANALYSIS", "hi": "कोर्ट केस / मुकदमेबाजी विश्लेषण", "bn": "কোর্ট কেস / মামলা বিশ্লেষণ"},
    "severe_case": {"en": "LITIGATION: SEVERE CASE INDICATED", "hi": "मुकदमेबाजी: गंभीर मामला संकेतित", "bn": "মামলা: গুরুতর কেস নির্দেশিত"},
    "litigation_likely": {"en": "LITIGATION: CASE LIKELY", "hi": "मुकदमेबाजी: मामला संभावित", "bn": "মামলা: কেস সম্ভাব্য"},
    "warning_only": {"en": "LITIGATION: WARNING ONLY (No formal case)", "hi": "मुकदमेबाजी: केवल चेतावनी (कोई औपचारिक मामला नहीं)", "bn": "মামলা: শুধুমাত্র সতর্কতা (কোন আনুষ্ঠানিক কেস নেই)"},
    "no_case": {"en": "LITIGATION: NO COURT CASE", "hi": "मुकदमेबाजी: कोई कोर्ट केस नहीं", "bn": "মামলা: কোন কোর্ট কেস নেই"},

    # --- Hospitalization ---
    "hospital_analysis": {"en": "HOSPITALIZATION RISK ANALYSIS", "hi": "अस्पताल में भर्ती जोखिम विश्लेषण", "bn": "হাসপাতালে ভর্তি ঝুঁকি বিশ্লেষণ"},
    
    # --- Common Verdicts ---
    "high_risk": {"en": "HIGH RISK", "hi": "उच्च जोखिम", "bn": "উচ্চ ঝুঁকি"},
    "moderate_risk": {"en": "MODERATE RISK", "hi": "मध्यम जोखिम", "bn": "মাঝারি ঝুঁকি"},
    "low_risk": {"en": "LOW RISK", "hi": "कम जोखिम", "bn": "কম ঝুঁকি"},
    "high_vulnerability": {"en": "HIGH VULNERABILITY", "hi": "उच्च संवेदनशीलता", "bn": "উচ্চ দুর্বলতা"},
    "moderate_vulnerability": {"en": "MODERATE VULNERABILITY", "hi": "मध्यम संवेदनशीलता", "bn": "মাঝারি দুর্বলতা"},
    "low_vulnerability": {"en": "LOW VULNERABILITY", "hi": "कम संवेदनशीलता", "bn": "কম দুর্বলতা"},
    
    # --- Windows Summary ---
    "windows_found_count": {"en": "Received {count} {type} windows.", "hi": "{count} {type} खिड़कियां प्राप्त हुईं।", "bn": "{count} টি {type} উইন্ডো পাওয়া গেছে।"},
    "no_windows_found": {"en": "No strong {type} windows found.", "hi": "कोई मजबूत {type} खिड़कियां नहीं मिलीं।", "bn": "কোন শক্তিশালী {type} উইন্ডো পাওয়া যায়নি।"},

    # --- Birth Details ---
    "birth_details": {"en": "BIRTH DETAILS", "hi": "जन्म विवरण", "bn": "জন্ম বিবরণ"},
    
    # --- Zodiac Signs (Simple Mapping) ---
    "sign_aries": {"en": "Aries", "hi": "मेष", "bn": "মেষ"},
    "sign_taurus": {"en": "Taurus", "hi": "वृषभ", "bn": "বৃষ"},
    "sign_gemini": {"en": "Gemini", "hi": "मिथुन", "bn": "মিথুন"},
    "sign_cancer": {"en": "Cancer", "hi": "कर्क", "bn": "কর্কট"},
    "sign_leo": {"en": "Leo", "hi": "सिंह", "bn": "সিংহ"},
    "sign_virgo": {"en": "Virgo", "hi": "कन्या", "bn": "কন্যা"},
    "sign_libra": {"en": "Libra", "hi": "तुला", "bn": "তুল"},
    "sign_scorpio": {"en": "Scorpio", "hi": "वृश्चिक", "bn": "বৃশ্চিক"},
    "sign_sagittarius": {"en": "Sagittarius", "hi": "धनु", "bn": "ধনু"},
    "sign_capricorn": {"en": "Capricorn", "hi": "मकर", "bn": "মকর"},
    "sign_aquarius": {"en": "Aquarius", "hi": "कुंभ", "bn": "কুম্ভ"},
    "sign_pisces": {"en": "Pisces", "hi": "मीन", "bn": "মীন"},
    
    # ==========================================================================
    # MAIN.PY TOOL BUTTONS
    # ==========================================================================
    "tool_planetary_positions": {"en": "🪐 Planetary Positions", "hi": "🪐 ग्रह स्थिति", "bn": "🪐 গ্রহ অবস্থান"},
    "tool_house_cusps": {"en": "🏠 House Cusps", "hi": "🏠 भाव शीर्ष", "bn": "🏠 ভাব শীর্ষ"},
    "tool_house_significators": {"en": "📊 House Significators", "hi": "📊 भाव द्योतक", "bn": "📊 ভাব দ্যোতক"},
    "tool_planet_significators": {"en": "🌟 Planet Significators", "hi": "🌟 ग्रह द्योतक", "bn": "🌟 গ্রহ দ্যোতক"},
    "tool_aspects_drishti": {"en": "👁️ Aspects & Drishti", "hi": "👁️ दृष्टि एवं योग", "bn": "👁️ দৃষ্টি ও যোগ"},
    "tool_kp_dasa": {"en": "📜 KP Dasa", "hi": "📜 केपी दशा", "bn": "📜 কেপি দশা"},
    "tool_daily_prediction": {"en": "📅 Daily Prediction", "hi": "📅 दैनिक भविष्यवाणी", "bn": "📅 দৈনিক ভবিষ্যদ্বাণী"},
    "tool_year_prediction": {"en": "📆 Year Wise Prediction", "hi": "📆 वार्षिक भविष्यवाणी", "bn": "📆 বার্ষিক ভবিষ্যদ্বাণী"},
    
    # ==========================================================================
    # KP ASTROLOGER UI ELEMENTS
    # ==========================================================================
    "titanium_title": {"en": "KP ASTROLOGER: UNIVERSAL PREDICTOR", "hi": "केपी एस्ट्रोलॉजर: सार्वभौमिक भविष्यवक्ता", "bn": "কেপি অ্যাস্ট্রোলজার: সার্বজনীন ভবিষ্যদ্বক্তা"},
    "titanium_window_title": {"en": "🔱 KP ASTROLOGER - Divya Drishti Master Console", "hi": "🔱 केपी एस्ट्रोलॉजर - दिव्य दृष्टि मास्टर कंसोल", "bn": "🔱 কেপি অ্যাস্ট্রোলজার - দিব্য দৃষ্টি মাস্টার কনসোল"},
    "event_timing": {"en": "Event Timing", "hi": "घटना समय", "bn": "ইভেন্ট টাইমিং"},
    "general_analysis": {"en": "General Analysis", "hi": "सामान्य विश्लेषण", "bn": "সাধারণ বিশ্লেষণ"},
    "load_data": {"en": "📂 Load Data", "hi": "📂 डेटा लोड करें", "bn": "📂 ডেটা লোড করুন"},
    "read_data": {"en": "📂 Read Data", "hi": "📂 डेटा पढ़ें", "bn": "📂 ডেটা পড়ুন"},
    "set_query": {"en": "❓ Set Query", "hi": "❓ प्रश्न सेट करें", "bn": "❓ প্রশ্ন সেট করুন"},
    "generate_btn": {"en": "⚡ Generate", "hi": "⚡ उत्पन्न करें", "bn": "⚡ জেনারেট করুন"},
    "rules_audit": {"en": "📋 Rules Audit", "hi": "📋 नियम ऑडिट", "bn": "📋 নিয়ম অডিট"},
    "transit_audit": {"en": "🔴 Transit Audit", "hi": "🔴 गोचर ऑडिट", "bn": "🔴 গোচর অডিট"},
    "final_report": {"en": "📊 Final Report", "hi": "📊 अंतिम रिपोर्ट", "bn": "📊 চূড়ান্ত রিপোর্ট"},
    "module_ready": {"en": "Module Ready", "hi": "मॉड्यूल तैयार", "bn": "মডিউল প্রস্তুত"},
    "possibility_check": {"en": "🔍 Possibility Check", "hi": "🔍 संभावना जांच", "bn": "🔍 সম্ভাবনা পরীক্ষা"},
    "generate_info": {"en": "✨ Generate Info", "hi": "✨ जानकारी उत्पन्न करें", "bn": "✨ তথ্য তৈরি করুন"},
    "show_result": {"en": "📋 Show Result", "hi": "📋 परिणाम दिखाएं", "bn": "📋 ফলাফল দেখান"},
    
    # ==========================================================================
    # STAGE TITLES
    # ==========================================================================
    "stage_1_title": {"en": "STAGE 1: PLANETARY STRENGTH & PRIMARY PROMISE", "hi": "चरण 1: ग्रह बल और प्राथमिक वचन", "bn": "পর্যায় ১: গ্রহ শক্তি এবং প্রাথমিক প্রতিশ্রুতি"},
    "stage_2_title": {"en": "STAGE 2: DASHA-BHUKTI SCAN", "hi": "चरण 2: दशा-भुक्ति स्कैन", "bn": "পর্যায় ২: দশা-ভুক্তি স্ক্যান"},
    "stage_3_title": {"en": "STAGE 3: TRANSIT TRIGGER & FINAL CONFIRMATION", "hi": "चरण 3: गोचर ट्रिगर और अंतिम पुष्टि", "bn": "পর্যায় ৩: গোচর ট্রিগার এবং চূড়ান্ত নিশ্চিতকরণ"},
    
    # ==========================================================================
    # TABLE HEADERS / POPUP TITLES
    # ==========================================================================
    "tbl_planetary_positions": {"en": "Planetary Positions (Nirayana)", "hi": "ग्रह स्थिति (निरयन)", "bn": "গ্রহ অবস্থান (নিরয়ণ)"},
    "tbl_house_cusps": {"en": "House Cusps", "hi": "भाव शीर्ष", "bn": "ভাব শীর্ষ"},
    "tbl_house_significators": {"en": "House Significators", "hi": "भाव द्योतक", "bn": "ভাব দ্যোতক"},
    "tbl_planet_significators": {"en": "Planet Significators", "hi": "ग्रह द्योतक", "bn": "গ্রহ দ্যোতক"},
    "tbl_aspects_drishti": {"en": "Unified Aspects & Drishti", "hi": "एकीकृत दृष्टि एवं योग", "bn": "একীভূত দৃষ্টি ও যোগ"},
    "tbl_kp_dasa": {"en": "KP Dasa", "hi": "केपी दशा", "bn": "কেপি দশা"},
    
    # Table column headers
    "col_planet": {"en": "Planet", "hi": "ग्रह", "bn": "গ্রহ"},
    "col_longitude": {"en": "Longitude", "hi": "देशांतर", "bn": "দ্রাঘিমাংশ"},
    "col_sign": {"en": "Sign", "hi": "राशि", "bn": "রাশি"},
    "col_nakshatra": {"en": "Nakshatra", "hi": "नक्षत्र", "bn": "নক্ষত্র"},
    "col_star_lord": {"en": "Star Lord", "hi": "नक्षत्र स्वामी", "bn": "নক্ষত্র স্বামী"},
    "col_sub_lord": {"en": "Sub Lord", "hi": "उप-स्वामी", "bn": "উপ-স্বামী"},
    "col_cusp": {"en": "Cusp", "hi": "भाव", "bn": "ভাব"},
    "col_degree": {"en": "Degree", "hi": "अंश", "bn": "ডিগ্রি"},
    "col_sign_lord": {"en": "Sign Lord", "hi": "राशि स्वामी", "bn": "রাশি স্বামী"},
    "col_house": {"en": "House", "hi": "भाव", "bn": "ভাব"},
    "col_level": {"en": "Level", "hi": "स्तर", "bn": "স্তর"},
    "col_details": {"en": "Details", "hi": "विवरण", "bn": "বিবরণ"},
    
    "col_l1": {"en": "Level 1", "hi": "स्तर 1", "bn": "স্তর ১"},
    "col_l2": {"en": "Level 2", "hi": "स्तर 2", "bn": "স্তর ২"},
    "col_l3": {"en": "Level 3", "hi": "स्तर 3", "bn": "স্তর ৩"},
    "col_l4": {"en": "Level 4", "hi": "स्तर 4", "bn": "স্তর ৪"},
    
    "col_system": {"en": "System", "hi": "प्रणाली", "bn": "পদ্ধতি"},
    "col_source": {"en": "Source", "hi": "स्रोत", "bn": "উৎস"},
    "col_relation": {"en": "Relation", "hi": "संबंध", "bn": "সম্পর্ক"},
    "col_target": {"en": "Target", "hi": "लक्ष्य", "bn": "লক্ষ্য"},
    "col_value_type": {"en": "Value/Type", "hi": "मान/प्रकार", "bn": "মান/প্রকার"},
    "col_quality": {"en": "Quality", "hi": "गुणवत्ता", "bn": "গুণমান"},
    
    "col_start": {"en": "Start", "hi": "प्रारंभ", "bn": "শুরু"},
    "col_end": {"en": "End", "hi": "अंत", "bn": "শেষ"},
    "col_duration": {"en": "Duration", "hi": "अवधि", "bn": "সময়কাল"},
    
    # Common labels
    "male": {"en": "Male", "hi": "पुरुष", "bn": "পুরুষ"},
    "female": {"en": "Female", "hi": "महिला", "bn": "মহিলা"},
    "other": {"en": "Other", "hi": "अन्य", "bn": "অন্যান্য"},
    
    # Planet Names
    "p_Sun": {"en": "Sun", "hi": "सूर्य", "bn": "রবি"},
    "p_Moon": {"en": "Moon", "hi": "चंद्र", "bn": "চন্দ্র"},
    "p_Mars": {"en": "Mars", "hi": "मंगल", "bn": "মঙ্গল"},
    "p_Mercury": {"en": "Mercury", "hi": "बुध", "bn": "বুধ"},
    "p_Jupiter": {"en": "Jupiter", "hi": "गुरु", "bn": "বৃহস্পতি"},
    "p_Venus": {"en": "Venus", "hi": "शुक्र", "bn": "শুক্র"},
    "p_Saturn": {"en": "Saturn", "hi": "शनि", "bn": "শনি"},
    "p_Rahu": {"en": "Rahu", "hi": "राहु", "bn": "রাহু"},
    "p_Ketu": {"en": "Ketu", "hi": "केतु", "bn": "কেতু"},
    "p_Uranus": {"en": "Uranus", "hi": "अरुण", "bn": "ইউরেনাস"},
    "p_Neptune": {"en": "Neptune", "hi": "वरुण", "bn": "নেপচুন"},
    "p_Pluto": {"en": "Pluto", "hi": "यम", "bn": "প্লুটো"},
    
    # Sign Names
    "sign_Aries": {"en": "Aries", "hi": "मेष", "bn": "মেষ"},
    "sign_Taurus": {"en": "Taurus", "hi": "वृषभ", "bn": "বৃষ"},
    "sign_Gemini": {"en": "Gemini", "hi": "मिथुन", "bn": "মিথুন"},
    "sign_Cancer": {"en": "Cancer", "hi": "कर्क", "bn": "কর্কট"},
    "sign_Leo": {"en": "Leo", "hi": "सिंह", "bn": "সিংহ"},
    "sign_Virgo": {"en": "Virgo", "hi": "कन्या", "bn": "কন্যা"},
    "sign_Libra": {"en": "Libra", "hi": "तुला", "bn": "তুলা"},
    "sign_Scorpio": {"en": "Scorpio", "hi": "वृश्चिक", "bn": "বৃশ্চিক"},
    "sign_Sagittarius": {"en": "Sagittarius", "hi": "धनु", "bn": "ধনু"},
    "sign_Capricorn": {"en": "Capricorn", "hi": "मकर", "bn": "মকর"},
    "sign_Aquarius": {"en": "Aquarius", "hi": "कुम्भ", "bn": "কুম্ভ"},
    "sign_Pisces": {"en": "Pisces", "hi": "मीन", "bn": "মীন"},

    # Nakshatra Names
    "nak_Ashwini": {"en": "Ashwini", "hi": "अश्विनी", "bn": "অশ্বিনী"},
    "nak_Bharani": {"en": "Bharani", "hi": "भरणी", "bn": "ভরণী"},
    "nak_Krittika": {"en": "Krittika", "hi": "कृत्तिका", "bn": "কৃত্তিকা"},
    "nak_Rohini": {"en": "Rohini", "hi": "रोहिणी", "bn": "রোহিণী"},
    "nak_Mrigashira": {"en": "Mrigashira", "hi": "मृगशिरा", "bn": "মৃগশিরা"},
    "nak_Ardra": {"en": "Ardra", "hi": "आर्द्रा", "bn": "আর্দ্রা"},
    "nak_Punarvasu": {"en": "Punarvasu", "hi": "पुनर्वसु", "bn": "পুনর্বসু"},
    "nak_Pushya": {"en": "Pushya", "hi": "पुष्य", "bn": "পুষ্যা"},
    "nak_Ashlesha": {"en": "Ashlesha", "hi": "अश्लेषा", "bn": "অশ্লেষা"},
    "nak_Magha": {"en": "Magha", "hi": "मघा", "bn": "মঘা"},
    "nak_PurvaPhalguni": {"en": "Purva Phalguni", "hi": "पूर्वा फाल्गुनी", "bn": "পূর্ব ফাল্গুনী"},
    "nak_UttaraPhalguni": {"en": "Uttara Phalguni", "hi": "उत्तरा फाल्गुनी", "bn": "উত্তর ফাল্গুনী"},
    "nak_Hasta": {"en": "Hasta", "hi": "हस्त", "bn": "হস্তা"},
    "nak_Chitra": {"en": "Chitra", "hi": "चित्रा", "bn": "চিত্রা"},
    "nak_Swati": {"en": "Swati", "hi": "स्वाति", "bn": "স্বাতী"},
    "nak_Vishakha": {"en": "Vishakha", "hi": "विशाखा", "bn": "বিশাখা"},
    "nak_Anuradha": {"en": "Anuradha", "hi": "अनुराधा", "bn": "অনুরাধা"},
    "nak_Jyeshtha": {"en": "Jyeshtha", "hi": "ज्येष्ठा", "bn": "জ্যেষ্ঠা"},
    "nak_Moola": {"en": "Moola", "hi": "मूल", "bn": "মূলা"},
    "nak_PurvaAshadha": {"en": "Purva Ashadha", "hi": "पूर्वाषाढ़ा", "bn": "পূর্বাষাঢ়া"},
    "nak_UttaraAshadha": {"en": "Uttara Ashadha", "hi": "उत्तराषाढ़ा", "bn": "উত্তরাষাঢ়া"},
    "nak_Shravana": {"en": "Shravana", "hi": "श्रवण", "bn": "শ্রবণা"},
    "nak_Dhanishtha": {"en": "Dhanishtha", "hi": "धनिष्ठा", "bn": "ধনিষ্ঠা"},
    "nak_Shatabhisha": {"en": "Shatabhisha", "hi": "शतभिषा", "bn": "শতভিষা"},
    "nak_PurvaBhadrapada": {"en": "Purva Bhadrapada", "hi": "पूर्वा भाद्रपद", "bn": "পূর্ব ভাদ্রপদ"},
    "nak_UttaraBhadrapada": {"en": "Uttara Bhadrapada", "hi": "उत्तरा भाद्रपद", "bn": "উত্তর ভাদ্রপদ"},
    "nak_Revati": {"en": "Revati", "hi": "रेवती", "bn": "রেবতী"},
    
    
    # Aspects
    "asp_Conjunction": {"en": "Conjunction", "hi": "युति", "bn": "সংযোগ"},
    "asp_Sextile": {"en": "Sextile", "hi": "षडाष्टक", "bn": "sextile"}, # Correct Hindi term needed, using translit or approx if unsure. Keeping Sextile for now or "लाभ दृष्टि"
    "asp_Square": {"en": "Square", "hi": "केन्द्र", "bn": "কেন্দ্র"},
    "asp_Trine": {"en": "Trine", "hi": "त्रिकोण", "bn": "ত্রিকোণ"},
    "asp_Opposition": {"en": "Opposition", "hi": "प्रतियुति", "bn": "বিপরীত"},
    "asp_KP_PP": {"en": "KP (P-P)", "hi": "केपी (ग्रह-ग्रह)", "bn": "কেপি (গ্রহ-গ্রহ)"},
    "asp_KP_PH": {"en": "KP (P-H)", "hi": "केपी (ग्रह-भाव)", "bn": "কেপি (গ্রহ-ভাব)"},
    "asp_Vedic_PP": {"en": "Vedic (P-P)", "hi": "वैदिक (ग्रह-ग्रह)", "bn": "বৈদিক (গ্রহ-গ্রহ)"},
    "asp_Vedic_PH": {"en": "Vedic (P-H)", "hi": "वैदिक (ग्रह-भाव)", "bn": "বৈদিক (গ্রহ-ভাব)"},
    "asp_Casts_Drishti": {"en": "Casts Drishti", "hi": "दृष्टि डालता है", "bn": "দৃষ্টি দেয়"},
    "asp_7th_House_Drishti": {"en": "7th House Drishti", "hi": "सप्तम दृष्टि", "bn": "সপ্তম দৃষ্টি"},
    "asp_4th_House_Drishti": {"en": "4th House Drishti", "hi": "चतुर्थ दृष्टि", "bn": "চতুর্থ  দৃষ্টি"},
    "asp_8th_House_Drishti": {"en": "8th House Drishti", "hi": "अष्टम दृष्टि", "bn": "অষ্টম দৃষ্টি"},
    "asp_3rd_House_Drishti": {"en": "3rd House Drishti", "hi": "तृतीय दृष्टि", "bn": "তৃতীয় দৃষ্টি"},
    "asp_10th_House_Drishti": {"en": "10th House Drishti", "hi": "दशम दृष्टि", "bn": "দশম দৃষ্টি"},
    "asp_5th_House_Drishti": {"en": "5th House Drishti", "hi": "पंचम दृष्टि", "bn": "পঞ্চম দৃষ্টি"},
    "asp_9th_House_Drishti": {"en": "9th House Drishti", "hi": "नवम दृष्टि", "bn": "নবম দৃষ্টি"},
    "qual_Benefic": {"en": "Benefic", "hi": "शुभ", "bn": "শুভ"},
    "qual_Malefic": {"en": "Malefic", "hi": "अशुभ", "bn": "অশুভ"},
    "qual_Neutral": {"en": "Neutral", "hi": "तटस्थ", "bn": "নিরপেক্ষ"},

    # ==========================================================================
    # EVENT MODULE COMMON TRANSLATIONS
    # ==========================================================================
    
    # Gate System
    "gate_checking": {"en": ">>> CHECKING GATE", "hi": ">>> गेट जाँच रहा है", "bn": ">>> গেট চেক করা হচ্ছে"},
    "gate_passed": {"en": "✅ GATE PASSED", "hi": "✅ गेट पास", "bn": "✅ গেট পাস"},
    "gate_failed": {"en": "❌ GATE FAILED", "hi": "❌ गेट विफल", "bn": "❌ গেট ব্যর্থ"},
    "gate_1": {"en": "GATE 1: STRUCTURAL PERMIT", "hi": "गेट 1: संरचनात्मक अनुमति", "bn": "গেট 1: কাঠামোগত অনুমতি"},
    "gate_2": {"en": "GATE 2: DASHA VERIFICATION", "hi": "गेट 2: दशा सत्यापन", "bn": "গেট 2: দশা যাচাই"},
    "gate_3": {"en": "GATE 3: SUB-LORD CODE", "hi": "गेट 3: उप-स्वामी कोड", "bn": "গেট 3: উপ-স্বামী কোড"},
    "gate_4": {"en": "GATE 4: KARAKA CHECK", "hi": "गेट 4: कारक जाँच", "bn": "গেট 4: কারক পরীক্ষা"},
    "gate_5": {"en": "GATE 5: TRIPLE CSL LOCK", "hi": "गेट 5: त्रिगुण सीएसएल लॉक", "bn": "গেট 5: ট্রিপল সিএসএল লক"},
    "gate_6": {"en": "GATE 6: SUN SEAL", "hi": "गेट 6: सूर्य मुद्रा", "bn": "গেট 6: সূর্য সীল"},
    
    # Verdicts
    "verdict_strong_promise": {"en": "STRONG PROMISE", "hi": "दृढ़ वचन", "bn": "দৃঢ় প্রতিশ্রুতি"},
    "verdict_weak_promise": {"en": "WEAK PROMISE", "hi": "कमजोर वचन", "bn": "দুর্বল প্রতিশ্রুতি"},
    "verdict_denied": {"en": "DENIED", "hi": "खारिज", "bn": "প্রত্যাখ্যান"},
    "verdict_neutral": {"en": "NEUTRAL", "hi": "तटस्थ", "bn": "নিরপেক্ষ"},
    "verdict_confirmed": {"en": "CONFIRMED", "hi": "पुष्टि", "bn": "নিশ্চিত"},
    "verdict_possible": {"en": "POSSIBLE", "hi": "संभव", "bn": "সম্ভব"},
    "verdict_unlikely": {"en": "UNLIKELY", "hi": "असंभावित", "bn": "অসম্ভব"},
    
    # Status Tags
    "status_golden_window": {"en": "🎯 GOLDEN WINDOW (Certain Event)", "hi": "🎯 स्वर्णिम अवधि (निश्चित घटना)", "bn": "🎯 সোনালী উইন্ডো (নিশ্চিত ঘটনা)"},
    "status_high_probability": {"en": "✅ HIGH PROBABILITY", "hi": "✅ उच्च संभावना", "bn": "✅ উচ্চ সম্ভাবনা"},
    "status_requires_transit": {"en": "🟡 POSSIBLE (Requires Transit)", "hi": "🟡 संभव (गोचर आवश्यक)", "bn": "🟡 সম্ভব (গোচর প্রয়োজন)"},
    "status_low_probability": {"en": "⚪ LOW PROBABILITY", "hi": "⚪ कम संभावना", "bn": "⚪ কম সম্ভাবনা"},
    "status_negation": {"en": "❌ NEGATION", "hi": "❌ निषेध", "bn": "❌ নাকচ"},
    
    # Common Messages
    "msg_promise_pass": {"en": "✅ PROMISE: {csl} connects to houses {houses}.", "hi": "✅ वचन: {csl} भाव {houses} से जुड़ता है।", "bn": "✅ প্রতিশ্রুতি: {csl} ভাব {houses}-এর সাথে যুক্ত।"},
    "msg_denial": {"en": "⛔ DENIAL: {csl} signifies houses {houses} (Negation Group).", "hi": "⛔ खारिज: {csl} भाव {houses} का द्योतक है (निषेध समूह)।", "bn": "⛔ প্রত্যাখ্যান: {csl} ভাব {houses} নির্দেশ করে (নাকচ গোষ্ঠী)।"},
    "msg_neutral": {"en": "⚠️ NEUTRAL: {csl} is mixed. Proceed with caution.", "hi": "⚠️ तटस्थ: {csl} मिश्रित है। सावधानी से आगे बढ़ें।", "bn": "⚠️ নিরপেক্ষ: {csl} মিশ্র। সাবধানে এগিয়ে যান।"},
    "msg_missing_data": {"en": "Missing {item} Data", "hi": "{item} डेटा गायब है", "bn": "{item} ডেটা অনুপস্থিত"},
    "msg_target_range": {"en": "Target Range: {start} - {end} Years", "hi": "लक्ष्य रेंज: {start} - {end} वर्ष", "bn": "লক্ষ্য পরিসীমা: {start} - {end} বছর"},
    "msg_negation_filter_active": {"en": "Negation Filter: ACTIVE", "hi": "निषेध फ़िल्टर: सक्रिय", "bn": "নাকচ ফিল্টার: সক্রিয়"},
    "msg_scanning": {"en": "Scanning {item}...", "hi": "{item} स्कैन हो रहा है...", "bn": "{item} স্ক্যান করা হচ্ছে..."},
    "msg_audit_complete": {"en": "Forensic Audit Complete. Found {count} windows.", "hi": "फोरेंसिक ऑडिट पूर्ण। {count} खिड़कियां मिलीं।", "bn": "ফরেনসিক অডিট সম্পূর্ণ। {count} টি উইন্ডো পাওয়া গেছে।"},
    
    # Dasha Related
    "dasha_period": {"en": "Dasha Period", "hi": "दशा अवधि", "bn": "দশা সময়কাল"},
    "dasha_mahadasha": {"en": "Maha Dasha", "hi": "महादशा", "bn": "মহাদশা"},
    "dasha_antardasha": {"en": "Antar Dasha", "hi": "अंतर्दशा", "bn": "অন্তর্দশা"},
    "dasha_pratyantardasha": {"en": "Pratyantar Dasha", "hi": "प्रत्यंतर दशा", "bn": "প্রত্যন্তর দশা"},
    "dasha_sookshma": {"en": "Sookshma Dasha", "hi": "सूक्ष्म दशा", "bn": "সূক্ষ্ম দশা"},
    "dasha_prana": {"en": "Prana Dasha", "hi": "प्राण दशा", "bn": "প্রাণ দশা"},
    "dasha_sandhi": {"en": "⚡ SANDHI JUNCTION: Period starts at dasha boundary (enhanced energy)", "hi": "⚡ संधि जंक्शन: दशा सीमा पर अवधि शुरू (बढ़ी हुई ऊर्जा)", "bn": "⚡ সন্ধি জংশন: দশা সীমায় সময়কাল শুরু (উন্নত শক্তি)"},
    
    # Transit Related
    "transit_check": {"en": "Transit Check", "hi": "गोचर जाँच", "bn": "গোচর পরীক্ষা"},
    "transit_quantum_lock": {"en": "🔒 QUANTUM LOCK: Transit {planet} in SUB of {lord}.", "hi": "🔒 क्वांटम लॉक: गोचर {planet} {lord} के उप में।", "bn": "🔒 কোয়ান্টাম লক: গোচর {planet} {lord}-এর উপে।"},
    "transit_star_lock": {"en": "🔓 STAR LOCK: Transit {planet} in STAR of {lord}.", "hi": "🔓 नक्षत्र लॉक: गोचर {planet} {lord} के नक्षत्र में।", "bn": "🔓 নক্ষত্র লক: গোচর {planet} {lord}-এর নক্ষত্রে।"},
    "transit_identity_lock": {"en": "🔒 IDENTITY LOCK: Transit {planet} IS a {houses} Lord.", "hi": "🔒 पहचान लॉक: गोचर {planet} {houses} भाव का स्वामी है।", "bn": "🔒 পরিচয় লক: গোচর {planet} {houses} ভাবের স্বামী।"},
    "transit_no_link": {"en": "❌ No Link: Transit {planet} - No target house connection.", "hi": "❌ कोई लिंक नहीं: गोचर {planet} - लक्ष्य भाव से कोई संबंध नहीं।", "bn": "❌ কোন লিঙ্ক নেই: গোচর {planet} - লক্ষ্য ভাবের সাথে সংযোগ নেই।"},
    "transit_event_confirmed": {"en": "🔴 EVENT CONFIRMED", "hi": "🔴 घटना की पुष्टि", "bn": "🔴 ইভেন্ট নিশ্চিত"},
    "transit_no_trigger": {"en": "⚪ NO TRIGGER", "hi": "⚪ कोई ट्रिगर नहीं", "bn": "⚪ কোন ট্রিগার নেই"},
    
    # ==========================================================================
    # MARRIAGE MODULE
    # ==========================================================================
    "marriage_title": {"en": "💍 MARRIAGE TIMING AUDIT", "hi": "💍 विवाह समय लेखा परीक्षा", "bn": "💍 বিবাহ টাইমিং অডিট"},
    "marriage_7th_csl": {"en": "7th Cusp Sub-Lord", "hi": "7वां भाव उप-स्वामी", "bn": "৭ম ভাব উপ-স্বামী"},
    "marriage_single": {"en": "SINGLE marriage indicated", "hi": "एकल विवाह संकेतित", "bn": "একক বিবাহ নির্দেশিত"},
    "marriage_multiple": {"en": "MULTIPLE marriages indicated (Dual Sign/Mercury/Multiple Houses)", "hi": "बहु विवाह संकेतित (द्वि-राशि/बुध/बहु-भाव)", "bn": "একাধিক বিবাহ নির্দেশিত (দ্বি-রাশি/বুধ/একাধিক ভাব)"},
    "marriage_no_marriage": {"en": "No Marriage indicated", "hi": "कोई विवाह संकेतित नहीं", "bn": "কোন বিবাহ নির্দেশিত নয়"},
    "marriage_karaka_retro": {"en": "Karaka is Retrograde - delay/break indicated", "hi": "कारक वक्री है - देरी/टूटने का संकेत", "bn": "কারক বক্র - বিলম্ব/ভাঙনের ইঙ্গিত"},
    
    # ==========================================================================
    # LIFE SPAN MODULE
    # ==========================================================================
    "lifespan_title": {"en": "☠️ LIFE SPAN AUDIT - 6-GATE FORENSIC SYSTEM", "hi": "☠️ जीवनकाल लेखा परीक्षा - 6-गेट फोरेंसिक प्रणाली", "bn": "☠️ জীবনকাল অডিট - 6-গেট ফরেনসিক সিস্টেম"},
    "lifespan_alpayu": {"en": "ALPAYU (Short Life: 0-32 years)", "hi": "अल्पायु (अल्प जीवन: 0-32 वर्ष)", "bn": "অল্পায়ু (স্বল্প জীবন: 0-32 বছর)"},
    "lifespan_madhyayu": {"en": "MADHYAYU (Medium Life: 32-64 years)", "hi": "मध्यायु (मध्यम जीवन: 32-64 वर्ष)", "bn": "মধ্যায়ু (মাঝারি জীবন: 32-64 বছর)"},
    "lifespan_purnayu": {"en": "PURNAYU (Long Life: 64-100 years)", "hi": "पूर्णायु (दीर्घ जीवन: 64-100 वर्ष)", "bn": "পূর্ণায়ু (দীর্ঘ জীবন: 64-100 বছর)"},
    "lifespan_death_window": {"en": "Death Window: {start}-{end} years", "hi": "मृत्यु अवधि: {start}-{end} वर्ष", "bn": "মৃত্যু উইন্ডো: {start}-{end} বছর"},
    "lifespan_scan_range": {"en": "Active Scan Range: {start}-{end} years (Age: {age})", "hi": "सक्रिय स्कैन रेंज: {start}-{end} वर्ष (आयु: {age})", "bn": "সক্রিয় স্ক্যান রেঞ্জ: {start}-{end} বছর (বয়স: {age})"},
    "lifespan_no_death": {"en": "No critical death windows detected in the scan range.", "hi": "स्कैन रेंज में कोई गंभीर मृत्यु अवधि नहीं मिली।", "bn": "স্ক্যান রেঞ্জে কোন গুরুতর মৃত্যু উইন্ডো পাওয়া যায়নি।"},
    "lifespan_critical": {"en": "⚠️ CRITICAL DEATH WINDOW DETECTED", "hi": "⚠️ गंभीर मृत्यु अवधि का पता चला", "bn": "⚠️ গুরুতর মৃত্যু উইন্ডো সনাক্ত"},
    
    # ==========================================================================
    # JOB MODULE
    # ==========================================================================
    "job_start_title": {"en": "💼 JOB START TIMING AUDIT", "hi": "💼 नौकरी शुरू समय लेखा परीक्षा", "bn": "💼 চাকরি শুরু টাইমিং অডিট"},
    "job_loss_title": {"en": "📉 JOB LOSS TIMING AUDIT", "hi": "📉 नौकरी छूटने का समय लेखा परीक्षा", "bn": "📉 চাকরি হারানোর টাইমিং অডিট"},
    "job_10th_csl": {"en": "10th Cusp Sub-Lord", "hi": "10वां भाव उप-स्वामी", "bn": "১০ম ভাব উপ-স্বামী"},
    "job_6th_csl": {"en": "6th Cusp Sub-Lord", "hi": "6वां भाव उप-स्वामी", "bn": "৬ষ্ঠ ভাব উপ-স্বামী"},
    "job_government": {"en": "Government Job indicated", "hi": "सरकारी नौकरी संकेतित", "bn": "সরকারি চাকরি নির্দেশিত"},
    "job_private": {"en": "Private Job indicated", "hi": "प्राइवेट नौकरी संकेतित", "bn": "প্রাইভেট চাকরি নির্দেশিত"},
    "job_business": {"en": "Business/Self-Employment indicated", "hi": "व्यापार/स्व-रोजगार संकेतित", "bn": "ব্যবসা/স্ব-কর্মসংস্থান নির্দেশিত"},
    "job_loss_risk": {"en": "Job Loss Risk: {level}", "hi": "नौकरी छूटने का जोखिम: {level}", "bn": "চাকরি হারানোর ঝুঁকি: {level}"},
    "job_confirmed_joining": {"en": "[CONFIRMED] JOB JOINING", "hi": "[पुष्टि] नौकरी में शामिल", "bn": "[নিশ্চিত] চাকরিতে যোগদান"},
    "job_likely_start": {"en": "[LIKELY] JOB START", "hi": "[संभावित] नौकरी शुरू", "bn": "[সম্ভাব্য] চাকরি শুরু"},
    "job_possible_opportunity": {"en": "[POSSIBLE] JOB OPPORTUNITY", "hi": "[संभव] नौकरी का अवसर", "bn": "[সম্ভব] চাকরির সুযোগ"},
    "job_moderate_promise": {"en": "MODERATE PROMISE", "hi": "मध्यम वचन", "bn": "মাঝারি প্রতিশ্রুতি"},
    "job_strong_promise_details": {"en": "6th CSL ({csl_6}) in Source shows {houses}; 10th CSL ({csl_10}) supports", "hi": "6वां सीएसएल ({csl_6}) स्रोत में {houses} दर्शाता है; 10वां सीएसएल ({csl_10}) समर्थन करता है", "bn": "৬ষ্ঠ সিএসএল ({csl_6}) উৎসে {houses} দেখায়; ১০ম সিএসএল ({csl_10}) সমর্থন করে"},
    "job_obstacles_details": {"en": "6th CSL ({csl}) shows job but also 12 in Source Row >>> Delays/struggles", "hi": "6वां सीएसएल ({csl}) नौकरी दर्शाता है लेकिन स्रोत पंक्ति में 12 भी है >>> देरी/संघर्ष", "bn": "৬ষ্ঠ সিএসএল ({csl}) চাকরি দেখায় কিন্তু উৎস সারিতে ১২ও আছে >>> বিলম্ব/সংগ্রাম"},
    "job_weak_promise_details": {"en": "Neither 6th nor 10th CSL show job houses in Source Row", "hi": "न तो 6वां और न ही 10वां सीएसएल स्रोत पंक्ति में नौकरी भाव दर्शाता है", "bn": "৬ষ্ঠ বা ১০ম সিএসএল কেউই উৎস সারিতে চাকরি ভাব দেখায় না"},
    
    # ==========================================================================
    # CHILD BIRTH MODULE
    # ==========================================================================
    "child_title": {"en": "👶 CHILD BIRTH TIMING AUDIT", "hi": "👶 संतान जन्म समय लेखा परीक्षा", "bn": "👶 সন্তান জন্ম টাইমিং অডিট"},
    "child_5th_csl": {"en": "5th Cusp Sub-Lord", "hi": "5वां भाव उप-स्वामी", "bn": "৫ম ভাব উপ-স্বামী"},
    "child_possible": {"en": "Child Birth is POSSIBLE", "hi": "संतान संभव है", "bn": "সন্তান সম্ভব"},
    "child_not_possible": {"en": "Child Birth is NOT POSSIBLE", "hi": "संतान संभव नहीं है", "bn": "সন্তান সম্ভব নয়"},
    "child_son": {"en": "SON indicated", "hi": "पुत्र संकेतित", "bn": "পুত্র নির্দেশিত"},
    "child_daughter": {"en": "DAUGHTER indicated", "hi": "पुत्री संकेतित", "bn": "কন্যা নির্দেশিত"},
    "child_multiple": {"en": "Multiple children indicated", "hi": "एकाधिक संतान संकेतित", "bn": "একাধিক সন্তান নির্দেশিত"},
    "child_multiple_prob": {"en": "MULTIPLE CHILDREN", "hi": "एकाधिक संतान", "bn": "একাধিক সন্তান"},
    "child_single_delayed": {"en": "SINGLE/DELAYED CHILD", "hi": "एकल/विलंबित संतान", "bn": "একক/বিলম্বিত সন্তান"},
    "child_moderate": {"en": "MODERATE", "hi": "मध्यम", "bn": "মাঝারি"},
    
    # ==========================================================================
    # WEALTH MODULE
    # ==========================================================================
    "wealth_gain_title": {"en": "💰 WEALTH GAIN TIMING AUDIT", "hi": "💰 धन लाभ समय लेखा परीक्षा", "bn": "💰 ধন লাভ টাইমিং অডিট"},
    "wealth_loss_title": {"en": "📉 WEALTH LOSS TIMING AUDIT", "hi": "📉 धन हानि समय लेखा परीक्षा", "bn": "📉 ধন ক্ষতি টাইমিং অডিট"},
    "wealth_2nd_csl": {"en": "2nd Cusp Sub-Lord", "hi": "2वां भाव उप-स्वामी", "bn": "২য় ভাব উপ-স্বামী"},
    "wealth_11th_csl": {"en": "11th Cusp Sub-Lord", "hi": "11वां भाव उप-स्वामी", "bn": "১১শ ভাব উপ-স্বামী"},
    "wealth_gain_strong": {"en": "Strong Wealth Gain indicated", "hi": "मजबूत धन लाभ संकेतित", "bn": "শক্তিশালী ধন লাভ নির্দেশিত"},
    "wealth_loss_risk": {"en": "Wealth Loss Risk: {level}", "hi": "धन हानि जोखिम: {level}", "bn": "ধন ক্ষতির ঝুঁকি: {level}"},
    "wealth_major_event": {"en": "💰 MAJOR WEALTH EVENT (Score: {score})", "hi": "💰 प्रमुख धन घटना (स्कोर: {score})", "bn": "💰 প্রধান ধন ইভেন্ট (স্কোর: {score})"},
    "wealth_significant_gain": {"en": "✅ SIGNIFICANT GAIN WINDOW (Score: {score})", "hi": "✅ महत्वपूर्ण लाभ अवधि (स्कोर: {score})", "bn": "✅ উল্লেখযোগ্য লাভের সময়কাল (স্কোর: {score})"},
    "wealth_moderate_gain": {"en": "MODERATE GAIN WINDOW (Score: {score})", "hi": "मध्यम लाभ अवधि (स्कोर: {score})", "bn": "মাঝারি লাভের সময়কাল (স্কোর: {score})"},
    "wealth_possible_gain": {"en": "POSSIBLE GAIN (Score: {score})", "hi": "संभावित लाभ (स्कोर: {score})", "bn": "সম্ভাব্য লাভ (স্কোর: {score})"},
    "wealth_major_loss": {"en": "⚠️ MAJOR LOSS EVENT (Score: {score})", "hi": "⚠️ प्रमुख हानि घटना (स्कोर: {score})", "bn": "⚠️ প্রধান ক্ষতি ইভেন্ট (স্কোর: {score})"},
    "wealth_significant_loss": {"en": "⚠️ SIGNIFICANT LOSS WINDOW (Score: {score})", "hi": "⚠️ महत्वपूर्ण हानि अवधि (स्कोर: {score})", "bn": "⚠️ উল্লেখযোগ্য ক্ষতির সময়কাল (স্কোর: {score})"},
    "wealth_moderate_loss": {"en": "MODERATE LOSS WINDOW (Score: {score})", "hi": "मध्यम हानि अवधि (स्कोर: {score})", "bn": "মাঝারি ক্ষতির সময়কাল (স্কোর: {score})"},
    "wealth_possible_loss": {"en": "POSSIBLE LOSS (Score: {score})", "hi": "संभावित हानि (स्कोर: {score})", "bn": "সম্ভাব্য ক্ষতি (স্কোর: {score})"},
    "wealth_loss_significant": {"en": "Significant loss events likely during adverse periods", "hi": "प्रतिकूल अवधियों में महत्वपूर्ण हानि घटनाएं संभव", "bn": "প্রতিকূল সময়ে উল্লেখযোগ্য ক্ষতির ঘটনা সম্ভব"},
    "wealth_loss_periodic": {"en": "Periodic financial stress possible", "hi": "समयिक वित्तीय तनाव संभव", "bn": "পর্যায়ক্রমিক আর্থিক চাপ সম্ভব"},
    "wealth_loss_protected": {"en": "Generally protected from major losses", "hi": "आमतौर पर बड़ी हानि से सुरक्षित", "bn": "সাধারণত বড় ক্ষতি থেকে সুরক্ষিত"},
    
    # ==========================================================================
    # COURT CASE MODULE
    # ==========================================================================
    "court_title": {"en": "⚖️ COURT CASE TIMING AUDIT", "hi": "⚖️ कोर्ट केस समय लेखा परीक्षा", "bn": "⚖️ কোর্ট কেস টাইমিং অডিট"},
    "court_6th_csl": {"en": "6th Cusp Sub-Lord (Litigation)", "hi": "6वां भाव उप-स्वामी (मुकदमेबाजी)", "bn": "৬ষ্ঠ ভাব উপ-স্বামী (মামলা)"},
    "court_case_indicated": {"en": "Court Case/Litigation indicated", "hi": "कोर्ट केस/मुकदमेबाजी संकेतित", "bn": "কোর্ট কেস/মামলা নির্দেশিত"},
    "court_no_case": {"en": "No significant court case indicated", "hi": "कोई महत्वपूर्ण कोर्ट केस संकेतित नहीं", "bn": "কোন উল্লেখযোগ্য কোর্ট কেস নির্দেশিত নয়"},
    "court_win": {"en": "Victory in Court Case likely", "hi": "कोर्ट केस में जीत की संभावना", "bn": "কোর্ট কেসে জয় সম্ভাব্য"},
    "court_loss": {"en": "Loss in Court Case likely", "hi": "कोर्ट केस में हार की संभावना", "bn": "কোর্ট কেসে হার সম্ভাব্য"},
    "court_severity_severe": {"en": "⚠️ SEVERE", "hi": "⚠️ गंभीर", "bn": "⚠️ গুরুতর"},
    "court_severity_high": {"en": "HIGH", "hi": "उच्च", "bn": "উচ্চ"},
    "court_severity_moderate": {"en": "MODERATE", "hi": "मध्यम", "bn": "মাঝারি"},
    "court_severity_low": {"en": "LOW", "hi": "कम", "bn": "কম"},
    
    # ==========================================================================
    # DIVORCE MODULE
    # ==========================================================================
    "divorce_title": {"en": "💔 DIVORCE/WIDOWED TIMING AUDIT", "hi": "💔 तलाक/विधवा समय लेखा परीक्षा", "bn": "💔 বিবাহ বিচ্ছেদ/বৈধব্য টাইমিং অডিট"},
    "divorce_indicated": {"en": "Divorce is indicated", "hi": "तलाक संकेतित है", "bn": "বিবাহ বিচ্ছেদ নির্দেশিত"},
    "divorce_not_indicated": {"en": "Divorce is NOT indicated", "hi": "तलाक संकेतित नहीं है", "bn": "বিবাহ বিচ্ছেদ নির্দেশিত নয়"},
    "widowed_risk": {"en": "Widowhood Risk: {level}", "hi": "विधवा होने का जोखिम: {level}", "bn": "বৈধব্য ঝুঁকি: {level}"},
    "divorce_legal_sep": {"en": "LEGAL SEPARATION / DIVORCE", "hi": "कानूनी अलगाव / तलाक", "bn": "আইনি বিচ্ছেদ / বিবাহ বিচ্ছেদ"},
    "divorce_widowhood_exit": {"en": "WIDOWHOOD / PERMANENT EXIT", "hi": "विधवापन / स्थायी विदाई", "bn": "বৈধব্য / স্থায়ী প্রস্থান"},
    "divorce_strife": {"en": "SEVERE CONFLICT / TEMPORARY SPLIT", "hi": "गंभीर संघर्ष / अस्थायी अलगाव", "bn": "গুরুতর দ্বন্দ্ব / অস্থায়ী বিচ্ছেদ"},
    "divorce_stable": {"en": "NO SEPARATION DETECTED", "hi": "कोई अलगाव नहीं मिला", "bn": "কোন বিচ্ছেদ সনাক্ত হয়নি"},
    "divorce_marital_crisis": {"en": "MARITAL_CRISIS", "hi": "वैवाहिक संकट", "bn": "বৈবাহিক সংকট"},
    "severity_critical": {"en": "CRITICAL", "hi": "गंभीर", "bn": "গুরুতর"},
    
    # ==========================================================================
    # HOSPITALIZATION MODULE
    # ==========================================================================
    "hospital_title": {"en": "🏥 HOSPITALIZATION TIMING AUDIT", "hi": "🏥 अस्पताल में भर्ती समय लेखा परीक्षा", "bn": "🏥 হাসপাতালে ভর্তি টাইমিং অডিট"},
    "hospital_12th_csl": {"en": "12th Cusp Sub-Lord (Hospitalization)", "hi": "12वां भाव उप-स्वामी (अस्पताल में भर्ती)", "bn": "১২শ ভাব উপ-স্বামী (হাসপাতালে ভর্তি)"},
    "hospital_risk": {"en": "Hospitalization Risk: {level}", "hi": "अस्पताल में भर्ती जोखिम: {level}", "bn": "হাসপাতালে ভর্তি ঝুঁকি: {level}"},
    "hospital_surgery": {"en": "Surgery indicated", "hi": "सर्जरी संकेतित", "bn": "সার্জারি নির্দেশিত"},
    "hospital_recovery": {"en": "Recovery likely", "hi": "ठीक होने की संभावना", "bn": "সুস্থতা সম্ভাব্য"},
    "hospital_certain": {"en": "CERTAIN ADMISSION", "hi": "निश्चित भर्ती", "bn": "নিশ্চিত ভর্তি"},
    "hospital_home": {"en": "HOME REST / OBSERVATION", "hi": "घर पर आराम / निगरानी", "bn": "বাড়িতে বিশ্রাম / পর্যবেক্ষণ"},
    "hospital_critical": {"en": "CRITICAL SURGERY", "hi": "गंभीर सर्जरी", "bn": "গুরুতর সার্জারি"},
    "hospital_vulnerable_verdict": {"en": "VULNERABLE", "hi": "कमजोर", "bn": "ঝুঁকিপূর্ণ"},
    "hospital_protected_verdict": {"en": "PROTECTED", "hi": "सुरक्षित", "bn": "সুরক্ষিত"},
    "hospital_neutral_verdict": {"en": "NEUTRAL", "hi": "तटस्थ", "bn": "নিরপেক্ষ"},
    
    "hospital_start_vulnerable": {"en": "⚠️ VULNERABLE: 1st CSL ({csl}) connects to {houses}.", "hi": "⚠️ कमजोर: 1st CSL ({csl}) {houses} से जुड़ता है।", "bn": "⚠️ ঝুঁকিপূর্ণ: 1st CSL ({csl}) {houses}-এর সাথে যুক্ত।"},
    "hospital_start_protected": {"en": "🛡️ PROTECTED: 1st CSL ({csl}) connects to Life Force {houses}.", "hi": "🛡️ सुरक्षित: 1st CSL ({csl}) जीवन शक्ति {houses} से जुड़ता है।", "bn": "🛡️ সুরক্ষিত: 1st CSL ({csl}) জীবন শক্তি {houses}-এর সাথে যুক্ত।"},
    "vehicle_verdict_blocked": {"en": "BLOCKED", "hi": "अवरुद्ध", "bn": "অবরুদ্ধ"},
    "vehicle_verdict_risky": {"en": "RISKY", "hi": "जोखिम भरा", "bn": "ঝুঁকিপূর্ণ"},
    "vehicle_verdict_promised": {"en": "PROMISED", "hi": "वचनबद्ध", "bn": "প্রতিশ্রুত"},
    "vehicle_verdict_denied": {"en": "DENIED", "hi": "अस्वीकृत", "bn": "প্রত্যাখ্যাত"},
    "vehicle_core_trigger": {"en": "✅ Core Trigger: 4th (Vehicle) + 11th (Gain) active", "hi": "✅ मुख्य ट्रिगर: चौथा (वाहन) + 11वां (लाभ) सक्रिय", "bn": "✅ মূল ট্রিগার: ৪র্থ (যানবাহন) + ১১শ (লাভ) সক্রিয়"},
    "vehicle_partial_4": {"en": "⚠️ Partial Trigger: 4th active but 11th missing", "hi": "⚠️ आंशिक ट्रिगर: चौथा सक्रिय लेकिन 11वां गायब", "bn": "⚠️ আংশিক ট্রিগার: ৪র্থ সক্রিয় কিন্তু ১১শ অনুপস্থিত"},
    "vehicle_partial_11": {"en": "⚠️ Partial Trigger: 11th active but 4th missing", "hi": "⚠️ आंशिक ट्रिगर: 11वां सक्रिय लेकिन चौथा गायब", "bn": "⚠️ আংশিক ট্রিগার: ১১শ সক্রিয় কিন্তু ৪র্থ অনুপস্থিত"},
    "vehicle_payment_2": {"en": "💰 Payment: 2nd House (Self Wealth)", "hi": "💰 भुगतान: दूसरा घर (स्वयं का धन)", "bn": "💰 পেমেন্ট: ২য় ভাব (নিজস্ব সম্পদ)"},
    "vehicle_payment_6": {"en": "🏦 Payment: 6th House (Loan/EMI)", "hi": "🏦 भुगतान: छठा घर (ऋण/ईएमआई)", "bn": "🏦 পেমেন্ট: ৬ষ্ঠ ভাব (ঋণ/ইএমআই)"},
    "vehicle_weak_payment": {"en": "⚠️ Weak Payment: Funding issue?", "hi": "⚠️ कमजोर भुगतान: फंडिंग की समस्या?", "bn": "⚠️ দুর্বল পেমেন্ট: ফাউন্ডিং সমস্যা?"},
    "vehicle_luck": {"en": "🍀 Luck: 9th House supports", "hi": "🍀 भाग्य: 9वां घर समर्थन करता है", "bn": "🍀 ভাগ্য: ৯ম ভাব সমর্থন করে"},
    "vehicle_blocker_3": {"en": "🛑 Blocker: 3rd House (Destruction of 4th)", "hi": "🛑 अवरोधक: तीसरा घर (तीसरे घर का विनाश)", "bn": "🛑 ব্লকার: ৩য় ভাব (৪র্থ ভাবের বিনাশ)"},
    "vehicle_warning_8": {"en": "⚠️ Warning: 8th House active (Accident risk)", "hi": "⚠️ चेतावनी: 8वां घर सक्रिय (दुर्घटना जोखिम)", "bn": "⚠️ সতর্কতা: ৮ম ভাব সক্রিয় (দুর্ঘটনা ঝুঁকি)"},
    "vehicle_expenditure": {"en": "💸 Expenditure: 12th active", "hi": "💸 व्यय: 12वां सक्रिय", "bn": "💸 ব্যয়: ১২শ সক্রিয়"},
    "vehicle_loss_regret": {"en": "❌ Loss: 12th active without gain", "hi": "❌ हानि: लाभ के बिना 12वां सक्रिय", "bn": "❌ ক্ষতি: লাভ ছাড়া ১২শ সক্রিয়"},
    "vehicle_best_combo": {"en": "🌟 BEST COMBO: 4 + 11 + 2", "hi": "🌟 सर्वोत्तम संयोजन: 4 + 11 + 2", "bn": "🌟 সেরা কম্বো: ৪ + ১১ + ২"},
    "vehicle_loan": {"en": "📝 Loan Indicated (4 + 6)", "hi": "📝 ऋण संकेतित (4 + 6)", "bn": "📝 ঋণ নির্দেশিত (৪ + ৬)"},
    "vehicle_second_hand": {"en": "🔄 Possible Second-Hand Vehicle (4 + 8)", "hi": "🔄 संभावित सेकेंड हैंड वाहन (4 + 8)", "bn": "🔄 সম্ভাব্য সেকেন্ড হ্যান্ড যানবাহন (৪ + ৮)"},
    "vehicle_transit_jupiter_4": {"en": "Jupiter aspects 4th CSL {csl} (Blessing)", "hi": "बृहस्पति 4th CSL {csl} को देखता है (आशीर्वाद)", "bn": "বৃহস্পতি ৪র্থ CSL {csl}-কে দেখে (আশীর্বাদ)"},
    "vehicle_transit_saturn_4": {"en": "Saturn aspects 4th CSL {csl} (Materializing)", "hi": "शनि 4th CSL {csl} को देखता है (साकार)", "bn": "শনি ৪র্থ CSL {csl}-কে দেখে (বাস্তবায়ন)"},
    "vehicle_transit_jupiter_11": {"en": "Jupiter aspects 11th CSL {csl} (Gain)", "hi": "बृहस्पति 11th CSL {csl} को देखता है (लाभ)", "bn": "বৃহস্পতি ১১শ CSL {csl}-কে দেখে (লাভ)"},

    # ==========================================================================
    # JOB LOSS MODULE
    # ==========================================================================
    "job_loss_sev_confirmed": {"en": "[EXIT CONFIRMED] JOB LOSS", "hi": "[निकास पुष्टि] नौकरी समाप्त", "bn": "[প্রস্থান নিশ্চিত] চাকরি শেষ"},
    "job_loss_sev_likely": {"en": "[LIKELY] JOB EXIT", "hi": "[संभावित] नौकरी निकास", "bn": "[সম্ভাব্য] চাকরি প্রস্থান"},
    "job_loss_sev_possible": {"en": "[POSSIBLE] JOB RISK", "hi": "[संभव] नौकरी जोखिम", "bn": "[সম্ভব] চাকরি ঝুঁকি"},
    "job_loss_sev_watch": {"en": "[WATCH] JOB STRESS", "hi": "[निगरानी] नौकरी तनाव", "bn": "[নজরদারি] চাকরি চাপ"},
    
    "job_loss_type_sudden": {"en": "🔴 SUDDEN TERMINATION", "hi": "🔴 अचानक बर्खास्तगी", "bn": "🔴 হঠাৎ ছাঁটাই"},
    "job_loss_type_forced": {"en": "🟠 FORCED RESIGNATION", "hi": "🟠 जबरन इस्तीफा", "bn": "🟠 জোরপূর্বক পদত্যাগ"},
    "job_loss_type_layoff": {"en": "🟡 LAYOFF / DOWNSIZING", "hi": "🟡 छंटनी / डाउनसाइजिंग", "bn": "🟡 ছাঁটাই / আকার হ্রাস"},
    "job_loss_type_end": {"en": "🔻 JOB END", "hi": "🔻 नौकरी समाप्त", "bn": "🔻 চাকুরির সমাপ্তি"},
    "job_loss_type_stress": {"en": "⚠️ JOB STRESS", "hi": "⚠️ नौकरी तनाव", "bn": "⚠️ চাকুরির চাপ"},
    "job_loss_type_uncertain": {"en": "📊 UNCERTAIN", "hi": "📊 अनिश्चित", "bn": "📊 অনিশ্চিত"},

    "job_loss_fp_leave": {"en": "FALSE POSITIVE: Both 12th and 6th in Source → Leave/Travel", "hi": "गलत सकारात्मक: 12वां और छठा दोनों स्रोत में → छुट्टी/यात्रा", "bn": "ফলস পজিটিভ: ১২শ এবং ৬ষ্ঠ উভয়ই উৎসে → ছুটি/ভ্রমণ"},
    "job_loss_fp_politics": {"en": "FALSE POSITIVE: 10th + 8th stress but 6th protected", "hi": "गलत सकारात्मक: 10वां + 8वां तनाव लेकिन छठा सुरक्षित", "bn": "ফলস পজিটিভ: ১০ম + ৮ম চাপ কিন্তু ৬ষ্ঠ সুরক্ষিত"},
    "job_loss_fp_salary": {"en": "FALSE POSITIVE: 11th absent but 6th strong", "hi": "गलत सकारात्मक: 11वां अनुपस्थित लेकिन छठा मजबूत", "bn": "ফলস পজিটিভ: ১১শ অনুপস্থিত কিন্তু ৬ষ্ঠ শক্তিশালী"},
    "job_loss_fp_foreign": {"en": "FALSE POSITIVE: 12th + 3rd + 9th + 6th → Foreign Assignment", "hi": "गलत सकारात्मक: 12+3+9+6 → विदेशी कार्य", "bn": "ফলস পজিটিভ: ১২+৩+৯+৬ → বিদেশী কাজ"},
    
    "job_loss_veto_strong": {"en": "🛡️ PD VETO: {pd} strongly protects job", "hi": "🛡️ PD वीटो: {pd} नौकरी की दृढ़ता से रक्षा करता है", "bn": "🛡️ PD ভেটো: {pd} চাকরিকে দৃঢ়ভাবে রক্ষা করে"},
    "job_loss_veto_6th": {"en": "🛡️ PD VETO: {pd} protects 6th house", "hi": "🛡️ PD वीटो: {pd} छठे घर की रक्षा करता है", "bn": "🛡️ PD ভেটো: {pd} ৬ষ্ঠ ভাব রক্ষা করে"},
    
    "job_loss_gate1_reject": {"en": "REJECTED: Without 12th activation, no exit", "hi": "अस्वीकृत: 12वें सक्रियण के बिना, कोई निकास नहीं", "bn": "প্রত্যাখ্যাত: ১২শ সক্রিয়করণ ছাড়া, কোন প্রস্থান নেই"},
    "job_loss_gate4_new": {"en": "⚠️ NEW JOB FORMING: This may be job CHANGE", "hi": "⚠️ नई नौकरी बन रही है: यह नौकरी परिवर्तन हो सकता है", "bn": "⚠️ নতুন চাকরি তৈরি হচ্ছে: এটি চাকরি পরিবর্তন হতে পারে"},

    # Job Loss Detail Messages
    "job_loss_11_collapsed": {"en": "11th destroyed by 12th + absent in Source → COMPLETE INCOME BREAK", "hi": "11वां 12वें द्वारा नष्ट + स्रोत में अनुपस्थित → पूर्ण आय विघटन", "bn": "১১শ ১২শ দ্বারা ধ্বংস + উৎসে অনুপস্থিত → সম্পূর্ণ আয় ভঙ্গ"},
    "job_loss_11_protected": {"en": "11th in Source Row → Income continues despite job loss", "hi": "स्रोत पंक्ति में 11वां → नौकरी छूटने के बावजूद आय जारी", "bn": "উৎস সারিতে ১১শ → চাকরি হারানো সত্ত্বেও আয় অব্যাহত"},
    "job_loss_11_weak": {"en": "11th only in Result → Temporary income, may stop eventually", "hi": "11वां केवल परिणाम में → अस्थायी आय, अंततः रुक सकती है", "bn": "১১শ শুধুমাত্র ফলাফলে → অস্থায়ী আয়, শেষ পর্যন্ত বন্ধ হতে পারে"},
    "job_loss_11_absent": {"en": "11th not signified → No income stability backup", "hi": "11वां संकेतित नहीं → कोई आय स्थिरता बैकअप नहीं", "bn": "১১শ নির্দেশিত নয় → কোন আয় স্থায়িত্ব ব্যাকআপ নেই"},
    "job_loss_11_stable": {"en": "11th house income continuity maintained", "hi": "11वें घर की आय निरंतरता बनी हुई है", "bn": "১১শ ভাবের আয় ধারাবাহিকতা বজায় আছে"},
    
    "job_loss_retro_generic": {"en": "{role} ({lord}) RETROGRADE: Exit pattern altered", "hi": "{role} ({lord}) वक्री: निकास पैटर्न बदला", "bn": "{role} ({lord}) বক্রী: প্রস্থান প্যাটার্ন পরিবর্তিত"},
    "job_loss_retro_jupiter": {"en": "{role} ({lord}) RETROGRADE: Protection may fail unexpectedly", "hi": "{role} ({lord}) वक्री: सुरक्षा अप्रत्याशित रूप से विफल हो सकती है", "bn": "{role} ({lord}) বক্রী: সুরক্ষা অপ্রত্যাশিতভাবে ব্যর্থ হতে পারে"},
    "job_loss_retro_mercury": {"en": "{role} ({lord}) RETROGRADE: Contract/communication issues", "hi": "{role} ({lord}) वक्री: अनुबंध/संचार मुद्दे", "bn": "{role} ({lord}) বক্রী: চুক্তি/যোগাযোগ সমস্যা"},
    "job_loss_retro_none": {"en": "No retrograde planets in dasha sequence", "hi": "दशा क्रम में कोई वक्री ग्रह नहीं", "bn": "দশা ক্রমানুসারে কোন বক্রী গ্রহ নেই"},

    "job_loss_12_absent": {"en": "12th NOT signified - No exit trigger possible", "hi": "12वां संकेतित नहीं - कोई निकास ट्रिगर संभव नहीं", "bn": "১২শ নির্দেশিত নয় - কোন প্রস্থান ট্রিগার সম্ভব নয়"},
    "job_loss_12_armed": {"en": "12th in Source WITH 6th connection - EXIT TRIGGER ARMED", "hi": "6वें कनेक्शन के साथ 12वां स्रोत में - निकास ट्रिगर तैयार", "bn": "৬ষ্ঠ সংযোগের সাথে ১২শ উৎসে - প্রস্থান ট্রিগার প্রস্তুত"},
    "job_loss_12_moderate": {"en": "12th in Source Row - Exit energy present", "hi": "12वां स्रोत पंक्ति में - निकास ऊर्जा उपस्थित", "bn": "১২শ উৎস সারিতে - প্রস্থান শক্তি উপস্থিত"},
    "job_loss_12_weak": {"en": "12th in Result only - Exit possible but not primary", "hi": "12वां केवल परिणाम में - निकास संभव लेकिन प्राथमिक नहीं", "bn": "১২শ শুধুমাত্র ফলাফলে - প্রস্থান সম্ভব কিন্তু প্রাথমিক নয়"},
    "job_loss_12_ineffective": {"en": "12th not effectively activated", "hi": "12वां प्रभावी रूप से सक्रिय नहीं", "bn": "১২শ কার্যকরভাবে সক্রিয় নয়"},

    "job_loss_6_destroyed": {"en": "12th active + 6th NOT in Source → SERVICE CONTRACT DESTROYED", "hi": "12वां सक्रिय + 6ठा स्रोत में नहीं → सेवा अनुबंध नष्ट", "bn": "১২শ সক্রিয় + ৬ষ্ঠ উৎসে নেই → পরিষেবা চুক্তি ধ্বংস"},
    "job_loss_6_eroded": {"en": "12th attacking, 6th only in Result → Job security eroding", "hi": "12वां हमलावर, 6ठा केवल परिणाम में → नौकरी सुरक्षा क्षरण", "bn": "১২শ আক্রমণ করছে, ৬ষ্ঠ শুধুমাত্র ফলাফলে → চাকরি নিরাপত্তা ক্ষয়"},
    "job_loss_6_absent": {"en": "6th NOT signified at all → No job structure present", "hi": "6ठा बिल्कुल संकेतित नहीं → कोई नौकरी संरचना मौजूद नहीं", "bn": "৬ষ্ঠ আদৌ নির্দেশিত নয় → কোন চাকরি কাঠামো উপস্থিত নেই"},
    "job_loss_6_overpowered": {"en": "6th Protected but 12th + 8th shock → Defense collapsed", "hi": "6ठा सुरक्षित लेकिन 12वां + 8वां झटका → रक्षा ध्वस्त", "bn": "৬ষ্ঠ সুরক্ষিত কিন্তু ১২শ + ৮ম আঘাত → প্রতিরক্ষা ধসে"},
    "job_loss_6_contested": {"en": "6th in Source but 12th also active → Job change possible", "hi": "6ठा स्रोत में लेकिन 12वां भी सक्रिय → नौकरी परिवर्तन संभव", "bn": "৬ষ্ঠ উৎসে কিন্তু ১২শও সক্রিয় → চাকরি পরিবর্তন সম্ভব"},
    "job_loss_6_protected": {"en": "6th in Source Row → Job structure intact, protected", "hi": "6ठा स्रोत पंक्ति में → नौकरी संरचना अक्षुण्ण, सुरक्षित", "bn": "৬ষ্ঠ উৎস সারিতে → চাকরি কাঠামো অক্ষত, সুরক্ষিত"},
    "job_loss_6_weak": {"en": "6th only in Result + no 10th support → Job stress", "hi": "6ठा केवल परिणाम में + कोई 10वां समर्थन नहीं → नौकरी तनाव", "bn": "৬ষ্ঠ শুধুমাত্র ফলাফলে + কোন ১০ম সমর্থন নেই → চাকরি চাপ"},
    "job_loss_6_stable": {"en": "6th structure maintained", "hi": "6ठा संरचना बनाए रखा", "bn": "৬ষ্ঠ কাঠামো বজায় রাখা"},

    "job_loss_10_destroyed": {"en": "Role abolished - Sudden organizational action", "hi": "भूमिका समाप्त - अचानक संगठनात्मक कार्रवाई", "bn": "ভূমিকা বিলুপ্তি - হঠাৎ সাংগঠনিক পদক্ষেপ"},
    "job_loss_10_rigid": {"en": "Authority clash - Forced exit from position", "hi": "अधिकार टकराव - पद से जबरन निकास", "bn": "কর্তৃত্বের সংঘাত - পদ থেকে জোরপূর্বক প্রস্থান"},
    "job_loss_10_absent": {"en": "No 10th signification - No authority/role protection", "hi": "कोई 10वां संकेत नहीं - कोई अधिकार/भूमिका संरक्षण नहीं", "bn": "কোন ১০ম নির্দেশক নেই - কোন কর্তৃত্ব/ভূমিকা সুরক্ষা নেই"},
    "job_loss_10_supported": {"en": "10th + 6th in Source - Strong role protection", "hi": "स्रोत में 10वां + 6ठा - मजबूत भूमिका संरक्षण", "bn": "উৎসে ১০ম + ৬ষ্ঠ - শক্তিশালী ভূমিকা সুরক্ষা"},
    "job_loss_10_strong": {"en": "10th in Source - Good authority support", "hi": "स्रोत में 10वां - अच्छा अधिकार समर्थन", "bn": "উৎসে ১০ম - ভালো কর্তৃত্ব সমর্থন"},
    "job_loss_10_neutral": {"en": "10th status unclear", "hi": "10वीं स्थिति अस्पष्ट", "bn": "১০ম স্থিতি অস্পষ্ট"},

    "job_loss_gate4_new_forming": {"en": "NEW 6TH FORMING: 6th in Source → Job transition", "hi": "नया 6ठा बन रहा है: स्रोत में 6ठा → नौकरी संक्रमण", "bn": "নতুন ৬ষ্ঠ তৈরি হচ্ছে: উৎসে ৬ষ্ঠ → চাকরি পরিবর্তন"},
    "job_loss_gate4_next_switch": {"en": "NEXT AD SWITCH: Current period lacks 6th, but next AD has 6th", "hi": "अगला AD स्विच: वर्तमान अवधि में 6ठा नहीं, लेकिन अगले AD में है", "bn": "পরবর্তী AD সুইচ: বর্তমান সময়ে ৬ষ্ঠ নেই, কিন্তু পরবর্তী AD-তে আছে"},
    "job_loss_gate4_next_opportunity": {"en": "NEXT AD OPPORTUNITY: Next AD has opportunity houses", "hi": "अगला AD अवसर: अगले AD में अवसर घर हैं", "bn": "পরবর্তী AD সুযোগ: পরবর্তী AD-তে সুযোগের ভাব আছে"},
    "job_loss_gate4_alternate": {"en": "ALTERNATE PATH: 3rd + 9th active → New opportunity", "hi": "वैकल्पिक पथ: 3सरा + 9वां सक्रिय → नया अवसर", "bn": "বিকল্প পথ: ৩য় + ৯ম সক্রিয় → নতুন সুযোগ"},
    "job_loss_gate4_business": {"en": "BUSINESS ALTERNATE: 7th active → Possible business transition", "hi": "व्यापार विकल्प: 7वां सक्रिय → संभावित व्यापार संक्रमण", "bn": "ব্যবসায়িক বিকল্প: ৭ম সক্রিয় → সম্ভাব্য ব্যবসায়িক পরিবর্তন"},
    "job_loss_gate4_independent": {"en": "INDEPENDENT PATH: 5th + 9th → Self-employment", "hi": "स्वतंत्र पथ: 5वां + 9वां → स्वरोजगार", "bn": "স্বাধীন পথ: ৫ম + ৯ম → স্ব-কর্মসংস্থান"},
    "job_loss_gate4_none": {"en": "NO ALTERNATE: No new 6th forming → TRUE JOB LOSS", "hi": "कोई विकल्प नहीं: कोई नया 6ठा नहीं बन रहा → सच्ची नौकरी हानि", "bn": "কোন বিকল্প নেই: নতুন ৬ষ্ঠ তৈরি হচ্ছে না → প্রকৃত চাকরি ক্ষতি"},

    "job_loss_timing_12": {"en": "12th Lord ({lord}) is Dasha lord - PRIMARY EXIT TRIGGER", "hi": "12वां स्वामी ({lord}) दशा स्वामी है - प्राथमिक निकास ट्रिगर", "bn": "১২শ অধিপতি ({lord}) দশা অধিপতি - প্রাথমিক প্রস্থান ট্রিগার"},
    "job_loss_timing_6": {"en": "6th Lord ({lord}) running with destruction - Job structure attack", "hi": "6ठा स्वामी ({lord}) विनाश के साथ - नौकरी संरचना पर हमला", "bn": "৬ষ্ঠ অধিপতি ({lord}) বিনাশের সাথে - চাকরি কাঠামোতে আঘাত"},
    "job_loss_timing_10": {"en": "10th Lord ({lord}) + 12th signification - Authority action", "hi": "10वां स्वामी ({lord}) + 12वां संकेत - अधिकार कार्रवाई", "bn": "১০ম অধিপতি ({lord}) + ১২শ নির্দেশক - কর্তৃপক্ষ পদক্ষেপ"},

    # Marriage Timing Detail Keys
    "marriage_negation_6": {"en": "❌ NEGATION (Separation House 6 active)", "hi": "❌ निषेध (अलगाव घर 6 सक्रिय)", "bn": "❌ নেতিবাচক (বিচ্ছেদ ভাব ৬ সক্রিয়)"},
    "marriage_obstacle_10": {"en": "⚠️ OBSTACLE (House 10 active)", "hi": "⚠️ बाधा (घर 10 सक्रिय)", "bn": "⚠️ বাধা (ভাব ১০ সক্রিয়)"},
    "marriage_status_golden": {"en": "🎯 GOLDEN WINDOW (Certain Event)", "hi": "🎯 सुनहरा अवसर (निश्चित घटना)", "bn": "🎯 সুবর্ণ সুযোগ (নিশ্চিত ঘটনা)"},
    "marriage_status_high": {"en": "✅ HIGH PROBABILITY", "hi": "✅ उच्च संभावना", "bn": "✅ উচ্চ সম্ভাবনা"},
    "marriage_status_possible": {"en": "🟡 POSSIBLE (Requires Transit)", "hi": "🟡 संभव (गोचर आवश्यक)", "bn": "🟡 সম্ভব (গোচর প্রয়োজন)"},
    "marriage_status_low": {"en": "⚪ LOW PROBABILITY", "hi": "⚪ कम संभावना", "bn": "⚪ কম সম্ভাবনা"},
    "marriage_g5_missing_lords": {"en": "⚠️ G5: Missing Natal 2/11 Lords", "hi": "⚠️ G5: जन्म 2/11 स्वामी गायब", "bn": "⚠️ G5: জন্ম ২/১১ অধিপতি অনুপস্থিত"},
    "marriage_g5_lock_quantum": {"en": "🔒 QUANTUM LOCK: Transit 7th CSL ({csl}) in SUB of {sub} (2/7/11 Lord).", "hi": "🔒 क्वांटम लॉक: {sub} के उप में गोचर 7वां CSL ({csl})।", "bn": "🔒 কোয়ান্টাম লক: {sub}-এর উপ-এ গোচর ৭ম CSL ({csl})।"},
    "marriage_g5_lock_identity": {"en": "🔒 IDENTITY LOCK: Transit 7th CSL ({csl}) IS a 2/7/11 Lord.", "hi": "🔒 पहचान लॉक: गोचर 7वां CSL ({csl}) एक 2/7/11 स्वामी है।", "bn": "🔒 পরিচয় লক: গোচর ৭ম CSL ({csl}) হল ২/৭/১১ অধিপতি।"},
    "marriage_g5_lock_star": {"en": "🔓 STAR LOCK: Transit 7th CSL ({csl}) in STAR of {star} (2/7/11 Lord).", "hi": "🔓 स्टार लॉक: {star} के नक्षत्र में गोचर 7वां CSL ({csl})।", "bn": "🔓 স্টার লক: {star}-এর নক্ষত্রে গোচর ৭ম CSL ({csl})।"},
    "marriage_g5_fail": {"en": "❌ G5: Transit CSL ({csl}) in Star={star}/Sub={sub} - No Link.", "hi": "❌ G5: स्टार={star}/उप={sub} में गोचर CSL ({csl}) - कोई लिंक नहीं।", "bn": "❌ G5: স্টার={star}/সাব={sub}-এ গোচর CSL ({csl}) - কোন লিঙ্ক নেই।"},
    "marriage_g5_confirmed": {"en": "🔴 EVENT CONFIRMED", "hi": "🔴 घटना पुष्टि", "bn": "🔴 ঘটনা নিশ্চিত"},
    "marriage_g5_no_trigger": {"en": "⚪ NO TRIGGER", "hi": "⚪ कोई ट्रिगर नहीं", "bn": "⚪ কোন ট্রিগার নেই"},
    "marriage_sandhi": {"en": "⚡ SANDHI JUNCTION: Dasha boundary energy", "hi": "⚡ संधि जंक्शन: दशा सीमा ऊर्जा", "bn": "⚡ সন্ধি জংশন: দশা সীমানা শক্তি"},

    "marriage_sandhi": {"en": "⚡ SANDHI JUNCTION: Dasha boundary energy", "hi": "⚡ संधि जंक्शन: दशा सीमा ऊर्जा", "bn": "⚡ সন্ধি জংশন: দশা সীমানা শক্তি"},

    # Life Span Categories & Outcomes
    "life_cat_alpayu": {"en": "ALPAYU (0-33 Years)", "hi": "अल्फायु (0-33 वर्ष)", "bn": "অল্পায়ু (০-৩৩ বছর)"},
    "life_cat_madhyayu": {"en": "MADHYAYU (33-66 Years)", "hi": "मध्यायु (33-66 वर्ष)", "bn": "মধ্যায়ু (৩৩-৬৬ বছর)"},
    "life_cat_purnayu": {"en": "PURNAYU (67+ Years)", "hi": "पूर्णायु (67+ वर्ष)", "bn": "পূর্ণায়ু (৬৭+ বছর)"},
    
    "death_out_confirmed": {"en": "CONFIRMED EXIT EVENT (Irreversible)", "hi": "पुष्टि निकास घटना (अपरिवर्तनीय)", "bn": "নিশ্চিত প্রস্থান ঘটনা (অপরিবর্তনীয়)"},
    "death_out_critical": {"en": "CRITICAL CONDITION (Survival Possible)", "hi": "गंभीर स्थिति (जीवन रक्षा संभव)", "bn": "গুরুতর অবস্থা (বেঁচে থাকা সম্ভব)"},
    "death_out_false": {"en": "FALSE ALARM (Structural Damage Only)", "hi": "झूठा अलार्म (केवल संरचनात्मक क्षति)", "bn": "মিথ্যা সতর্কবার্তা (শুধুমাত্র গঠনগত ক্ষতি)"},
    "death_out_deferred": {"en": "EVENT DEFERRED (Wrong Timing)", "hi": "घटना स्थगित (गलत समय)", "bn": "ঘটনা স্থগিত (ভুল সময়)"},
    "death_out_chronic": {"en": "CHRONIC ISSUES ONLY (No Immediate Threat)", "hi": "केवल दीर्घकालिक मुद्दे (कोई तत्काल खतरा नहीं)", "bn": "শুধুমাত্র দীর্ঘস্থায়ী সমস্যা (তাৎক্ষণিক হুমকি নেই)"},

    # Life Span Gate Details
    "life_g1_lsl_8_12": {"en": "LSL {lsl} Result: {res} → Contains 8/12", "hi": "LSL {lsl} परिणाम: {res} → 8/12 शामिल", "bn": "LSL {lsl} ফলাফল: {res} → ৮/১২ অন্তর্ভুক্ত"},
    "life_g1_dual_lord": {"en": "☠️ DUAL-LORD: {lord} = 1st Lord + 12th Lord (SELF-EXIT agent)", "hi": "☠️ दोहरी-स्वामी: {lord} = 1ला स्वामी + 12वां स्वामी (आत्म-निकास एजेंट)", "bn": "☠️ দ্বৈত-অধিপতি: {lord} = ১ম অধিপতি + ১২শ অধিপতি (আত্ম-প্রস্থানকারী)"},
    "life_g1_dual_maraka": {"en": "☠️ DUAL-LORD: {lord} = 1st Lord + Maraka (SELF-DESTRUCTION)", "hi": "☠️ दोहरी-स्वामी: {lord} = 1ला स्वामी + मारक (आत्म-विनाश)", "bn": "☠️ দ্বৈত-অধিপতি: {lord} = ১ম অধিপতি + মারক (আত্ম-ধ্বংস)"},
    "life_g1_dual_8th": {"en": "☠️ DUAL-LORD: {lord} = 1st Lord + 8th Lord (SELF-DEATH)", "hi": "☠️ दोहरी-स्वामी: {lord} = 1ला स्वामी + 8वां स्वामी (आत्म-मृत्यु)", "bn": "☠️ দ্বৈত-অধিপতি: {lord} = ১ম অধিপতি + ৮ম অধিপতি (আত্ম-মৃত্যু)"},
    "life_g1_lagna_death": {"en": "Lagna Lord has {n} death significations", "hi": "लग्न स्वामी के पास {n} मृत्यु संकेत हैं", "bn": "লগ্ন অধিপতির {n} টি মৃত্যু নির্দেশক আছে"},
    "life_g1_badhaka_strong": {"en": "Badhaka {lord} (death:{d}) > Lagna (life:{l})", "hi": "बाधक {lord} (मृत्यु:{d}) > लग्न (जीवन:{l})", "bn": "বাধক {lord} (মৃত্যু:{d}) > লগ্ন (জীবন:{l})"},
    "life_g1_11_alpayu": {"en": "11th Lord {lord} in House {h} → ALPAYU", "hi": "11वां स्वामी {lord} घर {h} में → अल्फायु", "bn": "১১শ অধিপতি {lord} ভাব {h}-এ → অল্পায়ু"},
    "life_g1_saturn_yoga": {"en": "💎 SATURN AYU YOGA: Saturn LSL connected to 8 (No 12/Maraka) → PURNAYU", "hi": "💎 शनि आयु योग: शनि LSL 8 से जुड़ा (कोई 12/मारक नहीं) → पूर्णायु", "bn": "💎 শনি আয়ু যোগ: শনি LSL ৮-এর সাথে যুক্ত (১২/मारक নেই) → পূর্ণায়ু"},

    "life_g2_mars_aspect": {"en": "Mars {asp} on {target}", "hi": "मंगल {asp} {target} पर", "bn": "মঙ্গল {asp} {target}-এর উপর"},
    "life_g2_saturn_grip": {"en": "Saturn {asp} on {target}", "hi": "शनि {asp} {target} पर", "bn": "শনি {asp} {target}-এর উপর"},
    "life_g2_badhaka_match": {"en": "Badhaka {lord} conjunct LSL in H{h}", "hi": "बाधक {lord} H{h} में LSL के साथ", "bn": "বাধক {lord} H{h}-এ LSL-এর সাথে যুক্ত"},
    "life_g2_self_reinforce": {"en": "MD-AD Self-Reinforcement ({md}-{ad})", "hi": "MD-AD आत्म-सुदृढ़ीकरण ({md}-{ad})", "bn": "MD-AD আত্ম-শক্তিবৃদ্ধি ({md}-{ad})"},
    "life_g2_conflict": {"en": "MD-AD in 6/8 conflict", "hi": "MD-AD 6/8 संघर्ष में", "bn": "MD-AD ৬/৮ সংঘাতে"},

    "life_g3_md_death": {"en": "MD {md} Result: {res} → 8/12", "hi": "MD {md} परिणाम: {res} → 8/12", "bn": "MD {md} ফলাফল: {res} → ৮/১২"},
    "life_g3_ad_maraka": {"en": "AD {ad} Result: {res} → Maraka/Badhaka", "hi": "AD {ad} परिणाम: {res} → मारक/बाधक", "bn": "AD {ad} ফলাফল: {res} → মারক/বাধক"},
    "life_g3_pd_exit": {"en": "PD {pd} Result: {res} → Body/Exit", "hi": "PD {pd} परिणाम: {res} → शरीर/निकास", "bn": "PD {pd} ফলাফল: {res} → শরীর/প্রস্থান"},
    "life_g3_triple_lock": {"en": "Triple Self-Lock ({md}) active on death houses", "hi": "तिहरा सेल्फ-लॉक ({md}) मृत्यु घरों पर सक्रिय", "bn": "ত্রিপল সেলফ-লক ({md}) মৃত্যু ভাবগুলিতে সক্রিয়"},
    "life_g3_chain": {"en": "Dasha chain: {n} death houses active", "hi": "दशा श्रृंखला: {n} मृत्यु घर सक्रिय", "bn": "দশা চেইন: {n} টি মৃত্যু ভাব সক্রিয়"},

    "life_g4_natal_11": {"en": "11th Lord {lord} in House {h}", "hi": "11वां स्वामी {lord} घर {h} में", "bn": "১১শ অধিপতি {lord} ভাব {h}-এ"},
    "life_g4_transit_11": {"en": "Transit 11th Lord in 8th House", "hi": "गोचर 11वां स्वामी 8वें घर में", "bn": "গোচর ১১শ অধিপতি ৮ম ভাবে"},
    "life_g4_retro_fail": {"en": "Recovery Lord {lord} is RETROGRADE", "hi": "रिकवरी स्वामी {lord} वक्री है", "bn": "রিকভারি অধিপতি {lord} বক্রী"},
    "life_g4_block": {"en": "{mal} {asp} on Transit 11th Lord", "hi": "गोचर 11वें स्वामी पर {mal} {asp}", "bn": "গোচর ১১শ অধিপতির উপর {mal} {asp}"},
    "life_g4_doctor": {"en": "11th Lord's Star = {star} (Maraka/Badhaka)", "hi": "11वें स्वामी का नक्षत्र = {star} (मारक/बाधक)", "bn": "১১শ অধিপতির নক্ষত্র = {star} (मारक/বাধক)"},
    "life_g4_fatal_retro": {"en": "☠️ FATAL: Rx {lord} in killer star", "hi": "☠️ घातक: वक्री {lord} हत्यारे नक्षत्र में", "bn": "☠️ মারাত্মক: ঘাতক নক্ষত্রে বক্রী {lord}"},
    "life_g4_sys_failed": {"en": "RECOVERY SYSTEM FAILED", "hi": "रिकवरी सिस्टम विफल", "bn": "রিকভারি সিস্টেম ব্যর্থ"},
    "life_g4_sys_intact": {"en": "RECOVERY SYSTEM INTACT", "hi": "रिकवरी सिस्टम सुरक्षित", "bn": "রিকভারি সিস্টেম অক্ষত"},

    "life_g5_md_auth": {"en": "MD Sub-Lord {sub} signifies 8/12", "hi": "MD उप-स्वामी {sub} 8/12 का संकेत देता है", "bn": "MD উপ-অধিপতি {sub} ৮/১২ নির্দেশ করে"},
    "life_g5_ad_auth": {"en": "AD Sub-Lord {sub} signifies Maraka/Badhaka", "hi": "AD उप-स्वामी {sub} मारक/बाधक का संकेत देता है", "bn": "AD উপ-অধিপতি {sub} মারক/বাধক নির্দেশ করে"},
    "life_g5_pd_link": {"en": "PD {pd} affects body/exit", "hi": "PD {pd} शरीर/निकास को प्रभावित करता है", "bn": "PD {pd} শরীর/প্রস্থান প্রভাবিত করে"},
    "life_g5_transit_md": {"en": "MD {md} in {sign} (death sign)", "hi": "MD {md} {sign} में (मृत्यु राशि)", "bn": "MD {md} {sign}-এ (মৃত্যু রাশি)"},

    "life_g6_sun_star": {"en": "Sun in Star of 8th Lord", "hi": "8वें स्वामी के नक्षत्र में सूर्य", "bn": "৮ম অধিপতির নক্ষত্রে রবি"},
    "life_g6_sun_house": {"en": "Sun in House {h}", "hi": "सूर्य घर {h} में", "bn": "রবি ভাব {h}-এ"},
    "life_g6_sun_seal": {"en": "Sun in {h}th Sign from Lagna (Transit Seal)", "hi": "लग्न से {h}वीं राशि में सूर्य (गोचर सील)", "bn": "লগ্ন থেকে {h}তম রাশিতে রবি (গোচর সিল)"},
    "life_g6_csl_collision": {"en": "1st CSL + 8th CSL in H{h}", "hi": "1ला CSL + 8वां CSL H{h} में", "bn": "১ম CSL + ৮ম CSL H{h}-এ"},
    "life_g6_moon_star": {"en": "Moon in Star of {star}", "hi": "{star} के नक्षत्र में चंद्रमा", "bn": "{star}-এর নক্ষত্রে চন্দ্র"},
    "life_g6_moon_house": {"en": "Moon in House {h}", "hi": "चंद्रमा घर {h} में", "bn": "চন্দ্র ভাব {h}-এ"},
    "life_g6_vain_trigger": {"en": "☠️ {msg}", "hi": "☠️ {msg}", "bn": "☠️ {msg}"},
    "life_g6_lagna_active": {"en": "Lagna Lord in death star", "hi": "मृत्यु नक्षत्र में लग्न स्वामी", "bn": "মৃত্যু নক্ষত্রে লগ্ন অধিপতি"},

    # Job Loss Reasons
    "job_loss_reason_personal": {"en": "Personal crisis / health emergency", "hi": "व्यक्तिगत संकट / स्वास्थ्य आपातकाल", "bn": "ব্যক্তিগত সংকট / স্বাস্থ্য জরুরি অবস্থা"},
    
    # Loan Timing Keys
    "loan_g1_dual_debt": {"en": "6th + 8th + 12th ACTIVE >>> Double debt pressure with drain", "hi": "6+8+12 सक्रिय >>> जल निकासी के साथ दोहरा ऋण दबाव", "bn": "৬+৮+১২ সক্রিয় >>> নিকাশী সহ দ্বিগুণ ঋণ চাপ"},
    "loan_g1_mixed_debt": {"en": "6th + 8th ACTIVE >>> Service + Crisis, monitor cash flow", "hi": "6+8 सक्रिय >>> सेवा + संकट, नकदी प्रवाह की निगरानी करें", "bn": "৬+৮ সক্রিয় >>> পরিষেবা + সংকট, নগদ প্রবাহ পর্যবেক্ষণ করুন"},
    "loan_g1_emi_drain": {"en": "6th + 12th ACTIVE (2nd weak) >>> EMI/Loan with drain", "hi": "6+12 सक्रिय (2रा कमजोर) >>> निकासी के साथ ईएमआई/ऋण", "bn": "৬+১২ সক্রিয় (২য় দুর্বল) >>> নিকাশী সহ ইএমআই/ঋণ"},
    "loan_g1_job_prosper": {"en": "6th + 10th + 11th ACTIVE >>> Job/Service prosperity, not debt", "hi": "6+10+11 सक्रिय >>> नौकरी/सेवा समृद्धि, ऋण नहीं", "bn": "৬+১০+১১ সক্রিয় >>> চাকরি/পরিষেবা সমৃদ্ধি, ঋণ নয়"},
    "loan_g1_career_focus": {"en": "6th + 10th ACTIVE >>> Career/service focus, not debt", "hi": "6+10 सक्रिय >>> करियर/सेवा फोकस, ऋण नहीं", "bn": "৬+১০ সক্রিয় >>> ক্যারিয়ার/পরিষেবা ফোকাস, ঋণ নয়"},
    "loan_g1_mixed_6": {"en": "6th ACTIVE >>> Possible debt OR service commitment", "hi": "6ठा सक्रिय >>> संभावित ऋण या सेवा प्रतिबद्धता", "bn": "৬ষ্ঠ সক্রিয় >>> সম্ভাব্য ঋণ বা পরিষেবা প্রতিশ্রুতি"},
    "loan_g1_crisis_borrow": {"en": "8th + 12th ACTIVE >>> Crisis borrowing with drain", "hi": "8+12 सक्रिय >>> निकासी के साथ संकट उधार", "bn": "৮+১২ সক্রিয় >>> নিকাশী সহ সংকট ঋণ"},
    "loan_g1_sudden_gain": {"en": "8th + 11th ACTIVE >>> Could be sudden gain, not debt", "hi": "8+11 सक्रिय >>> अचानक लाभ हो सकता है, ऋण नहीं", "bn": "৮+১১ সক্রিয় >>> হঠাৎ লাভ হতে পারে, ঋণ নয়"},
    "loan_g1_emergency": {"en": "8th ACTIVE >>> Emergency situation possible", "hi": "8वां सक्रिय >>> आपातकालीन स्थिति संभव", "bn": "৮ম সক্রিয় >>> জরুরি পরিস্থিতি সম্ভব"},
    "loan_g1_no_debt": {"en": "NO DEBT ACTIVATION: Neither 6th nor 8th active", "hi": "कोई ऋण सक्रियता नहीं: न 6ठा और न ही 8वां सक्रिय", "bn": "কোন ঋণ সক্রিয়তা নেই: ৬ষ্ঠ বা ৮ম সক্রিয় নয়"},

    "loan_g2_survival": {"en": "1st ACTIVE + 2nd ABSENT >>> Survival pressure destroys liquidity", "hi": "1ला सक्रिय + 2रा अनुपस्थित >>> अस्तित्व का दबाव तरलता को नष्ट कर देता है", "bn": "১ম সক্রিয় + ২য় অনুপস্থিত >>> অস্তিত্বের চাপ তরলতা ধ্বংস করে"},
    "loan_g2_ego_block": {"en": "1st STRONG >>> 2nd under pressure (ego blocks savings)", "hi": "1ला मजबूत >>> 2रा दबाव में (अहंकार बचत को रोकता है)", "bn": "১ম শক্তিশালী >>> ২য় চাপে (অহং সঞ্চয়কে বাধা দেয়)"},
    "loan_g2_no_liquidity": {"en": "2nd ABSENT + 11th ABSENT >>> No liquidity, no income support", "hi": "2रा + 11वां अनुपस्थित >>> कोई तरलता नहीं, कोई आय समर्थन नहीं", "bn": "২য় + ১১শ অনুপস্থিত >>> কোন তরলতা নেই, কোন আয় সমর্থন নেই"},
    "loan_g2_no_buffer": {"en": "2nd ABSENT >>> No cash buffer available", "hi": "2रा अनुपस्थित >>> कोई नकद बफर उपलब्ध नहीं", "bn": "২য় অনুপস্থিত >>> কোন নগদ বাফার উপলব্ধ নেই"},
    "loan_g2_weak_income": {"en": "2nd ACTIVE but 11th ABSENT >>> Cash exists but income weak", "hi": "2रा सक्रिय लेकिन 11वां अनुपस्थित >>> नकदी मौजूद है लेकिन आय कमजोर है", "bn": "২য় সক্রিয় কিন্তু ১১শ অনুপস্থিত >>> নগদ আছে কিন্তু আয় দুর্বল"},
    "loan_g2_healthy": {"en": "2nd HEALTHY >>> No liquidity collapse", "hi": "2रा स्वस्थ >>> कोई तरलता पतन नहीं", "bn": "২য় সুস্থ >>> কোন তরলতা পতন নেই"},

    "loan_g3_borrow": {"en": "1st + 12th ACTIVE >>> Self-driven action with expenses (may borrow)", "hi": "1+12 सक्रिय >>> खर्चों के साथ स्व-चालित कार्रवाई (उधार ले सकते हैं)", "bn": "১+১২ সক্রিয় >>> খরচের সাথে স্ব-চালিত পদক্ষেপ (ঋণ নিতে পারে)"},
    "loan_g3_self_reliant": {"en": "1st + 6th ACTIVE (no 10th) >>> Self-reliance through borrowing", "hi": "1+6 सक्रिय (कोई 10वां नहीं) >>> उधार के माध्यम से आत्मनिर्भरता", "bn": "১+৬ সক্রিয় (১০ম নেই) >>> ঋণের মাধ্যমে স্বনির্ভরতা"},
    "loan_g3_earning": {"en": "1st + 10th + 11th ACTIVE >>> Self-driven earning, not borrowing", "hi": "1+10+11 सक्रिय >>> स्व-चालित कमाई, उधार नहीं", "bn": "১+১০+১১ সক্রিয় >>> স্ব-চালিত উপার্জন, ঋণ নয়"},
    "loan_g3_effort": {"en": "1st + 10th ACTIVE >>> Career initiative, natural effort", "hi": "1+10 सक्रिय >>> करियर पहल, स्वाभाविक प्रयास", "bn": "১+১০ সক্রিয় >>> ক্যারিয়ার উদ্যোগ, স্বাভাবিক প্রচেষ্টা"},
    "loan_g3_will": {"en": "1st ACTIVE >>> Strong self-will (could be positive or pressure)", "hi": "1ला सक्रिय >>> मजबूत आत्म-इच्छा (सकारात्मक या दबाव हो सकता है)", "bn": "১ম সক্রিয় >>> শক্তিশালী ইচ্ছা (ইতিবাচক বা চাপ হতে পারে)"},
    "loan_g3_passive": {"en": "1st INACTIVE >>> Will adapt lifestyle, not take initiative to borrow", "hi": "1ला निष्क्रिय >>> जीवनशैली अपनाएगा, उधार लेने की पहल नहीं करेगा", "bn": "১ম নিষ্ক্রিয় >>> জীবনধারা মানিয়ে নেবে, ঋণ নেওয়ার উদ্যোগ নেবে না"},

    "loan_g4_safe": {"en": "12th INACTIVE >>> Loan is short-term and manageable", "hi": "12वां निष्क्रिय >>> ऋण अल्पकालिक और प्रबंधनीय है", "bn": "১২শ নিষ্ক্রিয় >>> ঋণ স্বল্পমেয়াদী এবং পরিচালনাযোগ্য"},
    "loan_g4_invest": {"en": "12th + 9th ACTIVE >>> Foreign investment/trade (asset building)", "hi": "12+9 सक्रिय >>> विदेशी निवेश/व्यापार (संपत्ति निर्माण)", "bn": "১২+৯ সক্রিয় >>> বিদেশী বিনিয়োগ/বাণিজ্য (সম্পদ গঠন)"},
    "loan_g4_speculate": {"en": "12th + 5th ACTIVE >>> Speculative investment (calculated risk)", "hi": "12+5 सक्रिय >>> सट्टा निवेश (परिकलित जोखिम)", "bn": "১২+৫ সক্রিয় >>> ফাটকা বিনিয়োগ (গণনা করা ঝুঁকি)"},
    "loan_g4_trap": {"en": "12th + 6th + 8th ALL ACTIVE >>> Severe debt trap", "hi": "12+6+8 सक्रिय >>> गंभीर ऋण जाल", "bn": "১২+৬+৮ সক্রিয় >>> গুরুতর ঋণ ফাঁদ"},
    "loan_g4_manageable": {"en": "12th + 6th + 11th >>> EMI but income supports it", "hi": "12+6+11 >>> ईएमआई लेकिन आय इसका समर्थन करती है", "bn": "১২+৬+১১ >>> ইএমআই কিন্তু আয় এটি সমর্থন করে"},
    "loan_g4_emi_trap": {"en": "12th + 6th ACTIVE (no 11th) >>> EMI cycle with interest drain", "hi": "12+6 सक्रिय (कोई 11वां नहीं) >>> ब्याज निकासी के साथ ईएमआई चक्र", "bn": "১২+৬ সক্রিয় (১১শ নেই) >>> সুদের নিকাশী সহ ইএমআই চক্র"},
    "loan_g4_compound": {"en": "12th + 8th ACTIVE >>> Emergency expense with compounding cost", "hi": "12+8 सक्रिय >>> कंपाउंडिंग लागत के साथ आपातकालीन व्यय", "bn": "১২+৮ সক্রিয় >>> চক্রবৃদ্ধি খরচ সহ জরুরি ব্যয়"},
    "loan_g4_ongoing": {"en": "12th ACTIVE >>> Expenses ongoing (check context)", "hi": "12वां सक्रिय >>> खर्च जारी (संदर्भ की जाँच करें)", "bn": "১২শ সক্রিয় >>> খরচ চলছে (প্রসঙ্গ পরীক্ষা করুন)"},
    
    # Loan Classification
    "loan_type_spiral": {"en": "🚨 DEBT SPIRAL (6-12 loop, 2nd never recovers, 11th blocked)", "hi": "🚨 ऋण सर्पिल (6-12 लूप, 2रा कभी ठीक नहीं होता)", "bn": "🚨 ঋণ সর্পিল (৬-১২ লুপ, ২য় কখনও পুনরুদ্ধার হয় না)"},
    "loan_type_emergency": {"en": "🚨 EMERGENCY DEBT (Crisis borrowing, survival pressure high)", "hi": "🚨 आपातकालीन ऋण (संकट उधार, उच्च अस्तित्व दबाव)", "bn": "🚨 জরুরি ঋণ (সংকট ঋণ, উচ্চ অস্তিত্বের চাপ)"},
    "loan_type_bank": {"en": "🏦 BANK/EMI LOAN (Structured debt with interest drain)", "hi": "🏦 बैंक/ईएमआई ऋण (ब्याज निकासी के साथ संरचित ऋण)", "bn": "🏦 ব্যাংক/ইএমআই ঋণ (সুদের নিকাশী সহ কাঠামোগত ঋণ)"},
    "loan_type_short": {"en": "💳 SHORT-TERM LOAN (Manageable, no 12th drain)", "hi": "💳 अल्पकालिक ऋण (प्रबंधनीय, कोई 12वां नाली नहीं)", "bn": "💳 স্বল্পমেয়াদী ঋণ (পরিচালনাযোগ্য, ১২শ নিকাশী নেই)"},
    "loan_type_bridge": {"en": "🚑 EMERGENCY BRIDGE (Crisis but manageable)", "hi": "🚑 आपातकालीन ब्रिज (संकट लेकिन प्रबंधनीय)", "bn": "🚑 জরুরি ব্রিজ (সংকট কিন্তু পরিচালনাযোগ্য)"},
    "loan_type_dual": {"en": "⚠️ DUAL DEBT PRESSURE (Both EMI + Crisis active)", "hi": "⚠️ दोहरा ऋण दबाव (ईएमआई + संकट दोनों सक्रिय)", "bn": "⚠️ দ্বৈত ঋণ চাপ (উভয় ইএমআই + সংকট সক্রিয়)"},
    "loan_type_general": {"en": "💸 GENERAL DEBT PHASE", "hi": "💸 सामान्य ऋण चरण", "bn": "💸 সাধারণ ঋণ পর্যায়"},

    # Loan Repayment Keys
    "repay_g1_weak": {"en": "2nd NOT signified - No repayment capacity", "hi": "2रा संकेतित नहीं - कोई पुनर्भुगतान क्षमता नहीं", "bn": "২য় নির্দেশিত নয় - কোন ঋণ পরিশোধের ক্ষমতা নেই"},
    "repay_g1_destroyed": {"en": "2nd destroyed by 1st/12th - No repayment", "hi": "1ला/12वें द्वारा 2रा नष्ट - कोई पुनर्भुगतान नहीं", "bn": "১ম/১২শ দ্বারা ২য় ধ্বংস - কোন ঋণ পরিশোধ নেই"},
    "repay_g1_strong": {"en": "2nd linked to 11th - Regular repayment possible", "hi": "2रा 11वें से जुड़ा - नियमित पुनर्भुगतान संभव", "bn": "২য় ১১শের সাথে যুক্ত - নিয়মিত ঋণ পরিশোধ সম্ভব"},
    "repay_g1_mod": {"en": "2nd active but isolated - Sporadic payment", "hi": "2रा सक्रिय लेकिन अलग - छिटपुट भुगतान", "bn": "২য় সক্রিয় কিন্তু বিচ্ছিন্ন - বিক্ষিপ্ত পেমেন্ট"},

    "repay_g2_weak": {"en": "12th inactive - Leak stopped", "hi": "12वां निष्क्रिय - रिसाव रुक गया", "bn": "১২শ নিষ্ক্রিয় - ফুটো বন্ধ"},
    "repay_g2_trap": {"en": "12th destroying 2nd - Interest trap", "hi": "12वां 2रे को नष्ट कर रहा है - ब्याज जाल", "bn": "১২শ ২য়কে ধ্বংস করছে - সুদের ফাঁদ"},
    "repay_g2_settle": {"en": "12th redirected - Settlement possible", "hi": "12वां पुनर्निर्देशित - समझौता संभव", "bn": "১২শ পুনঃনির্দেশিত - নিষ্পত্তি সম্ভব"},
    "repay_g2_active": {"en": "12th active - Still draining", "hi": "12वां सक्रिय - अभी भी बह रहा है", "bn": "১২শ সক্রিয় - এখনও নিকাশী হচ্ছে"},

    "repay_g3_inactive": {"en": "6th not active - No EMI action", "hi": "6ठा सक्रिय नहीं - कोई ईएमआई कार्रवाई नहीं", "bn": "৬ষ্ঠ সক্রিয় নয় - কোন ইএমআই অ্যাকশন নেই"},
    "repay_g3_loop": {"en": "6th linked to 12th - Still in EMI loop", "hi": "6ठा 12वें से जुड़ा - अभी भी ईएमआई लूप में", "bn": "৬ষ্ঠ ১২শের সাথে যুক্ত - এখনও ইএমআই লুপে"},
    "repay_g3_pay": {"en": "6th linked to 2nd - Repayment discipline active", "hi": "6ठा 2रे से जुड़ा - पुनर्भुगतान अनुशासन सक्रिय", "bn": "৬ষ্ঠ ২য়র সাথে যুক্ত - ঋণ পরিশোধ শৃঙ্খলা সক্রিয়"},
    "repay_g3_neut": {"en": "6th active, neutral - Restructuring possible", "hi": "6ठा सक्रिय, तटस्थ - पुनर्गठन संभव", "bn": "৬ষ্ঠ সক্রিয়, নিরপেক্ষ - পুনর্গঠন সম্ভব"},

    "repay_g4_weak": {"en": "11th inactive - Forced delay or asset sale", "hi": "11वां निष्क्रिय - जबरन देरी या संपत्ति बिक्री", "bn": "১১শ নিষ্ক্রিয় - জোরপূর্বক বিলম্ব বা সম্পদ বিক্রি"},
    "repay_g4_drained": {"en": "11th destroyed by 10th - Money vanishes", "hi": "10वें द्वारा 11वां नष्ट - पैसा गायब", "bn": "১০ম দ্বারা ১১শ ধ্বংস - টাকা উধাও"},
    "repay_g4_strong": {"en": "11th supports 2nd - Smooth repayment", "hi": "11वां 2रे का समर्थन करता है - सहज पुनर्भुगतान", "bn": "১১শ ২য়কে সমর্থন করে - মসৃণ ঋণ পরিশোধ"},
    "repay_g4_mod": {"en": "11th active - Income exists", "hi": "11वां सक्रिय - आय मौजूद है", "bn": "১১শ সক্রিয় - আয় বিদ্যমান"},

    "repay_g5_fear": {"en": "1st with 8/12 - Survival fear blocking repayment", "hi": "1ला 8/12 के साथ - अस्तित्व का डर पुनर्भुगतान को रोक रहा है", "bn": "১ম ৮/১২ এর সাথে - অস্তিত্বের ভয় ঋণ পরিশোধ আটকাচ্ছে"},
    "repay_g5_hoard": {"en": "1st strong - Hoarding, delay tendency", "hi": "1ला मजबूत - जमाखोरी, देरी की प्रवृत्ति", "bn": "১ম শক্তিশালী - মজুতদারি, বিলম্ব প্রবণতা"},
    "repay_g5_relax": {"en": "1st relaxed - Confidence enables repayment", "hi": "1ला तनावमुक्त - आत्मविश्वास पुनर्भुगतान में सक्षम बनाता है", "bn": "১ম শিথিল - আত্মবিশ্বাস ঋণ পরিশোধে সক্ষম করে"},

    "repay_stb_clear": {"en": "🌟 COMPLETE CLEARANCE (Score: {score})", "hi": "🌟 पूर्ण निकासी (स्कोर: {score})", "bn": "🌟 সম্পূর্ণ ক্লিয়ারেন্স (স্কোর: {score})"},
    "repay_stb_emi": {"en": "✅ EMI CLOSURE (Score: {score})", "hi": "✅ ईएमआई बंद (स्कोर: {score})", "bn": "✅ ইএমআই বন্ধ (স্কোর: {score})"},
    "repay_stb_phase": {"en": "💰 REPAYMENT PHASE (Score: {score})", "hi": "💰 पुनर्भुगतान चरण (स्कोर: {score})", "bn": "💰 ঋণ পরিশোধ পর্যায় (স্কোর: {score})"},
    "repay_stb_part": {"en": "🟡 PARTIAL PAYMENT (Score: {score})", "hi": "🟡 आंशिक भुगतान (स्कोर: {score})", "bn": "🟡 আংশিক পেমেন্ট (স্কোর: {score})"},

    # Loan Extras (False Alarm, Exit, Scoring)
    "loan_false_1": {"en": "FALSE ALARM: 6th + 2nd + 11th healthy >>> Manageable EMI, not debt crisis", "hi": "झूठा अलार्म: 6+2+11 स्वस्थ >>> प्रबंधनीय ईएमआई, ऋण संकट नहीं", "bn": "মিথ্যা সতর্কবার্তা: ৬+২+১১ সুস্থ >>> পরিচালনাযোগ্য ইএমআই, ঋণ সংকট নয়"},
    "loan_false_2": {"en": "FALSE ALARM: 12th without 6th/8th >>> Expenses, not formal debt", "hi": "झूठा अलार्म: 6/8 के बिना 12 >>> खर्च, औपचारिक ऋण नहीं", "bn": "মিথ্যা সতর্কবার্তা: ৬/৮ ছাড়া ১২ >>> ব্যয়, আনুষ্ঠানিক ঋণ নয়"},
    "loan_false_3": {"en": "FALSE ALARM: 2nd weak + 1st weak >>> Lifestyle reduction, not loan", "hi": "झूठा अलार्म: 2रा कमजोर + 1ला कमजोर >>> जीवनशैली में कमी, कर्ज नहीं", "bn": "মিথ্যা সতর্কবার্তা: ২য় দুর্বল + ১ম দুর্বল >>> জীবনযাত্রার হ্রাস, ঋণ নয়"},

    "loan_exit_clean": {"en": "🟢 LOAN EXIT: 2nd + 11th + 6th active (repaying), no 12th drain", "hi": "🟢 ऋण निकास: 2+11+6 सक्रिय (पुनर्भुगतान), कोई 12वां नाली नहीं", "bn": "🟢 ঋণ প্রস্থান: ২+১১+৬ সক্রিয় (পরিশোধ), ১২শ নিকাশী নেই"},
    "loan_exit_clear": {"en": "🟢 DEBT CLEARING: Income + career supporting liquidity", "hi": "🟢 ऋण समाशोधन: आय + करियर तरलता का समर्थन", "bn": "🟢 ঋণ ক্লিয়ারিং: আয় + ক্যারিয়ার তারল্য সমর্থন"},
    "loan_exit_reduce": {"en": "🟢 DEBT REDUCING: Income supporting liquidity, no drain", "hi": "🟢 ऋण कम करना: आय तरलता का समर्थन करती है, कोई नाली नहीं", "bn": "🟢 ঋণ হ্রাস: আয় তরলতা সমর্থন করে, কোন নিকাশী নেই"},
    "loan_exit_repay": {"en": "🟢 REPAYMENT PHASE: Job/service income clearing dues", "hi": "🟢 पुनर्भुगतान चरण: नौकरी/सेवा आय बकाया समाशोधन", "bn": "🟢 ঋণ পরিশোধ পর্যায়: চাকরি/পরিষেবা আয় বকেয়া ক্লিয়ারিং"},

    "loan_score_rejected": {"en": "REJECTED: No debt house activation >>> Cannot have formal debt", "hi": "अस्वीकृत: कोई ऋण घर सक्रियण नहीं >>> औपचारिक ऋण नहीं हो सकता", "bn": "প্রত্যাখ্যাত: কোন ঋণ ঘর সক্রিয়করণ >>> আনুষ্ঠানিক ঋণ হতে পারে না"},
    "loan_score_mixed": {"en": "⚠️ MIXED: Could be service/job OR debt, context matters", "hi": "⚠️ मिश्रित: सेवा/नौकरी या ऋण हो सकता है, संदर्भ मायने रखता है", "bn": "⚠️ মিশ্র: পরিষেবা/চাকরি বা ঋণ হতে পারে, প্রসঙ্গ গুরুত্বপূর্ণ"},
    "loan_score_service": {"en": "⚠️ SERVICE: 6th indicates job/service, not debt", "hi": "⚠️ सेवा: 6ठा नौकरी/सेवा को दर्शाता है, ऋण को नहीं", "bn": "⚠️ পরিষেবা: ৬ষ্ঠ চাকরি/পরিষেবা নির্দেশ করে, ঋণ নয়"},
    "loan_score_gain": {"en": "⚠️ GAIN: 8th + 11th indicates sudden gain, not debt", "hi": "⚠️ लाभ: 8+11 अचानक लाभ को दर्शाता है, ऋण को नहीं", "bn": "⚠️ লাভ: ৮+১১ হঠাৎ লাভ নির্দেশ করে, ঋণ নয়"},

    "loan_warn_leverage": {"en": "[WARN] 2nd healthy >>> May be LEVERAGE loan (business/tax), not need-based", "hi": "[चेतावनी] 2रा स्वस्थ >>> लेवरेज ऋण (व्यवसाय/कर) हो सकता है, आवश्यकता-आधारित नहीं", "bn": "[সতর্কতা] ২য় সুস্থ >>> লিভারেজ লোন (ব্যবসা/ট্যাক্স) হতে পারে, প্রয়োজন-ভিত্তিক নয়"},
    "loan_warn_downscale": {"en": "[WARN] No survival pressure >>> May downscale instead of borrow", "hi": "[चेतावनी] कोई अस्तित्व का दबाव नहीं >>> उधार लेने के बजाय कम हो सकता है", "bn": "[সতর্কতা] কোন অস্তিত্বের চাপ নেই >>> ধারের পরিবর্তে হ্রাস পেতে পারে"},
    "loan_warn_earning": {"en": "💪 Self-driven earning, not borrowing", "hi": "💪 स्व-चालित कमाई, उधार नहीं", "bn": "💪 স্ব-চালিত উপার্জন, ঋণ নয়"},
    "loan_warn_effort": {"en": "💪 Career initiative, natural effort", "hi": "💪 करियर पहल, स्वाभाविक प्रयास", "bn": "💪 ক্যারিয়ার উদ্যোগ, স্বাভাবিক প্রচেষ্টা"},
    "job_loss_reason_scandal": {"en": "Scandal / fraud / misconduct investigation", "hi": "घोटाला / धोखाधड़ी / कदाचार जांच", "bn": "স্ক্যান্ডাল / জালিয়াতি / অসদাচরণ তদন্ত"},
    "job_loss_reason_shock": {"en": "Sudden unexpected termination", "hi": "अचानक बर्खास्तगी", "bn": "হঠাৎ অপ্রত্যাশিত ছাঁটাই"},
    "job_loss_reason_budget": {"en": "Budget cuts / financial restructuring", "hi": "बजट में कटौती / वित्तीय पुनर्गठन", "bn": "বাজেট কাটছাঁট / আর্থিক পুনর্গঠন"},
    "job_loss_reason_closure": {"en": "Office/branch closure / relocation", "hi": "कार्यालय/शाखा बंद / स्थानांतरण", "bn": "অফিস/শাখা বন্ধ / স্থানান্তরণ"},
    "job_loss_reason_restructuring": {"en": "Organizational restructuring / role abolishment", "hi": "संगठनात्मक पुनर्गठन / भूमिका समाप्ति", "bn": "সাংগঠনিক পুনর্গঠন / ভূমিকা বিলুপ্তি"},
    "job_loss_reason_contract_breach": {"en": "Contract violation / communication failure", "hi": "अनुबंध उल्लंघन / संचार विफलता", "bn": "চুক্তি লঙ্ঘন / যোগাযোগ ব্যর্থতা"},
    "job_loss_reason_contract_end": {"en": "Contract non-renewal / project completion", "hi": "अनुबंध नवीनीकरण नहीं / परियोजना पूर्ण", "bn": "চুক্তি নবায়ন না করা / প্রকল্প সমাপ্তি"},
    "job_loss_reason_performance": {"en": "Poor performance / skill mismatch", "hi": "खराब प्रदर्शन / कौशल बेमेल", "bn": "খারাপ পারফরম্যান্স / দক্ষতা অমিল"},
    "job_loss_reason_incompetence": {"en": "Competence issues / unable to meet requirements", "hi": "क्षमता मुद्दे / आवश्यकताओं को पूरा करने में असमर्थ", "bn": "দক্ষতা সমস্যা / প্রয়োজনীয়তা পূরণে অক্ষম"},
    "job_loss_reason_power": {"en": "Power struggle / political victimization", "hi": "सत्ता संघर्ष / राजनीतिक शिकार", "bn": "ক্ষমতার লড়াই / রাজনৈতিক শিকার"},
    "job_loss_reason_clash": {"en": "Conflict with superiors / ego clash", "hi": "वरिष्ठों के साथ संघर्ष / अहंकार टकराव", "bn": "ঊর্ধ্বতনদের সাথে দ্বন্দ্ব / অহং সংঘাত"},
    "job_loss_reason_client": {"en": "Major client loss / vendor breakdown", "hi": "प्रमुख ग्राहक हानि / विक्रेता संबंध टूटना", "bn": "প্রধান ক্লায়েন্ট ক্ষতি / বিক্রেতা বিভ্রাট"},
    "job_loss_reason_partner": {"en": "Partnership dissolution / conflict", "hi": "साझेदारी विघटन / संघर्ष", "bn": "অংশীদারিত্ব বিলুপ্তি / দ্বন্দ্ব"},
    "job_loss_reason_better": {"en": "Resigned for better opportunity", "hi": "बेहतर अवसर के लिए इस्तीफा", "bn": "ভাল সুযোগের জন্য পদত্যাগ"},
    "job_loss_reason_family": {"en": "Resigned due to family / relocation", "hi": "परिवार / स्थानांतरण के कारण इस्तीफा", "bn": "পরিবার / স্থানান্তরের কারণে পদত্যাগ"},
    "job_loss_reason_voluntary": {"en": "Self-initiated resignation", "hi": "स्वयं शुरू किया गया इस्तीफा", "bn": "স্ব-উদ্যোগী পদত্যাগ"},
    "job_loss_reason_health": {"en": "Health problems / medical leave", "hi": "स्वास्थ्य समस्याएं / चिकित्सा अवकाश", "bn": "স্বাস্থ্য সমস্যা / চিকিৎসা ছুটি"},
    "job_loss_reason_legal": {"en": "Legal complications / court cases", "hi": "कानूनी जटिलताएं / अदालती मामले", "bn": "আইনি জটিলতা / আদালতের মামলা"},
    "job_loss_reason_ethics": {"en": "Ethical breach / compliance violation", "hi": "नैतिक उल्लंघन / अनुपालन उल्लंघन", "bn": "নৈতিক লঙ্ঘন / কমপ্লায়েন্স লঙ্ঘন"},
    "job_loss_reason_financial": {"en": "Company financial distress", "hi": "कंपनी वित्तीय संकट", "bn": "কোম্পানির আর্থিক সংকট"},
    "job_loss_reason_creative": {"en": "Creative differences", "hi": "रचनात्मक मतभेद", "bn": "সৃজনশীল পার্থক্য"},
    "job_loss_reason_comm": {"en": "Communication breakdown", "hi": "संचार टूटना", "bn": "যোগাযোগ বিভ্রাট"},
    "job_loss_reason_general": {"en": "General job termination", "hi": "सामान्य नौकरी समाप्ति", "bn": "সাধারণ চাকরি সমাপ্তি"},
    "job_loss_reason_unknown": {"en": "Reason unclear from chart", "hi": "चार्ट से कारण स्पष्ट नहीं", "bn": "চার্ট থেকে কারণ অস্পষ্ট"},
    "vehicle_4th_csl": {"en": "4th Cusp Sub-Lord (Vehicle)", "hi": "4वां भाव उप-स्वामी (वाहन)", "bn": "৪র্থ ভাব উপ-স্বামী (যানবাহন)"},
    "vehicle_indicated": {"en": "Vehicle Purchase is indicated", "hi": "वाहन खरीद संकेतित है", "bn": "যানবাহন ক্রয় নির্দেশিত"},
    "vehicle_not_indicated": {"en": "Vehicle Purchase NOT indicated", "hi": "वाहन खरीद संकेतित नहीं", "bn": "যানবাহন ক্রয় নির্দেশিত নয়"},
    
    # ==========================================================================
    # LOAN MODULE
    # ==========================================================================
    "loan_title": {"en": "💳 LOAN TIMING AUDIT", "hi": "💳 ऋण समय लेखा परीक्षा", "bn": "💳 ঋণ টাইমিং অডিট"},
    "loan_repay_title": {"en": "💵 LOAN REPAYMENT TIMING AUDIT", "hi": "💵 ऋण चुकाने का समय लेखा परीक्षा", "bn": "💵 ঋণ পরিশোধ টাইমিং অডিট"},
    "loan_6th_csl": {"en": "6th Cusp Sub-Lord (Loan/Debt)", "hi": "6वां भाव उप-स्वामी (ऋण)", "bn": "৬ষ্ঠ ভাব উপ-স্বামী (ঋণ)"},
    "loan_indicated": {"en": "Loan is indicated", "hi": "ऋण संकेतित है", "bn": "ঋণ নির্দেশিত"},
    "loan_repay_possible": {"en": "Loan Repayment is possible", "hi": "ऋण चुकाना संभव है", "bn": "ঋণ পরিশোধ সম্ভব"},
    "loan_trap": {"en": "Debt Trap Warning", "hi": "कर्ज जाल चेतावनी", "bn": "ঋণ ফাঁদ সতর্কতা"},
    
    # ==========================================================================
    # REPORT HEADERS
    # ==========================================================================
    "report_summary": {"en": "SUMMARY", "hi": "सारांश", "bn": "সারসংক্ষেপ"},
    "report_windows_found": {"en": "Total Windows Found: {count}", "hi": "कुल खिड़कियां मिलीं: {count}", "bn": "মোট উইন্ডো পাওয়া গেছে: {count}"},
    "report_date_range": {"en": "Date Range: {start} to {end}", "hi": "तिथि सीमा: {start} से {end}", "bn": "তারিখ পরিসীমা: {start} থেকে {end}"},
    "report_age": {"en": "Age", "hi": "आयु", "bn": "বয়স"},
    "report_dasha_window": {"en": "Dasha Window", "hi": "दशा अवधि", "bn": "দশা উইন্ডো"},
    "report_score": {"en": "Score", "hi": "स्कोर", "bn": "স্কোর"},
    "report_forensic_status": {"en": "Forensic Status", "hi": "फोरेंसिक स्थिति", "bn": "ফরেনসিক অবস্থা"},
    "report_confidence": {"en": "Confidence: {value}%", "hi": "विश्वास: {value}%", "bn": "আত্মবিশ্বাস: {value}%"},

    # ==========================================================================
    # LANDING PAGE & NAVIGATION KEYS
    # ==========================================================================
    "nav_home": {"en": "Home", "hi": "होम", "bn": "হোম"},
    "nav_services": {"en": "Services", "hi": "सेवाएं", "bn": "সেবাসমূহ"},
    "nav_calculator": {"en": "Calculator", "hi": "कैलकुलेटर", "bn": "ক্যালকুলেটর"},
    "nav_about": {"en": "About", "hi": "परिचय", "bn": "পরিচিতি"},
    "nav_pricing": {"en": "Pricing", "hi": "मूल्य निर्धारण", "bn": "মূল্য তালিকা"},
    "nav_contact": {"en": "Contact", "hi": "संपर्क", "bn": "যোগাযোগ"},
    "nav_free_chart": {"en": "Free Chart", "hi": "निःशुल्क कुंडली", "bn": "ফ্রি চার্ট"},
    "nav_report": {"en": "Astrology Report", "hi": "ज्योतिष रिपोर्ट", "bn": "কোষ্ঠী বিবরণী"},

    "hero_tag": {"en": "Vedic Forensics & KP Astrological Science", "hi": "वैदिक फोरेंसिक्स और केपी ज्योतिषीय विज्ञान", "bn": "বৈদিক ফরেনসিক ও কেপি জ্যোতিষ বিজ্ঞান"},
    "hero_title_1": {"en": "Discover Your Destiny With", "hi": "अपने भाग्य को जानें", "bn": "আপনার ভাগ্য জানুন"},
    "hero_title_2": {"en": "Mathematical Precision", "hi": "गणितीय सटीकता के साथ", "bn": "গাণিতিক নির্ভুলতার সাথে"},
    "hero_subtitle": {
        "en": "Discover the true guidance of your past, present, and future through the precise mathematical analysis of the advanced Krishnamurti Paddhati (KP System) and Vedic zodiac.",
        "hi": "उन्नत कृष्णमूर्ति पद्धति (केपी सिस्टम) और वैदिक राशि चक्र के सटीक गणितीय विश्लेषण के माध्यम से अपने अतीत, वर्तमान और भविष्य के सच्चे मार्गदर्शन की खोज करें।",
        "bn": "উন্নত কৃষ্ণমূর্তি পদ্ধতি (KP System) ও বৈদিক রাশিচক্রের নিখুঁত গাণিতিক বিশ্লেষণের মাধ্যমে আপনার জীবনের অতীত, বর্তমান এবং ভবিষ্যতের সঠিক দিকনির্দেশনা জানুন।"
    },
    "hero_btn_calc": {"en": "Calculate Chart", "hi": "कुंडली गणना", "bn": "জন্মাঙ্গ গণনা (Calculate Chart)"},
    "hero_btn_consult": {"en": "Consultation", "hi": "परामर्श लें", "bn": "পরামর্শ নিন (Consultation)"},

    "services_title": {"en": "Our Services", "hi": "हमारी सेवाएं", "bn": "আমাদের সেবাসমূহ (Astrology Services)"},
    "services_subtitle": {
        "en": "Get answers to every important question of your life with the combination of mathematical accuracy and scientific astrology.",
        "hi": "गणितीय सटीकता और वैज्ञानिक ज्योतिष के संयोजन के साथ अपने जीवन के हर महत्वपूर्ण प्रश्न का उत्तर प्राप्त करें।",
        "bn": "গাণিতিক নির্ভুলতা এবং বৈজ্ঞানিক জ্যোতিষতত্ত্বের সমন্বয়ে আপনার জীবনের প্রতিটি গুরুত্বপূর্ণ প্রশ্নের উত্তর লাভ করুন।"
    },
    "service_1_title": {"en": "Marriage Forensics", "hi": "विवाह विश्लेषण", "bn": "বিবাহ ও যোটক বিচার (Marriage Forensics)"},
    "service_1_desc": {
        "en": "Detailed KP Sub-Lord based analysis and remedies regarding timing of marriage, marital happiness, and possibility of legal issues or separation.",
        "hi": "विवाह का सही समय, दांपत्य सुख और कानूनी समस्याओं या अलगाव की संभावना के बारे में विस्तृत केपी उप-स्वामी (Sub-Lord) आधारित विश्लेषण और उपाय।",
        "bn": " বিবাহের সঠিক সময় নির্ধারণ, দাম্পত্য সুখ-শান্তির প্রতিশ্রুতি এবং আইনি জটিলতা বা বিচ্ছেদের সম্ভাবনা নিয়ে বিস্তারিত কেপি সাব-লর্ড ভিত্তিক বিশ্লেষণ ও প্রতিকার।"
    },
    "service_2_title": {"en": "Career & Wealth", "hi": "करियर और धन", "bn": "জীবিকা ও অর্থযোগ (Career & Wealth)"},
    "service_2_desc": {
        "en": "Job or business? Timing of promotion, career obstacles, and precise wealth accumulation analysis based on birth chart.",
        "hi": "नौकरी या व्यवसाय? पदोन्नति का सही समय, करियर की बाधाएं, और जन्म कुंडली के आधार पर सटीक धन संचय विश्लेषण।",
        "bn": "চাকরি না ব্যবসা? পদোন্নতির সঠিক সময় নির্ধারণ, কর্মক্ষেত্রে বাধা এবং আর্থিক অগ্রগতির সঠিক কোষ্ঠী বিচার ও রাশিচক্রের বিশ্লেষণ।"
    },
    "service_3_title": {"en": "Wisdom & Skills", "hi": "शिक्षा और कौशल", "bn": "শিক্ষা ও মেধা বিচার (Wisdom & Skills)"},
    "service_3_desc": {
        "en": "Primary and higher education success, opportunities for foreign study, and guidance for your child's future oriented education.",
        "hi": "प्राथमिक और उच्च शिक्षा में सफलता, विदेश में अध्ययन की संभावना, और आपके बच्चे की भविष्योन्मुखी शिक्षा के लिए मार्गदर्शन।",
        "bn": "প্রাথমিক ও উচ্চ শিক্ষার যোগ, বিদেশের বিশ্ববিদ্যালয়ে পড়াশোনার সম্ভাবনা এবং সন্তানের ভবিষ্যৎ কর্মমুখী শিক্ষার দিকনির্দেশনা।"
    },
    "service_4_title": {"en": "Karmic Remedies", "hi": "कर्मफल और उपाय", "bn": "কর্মফল ও প্রতিকার (Karmic Remedies)"},
    "service_4_desc": {
        "en": "Special KP remedies including Lal Kitab, Vedic mantras, and strengthening weak planets to counter negative influences in your life.",
        "hi": "लाल किताब, वैदिक मंत्र और आपके जीवन में नकारात्मक प्रभावों को दूर करने के लिए कमजोर ग्रहों को मजबूत करने के विशेष केपी उपाय।",
        "bn": "লাল কিতাব, বৈদিক মন্ত্র, কুষ্টির দুর্বল গ্রহসমূহকে সবল করার বিশেষ কেপি প্রতিকার যা আপনার জীবনের নেতিবাচক প্রভাবকে প্রতিহত করবে।"
    },

    "calc_title": {"en": "Free Kundli Calculator", "hi": "निःशुल्क कुंडली कैलकुलेटर", "bn": "বিনামূল্যে কুষ্ঠি গণনা (Free Kundli Calculator)"},
    "calc_subtitle": {
        "en": "Enter your birth details and generate an instant, highly accurate KP Predictive Report.",
        "hi": "अपने जन्म का विवरण दर्ज करें और तुरंत एक अत्यंत सटीक केपी भविष्यवाणिया रिपोर्ट प्राप्त करें।",
        "bn": "আপনার জন্ম বিবরণী প্রদান করুন এবং অবিলম্বে একটি নিখুঁত জ্যোতিষীয় গণনাপত্র (KP Predictive Report) তৈরি করুন।"
    },
    "form_title": {"en": "Enter Birth Details", "hi": "जन्म विवरण भरें", "bn": "জন্মের বিবরণ পূরণ করুন (Enter Birth Details)"},
    "quick_city": {"en": "Quick City Autocomplete:", "hi": "त्वरित शहर चयन:", "bn": "দ্রুত স্থান নির্বাচন (Quick City Autocomplete):"},
    "name_label": {"en": "Full Name", "hi": "पूरा नाम", "bn": "আপনার নাম (Full Name)"},
    "name_placeholder": {"en": "e.g. Debasish Guha", "hi": "जैसे: देबाशीष गुहा", "bn": "উদা: Debasish Guha"},
    "dob_label": {"en": "Birth Date (DD-MM-YYYY)", "hi": "जन्म तिथि (दिन-माह-वर्ष)", "bn": "জন্ম তারিখ (Birth Date - DD-MM-YYYY)"},
    "tob_label": {"en": "Birth Time (HH:MM:SS)", "hi": "जन्म का समय (घंटा:मिनट:सेकंड)", "bn": "জন্ম সময় (Birth Time - HH:MM:SS)"},
    "lat_label_full": {"en": "Latitude (Decimal)", "hi": "अक्षांश (दशमलव)", "bn": "অক্ষাংশ (Latitude - Decimal)"},
    "lon_label_full": {"en": "Longitude (Decimal)", "hi": "देशांतर (दशमलव)", "bn": "দ্রাঘিমাংশ (Longitude - Decimal)"},
    "tz_label_full": {"en": "Timezone Offset", "hi": "समय क्षेत्र (Timezone Offset)", "bn": "টাইমজোন (Timezone Offset)"},
    "btn_calc_submit": {"en": "Generate KP Chart", "hi": "कुंडली बनाएं", "bn": "জন্মাঙ্গ কুষ্ঠি তৈরি করুন (Generate KP Chart)"},

    "about_intro": {"en": "Introduction", "hi": "परिचय", "bn": "পরিচিতি (Introduction)"},
    "about_title": {"en": "Astrologer Debasish Guha", "hi": "ज्योतिषी देबाशीष गुहा", "bn": "জ্যোতিষী দেবাশীষ গুহ (Astrologer Debasish Guha)"},
    "about_p1": {
        "en": "Welcome! I am Debasish Guha, and for many years I have been successfully working with the Krishnamurti Paddhati (KP System), the most modern and scientifically proven branch of mathematical astrology.",
        "hi": "स्वागत है! मैं देबाशीष गुहा हूँ, और कई वर्षों से मैं गणितीय ज्योतिष की सबसे आधुनिक और वैज्ञानिक रूप से प्रमाणित शाखा कृष्णमूर्ति पद्धति (केपी सिस्टम) के साथ सफलतापूर्वक काम कर रहा हूँ।",
        "bn": "স্বাগতম! আমি দেবাশীষ গুহ, বিগত বহু বছর ধরে গাণিতিক জ্যোতিষশাস্ত্রের সবচেয়ে আধুনিক ও প্রামাণ্য শাখা কৃষ্ণমূর্তি পদ্ধতি (KP System) নিয়ে সফলতার সাথে কাজ করছি।"
    },
    "about_p2": {
        "en": "My goal is to present astrology as an accurate mathematical science, moving away from common superstitions and vague assumptions. Based on the mutual relationships of planetary positions, Star Lords, and Sub-Lords, my specialty is determining the precise timings of major life events.",
        "hi": "मेरा लक्ष्य ज्योतिष को एक सटीक गणितीय विज्ञान के रूप में प्रस्तुत करना है, जो सामान्य अंधविश्वासों और अस्पष्ट अनुमानों से दूर हो। ग्रहों की स्थिति, नक्षत्र स्वामियों और उप-स्वामियों के पारस्परिक संबंधों के आधार पर, जीवन की प्रमुख घटनाओं के सटीक समय का निर्धारण करना ही मेरी विशेषता है।",
        "bn": "আমার লক্ষ্য সাধারণ কুসংস্কার ও ভাসাভাসা অনুমানের বাইরে গিয়ে জ্যোতিষশাস্ত্রকে একটি নির্ভুল গাণিতিক বিজ্ঞান হিসেবে মানুষের সামনে তুলে ধরা। গ্রহের অবস্থান, নক্ষত্রাধিপতি (Star Lord) এবং উপ-অধিপতির (Sub Lord) পারস্পরিক সম্পর্কের উপর ভিত্তি করে জীবনের গুরুত্বপূর্ণ বিষয়ের নিখুঁত সমকাল নির্ণয় করাই আমার বিশেষত্ব।"
    },
    "about_p3": {
        "en": "I provide services through both online and offline mediums. This website has been created to make it extremely easy for anyone to calculate their accurate cosmic birth chart from the comfort of their home for free.",
        "hi": "मैं ऑनलाइन और ऑफलाइन दोनों माध्यमों से सेवाएं प्रदान करता हूं। यह वेबसाइट इसलिए बनाई गई है ताकि कोई भी अपने घर बैठे ही अपनी सटीक कुंडली की निःशुल्क गणना कर सके।",
        "bn": "অনলাইন এবং অফলাইন উভয় মাধ্যমেই আমি সেবা প্রদান করে থাকি। আমার এই ওয়েবসাইটটি তৈরি করা হয়েছে যাতে অতি সহজে যেকোনো মানুষ নিজ ঘরে বসেই তাদের জন্মের সঠিক মহাজাগতিক চিত্রটি বিনামূল্যে গণনা করতে পারে।"
    },

    "pricing_title": {"en": "Pricing Plans", "hi": "शुल्क योजनाएं", "bn": "পরামর্শ ও সেবার মূল্য তালিকা (Pricing Plans)"},
    "pricing_subtitle": {"en": "Choose the right astrology service according to your needs.", "hi": "अपनी आवश्यकता के अनुसार सही ज्योतिष सेवा चुनें।", "bn": "আপনার প্রয়োজন অনুযায়ী সঠিক জ্যোতিষ সেবাটি বেছে নিন।"},
    "plan_1_title": {"en": "Free Chart", "hi": "निःशुल्क कुंडली", "bn": "ফ্রি চার্ট গণনা"},
    "plan_1_price": {"en": "₹0 / Free", "hi": "₹0 / निःशुल्क", "bn": "₹0 / Free"},
    "plan_1_f1": {"en": "Basic Kundli Charts (Rasi & Bhava)", "hi": "बुनियादी कुंडली चार्ट (राशि और भाव)", "bn": "সাধারণ কুষ্ঠি চার্ট (Rasi & Bhava)"},
    "plan_1_f2": {"en": "Planetary and house longitude details", "hi": "ग्रहों और भावों की सही डिग्री का विवरण", "bn": "গ্রহ ও ভাবের সঠিক ডিগ্রি বিবরণ"},
    "plan_1_f3": {"en": "KP planetary and house significators", "hi": "केपी ग्रह और भाव संकेतक", "bn": "কেপি গ্রহ ও ভাব নির্দেশক ছক"},
    "plan_1_f4": {"en": "Automated general predictions", "hi": "स्वचालित सामान्य भविष्यफल", "bn": "স্বয়ংক্রিয় এআই সাধারণ পূর্বাভাস"},
    "plan_1_btn": {"en": "Calculate", "hi": "गणना करें", "bn": "গণনা করুন"},
    
    "plan_2_title": {"en": "Premium PDF Report", "hi": "प्रीमियम पीडीएफ रिपोर्ट", "bn": "পূর্ণাঙ্গ প্রিমিয়াম রিপোর্ট"},
    "plan_2_price": {"en": "₹499 / $8", "hi": "₹499 / $8", "bn": "₹499 / $8"},
    "plan_2_badge": {"en": "MOST POPULAR", "hi": "सबसे लोकप्रिय", "bn": "সবচেয়ে জনপ্রিয়"},
    "plan_2_f1": {"en": "Precise event timing for next 5 years", "hi": "अगले 5 वर्षों के लिए सटीक घटना समय", "bn": "পরবর্তী ৫ বছরের নিখুঁত ইভেন্ট টাইমিং"},
    "plan_2_f2": {"en": "Marriage stability & separation scan", "hi": "विवाह स्थिरता और अलगाव विश्लेषण", "bn": "বিচ্ছেদের সময় ও বিবাহ স্থায়িত্ব স্ক্যান"},
    "plan_2_f3": {"en": "Lal Kitab & Vedic remedies guide", "hi": "लाल किताब और वैदिक उपाय गाइड", "bn": "লাল কিতাব ও বৈদিক প্রতিকার গাইড"},
    "plan_2_f4": {"en": "Digital Premium PDF format", "hi": "डिजिटल प्रीमियम पीडीएफ प्रारूप", "bn": "ডিজিটাল প্রিমিয়াম পিডিএফ ফর্ম্যাট"},
    "plan_2_btn": {"en": "Order Now", "hi": "ऑर्डर करें", "bn": "অর্ডার করুন"},

    "plan_3_title": {"en": "Personal Consultation", "hi": "व्यक्तिगत परामर्श", "bn": "ব্যক্তিগত আলোচনা"},
    "plan_3_price": {"en": "₹999 / $15", "hi": "₹999 / $15", "bn": "₹999 / $15"},
    "plan_3_f1": {"en": "Direct audio/video consultation", "hi": "सीधा ऑडियो/वीडियो परामर्श", "bn": "সরাসরি অডিও/ভিডিও কনসালটেশন"},
    "plan_3_f2": {"en": "Detailed answers to 3 specific questions", "hi": "3 विशिष्ट प्रश्नों के विस्तृत उत्तर", "bn": "৩টি নির্দিষ্ট প্রশ্নের পুঙ্খানুপুঙ্খ উত্তর"},
    "plan_3_f3": {"en": "KP Horary/Prashna Kundli analysis", "hi": "केपी प्रश्न कुंडली विश्लेषण", "bn": "কেপি হোরারি বা প্রশ্ন কুষ্ঠি বিশ্লেষণ"},
    "plan_3_f4": {"en": "Guidance on suitable gems & remedies", "hi": "उपयुक्त रत्न और उपायों पर मार्गदर्शन", "bn": "উপযুক্ত রত্ন ও প্রতিকার সংক্রান্ত পরামর্শ"},
    "plan_3_btn": {"en": "Book Now", "hi": "बुक करें", "bn": "বুক করুন"},

    "contact_title": {"en": "Contact & Booking", "hi": "संपर्क और बुकिंग", "bn": "যোগাযোগ ও পরামর্শ বুকিং (Contact & Booking)"},
    "contact_subtitle": {"en": "Fill the form below for any queries, premium report orders, or personal appointments.", "hi": "किसी भी प्रश्न, प्रीमियम रिपोर्ट ऑर्डर, या व्यक्तिगत नियुक्तियों के लिए नीचे दिए गए फॉर्म को भरें।", "bn": "যেকোনো জিজ্ঞাসা, প্রিমিয়াম রিপোর্ট অর্ডার বা ব্যক্তিগত অ্যাপয়েন্টমেন্টের জন্য নিচের ফর্মটি পূরণ করুন।"},
    "contact_success_msg": {"en": "Your message has been sent successfully! Astrologer Debasish Guha will contact you soon.", "hi": "आपका संदेश सफलतापूर्वक भेज दिया गया है! ज्योतिषी देबाशीष गुहा जल्द ही आपसे संपर्क करेंगे।", "bn": "আপনার বার্তাটি সফলভাবে পাঠানো হয়েছে! জ্যোতিষী দেবাশীষ গুহ খুব শীঘ্রই আপনার সাথে যোগাযোগ করবেন।"},
    "contact_name_label": {"en": "Your Name", "hi": "आपका नाम", "bn": "আপনার নাম (Your Name)"},
    "contact_whatsapp_label": {"en": "WhatsApp Number", "hi": "व्हाट्सएप नंबर", "bn": "হোয়াটসঅ্যাপ নাম্বার"},
    "contact_subject_label": {"en": "Subject", "hi": "विषय", "bn": "বিষয় (Subject)"},
    "contact_sub_opt1": {"en": "Premium Report Order (Premium Report - ₹499)", "hi": "प्रीमियम रिपोर्ट ऑर्डर (Premium Report - ₹499)", "bn": "প্রিমিয়াম রিপোর্ট অর্ডার (Premium Report - ₹499)"},
    "contact_sub_opt2": {"en": "1-on-1 Consultation Booking (1-on-1 Consultation - ₹999)", "hi": "सीधे परामर्श बुकिंग (1-on-1 Consultation - ₹999)", "bn": "সরাসরি পরামর্শ বুকিং (1-on-1 Consultation - ₹৯৯৯)"},
    "contact_sub_opt3": {"en": "Desktop Software License Inquiry", "hi": "डेस्कटॉप सॉफ्टवेयर लाइसेंस पूछताछ", "bn": "ডেস্কটপ সফটওয়্যার লাইসেন্স জিজ্ঞাসা"},
    "contact_sub_opt4": {"en": "General Query", "hi": "सामान्य पूछताछ", "bn": "সাধারণ জিজ্ঞাসা (General Query)"},
    "contact_msg_label": {"en": "Message / Birth Info", "hi": "संदेश / जन्म विवरण", "bn": "বার্তা / জন্ম তথ্য (Message / Birth Info)"},
    "contact_msg_placeholder": {"en": "Enter your birth details or query here...", "hi": "अपने जन्म का विवरण या प्रश्न यहाँ दर्ज करें...", "bn": "আপনার জন্ম বিবরণ বা প্রশ্নের বিবরণ এখানে লিখুন..."},
    "contact_btn_send": {"en": "Send Message", "hi": "संदेश भेजें", "bn": "বার্তা পাঠান (Send Message)"},
    "info_whatsapp_title": {"en": "WhatsApp Contact", "hi": "व्हाट्सएप संपर्क", "bn": "হোয়াটসঅ্যাপ যোগাযোগ"},
    "info_license_title": {"en": "Desktop License Query", "hi": "डेस्कटॉप लाइसेंस पूछताछ", "bn": "ডেস্কটপ লাইসেন্স কুয়েরি"},
    "info_license_desc": {"en": "Contact via WhatsApp for offline desktop app full license key.", "hi": "ऑफ़लाइन डेस्कटॉप ऐप की पूर्ण लाइसेंस कुंजी के लिए व्हाट्सएप के माध्यम से संपर्क करें।", "bn": "অফলাইন ডেস্কটপ অ্যাপের ফুল লাইসেন্স কি-এর জন্য হোয়াটসঅ্যাপ মারফত যোগাযোগ করুন।"},

    # ==========================================================================
    # REPORT PAGE TRANSLATIONS
    # ==========================================================================
    "report_back_btn": {"en": "← Calculate Another Chart", "hi": "← दूसरी कुंडली की गणना करें", "bn": "← অন্য জন্মাঙ্গ গণনা করুন"},
    "report_birth_summary": {"en": "Birth Information Summary", "hi": "जन्म विवरण सारांश", "bn": "জন্ম বিবরণী সারাংশ"},
    "report_visual_kundli": {"en": "Visual Birth Chart (Kundli)", "hi": "जन्म कुंडली चार्ट (Kundli)", "bn": "দৃশ্যমান জন্ম কুষ্ঠি (Kundli)"},
    "report_north_diamond": {"en": "North Indian (Diamond)", "hi": "उत्तर भारतीय (डायमंड)", "bn": "উত্তর ভারতীয় (ডায়মন্ড)"},
    "report_south_box": {"en": "South Indian (Box)", "hi": "दक्षिण भारतीय (बॉक्स)", "bn": "দক্ষিণ ভারতীয় (বক্স)"},
    "report_rasi_chart": {"en": "Rasi Chart (D1)", "hi": "राशि चार्ट (D1)", "bn": "রাশি চক্র (D1)"},
    "report_bhava_chart": {"en": "Bhava Chalit", "hi": "भाव चलित", "bn": "ভাব চলিত"},
    "report_planet_pos": {"en": "Planetary Positions & Star Lords", "hi": "ग्रह स्थिति और नक्षत्र स्वामी", "bn": "গ্রহ অবস্থান ও নক্ষত্র স্বামী"},
    "report_house_cusp": {"en": "House Cusps (Placidus Houses)", "hi": "भाव स्पष्ट (Placidus Houses)", "bn": "ভাব স্পষ্ট (Placidus Houses)"},
    "report_planet_sig": {"en": "KP Planetary Significators", "hi": "केपी ग्रह द्योतक (Planetary Significators)", "bn": "কেপি গ্রহ দ্যোতক (Planetary Significators)"},
    "report_source_row": {"en": "Source Row (Occupies & Owns)", "hi": "स्रोत पंक्ति (स्थित और स्वामित्व)", "bn": "উৎস শ্রেণী (অবস্থিত ও অধিপতি)"},
    "report_result_row": {"en": "Result Row (Star Lord & Sub Lord CSL connections)", "hi": "परिणाम पंक्ति (नक्षत्र और उप-स्वामी संबंध)", "bn": "ফলাফল শ্রেণী (নক্ষত্র ও উপ-অধিপতি সংযোগ)"},
    "report_narrative_title": {"en": "AI & KP Forensic Narrative Report", "hi": "एआई और केपी फोरेंसिक रिपोर्ट", "bn": "এআই ও কেপি ফরেনসিক বিবরণী"},
    "report_tab_purpose": {"en": "Dharma & Purpose", "hi": "धर्म और उद्देश्य", "bn": "ধর্ম ও উদ্দেশ্য"},
    "report_tab_family": {"en": "Family & Relations", "hi": "परिवार और संबंध", "bn": "পরিবার ও সম্পর্ক"},
    "report_tab_education": {"en": "Wisdom & Skills", "hi": "ज्ञान और कौशल", "bn": "জ্ঞান ও দক্ষতা"},
    "report_tab_career": {"en": "Career & Wealth", "hi": "करियर और धन", "bn": "পেশা ও সম্পদ"},
    "report_tab_marriage": {"en": "Marriage Stability", "hi": "विवाह स्थिरता", "bn": "বিবাহ স্থায়িত্ব"},
    "report_marriage_promise_title": {"en": "💍 Marriage Promise & Stability Verdict", "hi": "💍 विवाह योग और वैवाहिक स्थिरता निर्णय", "bn": "💍 দাম্পত্য যোগ ও বৈবাহিক স্থায়িত্ব রায়"},
    "report_sep_title": {"en": "⚠️ Detected Forensic Separation Windows", "hi": "⚠️ अलगाव समय अवधि (Forensic Windows)", "bn": "⚠️ সনাক্তকৃত বৈবাহিক বিচ্ছেদ সময়কাল"},
    "report_sep_desc": {
        "en": "The timing engine checks 6-8-12 dasha periods coupled with transits in the 7th and 8th house sign lords:",
        "hi": "टाइमिंग इंजन 7वें और 8वें भाव के स्वामियों के गोचर के साथ 6-8-12 दशा अवधियों की जाँच करता है:",
        "bn": "টাইমিং ইঞ্জিন ৭ম এবং ৮ম ভাবের অধিপতির গোচরের সাথে ৬-৮-১২ দশা সময়কাল পরীক্ষা করে:"
    },
    "report_sep_headers_window": {"en": "Date Range", "hi": "समय सीमा", "bn": "সময়সীমা"},
    "report_sep_headers_dasha": {"en": "Dasha Period", "hi": "दशा अवधि", "bn": "দশা সময়কাল"},
    "report_sep_headers_houses": {"en": "Negation Houses Involved", "hi": "বাধ্যবাধকতা ভাব", "bn": "যুক্ত নাকচ ভাবসমূহ"},
    "report_sep_headers_stability": {"en": "Status/Severity", "hi": "स्थिति/गंभीरता", "bn": "অবস্থা/গুরুত্ব"},
    "report_sep_safe": {"en": "No severe separation or divorce timeline windows detected between ages 18 and 60.", "hi": "18 से 60 वर्ष की आयु के बीच कोई गंभीर अलगाव या तलाक की समय अवधि नहीं मिली है।", "bn": "১৮ থেকে ৬০ বছর বয়সের মধ্যে কোনো গুরুতর বিচ্ছেদ বা বিবাহবিচ্ছেদের সময়কাল সনাক্ত করা যায়নি।"},
    "report_sep_safe_title": {"en": "✅ Separation Forensic Status", "hi": "✅ अलगाव फोरेंसिक स्थिति", "bn": "✅ বিচ্ছেদ ফরেনসিক স্থিতি"},
    
    "report_cta_title": {"en": "Need a Full Professional Consultation or PDF Report?", "hi": "क्या आपको पूर्ण व्यावसायिक परामर्श या पीडीएफ रिपोर्ट की आवश्यकता है?", "bn": "আপনার কি সম্পূর্ণ পেশাদার পরামর্শ বা পিডিএফ রিপোর্টের প্রয়োজন?"},
    "report_cta_sub": {"en": "Consultation & Licensing by Astrologer Debasish Guha", "hi": "ज्योतिषी देबाशीष गुहा द्वारा परामर्श और लाइसेंसिंग", "bn": "জ্যোতিষী দেবাশীষ গুহর দ্বারা পরামর্শ ও লাইসেন্সিং"},
    "report_cta_desc": {
        "en": "Unlock deep life-span calculation analysis, multi-dasa timeline scans, and comprehensive Lal Kitab remedies. Contact Debasish Guha directly to order a custom-printed manual PDF report or to purchase the offline desktop software license key.",
        "hi": "गहन जीवनकाल विश्लेषण, बहु-दशा समय स्कैन और व्यापक लाल किताब उपायों को अनलॉक करें। कस्टम-मुद्रित मैनुअल पीडीएफ रिपोर्ट ऑर्डर करने या ऑफ़लाइन डेस्कटॉप सॉफ़्टवेयर लाइसेंस कुंजी खरीदने के लिए सीधे देबाशीष गुहा से संपर्क करें।",
        "bn": "বিশদ জীবনকাল বিশ্লেষণ, বহু-দশা টাইমলাইন স্ক্যান এবং ব্যাপক লাল কিতাব প্রতিকার আনলক করুন। একটি কাস্টম প্রিমিয়াম পিডিএফ রিপোর্ট অর্ডার করতে বা অফলাইন ডেস্কটপ সফ্টওয়্যার লাইসেন্স কি কিনতে সরাসরি দেবাশীষ গুহর সাথে যোগাযোগ করুন।"
    },
    "report_cta_btn": {"en": "Contact for Full Consultation", "hi": "पूर्ण परामर्श के लिए संपर्क करें", "bn": "সম্পূর্ণ পরামর্শের জন্য যোগাযোগ করুন"},

    # ==========================================================================
    # DYNAMIC AI REPORT & VERDICT TRANSLATIONS
    # ==========================================================================
    "Past Life Karma": {"en": "Past Life Karma", "hi": "पिछले जन्म का कर्म", "bn": "পূর্বজন্মের কর্ম"},
    "Past Life Nature": {"en": "Past Life Nature", "hi": "पिछले जन्म का स्वभाव", "bn": "পূর্বজন্মের স্বভাব"},
    "Karmic Debt": {"en": "Karmic Debt", "hi": "कर्मों का कर्ज (ऋण)", "bn": "কর্ম ঋণ"},
    "Purpose of Rebirth": {"en": "Purpose of Rebirth", "hi": "पुनर्जन्म का उद्देश्य", "bn": "পুনর্বাসন/পুনর্জন্মের উদ্দেশ্য"},
    "Native Nature": {"en": "Native Nature", "hi": "मूल स्वभाव", "bn": "জাতকের স্বভাব"},
    "Fear & Subconscious": {"en": "Fear & Subconscious", "hi": "भय और अवचेतन मन", "bn": "ভয় ও অবচেতন মন"},
    "Spirituality": {"en": "Spirituality", "hi": "आध्यात्मिकता", "bn": "আধ্যাত্মিকতা"},
    "Father Nature": {"en": "Father Nature", "hi": "पिता का स्वभाव", "bn": "পিতার স্বভাব"},
    "Mother Nature": {"en": "Mother Nature", "hi": "माता का स्वभाव", "bn": "মাতার স্বভাব"},
    "Sibling Nature": {"en": "Sibling/Brother-Sister Nature", "hi": "भाई-बहन का स्वभाव", "bn": "ভাই-বোনের স্বভাব"},
    "Friends Nature": {"en": "Friends Nature", "hi": "मित्रों का स्वभाव", "bn": "বন্ধুদের স্বভাব"},
    "Spouse Nature": {"en": "Spouse Nature", "hi": "जीवनसाथी का स्वभाव", "bn": "জীবনসঙ্গীর স্বভাব"},
    "Pets": {"en": "Pets", "hi": "पालतू पशु", "bn": "গৃহপালিত পশু"},
    "Vastu": {"en": "Vastu/Home Energy", "hi": "वास्तु दोष/ऊर्जा", "bn": "বাস্তু দোষ ও প্রতিকার"},
    "Buy House": {"en": "Purchasing a House", "hi": "घर खरीदना", "bn": "গৃহ ক্রয়"},
    "Buy Vehicle": {"en": "Purchasing a Vehicle", "hi": "वाहन खरीदना", "bn": "যানবাহন ক্রয়"},
    "School Success": {"en": "Primary Education Success", "hi": "स्कूली शिक्षा में सफलता", "bn": "বিদ্যালয় শিক্ষার সাফল্য"},
    "Higher Education": {"en": "Higher Education", "hi": "उच्च शिक्षा", "bn": "উচ্চ শিক্ষা"},
    "Skills": {"en": "Skills & Talents", "hi": "कौशल और प्रतिभा", "bn": "দক্ষতা ও প্রতিভা"},
    "Weakness": {"en": "Weaknesses", "hi": "कमजोरियां", "bn": "দুর্বলতা"},
    "Love Relationships": {"en": "Love Relationships", "hi": "प्रेम संबंध", "bn": "প্রেমের সম্পর্ক"},
    "Married Life": {"en": "Married Life Stability", "hi": "वैवाहिक जीवन", "bn": "দাম্পত্য জীবন"},
    "Multiple Marriages": {"en": "Multiple Marriages", "hi": "बहु विवाह योग", "bn": "একাধিক বিবাহের যোগ"},
    "Sex Capacity": {"en": "Physical Vitality & Intimacy", "hi": "शारीरिक जीवन और अंतरंगता", "bn": "শারীরিক জীবন ও ঘনিষ্ঠতা"},
    "Extra Marital": {"en": "Extra-Marital Relationships", "hi": "विवाहेतर संबंध", "bn": "পরকীয়া সম্পর্ক"},
    "Immunity": {"en": "Immunity & Health Strength", "hi": "रोग प्रतिरोधक क्षमता", "bn": "রোগ প্রতিরোধ ক্ষমতা"},
    "Disease": {"en": "Diseases & Health Issues", "hi": "बीमारी और स्वास्थ्य समस्याएं", "bn": "রোগব্যাধি ও স্বাস্থ্য সমস্যা"},
    "Court Cases": {"en": "Court Cases & Disputes", "hi": "कोर्ट केस और विवाद", "bn": "কোর্ট কেস ও বিবাদ"},
    "Imprisonment": {"en": "Imprisonment/Confinement Risk", "hi": "जेल/कारावास का जोखिम", "bn": "কারাবাসের ঝুঁকি"},
    "Hospitalization": {"en": "Hospitalization Risk", "hi": "अस्पताल में भर्ती होने का जोखिम", "bn": "হাসপাতালে ভর্তির ঝুঁকি"},
    "Accident": {"en": "Accidents & Injuries Risk", "hi": "दुर्घटना का जोखिम", "bn": "দুর্ঘটনার ঝুঁকি"},
    "Interview": {"en": "Job Interviews & Selection", "hi": "साक्षात्कार और नौकरी चयन", "bn": "চাকরির ইন্টারভিউ ও নির্বাচন"},
    "Profession": {"en": "Profession & Career Path", "hi": "पेशा और आजीविका", "bn": "পেশা ও জীবিকা"},
    "Promotion": {"en": "Job Promotion & Growth", "hi": "पदोन्नति और उन्नति", "bn": "চাকরিতে পদোন্নতি ও উন্নতি"},
    "Bank Balance": {"en": "Wealth Accumulation & Bank Balance", "hi": "धन संचय और बैंक बैलेंस", "bn": "অর্থ সঞ্চয় ও ব্যাংক ব্যালেন্স"},
    "Speculation": {"en": "Speculation & Lottery Gains", "hi": "सट्टा और लॉटरी लाभ", "bn": "শেয়ার বাজার ও লটারি লাভ"},
    "Life Span": {"en": "Longevity & Life Span", "hi": "दीर्घायु और जीवन काल", "bn": "দীর্ঘায়ু ও জীবনকাল"},
    "Reason of Death": {"en": "Reason/Nature of Departure", "hi": "मृत्यु का कारण", "bn": "মৃত্যুর কারণ"},

    "Marriage NOT Promised (7th CSL {csl_planet} lacks 2/11).": {
        "en": "Marriage NOT Promised (7th CSL {csl_planet} lacks 2/11).",
        "hi": "विवाह का योग नहीं है (सातवें भाव का उप-स्वामी {csl_planet} भाव 2/11 से नहीं जुड़ा है)।",
        "bn": "বিবাহের যোগ নেই (৭ম ভাবের উপ-অধিপতি {csl_planet} ২/১১ ভাবের সাথে যুক্ত নয়)।"
    },
    "Marriage happened but separation confirmed (7th CSL {csl_planet} shows 2/11 and 1/6/8/12).": {
        "en": "Marriage promised but separation/dispute indicated (7th CSL {csl_planet} shows 2/11 and 1/6/8/12).",
        "hi": "विवाह का योग है लेकिन अलगाव की प्रबल संभावना है (सातवें भाव का उप-स्वामी {csl_planet} भाव 2/11 और 1/6/8/12 दोनों दर्शाता है)।",
        "bn": "বিবাহের যোগ আছে কিন্তু বিচ্ছেদের প্রবল সম্ভাবনা রয়েছে (৭ম ভাবের উপ-অধিপতি {csl_planet} ২/১১ এবং ১/৬/৮/১২ উভয় ভাব নির্দেশ করছে)।"
    },
    "Stable Marriage promised (7th CSL {csl_planet} lacks 1/6/8/12).": {
        "en": "Stable Marriage promised (7th CSL {csl_planet} lacks 1/6/8/12).",
        "hi": "स्थिर वैवाहिक जीवन का योग है (सातवें भाव का उप-स्वामी {csl_planet} भाव 1/6/8/12 से दूर है)।",
        "bn": "সুস্থির দাম্পত্য জীবনের যোগ রয়েছে (৭ম ভাবের উপ-অধিপতি {csl_planet} ১/৬/৮/১২ ভাবের সাথে যুক্ত নয়)।"
    },
    "MAJOR {event_type} WINDOW": {
        "en": "MAJOR {event_type} WINDOW",
        "hi": "मुख्य {event_type} समय",
        "bn": "প্রধান {event_type} সময়কাল"
    },
    "DIVORCE": {
        "en": "DIVORCE",
        "hi": "तलाक",
        "bn": "বিবাহবিচ্ছেদ"
    },
    "WIDOWHOOD": {
        "en": "WIDOWHOOD",
        "hi": "वैधव्य (जीवनसाथी की मृत्यु)",
        "bn": "বৈধব্য (জীবনসঙ্গী বিয়োগ)"
    },

    "pred_strong_1": {
        "en": "The cosmic gates are wide open. {karaka} smiles benevolently upon this aspect.",
        "hi": "ब्रह्मांडीय द्वार पूरी तरह खुले हैं। {karaka} इस पहलू पर कृपा बरसा रहे हैं।",
        "bn": "মহাজাগতিক দ্বার সম্পূর্ণ উন্মুক্ত। {karaka} এই বিষয়ের ওপর আশীর্বাদ বর্ষণ করছেন।"
    },
    "pred_strong_2": {
        "en": "A powerful destiny is written here, strong and undeniable.",
        "hi": "यहाँ एक शक्तिशाली भाग्य लिखा गया है, जो दृढ़ और अकाट्य है।",
        "bn": "এখানে একটি শক্তিশালী ভাগ্য লিখিত রয়েছে, যা দৃঢ় এবং অনস্বীকার্য।"
    },
    "pred_strong_3": {
        "en": "Fortune favors you greatly in this realm; the energy flows without obstruction.",
        "hi": "इस क्षेत्र में भाग्य आपका पूरा साथ दे रहा है; ऊर्जा बिना किसी बाधा के प्रवाहित हो रही है।",
        "bn": "এই ক্ষেত্রে ভাগ্য আপনাকে ব্যাপকভাবে সমর্থন করছে; শক্তি কোনো বাধা ছাড়াই প্রবাহিত হচ্ছে।"
    },
    "pred_moderate_1": {
        "en": "The path is visible but requires effort. {karaka} watches, waiting for your action.",
        "hi": "मार्ग दिखाई दे रहा है लेकिन प्रयास की आवश्यकता है। {karaka} देख रहे हैं, आपके कर्म की प्रतीक्षा कर रहे हैं।",
        "bn": "পথটি দৃশ্যমান তবে প্রচেষ্টার প্রয়োজন। {karaka} দেখছেন, আপনার কর্মের অপেক্ষায় আছেন।"
    },
    "pred_moderate_2": {
        "en": "Success is promised, though it may come with lessons to be learned.",
        "hi": "सफलता का वादा है, हालांकि इसके लिए कुछ सबक सीखने पड़ सकते हैं।",
        "bn": "সাফল্য নিশ্চিত, তবে এর জন্য কিছু শিক্ষা লাভ করতে হতে পারে।"
    },
    "pred_moderate_3": {
        "en": "A moderate influence. With free will and persistence, this fruit will ripen.",
        "hi": "एक मध्यम प्रभाव। स्वतंत्र इच्छा और दृढ़ता के साथ, यह फल अवश्य पकेगा।",
        "bn": "একটি মাঝারি প্রভাব। মুক্ত ইচ্ছা এবং অধ্যবসায়ের সাথে, এই ফল অবশ্যই পাকবে।"
    },
    "pred_weak_1": {
        "en": "The mists of karma obscure this path. {karaka} suggests focusing elsewhere.",
        "hi": "कर्म का कोहरा इस मार्ग को धुंधला कर रहा है। {karaka} कहीं और ध्यान केंद्रित करने का सुझाव देते हैं।",
        "bn": "কর্মের কুয়াশা এই পথটিকে অস্পষ্ট করছে। {karaka} অন্য কোথাও মনোনিবেশ করার পরামর্শ দিচ্ছেন।"
    },
    "pred_weak_2": {
        "en": "Challenges are indicated. Use this knowledge to prepare, not to fear.",
        "hi": "चुनौतियों का संकेत है। इस ज्ञान का उपयोग तैयारी के लिए करें, डरने के लिए नहीं।",
        "bn": "চ্যালেঞ্জের ইঙ্গিত রয়েছে। এই জ্ঞানটিকে প্রস্তুতির জন্য ব্যবহার করুন, ভয়ের জন্য নয়।"
    },
    "pred_weak_3": {
        "en": "The energy here is quiet. Do not force the river to flow upstream.",
        "hi": "यहाँ ऊर्जा शांत है। नदी को विपरीत दिशा में बहने के लिए मजबूर न करें।",
        "bn": "এখানে শক্তি শান্ত। নদীকে উল্টো দিকে প্রবাহিত হতে বাধ্য করবেন না।"
    },
}


SIGN_KEY_MAP = {
    "Aries": "sign_aries", "Taurus": "sign_taurus", "Gemini": "sign_gemini", "Cancer": "sign_cancer",
    "Leo": "sign_leo", "Virgo": "sign_virgo", "Libra": "sign_libra", "Scorpio": "sign_scorpio",
    "Sagittarius": "sign_sagittarius", "Capricorn": "sign_capricorn", "Aquarius": "sign_aquarius", "Pisces": "sign_pisces"
}

def t(key: str, lang: str = None, **kwargs) -> str:
    """
    Get translated string for a key.
    Args:
        key: Translation key (e.g., "app_title")
        lang: Optional language override. Uses current language if not provided.
        **kwargs: Arguments for string formatting (e.g., {name})
    Returns:
        Translated string, formatted if args provided.
        Returns key itself if not found.
    """
    lang = lang or _current_lang
    translation = T.get(key, {})
    text = translation.get(lang, translation.get("en", key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            # Fallback if formatting fails (e.g. key missing in format string)
            return text
            
    return text

def translate_sign(name: str, lang: str = None) -> str:
    """Translate a zodiac sign name."""
    key = SIGN_KEY_MAP.get(name, "")
    return t(key, lang) if key else name

# Numeral mappings for language-specific digit conversion
NUMERALS = {
    "en": "0123456789",
    "hi": "०१२३४५६७८९",
    "bn": "০১২৩৪৫৬৭৮৯"
}

def convert_number(value, lang: str = None) -> str:
    """
    Convert a number or numeric string to the script of the target language.
    
    Args:
        value: Integer, float, or string containing digits (e.g., 123, "45", "1+, 2, 3")
        lang: Optional language override. Uses current language if not provided.
    
    Returns:
        String with digits converted to the target language script.
        Special characters like '+', '-', '°', ',', ' ' are preserved.
    """
    lang = lang or _current_lang
    source_numerals = NUMERALS["en"]
    target_numerals = NUMERALS.get(lang, source_numerals)
    
    # Convert value to string
    text = str(value)
    
    # Build translation table
    trans_table = str.maketrans(source_numerals, target_numerals)
    
    return text.translate(trans_table)
