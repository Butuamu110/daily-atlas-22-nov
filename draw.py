#!/usr/bin/env python3
"""THE DAILY ATLAS — NI22 @rojanon11 (DUEL WINNER: variant A, 2D flat).
Duel test per akun: A 2D flat vs B 3D layered vs C 2D compact grid.
A menang karena paling bersih dan paling terbaca di 300px; B (3D)
menambah bayangan tapi tidak menambah keterbacaan dan jadi cadangan
banding (variants/entry-b.png); C kalah hierarki lead.
All facts come ONLY from POOL22-BARU v3 (13 verified 22 Nov 2026
events). COP31 is in ANTALYA, Turkiye. No story from the retired
POOL22 is used anywhere. Deterministic PIL only, no network.
Usage: python3 draw-a.py  -> variants/entry-a.png (etc.)
"""
import os, sys, math, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE  # final draw.py lives in the repo root, beside fonts/ + mapdata.py
sys.path.insert(0, ROOT)
from mapdata import WORLD
W = H = 1024
M = 24
CW = W - 2 * M

BG      = (243, 234, 211)
PAPER   = (250, 246, 233)
INK     = (38, 51, 42)
FOREST  = (31, 81, 48)
BURG    = (123, 45, 38)
RULE    = (178, 164, 128)
CARDB   = (196, 184, 152)
MAPBG   = (24, 54, 38)
LAND    = (168, 191, 165)
PARCH   = (243, 234, 211)
SHADOW  = (120, 108, 80)

REGIONS = {
    "EUROPE":   (176, 58, 46),
    "ASIA":     (29, 111, 184),
    "MIDEAST":  (125, 60, 152),
    "AFRICA":   (30, 132, 73),
    "AMERICAS": (202, 111, 30),
    "OCEANIA":  (20, 143, 119),
    "GLOBAL":   (93, 109, 126),
}

def _font(name, size):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", name), size)

_cache = {}
def PF(s): return _cache.setdefault(("pf", s), _font("PlayfairDisplay-900.ttf", s))
def AB(s): return _cache.setdefault(("ab", s), _font("Archivo-Bold.ttf", s))
def AM(s): return _cache.setdefault(("am", s), _font("Archivo-Medium.ttf", s))

# ---- pool v3: the day in numbers (all bound to cards) ----
NUMBERS = [
    ("2",      "Patriot radars IRGC CLAIMS hit"),
    ("720/9",  "India declared in Wellington"),
    ("50",     "laps, Las Vegas Grand Prix"),
    ("$4M",    "LPGA CME winner's prize"),
    ("12-2",   "Kyushu Basho leaders"),
    ("06:00",  "COP31 approval plenary, Antalya"),
]
TIMELINE = [
    ("02:40 WIB", "IRGC first Gulf statement"),
    ("03:43 WIB", "Mecca sirens sound"),
    ("04:05 WIB", "Myanmar M4.1 quake"),
    ("05:42 WIB", "Mecca interception confirmed"),
    ("11:00 WIB", "Las Vegas GP lights out"),
    ("19:16 WIB", "Falcon 9 NROL-136 lifts off"),
]
REGION_COUNTS = [  # counted from CARDS + BRIEFS below: 4+5+7+0+15+5+4 = 40
    ("EUROPE", 4), ("ASIA", 5), ("MIDEAST", 7), ("AFRICA", 0),
    ("AMERICAS", 15), ("OCEANIA", 5), ("GLOBAL", 4),
]

