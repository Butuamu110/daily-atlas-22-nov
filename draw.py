#!/usr/bin/env python3
"""Renderer for The Daily Atlas — one-page world, Sunday 22 Nov 2026.

Written from scratch for the round-4 entry of @rojanon11. The page
packs 37 stories into a single 1024x1024 sheet: a date masthead, an
italic standfirst, a strip of six headline figures, a proportional
region tally, three large pictured leads, eighteen small pictured
cards, a pin map covering every story, sixteen one-line briefs and
a three-row DATE CHECK box.

Colour discipline: each pictured scene sits on a ground made by
washing its region colour most of the way toward the paper tone,
then carries a single mid-strength shape and one small saturated
accent. The loud full-strength region colours are reserved for the
slug ribbons, the tally, the number discs and the map pins, which
is what keeps the sheet readable when shrunk to a thumbnail.

PIL only; the render is deterministic.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANVAS = 1024
MARGIN = 12
SPAN = CANVAS - 2 * MARGIN

PAGE_BG = (247, 242, 232)
TYPE_BLACK = (26, 24, 20)
TOPBAR = (26, 26, 26)
ACCENT_RED = (165, 40, 40)
OFFWHITE = (250, 248, 240)
MUTED = (110, 102, 88)
MAP_SEA = (205, 225, 235)
MAP_LAND = (222, 205, 180)

REGIONS = {
    "MIDEAST": (156, 46, 90),
    "GLOBAL": (17, 107, 88),
    "OCEANIA": (78, 128, 45),
    "ASIA": (160, 130, 47),
    "EUROPE": (45, 88, 146),
    "AMERICAS": (181, 83, 39),
}
REGION_ORDER = ["MIDEAST", "GLOBAL", "OCEANIA", "ASIA", "EUROPE",
                "AMERICAS"]

_FONT_FILES = {"bold": "Archivo-Bold.ttf",
               "med": "Archivo-Medium.ttf",
               "serif": "PlayfairDisplay-900.ttf"}
_font_store = {}


def font(kind, px):
    key = (kind, px)
    if key not in _font_store:
        path = os.path.join(BASE_DIR, "fonts", _FONT_FILES[kind])
        _font_store[key] = ImageFont.truetype(path, px)
    return _font_store[key]


def measure(d, text, fnt):
    return d.textlength(text, font=fnt)


def wrap_paragraph(d, text, fnt, maxw):
    """Greedy word wrap; returns the list of line strings."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if measure(d, trial, fnt) <= maxw or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def truncate_line(d, text, fnt, maxw):
    """Whole words only, cut until the line fits maxw."""
    if measure(d, text, fnt) <= maxw:
        return text
    kept = ""
    for word in text.split():
        trial = (kept + " " + word).strip()
        if measure(d, trial, fnt) > maxw:
            break
        kept = trial
    return kept


def ink_text(d, pos, text, fnt, fill=TYPE_BLACK, anchor="la"):
    d.text(pos, text, font=fnt, fill=fill, anchor=anchor)


def wash(colour, amount):
    """Blend a colour toward the paper tone (0 = raw, 1 = paper)."""
    return tuple(int(round(c + (p - c) * amount))
                 for c, p in zip(colour, PAGE_BG))


