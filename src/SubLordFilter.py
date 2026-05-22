"""
SUB-LORD REJECTION FILTER - STRICT KP ASTROLOGY LOGIC
UAKP Critical Rule: Sub-Lord determines final outcome

CRITICAL KP RULE:
If Star Lord signifies SUCCESS (10, 11) but Sub-Lord signifies OBSTACLES (8, 12):
The event will NOT happen - Dasha window is REJECTED / FALSE_POSITIVE

This module provides a unified Sub-Lord Rejection Filter for all prediction modules.
"""

import re
from typing import Set, Tuple, Optional, Dict


class SubLordRejectionFilter:
    """
    STRICT SUB-LORD REJECTION FILTER
    
    KP Rule: The Sub-Lord is the final deciding factor.
    Even if Star Lord promises success, Sub-Lord negation will REJECT the event.
    """
    
    # Event-specific negation houses (obstacles/denial)
    NEGATION_HOUSES = {
        "marriage": {1, 6, 10, 12},
        "career": {5, 8, 12},
        "job": {5, 8, 12},
        "wealth": {5, 8, 12},
        "child": {1, 4, 10, 12},
        "health": {6, 8, 12},
        "court": {6, 8, 12},
        "loan": {5, 8, 12},
        "vehicle": {5, 8, 12},
        "general": {6, 8, 12}
    }
    
    # Event-specific success houses
    SUCCESS_HOUSES = {
        "marriage": {2, 7, 11},
        "career": {2, 6, 10, 11},
        "job": {2, 6, 10, 11},
        "wealth": {2, 6, 10, 11},
        "child": {2, 5, 11},
        "health": {1, 5, 11},
        "court": {1, 6, 11},
        "loan": {6, 11, 12},
        "vehicle": {4, 11},
        "general": {2, 5, 9, 11}
    }
    
    @staticmethod
    def get_houses_from_string(row_str: str) -> Set[int]:
        """Extract house numbers from Source_Row or Result_Row strings."""
        if not row_str or not isinstance(row_str, str):
            return set()
        return set(int(h) for h in re.findall(r'\d+', row_str))
    
    @staticmethod
    def check_strict_rejection(
        star_lord_houses: Set[int],
        sub_lord_houses: Set[int],
        event_type: str = "general"
    ) -> Tuple[bool, str, int]:
        """
        STRICT REJECTION CHECK
        
        Returns:
            (is_rejected, reason, penalty_score)
        """
        negation = SubLordRejectionFilter.NEGATION_HOUSES.get(
            event_type, SubLordRejectionFilter.NEGATION_HOUSES["general"]
        )
        success = SubLordRejectionFilter.SUCCESS_HOUSES.get(
            event_type, SubLordRejectionFilter.SUCCESS_HOUSES["general"]
        )
        
        # Check if Sub-Lord has negation houses
        sub_negation = sub_lord_houses & negation
        sub_success = sub_lord_houses & success
        
        # STRICT REJECTION RULE:
        # If Sub-Lord ONLY signifies negation (no success), REJECT
        if sub_negation and not sub_success:
            return (
                True,
                f"REJECTED: Sub-Lord signifies only negation houses {sorted(sub_negation)}",
                -100
            )
        
        # If negation outweighs success, REJECT
        if len(sub_negation) > len(sub_success):
            return (
                True,
                f"REJECTED: Sub-Lord negation ({sorted(sub_negation)}) > success ({sorted(sub_success)})",
                -80
            )
        
        # Star Lord shows promise but Sub-Lord has mixed signals
        star_success = star_lord_houses & success
        if star_success and sub_negation and sub_success:
            return (
                False,
                f"MIXED: Star={sorted(star_success)}, Sub negation={sorted(sub_negation)}",
                -30
            )
        
        # Pure success
        if sub_success and not sub_negation:
            return (
                False,
                f"CLEAR: Sub-Lord signifies success houses {sorted(sub_success)}",
                0
            )
        
        # Neutral (no clear indication)
        return (
            False,
            "NEUTRAL: No clear Sub-Lord indication",
            0
        )
    
    @staticmethod
    def filter_dasha_window(
        planet_sigs: dict,
        md_lord: str,
        ad_lord: str,
        pd_lord: str,
        event_type: str = "general"
    ) -> Tuple[bool, str, int]:
        """
        Filter a complete MD-AD-PD dasha window.
        
        Returns:
            (should_skip, reason, total_penalty)
        """
        total_penalty = 0
        reasons = []
        should_skip = False
        
        # Check each dasha lord
        for level, lord in [("MD", md_lord), ("AD", ad_lord), ("PD", pd_lord)]:
            sig = planet_sigs.get(lord, {})
            
            # Get star lord and sub lord significations
            star_lord = sig.get('star_lord', '')
            sub_lord = sig.get('sub_lord', '')
            
            # Get star lord's significations
            star_sig = planet_sigs.get(star_lord, {})
            star_houses = SubLordRejectionFilter.get_houses_from_string(
                star_sig.get('Result_Row', '')
            )
            
            # Get sub lord's significations
            sub_sig = planet_sigs.get(sub_lord, {})
            sub_houses = SubLordRejectionFilter.get_houses_from_string(
                sub_sig.get('Result_Row', '')
            )
            
            is_rejected, reason, penalty = SubLordRejectionFilter.check_strict_rejection(
                star_houses, sub_houses, event_type
            )
            
            if is_rejected:
                should_skip = True
                reasons.append(f"{level} ({lord}): {reason}")
            
            total_penalty += penalty
        
        if should_skip:
            return True, " | ".join(reasons), total_penalty
        
        return False, "All dasha lords passed Sub-Lord filter", total_penalty


# Convenience function for backward compatibility
def check_sublord_rejection(
    star_houses: Set[int],
    sub_houses: Set[int],
    event_type: str = "general"
) -> Tuple[bool, str]:
    """
    Simple function to check if Sub-Lord causes rejection.
    
    Returns: (is_rejected, reason)
    """
    is_rejected, reason, _ = SubLordRejectionFilter.check_strict_rejection(
        star_houses, sub_houses, event_type
    )
    return is_rejected, reason