# ---- 13 cards: one per verified 22 Nov event ----
CARDS = [
 dict(no=1, place="THE GULF", region="MIDEAST", topic="WAR",
      headline="Gulf hit overnight: radars, fire, drones",
      deck="IRGC claims missiles and drones hit 2 US Patriot radars in Bahrain; a civilian plant burns. A drone is downed at Ali Al Salem, Kuwait. (IRGC / Bahrain)",
      tag="CLAIM - IRGC", stag="IRGC", label="2 RADARS CLAIMED",
      caption="THE GULF - OVERNIGHT STRIKES", lon=50.5, lat=26.0, scene="gulf"),
 dict(no=2, place="MAKKAH REGION", region="MIDEAST", topic="DEFENCE",
      headline="Houthi missile to Makkah is intercepted",
      deck="Civil-defence sirens sound at 23:43 Riyadh time; the Saudi-led coalition confirms the interception at 01:42. No damage reported. (Anadolu)",
      tag="CONFIRMED - ANADOLU", stag="ANADOLU", label="INTERCEPTED 01:42",
      caption="MAKKAH - MISSILE DOWNED", lon=39.8, lat=21.4, scene="intercept"),
 dict(no=3, place="ANTALYA", region="GLOBAL", topic="CLIMATE",
      headline="COP31 final text tabled in Antalya",
      deck="President Murat Kurum tables the final package; objections close 03:00 GMT and the approval plenary is set for 06:00 GMT Sunday. (Reuters)",
      tag="REUTERS", stag="REUTERS", label="FINAL TEXT 06:00 GMT",
      caption="ANTALYA - FINAL TEXT TABLED", lon=30.7, lat=36.9, scene="cop"),
 dict(no=4, place="MYANMAR", region="ASIA", topic="QUAKE",
      headline="M4.1 quake strikes Myanmar at 04:05 WIB",
      deck="NCS records a magnitude 4.1 quake at 02:35:57 IST, 95 km deep, epicentre 24.404N 94.616E. (NCS / ANI)",
      tag="NCS - ANI", stag="NCS", label="M4.1 - 95 KM DEEP",
      caption="MYANMAR - M4.1 QUAKE", lon=94.6, lat=24.4, scene="quake"),
 dict(no=5, place="WELLINGTON", region="OCEANIA", topic="CRICKET",
      headline="India declare 720/9 - a record in New Zealand",
      deck="India declare 720/9 on day four: Rahul 136, Pant 128. New Zealand made 368 (Nicholls 175, Bumrah 4-92); India lead by 352. (IANS / AFP)",
      tag="IANS - AFP", stag="IANS", label="720/9 DECLARED",
      caption="WELLINGTON - RECORD 720/9", lon=174.8, lat=-41.3, scene="cricket"),
 dict(no=6, place="LAS VEGAS", region="AMERICAS", topic="MOTORSPORT",
      headline="Las Vegas Grand Prix races under the lights",
      deck="Lights out 04:00 UTC (11:00 WIB) for 50 laps of the Strip Circuit, round 22. (formula1.com)",
      tag="FORMULA1.COM", stag="F1.COM", label="50 LAPS - ROUND 22",
      caption="LAS VEGAS - GP UNDER LIGHTS", lon=-115.2, lat=36.1, scene="f1"),
 dict(no=7, place="VANDENBERG", region="AMERICAS", topic="SPACE",
      headline="Falcon 9 launches NROL-136 at 19:16 WIB",
      deck="SpaceX launches the 15th NRO constellation batch from SLC-4E; booster B1097 returns to LZ-4. (VSFB)",
      tag="VSFB - SPACEX", stag="VSFB", label="B1097 RETURNS TO LZ-4",
      caption="VANDENBERG - NROL-136 UP", lon=-120.5, lat=34.7, scene="rocket"),
 dict(no=8, place="ANFIELD", region="EUROPE", topic="FOOTBALL",
      headline="Liverpool host Manchester United at 23:30 WIB",
      deck="The derby closes Premier League Matchweek 11 at Anfield, 16:30 UTC. Hull host Brighton at 21:00 WIB. (PL)",
      tag="PREMIER LEAGUE", stag="PL", label="16:30 UTC - ANFIELD",
      caption="ANFIELD - DERBY NIGHT", lon=-2.96, lat=53.43, scene="football"),
 dict(no=9, place="TURIN", region="EUROPE", topic="TENNIS",
      headline="Alcaraz v Zverev for the Turin title",
      deck="The ATP Finals title match is played Sunday night in Turin (about 16:00 UTC). Alcaraz rallied past Shelton. (ATP)",
      tag="ATP - REUTERS", stag="ATP", label="FINAL - TURIN",
      caption="TURIN - ATP FINALS", lon=7.7, lat=45.1, scene="tennis"),
 dict(no=10, place="NAPLES, FLORIDA", region="AMERICAS", topic="GOLF",
      headline="A Lim Kim leads the LPGA finale at -18",
      deck="The CME finale is played Sunday at Tiburon; Kim leads by one from Thitikul and Yoshida. Winner takes $4m. (LPGA)",
      tag="LPGA.COM", stag="LPGA", label="-18 LEADS BY ONE",
      caption="NAPLES - LPGA FINALE", lon=-81.8, lat=26.1, scene="golf"),
 dict(no=11, place="FUKUOKA", region="ASIA", topic="SUMO",
      headline="Kyushu Basho ends: two men tied at 12-2",
      deck="Senshuraku at Fukuoka: Onosato and Wakamotoharu are 12-2, Atamifuji 11-3. Onosato faces Hoshoryu. (JSA)",
      tag="JSA", stag="JSA", label="12-2 - TITLE DECIDER",
      caption="FUKUOKA - SENSHURAKU", lon=130.4, lat=33.6, scene="sumo"),
 dict(no=12, place="GEORGIA", region="AMERICAS", topic="GOLF",
      headline="RSM Classic round three moves to Sunday",
      deck="Saturday washed out, so round three is played Sunday at Sea Island; three share the lead at -9. Final Monday. (PGA)",
      tag="PGA TOUR - REUTERS", stag="PGA", label="THREE TIED AT -9",
      caption="SEA ISLAND - RSM R3 SUNDAY", lon=-81.3, lat=31.2, scene="golf2"),
 dict(no=13, place="UNITED STATES", region="AMERICAS", topic="NFL",
      headline="NFL Week 12: eleven games on Sunday",
      deck="The early window opens 18:00 UTC (Monday 01:00 WIB); Vikings visit the 49ers at night. (ESPN / NFL)",
      tag="ESPN - NFL", stag="ESPN", label="11 GAMES SUNDAY",
      caption="USA - NFL WEEK 12", lon=-98.0, lat=39.0, scene="nfl"),
]

