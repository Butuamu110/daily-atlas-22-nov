#!/usr/bin/env python3
"""THE DAILY ATLAS — one page that holds a whole day of world news.

Edition: Sunday 22 November 2026, made for the MakeFun
news-image-20261122 bounty by @rojanon11 (GitHub @Butuamu110).

How the page is put together:
  * a green gazetteer bar and a burgundy hook band across the top,
  * a six-slot UTC timeline and a "day in numbers" row under it,
  * thirteen pictured story cards (three wide leads, then two rows
    of five), each with its own little flat illustration,
  * a real-polygon world map with numbered pins for the cards and
    dots for the briefs, beside a column of 27 one-line briefs,
  * a DATE CHECK band near the foot naming the older and
    not-yet-happened items that were deliberately kept off the page.

Every fact on the page comes from POOL22-BARU v3 — thirteen events
verified for 22 November 2026, nothing from the retired pool. COP31
sits in Antalya, Türkiye. Contested claims stay attributed to the
outlet that made them. Rendering is pure PIL, fully deterministic,
and needs no network: run `python3 draw.py` to rebuild entry.png.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from mapdata import WORLD  # noqa: E402  (real country polygons)

# ---------------------------------------------------------------- page frame
SIDE = 1024               # the page is square
EDGE = 24                 # outer margin on every side
SPAN = SIDE - 2 * EDGE    # usable width inside the margins

# ------------------------------------------------------------------- palette
CREAM = (243, 234, 211)   # page background
SHEET = (250, 246, 233)   # pale panel fill
BODY = (38, 51, 42)       # main ink
PINE = (31, 81, 48)       # gazetteer green
WINE = (123, 45, 38)      # hook-band burgundy
LINERULE = (178, 164, 128)
CARD_EDGE = (196, 184, 152)
DEEP_SEA = (24, 54, 38)   # map water
LANDMASS = (168, 191, 165)
FADED = (84, 92, 76)      # muted caption ink
DECK_INK = (64, 74, 62)
DROP = (120, 108, 80)     # drop-shadow tone (layered layout only)
BRIEF_INK = (52, 62, 54)

REGION_TINT = {
    "EUROPE": (176, 58, 46),
    "ASIA": (29, 111, 184),
    "MIDEAST": (125, 60, 152),
    "AFRICA": (30, 132, 73),
    "AMERICAS": (202, 111, 30),
    "OCEANIA": (20, 143, 119),
    "GLOBAL": (93, 109, 126),
}

# --------------------------------------------------------------------- fonts
_font_memo = {}


def _load_font(filename, size):
    return ImageFont.truetype(os.path.join(BASE, "fonts", filename), size)


def display(size):
    """Playfair Display 900 — masthead and headlines."""
    key = ("display", size)
    if key not in _font_memo:
        _font_memo[key] = _load_font("PlayfairDisplay-900.ttf", size)
    return _font_memo[key]


def bold(size):
    """Archivo Bold — labels, chips, kickers."""
    key = ("bold", size)
    if key not in _font_memo:
        _font_memo[key] = _load_font("Archivo-Bold.ttf", size)
    return _font_memo[key]


def plain(size):
    """Archivo Medium — decks, briefs, captions."""
    key = ("plain", size)
    if key not in _font_memo:
        _font_memo[key] = _load_font("Archivo-Medium.ttf", size)
    return _font_memo[key]


# --------------------------------------------------------------- text helpers
def text_w(draw, s, font):
    return draw.textlength(s, font=font)


def wrap_lines(draw, s, font, maxw):
    """Greedy word wrap: keep adding words while the line still fits."""
    done, current = [], ""
    for word in s.split():
        trial = (current + " " + word).strip()
        if text_w(draw, trial, font) <= maxw or not current:
            current = trial
        else:
            done.append(current)
            current = word
    if current:
        done.append(current)
    return done


def shrink_to_fit(draw, s, start, maxw, floor=8):
    """Largest Archivo Bold size, from `start` down, that fits `maxw`."""
    size = start
    while size > floor and text_w(draw, s, bold(size)) > maxw:
        size -= 1
    return bold(size)


def centred(draw, cx, y, s, font, fill):
    draw.text((cx - text_w(draw, s, font) / 2, y), s, font=font, fill=fill)


# ------------------------------------------------------------- the day's data
# The six figures in the numbers row; every one is bound to a card below.
DAY_FIGURES = [
    ("2", "Patriot radars IRGC CLAIMS hit"),
    ("720/9", "India declared in Wellington"),
    ("50", "laps, Las Vegas Grand Prix"),
    ("$4M", "LPGA CME winner's prize"),
    ("12-2", "Kyushu Basho leaders"),
    ("06:00", "COP31 approval plenary, Antalya"),
]

# Six moments of the day, WIB, in the order they happened.
DAY_CLOCK = [
    ("02:40 WIB", "IRGC first Gulf statement"),
    ("03:43 WIB", "Mecca sirens sound"),
    ("04:05 WIB", "Myanmar M4.1 quake"),
    ("05:42 WIB", "Mecca interception confirmed"),
    ("11:00 WIB", "Las Vegas GP lights out"),
    ("19:16 WIB", "Falcon 9 NROL-136 lifts off"),
]

# Story tally per region, counted from the cards and briefs: 4+5+7+0+15+5+4.
REGION_TALLY = [
    ("EUROPE", 4), ("ASIA", 5), ("MIDEAST", 7), ("AFRICA", 0),
    ("AMERICAS", 15), ("OCEANIA", 5), ("GLOBAL", 4),
]

# The thirteen pictured stories, one row per verified event:
# (number, dateline, region, topic, headline, deck, full tag, short tag,
#  label chip, strip caption, longitude, latitude, scene key)
STORY_ROWS = [
    (1, "THE GULF", "MIDEAST", "WAR",
     "Gulf hit overnight: radars, fire, drones",
     "IRGC claims missiles and drones hit 2 US Patriot radars in Bahrain; a civilian plant burns. A drone is downed at Ali Al Salem, Kuwait. (IRGC / Bahrain)",
     "CLAIM - IRGC", "IRGC", "2 RADARS CLAIMED",
     "THE GULF - OVERNIGHT STRIKES", 50.5, 26.0, "gulf"),
    (2, "MAKKAH REGION", "MIDEAST", "DEFENCE",
     "Houthi missile to Makkah is intercepted",
     "Civil-defence sirens sound at 23:43 Riyadh time; the Saudi-led coalition confirms the interception at 01:42. No damage reported. (Anadolu)",
     "CONFIRMED - ANADOLU", "ANADOLU", "INTERCEPTED 01:42",
     "MAKKAH - MISSILE DOWNED", 39.8, 21.4, "intercept"),
    (3, "ANTALYA", "GLOBAL", "CLIMATE",
     "COP31 final text tabled in Antalya",
     "President Murat Kurum tables the final package; objections close 03:00 GMT and the approval plenary is set for 06:00 GMT Sunday. (Reuters)",
     "REUTERS", "REUTERS", "FINAL TEXT 06:00 GMT",
     "ANTALYA - FINAL TEXT TABLED", 30.7, 36.9, "cop"),
    (4, "MYANMAR", "ASIA", "QUAKE",
     "M4.1 quake strikes Myanmar at 04:05 WIB",
     "NCS records a magnitude 4.1 quake at 02:35:57 IST, 95 km deep, epicentre 24.404N 94.616E. (NCS / ANI)",
     "NCS - ANI", "NCS", "M4.1 - 95 KM DEEP",
     "MYANMAR - M4.1 QUAKE", 94.6, 24.4, "quake"),
    (5, "WELLINGTON", "OCEANIA", "CRICKET",
     "India declare 720/9 - a record in New Zealand",
     "India declare 720/9 on day four: Rahul 136, Pant 128. New Zealand made 368 (Nicholls 175, Bumrah 4-92); India lead by 352. (IANS / AFP)",
     "IANS - AFP", "IANS", "720/9 DECLARED",
     "WELLINGTON - RECORD 720/9", 174.8, -41.3, "cricket"),
    (6, "LAS VEGAS", "AMERICAS", "MOTORSPORT",
     "Las Vegas Grand Prix races under the lights",
     "Lights out 04:00 UTC (11:00 WIB) for 50 laps of the Strip Circuit, round 22. (formula1.com)",
     "FORMULA1.COM", "F1.COM", "50 LAPS - ROUND 22",
     "LAS VEGAS - GP UNDER LIGHTS", -115.2, 36.1, "f1"),
    (7, "VANDENBERG", "AMERICAS", "SPACE",
     "Falcon 9 launches NROL-136 at 19:16 WIB",
     "SpaceX launches the 15th NRO constellation batch from SLC-4E; booster B1097 returns to LZ-4. (VSFB)",
     "VSFB - SPACEX", "VSFB", "B1097 RETURNS TO LZ-4",
     "VANDENBERG - NROL-136 UP", -120.5, 34.7, "rocket"),
    (8, "ANFIELD", "EUROPE", "FOOTBALL",
     "Liverpool host Manchester United at 23:30 WIB",
     "The derby closes Premier League Matchweek 11 at Anfield, 16:30 UTC. Hull host Brighton at 21:00 WIB. (PL)",
     "PREMIER LEAGUE", "PL", "16:30 UTC - ANFIELD",
     "ANFIELD - DERBY NIGHT", -2.96, 53.43, "football"),
    (9, "TURIN", "EUROPE", "TENNIS",
     "Alcaraz v Zverev for the Turin title",
     "The ATP Finals title match is played Sunday night in Turin (about 16:00 UTC). Alcaraz rallied past Shelton. (ATP)",
     "ATP - REUTERS", "ATP", "FINAL - TURIN",
     "TURIN - ATP FINALS", 7.7, 45.1, "tennis"),
    (10, "NAPLES, FLORIDA", "AMERICAS", "GOLF",
     "A Lim Kim leads the LPGA finale at -18",
     "The CME finale is played Sunday at Tiburon; Kim leads by one from Thitikul and Yoshida. Winner takes $4m. (LPGA)",
     "LPGA.COM", "LPGA", "-18 LEADS BY ONE",
     "NAPLES - LPGA FINALE", -81.8, 26.1, "golf"),
    (11, "FUKUOKA", "ASIA", "SUMO",
     "Kyushu Basho ends: two men tied at 12-2",
     "Senshuraku at Fukuoka: Onosato and Wakamotoharu are 12-2, Atamifuji 11-3. Onosato faces Hoshoryu. (JSA)",
     "JSA", "JSA", "12-2 - TITLE DECIDER",
     "FUKUOKA - SENSHURAKU", 130.4, 33.6, "sumo"),
    (12, "GEORGIA", "AMERICAS", "GOLF",
     "RSM Classic round three moves to Sunday",
     "Saturday washed out, so round three is played Sunday at Sea Island; three share the lead at -9. Final Monday. (PGA)",
     "PGA TOUR - REUTERS", "PGA", "THREE TIED AT -9",
     "SEA ISLAND - RSM R3 SUNDAY", -81.3, 31.2, "golf2"),
    (13, "UNITED STATES", "AMERICAS", "NFL",
     "NFL Week 12: eleven games on Sunday",
     "The early window opens 18:00 UTC (Monday 01:00 WIB); Vikings visit the 49ers at night. (ESPN / NFL)",
     "ESPN - NFL", "ESPN", "11 GAMES SUNDAY",
     "USA - NFL WEEK 12", -98.0, 39.0, "nfl"),
]

_STORY_KEYS = ("no", "place", "region", "topic", "headline", "deck",
               "tag", "stag", "label", "caption", "lon", "lat", "scene")
STORIES = [dict(zip(_STORY_KEYS, row)) for row in STORY_ROWS]

# Briefs 14-40: sub-facts of the same thirteen events, all dated 22 Nov.
# (number, one-line text, region, longitude, latitude)
BRIEF_ROWS = [
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
FOOT_LEFT = "Every story here happened, or was first reported, on Sunday 22 November 2026. Contested claims are attributed."
FOOT_RIGHT = "Sources named beside each story - original drawings"


# ------------------------------------------------------- story illustrations
# One small flat scene per card. Each painter receives the strip's
# draw handle and its box (x, y, w, h) and fills exactly that box.
PAINTERS = {}


def painter(key):
    def register(fn):
        PAINTERS[key] = fn
        return fn
    return register


def _skyline(d, x, y, w, h, sky, tower, heights):
    """A row of dark towers against a flat sky — shared night backdrop."""
    d.rectangle([x, y, x + w, y + h], fill=sky)
    for i, frac in enumerate(heights):
        bx = x + int(w * (0.02 + 0.14 * i))
        bw = int(w * 0.12)
        d.rectangle([bx, y + h - int(h * frac), bx + bw, y + h], fill=tower)


def _burst(d, cx, cy, radii, squash, color, width):
    """Radial flash: one line per radius, angles spread over the circle,
    vertical reach squashed by `squash` so the burst sits flat."""
    count = len(radii)
    for k, r in enumerate(radii):
        a = 2 * math.pi * k / count
        d.line([cx, cy, cx + r * math.cos(a), cy + r * squash * math.sin(a)],
               fill=color, width=width)


@painter("gulf")
def paint_gulf(d, x, y, w, h):
    _skyline(d, x, y, w, h, (52, 54, 74), (26, 27, 38),
             (0.34, 0.48, 0.28, 0.42, 0.32, 0.52, 0.30))
    cx, cy = x + int(w * 0.60), y + int(h * 0.34)
    radii = [int(h * (0.30 if k % 2 == 0 else 0.16)) for k in range(12)]
    _burst(d, cx, cy, radii, 0.72, (255, 170, 60), 2)
    d.ellipse([cx - int(h * 0.13), cy - int(h * 0.10), cx + int(h * 0.13), cy + int(h * 0.10)], fill=(255, 196, 84))


@painter("intercept")
def paint_intercept(d, x, y, w, h):
    _skyline(d, x, y, w, h, (26, 30, 52), (12, 14, 26),
             (0.30, 0.44, 0.26, 0.38, 0.30, 0.48, 0.28))
    for fx, fy in ((0.30, 0.30), (0.58, 0.22), (0.80, 0.36)):
        cx, cy = x + int(w * fx), y + int(h * fy)
        _burst(d, cx, cy, [int(h * 0.13)] * 8, 0.8, (255, 190, 90), 1)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 140))


@painter("cop")
def paint_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(86, 128, 156))
    gx, gy, gr = x + int(w * 0.30), y + int(h * 0.48), int(h * 0.34)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 90))
    d.ellipse([gx - gr * 0.55, gy - gr * 0.5, gx - gr * 0.05, gy - gr * 0.05], fill=(120, 160, 90))
    d.ellipse([gx + gr * 0.1, gy + gr * 0.05, gx + gr * 0.6, gy + gr * 0.55], fill=(120, 160, 90))
    tx = x + int(w * 0.68)
    thermo_w = max(5, int(w * 0.05))
    d.rectangle([tx, y + int(h * 0.14), tx + thermo_w, y + int(h * 0.66)], outline=(240, 240, 240), width=2)
    d.rectangle([tx + 1, y + int(h * 0.40), tx + thermo_w - 1, y + int(h * 0.66)], fill=(220, 70, 50))
    d.ellipse([tx - 3, y + int(h * 0.62), tx + thermo_w + 3, y + int(h * 0.62) + thermo_w + 6], fill=(220, 70, 50))


@painter("quake")
def paint_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 210))
    for i in range(1, 4):
        gy = y + int(h * i / 4)
        d.line([x + 3, gy, x + w - 3, gy], fill=(210, 200, 175), width=1)
    pts = [(0.04, 0.50), (0.18, 0.50), (0.28, 0.18), (0.38, 0.82), (0.48, 0.30), (0.58, 0.70), (0.68, 0.50), (0.96, 0.50)]
    xy = [(x + int(w * fx), y + int(h * fy)) for fx, fy in pts]
    d.line(xy, fill=(176, 58, 46), width=2)
    d.line([x + int(w * 0.28), y, x + int(w * 0.28), y + h], fill=(176, 58, 46), width=1)


@painter("cricket")
def paint_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(92, 142, 82))
    d.rectangle([x + int(w * 0.28), y, x + int(w * 0.72), y + h], fill=(198, 172, 112))
    sx = x + int(w * 0.60)
    for i in range(3):
        d.line([sx + i * 4 - 4, y + int(h * 0.30), sx + i * 4 - 4, y + int(h * 0.72)], fill=(240, 230, 190), width=2)
    d.polygon([(x + int(w * 0.10), y + int(h * 0.78)), (x + int(w * 0.20), y + int(h * 0.74)), (x + int(w * 0.34), y + int(h * 0.30)), (x + int(w * 0.28), y + int(h * 0.26))], fill=(214, 178, 120))
    bx, by = x + int(w * 0.82), y + int(h * 0.34)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(196, 40, 44))


@painter("f1")
def paint_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 34))
    d.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(40, 44, 56))
    for i in range(5):  # start-gantry lights
        lx = x + int(w * (0.15 + 0.18 * i))
        d.ellipse([lx - 3, y + int(h * 0.16) - 3, lx + 3, y + int(h * 0.16) + 3], fill=(250, 60, 60) if i < 4 else (250, 220, 90))
    cx, cy = x + int(w * 0.50), y + int(h * 0.62)
    d.rectangle([cx - int(w * 0.30), cy - int(h * 0.10), cx + int(w * 0.30), cy + int(h * 0.08)], fill=(196, 40, 44))
    d.rectangle([cx - int(w * 0.10), cy - int(h * 0.26), cx + int(w * 0.12), cy - int(h * 0.08)], fill=(120, 20, 30))
    for wx in (cx - int(w * 0.22), cx + int(w * 0.22)):
        d.ellipse([wx - 5, cy + int(h * 0.02), wx + 5, cy + int(h * 0.14)], fill=(10, 10, 12))


@painter("rocket")
def paint_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 14, 30))
    stars = random.Random(22)
    for _ in range(30):
        sx = x + stars.randint(2, max(2, int(w) - 3))
        sy = y + stars.randint(2, max(2, int(h) - 3))
        d.ellipse([sx, sy, sx + 1.4, sy + 1.4], fill=(230, 234, 244))
    cx = x + w // 2
    d.rectangle([cx - 6, y + int(h * 0.18), cx + 6, y + int(h * 0.62)], fill=(226, 228, 232))
    d.polygon([(cx - 6, y + int(h * 0.18)), (cx + 6, y + int(h * 0.18)), (cx, y + int(h * 0.04))], fill=(196, 40, 44))
    d.polygon([(cx - 6, y + int(h * 0.55)), (cx - 14, y + int(h * 0.68)), (cx - 6, y + int(h * 0.68))], fill=(52, 84, 168))
    d.polygon([(cx + 6, y + int(h * 0.55)), (cx + 14, y + int(h * 0.68)), (cx + 6, y + int(h * 0.68))], fill=(52, 84, 168))
    d.polygon([(cx - 4, y + int(h * 0.68)), (cx + 4, y + int(h * 0.68)), (cx + 8, y + h - 2), (cx - 8, y + h - 2)], fill=(255, 170, 60))


@painter("football")
def paint_football(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 120, 60))
    for i in range(4):
        d.line([x, y + int(h * (0.2 + 0.2 * i)), x + w, y + int(h * (0.2 + 0.2 * i))], fill=(70, 150, 84), width=2)
    d.ellipse([x + int(w * 0.30), y + int(h * 0.25), x + int(w * 0.70), y + int(h * 0.75)], outline=(240, 240, 240), width=2)
    bx, by = x + int(w * 0.50), y + int(h * 0.50)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(250, 250, 250), outline=(30, 30, 30))


@painter("tennis")
def paint_tennis(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 90, 160))
    d.rectangle([x + int(w * 0.12), y + int(h * 0.12), x + int(w * 0.88), y + int(h * 0.88)], outline=(240, 240, 240), width=2)
    d.line([x + int(w * 0.12), y + h // 2, x + int(w * 0.88), y + h // 2], fill=(240, 240, 240), width=1)
    bx, by = x + int(w * 0.72), y + int(h * 0.30)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(200, 230, 60))


@painter("golf")
def paint_golf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 180, 110))
    d.ellipse([x + int(w * 0.55), y + int(h * 0.45), x + int(w * 0.95), y + int(h * 0.85)], fill=(90, 160, 90))
    fx = x + int(w * 0.75)
    d.line([fx, y + int(h * 0.20), fx, y + int(h * 0.62)], fill=(240, 240, 240), width=2)
    d.polygon([(fx, y + int(h * 0.20)), (fx + int(w * 0.16), y + int(h * 0.28)), (fx, y + int(h * 0.36))], fill=(196, 40, 44))
    d.ellipse([x + int(w * 0.20) - 3, y + int(h * 0.70) - 3, x + int(w * 0.20) + 3, y + int(h * 0.70) + 3], fill=(250, 250, 250))


@painter("sumo")
def paint_sumo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 164, 108))
    cx, cy = x + w // 2, y + int(h * 0.55)
    d.ellipse([cx - int(w * 0.34), cy - int(h * 0.28), cx + int(w * 0.34), cy + int(h * 0.28)], fill=(140, 110, 60))
    d.ellipse([cx - int(w * 0.28), cy - int(h * 0.20), cx + int(w * 0.28), cy + int(h * 0.20)], fill=(168, 134, 76))
    d.ellipse([cx - int(w * 0.16), cy - int(h * 0.30), cx - int(w * 0.06), cy - int(h * 0.20)], fill=(60, 40, 30))
    d.ellipse([cx + int(w * 0.06), cy - int(h * 0.30), cx + int(w * 0.16), cy - int(h * 0.20)], fill=(60, 40, 30))


@painter("golf2")
def paint_golf2(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(90, 130, 120))
    d.rectangle([x, y + int(h * 0.60), x + w, y + h], fill=(70, 110, 90))
    for i in range(3):  # rain streaks over a washed-out course
        rx = x + int(w * (0.2 + 0.3 * i))
        d.line([rx, y + int(h * 0.15), rx - 4, y + int(h * 0.35)], fill=(200, 220, 235), width=1)
    fx = x + int(w * 0.60)
    d.line([fx, y + int(h * 0.30), fx, y + int(h * 0.70)], fill=(240, 240, 240), width=2)
    d.polygon([(fx, y + int(h * 0.30)), (fx + int(w * 0.14), y + int(h * 0.38)), (fx, y + int(h * 0.46))], fill=(240, 200, 40))


@painter("nfl")
def paint_nfl(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 110, 60))
    for i in range(5):
        lx = x + int(w * (0.15 + 0.18 * i))
        d.line([lx, y + 4, lx, y + h - 4], fill=(240, 240, 240), width=1)
    cx, cy = x + int(w * 0.50), y + int(h * 0.50)
    d.ellipse([cx - int(w * 0.14), cy - int(h * 0.14), cx + int(w * 0.14), cy + int(h * 0.14)], fill=(120, 70, 40), outline=(250, 250, 250))
    d.line([cx - int(w * 0.08), cy, cx + int(w * 0.08), cy], fill=(250, 250, 250), width=1)


# ------------------------------------------------------------------- layouts
# The duel layouts. A (flat) won the account's duel and produces the
# committed entry.png; B (layered shadows) is the appeal backup and
# C (compact grid) the third variant. Only geometry differs.
LAYOUTS = {
    "A": dict(label="A - 2D FLAT", shadow=0, lead_ids=[1, 3, 5],
              hook="GULF HIT OVERNIGHT  -  COP31 FINAL TEXT IN ANTALYA  -  INDIA 720/9, A RECORD",
              lead_strip=48, small_strip=30),
    "B": dict(label="B - 3D LAYERED", shadow=5, lead_ids=[1, 3, 5],
              hook="GULF HIT OVERNIGHT  -  COP31 FINAL TEXT IN ANTALYA  -  INDIA 720/9, A RECORD",
              lead_strip=52, small_strip=32),
    "C": dict(label="C - 2D COMPACT GRID", shadow=0, lead_ids=[],
              hook="INDIA 720/9, A RECORD  -  GULF HIT OVERNIGHT  -  COP31 FINAL TEXT IN ANTALYA",
              lead_strip=36, small_strip=36),
}


class Atlas:
    """One newspaper page, painted section by section onto a canvas."""

    def __init__(self, layout):
        self.layout = layout
        self.img = Image.new("RGB", (SIDE, SIDE), CREAM)
        self.d = ImageDraw.Draw(self.img)

    # -- a single pictured story -------------------------------------------
    def strip(self, card, x, y, w, h, lead=False):
        d = self.d
        lay = self.layout
        if lay["shadow"]:
            d.rectangle([x + 3, y + 3, x + w + 3, y + h + 3], fill=(200, 190, 160))
            d.rectangle([x, y, x + w, y + 2], fill=(255, 255, 255))
        PAINTERS[card["scene"]](d, x, y, w, h)
        d.rectangle([x, y, x + w, y + 3], fill=REGION_TINT[card["region"]])
        band_h = 16 if lead else 12
        d.rectangle([x, y + h - band_h, x + w, y + h], fill=BODY)
        cap_font = shrink_to_fit(d, card["caption"], 10 if lead else 9, w - 10)
        centred(d, x + w / 2, y + h - band_h + (1 if lead else 0),
                card["caption"], cap_font, CREAM)
        if lead:
            self._tag_chip(card["tag"], bold(10), x, y, w, top=5, height=14)
            self._label_chip(card, x, y + h - band_h - 18, w, big=True)
        else:
            # small strip: source tag top-right, label chip top-left;
            # the label's width budget leaves room so they never meet.
            tag_w = self._tag_chip(card["stag"], bold(9), x, y, w, top=2, height=13)
            self._label_chip(card, x, y + 2, w, big=False, budget=w - tag_w - 20)

    def _tag_chip(self, text, font, x, y, w, top, height):
        d = self.d
        tag_w = text_w(d, text, font) + 8
        d.rectangle([x + w - tag_w - 3, y + top, x + w - 3, y + top + height], fill=BODY)
        d.text((x + w - tag_w + 1, y + top + 1), text, font=font, fill=CREAM)
        return tag_w

    def _label_chip(self, card, x, ly, w, big, budget=None):
        d = self.d
        lab_font = shrink_to_fit(d, card["label"], 12 if big else 10,
                                 (w - 12) if big else budget)
        lab_w = text_w(d, card["label"], lab_font) + 9
        lab_h = 16 if big else 13
        d.rectangle([x + 3, ly, x + 3 + lab_w, ly + lab_h], fill=WINE)
        d.text((x + 7, ly + 2), card["label"], font=lab_font, fill=(255, 255, 255))

    def card(self, card, x, y, w, strip_h, lead=False):
        d = self.d
        lay = self.layout
        if lay["shadow"]:
            off = lay["shadow"]
            d.rectangle([x + off, y + off, x + w + off, y + strip_h + 62 + off], fill=DROP)
        d.rectangle([x, y, x + w, y + strip_h], outline=CARD_EDGE, width=1)
        self.strip(card, x, y, w, strip_h, lead)
        ry = y + strip_h + (5 if lead else 3)
        d.text((x + 1, ry),
               "%d  %s - %s - %s" % (card["no"], card["place"], card["region"], card["topic"]),
               font=bold(11 if lead else 9), fill=REGION_TINT[card["region"]])
        hy = ry + (15 if lead else 12)
        head_font = display(22 if lead else 14)
        for ln in wrap_lines(d, card["headline"], head_font, w - 2)[:2]:
            d.text((x + 1, hy), ln, font=head_font, fill=BODY)
            hy += 24 if lead else 15
        for ln in wrap_lines(d, card["deck"], plain(12), w - 2):
            d.text((x + 1, hy + 1), ln, font=plain(12), fill=DECK_INK)
            hy += 13 if lead else 12.5
        return hy

    # -- everything above the cards -----------------------------------------
    def header(self):
        d = self.d
        lay = self.layout
        d.rectangle([0, 0, SIDE, 24], fill=PINE)
        d.text((EDGE, 5), "THE WORLD IN ONE DAY  ·  GAZETTEER EDITION", font=bold(12), fill=CREAM)
        right = "40 STORIES - 7 REGIONS - EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
        d.text((SIDE - EDGE - text_w(d, right, bold(11)), 6), right, font=bold(11), fill=CREAM)
        if lay["shadow"]:
            d.text((EDGE + 2, 31), "The Daily Atlas", font=display(44), fill=(200, 190, 160))
        d.text((EDGE, 29), "The Daily Atlas", font=display(44), fill=BODY)
        date1 = "SUNDAY 22 NOVEMBER 2026"
        d.text((SIDE - EDGE - text_w(d, date1, bold(14)), 34), date1, font=bold(14), fill=PINE)
        date2 = "Atlas edition - one page, the whole day"
        d.text((SIDE - EDGE - text_w(d, date2, plain(11)), 54), date2, font=plain(11), fill=FADED)
        d.line([EDGE, 78, SIDE - EDGE, 78], fill=WINE, width=3)
        d.rectangle([EDGE, 84, SIDE - EDGE, 108], fill=WINE)
        centred(d, SIDE / 2, 90, lay["hook"],
                shrink_to_fit(d, lay["hook"], 13, SPAN - 24), (255, 255, 255))
        slot_w = SPAN / 6
        for i, (lab, ev) in enumerate(DAY_CLOCK):
            cx = EDGE + i * slot_w
            if i:
                d.line([cx, 114, cx, 144], fill=LINERULE, width=1)
            d.text((cx + 8, 109), lab, font=bold(10), fill=PINE)
            ey = 120
            for ln in wrap_lines(d, ev, plain(10), slot_w - 14)[:2]:
                d.text((cx + 8, ey), ln, font=plain(10), fill=BODY)
                ey += 11
        d.line([EDGE, 144, SIDE - EDGE, 144], fill=LINERULE, width=1)
        d.text((EDGE, 148), "THE DAY IN NUMBERS", font=bold(10), fill=PINE)
        num_w = SPAN / 6
        for i, (num, cap) in enumerate(DAY_FIGURES):
            cx = EDGE + i * num_w
            centred(d, cx + num_w / 2, 160, num, display(25), WINE)
            cy = 189
            for ln in wrap_lines(d, cap, plain(10), num_w - 8)[:2]:
                centred(d, cx + num_w / 2, cy, ln, plain(10), FADED)
                cy += 11
        chip_w = (SPAN - 6 * 6) / 7
        for i, (name, n) in enumerate(REGION_TALLY):
            cx = EDGE + i * (chip_w + 6)
            d.rectangle([cx, 203, cx + chip_w, 221], fill=REGION_TINT[name])
            centred(d, cx + chip_w / 2, 207, "%s %d" % (name, n), bold(10), (255, 255, 255))
        d.line([EDGE, 226, SIDE - EDGE, 226], fill=LINERULE, width=1)

    # -- the card block; returns the y where the lower band starts ---------
    def card_block(self):
        lay = self.layout
        by_no = {c["no"]: c for c in STORIES}
        if lay["lead_ids"]:
            lead_w = (SPAN - 2 * 12) / 3
            end = 0
            for i, no in enumerate(lay["lead_ids"]):
                end = max(end, self.card(by_no[no], EDGE + i * (lead_w + 12), 230,
                                         lead_w, lay["lead_strip"], lead=True))
            fy = end + 6
            rest = [c for c in STORIES if c["no"] not in lay["lead_ids"]]
            feat_w = (SPAN - 4 * 10) / 5
            for r in range(2):
                end = 0
                for c in range(5):
                    end = max(end, self.card(rest[r * 5 + c], EDGE + c * (feat_w + 10),
                                             fy, feat_w, lay["small_strip"]))
                fy = end + 6
            return fy
        # compact grid: rows of 5 + 5 + 3, every card the same size
        feat_w = (SPAN - 4 * 10) / 5
        fy = 230
        for r in range(3):
            end = 0
            for c, card in enumerate(STORIES[r * 5:(r + 1) * 5]):
                end = max(end, self.card(card, EDGE + c * (feat_w + 10),
                                         fy, feat_w, lay["small_strip"]))
            fy = end + 6
        return fy

    # -- map panel (left) ----------------------------------------------------
    def map_panel(self, top, bottom=960):
        d = self.d
        x0, x1 = EDGE, EDGE + 430
        d.rectangle([x0, top, x1, bottom], fill=DEEP_SEA)
        d.text((x0 + 12, top + 7), "WHERE IT HAPPENED", font=bold(12), fill=CREAM)
        mx0, mx1, my0, my1 = x0 + 10, x1 - 10, top + 28, bottom - 30

        def px(lon):
            return mx0 + (lon + 180) / 360 * (mx1 - mx0)

        def py(lat):
            return my0 + (82 - lat) / 140 * (my1 - my0)

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
                    d.polygon(pts, fill=LANDMASS)
        for _no, _text, region, lon, lat in BRIEF_ROWS:
            if lon is not None:
                cx, cy = px(lon), py(lat)
                d.ellipse([cx - 2.6, cy - 2.6, cx + 2.6, cy + 2.6], fill=REGION_TINT[region])
        for card in STORIES:
            if card["lon"] is None:
                continue
            cx, cy = px(card["lon"]), py(card["lat"])
            r = 9
            d.ellipse([cx - r, cy - r, cx + r, cy + r],
                      fill=REGION_TINT[card["region"]], outline=CREAM, width=2)
            s = str(card["no"])
            f = bold(10)
            d.text((cx - text_w(d, s, f) / 2, cy - 5), s, font=f, fill=(255, 255, 255))
        d.text((x0 + 12, bottom - 18), "Pins 1-13 = pictured stories - dots = briefs",
               font=plain(9), fill=CREAM)

    # -- briefs column (right of the map) ------------------------------------
    def briefs_column(self, top):
        d = self.d
        x = EDGE + 430 + 16
        w = SIDE - EDGE - x
        d.text((x, top + 5), "ALSO ON SUNDAY 22 NOVEMBER - 27 MORE STORIES",
               font=bold(12), fill=PINE)
        d.line([x, top + 21, SIDE - EDGE, top + 21], fill=PINE, width=1)
        y0 = top + 26
        leading = (960 - y0) / len(BRIEF_ROWS)
        y = y0
        for no, text, region, _lon, _lat in BRIEF_ROWS:
            ns = str(no)
            d.text((x, y), ns, font=bold(9), fill=REGION_TINT[region])
            off = text_w(d, ns, bold(9)) + 5
            first = wrap_lines(d, text, plain(9), w - off)[0]  # one line only
            d.text((x + off, y), first, font=plain(9), fill=BRIEF_INK)
            y += leading
        return leading

    # -- date-check band and footers ------------------------------------------
    def foot_bands(self):
        d = self.d
        y0, y1 = 966, 1004
        d.rectangle([EDGE, y0, SIDE - EDGE, y1], fill=SHEET, outline=WINE, width=2)
        lab = "DATE CHECK"
        d.text((EDGE + 8, y0 + 5), lab, font=bold(10), fill=WINE)
        tx = EDGE + 8 + text_w(d, lab, bold(10)) + 8
        cur = ""
        for word in DATE_CHECK.split():
            trial = (cur + " " + word).strip()
            if text_w(d, trial, plain(9)) <= (SIDE - EDGE - 8) - tx:
                cur = trial
            else:
                break
        first = cur
        remainder = DATE_CHECK[len(first):].strip()
        d.text((tx, y0 + 5), first, font=plain(9), fill=BODY)
        yy = y0 + 16
        for ln in wrap_lines(d, remainder, plain(9), SPAN - 16)[:2]:
            d.text((EDGE + 8, yy), ln, font=plain(9), fill=BODY)
            yy += 11
        d.text((EDGE, 1010), FOOT_LEFT, font=plain(9), fill=FADED)
        d.text((SIDE - EDGE - text_w(d, FOOT_RIGHT, plain(9)), 1010),
               FOOT_RIGHT, font=plain(9), fill=FADED)

    # -- whole page -------------------------------------------------------------
    def render(self, out_path):
        self.header()
        lower_top = self.card_block()
        leading = self.briefs_column(lower_top)
        self.map_panel(lower_top)
        self.foot_bands()
        flat = self.img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
        flat.save(out_path, optimize=True)
        print(self.layout["label"], "lower band starts:", lower_top,
              "brief leading: %.2f" % leading)
        print("saved", out_path, os.path.getsize(out_path), "bytes")
        return lower_top


def build(layout_key, out_path):
    return Atlas(LAYOUTS[layout_key]).render(out_path)


if __name__ == "__main__":
    build("A", os.path.join(BASE, "entry.png"))