def burst(d, cx, cy, radius, fill):
    """Sixteen-point explosion star, points alternating long/short."""
    pts = []
    for i in range(16):
        ang = i * math.pi / 8.0
        rad = radius if i % 2 == 0 else radius * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def dash_line(d, start, stop, fill, width, dash=6, gap=5):
    x0, y0 = start
    x1, y1 = stop
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    steps = int(dist // (dash + gap)) + 1
    for i in range(steps):
        t0 = i * (dash + gap) / dist
        t1 = min((i * (dash + gap) + dash) / dist, 1.0)
        d.line([x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0,
                x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1],
               fill=fill, width=width)


def slug_ribbon(d, x, y, w, h, region_key, label):
    d.rectangle([x, y, x + w, y + h], fill=REGIONS[region_key])
    fnt = font("bold", 12 if h >= 20 else 10)
    ink_text(d, (x + 6, y + (h - fnt.size) // 2 - 1),
             truncate_line(d, label, fnt, w - 12), fnt, OFFWHITE)


def number_disc(d, x, y, w, h, region_key, num, dia=17):
    bx = x + w - dia - 4
    by = y + h - dia - 4
    d.ellipse([bx, by, bx + dia, by + dia], fill=REGIONS[region_key],
              outline=OFFWHITE, width=2)
    ink_text(d, (bx + dia // 2, by + dia // 2 - 5), str(num),
             font("bold", 10), OFFWHITE, anchor="ma")


# ------------------------------------------------------------- content
LEAD_CARDS = [
    {"no": 1, "reg": "MIDEAST", "where": "BAHRAIN · STRAIT OF HORMUZ",
     "slug": "BAHRAIN: 2 RADARS CLAIMED HIT",
     "title": "Iran claims Gulf strikes on US radars",
     "body": "Missiles and drones aimed at 2 Patriot radars, Al-Riffa "
             "and Awali; a civil site burned and a tanker hit near "
             "Hormuz.",
     "credit": "REUTERS · AP · AL JAZEERA", "art": "radar"},
    {"no": 2, "reg": "GLOBAL", "where": "ANTALYA, TÜRKIYE",
     "slug": "ANTALYA: FINAL TEXT TABLED",
     "title": "COP31 final text tabled in Antalya",
     "body": "Kurum tabled the package late Saturday; objections shut "
             "03:00 GMT, approval plenary 06:00 GMT Sunday.",
     "credit": "REUTERS · DW · ANADOLU", "art": "globe"},
    {"no": 3, "reg": "OCEANIA", "where": "WELLINGTON, NEW ZEALAND",
     "slug": "WELLINGTON: 720/9 — A RECORD",
     "title": "India declare at 720/9, a record",
     "body": "Rahul 136, Pant 128: the highest Test total ever made "
             "in New Zealand. India lead NZ by 352.",
     "credit": "IANS · AFP · ESPNCRICINFO", "art": "cricket"},
]

MINI_CARDS = [
    {"no": 4, "reg": "MIDEAST", "slug": "MAKKAH: INTERCEPT 01:42",
     "title": "Makkah-bound Houthi missile intercepted",
     "credit": "MIDEAST · ANADOLU", "art": "houthi"},
    {"no": 5, "reg": "ASIA", "slug": "MYANMAR: M4.1 · 95 KM",
     "title": "M4.1 quake in Myanmar, 95 km deep at 02:35",
     "credit": "ASIA · NCS INDIA", "art": "quake"},
    {"no": 6, "reg": "AMERICAS", "slug": "LAS VEGAS: 50 LAPS · RND 22",
     "title": "Las Vegas GP: 50 laps of the Strip, round 22",
     "credit": "AMERICAS · F1", "art": "f1"},
    {"no": 7, "reg": "AMERICAS", "slug": "VANDENBERG: 12:16 UTC",
     "title": "Falcon 9 flies NROL-136, 15th NRO batch",
     "credit": "AMERICAS · VSFB", "art": "rocket_a"},
    {"no": 8, "reg": "EUROPE", "slug": "ANFIELD: 16:30 UTC · MW11",
     "title": "Liverpool host Man United, 16:30 at Anfield",
     "credit": "EUROPE · PREMIER LEAGUE", "art": "football"},
    {"no": 9, "reg": "EUROPE", "slug": "TURIN: FINAL ±16:00 UTC",
     "title": "Alcaraz meets Zverev in Turin final tonight",
     "credit": "EUROPE · ATP", "art": "tennis"},
    {"no": 10, "reg": "AMERICAS", "slug": "NAPLES: KIM -18 LEADS",
     "title": "Kim leads by one at -18 into the $4m round",
     "credit": "AMERICAS · LPGA / AP", "art": "golf_a"},
    {"no": 11, "reg": "ASIA", "slug": "FUKUOKA: TWO AT 12-2",
     "title": "Two leaders at 12-2 into sumo's final day",
     "credit": "ASIA · JSA", "art": "sumo"},
    {"no": 12, "reg": "AMERICAS", "slug": "SEA ISLAND: 3 SHARE -9",
     "title": "RSM third round rained out, three share -9",
     "credit": "AMERICAS · REUTERS", "art": "rsm"},
    {"no": 13, "reg": "AMERICAS", "slug": "NFL: 11 GAMES · WEEK 12",
     "title": "Eleven Sunday games open NFL Week 12",
     "credit": "AMERICAS · NFL", "art": "nfl"},
    {"no": 14, "reg": "OCEANIA", "slug": "WELLINGTON: GILL 98",
     "title": "Gill makes 98 in India's record 720/9 total",
     "credit": "OCEANIA · IANS", "art": "bat"},
    {"no": 15, "reg": "OCEANIA", "slug": "WELLINGTON: NICHOLLS 175",
     "title": "Nicholls top-scores with 175 in NZ's 368",
     "credit": "OCEANIA · AFP", "art": "bat"},
    {"no": 16, "reg": "MIDEAST", "slug": "BAHRAIN: RES. 2817 AT UN",
     "title": "Bahrain asks UN to enforce Resolution 2817",
     "credit": "MIDEAST · REUTERS", "art": "un"},
    {"no": 17, "reg": "MIDEAST", "slug": "KUWAIT: FIRST SINCE SEPT",
     "title": "Kuwait interception, its first since September",
     "credit": "MIDEAST · KUNA", "art": "intercept"},
    {"no": 18, "reg": "ASIA", "slug": "FUKUOKA: YUSHO 12-2",
     "title": "Yusho decider set: Onosato meets Hoshoryu",
     "credit": "ASIA · JSA", "art": "sumo"},
    {"no": 19, "reg": "AMERICAS", "slug": "SEA ISLAND: MONDAY FINISH",
     "title": "RSM final round pushed to a Monday finish",
     "credit": "AMERICAS · PGA TOUR", "art": "golf_a"},
    {"no": 20, "reg": "AMERICAS", "slug": "NAPLES: THITIKUL -17",
     "title": "Thitikul one back at -17 at Tiburon",
     "credit": "AMERICAS · LPGA / AP", "art": "golf_b"},
    {"no": 21, "reg": "AMERICAS", "slug": "LZ-4: BOOSTER B1097 BACK",
     "title": "Falcon booster B1097 lands back at Zone 4",
     "credit": "AMERICAS · SPACEX", "art": "rocket_b"},
]

BIG_NUMBERS = [
    ("2", "PATRIOT RADARS CLAIMED HIT · BAHRAIN"),
    ("06:00", "GMT - COP31 APPROVAL PLENARY"),
    ("720/9", "INDIA DECLARED · WELLINGTON"),
    ("352", "INDIA'S LEAD OVER NEW ZEALAND"),
    ("M4.1", "MYANMAR QUAKE · 95 KM DEEP"),
    ("$4M", "LPGA WINNER'S PRIZE · NAPLES"),
]

SHORT_ITEMS = [
    ("OCEANIA", "Jaiswal 85 in the Wellington total", "IANS"),
    ("OCEANIA", "Padikkal 80 as India declared, day 4", "IANS"),
    ("OCEANIA", "Bumrah 4-92 in New Zealand's 368", "AFP"),
    ("MIDEAST", "UKMTO tanker report 11:27 UTC", "UKMTO"),
    ("MIDEAST", "IRGC first statement at 19:40 UTC", "IRNA"),
    ("ASIA", "Wakamotoharu v Atamifuji finale", "JSA"),
    ("ASIA", "Atamifuji starts the last day 11-3", "JSA"),
    ("AMERICAS", "RSM Sunday tees 09:10-11:00 ET", "PGA"),
    ("AMERICAS", "Yoshida one back at -17 Sunday", "AP"),
    ("AMERICAS", "NFL early window opens 13:00 ET", "NFL"),
    ("AMERICAS", "NFL late window 16:05-16:25 ET", "NFL"),
    ("AMERICAS", "Vikings @ 49ers 20:20 ET", "NFL"),
    ("GLOBAL", "COP31 objections closed 03:00", "UNFCCC"),
    ("AMERICAS", "NROL-136 slipped Sat to Sunday", "VSFB"),
    ("AMERICAS", "Strip Circuit hosts round 22", "F1"),
    ("EUROPE", "Alcaraz rallied past Shelton, Turin semi", "ATP"),
]

DATE_CHECK_ROWS = [
    ("LEFT OUT",
     "Lviv strikes (20 Nov) · Peru M6.9 (20/21 Nov) · Sparta II "
     "(21 Nov) · Riyadh missiles (21 Nov) · France march 82,500 "
     "(21 Nov) · Berlin Coalition (19 Nov) · ICJ ruling (19 Nov) "
     "· Geneva robot deal (21 Nov)", 52),
    ("NOT YET",
     "COP31 final adoption - vote still to come · Liverpool v "
     "Man Utd result - 16:30 UTC kick-off · ATP Turin final "
     "result - played Sunday evening", 52),
    ("UNCONFIRMED",
     "IRGC claim: 2 Patriot radars destroyed - no independent "
     "confirmation · Houthi interception claim over Makkah - "
     "coalition account only", 78),
]

MAP_POINTS = {
    1: (50.5, 26.2), 2: (30.7, 36.9), 3: (174.8, -41.3),
    4: (39.8, 21.4), 5: (94.6, 24.4), 6: (-115.1, 36.1),
    7: (-120.6, 34.7), 8: (-2.96, 53.4), 9: (7.7, 45.1),
    10: (-81.8, 26.1), 11: (130.4, 33.6), 12: (-81.4, 31.2),
    13: (-98.0, 39.0), 14: (176.5, -40.6), 15: (173.2, -41.9),
    16: (51.8, 25.6), 17: (47.9, 29.3), 18: (132.0, 34.2),
    19: (-79.8, 30.6), 20: (-80.4, 25.4), 21: (-122.6, 33.4),
    22: (175.6, -42.0), 23: (174.0, -40.4), 24: (176.2, -41.6),
    25: (56.3, 26.5), 26: (51.4, 35.7), 27: (129.2, 32.9),
    28: (131.2, 34.8), 29: (-82.6, 30.4), 30: (-82.4, 25.6),
    31: (-96.0, 40.6), 32: (-100.0, 37.6), 33: (-122.0, 37.4),
    34: (29.2, 37.6), 35: (-119.0, 33.2), 36: (-113.4, 37.8),
    37: (9.3, 44.4),
}

# Rough continent outlines as (lon, lat) rings; decorative landmass
# under the pins, which carry the actual story locations.
LANDMASSES = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69),
     (-85, 66), (-80, 62), (-78, 58), (-85, 55), (-82, 50), (-90, 49),
     (-98, 49), (-110, 49), (-122, 49), (-124, 42), (-120, 35),
     (-112, 30), (-105, 24), (-97, 26), (-90, 29), (-84, 30),
     (-81, 25), (-76, 35), (-70, 42), (-65, 44), (-60, 46),
     (-65, 50), (-78, 52), (-95, 57), (-115, 60), (-140, 62),
     (-155, 60), (-165, 60)],
    [(-80, 9), (-72, 11), (-62, 8), (-52, 5), (-50, 0), (-44, -3),
     (-38, -6), (-40, -12), (-42, -20), (-50, -26), (-56, -33),
     (-62, -39), (-65, -43), (-68, -50), (-72, -52), (-74, -48),
     (-74, -40), (-72, -30), (-70, -20), (-72, -12), (-76, -6),
     (-80, -2), (-80, 4)],
    [(-10, 36), (-6, 35), (0, 37), (10, 37), (20, 32), (30, 31),
     (35, 28), (38, 22), (40, 15), (43, 12), (48, 11), (51, 12),
     (48, 6), (42, 0), (40, -6), (39, -12), (36, -20), (33, -26),
     (28, -33), (20, -35), (17, -30), (14, -22), (12, -15),
     (13, -8), (9, -2), (9, 4), (4, 6), (-3, 5), (-8, 5),
     (-13, 8), (-17, 12), (-17, 20), (-14, 24), (-10, 30)],
    [(-5, 43), (-2, 44), (0, 46), (-2, 48), (-5, 48), (-1, 50),
     (2, 51), (5, 53), (8, 55), (8, 57), (12, 56), (18, 56),
     (21, 55), (24, 58), (28, 60), (30, 62), (28, 66), (32, 70),
     (40, 68), (50, 69), (60, 69), (45, 65), (40, 62), (35, 55),
     (30, 52), (28, 48), (24, 45), (20, 42), (16, 40), (12, 44),
     (8, 44), (3, 43), (0, 39), (-2, 37), (-6, 36), (-9, 37),
     (-9, 43)],
    [(35, 36), (45, 37), (50, 30), (56, 27), (58, 23), (55, 17),
     (52, 15), (45, 12), (43, 12), (40, 20), (36, 28), (34, 31),
     (36, 36)],
    [(48, 42), (55, 45), (65, 48), (75, 50), (85, 48), (95, 50),
     (105, 48), (115, 50), (125, 52), (135, 50), (142, 52),
     (142, 45), (135, 40), (128, 38), (122, 38), (120, 32),
     (122, 28), (115, 23), (108, 20), (108, 12), (105, 8),
     (103, 5), (100, 8), (98, 14), (95, 16), (92, 20), (90, 22),
     (86, 20), (80, 15), (77, 8), (73, 16), (70, 21), (66, 25),
     (61, 25), (57, 27), (52, 28), (50, 29), (54, 35), (48, 38)],
    [(112, -12), (122, -14), (130, -12), (136, -12), (142, -11),
     (146, -15), (150, -20), (153, -27), (150, -32), (147, -38),
     (140, -38), (135, -35), (130, -32), (124, -33), (118, -35),
     (114, -32), (113, -24), (112, -16)],
    [(167, -46), (172, -43), (174, -41), (176, -38), (173, -35),
     (171, -38), (169, -43), (167, -45)],
    [(95, 5), (100, 2), (105, -2), (110, -3), (115, -2), (119, 0),
     (120, -3), (114, -5), (108, -4), (102, -2), (97, 2)],
    [(130, 32), (133, 34), (137, 35), (140, 36), (141, 40),
     (141, 44), (140, 40), (138, 36), (135, 34), (131, 33)],
]