# ---- briefs 14-40: sub-facts of the same 13 events (all 22 Nov) ----
BRIEFS = [
 (14, "Manama Bahrain demands the UN Security Council enforce Resolution 2817 (Al Jazeera)", "MIDEAST", 50.6, 26.2),
 (15, "Bahrain A civilian industrial facility catches fire in the overnight strikes (Bahrain)", "MIDEAST", 50.5, 26.0),
 (16, "Kuwait A drone is intercepted at Ali Al Salem base, the first since September (IRGC)", "MIDEAST", 47.9, 29.3),
 (17, "Riyadh Mecca sirens sound at 23:43 local time on Saturday night (Anadolu)", "MIDEAST", 46.7, 24.6),
 (18, "Jeddah The coalition confirms the Makkah interception at 01:42 Sunday (Anadolu)", "MIDEAST", 39.2, 21.5),
 (19, "Antalya COP31 objections are shut at 03:00 GMT by President Murat Kurum (Reuters)", "GLOBAL", 30.7, 36.9),
 (20, "Antalya The third draft recalls the Dubai fossil-fuel deal (Reuters)", "GLOBAL", 30.7, 36.9),
 (21, "Antalya Australia co-hosts the COP31 presidency with Chris Bowen (Reuters)", "GLOBAL", 30.7, 36.9),
 (22, "Naypyitaw The quake epicentre is 24.404N 94.616E, depth 95 km (NCS)", "ASIA", 94.6, 24.4),
 (23, "Wellington Rahul 136 and Pant 128 build India's record total (IANS)", "OCEANIA", 174.8, -41.3),
 (24, "Wellington Gill 98, Jaiswal 85 and Padikkal 80 in the 720/9 (IANS)", "OCEANIA", 174.8, -41.3),
 (25, "Wellington Nicholls 175 not out; Bumrah takes 4-92 for India (AFP)", "OCEANIA", 174.8, -41.3),
 (26, "Las Vegas The Strip Circuit hosts round 22 of the season (formula1.com)", "AMERICAS", -115.2, 36.1),
 (27, "Las Vegas Lights out 04:00 UTC, 11:00 WIB on Sunday (Williams F1)", "AMERICAS", -115.2, 36.1),
 (28, "Vandenberg The launch window runs 12:16-12:46 UTC (VSFB alert)", "AMERICAS", -120.5, 34.7),
 (29, "Vandenberg NROL-136 is the 15th batch of the NRO constellation (SpaceX)", "AMERICAS", -120.5, 34.7),
 (30, "Hull Hull host Brighton at 14:00 UTC, 21:00 WIB (premierleague.com)", "EUROPE", -0.4, 53.7),
 (31, "Turin Alcaraz rallies past Shelton to reach the final (ATP)", "EUROPE", 7.7, 45.1),
 (32, "Naples Thitikul and Yoshida trail A Lim Kim by one shot (LPGA)", "AMERICAS", -81.8, 26.1),
 (33, "Naples The $4m winner's prize is the biggest in women's golf (LPGA)", "AMERICAS", -81.8, 26.1),
 (34, "Fukuoka Atamifuji sits third at 11-3 going into senshuraku (JSA)", "ASIA", 130.4, 33.6),
 (35, "Fukuoka Wakamotoharu faces Atamifuji in the title race (JSA)", "ASIA", 130.4, 33.6),
 (36, "Sea Island Thorbjornsen, Penge and Neergaard-Petersen share -9 (PGA Tour)", "AMERICAS", -81.3, 31.2),
 (37, "Sea Island The RSM final moves to Monday after the washout (Reuters)", "AMERICAS", -81.3, 31.2),
 (38, "New York The early NFL window opens 13:00 ET, 18:00 UTC (ESPN)", "AMERICAS", -74.0, 40.7),
 (39, "San Francisco Vikings visit the 49ers in Sunday Night Football (NFL)", "AMERICAS", -122.4, 37.8),
 (40, "Wellington India's 720/9 is the highest Test total ever made in New Zealand (AFP)", "OCEANIA", 174.8, -41.3),
]

DATE_CHECK = ("Left out as earlier news: three missiles over Riyadh (Friday 21 November), the EU-Indonesia "
 "CEPA signing (Friday 21 November), the France march of 82,500 (Friday 21 November), the ICJ Rohingya "
 "verdict (Thursday 19 November), the Shenzhen three-leader summit (Thursday 19 November), the FBI NCIC "
 "breach (Thursday 19 November), Kenya's last Ebola patient going home (Tuesday 11 November), the Norway "
 "oil ruling (Thursday 13 November), the Lviv strike (Thursday 20 November) and the tanker attack off "
 "Hormuz (Saturday 11:27 UTC). Not yet happened, so not "
 "shown: the Davis Cup final (29 November).")
