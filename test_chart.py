import os
import sys

PROD_PATH = r"C:\kp_astrology_softwarer_final(gravity)"
if os.path.exists(PROD_PATH) and PROD_PATH not in sys.path:
    sys.path.insert(0, PROD_PATH)
    sys.path.insert(0, os.path.join(PROD_PATH, "src"))

import swisseph as swe
swe.set_ephe_path(os.path.join(PROD_PATH, "ephe"))
swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)

from main import ChartEngine, AppMode

engine = ChartEngine()
p1 = engine._calculate_one('16-11-1983', '04:36:00', 22.5411, 88.3378, '+05:30', AppMode.BIRTH)
exp = engine.build_export(p1)

print("PLANETARY_POSITIONS")
for p in exp['planetary_positions']:
    print(f"{p['planet']} | {p['longitude_dms']} | {p['sign']} | {p['star_lord']} | {p['sub_lord']}")

print("HOUSE_CUSPS")
for c in exp['house_cusps']:
    print(f"Cusp {c['cusp']} | {c['longitude_dms']} | {c['sign']} | {c['star_lord']} | {c['sub_lord']}")
