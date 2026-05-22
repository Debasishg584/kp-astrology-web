from datetime import datetime
import re
from src.core_transit import DivineTransitEngine

class HoraryDailyPrediction:
    """
    🔱 DAILY TRANSIT AUDITOR (HORARY CHART)
    
    Refined KP System for Daily Transit Analysis.
    Replaces "Stability Formula" scoring with strict binary KP Gates:
      1. Retro-Gate (Kill-switch)
      2. Natal-Freeze (Promise blockage)
      3. Double-Transit (Power boost)
      4. Signification Match (Fulfillment)
    """
    
    RETRO_EXEMPT = {"Rahu", "Ketu"}
    MAJOR_PLANETS = {"Jupiter", "Saturn", "Rahu", "Ketu"}
    
    def __init__(self, chart_data):
        self.chart_data = chart_data
        self.transit_engine = DivineTransitEngine(chart_data)
        
        self.house_significators = self._parse_house_significators()
        self.planet_significators = self._parse_planet_significators()

    def get_prediction(self, date):
        """
        Produce a strict KP Transit Audit for the Horary context.
        """
        transits = self.transit_engine.get_all_planet_positions(date)
        dasha_lords = self._get_dasha_lords(date)
        
        # 1. Gate Analysis
        retro_blocked = self._get_retro_blocked(transits)
        natal_frozen = self._get_natal_frozen(transits)
        double_transit_houses = self._get_double_transit(transits)
        
        # 2. House Analysis
        house_results = {}
        for h in range(1, 13):
            house_results[h] = self._analyze_house(h, transits, dasha_lords, retro_blocked, natal_frozen, double_transit_houses)
            
        return self._generate_report(date, dasha_lords, house_results, transits, retro_blocked, natal_frozen, double_transit_houses)

    def _analyze_house(self, house, transits, dasha_lords, retro_blocked, natal_frozen, dt_houses):
        """Strict KP filter for a specific house."""
        sigs = set(self.house_significators.get(house, []))
        
        status = "NEUTRAL"
        indicators = []
        
        # Check Dasha Lords (The primary fruit deliverers)
        for level in ['MD', 'AD', 'PD']:
            lord = dasha_lords.get(level)
            if not lord: continue
            
            full_lord = self._normalize_name(lord)
            if full_lord in sigs:
                if full_lord in retro_blocked or full_lord in natal_frozen:
                    indicators.append(f"⚠️ {level} Lord {full_lord} significator but BLOCKED")
                else:
                    indicators.append(f"✅ {level} Lord {full_lord} signifies outcome")
                    status = "FAVORABLE"
        
        # Check Transit triggers
        for pname, pdata in transits.items():
            full_p = self._normalize_name(pname)
            if full_p in retro_blocked: continue
            
            # Direct transit to house
            if pdata.get("house") == house:
                if full_p in sigs:
                    indicators.append(f"✨ {full_p} transiting house")
                    status = "FAVORABLE" if status != "FAVORABLE" else "STRONG"
            
            # Transit Star Lord
            tsl = self._normalize_name(pdata.get("star_lord", ""))
            if tsl in sigs and full_p in self.MAJOR_PLANETS:
                indicators.append(f"💎 {full_p}(★{tsl}) supports")
                if status == "NEUTRAL": status = "FAVORABLE"

        # Double Transit Boost
        if house in dt_houses:
            indicators.append("⚡ Double Transit support")
            if status == "FAVORABLE": status = "STRONG"

        return {"status": status, "indicators": indicators}

    def _get_retro_blocked(self, transits):
        blocked = {}
        for pname, pdata in transits.items():
            full = self._normalize_name(pname)
            if full in self.RETRO_EXEMPT: continue
            
            sl_short = pdata.get("star_lord", "")
            sl_data = transits.get(sl_short)
            if sl_data and sl_data.get("is_retrograde", False):
                blocked[full] = self._normalize_name(sl_short)
        return blocked

    def _get_natal_frozen(self, transits):
        frozen = {}
        natal_pos = self.chart_data.get('planetary_positions', []) or []
        for p_info in natal_pos:
            lord = p_info.get('planet', '')
            sl = p_info.get('star_lord', '')
            if not lord or not sl: continue
            
            sl_full = self._normalize_name(sl)
            if sl_full in self.RETRO_EXEMPT: continue
            
            sl_transit = transits.get(self._get_short(sl_full))
            if sl_transit and sl_transit.get('is_retrograde', False):
                frozen[self._normalize_name(lord)] = sl_full
        return frozen

    def _get_double_transit(self, transits):
        # A house is boosted if both Jup and Sat hit it via occupancy or star
        jup_hit = set()
        sat_hit = set()
        
        for p_short, p_full in [('Jup', 'Jupiter'), ('Sat', 'Saturn')]:
            pos = transits.get(p_short)
            if not pos: continue
            
            target = jup_hit if p_short == 'Jup' else sat_hit
            target.add(pos.get('house', 0))
            
            sl = self._normalize_name(pos.get('star_lord', ''))
            # Get houses the star lord signifies in natal
            for h, sigs in self.house_significators.items():
                if sl in sigs: target.add(h)
                
        return jup_hit & sat_hit

    def _normalize_name(self, name):
        mapping = {
            "Sun": "Sun", "Mon": "Moon", "Mar": "Mars", "Mer": "Mercury",
            "Jup": "Jupiter", "Ven": "Venus", "Sat": "Saturn", "Rah": "Rahu", "Ket": "Ketu",
            "Moon": "Moon", "Mars": "Mars", "Mercury": "Mercury", "Jupiter": "Jupiter",
            "Venus": "Venus", "Saturn": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu"
        }
        return mapping.get(name, name)

    def _get_short(self, full):
        mapping = {"Sun":"Sun", "Moon":"Mon", "Mars":"Mar", "Mercury":"Mer", "Jupiter":"Jup", "Venus":"Ven", "Saturn":"Sat", "Rahu":"Rah", "Ketu":"Ket"}
        return mapping.get(full, full[:3])

    def _parse_house_significators(self):
        h_sigs = {}
        raw = self.chart_data.get('house_significators', []) or []
        for item in raw:
            try:
                h_str = str(item.get('house', '')).replace('H', '').strip()
                h = int(h_str)
                planets = set()
                if 'significators' in item and isinstance(item['significators'], list):
                    planets.update(item['significators'])
                for level in ['L1', 'L2', 'L3', 'L4']:
                    if level in item:
                        planets.update([p.strip() for p in str(item[level]).split(',') if p.strip()])
                h_sigs[h] = list(planets)
            except: continue
        return h_sigs

    def _parse_planet_significators(self):
        return {}

    def _get_dasha_lords(self, target_date):
        dasas = self.chart_data.get('vimshottari_dasa_full', []) or []
        result = {"MD": "??", "AD": "??", "PD": "??"}
        
        def parse_date(date_str):
            for fmt in ["%d-%m-%Y %H:%M", "%d-%m-%Y", "%d-%b-%Y"]:
                try: return datetime.strptime(date_str.strip(), fmt)
                except: continue
            return None
        
        for md in dasas:
            s, e = parse_date(md.get('start', '')), parse_date(md.get('end', ''))
            if s and e and s <= target_date <= e:
                result["MD"] = md.get('lord')
                for ad in md.get('sub_periods', []):
                    as_, ae = parse_date(ad.get('start', '')), parse_date(ad.get('end', ''))
                    if as_ and ae and as_ <= target_date <= ae:
                        result["AD"] = ad.get('lord')
                        for pd in ad.get('sub_periods', []):
                            ps, pe = parse_date(pd.get('start', '')), parse_date(pd.get('end', ''))
                            if ps and pe and ps <= target_date <= pe:
                                result["PD"] = pd.get('lord')
                                return result
        return result

    def _generate_report(self, date, dasha, house_results, transits, retro_blocked, natal_frozen, dt_houses):
        lines = []
        lines.append(f"🔮 HORARY DAILY TRANSIT AUDIT: {date.strftime('%Y-%m-%d')}")
        lines.append("=" * 60)
        lines.append(f"Dasha: {dasha['MD']}—{dasha['AD']}—{dasha['PD']}")
        
        if retro_blocked:
            lines.append(f"⛔ RETRO BLOCKAGE: {', '.join([f'{k}(★{v})' for k,v in retro_blocked.items()])}")
        if natal_frozen:
            lines.append(f"🧊 NATAL FREEZE: {', '.join([f'{k}(★{v})' for k,v in natal_frozen.items()])}")
        
        lines.append("-" * 60)
        lines.append(f"{'HOUSE':<6} {'STATUS':<15} {'KEY OBSERVATIONS'}")
        lines.append("-" * 60)
        
        for h in range(1, 13):
            res = house_results[h]
            obs = "; ".join([o.split(' ')[-1] for o in res["indicators"][:2]])
            lines.append(f"{h:<6} {res['status']:<15} {obs}")
            
        lines.append("\n" + "-" * 60)
        lines.append("🪐 TRANSIT POSITIONS:")
        for pname, pdata in transits.items():
            full = self._normalize_name(pname)
            lines.append(f"   {full:10s} → H{pdata['house']:<2d} [{pdata['sign']}] Star: {pdata['star_lord']}")
            
        lines.append("\n" + "=" * 60)
        lines.append("📝 TEXTUAL INTERPRETATION:")
        lines.append("-" * 60)
        
        favorable_houses = [h for h in range(1, 13) if house_results[h]['status'] in ['FAVORABLE', 'STRONG']]
        if 1 in favorable_houses: lines.append("• House 1: Focus is on self, current state of mind, and immediate health/vitality.")
        if 2 in favorable_houses: lines.append("• House 2: Matters involving cash flow, bank balance, family, or speech are highlighted.")
        if 3 in favorable_houses: lines.append("• House 3: Short trips, communications, siblings, or documents are favorable today.")
        if 4 in favorable_houses: lines.append("• House 4: Property, vehicles, mother, or domestic peace/comfort are indicated.")
        if 5 in favorable_houses: lines.append("• House 5: Children, romance, speculation, entertainment, or creativity show promise.")
        if 6 in favorable_houses: lines.append("• House 6: Daily work, service, overcoming diseases, loans, or competitive success.")
        if 7 in favorable_houses: lines.append("• House 7: Partnerships, marriage, business clients, or open interactions are favored.")
        if 8 in favorable_houses: lines.append("• House 8: Unexpected events, longevity, joint finances, or hidden matters are active.")
        if 9 in favorable_houses: lines.append("• House 9: Higher education, long travel, legal matters, spirituality, or fatherly figures.")
        if 10 in favorable_houses: lines.append("• House 10: Career advancement, status, recognition, or official governmental interactions.")
        if 11 in favorable_houses: lines.append("• House 11: Fulfillment of desires, gains, networking, and support from friends are strong.")
        if 12 in favorable_houses: lines.append("• House 12: Expenses, isolation, foreign connections, spiritual retreat, or hidden losses.")
        if not favorable_houses:
            lines.append("• No major positive developments indicated for today. A neutral day.")
            
        return "\n".join(lines)