FOOTER_L = "Every story here happened, or was first reported, on Sunday 22 November 2026. Contested claims are attributed."
FOOTER_R = "Sources named beside each story - original drawings"

# ---- text helpers ----
def tw(d, s, f):
    return d.textlength(s, font=f)

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit(d, s, start, maxw, floor=8):
    size = start
    while size > floor and tw(d, s, AB(size)) > maxw:
        size -= 1
    return AB(size)

def ctext(d, cx, y, s, f, fill):
    d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)

# ---- flat scenes (one per card) ----
def sc_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 54, 74))
    for i, bh in enumerate((0.34, 0.48, 0.28, 0.42, 0.32, 0.52, 0.30)):
        bx = x + int(w * (0.02 + 0.14 * i)); bw = int(w * 0.12)
        d.rectangle([bx, y + h - int(h * bh), bx + bw, y + h], fill=(26, 27, 38))
    cx, cy = x + int(w * 0.60), y + int(h * 0.34)
    for k in range(12):
        a = 2 * math.pi * k / 12
        r = int(h * (0.30 if k % 2 == 0 else 0.16))
        d.line([cx, cy, cx + r * math.cos(a), cy + r * 0.72 * math.sin(a)], fill=(255, 170, 60), width=2)
    d.ellipse([cx - int(h * 0.13), cy - int(h * 0.10), cx + int(h * 0.13), cy + int(h * 0.10)], fill=(255, 196, 84))

def sc_intercept(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 30, 52))
    for i, bh in enumerate((0.30, 0.44, 0.26, 0.38, 0.30, 0.48, 0.28)):
        bx = x + int(w * (0.02 + 0.14 * i)); bw = int(w * 0.12)
        d.rectangle([bx, y + h - int(h * bh), bx + bw, y + h], fill=(12, 14, 26))
    for fx, fy in ((0.30, 0.30), (0.58, 0.22), (0.80, 0.36)):
        cx, cy = x + int(w * fx), y + int(h * fy)
        for a in range(8):
            ang = 2 * math.pi * a / 8
            r = int(h * 0.13)
            d.line([cx, cy, cx + r * math.cos(ang), cy + r * 0.8 * math.sin(ang)], fill=(255, 190, 90), width=1)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 140))

def sc_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(86, 128, 156))
    gx, gy, gr = x + int(w * 0.30), y + int(h * 0.48), int(h * 0.34)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 90))
    d.ellipse([gx - gr * 0.55, gy - gr * 0.5, gx - gr * 0.05, gy - gr * 0.05], fill=(120, 160, 90))
    d.ellipse([gx + gr * 0.1, gy + gr * 0.05, gx + gr * 0.6, gy + gr * 0.55], fill=(120, 160, 90))
    tx = x + int(w * 0.68); tw_ = max(5, int(w * 0.05))
    d.rectangle([tx, y + int(h * 0.14), tx + tw_, y + int(h * 0.66)], outline=(240, 240, 240), width=2)
    d.rectangle([tx + 1, y + int(h * 0.40), tx + tw_ - 1, y + int(h * 0.66)], fill=(220, 70, 50))
    d.ellipse([tx - 3, y + int(h * 0.62), tx + tw_ + 3, y + int(h * 0.62) + tw_ + 6], fill=(220, 70, 50))

def sc_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 210))
    for i in range(1, 4):
        gy = y + int(h * i / 4)
        d.line([x + 3, gy, x + w - 3, gy], fill=(210, 200, 175), width=1)
    pts = [(0.04, 0.50), (0.18, 0.50), (0.28, 0.18), (0.38, 0.82), (0.48, 0.30), (0.58, 0.70), (0.68, 0.50), (0.96, 0.50)]
    xy = [(x + int(w * fx), y + int(h * fy)) for fx, fy in pts]
    d.line(xy, fill=(176, 58, 46), width=2)
    d.line([x + int(w * 0.28), y, x + int(w * 0.28), y + h], fill=(176, 58, 46), width=1)

def sc_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(92, 142, 82))
    d.rectangle([x + int(w * 0.28), y, x + int(w * 0.72), y + h], fill=(198, 172, 112))
    sx = x + int(w * 0.60)
    for i in range(3):
        d.line([sx + i * 4 - 4, y + int(h * 0.30), sx + i * 4 - 4, y + int(h * 0.72)], fill=(240, 230, 190), width=2)
    d.polygon([(x + int(w * 0.10), y + int(h * 0.78)), (x + int(w * 0.20), y + int(h * 0.74)), (x + int(w * 0.34), y + int(h * 0.30)), (x + int(w * 0.28), y + int(h * 0.26))], fill=(214, 178, 120))
    bx, by = x + int(w * 0.82), y + int(h * 0.34)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(196, 40, 44))