# ------------------------------------------------------- lead scenes
# Each lead scene: washed ground, one mid-strength mass, one raw
# accent. Subjects fill at least 70% of the 110px scene height.
def scene_radar(d, x, y, w, h, colour):
    d.rectangle([x, y, x + w, y + h], fill=wash(colour, 0.80))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=wash(colour, 0.55))
    mast_x, top = x + 92, y + 8
    d.line([mast_x, y + h - 18, mast_x, top + 38],
           fill=(70, 74, 80), width=6)
    d.pieslice([mast_x - 58, top - 4, mast_x + 58, top + 54],
               start=0, end=180, fill=wash(colour, 0.35))
    d.ellipse([mast_x - 58, top - 4, mast_x + 58, top + 8],
              fill=(96, 100, 106))
    d.line([mast_x, top + 24, mast_x + 48, top + 2],
           fill=(70, 74, 80), width=3)
    d.ellipse([mast_x + 44, top - 2, mast_x + 54, top + 8], fill=colour)
    burst(d, x + 252, y + 52, 40, colour)
    burst(d, x + 252, y + 52, 18, wash(colour, 0.30))
    ship_x, ship_y = x + w - 96, y + h - 16
    d.polygon([(ship_x, ship_y), (ship_x + 80, ship_y),
               (ship_x + 70, ship_y + 7), (ship_x + 8, ship_y + 7)],
              fill=(40, 44, 50))
    d.rectangle([ship_x + 52, ship_y - 7, ship_x + 65, ship_y],
                fill=(40, 44, 50))


