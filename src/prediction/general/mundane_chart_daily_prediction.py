from datetime import datetime
import re
from src.core_transit import DivineTransitEngine

class MundaneDailyPrediction:
    """
    🔱 DAILY TRANSIT AUDITOR (MUNDANE CHART)
    
    Strict KP System for mundane transit analysis.
    Replaces point-based scoring with binary Promise/Denial logic.
    """
    
    RETRO_EXEMPT = {"Rahu", "Ketu"}
    
    def __init__(self, chart_data):
        self.chart_data = chart_data
        self.transit_engine = DivineTransitEngine(chart_data)
        
        self.house_significators = self._parse_house_significators()
        self.planet_significators = self._parse_planet_significators()

    def get_prediction(self, date):
        """
        Generate KP Daily Transit Audit for Mundane charts.
        """
        transits = self.transit_engine.get_all_planet_positions(date)
        dasha_lords = self._get_dasha_lords(date)
        
        # 1. Check Retrograde Blockages (Kill-Switch)
        retro_blocked = self._get_retro_blocked(transits)
        
        # 2. Analyze each House for Promise/Denial
        house_results = {}
        for h in range(1, 13):
            house_results[h] = self._analyze_house(h, transits, dasha_lords, retro_blocked)
            
        return self._generate_report(date, dasha_lords, house_results, transits, retro_blocked)

    def _analyze_house(self, house, transits, dasha_lords, retro_blocked):
        """Binary KP analysis for a house."""
        sigs = set(self.house_significators.get(house, []))
        
        favorable_transits = []
        unfavorable_transits = []
        
        # Check Transit Planets
        for pname, pdata in transits.items():
            full_name = self._normalize_name(pname)
            if full_name in retro_blocked:
                continue
                
            # If planet transits house directly
            if pdata.get("house") == house:
                if full_name in sigs:
                    favorable_transits.append(full_name)
                    
            # If planet's transit star lord is a significator
            star_lord = self._normalize_name(pdata.get("star_lord", ""))
            if star_lord in sigs:
                favorable_transits.append(f"{full_name}(★{star_lord})")

        # Status determination
        if favorable_transits:
            status = "FAVORABLE"
        else:
            status = "NEUTRAL"
            
        return {
            "status": status,
            "favorable": favorable_transits,
            "unfavorable": unfavorable_transits
        }

    def _get_retro_blocked(self, transits):
        blocked = {}
        for pname, pdata in transits.items():
            full_name = self._normalize_name(pname)
            if full_name in self.RETRO_EXEMPT:
                continue
            
            # Planet blocked if its transit star lord is retro
            sl_short = pdata.get("star_lord", "")
            sl_data = transits.get(sl_short)
            if sl_data and sl_data.get("is_retrograde", False):
                blocked[full_name] = self._normalize_name(sl_short)
        return blocked

    def _normalize_name(self, name):
        mapping = {
            "Sun": "Sun", "Mon": "Moon", "Mar": "Mars", "Mer": "Mercury",
            "Jup": "Jupiter", "Ven": "Venus", "Sat": "Saturn", "Rah": "Rahu", "Ket": "Ketu",
            "Moon": "Moon", "Mars": "Mars", "Mercury": "Mercury", "Jupiter": "Jupiter",
            "Venus": "Venus", "Saturn": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu"
        }
        return mapping.get(name, name)

    def _parse_house_significators(self):
        h_sigs = {}
        raw = self.chart_data.get('house_significators', [])
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

    def _get_dasha_lords(self, date):
        # Placeholder for mundane chart dashas
        return {"MD": "Jupiter", "AD": "Saturn", "PD": "Venus"}

    def _generate_report(self, date, dasha, house_results, transits, retro_blocked):
        lines = []
        lines.append(f"🌍 MUNDANE KP TRANSIT AUDIT: {date.strftime('%Y-%m-%d')}")
        lines.append("=" * 60)
        lines.append(f"DASHA: MD={dasha['MD']} | AD={dasha['AD']} | PD={dasha['PD']}")
        
        if retro_blocked:
            lines.append(f"⛔ RETRO BLOCKAGE: {', '.join([f'{k}(★{v})' for k,v in retro_blocked.items()])}")
        
        lines.append("-" * 60)
        lines.append(f"{'HOUSE':<6} {'STATUS':<15} {'SIGNIFICATORS AT PLAY'}")
        lines.append("-" * 60)
        
        for h in range(1, 13):
            res = house_results[h]
            sigs = ", ".join(res["favorable"][:3])
            lines.append(f"{h:<6} {res['status']:<15} {sigs}")
            
        lines.append("\n" + "-" * 60)
        lines.append("🪐 TRANSIT POSITIONS:")
        for pname, pdata in transits.items():
            full = self._normalize_name(pname)
            pdata.get("is_retrograde")
            lines.append(f"   {full:10s} → H{pdata['house']:<2d} [{pdata['sign']}] Star: {pdata['star_lord']}")
            
        lines.append("\n" + "=" * 60)
        lines.append("📝 TEXTUAL INTERPRETATION:")
        lines.append("-" * 60)
        
        favorable_houses = [h for h in range(1, 13) if house_results[h]['status'] == 'FAVORABLE']
        if 1 in favorable_houses: lines.append("• House 1: The nation/population is primarily affected by today's transits.")
        if 2 in favorable_houses: lines.append("• House 2: Economic indicators, state revenue, and banking sectors may see activity.")
        if 3 in favorable_houses: lines.append("• House 3: Transportation, media, neighboring relationships, and communications are highlighted.")
        if 4 in favorable_houses: lines.append("• House 4: Real estate, agriculture, weather conditions, and opposition parties are in focus.")
        if 5 in favorable_houses: lines.append("• House 5: Speculation, stock markets, entertainment, and national education show promise.")
        if 6 in favorable_houses: lines.append("• House 6: Public health, medical services, armed forces, and debts require attention.")
        if 7 in favorable_houses: lines.append("• House 7: Foreign affairs, international treaties, trade, and open enemies are highlighted.")
        if 8 in favorable_houses: lines.append("• House 8: Hidden matters, national mortality, sudden calamities, and pensions are active.")
        if 9 in favorable_houses: lines.append("• House 9: Judiciary, higher courts, religious institutions, and long-distance trade.")
        if 10 in favorable_houses: lines.append("• House 10: The ruling government, leaders, national prestige, and foreign trade are prominent.")
        if 11 in favorable_houses: lines.append("• House 11: National gains, allies, treaties, legislation, and parliament dynamics.")
        if 12 in favorable_houses: lines.append("• House 12: Secret foes, foreign debt, hospitals, prisons, and investments abroad.")
        if not favorable_houses:
            lines.append("• No major positive astrological developments for the nation today.")
            
        return "\n".join(lines)