def sc_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 34))
    d.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(40, 44, 56))
    for i in range(5):  # light gantry dots
        lx = x + int(w * (0.15 + 0.18 * i))
        d.ellipse([lx - 3, y + int(h * 0.16) - 3, lx + 3, y + int(h * 0.16) + 3], fill=(250, 60, 60) if i < 4 else (250, 220, 90))
    cx, cy = x + int(w * 0.50), y + int(h * 0.62)
    d.rectangle([cx - int(w * 0.30), cy - int(h * 0.10), cx + int(w * 0.30), cy + int(h * 0.08)], fill=(196, 40, 44))
    d.rectangle([cx - int(w * 0.10), cy - int(h * 0.26), cx + int(w * 0.12), cy - int(h * 0.08)], fill=(120, 20, 30))
    for wx in (cx - int(w * 0.22), cx + int(w * 0.22)):
        d.ellipse([wx - 5, cy + int(h * 0.02), wx + 5, cy + int(h * 0.14)], fill=(10, 10, 12))

def sc_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 14, 30))
    rng = random.Random(22)
    for _ in range(30):
        sx, sy = x + rng.randint(2, max(2, int(w) - 3)), y + rng.randint(2, max(2, int(h) - 3))
        d.ellipse([sx, sy, sx + 1.4, sy + 1.4], fill=(230, 234, 244))
    cx = x + w // 2
    d.rectangle([cx - 6, y + int(h * 0.18), cx + 6, y + int(h * 0.62)], fill=(226, 228, 232))
    d.polygon([(cx - 6, y + int(h * 0.18)), (cx + 6, y + int(h * 0.18)), (cx, y + int(h * 0.04))], fill=(196, 40, 44))
    d.polygon([(cx - 6, y + int(h * 0.55)), (cx - 14, y + int(h * 0.68)), (cx - 6, y + int(h * 0.68))], fill=(52, 84, 168))
    d.polygon([(cx + 6, y + int(h * 0.55)), (cx + 14, y + int(h * 0.68)), (cx + 6, y + int(h * 0.68))], fill=(52, 84, 168))
    d.polygon([(cx - 4, y + int(h * 0.68)), (cx + 4, y + int(h * 0.68)), (cx + 8, y + h - 2), (cx - 8, y + h - 2)], fill=(255, 170, 60))

def sc_football(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 120, 60))
    for i in range(4):
        d.line([x, y + int(h * (0.2 + 0.2 * i)), x + w, y + int(h * (0.2 + 0.2 * i))], fill=(70, 150, 84), width=2)
    d.ellipse([x + int(w * 0.30), y + int(h * 0.25), x + int(w * 0.70), y + int(h * 0.75)], outline=(240, 240, 240), width=2)
    bx, by = x + int(w * 0.50), y + int(h * 0.50)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(250, 250, 250), outline=(30, 30, 30))

def sc_tennis(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 90, 160))
    d.rectangle([x + int(w * 0.12), y + int(h * 0.12), x + int(w * 0.88), y + int(h * 0.88)], outline=(240, 240, 240), width=2)
    d.line([x + int(w * 0.12), y + h // 2, x + int(w * 0.88), y + h // 2], fill=(240, 240, 240), width=1)
    bx, by = x + int(w * 0.72), y + int(h * 0.30)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(200, 230, 60))

def sc_golf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 180, 110))
    d.ellipse([x + int(w * 0.55), y + int(h * 0.45), x + int(w * 0.95), y + int(h * 0.85)], fill=(90, 160, 90))
    fx = x + int(w * 0.75)
    d.line([fx, y + int(h * 0.20), fx, y + int(h * 0.62)], fill=(240, 240, 240), width=2)
    d.polygon([(fx, y + int(h * 0.20)), (fx + int(w * 0.16), y + int(h * 0.28)), (fx, y + int(h * 0.36))], fill=(196, 40, 44))
    d.ellipse([x + int(w * 0.20) - 3, y + int(h * 0.70) - 3, x + int(w * 0.20) + 3, y + int(h * 0.70) + 3], fill=(250, 250, 250))

def sc_sumo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 164, 108))
    cx, cy = x + w // 2, y + int(h * 0.55)
    d.ellipse([cx - int(w * 0.34), cy - int(h * 0.28), cx + int(w * 0.34), cy + int(h * 0.28)], fill=(140, 110, 60))
    d.ellipse([cx - int(w * 0.28), cy - int(h * 0.20), cx + int(w * 0.28), cy + int(h * 0.20)], fill=(168, 134, 76))
    d.ellipse([cx - int(w * 0.16), cy - int(h * 0.30), cx - int(w * 0.06), cy - int(h * 0.20)], fill=(60, 40, 30))
    d.ellipse([cx + int(w * 0.06), cy - int(h * 0.30), cx + int(w * 0.16), cy - int(h * 0.20)], fill=(60, 40, 30))