def scene_globe(d, x, y, w, h, colour):
    d.rectangle([x, y, x + w, y + h], fill=wash(colour, 0.82))
    cx, cy, r = x + w // 2, y + h // 2 - 2, 47
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=wash(colour, 0.30))
    d.ellipse([cx - r + 9, cy - r + 12, cx - 6, cy - 6], fill=colour)
    d.ellipse([cx + 7, cy - 1, cx + 34, cy + 26], fill=colour)
    d.ellipse([cx - 31, cy + 14, cx - 7, cy + 34], fill=wash(colour, 0.05))
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              outline=(90, 94, 98), width=3)
    podium = wash(colour, 0.45)
    d.rectangle([x + 10, y + h - 16, x + 84, y + h - 10], fill=podium)
    d.polygon([(x + 10, y + h - 16), (x + 84, y + h - 16),
               (x + 47, y + h - 24)], fill=podium)
    d.rectangle([x + w - 84, y + h - 16, x + w - 10, y + h - 10],
                fill=podium)
    d.polygon([(x + w - 84, y + h - 16), (x + w - 10, y + h - 16),
               (x + w - 47, y + h - 24)], fill=podium)


def scene_cricket(d, x, y, w, h, colour):
    d.rectangle([x, y, x + w, y + h], fill=wash(colour, 0.78))
    d.ellipse([x + 6, y + 4, x + w - 6, y + h - 3], fill=wash(colour, 0.55))
    d.ellipse([x + 16, y + 9, x + w - 16, y + h - 7],
              fill=wash(colour, 0.88))
    d.ellipse([x + 28, y + 14, x + w - 28, y + h - 12],
              fill=wash(colour, 0.40))
    cx = x + w // 2
    d.rectangle([cx - 12, y + 20, cx + 12, y + h - 18],
                fill=(219, 198, 148))
    for stump_x in (cx - 7, cx + 4):
        d.rectangle([stump_x, y + 25, stump_x + 3, y + 34],
                    fill=(120, 96, 30))
        d.rectangle([stump_x, y + h - 36, stump_x + 3, y + h - 27],
                    fill=(120, 96, 30))
    d.ellipse([x + w - 70, y + 13, x + w - 28, y + 55], fill=(172, 44, 48))
    d.arc([x + w - 62, y + 17, x + w - 36, y + 51], start=300, end=130,
          fill=OFFWHITE, width=2)


