from datetime import datetime
import json
import os
from src.utils import get_resource_path
from src.rule_processor import SIGN_INDEX

class DivineDrishtiEngine:
    """
    🔱 DIVINE DRISHTI: Supreme Intelligence Engine - Master Orchestrator
    """
    
    def __init__(self, chart_data):
        self.chart_data = chart_data
        self.event_config = self.load_event_config()
        
        # Imports done locally to avoid circular dependency if any
        from src.signification import ChartDecomposer
        from src.rule_processor import SevenLayerAnalyzer, ConflictResolver, DivineScorer, PatternDetector
        from src.core_transit import DivineTransitEngine
        
        # Initialize all divine components
        self.decomposer = ChartDecomposer(chart_data)
        self.analyzer = SevenLayerAnalyzer(chart_data, self.decomposer)
        self.resolver = ConflictResolver(chart_data, self.decomposer)
        self.scorer = DivineScorer()
        self.pattern_detector = PatternDetector(chart_data, self.decomposer)
        
        # Initialize Swiss Ephemeris Transit Engine
        self.transit_engine = DivineTransitEngine(chart_data)
        
        # Chart metadata
        self.cusps = {c['cusp']: c for c in chart_data.get('house_cusps', [])}
        self.dob = None
        try:
            dob_str = chart_data.get('metadata', {}).get('dob', '')
            self.dob = datetime.strptime(dob_str, "%d-%m-%Y")
        except:
            pass

    def load_event_config(self):
        """Load event configuration from external JSON."""
        try:
            path = get_resource_path(os.path.join("data", "event_config.json"))
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading event config: {e}")
        return {}
    
    def get_target_signs(self, cusp_nums):
        """Get target sign indices from cusp numbers."""
        target_signs = []
        for cusp_num in cusp_nums:
            cusp = self.cusps.get(cusp_num, {})
            sign = cusp.get('sign', '')
            sign_idx = SIGN_INDEX.get(sign, -1)
            if sign_idx >= 0:
                target_signs.append(sign_idx)
        return target_signs
    
    def analyze_event_promise(self, event_type):
        """Analyze if an event is promised in the chart."""
        config = self.event_config.get(event_type, self.event_config.get("marriage"))
        if not config: return {"error": "Config not found"}
        
        cusp_num = config["cusp"]
        promise_houses = set(config["promise_houses"])
        denial_houses = set(config["denial_houses"])
        
        # Get CSL and its significations
        csl = self.decomposer.get_cusp_sub_lord(cusp_num)
        csl_houses = self.decomposer.get_planet_houses(csl, 'both')
        
        # Decompose CSL for deep analysis
        csl_decomp = self.decomposer.decompose_planet(csl)
        
        # Check promise vs denial
        promise_hit = csl_houses & promise_houses
        denial_hit = csl_houses & denial_houses
        
        # Get patterns
        patterns = self.pattern_detector.get_all_patterns(event_type)
        
        # Generate verdict
        if promise_hit and not denial_hit:
            verdict = "STRONGLY PROMISED"
            confidence = 85
        elif promise_hit and denial_hit:
            if len(promise_hit) >= len(denial_hit):
                verdict = "PROMISED WITH OBSTACLES"
                confidence = 60
            else:
                verdict = "WEAK PROMISE"
                confidence = 40
        elif denial_hit and not promise_hit:
            verdict = "DENIED"
            confidence = 20
        else:
            verdict = "UNCERTAIN"
            confidence = 50
        
        # Adjust for patterns
        if patterns["net_effect"] == "POSITIVE":
            confidence = min(100, confidence + 10)
        elif patterns["net_effect"] == "NEGATIVE":
            confidence = max(0, confidence - 10)
        
        return {
            "event_type": event_type,
            "cusp": cusp_num,
            "csl": csl,
            "csl_houses": list(csl_houses),
            "promise_houses_hit": list(promise_hit),
            "denial_houses_hit": list(denial_hit),
            "verdict": verdict,
            "confidence": confidence,
            "patterns": patterns,
            "csl_decomposition": csl_decomp
        }
    
    def divine_analysis(self, event_type, md, ad, pd, event_date):
        """Perform DIVINE ANALYSIS - comprehensive 7-layer analysis with scoring."""
        config = self.event_config.get(event_type, self.event_config.get("marriage"))
        if not config: return {"error": "Config not found"}
        
        cusp_num = config["cusp"]
        promise_houses = set(config["promise_houses"])
        denial_houses = set(config["denial_houses"])
        target_signs = self.get_target_signs(config["target_sign_cusps"])
        
        # Run 7-layer analysis
        layer_results = self.analyzer.run_full_analysis(
            cusp_num, promise_houses, denial_houses,
            md, ad, pd, event_date, target_signs, event_type
        )
        
        # Generate conflict report
        conflict_report = self.resolver.generate_conflict_report(
            md, ad, pd, promise_houses, denial_houses, cusp_num
        )
        
        # Calculate divine score
        divine_score = self.scorer.calculate_divine_score(layer_results, conflict_report)
        confidence_level = self.scorer.get_confidence_level(divine_score)
        
        # Get patterns
        patterns = self.pattern_detector.get_all_patterns(event_type)
        
        # Build comprehensive result
        return {
            "event_type": event_type,
            "dasha": f"{md}-{ad}-{pd}",
            "event_date": event_date.strftime("%d-%m-%Y") if event_date else "N/A",
            "divine_score": divine_score,
            "confidence_level": confidence_level,
            "layer_analysis": layer_results,
            "conflict_report": conflict_report,
            "patterns": patterns,
            "score_breakdown": self.scorer.score_breakdown.copy(),
            "final_verdict": layer_results["final_verdict"]
        }
    
    def quick_verdict(self, event_type, md, ad, pd):
        """Quick verdict without full analysis - for filtering."""
        config = self.event_config.get(event_type, self.event_config.get("marriage"))
        if not config: return False, "No Config"
        promise_houses = set(config["promise_houses"])
        
        # Quick intersection check
        md_houses = self.decomposer.get_planet_houses(md, 'result')
        ad_houses = self.decomposer.get_planet_houses(ad, 'result')
        pd_houses = self.decomposer.get_planet_houses(pd, 'result')
        
        md_match = bool(md_houses & promise_houses)
        ad_match = bool(ad_houses & promise_houses)
        pd_match = bool(pd_houses & promise_houses)
        
        match_count = sum([md_match, ad_match, pd_match])
        
        if match_count >= 2:
            return True, "LIKELY"
        elif match_count == 1:
            return True, "POSSIBLE"
        else:
            return False, "UNLIKELY"

    def generate_divine_report(self, analysis_result):
        """Generate formatted divine analysis report for display."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"🔱 DIVINE DRISHTI ANALYSIS: {analysis_result['event_type'].upper()}")
        lines.append("=" * 60)
        
        lines.append(f"\n📅 Dasha: {analysis_result['dasha']}")
        lines.append(f"📅 Date: {analysis_result['event_date']}")
        
        lines.append(f"\n⭐ DIVINE SCORE: {analysis_result['divine_score']}/100")
        lines.append(f"🎯 CONFIDENCE: {analysis_result['confidence_level']}")
        lines.append(f"📜 VERDICT: {analysis_result['final_verdict']}")
        
        # Layer details
        lines.append("\n" + "-" * 40)
        lines.append("7-LAYER ANALYSIS:")
        for layer in analysis_result['layer_analysis']['layers']:
            status = "✅" if layer['passed'] else "❌" if layer['passed'] is False else "⚪"
            lines.append(f"  {status} L{layer['layer']} {layer['name']}: +{layer['score']} - {layer['details'][:50]}")
        
        lines.append(f"\n  Layers Passed: {analysis_result['layer_analysis']['passed_layers']}/7")
        
        # Patterns
        if analysis_result['patterns']['positive_yogas']:
            lines.append("\n✨ POSITIVE YOGAS:")
            for yoga in analysis_result['patterns']['positive_yogas']:
                lines.append(f"  • {yoga['yoga']} ({yoga['strength']})")
        
        if analysis_result['patterns']['negative_patterns']:
            lines.append("\n⚠️ NEGATIVE PATTERNS:")
            for pattern in analysis_result['patterns']['negative_patterns']:
                lines.append(f"  • {pattern['pattern']} ({pattern['strength']})")
        
        # Conflicts
        if analysis_result['conflict_report']['conflicts_detected']:
            lines.append("\n⚔️ CONFLICTS RESOLVED:")
            for c in analysis_result['conflict_report']['conflicts_detected']:
                lines.append(f"  • {c}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