def sc_golf2(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(90, 130, 120))
    d.rectangle([x, y + int(h * 0.60), x + w, y + h], fill=(70, 110, 90))
    for i in range(3):  # rain streaks
        rx = x + int(w * (0.2 + 0.3 * i))
        d.line([rx, y + int(h * 0.15), rx - 4, y + int(h * 0.35)], fill=(200, 220, 235), width=1)
    fx = x + int(w * 0.60)
    d.line([fx, y + int(h * 0.30), fx, y + int(h * 0.70)], fill=(240, 240, 240), width=2)
    d.polygon([(fx, y + int(h * 0.30)), (fx + int(w * 0.14), y + int(h * 0.38)), (fx, y + int(h * 0.46))], fill=(240, 200, 40))

def sc_nfl(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 110, 60))
    for i in range(5):
        lx = x + int(w * (0.15 + 0.18 * i))
        d.line([lx, y + 4, lx, y + h - 4], fill=(240, 240, 240), width=1)
    cx, cy = x + int(w * 0.50), y + int(h * 0.50)
    d.ellipse([cx - int(w * 0.14), cy - int(h * 0.14), cx + int(w * 0.14), cy + int(h * 0.14)], fill=(120, 70, 40), outline=(250, 250, 250))
    d.line([cx - int(w * 0.08), cy, cx + int(w * 0.08), cy], fill=(250, 250, 250), width=1)

SCENES = {"gulf": sc_gulf, "intercept": sc_intercept, "cop": sc_cop,
          "quake": sc_quake, "cricket": sc_cricket, "f1": sc_f1,
          "rocket": sc_rocket, "football": sc_football, "tennis": sc_tennis,
          "golf": sc_golf, "sumo": sc_sumo, "golf2": sc_golf2, "nfl": sc_nfl}

MODES = {
    "A": dict(name="A - 2D FLAT", shadow=0, lead_ids=[1, 3, 5],
              hook="GULF HIT OVERNIGHT  -  COP31 FINAL TEXT IN ANTALYA  -  INDIA 720/9, A RECORD",
              lead_strip=48, small_strip=30),
    "B": dict(name="B - 3D LAYERED", shadow=5, lead_ids=[1, 3, 5],
              hook="GULF HIT OVERNIGHT  -  COP31 FINAL TEXT IN ANTALYA  -  INDIA 720/9, A RECORD",
              lead_strip=52, small_strip=32),
    "C": dict(name="C - 2D COMPACT GRID", shadow=0, lead_ids=[],
              hook="INDIA 720/9, A RECORD  -  GULF HIT OVERNIGHT  -  COP31 FINAL TEXT IN ANTALYA",
              lead_strip=36, small_strip=36),
}

# ---- card / page rendering ----
def draw_strip(d, card, x, y, w, h, mode, lead=False):
    if mode["shadow"]:
        d.rectangle([x + 3, y + 3, x + w + 3, y + h + 3], fill=(200, 190, 160))
        d.rectangle([x, y, x + w, y + 2], fill=(255, 255, 255))
    SCENES[card["scene"]](d, x, y, w, h)
    rc = REGIONS[card["region"]]
    d.rectangle([x, y, x + w, y + 3], fill=rc)
    band_h = 16 if lead else 12
    d.rectangle([x, y + h - band_h, x + w, y + h], fill=INK)
    cf = fit(d, card["caption"], 10 if lead else 9, w - 10)
    ctext(d, x + w / 2, y + h - band_h + (1 if lead else 0), card["caption"], cf, PARCH)
    if lead:
        tag_f = AB(10)
        tag_w = tw(d, card["tag"], tag_f) + 8
        ty = y + 5
        d.rectangle([x + w - tag_w - 3, ty, x + w - 3, ty + 14], fill=INK)
        d.text((x + w - tag_w + 1, ty + 1), card["tag"], font=tag_f, fill=PARCH)
    if lead:
        lab_f = fit(d, card["label"], 12, w - 12)
        lab_w = tw(d, card["label"], lab_f) + 9
        lab_h = 16
        ly = y + h - band_h - lab_h - 2
        d.rectangle([x + 3, ly, x + 3 + lab_w, ly + lab_h], fill=BURG)
        d.text((x + 7, ly + 2), card["label"], font=lab_f, fill=(255, 255, 255))
    else:
        # small strip (30px): short source tag top-right, label chip top-left,
        # label width budgeted so the two can never overlap.
        tag_f = AB(9)
        tag_w = tw(d, card.get("stag", card["tag"]), tag_f) + 8
        d.rectangle([x + w - tag_w - 3, y + 2, x + w - 3, y + 15], fill=INK)
        d.text((x + w - tag_w + 1, y + 3), card.get("stag", card["tag"]), font=tag_f, fill=PARCH)
        lab_f = fit(d, card["label"], 10, w - tag_w - 20)
        lab_w = tw(d, card["label"], lab_f) + 9
        ly = y + 2
        d.rectangle([x + 3, ly, x + 3 + lab_w, ly + 13], fill=BURG)
        d.text((x + 7, ly + 2), card["label"], font=lab_f, fill=(255, 255, 255))