LEAD_SCENES = {"radar": scene_radar, "globe": scene_globe,
               "cricket": scene_cricket}


# ------------------------------------------------------- mini scenes
# Same colour recipe at 45px: washed ground, mid mass, raw accent.
def mini_intercept_arc(d, x, y, w, h, pale, mid, full):
    dash_line(d, (x + 6, y + h - 6), (x + 92, y + 8), mid, width=4)
    burst(d, x + 110, y + 13, 13, full)
    d.rectangle([x + 126, y + h - 14, x + w - 4, y + h - 5], fill=mid)


def mini_seismograph(d, x, y, w, h, pale, mid, full):
    midy = y + h // 2
    pts = []
    for i in range(46):
        amp = 3 + 15 * abs(math.sin(i * 0.55)) * (
            0.4 + 0.6 * abs(math.sin(i * 0.13)))
        pts.append((x + 5 + i * 3.3, midy + (amp if i % 2 else -amp)))
    d.line(pts, fill=full, width=3)


def mini_racecar(d, x, y, w, h, pale, mid, full):
    d.arc([x + 2, y, x + 126, y + h + 20], start=180, end=330,
          fill=mid, width=5)
    d.polygon([(x + 102, y + 13), (x + 140, y + 13), (x + 148, y + 25),
               (x + 110, y + 25)], fill=(30, 30, 34))
    d.rectangle([x + 114, y + 6, x + 128, y + 13], fill=full)
    d.ellipse([x + 108, y + 23, x + 118, y + 33], fill=(30, 30, 34))
    d.ellipse([x + 134, y + 23, x + 144, y + 33], fill=(30, 30, 34))


def _rocket_body(d, x, y, w, h, pale, mid, full, nose_x):
    d.polygon([(nose_x, y + 1), (nose_x + 11, y + 13),
               (nose_x - 11, y + 13)], fill=mid)
    d.rectangle([nose_x - 11, y + 13, nose_x + 11, y + h - 9], fill=mid)
    d.rectangle([nose_x - 4, y + 19, nose_x + 4, y + 27], fill=pale)
    d.polygon([(nose_x - 11, y + h - 15), (nose_x - 20, y + h - 3),
               (nose_x - 11, y + h - 3)], fill=full)
    d.polygon([(nose_x + 11, y + h - 15), (nose_x + 20, y + h - 3),
               (nose_x + 11, y + h - 3)], fill=full)
    burst(d, nose_x, y + h - 2, 7, full)


def mini_rocket_left(d, x, y, w, h, pale, mid, full):
    _rocket_body(d, x, y, w, h, pale, mid, full, x + 44)


def mini_rocket_right(d, x, y, w, h, pale, mid, full):
    _rocket_body(d, x, y, w, h, pale, mid, full, x + 106)


