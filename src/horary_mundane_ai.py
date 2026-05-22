"""
🔮 HORARY & MUNDANE ASTROLOGY AI
================================

A simplified prediction UI specifically for:
- Horary (Prashna) Astrology - Question-based predictions
- Mundane Astrology - World/Political event predictions

Features:
- Event Tab: LOAD DATA, SET QUERY, GENERATE (combined analysis)
- General Tab: Similar to birth chart analysis
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import json
import os
import sys
from src.prediction.general.horary_chart_daily_prediction import HoraryDailyPrediction
from src.prediction.general.mundane_chart_daily_prediction import MundaneDailyPrediction

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import utilities
try:
    from src.utils import get_resource_path
except ImportError:
    def get_resource_path(path):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), path)

# Import translations
try:
    from src.translations import t
except ImportError:
    def t(key): return key

# =============================================================================
# THEME (Matching main app)
# =============================================================================
THEME = {
    "app_bg": "#0D0D1A",
    "card_bg": "#161627",
    "card_bg_alt": "#1C1C35",
    "header_bg": "#0A0A14",
    "text_main": "#F0F0F5",
    "text_dim": "#8A8AA3",
    "gold": "#FFD700",
    "primary": "#9D4EDD",
    "secondary": "#00F5D4",
    "success": "#00E676",
    "warning": "#FFB347",
    "danger": "#FF6B6B",
    "border": "#2A2A4A"
}

# =============================================================================
# HORARY MUNDANE AI CLASS
# =============================================================================

class HoraryMundaneAI:
    """
    Simplified AI interface for Horary and Mundane predictions.
    
    Modes:
        - "horary": Question-based predictions with horary number
        - "mundane": World/Political event predictions
    """
    
    def __init__(self, root, mode="horary"):
        self.root = root
        self.mode = mode
        self.chart_data = None
        
        # Set title based on mode
        titles = {
            "horary": "🔮 Horary (Prashna) AI Analyzer",
            "mundane": "🌍 Mundane Political AI Analyzer"
        }
        self.root.title(titles.get(mode, "AI Analyzer"))
        self.root.state('zoomed')
        self.root.configure(bg=THEME["app_bg"])
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the simplified UI with 2 tabs"""
        
        # =================================================================
        # HEADER
        # =================================================================
        header = tk.Frame(self.root, bg=THEME["header_bg"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Accent line
        tk.Frame(header, bg=THEME["primary"], height=3).pack(fill=tk.X)
        
        # Title
        title_frame = tk.Frame(header, bg=THEME["header_bg"])
        title_frame.pack(fill=tk.X, pady=15)
        
        mode_icons = {"horary": "🔮", "mundane": "🌍"}
        mode_titles = {"horary": "HORARY (PRASHNA) AI", "mundane": "MUNDANE POLITICAL AI"}
        
        tk.Label(title_frame, 
                text=f"{mode_icons.get(self.mode, '✦')} {mode_titles.get(self.mode, 'AI ANALYZER')}",
                bg=THEME["header_bg"], fg=THEME["gold"],
                font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT, padx=20)
        
        # Close button
        tk.Button(title_frame, text="✕ Close", bg=THEME["danger"], fg="white",
                 font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, pady=5,
                 command=self.root.destroy).pack(side=tk.RIGHT, padx=20)
        
        # Bottom border
        tk.Frame(header, bg=THEME["border"], height=1).pack(fill=tk.X, side=tk.BOTTOM)
        
        # =================================================================
        # MAIN CONTENT - TABBED INTERFACE
        # =================================================================
        main = tk.Frame(self.root, bg=THEME["app_bg"])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create notebook (tabs)
        style = ttk.Style()
        style.configure("TNotebook", background=THEME["app_bg"])
        style.configure("TNotebook.Tab", background=THEME["card_bg"], 
                       foreground=THEME["text_main"], padding=[20, 10],
                       font=("Segoe UI", 11, "bold"))
        style.map("TNotebook.Tab", 
                 background=[("selected", THEME["primary"])],
                 foreground=[("selected", "white")])
        
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.event_tab = tk.Frame(self.notebook, bg=THEME["app_bg"])
        self.general_tab = tk.Frame(self.notebook, bg=THEME["app_bg"])
        
        self.notebook.add(self.event_tab, text="⏰ Event Timing")
        self.notebook.add(self.general_tab, text="📊 General Analysis")
        
        # Setup tab contents
        self._setup_event_tab()
        self._setup_general_tab()
        
        # New Tabs: Daily & Year Wise
        self.daily_tab = tk.Frame(self.notebook, bg=THEME["app_bg"])
        self.year_tab = tk.Frame(self.notebook, bg=THEME["app_bg"])
        
        self.notebook.add(self.daily_tab, text="📅 Daily Prediction")
        self.notebook.add(self.year_tab, text="📆 Year Prediction")
        
        self._setup_daily_tab()
        self._setup_year_tab()
    
    def _setup_event_tab(self):
        """Setup Event Timing tab with simplified buttons"""
        
        # Left panel - Controls
        left = tk.Frame(self.event_tab, bg=THEME["card_bg"], width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        left.pack_propagate(False)
        
        # Section header
        tk.Label(left, text="◈ EVENT ANALYSIS", bg=THEME["card_bg"], 
                fg=THEME["gold"], font=("Segoe UI", 14, "bold")).pack(pady=20)
        
        # Description based on mode
        if self.mode == "horary":
            desc = "Analyze horary chart for\nevent timing predictions"
        else:
            desc = "Analyze mundane chart for\npolitical/world event timing"
        
        tk.Label(left, text=desc, bg=THEME["card_bg"], 
                fg=THEME["text_dim"], font=("Segoe UI", 10)).pack(pady=10)
        
        # Separator
        tk.Frame(left, bg=THEME["border"], height=1).pack(fill=tk.X, padx=20, pady=20)
        
        # =================================================================
        # THREE MAIN BUTTONS
        # =================================================================
        
        # 1. LOAD DATA Button
        self._create_big_button(left, "📂 LOAD DATA", 
                               "Load chart from chart_data.json",
                               THEME["secondary"], self._load_data)
        
        # 2. SET QUERY Button
        self._create_big_button(left, "❓ SET QUERY",
                               "Define your question/event type",
                               THEME["warning"], self._set_query)
        
        # 3. GENERATE Button (Combined analysis)
        self._create_big_button(left, "⚡ GENERATE",
                               "Run UAKP Rules + Transit + Report",
                               THEME["primary"], self._generate_analysis)
        
        # Separator
        tk.Frame(left, bg=THEME["border"], height=1).pack(fill=tk.X, padx=20, pady=20)
        
        # Query display
        tk.Label(left, text="Current Query:", bg=THEME["card_bg"], 
                fg=THEME["text_dim"], font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        
        self.query_label = tk.Label(left, text="[Not Set]", bg=THEME["card_bg_alt"], 
                                   fg=THEME["gold"], font=("Segoe UI", 10),
                                   wraplength=260, justify="left")
        self.query_label.pack(fill=tk.X, padx=20, pady=5)
        
        # Right panel - Console output
        right = tk.Frame(self.event_tab, bg=THEME["app_bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        
        # Console header
        console_header = tk.Frame(right, bg=THEME["card_bg"])
        console_header.pack(fill=tk.X)
        
        tk.Label(console_header, text="📜 EVENT TIMING REPORT", bg=THEME["card_bg"],
                fg=THEME["gold"], font=("Segoe UI", 12, "bold")).pack(pady=10, padx=15, anchor="w")
        
        # Console area
        self.event_console = scrolledtext.ScrolledText(right, 
            bg="#0A0A14", fg=THEME["text_main"],
            font=("Consolas", 11), wrap=tk.WORD,
            insertbackground=THEME["gold"])
        self.event_console.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self._log_event("=" * 60)
        if self.mode == "horary":
            self._log_event("🔮 HORARY (PRASHNA) EVENT TIMING ANALYZER")
            self._log_event("   Question-based predictions using KP System")
        else:
            self._log_event("🌍 MUNDANE POLITICAL EVENT ANALYZER")  
            self._log_event("   World events & political predictions")
        self._log_event("=" * 60)
        self._log_event("\n📋 STEPS:")
        self._log_event("   1. Click 'LOAD DATA' to read chart_data.json")
        self._log_event("   2. Click 'SET QUERY' to define your question")
        self._log_event("   3. Click 'GENERATE' for full analysis\n")
    
    def _setup_general_tab(self):
        """Setup General Analysis tab"""
        
        # Left panel - Controls
        left = tk.Frame(self.general_tab, bg=THEME["card_bg"], width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        left.pack_propagate(False)
        
        # Section header
        tk.Label(left, text="◈ GENERAL ANALYSIS", bg=THEME["card_bg"], 
                fg=THEME["gold"], font=("Segoe UI", 14, "bold")).pack(pady=20)
        
        # Description
        tk.Label(left, text="Comprehensive chart analysis\nfor various life topics",
                bg=THEME["card_bg"], fg=THEME["text_dim"], 
                font=("Segoe UI", 10)).pack(pady=10)
        
        # Separator
        tk.Frame(left, bg=THEME["border"], height=1).pack(fill=tk.X, padx=20, pady=20)
        
        # Buttons
        self._create_big_button(left, "📂 LOAD DATA",
                               "Load chart from chart_data.json",
                               THEME["secondary"], self._load_data_general)
        
        self._create_big_button(left, "❓ SET QUERY",
                               "Choose analysis topic",
                               THEME["warning"], self._set_query_general)
        
        self._create_big_button(left, "📊 ANALYZE",
                               "Generate analysis report",
                               THEME["primary"], self._analyze_general)
        
        # Right panel - Console
        right = tk.Frame(self.general_tab, bg=THEME["app_bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        
        # Console header
        console_header = tk.Frame(right, bg=THEME["card_bg"])
        console_header.pack(fill=tk.X)
        
        tk.Label(console_header, text="📜 GENERAL ANALYSIS REPORT", bg=THEME["card_bg"],
                fg=THEME["gold"], font=("Segoe UI", 12, "bold")).pack(pady=10, padx=15, anchor="w")
        
        # Console area
        self.general_console = scrolledtext.ScrolledText(right,
            bg="#0A0A14", fg=THEME["text_main"],
            font=("Consolas", 11), wrap=tk.WORD,
            insertbackground=THEME["gold"])
        self.general_console.pack(fill=tk.BOTH, expand=True)
        
        self._log_general("=" * 60)
        self._log_general("📊 GENERAL ANALYSIS MODULE")
        self._log_general("=" * 60)
        self._log_general("\nReady for general astrological analysis.\n")
    
    def _create_big_button(self, parent, text, description, color, command):
        """Create a big styled button with description"""
        container = tk.Frame(parent, bg=THEME["card_bg"])
        container.pack(fill=tk.X, padx=20, pady=8)
        
        btn = tk.Button(container, text=text, bg=color, fg="white",
                       font=("Segoe UI", 12, "bold"), relief=tk.FLAT,
                       pady=12, cursor="hand2", command=command)
        btn.pack(fill=tk.X)
        
        tk.Label(container, text=description, bg=THEME["card_bg"],
                fg=THEME["text_dim"], font=("Segoe UI", 9)).pack(pady=(2, 0))
        
        # Hover effects
        def on_enter(e): btn['bg'] = self._lighten_color(color)
        def on_leave(e): btn['bg'] = color
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _lighten_color(self, hex_color):
        """Lighten a hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(min(255, c + 30) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)
    
    # =========================================================================
    # EVENT TAB ACTIONS
    # =========================================================================
    
    def _load_data(self):
        """Load chart data from chart_data.json"""
        self._log_event("\n" + "=" * 50)
        self._log_event("📂 LOADING CHART DATA...")
        self._log_event("=" * 50)
        
        try:
            target_filename = "chart_data.json"
            if self.mode == "mundane":
                target_filename = "chart_data(M).json"
            elif self.mode == "horary":
                target_filename = "chart_data(H).json"
            data_path = get_resource_path(os.path.join("data", target_filename))
            with open(data_path, 'r', encoding='utf-8') as f:
                self.chart_data = json.load(f)
            
            # Extract Language directly from chart data (Set by main.py)
            self.language = self.chart_data.get('metadata', {}).get('language', 'en')
            
            # Parse main.py export structure
            metadata = self.chart_data.get('metadata', {})
            planets_list = self.chart_data.get('planetary_positions', [])
            cusps_list = self.chart_data.get('house_cusps', [])
            
            name = metadata.get('name', 'Unknown')
            dob = metadata.get('dob', 'Unknown')
            
            self._log_event(f"\n✅ Chart loaded successfully!")
            self._log_event(f"   Name: {name}")
            self._log_event(f"   Date: {dob}")
            self._log_event(f"   Language: {self.language}")
            self._log_event(f"   Planets: {len(planets_list)}")
            self._log_event(f"   Cusps: {len(cusps_list)}\n")
            
        except FileNotFoundError:
            self._log_event("\n❌ ERROR: chart_data.json not found!")
            self._log_event("   Please generate a chart first.\n")
        except Exception as e:
            self._log_event(f"\n❌ ERROR: {str(e)}\n")
    
    def _set_query(self):
        """Set the prediction query"""
        from tkinter import simpledialog
        
        if self.mode == "horary":
            prompt = "Enter your horary question:"
        else:
            prompt = "Enter event to analyze (e.g., 'Election 2026', 'War prediction'):"
        
        query = simpledialog.askstring("Set Query", prompt)
        
        if query:
            self.current_query = query
            self.query_label.config(text=query)
            self._log_event(f"\n📝 Query set: {query}\n")
    
    def _generate_analysis(self):
        """Generate combined analysis: Rules Audit + Transit + Report"""
        if not self.chart_data:
            messagebox.showwarning("No Data", "Please load chart data first!")
            return
        
        if not hasattr(self, 'current_query') or not self.current_query:
            messagebox.showwarning("No Query", "Please set a query first!")
            return

        if self.mode == "horary":
            self._generate_horary_analysis()
            return
            
        # =================================================================
        # MUNDANE ANALYSIS (MundaneEngine)
        # =================================================================

        self._log_event("\n" + "=" * 60)
        self._log_event("🌍 INITIALIZING MUNDANE ENGINE")
        self._log_event("=" * 60)

        # 1. Determine Nation
        nation = "INDIA" # Default
        custom_nat_data = None
        if self.chart_data and 'metadata' in self.chart_data:
            metadata = self.chart_data['metadata']
            chart_name = metadata.get('name', 'INDIA').upper()
            
            from datetime import datetime
            dt_str = f"{metadata.get('date', '')} {metadata.get('time', '00:00:00')}".strip()
            def parse_date(dstr):
                for fmt in ["%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%Y-%m-%d"]:
                    try: return datetime.strptime(dstr, fmt)
                    except: pass
                return datetime.now()
            chart_date = parse_date(dt_str)
            
            custom_nat_data = {
                "name": chart_name,
                "date": chart_date,
                "latitude": float(metadata.get('lat', 0.0)),
                "longitude": float(metadata.get('lon', 0.0)),
                "timezone": float(metadata.get('tz', 0.0)),
                "asc_degree": 0.0
            }
            
            try:
                from prediction.horary.mundane_world import NATIONAL_CHARTS
                if chart_name in NATIONAL_CHARTS:
                    nation = chart_name
                    custom_nat_data = None
                else:
                    # Fuzzy match for things like "United States" -> "USA"
                    for key, data in NATIONAL_CHARTS.items():
                        db_name = data['name'].upper()
                        if chart_name in db_name or db_name in chart_name:
                            nation = key
                            custom_nat_data = None
                            break
                    if custom_nat_data:
                        nation = chart_name # Custom chart
            except ImportError:
                nation = chart_name

        self._log_event(f"   ✓ Target Nation: {nation}")

        # 2. Initialize Engine
        try:
            from prediction.horary.mundane_world import MundaneEngine
            from datetime import datetime
            engine = MundaneEngine(nation=nation, query_time=datetime.now(), national_data=custom_nat_data)
        except ImportError as e:
            self._log_event(f"⚠️ Engine Import Error: {e}")
            return
        except Exception as e:
            self._log_event(f"⚠️ Engine Init Error: {e}")
            return

        # 3. Determine Event Type
        event_type = self._infer_event_type(self.current_query)
        self._log_event(f"\n🧠 INFERRED TOPIC: {event_type.upper()}")
        
        # 4. Run Analysis
        self._log_event("\n🔍 STAGE 1: MUNDANE ANALYSIS")
        self._log_event("-" * 40)
        
        try:
            result = None
            q_lower = self.current_query.lower()
            
            lang = getattr(self, 'language', 'en')
            if event_type in ["job", "wealth", "business", "market", "economy"] or any(x in q_lower for x in ["market", "stock", "economy"]):
                self._log_event("   Running Economic & Market Analysis...")
                result = engine.analyze_market(market="Stock/Economy", lang=lang) if hasattr(engine, 'analyze_market') and 'lang' in engine.analyze_market.__code__.co_varnames else engine.analyze_market(market="Stock/Economy")
            elif any(x in q_lower for x in ["election", "vote", "politics", "government", "win"]):
                self._log_event("   Running Political & Election Analysis...")
                # Extract simple candidate names or default
                result = engine.analyze_election(c1="Incumbent Party", c2="Challenger Party", lang=lang) if hasattr(engine, 'analyze_election') and 'lang' in engine.analyze_election.__code__.co_varnames else engine.analyze_election(c1="Incumbent Party", c2="Challenger Party")
            elif any(x in q_lower for x in ["war", "conflict", "fight", "attack", "army"]):
                self._log_event("   Running War & Conflict Analysis...")
                result = engine.analyze_war(nation2="PAKISTAN", lang=lang)
            elif any(x in q_lower for x in ["disease", "health", "pandemic", "virus", "covid"]):
                self._log_event("   Running Pandemic Analysis...")
                result = engine.analyze_pandemic(lang=lang) if hasattr(engine, 'analyze_pandemic') and 'lang' in engine.analyze_pandemic.__code__.co_varnames else engine.analyze_pandemic()
            elif event_type == "disaster" or any(x in q_lower for x in ["disaster", "earthquake", "flood", "cyclone", "storm"]):
                self._log_event("   Running Natural Disaster Analysis...")
                result = engine.analyze_disaster(dtype="general", lang=lang) if hasattr(engine, 'analyze_disaster') and 'lang' in engine.analyze_disaster.__code__.co_varnames else engine.analyze_disaster(dtype="general")
            else:
                self._log_event("   Running General Political/Economic Analysis...")
                result = engine.analyze_market(market="General Economy", lang=lang) if hasattr(engine, 'analyze_market') and 'lang' in engine.analyze_market.__code__.co_varnames else engine.analyze_market(market="General Economy")
                
            if result:
                try:
                    from prediction.horary.mundane_world import LanguageSystem as MundaneLang
                    v_val = getattr(result.verdict, 'value', result.verdict)
                    verdict_str = MundaneLang.get(f"verdict_{v_val.lower()}", lang)
                except ImportError:
                    verdict_str = getattr(result.verdict, 'value', result.verdict)

                self._log_event(f"   ✓ Verdict: {verdict_str}")
                self._log_event(f"   ✓ Confidence: {result.confidence:.1f}%")
                self._log_event(f"   ✓ Primary Reason: {result.primary_reason}")
                
                if result.factors:
                    self._log_event("\n   📋 KEY ASTROLOGICAL FACTORS:")
                    for f in result.factors:
                        self._log_event(f"      • {f}")
                        
                if getattr(result, 'winner', None):
                    self._log_event(f"\n   🏆 PREDICTED WINNER: {result.winner}")
                    
                if getattr(result, 'affected_sectors', None):
                    self._log_event(f"\n   🏭 AFFECTED SECTORS: {', '.join(result.affected_sectors)}")
                    
            self._log_event("\n" + "=" * 60)
            self._log_event("✅ MUNDANE ANALYSIS COMPLETE")
            self._log_event("=" * 60 + "\n")
            
        except Exception as e:
            self._log_event(f"❌ Error during Mundane Analysis: {str(e)}")
            import traceback
            traceback.print_exc()

    def _generate_horary_analysis(self):
        """
        Specialized Analysis using HoraryEngine.
        Connects directly to prediction/horary/horary.py
        """
        try:
            from prediction.horary.horary import HoraryEngine, QuestionCategory
            from datetime import datetime
            
            # 1. Extract Metadata
            meta = self.chart_data.get('metadata', {})
            h_num = int(meta.get('horary_number', 0))
            if h_num == 0:
                 # Try finding it in description or assume error
                 self._log_event("❌ Error: Valid Horary Number not found in chart data.")
                 return

            # Parse Location
            loc_data = meta.get('location', {})
            if isinstance(loc_data, str):
                # Handle string format if necessary, but usually dict in chart_data
                pass 
                
            location = {
                "latitude": float(loc_data.get('lat', 0.0)),
                "longitude": float(loc_data.get('lon', 0.0)),
                "timezone": float(loc_data.get('tz', 5.5))
            }
            
            # Parse Time
            dob_str = meta.get('dob', '') # Usually "DD-MM-YYYY HH:MM:SS"
            try:
                cast_time = datetime.strptime(dob_str, "%d-%m-%Y %H:%M:%S")
            except:
                cast_time = datetime.now()
                self._log_event("⚠️ Warning: Could not parse chart time. Using 'now'.")

            # 2. Instantiate Engine
            self._log_event("\n" + "=" * 60)
            self._log_event("🔮 INITIALIZING HORARY ENGINE")
            self._log_event("=" * 60)
            
            engine = HoraryEngine(h_num, self.current_query, location, cast_time)
            
            # 3. Determine Category from Query
            inferred_cat = self._infer_event_type(self.current_query)
            try:
                # Map mundane/legacy string types to QuestionCategory
                cat_map = {
                    "job": QuestionCategory.JOB,
                    "wealth": QuestionCategory.WEALTH,
                    "marriage": QuestionCategory.MARRIAGE,
                    "child": QuestionCategory.CHILDREN,
                    "health": QuestionCategory.HEALTH,
                    "property": QuestionCategory.PROPERTY,
                    "vehicle": QuestionCategory.PROPERTY, # Fallback
                    "travel": QuestionCategory.TRAVEL
                }
                category = cat_map.get(inferred_cat, QuestionCategory.GENERAL)
            except:
                category = QuestionCategory.GENERAL
                
            self._log_event(f"   ✓ Horary Number: {h_num}")
            self._log_event(f"   ✓ Question Category: {category.value.title()}")
            
            # 4. Analyze Promise
            self._log_event("\n🔍 STAGE 1: PROMISE ANALYSIS")
            self._log_event("-" * 40)
            
            lang = getattr(self, 'language', 'en')
            # Fallback for HoraryEngine since it may not absorb lang natively
            result = engine.analyze(category, lang=lang) if hasattr(engine.analyze, '__code__') and 'lang' in engine.analyze.__code__.co_varnames else engine.analyze(category)
            
            try:
                from prediction.horary.horary import LanguageSystem as HoraryLang
                v_val = result.verdict.value
                verdict_str = HoraryLang.get(f"verdict_{v_val.lower()}", lang)
            except ImportError:
                verdict_str = result.verdict.value
                
            self._log_event(f"   ✓ Verdict: {verdict_str}")
            self._log_event(f"   ✓ Confidence: {result.confidence}%")
            self._log_event(f"   ✓ Reason: {result.primary_reason}")
            
            # Log Factors
            if result.supporting_factors:
                for f in result.supporting_factors:
                    self._log_event(f"      • {f}")

            # 5. Timing Calculation
            if result.verdict.value in ["YES", "LIKELY", "DELAYED", "MAYBE"]:  # Only check timing if YES/MAYBE/DELAYED
                self._log_event("\n📅 STAGE 2: TIMING PREDICTION")
                self._log_event("-" * 40)
                
                # Get rules to find promise houses for scanners
                # We need to access the rules used. 
                # Assuming engine.analyze set them internally, but we need them here.
                # We can re-fetch from QUESTION_RULES if we import it, or just ask engine.
                # Engine 'analyze' takes category, so we pass it again to calculate_timing
                # calculate_timing needs PROMISE HOUSES.
                
                # We need to import QUESTION_RULES or modify calculate_timing to look them up.
                # 'calculate_timing' takes 'promise_houses' set.
                # Let's import QUESTION_RULES
                from prediction.horary.horary import QUESTION_RULES
                rules = QUESTION_RULES.get(category, QUESTION_RULES[QuestionCategory.GENERAL])
                promise_houses = rules["promise_houses"]
                
                self._log_event(f"   Scanning for events (Horizon: Dynamic)...")
                
                windows = engine.calculate_timing(category, promise_houses)
                
                if windows:
                    for w in windows:
                        self._log_event(f"   🎯 {w['date_str']} | Score: {w['score']:.1f}")
                        self._log_event(f"      period: {w['period']}")
                        self._log_event(f"      {w['description']}")
                else:
                    self._log_event("   ⚠️ No strong timing windows found in near future.")
            else:
                 self._log_event("\n📅 STAGE 2: TIMING PREDICTION")
                 self._log_event("-" * 40)
                 self._log_event(f"   ⚠️ TIMING SKIPPED: Verdict is '{result.verdict.value}'.")
                 self._log_event("      (Timing is only calculated for YES/LIKELY/MAYBE outcomes)")
            
            self._log_event("\n" + "=" * 60)
            self._log_event("✅ HORARY ANALYSIS COMPLETE")
            self._log_event("=" * 60 + "\n")

        except Exception as e:
            self._log_event(f"\n❌ Error in Horary Analysis: {e}")
            import traceback
            traceback.print_exc()

    def _infer_event_type(self, query):
        """Map user query to event type."""
        q = query.lower()
        if any(x in q for x in ["job", "work", "career", "implement", "start", "business", "profession", "promotion"]):
            return "job"
        if any(x in q for x in ["earn", "money", "wealth", "finance", "gain", "profit", "rich"]):
            return "wealth" # Use wealth logic for earning
        if any(x in q for x in ["marry", "marriage", "wedding", "spouse", "partner", "wife", "husband"]):
            return "marriage"
        if any(x in q for x in ["divorce", "separate", "breakup"]):
            return "divorce"
        if any(x in q for x in ["child", "baby", "progeny", "pregnant", "birth"]):
            return "child"
        if any(x in q for x in ["sick", "health", "disease", "ill", "surgery", "recover"]):
            return "health"
        if any(x in q for x in ["house", "home", "property", "land", "flat", "apartment"]):
            return "property"
        if any(x in q for x in ["vehicle", "car", "buy", "bike", "scooter"]):
            return "vehicle"
        if any(x in q for x in ["travel", "abroad", "visa", "journey"]):
            # Assuming 'travel' config exists or fallback
            return "travel"
            
        return "general"

    def _run_rules_audit(self, event_type):
        """Run real chart promise analysis."""
        try:
            audit = self.engine.analyze_event_promise(event_type)
            
            self._log_event(f"   ✓ Cusp Analyzed: {audit['cusp']} ({audit.get('csl', 'Unknown')})")
            self._log_event(f"   ✓ Promise Verdict: {audit['verdict']}")
            self._log_event(f"   ✓ Confidence: {audit['confidence']}%")
            
            if audit['patterns']['positive_yogas']:
                self._log_event(f"   ✓ Yogas: {', '.join([y['yoga'] for y in audit['patterns']['positive_yogas']])}")
                
            return audit
        except Exception as e:
            self._log_event(f"   ⚠️ Audit Error: {str(e)}")
            return None

    def _run_timeline_scan(self, event_type):
        """Scan Dasha periods for high scoring windows."""
        from datetime import datetime
        
        top_windows = []
        dasa_list = self.chart_data.get('vimshottari_dasa_full', [])
        current_date = datetime.now()
        end_date_limit = current_date.replace(year=current_date.year + 2) # Scan 2 years
        
        candidates = []
        
        # Flatten the nested dasha list to find relevant PDs
        for md in dasa_list:
            md_lord = md['lord']
            
            # Check date range of MD
            md_end = datetime.strptime(md['end'].split()[0], "%d-%m-%Y")
            if md_end < current_date: continue
            
            for ad in md.get('sub_periods', []):
                ad_lord = ad['lord']
                ad_end = datetime.strptime(ad['end'].split()[0], "%d-%m-%Y")
                if ad_end < current_date: continue
                
                for pd in ad.get('sub_periods', []):
                    pd_lord = pd['lord']
                    pd_start_str = pd['start'].split()[0]
                    pd_end_str = pd['end'].split()[0]
                    pd_start = datetime.strptime(pd_start_str, "%d-%m-%Y")
                    pd_end = datetime.strptime(pd_end_str, "%d-%m-%Y")
                    
                    # Check window overlap with next 2 years
                    if pd_end < current_date: continue
                    if pd_start > end_date_limit: continue
                    
                    # Run Analysis for this window
                    # Use middle of PD for transit check
                    mid_point = pd_start + (pd_end - pd_start) / 2
                    
                    try:
                        result = self.engine.divine_analysis(event_type, md_lord, ad_lord, pd_lord, mid_point)
                        score = result['divine_score']
                        
                        candidates.append({
                            "md": md_lord, "ad": ad_lord, "pd": pd_lord,
                            "start": pd_start, "end": pd_end,
                            "score": score,
                            "verdict": result['final_verdict'],
                            "confidence": result['confidence_level']
                        })
                        
                        # Log high scoring ones immediately to show progress
                        if score > 50:
                            self._log_event(f"   Found candidate: {md_lord}-{ad_lord}-{pd_lord} (Score: {score})")
                            
                    except Exception as e:
                        # self._log_event(f"Skipped {md_lord}-{ad_lord}-{pd_lord}: {e}")
                        pass

        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:3]

    def _generate_event_timing(self, top_windows, audit):
        """Output the top predictions with Deep Transit Audit."""
        self._log_event(f"\n   📅 PREDICTED EVENT WINDOWS:")
        self._log_event(f"   ─────────────────────────────")
        
        if not top_windows:
            self._log_event(f"   ⚠️ No strong windows found in next 2 years.")
            return

        # Initialize Deep Audit Engine
        daily_engine = None
        try:
             daily_engine = HoraryDailyPrediction(self.chart_data)
        except: pass

        # Determine Target House for Scoring
        target_house = 1
        q = self.current_query.lower()
        if any(w in q for w in ["marriage", "spouse", "wedding", "married"]): target_house = 7
        elif any(w in q for w in ["job", "career", "work"]): target_house = 10
        elif any(w in q for w in ["child", "baby", "conception"]): target_house = 5
        elif any(w in q for w in ["property", "house", "land"]): target_house = 4
        elif any(w in q for w in ["vehicle", "car"]): target_house = 4
        elif any(w in q for w in ["foreign", "travel"]): target_house = 12 
        elif any(w in q for w in ["disease", "health", "hospital"]): target_house = 6
        elif any(w in q for w in ["wealth", "money", "finance"]): target_house = 2

        labels = ["PRIMARY", "SECONDARY", "TERTIARY"]
        
        for i, window in enumerate(top_windows):
            if i >= 3: break
            label = labels[i]
            
            dstr = window['start'].strftime('%d-%b-%Y')
            dend = window['end'].strftime('%d-%b-%Y')
            
            # 🔍 DEEP TRANSIT AUDIT
            audit_msg = ""
            retro_msg = ""
            if daily_engine:
                try:
                    # Check scores at START of window (entry point)
                    scores = daily_engine.get_transit_scores(window['start'])
                    
                    # Score Check
                    adj_score = scores['adjusted_cls'].get(target_house, 0)
                    base_score = scores['details'][target_house]['Base']
                    
                    status_icon = "🟢"
                    if adj_score < 1.0: status_icon = "🔴"
                    elif adj_score < 2.5: status_icon = "🟠"
                    
                    # Natal Freeze
                    natal_frozen = scores.get('natal_frozen', {})
                    freeze_icon = "🧊 FREEZE" if natal_frozen else ""
                    
                    # Retro Block
                    retro_blocked = scores.get('retro_blocked', {})
                    if retro_blocked:
                        retro_msg = f"\n      ⛔ BLOCKED: {', '.join(retro_blocked.keys())}"
                        
                    audit_msg = f" | {status_icon} Transit Score: {adj_score:.1f} (H{target_house}){freeze_icon}"
                    
                except Exception as e:
                    audit_msg = f" (Audit Err: {e})"
            
            self._log_event(f"   🎯 {label}:   {dstr} to {dend}")
            self._log_event(f"      Dasha: {window['md']}-{window['ad']}-{window['pd']} | Score: {window['score']:.1f}{audit_msg}{retro_msg}")
        
        if audit:
            self._log_event(f"\n   📊 STRUCTURAL PROMISE: {audit.get('verdict', 'N/A')}")
        
        self._log_event(f"   ⚠️  Note: Accuracy depends on birth/horary time precision.")
    
    # =========================================================================
    # GENERAL TAB ACTIONS
    # =========================================================================
    
    def _load_data_general(self):
        """Load data for general analysis"""
        self._log_general("\n📂 LOADING CHART DATA...")
        try:
            target_filename = "chart_data.json"
            if self.mode == "mundane":
                target_filename = "chart_data(M).json"
            elif self.mode == "horary":
                target_filename = "chart_data(H).json"
            data_path = get_resource_path(os.path.join("data", target_filename))
            with open(data_path, 'r', encoding='utf-8') as f:
                self.chart_data = json.load(f)
            self._log_general("✅ Chart loaded successfully!\n")
        except Exception as e:
            self._log_general(f"❌ ERROR: {str(e)}\n")
    
    def _set_query_general(self):
        """Set query for general analysis"""
        from tkinter import simpledialog
        
        topics = [
            "Career", "Finance", "Marriage", "Health", "Education",
            "Children", "Property", "Travel", "Legal", "Spiritual"
        ]
        
        query = simpledialog.askstring("Set Topic", 
            f"Enter analysis topic:\n({', '.join(topics)})")
        
        if query:
            self.general_query = query
            self._log_general(f"📝 Topic set: {query}\n")
    
    def _analyze_general(self):
        """Generate general analysis"""
        if not self.chart_data:
            messagebox.showwarning("No Data", "Please load chart data first!")
            return
        
        if not hasattr(self, 'general_query'):
            messagebox.showwarning("No Topic", "Please set a topic first!")
            return
        
        self._log_general("\n" + "=" * 50)
        self._log_general(f"📊 ANALYZING: {self.general_query.upper()}")
        self._log_general("=" * 50 + "\n")
        
        # 1. Map query to module
        module_info = self._map_query_to_module(self.general_query)
        
        if module_info == "USE_EVENT_TAB":
            self._log_general("⚠️ REDIRECT: Use Event Timing Tab")
            self._log_general("-" * 45)
            self._log_general("   For War, Elections, Markets, and World Events,")
            self._log_general("   please use the 'Event Timing' tab.")
            return

        if module_info == "BLOCKED_MUNDANE":
            self._log_general("⛔ ACCESS DENIED: Personal Query in Mundane Mode")
            self._log_general("-" * 45)
            self._log_general("   Mundane Astrology is strictly for WORLD/POLITICAL events.")
            self._log_general("   It cannot answer personal questions about marriage,")
            self._log_general("   children, or personal finance.")
            self._log_general("\n   👉 Please switch to HORARY mode for personal queries.")
            return

        if not module_info:
            self._log_general("⚠️ Could not identify specific topic from query.")
            
            if self.mode == 'mundane':
                 self._log_general("   (Mundane Mode matches: Election, War, Leadership, Nation)")
                 return
                 
            self._log_general("   Trying generic Life Path analysis...")
            # Fallback to personality/life path if available, or just list options
            module_info = ("personality_predict", "get_personality_report")

        # 2. Execute Prediction
        try:
            self._log_general("Running prediction analysis...\n")
            
            result = self._execute_prediction_module(module_info[0], module_info[1])
            
            if result.get("status") == "SUCCESS":
                self._log_general("✅ Analysis complete!\n")
                self._log_general(result.get("narrative", "No narrative returned."))
            else:
                self._log_general("❌ Analysis Failed:")
                self._log_general(result.get("error", "Unknown error"))
                self._log_general(result.get("narrative", ""))
                
        except Exception as e:
            self._log_general(f"❌ Critical Error: {str(e)}")

    def _map_query_to_module(self, query):
        """
        Map user query string to (module_name, function_name).
        Returns "BLOCKED_MUNDANE" if personal query in mundane mode.
        Returns None if no match found.
        """
        q = query.lower()
        self._log_general(f"   [DEBUG] Mapping Query: '{q}'")
        is_mundane = (self.mode == "mundane")
        
        # Mapping Rules
        # structure: (keywords, target, is_personal)
        rules = [
            # 1. MUNDANE COMPATIBLE (Allowed in both, but context differs)
            # 1. MUNDANE COMPATIBLE (Redirect to Event Tab)
            (["election", "win", "vote", "seat", "minister", "president", "pm", "king", "ruling", "opposition"], 
             "USE_EVENT_TAB", False),
            
            (["war", "conflict", "battle", "treaty", "shatru", "enemy"], 
             "USE_EVENT_TAB", False),

            (["market", "stock", "economy", "trade"], 
             "USE_EVENT_TAB", False),

            (["disaster", "earthquake", "flood", "cyclone", "pandemic", "virus"], 
             "USE_EVENT_TAB", False),

            # 2. PERSONAL TOPICS (Strictly Blocked in Mundane)
            (["career", "job", "work", "profession", "business", "promotion"], 
             ("career_direction_predict", "get_career_direction_report"), True),
             
            (["wealth", "money", "finance", "bank", "rich", "gain", "loss"], 
             ("bank_balance_predict", "get_bank_balance_report"), True),
             
            (["marriage", "wedding", "spouse", "partner", "wife", "husband"], 
             ("marriage_timing_predict", "get_marriage_timing_report"), True),
             
            (["divorce", "separate", "breakup"], 
             ("divorce_widowhood_predict", "get_divorce_report"), True), # Assuming separate logic or combined
             
            (["child", "baby", "adpot", "surrogacy", "pregnant", "ivf"],
             ("children_predict", "get_children_report"), True),
             
            (["health", "sick", "disease", "ill", "surgery", "recover", "pain"], 
             ("health_predict", "get_health_report"), True),
             
            (["education", "study", "exam", "college", "school", "result", "rank"], 
             ("education_predict", "get_education_report"), True),
             
            (["property", "house", "home", "land", "flat", "buy"], 
             ("property_predict", "get_property_report"), True),
             
            (["vehicle", "car", "bike", "scooter", "buy"], 
             ("vehicle_predict", "get_vehicle_report"), True),
             
            (["travel", "foreign", "abroad", "visa", "settle", "journey"], 
             ("travel_predict", "get_travel_report"), True),
             
            (["legal", "court", "case", "jail", "litigation"], 
             ("litigation_predict", "get_litigation_report"), True),

             (["spiritual", "moksha", "guru", "god", "soul"],
             ("spirituality_predict", "get_spirituality_report"), True)
        ]
        
        for keywords, target, is_personal in rules:
            if any(k in q for k in keywords):
                if is_mundane and is_personal:
                    return "BLOCKED_MUNDANE"
                return target
                
        return None

    def _execute_prediction_module(self, module_name, function_name):
        """Dynamically import and execute prediction module."""
        try:
            # 1. Import module
            module_path = f"prediction.life.{module_name}"
            try:
                module = importlib.import_module(module_path)
            except ImportError:
                 # Try event package if not in life
                module_path = f"prediction.event.{module_name}"
                module = importlib.import_module(module_path)

            # 2. Get function
            func = getattr(module, function_name)
            
            # 3. Prepare data
            # Most modules expect chart_data as input
            # Ensure full_degree is present
            if 'planetary_positions' in self.chart_data:
                 pass # DataConverter logic handled in main app usually, assume valid

            # 4. Call function
            result = func(self.chart_data)
            return result
            
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    # =========================================================================
    # DAILY & YEARLY TABS (PLACEHOLDERS)
    # =========================================================================
    
    def _setup_daily_tab(self):
        """Setup Daily Prediction Tab"""
        main = tk.Frame(self.daily_tab, bg=THEME["app_bg"])
        main.pack(fill=tk.BOTH, expand=True)

        # Header
        header = tk.Label(main, text="📅 DAILY PREDICTION", 
                         bg=THEME["app_bg"], fg=THEME["gold"],
                         font=("Segoe UI", 20, "bold"))
        header.pack(pady=20)
        
        # Date Selection Area
        selection_frame = tk.Frame(main, bg=THEME["card_bg"], padx=20, pady=20)
        selection_frame.pack(fill="x", padx=40, pady=10)
        
        # Label
        tk.Label(selection_frame, text="Select Date:", 
                font=("Segoe UI", 11, "bold"),
                fg=THEME["text_main"],
                bg=THEME["card_bg"]).pack(side="left", padx=(0, 15))
        
        from datetime import datetime
        current_date = datetime.now()
        
        # Day
        self.daily_day_var = tk.StringVar(value=str(current_date.day))
        days = [str(d) for d in range(1, 32)]
        self.combo_day = ttk.Combobox(selection_frame, textvariable=self.daily_day_var, values=days, width=3, state="readonly")
        self.combo_day.pack(side="left", padx=5)
        
        # Month
        self.daily_month_var = tk.StringVar(value=current_date.strftime("%B"))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.combo_month = ttk.Combobox(selection_frame, textvariable=self.daily_month_var, values=months, width=10, state="readonly")
        self.combo_month.pack(side="left", padx=5)
        
        # Year
        current_year = current_date.year
        self.daily_year_var = tk.StringVar(value=str(current_year))
        years = [str(y) for y in range(current_year - 5, current_year + 6)]
        self.combo_year = ttk.Combobox(selection_frame, textvariable=self.daily_year_var, values=years, width=5, state="readonly")
        self.combo_year.pack(side="left", padx=5)
        
        # Prediction Buttons Area
        btn_action_frame = tk.Frame(selection_frame, bg=THEME["card_bg"])
        btn_action_frame.pack(side="left", padx=20)
        
        tk.Button(btn_action_frame, text="📂 READ DATA", command=self._daily_read_data,
                 bg="#1a1a1a", fg="#00e5ff", font=("Segoe UI", 10, "bold"), 
                 padx=15, pady=5, relief=tk.FLAT).pack(side="left", padx=5)
                 
        tk.Button(btn_action_frame, text="⚡ PREDICTION", command=self._generate_daily_prediction,
                 bg=THEME["primary"], fg="white", font=("Segoe UI", 10, "bold"), 
                 padx=15, pady=5, relief=tk.FLAT).pack(side="left", padx=5)

        # Result Console
        self.daily_console = scrolledtext.ScrolledText(main, width=80, height=20, 
                                                      bg="#080808", fg="#ccc", font=("Consolas", 11),
                                                      insertbackground=THEME["gold"])
        self.daily_console.pack(fill="both", expand=True, padx=40, pady=10)

    def _daily_read_data(self):
        """Read data for the Daily Prediction tab based on horary/mundane mode."""
        self.daily_console.delete(1.0, tk.END)
        self.daily_console.insert(tk.END, f"📂 LOADING {self.mode.upper()} CHART DATA...\n")
        
        try:
            target_filename = "chart_data.json"
            if self.mode == "mundane":
                target_filename = "chart_data(M).json"
            elif self.mode == "horary":
                target_filename = "chart_data(H).json"
                
            data_path = get_resource_path(os.path.join("data", target_filename))
            
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.chart_data = json.load(f)
                    
                name = self.chart_data.get('metadata', {}).get('name', 'Unknown')
                self.daily_console.insert(tk.END, f"✅ DATA LOADED SUCCESSFULLY!\n")
                self.daily_console.insert(tk.END, f"   Chart Name: {name}\n")
                self.daily_console.insert(tk.END, f"   Mode Active: {self.mode.upper()}\n")
                self.daily_console.insert(tk.END, f"   Status: Ready for Daily Prediction...\n")
            else:
                self.daily_console.insert(tk.END, f"❌ ERROR: {target_filename} not found in data folder.\n")
        except Exception as e:
            self.daily_console.insert(tk.END, f"❌ CRITICAL ERROR: {str(e)}\n")

    def _generate_daily_prediction(self):
        """Generate Daily Prediction based on selected date."""
        from datetime import datetime
        day = self.daily_day_var.get()
        month = self.daily_month_var.get()
        year = self.daily_year_var.get()
        
        try:
            date_str = f"{day} {month} {year}"
            target_date = datetime.strptime(date_str, "%d %B %Y")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select a valid date.")
            return

        self.daily_console.delete(1.0, tk.END)
        
        if not hasattr(self, 'chart_data') or not self.chart_data:
            self.daily_console.insert(tk.END, "⚠️ WARNING: No chart data loaded!\n")
            self.daily_console.insert(tk.END, "Please click '📂 READ DATA' first before generating a prediction.\n")
            return
            
        mode_title = "UNKNOWN"
        
        try:
            # Select Engine based on Mode
            if self.mode == "mundane":
                engine = MundaneDailyPrediction(self.chart_data)
                mode_title = "MUNDANE"
            else:
                engine = HoraryDailyPrediction(self.chart_data)
                mode_title = "HORARY"
                
            report = engine.get_prediction(target_date)
            self.daily_console.insert(tk.END, report)
            
        except Exception as e:
            self.daily_console.insert(tk.END, f"Error generating {mode_title} prediction: {str(e)}\n\nCheck logs.")
            import traceback; traceback.print_exc()

    def _setup_year_tab(self):
        """Setup Year Prediction Tab"""
        main = tk.Frame(self.year_tab, bg=THEME["app_bg"])
        main.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Label(main, text="📆 YEAR WISE PREDICTION", 
                         bg=THEME["app_bg"], fg=THEME["gold"],
                         font=("Segoe UI", 20, "bold"))
        header.pack(pady=20)
        
        # Year Selection Area
        selection_frame = tk.Frame(main, bg=THEME["card_bg"], padx=20, pady=20)
        selection_frame.pack(fill="x", padx=40, pady=10)
        
        # Label
        tk.Label(selection_frame, text="Select Year:", 
                font=("Segoe UI", 11, "bold"),
                fg=THEME["text_main"],
                bg=THEME["card_bg"]).pack(side="left", padx=(0, 15))
        
        from datetime import datetime
        current_year = datetime.now().year
        
        # Year Dropdown
        self.year_val_var = tk.StringVar(value=str(current_year))
        years = [str(y) for y in range(current_year - 5, current_year + 11)]
        self.combo_year_only = ttk.Combobox(selection_frame, textvariable=self.year_val_var, values=years, width=10, state="readonly")
        self.combo_year_only.pack(side="left", padx=5)
        
        # Prediction Button
        tk.Button(selection_frame, text="⚡ PREDICTION", command=self._generate_year_prediction,
                 bg=THEME["primary"], fg="white", font=("Segoe UI", 10, "bold"), 
                 padx=15, pady=5, relief=tk.FLAT).pack(side="left", padx=20)

        # Result Console
        self.year_console = scrolledtext.ScrolledText(main, width=80, height=20, 
                                                      bg="#080808", fg="#ccc", font=("Consolas", 11),
                                                      insertbackground=THEME["gold"])
        self.year_console.pack(fill="both", expand=True, padx=40, pady=10)

    def _generate_year_prediction(self):
        """Generate Year Wise Prediction based on selected year."""
        year = self.year_val_var.get()
        
        self.year_console.delete(1.0, tk.END)
        
        if not hasattr(self, 'chart_data') or not self.chart_data:
            self.year_console.insert(tk.END, "⚠️ WARNING: No chart data loaded!\n")
            self.year_console.insert(tk.END, "Please click '📂 READ DATA' in the Daily Tab first.\n")
            return
            
        self.year_console.insert(tk.END, "="*60 + "\n")
        self.year_console.insert(tk.END, f"📆 YEAR WISE OVERVIEW FOR: {year}\n")
        self.year_console.insert(tk.END, "="*60 + "\n\n")
        
        mode_title = "MUNDANE" if self.mode == "mundane" else "HORARY"
        self.year_console.insert(tk.END, f"Scanning quarterly transits for {year} ({mode_title} Mode)...\n\n")
        self.year_console.update()
        
        try:
            from datetime import datetime
            if self.mode == "mundane":
                engine = MundaneDailyPrediction(self.chart_data)
            else:
                engine = HoraryDailyPrediction(self.chart_data)
                
            quarters = [
                ("Q1 (Jan-Mar)", f"15 January {year}"),
                ("Q2 (Apr-Jun)", f"15 April {year}"),
                ("Q3 (Jul-Sep)", f"15 July {year}"),
                ("Q4 (Oct-Dec)", f"15 October {year}")
            ]
            
            for q_name, date_str in quarters:
                target_date = datetime.strptime(date_str, "%d %B %Y")
                report = engine.get_prediction(target_date)
                
                # Extract just the active houses from the full daily report
                self.year_console.insert(tk.END, f"▶ {q_name} Outlook:\n")
                self.year_console.insert(tk.END, "-"*40 + "\n")
                
                lines = report.split('\n')
                favorable = []
                strong = []
                for line in lines:
                    if "FAVORABLE" in line:
                        h_num = line.split()[0]
                        favorable.append(h_num)
                    elif "STRONG" in line:
                        h_num = line.split()[0]
                        strong.append(h_num)
                
                if strong:
                    self.year_console.insert(tk.END, f"Strong Activity in Houses: {', '.join(strong)}\n")
                if favorable:
                    self.year_console.insert(tk.END, f"Favorable Activity in Houses: {', '.join(favorable)}\n")
                if not strong and not favorable:
                    self.year_console.insert(tk.END, "Period of slow or neutral developments.\n")
                
                self.year_console.insert(tk.END, "\n")
                self.year_console.update()
                
            self.year_console.insert(tk.END, "="*60 + "\n")
            self.year_console.insert(tk.END, "✅ YEARLY SCAN COMPLETE.\n")
            
        except Exception as e:
            self.year_console.insert(tk.END, f"\n❌ Error generating Yearly prediction: {str(e)}\n\nCheck logs.")
            import traceback; traceback.print_exc()


    def _execute_prediction_module(self, module_name, function_name):
        """Dynamically import and run a prediction module."""
        import importlib
        
        try:
            # Import module from prediction.general package
            module = importlib.import_module(f"prediction.general.{module_name}")
            
            # Get the function
            func = getattr(module, function_name)
            
            # NORMALIZE DATA BEFORE PASSING (Fix for UNKNOWN Output)
            # Now includes significators for accurate KP analysis
            norm_planets, norm_cusps, norm_p_sigs, norm_h_sigs = self._normalize_chart_data()
            
            # EXTRACT CONTEXT (Time & Query)
            dasha_data = self.chart_data.get('vimshottari_dasa_full', [])
            query_context = getattr(self, 'general_query', '')
            
            # DEBUG: Log first planet to verify normalization in UI
            if norm_planets:
                p1 = norm_planets[0]
                self._log_general(f"   [DEBUG] Input: {p1.get('name')} @ {p1.get('long'):.2f}°")
            
            # Call function with normalized data
            # Try passing 4 arguments first (New Signature)
            try:
                # NEW V5 SIGNATURE: Adds Dasha and Query for Time-Based Prediction
                return func(norm_planets, norm_cusps, norm_p_sigs, norm_h_sigs, dasha_data, query_context)
            except TypeError:
                try:
                    # FALLBACK V4: Just Significators
                    return func(norm_planets, norm_cusps, norm_p_sigs, norm_h_sigs)
                except TypeError:
                    # FALLBACK V2: Oldest
                    return func(norm_planets, norm_cusps)
            
        except ImportError:
            return {"status": "ERROR", "error": f"Module {module_name} not found"}
        except AttributeError:
            return {"status": "ERROR", "error": f"Function {function_name} not found in {module_name}"}
        except Exception as e:
            return {"status": "ERROR", "error": f"Execution error: {str(e)}"}

    # =========================================================================
    # DATA NORMALIZATION HELPERS
    # =========================================================================

    def _normalize_chart_data(self):
        """
        Convert chart_data.json format to prediction-ready format.
        (DMS strings -> Float longitudes, key remapping)
        """
        raw_planets = self.chart_data.get('planetary_positions', [])
        raw_cusps = self.chart_data.get('house_cusps', [])
        
        norm_planets = []
        for p in raw_planets:
            # Calculate absolute longitude
            dms_str = p.get('longitude_dms', '0° 0\' 0"')
            sign = p.get('sign', 'Aries')
            long_val = self._convert_dms_to_float(dms_str, sign)
            
            # ROBUST NAME EXTRACTION: Try 'planet', 'name', 'Planet'
            p_name = p.get("planet") or p.get("name") or p.get("Planet") or "Unknown"
            
            norm_planets.append({
                "name": p_name,              # Robust name
                "long": long_val,            # Float longitude
                "star": p.get("star_lord"),  # Map 'star_lord' -> 'star'
                "sub": p.get("sub_lord"),    # Map 'sub_lord' -> 'sub'
                "sign": sign,
                "speed": p.get("speed", 0.0), # Preserve if exists
                "is_retro": p.get("is_retro", False)
            })
            
        norm_cusps = []
        for c in raw_cusps:
            dms_str = c.get('longitude_dms', '0° 0\' 0"')
            sign = c.get('sign', 'Aries')
            long_val = self._convert_dms_to_float(dms_str, sign)
            
            norm_cusps.append({
                "id": c.get("cusp"),         # Map 'cusp' -> 'id'
                "long": long_val,            # Float longitude
                "star": c.get("star_lord"),
                "sub": c.get("sub_lord"),
                "sign": sign,
                "sign_lord": c.get("sign_lord")
            })
            
        # Extract Significators (Source & Result Rows)
        norm_planet_sigs = self.chart_data.get('planet_significators', [])
        norm_house_sigs = self.chart_data.get('house_significators', [])
            
        return norm_planets, norm_cusps, norm_planet_sigs, norm_house_sigs

    def _execute_prediction_module(self, module_name, function_name):
        """Dynamically import and run a prediction module."""
        import importlib
        
        try:
            # Import module from prediction.general package
            module = importlib.import_module(f"prediction.general.{module_name}")
            
            # Get the function
            func = getattr(module, function_name)
            
            # NORMALIZE DATA BEFORE PASSING (Fix for UNKNOWN Output)
            # Now includes significators for accurate KP analysis
            norm_planets, norm_cusps, norm_p_sigs, norm_h_sigs = self._normalize_chart_data()
            
            # DEBUG: Log first planet to verify normalization in UI
            if norm_planets:
                p1 = norm_planets[0]
                self._log_general(f"   [DEBUG] Input: {p1.get('name')} @ {p1.get('long'):.2f}°")
            
            # Call function with normalized data
            # Try passing 4 arguments first (New Signature)
            try:
                return func(norm_planets, norm_cusps, norm_p_sigs, norm_h_sigs)
            except TypeError:
                # Fallback to 2 arguments (Old Signature) for backward compatibility
                return func(norm_planets, norm_cusps)
            
        except ImportError:
            return {"status": "ERROR", "error": f"Module {module_name} not found"}
        except AttributeError:
            return {"status": "ERROR", "error": f"Function {function_name} not found in {module_name}"}
        except Exception as e:
            return {"status": "ERROR", "error": f"Execution error: {str(e)}"}

    def _convert_dms_to_float(self, dms_str, sign_name):
        """Convert '12° 18' 32"' + 'Capricorn' to absolute float degree."""
        try:
            # Parse DMS: "12° 18' 32""
            parts = dms_str.replace('"', '').split('°')
            deg = float(parts[0].strip())
            
            min_parts = parts[1].split("'")
            minute = float(min_parts[0].strip())
            second = float(min_parts[1].strip()) if len(min_parts) > 1 else 0.0
            
            # Calculate decimal degrees within sign
            decimal_within_sign = deg + (minute / 60.0) + (second / 3600.0)
            
            # Add sign offset
            sign_offset = self._get_sign_offset(sign_name)
            
            return sign_offset + decimal_within_sign
            
        except Exception:
            return 0.0

    def _get_sign_offset(self, sign_name):
        """Get starting degree for a sign."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        try:
            # Case insensitive lookup
            idx = next(i for i, s in enumerate(signs) if s.lower() == sign_name.lower())
            return idx * 30.0
        except StopIteration:
            return 0.0

    
    # =========================================================================
    # LOGGING UTILITIES
    # =========================================================================
    
    def _log_event(self, message):
        """Log message to event console"""
        self.event_console.insert(tk.END, message + "\n")
        self.event_console.see(tk.END)
    
    def _log_general(self, message):
        """Log message to general console"""
        self.general_console.insert(tk.END, message + "\n")
        self.general_console.see(tk.END)


# =============================================================================
# STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = HoraryMundaneAI(root, mode="horary")  # or "mundane"
    root.mainloop()