def draw_card(d, card, x, y, w, strip_h, mode, lead=False):
    if mode["shadow"]:
        d.rectangle([x + mode["shadow"], y + mode["shadow"], x + w + mode["shadow"], y + strip_h + 62 + mode["shadow"]], fill=SHADOW)
    d.rectangle([x, y, x + w, y + strip_h], outline=CARDB, width=1)
    draw_strip(d, card, x, y, w, strip_h, mode, lead)
    rc = REGIONS[card["region"]]
    ry = y + strip_h + (5 if lead else 3)
    d.text((x + 1, ry), "%d  %s - %s - %s" % (card["no"], card["place"], card["region"], card["topic"]),
           font=AB(11 if lead else 9), fill=rc)
    hy = ry + (15 if lead else 12)
    hf = PF(22 if lead else 14)
    for ln in wrap(d, card["headline"], hf, w - 2)[:2]:
        d.text((x + 1, hy), ln, font=hf, fill=INK)
        hy += 24 if lead else 15
    for ln in wrap(d, card["deck"], AM(12), w - 2):
        d.text((x + 1, hy + 1), ln, font=AM(12), fill=(64, 74, 62))
        hy += 13 if lead else 12.5
    return hy

def draw_top(d, mode):
    d.rectangle([0, 0, W, 24], fill=FOREST)
    d.text((M, 5), "THE WORLD IN ONE DAY  ·  GAZETTEER EDITION", font=AB(12), fill=PARCH)
    right = "40 STORIES - 7 REGIONS - EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - M - tw(d, right, AB(11)), 6), right, font=AB(11), fill=PARCH)
    if mode["shadow"]:
        d.text((M + 2, 31), "The Daily Atlas", font=PF(44), fill=(200, 190, 160))
    d.text((M, 29), "The Daily Atlas", font=PF(44), fill=INK)
    date1 = "SUNDAY 22 NOVEMBER 2026"
    d.text((W - M - tw(d, date1, AB(14)), 34), date1, font=AB(14), fill=FOREST)
    date2 = "Atlas edition - one page, the whole day"
    d.text((W - M - tw(d, date2, AM(11)), 54), date2, font=AM(11), fill=(84, 92, 76))
    d.line([M, 78, W - M, 78], fill=BURG, width=3)
    d.rectangle([M, 84, W - M, 108], fill=BURG)
    ctext(d, W / 2, 90, mode["hook"], fit(d, mode["hook"], 13, CW - 24), (255, 255, 255))
    cw6 = CW / 6
    for i, (lab, ev) in enumerate(TIMELINE):
        cx = M + i * cw6
        if i:
            d.line([cx, 114, cx, 144], fill=RULE, width=1)
        d.text((cx + 8, 109), lab, font=AB(10), fill=FOREST)
        ey = 120
        for ln in wrap(d, ev, AM(10), cw6 - 14)[:2]:
            d.text((cx + 8, ey), ln, font=AM(10), fill=INK)
            ey += 11
    d.line([M, 144, W - M, 144], fill=RULE, width=1)
    d.text((M, 148), "THE DAY IN NUMBERS", font=AB(10), fill=FOREST)
    cw6n = CW / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cw6n
        ctext(d, cx + cw6n / 2, 160, num, PF(25), BURG)
        cy = 189
        for ln in wrap(d, cap, AM(10), cw6n - 8)[:2]:
            ctext(d, cx + cw6n / 2, cy, ln, AM(10), (84, 92, 76))
            cy += 11
    cw7 = (CW - 6 * 6) / 7
    for i, (name, n) in enumerate(REGION_COUNTS):
        cx = M + i * (cw7 + 6)
        d.rectangle([cx, 203, cx + cw7, 221], fill=REGIONS[name])
        ctext(d, cx + cw7 / 2, 207, "%s %d" % (name, n), AB(10), (255, 255, 255))
    d.line([M, 226, W - M, 226], fill=RULE, width=1)

def draw_cards(d, mode):
    by_no = {c["no"]: c for c in CARDS}
    if mode["lead_ids"]:
        lead_w = (CW - 2 * 12) / 3
        end = 0
        for i, no in enumerate(mode["lead_ids"]):
            end = max(end, draw_card(d, by_no[no], M + i * (lead_w + 12), 230, lead_w, mode["lead_strip"], mode, lead=True))
        fy = end + 6
        rest = [c for c in CARDS if c["no"] not in mode["lead_ids"]]
        feat_w = (CW - 4 * 10) / 5
        for r in range(2):
            end = 0
            for c in range(5):
                end = max(end, draw_card(d, rest[r * 5 + c], M + c * (feat_w + 10), fy, feat_w, mode["small_strip"], mode))
            fy = end + 6
        return fy
    # compact grid: 5 + 5 + 3, all equal
    feat_w = (CW - 4 * 10) / 5
    fy = 230
    for r in range(3):
        row = CARDS[r * 5:(r + 1) * 5]
        end = 0
        for c, card in enumerate(row):
            end = max(end, draw_card(d, card, M + c * (feat_w + 10), fy, feat_w, mode["small_strip"], mode))
        fy = end + 6
    return fy