def mini_pitch(d, x, y, w, h, pale, mid, full):
    d.rectangle([x + 5, y + 5, x + w - 5, y + h - 5], outline=mid, width=2)
    d.line([x + w // 2, y + 5, x + w // 2, y + h - 5], fill=mid, width=2)
    d.ellipse([x + w // 2 - 12, y + h // 2 - 12, x + w // 2 + 12,
               y + h // 2 + 12], outline=mid, width=2)
    d.ellipse([x + w // 2 + 26, y + h // 2 - 7, x + w // 2 + 40,
               y + h // 2 + 7], fill=full)


def mini_court(d, x, y, w, h, pale, mid, full):
    d.rectangle([x + 8, y + 6, x + 120, y + h - 6], outline=mid, width=2)
    d.line([x + 64, y + 6, x + 64, y + h - 6], fill=(40, 40, 44), width=4)
    d.line([x + 8, y + h // 2, x + 120, y + h // 2], fill=mid, width=2)
    d.ellipse([x + 94, y + 8, x + 110, y + 24], fill=full)
    d.ellipse([x + 136, y + h - 18, x + 148, y + h - 6], fill=mid)


def _golf_green(d, x, y, w, h, pale, mid, full, flag_x):
    d.ellipse([x + 6, y + h - 16, x + 130, y + h - 2], fill=mid)
    d.line([flag_x, y + 4, flag_x, y + h - 4], fill=(90, 94, 98), width=3)
    d.polygon([(flag_x, y + 4), (flag_x + 16, y + 10), (flag_x, y + 16)],
              fill=full)
    d.ellipse([flag_x - 5, y + h - 9, flag_x + 5, y + h - 3],
              fill=(30, 30, 32))
    d.ellipse([x + 26, y + 9, x + 34, y + 17], fill=mid)


def mini_golf_far_flag(d, x, y, w, h, pale, mid, full):
    _golf_green(d, x, y, w, h, pale, mid, full, x + 146)


def mini_golf_near_flag(d, x, y, w, h, pale, mid, full):
    _golf_green(d, x, y, w, h, pale, mid, full, x + 40)


def mini_ring(d, x, y, w, h, pale, mid, full):
    d.ellipse([x + 42, y + 1, x + 118, y + h - 1], outline=mid, width=4)
    d.ellipse([x + 62, y + 11, x + 82, y + 31], fill=(52, 44, 40))
    d.ellipse([x + 80, y + 11, x + 100, y + 31], fill=mid)
    d.rectangle([x + 66, y + 28, x + 96, y + 36], fill=full)


def mini_rain_chart(d, x, y, w, h, pale, mid, full):
    for i in range(3):
        bar_x = x + 18 + i * 42
        d.rectangle([bar_x, y + 14, bar_x + 26, y + h - 3], fill=mid)
    ink_text(d, (x + w // 2, y + 1), "-9", font("bold", 14), full,
             anchor="ma")


def mini_gridiron(d, x, y, w, h, pale, mid, full):
    for i in range(6):
        line_x = x + 10 + i * 26
        d.line([line_x, y + 4, line_x, y + h - 4], fill=mid, width=2)
    d.ellipse([x + w // 2 - 16, y + h // 2 - 9, x + w // 2 + 16,
               y + h // 2 + 9], fill=full)
    d.line([x + w // 2 - 8, y + h // 2, x + w // 2 + 8, y + h // 2],
           fill=OFFWHITE, width=2)


def mini_bat(d, x, y, w, h, pale, mid, full):
    d.polygon([(x + 30, y + h - 4), (x + 52, y + h - 4), (x + 96, y + 6),
               (x + 82, y + 2)], fill=mid)
    d.ellipse([x + 106, y + 20, x + 138, y + 42], fill=full)


def mini_assembly(d, x, y, w, h, pale, mid, full):
    d.rectangle([x + 18, y + 12, x + w - 18, y + h - 4], fill=mid)
    for i in range(5):
        col_x = x + 30 + i * 22
        d.rectangle([col_x, y + 18, col_x + 8, y + h - 10], fill=pale)
    d.polygon([(x + 12, y + 12), (x + w - 12, y + 12),
               (x + w // 2, y + 2)], fill=full)


def mini_intercept_low(d, x, y, w, h, pale, mid, full):
    dash_line(d, (x + w - 8, y + 4), (x + 60, y + h - 10), mid, width=4)
    burst(d, x + 48, y + h - 14, 14, full)
    d.rectangle([x + 8, y + 6, x + 44, y + 16], fill=mid)


MINI_SCENES = {
    "houthi": mini_intercept_arc,
    "quake": mini_seismograph,
    "f1": mini_racecar,
    "rocket_a": mini_rocket_left,
    "rocket_b": mini_rocket_right,
    "football": mini_pitch,
    "tennis": mini_court,
    "golf_a": mini_golf_far_flag,
    "golf_b": mini_golf_near_flag,
    "sumo": mini_ring,
    "rsm": mini_rain_chart,
    "nfl": mini_gridiron,
    "bat": mini_bat,
    "un": mini_assembly,
    "intercept": mini_intercept_low,
}


def paint_mini_scene(d, x, y, w, h, art_key, colour):
    d.rectangle([x, y, x + w, y + h], fill=wash(colour, 0.80))
    MINI_SCENES[art_key](d, x, y, w, h, wash(colour, 0.80),
                         wash(colour, 0.45), colour)


# ---------------------------------------------------------------- map
def paint_world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAP_SEA)
    ox, oy = x + 6, y + 6
    mw, mh = w - 12, h - 12

    def project(lon, lat):
        lat = max(-58.0, min(84.0, lat))
        return (ox + (lon + 180.0) / 360.0 * mw,
                oy + (84.0 - lat) / 142.0 * mh)

    for ring in LANDMASSES:
        d.polygon([project(lo, la) for lo, la in ring], fill=MAP_LAND)

    region_of = {}
    for card in LEAD_CARDS + MINI_CARDS:
        region_of[card["no"]] = card["reg"]
    for i, (reg, _txt, _src) in enumerate(SHORT_ITEMS):
        region_of[22 + i] = reg

    for num in range(1, 38):
        px, py = project(*MAP_POINTS[num])
        dia = 15 if num <= 21 else 13
        d.ellipse([px - dia / 2, py - dia / 2, px + dia / 2,
                   py + dia / 2], fill=REGIONS[region_of[num]],
                  outline=OFFWHITE, width=1)
        ink_text(d, (px, py - 4), str(num), font("bold", 8), OFFWHITE,
                 anchor="ma")


# ------------------------------------------------------------ assembly
def render_page():
    img = Image.new("RGB", (CANVAS, CANVAS), PAGE_BG)
    d = ImageDraw.Draw(img)

    story_total = len(LEAD_CARDS) + len(MINI_CARDS) + len(SHORT_ITEMS)
    assert story_total == 37, story_total

    # Top black bar.
    d.rectangle([0, 0, CANVAS, 22], fill=TOPBAR)
    ink_text(d, (MARGIN, 4), "THE DAILY ATLAS · THE WORLD IN ONE DAY",
             font("bold", 12), OFFWHITE)
    ink_text(d, (CANVAS - MARGIN, 4),
             "%d STORIES · 6 REGIONS · ALL FROM TODAY" % story_total,
             font("bold", 12), OFFWHITE, anchor="ra")

    # Masthead: set the date huge on a scratch layer, trim it, scale
    # it to the measured 958x88 ink box and centre it.
    layer = Image.new("RGBA", (1750, 160), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((6, 6), "SUNDAY 22 NOVEMBER 2026",
                               font=font("serif", 118),
                               fill=TYPE_BLACK + (255,))
    layer = layer.crop(layer.getbbox()).resize((958, 88), Image.LANCZOS)
    img.paste(layer, (MARGIN + (SPAN - layer.size[0]) // 2, 26), layer)
    d = ImageDraw.Draw(img)

    # Italic standfirst: the three lead headlines joined, sheared.
    standfirst = " · ".join(c["title"] for c in LEAD_CARDS)
    size = 19
    while size > 14 and measure(d, standfirst, font("serif", size)) \
            > SPAN - 8:
        size -= 1
    slab = Image.new("RGBA", (SPAN + 80, 44), (0, 0, 0, 0))
    ImageDraw.Draw(slab).text((30, 4), standfirst,
                              font=font("serif", size),
                              fill=(70, 52, 30, 255))
    slab = slab.transform(slab.size, Image.AFFINE, (1, 0.22, -10, 0, 1, 0),
                          resample=Image.BICUBIC)
    slab = slab.crop(slab.getbbox())
    img.paste(slab, (MARGIN + (SPAN - slab.size[0]) // 2, 118), slab)
    d = ImageDraw.Draw(img)

    # Six headline figures with captions.
    fig_y = 148
    d.line([MARGIN, fig_y - 5, CANVAS - MARGIN, fig_y - 5],
           fill=ACCENT_RED, width=2)
    segw = SPAN // 6
    for i, (num, caption) in enumerate(BIG_NUMBERS):
        cell_x = MARGIN + i * segw
        ink_text(d, (cell_x + 2, fig_y), num, font("bold", 50), ACCENT_RED)
        ink_text(d, (cell_x + 2, fig_y + 54),
                 truncate_line(d, caption, font("bold", 8), segw - 8),
                 font("bold", 8), TYPE_BLACK)

    # Region tally: segment widths proportional to story counts,
    # labels inside their segments.
    counts = {}
    for card in LEAD_CARDS + MINI_CARDS:
        counts[card["reg"]] = counts.get(card["reg"], 0) + 1
    for reg, _txt, _src in SHORT_ITEMS:
        counts[reg] = counts.get(reg, 0) + 1
    assert sum(counts.values()) == story_total
    tx = MARGIN
    for reg in REGION_ORDER:
        seg_w = int(round(SPAN * counts[reg] / story_total))
        if reg == REGION_ORDER[-1]:
            seg_w = MARGIN + SPAN - tx
        d.rectangle([tx, 218, tx + seg_w, 218 + 16], fill=REGIONS[reg])
        label = "%s %d" % (reg, counts[reg])
        if measure(d, label, font("bold", 9)) + 8 <= seg_w:
            ink_text(d, (tx + seg_w // 2, 222), label, font("bold", 9),
                     OFFWHITE, anchor="ma")
        tx += seg_w

    # The three leads.
    lead_y, scene_h = 242, 110
    lead_w = (SPAN - 16) // 3
    for i, card in enumerate(LEAD_CARDS):
        cx = MARGIN + i * (lead_w + 8)
        slug_ribbon(d, cx, lead_y, lead_w, 20, card["reg"], card["slug"])
        LEAD_SCENES[card["art"]](d, cx, lead_y + 20, lead_w, scene_h,
                                 REGIONS[card["reg"]])
        number_disc(d, cx, lead_y + 20, lead_w, scene_h, card["reg"],
                    card["no"])
        kick_y = lead_y + 20 + scene_h + 4
        ink_text(d, (cx, kick_y),
                 "%d · %s · %s" % (card["no"], card["where"], card["reg"]),
                 font("bold", 10), REGIONS[card["reg"]])
        head_y = kick_y + 14
        for ln in wrap_paragraph(d, card["title"], font("serif", 18),
                                 lead_w - 2)[:2]:
            ink_text(d, (cx, head_y), ln, font("serif", 18), TYPE_BLACK)
            head_y += 19
        deck_y = head_y + 2
        for ln in wrap_paragraph(d, card["body"], font("med", 11),
                                 lead_w - 2)[:2]:
            ink_text(d, (cx, deck_y), ln, font("med", 11), TYPE_BLACK)
            deck_y += 13
        ink_text(d, (cx, deck_y + 1), card["credit"], font("bold", 8),
                 MUTED)
    leads_bottom = lead_y + 20 + scene_h + 4 + 14 + 38 + 2 + 26 + 12

    # Section header above the mini grid.
    hdr_y = leads_bottom + 4
    ink_text(d, (MARGIN, hdr_y), "MORE FROM SUNDAY · STORIES 4–21",
             font("bold", 12), ACCENT_RED)
    d.line([MARGIN, hdr_y + 16, CANVAS - MARGIN, hdr_y + 16],
           fill=ACCENT_RED, width=1)

    # Eighteen minis in a 6x3 grid, headline only, no decks.
    mini_w = (SPAN - 40) // 6
    grid_y = hdr_y + 22
    for idx, card in enumerate(MINI_CARDS):
        row, col_i = divmod(idx, 6)
        cx = MARGIN + col_i * (mini_w + 8)
        ry = grid_y + row * 100
        slug_ribbon(d, cx, ry, mini_w, 15, card["reg"], card["slug"])
        paint_mini_scene(d, cx, ry + 15, mini_w, 45, card["art"],
                         REGIONS[card["reg"]])
        number_disc(d, cx, ry + 15, mini_w, 45, card["reg"], card["no"])
        head_y = ry + 63
        lines = wrap_paragraph(d, card["title"], font("serif", 13),
                               mini_w - 2)
        assert len(lines) <= 2, (card["no"], lines)
        for ln in lines:
            ink_text(d, (cx, head_y), ln, font("serif", 13), TYPE_BLACK)
            head_y += 12
        ink_text(d, (cx, ry + 89), card["credit"], font("bold", 8), MUTED)
    grid_bottom = grid_y + 300

    # Bottom band: pin map on the left, numbered briefs on the right.
    bot_y = grid_bottom + 2
    ink_text(d, (MARGIN, bot_y), "WHERE IT HAPPENED · ALL 37 STORIES",
             font("bold", 11), ACCENT_RED)
    briefs_x = MARGIN + 464
    ink_text(d, (briefs_x, bot_y), "ALSO ON SUNDAY · STORIES 22–37",
             font("bold", 11), ACCENT_RED)
    bot_y += 15
    paint_world_map(d, MARGIN, bot_y, 452, 128)
    col_w = (CANVAS - MARGIN - briefs_x) // 2
    half = (len(SHORT_ITEMS) + 1) // 2
    for i, (reg, text_, src) in enumerate(SHORT_ITEMS):
        col_i = 0 if i < half else 1
        row = i if i < half else i - half
        by = bot_y + 4 + row * 13
        cx = briefs_x + col_i * col_w
        num = 22 + i
        d.ellipse([cx, by, cx + 13, by + 13], fill=REGIONS[reg],
                  outline=OFFWHITE, width=1)
        ink_text(d, (cx + 6.5, by + 2), str(num), font("bold", 8),
                 OFFWHITE, anchor="ma")
        lx = cx + 17
        ink_text(d, (lx, by + 2), reg, font("bold", 9), REGIONS[reg])
        lx += int(measure(d, reg, font("bold", 9))) + 5
        line = truncate_line(d, "%s (%s)" % (text_, src), font("med", 10),
                             cx + col_w - 4 - lx)
        ink_text(d, (lx, by + 2), line, font("med", 10), TYPE_BLACK)

    # DATE CHECK box: what was left out, what is not yet decided,
    # what is still only a claim.
    dc_y = bot_y + 128 + 8
    d.rectangle([MARGIN, dc_y, CANVAS - MARGIN, dc_y + 52],
                outline=ACCENT_RED, width=2)
    ink_text(d, (MARGIN + 8, dc_y + 5), "DATE CHECK", font("bold", 11),
             ACCENT_RED)
    lx = MARGIN + 104
    for j, (label, body, off) in enumerate(DATE_CHECK_ROWS):
        yy = dc_y + 4 + j * 13
        ink_text(d, (lx, yy), label, font("bold", 9), ACCENT_RED)
        bsize = 9
        while bsize > 7 and len(wrap_paragraph(
                d, body, font("med", bsize), SPAN - 118 - off)) > 1:
            bsize -= 1
        ink_text(d, (lx + off, yy), body, font("med", bsize), TYPE_BLACK)
    ink_text(d, (MARGIN, dc_y + 58),
             "Every story happened, or was first reported, on Sunday 22 "
             "November 2026. Contested claims are attributed as claims.",
             font("med", 9), MUTED)
    ink_text(d, (CANVAS - MARGIN, dc_y + 58),
             "Original drawings · POOL22-BARU v3", font("med", 9), MUTED,
             anchor="ra")
    return img


def produce():
    img = render_page()
    out_path = os.path.join(BASE_DIR, "entry.png")
    img.quantize(colors=256, method=Image.MEDIANCUT,
                 dither=Image.NONE).save(out_path, optimize=True)
    if os.path.getsize(out_path) > 160 * 1024:
        img.quantize(colors=192, method=Image.MEDIANCUT,
                     dither=Image.NONE).save(out_path, optimize=True)
    img.resize((300, 300), Image.LANCZOS).save(
        os.path.join(BASE_DIR, "entry-300.png"))


if __name__ == "__main__":
    produce()