def draw_map(d, top, bottom=960):
    x0, x1 = M, M + 430
    d.rectangle([x0, top, x1, bottom], fill=MAPBG)
    d.text((x0 + 12, top + 7), "WHERE IT HAPPENED", font=AB(12), fill=PARCH)
    mx0, mx1, my0, my1 = x0 + 10, x1 - 10, top + 28, bottom - 30
    def px(lon): return mx0 + (lon + 180) / 360 * (mx1 - mx0)
    def py(lat): return my0 + (82 - lat) / 140 * (my1 - my0)
    for glon in range(-150, 181, 30):
        d.line([px(glon), my0, px(glon), my1], fill=(36, 74, 52), width=1)
    for glat in range(-45, 76, 15):
        d.line([mx0, py(glat), mx1, py(glat)], fill=(36, 74, 52), width=1)
    for rings in WORLD.values():
        for ring in rings.split("|"):
            pts = []
            for pair in ring.split(","):
                lo, la = pair.split(":")
                pts.append((px(float(lo)), py(float(la))))
            if len(pts) >= 3:
                d.polygon(pts, fill=LAND)
    for no, _t, region, lon, lat in BRIEFS:
        if lon is not None:
            cx, cy = px(lon), py(lat)
            d.ellipse([cx - 2.6, cy - 2.6, cx + 2.6, cy + 2.6], fill=REGIONS[region])
    for card in CARDS:
        if card["lon"] is None:
            continue
        cx, cy = px(card["lon"]), py(card["lat"])
        r = 9
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=REGIONS[card["region"]], outline=PARCH, width=2)
        s = str(card["no"])
        f = AB(10)
        d.text((cx - tw(d, s, f) / 2, cy - 5), s, font=f, fill=(255, 255, 255))
    d.text((x0 + 12, bottom - 18), "Pins 1-13 = pictured stories - dots = briefs",
           font=AM(9), fill=PARCH)

def draw_briefs(d, top):
    x = M + 430 + 16
    w = W - M - x
    d.text((x, top + 5), "ALSO ON SUNDAY 22 NOVEMBER - 27 MORE STORIES", font=AB(12), fill=FOREST)
    d.line([x, top + 21, W - M, top + 21], fill=FOREST, width=1)
    y0 = top + 26
    lh = (960 - y0) / len(BRIEFS)
    y = y0
    for no, text, region, _lon, _lat in BRIEFS:
        ns = str(no)
        d.text((x, y), ns, font=AB(9), fill=REGIONS[region])
        off = tw(d, ns, AB(9)) + 5
        ln = wrap(d, text, AM(9), w - off)[0]  # one line only: no wrap-overlap
        d.text((x + off, y), ln, font=AM(9), fill=(52, 62, 54))
        y += lh
    return lh

def draw_bottom_bands(d):
    y0, y1 = 966, 1004
    d.rectangle([M, y0, W - M, y1], fill=PAPER, outline=BURG, width=2)
    lab = "DATE CHECK"
    d.text((M + 8, y0 + 5), lab, font=AB(10), fill=BURG)
    tx = M + 8 + tw(d, lab, AB(10)) + 8
    words = DATE_CHECK.split()
    first, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, AM(9)) <= (W - M - 8) - tx:
            cur = t
        else:
            break
    first = cur
    remainder = DATE_CHECK[len(first):].strip()
    d.text((tx, y0 + 5), first, font=AM(9), fill=INK)
    yy = y0 + 16
    for ln in wrap(d, remainder, AM(9), CW - 16)[:2]:
        d.text((M + 8, yy), ln, font=AM(9), fill=INK)
        yy += 11
    d.text((M, 1010), FOOTER_L, font=AM(9), fill=(84, 92, 76))
    d.text((W - M - tw(d, FOOTER_R, AM(9)), 1010), FOOTER_R, font=AM(9), fill=(84, 92, 76))

def build(mode_key, out_path):
    mode = MODES[mode_key]
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_top(d, mode)
    bottom_top = draw_cards(d, mode)
    lh = draw_briefs(d, bottom_top)
    draw_map(d, bottom_top)
    draw_bottom_bands(d)
    q = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(out_path, optimize=True)
    print(mode["name"], "bottom_top:", bottom_top, "brief leading: %.2f" % lh)
    print("saved", out_path, os.path.getsize(out_path), "bytes")
    return bottom_top


if __name__ == "__main__":
    build("A", os.path.join(HERE, "entry.png"))
