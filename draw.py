#!/usr/bin/env python3
"""The Daily Atlas, round 3 revision 2 — one-page atlas of Sunday
22 November 2026, rebuilt to the pixel-measured #1 spec (BEDAH-TOP1).

Renderer for @rojanon11. Changes from the first r3 build, per TOP1:
no certainty chips anywhere; a coloured D1 slug bar on every one of
the 21 pictured cards, the slug carrying the card's biggest fact;
lead headlines back to ~18px serif; lead scenes 110px with the main
subject at >=70% of scene height; mini cards deck-less (slug 15px,
full-bleed 45px scene, two-line headline, source line) — 18 minis,
21 pictured cards in total; a numbered badge (17px) on every scene
and numbered map pins for all 37 stories; an italic subdeck under
the date joining the three lead headlines; briefs in the TOP1
format (region badge + coloured region label + one line + source);
the region tally stays 16px with labels inside the segments.

Every story is drawn from POOL22-BARU v3 (events of 22 Nov 2026
only). PIL only; deterministic output.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE = 1024
MARGIN = 12
SPAN = PAGE - 2 * MARGIN

PAPER = (243, 236, 214)
BLACK = (24, 22, 19)
NAVY = (20, 38, 62)
ACCENT = (165, 40, 40)
OFFWHITE = (250, 248, 240)
MUTED = (108, 100, 86)
RULE = (199, 188, 163)

# Mid-tone region colours (TOP1 D12 palette family).
REGION_INK = {
    "MIDEAST": (156, 46, 90),
    "GLOBAL": (17, 107, 88),
    "OCEANIA": (78, 128, 45),
    "ASIA": (160, 130, 47),
    "EUROPE": (45, 88, 146),
    "AMERICAS": (181, 83, 39),
}

_fonts = {}


def font(fname, size):
    key = (fname, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(os.path.join(BASE, "fonts", fname), size)
    return _fonts[key]


def bold(size):
    return font("Archivo-Bold.ttf", size)


def med(size):
    return font("Archivo-Medium.ttf", size)


def serif(size):
    return font("PlayfairDisplay-900.ttf", size)


def width_of(d, s, fnt):
    return d.textlength(s, font=fnt)


def wrapped(d, s, fnt, maxw):
    out, line = [], ""
    for word in s.split():
        trial = (line + " " + word).strip()
        if width_of(d, trial, fnt) <= maxw or not line:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def fit_line(d, s, fnt, maxw):
    """Trim s (with an ellipsis-free hard cut at a word edge) to one line."""
    if width_of(d, s, fnt) <= maxw:
        return s
    words = s.split()
    out = ""
    for w_ in words:
        trial = (out + " " + w_).strip()
        if width_of(d, trial, fnt) > maxw:
            break
        out = trial
    return out


def put(d, xy, s, fnt, fill=BLACK, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def ray_burst(d, cx, cy, r, fill):
    pts = []
    for i in range(16):
        a = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def dash_line(d, p, q, fill, dash=6, gap=5, width=2):
    x0, y0 = p
    x1, y1 = q
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    n = int(dist // (dash + gap)) + 1
    for i in range(n):
        t0 = i * (dash + gap) / dist
        t1 = min((i * (dash + gap) + dash) / dist, 1.0)
        d.line([x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0,
                x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1], fill=fill, width=width)


def slug_bar(d, x, y, w, h, region, text):
    """D1: full-width region-coloured slug bar, white bold caps."""
    d.rectangle([x, y, x + w, y + h], fill=REGION_INK[region])
    fnt = bold(12 if h >= 20 else 10)
    put(d, (x + 6, y + (h - fnt.size) // 2 - 1),
        fit_line(d, text, fnt, w - 12), fnt, OFFWHITE)


def number_badge(d, x, y, w, h, region, num, dia=17):
    """D3: numbered badge, bottom-right of a scene."""
    bx, by = x + w - dia - 4, y + h - dia - 4
    d.ellipse([bx, by, bx + dia, by + dia], fill=REGION_INK[region],
              outline=OFFWHITE, width=2)
    put(d, (bx + dia // 2, by + dia // 2 - 5), str(num), bold(10),
        OFFWHITE, anchor="ma")


# ------------------------------------------------------------------ data
# Leads: pool events 1 (Gulf), 3 (COP31), 5 (India) — as r3.
LEAD_STORIES = [
    dict(n=1, region="MIDEAST", place="BAHRAIN · STRAIT OF HORMUZ",
         slug="BAHRAIN: 2 RADARS CLAIMED HIT",
         head="Iran claims Gulf strikes on US radars",
         deck="Missiles and drones aimed at 2 Patriot radars, Al-Riffa "
              "and Awali; a civil site burned and a tanker hit near Hormuz.",
         src="REUTERS · AP · AL JAZEERA", nfact=5, art="gulf"),
    dict(n=2, region="GLOBAL", place="ANTALYA, TÜRKIYE",
         slug="ANTALYA: FINAL TEXT TABLED",
         head="COP31 final text tabled in Antalya",
         deck="Kurum tabled the package late Saturday; objections shut "
              "03:00 GMT, approval plenary 06:00 GMT Sunday.",
         src="REUTERS · DW · ANADOLU", nfact=4, art="cop31"),
    dict(n=3, region="OCEANIA", place="WELLINGTON, NEW ZEALAND",
         slug="WELLINGTON: 720/9 — A RECORD",
         head="India declare at 720/9, a record",
         deck="Rahul 136, Pant 128: the highest Test total ever made in "
              "New Zealand. India lead NZ by 352.",
         src="IANS · AFP · ESPNCRICINFO", nfact=4, art="cricket"),
]

# Minis: the ten r3 minis (deck facts folded into the headline, D2)
# plus eight briefs converted to pictured minis (n 14-21).
MINI_STORIES = [
    dict(n=4, region="MIDEAST", slug="MAKKAH: INTERCEPT 01:42",
         head="Makkah-bound Houthi missile intercepted",
         src="MIDEAST · ANADOLU", nfact=2, art="houthi"),
    dict(n=5, region="ASIA", slug="MYANMAR: M4.1 · 95 KM",
         head="M4.1 quake in Myanmar, 95 km deep at 02:35",
         src="ASIA · NCS INDIA", nfact=3, art="quake"),
    dict(n=6, region="AMERICAS", slug="LAS VEGAS: 50 LAPS · RND 22",
         head="Las Vegas GP: 50 laps of the Strip, round 22",
         src="AMERICAS · F1", nfact=3, art="f1"),
    dict(n=7, region="AMERICAS", slug="VANDENBERG: 12:16 UTC",
         head="Falcon 9 flies NROL-136, 15th NRO batch",
         src="AMERICAS · VSFB", nfact=3, art="rocket"),
    dict(n=8, region="EUROPE", slug="ANFIELD: 16:30 UTC · MW11",
         head="Liverpool host Man United, 16:30 at Anfield",
         src="EUROPE · PREMIER LEAGUE", nfact=3, art="football"),
    dict(n=9, region="EUROPE", slug="TURIN: FINAL ±16:00 UTC",
         head="Alcaraz meets Zverev in Turin final tonight",
         src="EUROPE · ATP", nfact=2, art="tennis"),
    dict(n=10, region="AMERICAS", slug="NAPLES: KIM -18 LEADS",
         head="Kim leads by one at -18 into the $4m round",
         src="AMERICAS · LPGA / AP", nfact=3, art="golf"),
    dict(n=11, region="ASIA", slug="FUKUOKA: TWO AT 12-2",
         head="Two leaders at 12-2 into sumo's final day",
         src="ASIA · JSA", nfact=3, art="sumo"),
    dict(n=12, region="AMERICAS", slug="SEA ISLAND: 3 SHARE -9",
         head="RSM third round rained out, three share -9",
         src="AMERICAS · REUTERS", nfact=3, art="rsm"),
    dict(n=13, region="AMERICAS", slug="NFL: 11 GAMES · WEEK 12",
         head="Eleven Sunday games open NFL Week 12",
         src="AMERICAS · NFL", nfact=2, art="nfl"),
    dict(n=14, region="OCEANIA", slug="WELLINGTON: GILL 98",
         head="Gill makes 98 in India's record 720/9 total",
         src="OCEANIA · IANS", nfact=2, art="bat"),
    dict(n=15, region="OCEANIA", slug="WELLINGTON: NICHOLLS 175",
         head="Nicholls top-scores with 175 in NZ's 368",
         src="OCEANIA · AFP", nfact=2, art="bat2"),
    dict(n=16, region="MIDEAST", slug="BAHRAIN: RES. 2817 AT UN",
         head="Bahrain asks UN to enforce Resolution 2817",
         src="MIDEAST · REUTERS", nfact=2, art="un"),
    dict(n=17, region="MIDEAST", slug="KUWAIT: FIRST SINCE SEPT",
         head="Kuwait interception, its first since September",
         src="MIDEAST · KUNA", nfact=2, art="intercept"),
    dict(n=18, region="ASIA", slug="FUKUOKA: YUSHO 12-2",
         head="Yusho decider set: Onosato meets Hoshoryu",
         src="ASIA · JSA", nfact=2, art="sumo2"),
    dict(n=19, region="AMERICAS", slug="SEA ISLAND: MONDAY FINISH",
         head="RSM final round pushed to a Monday finish",
         src="AMERICAS · PGA TOUR", nfact=2, art="golf2"),
    dict(n=20, region="AMERICAS", slug="NAPLES: THITIKUL -17",
         head="Thitikul one back at -17 at Tiburon",
         src="AMERICAS · LPGA / AP", nfact=2, art="golf3"),
    dict(n=21, region="AMERICAS", slug="LZ-4: BOOSTER B1097 BACK",
         head="Falcon booster B1097 lands back at Zone 4",
         src="AMERICAS · SPACEX", nfact=2, art="rocket2"),
]

FIGURE_STRIP = [
    ("2", "PATRIOT RADARS CLAIMED HIT · BAHRAIN"),
    ("06:00", "GMT - COP31 APPROVAL PLENARY"),
    ("720/9", "INDIA DECLARED · WELLINGTON"),
    ("352", "INDIA'S LEAD OVER NEW ZEALAND"),
    ("M4.1", "MYANMAR QUAKE · 95 KM DEEP"),
    ("$4M", "LPGA WINNER'S PRIZE · NAPLES"),
]

# (region, one-line text, source) — 16 briefs, TOP1 D5 format.
BRIEF_ITEMS = [
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

LEFT_OUT = ("Lviv strikes (20 Nov) · Peru M6.9 (20/21 Nov) · Sparta II "
            "(21 Nov) · Riyadh missiles (21 Nov) · France march 82,500 "
            "(21 Nov) · Berlin Coalition (19 Nov) · ICJ ruling (19 Nov) "
            "· Geneva robot deal (21 Nov)")
NOT_YET = ("COP31 final adoption - vote still to come · Liverpool v "
           "Man Utd result - 16:30 UTC kick-off · ATP Turin final "
           "result - played Sunday evening")
UNCONFIRMED = ("IRGC claim: 2 Patriot radars destroyed - no independent "
               "confirmation · Houthi interception claim over Makkah - "
               "coalition account only")

# Numbered pin spots (lon, lat) for ALL 37 stories: cards 1-21, briefs 22-37.
PIN_SPOTS = {
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


# ------------------------------------------------------------- lead art
# Flat vector, one sky gradient, <=3 large elements, subject >=70%.
def art_gulf(d, x, y, w, h):
    for i in range(h):
        t = i / max(h - 1, 1)
        d.line([x, y + i, x + w, y + i],
               fill=(24 + int(26 * t), 62 + int(44 * t), 128 + int(56 * t)))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(16, 110, 120))
    # giant dish: bowl 118 wide, mast to the sea (subject ~84px tall)
    cx, top = x + 96, y + 10
    d.line([cx, y + h - 20, cx, top + 40], fill=(225, 230, 235), width=6)
    d.pieslice([cx - 59, top - 6, cx + 59, top + 56], start=0, end=180,
               fill=(232, 236, 240))
    d.ellipse([cx - 59, top - 6, cx + 59, top + 9], fill=(198, 208, 218))
    d.line([cx, top + 26, cx + 50, top + 4], fill=(240, 244, 248), width=3)
    d.ellipse([cx + 46, top, cx + 56, top + 10], fill=(245, 200, 70))
    # one huge burst field on the right (80px tall = 73% of scene)
    d.ellipse([x + 208, y + 14, x + 304, y + 94], fill=(232, 92, 30))
    ray_burst(d, x + 256, y + 54, 30, (248, 178, 52))
    ray_burst(d, x + 256, y + 54, 15, (250, 226, 130))
    # tanker silhouette, low right
    tx, ty = x + w - 100, y + h - 18
    d.polygon([(tx, ty), (tx + 84, ty), (tx + 74, ty + 8), (tx + 8, ty + 8)],
              fill=(10, 16, 24))
    d.rectangle([tx + 54, ty - 8, tx + 68, ty], fill=(10, 16, 24))


def art_cop31(d, x, y, w, h):
    for i in range(h):
        t = i / max(h - 1, 1)
        d.line([x, y + i, x + w, y + i],
               fill=(228 - int(36 * t), 126 - int(18 * t), 46 + int(26 * t)))
    # giant globe: diameter 94px = 85% of the 110px scene
    cx, cy, r = x + w // 2, y + h // 2 - 2, 47
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(28, 110, 168))
    d.ellipse([cx - r + 8, cy - r + 11, cx - 5, cy - 6], fill=(52, 150, 84))
    d.ellipse([cx + 6, cy - 2, cx + 35, cy + 27], fill=(52, 150, 84))
    d.ellipse([cx - 32, cy + 13, cx - 6, cy + 35], fill=(64, 160, 92))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(240, 244, 248), width=3)
    # plenary hall silhouettes along the base
    d.rectangle([x + 10, y + h - 18, x + 88, y + h - 11], fill=(70, 44, 30))
    d.polygon([(x + 10, y + h - 18), (x + 88, y + h - 18), (x + 49, y + h - 27)],
              fill=(70, 44, 30))
    d.rectangle([x + w - 88, y + h - 18, x + w - 10, y + h - 11], fill=(70, 44, 30))
    d.polygon([(x + w - 88, y + h - 18), (x + w - 10, y + h - 18),
               (x + w - 49, y + h - 27)], fill=(70, 44, 30))


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(36, 128, 52))
    d.ellipse([x + 5, y + 3, x + w - 5, y + h - 2], fill=(24, 96, 44))
    d.ellipse([x + 13, y + 8, x + w - 13, y + h - 6], fill=(238, 234, 222))
    d.ellipse([x + 23, y + 13, x + w - 23, y + h - 11], fill=(52, 156, 62))
    d.ellipse([x + 37, y + 18, x + w - 37, y + h - 16], fill=(66, 170, 72))
    cx = x + w // 2
    d.rectangle([cx - 13, y + 20, cx + 13, y + h - 18], fill=(219, 198, 148))
    for sx in (cx - 8, cx + 4):
        d.rectangle([sx, y + 25, sx + 4, y + 35], fill=(245, 205, 60))
        d.rectangle([sx, y + h - 37, sx + 4, y + h - 27], fill=(245, 205, 60))
    # giant ball, top right (44px)
    d.ellipse([x + w - 72, y + 14, x + w - 28, y + 58], fill=(196, 36, 48))
    d.arc([x + w - 64, y + 18, x + w - 36, y + 54], start=300, end=130,
          fill=(248, 242, 230), width=2)


LEAD_ART = {"gulf": art_gulf, "cop31": art_cop31, "cricket": art_cricket}


# ------------------------------------------------------------- mini art
# Full-bleed colour field, 1-3 large flat elements, no small labels.
def mini_scene(d, x, y, w, h, kind):
    if kind == "houthi":
        d.rectangle([x, y, x + w, y + h], fill=(176, 52, 44))
        dash_line(d, (x + 6, y + h - 6), (x + 96, y + 8), (250, 220, 150), width=4)
        ray_burst(d, x + 112, y + 13, 14, (250, 196, 70))
        d.rectangle([x + 128, y + h - 15, x + w - 4, y + h - 5], fill=(120, 30, 26))
    elif kind == "quake":
        d.rectangle([x, y, x + w, y + h], fill=(110, 76, 160))
        pts, mid = [], y + h // 2
        for i in range(46):
            amp = 3 + 16 * abs(math.sin(i * 0.55)) * (0.4 + 0.6 * abs(math.sin(i * 0.13)))
            pts.append((x + 5 + i * 3.3, mid + (amp if i % 2 else -amp)))
        d.line(pts, fill=(250, 246, 232), width=3)
    elif kind == "f1":
        d.rectangle([x, y, x + w, y + h], fill=(178, 30, 42))
        d.arc([x + 2, y, x + 128, y + h + 20], start=180, end=330,
              fill=(248, 244, 238), width=5)
        d.polygon([(x + 104, y + 13), (x + 142, y + 13), (x + 150, y + 25),
                   (x + 112, y + 25)], fill=(16, 16, 20))
        d.rectangle([x + 116, y + 6, x + 130, y + 13], fill=(230, 230, 230))
        d.ellipse([x + 110, y + 23, x + 120, y + 33], fill=(16, 16, 20))
        d.ellipse([x + 136, y + 23, x + 146, y + 33], fill=(16, 16, 20))
    elif kind in ("rocket", "rocket2"):
        d.rectangle([x, y, x + w, y + h], fill=(30, 84, 160))
        rx = x + (44 if kind == "rocket" else 108)
        d.polygon([(rx, y + 1), (rx + 11, y + 13), (rx - 11, y + 13)], fill=OFFWHITE)
        d.rectangle([rx - 11, y + 13, rx + 11, y + h - 9], fill=OFFWHITE)
        d.rectangle([rx - 4, y + 19, rx + 4, y + 27], fill=(30, 84, 160))
        d.polygon([(rx - 11, y + h - 15), (rx - 21, y + h - 3), (rx - 11, y + h - 3)],
                  fill=ACCENT)
        d.polygon([(rx + 11, y + h - 15), (rx + 21, y + h - 3), (rx + 11, y + h - 3)],
                  fill=ACCENT)
        ray_burst(d, rx, y + h - 2, 8, (250, 178, 60))
    elif kind == "football":
        d.rectangle([x, y, x + w, y + h], fill=(40, 138, 58))
        d.rectangle([x + 5, y + 5, x + w - 5, y + h - 5],
                    outline=(244, 246, 240), width=2)
        d.line([x + w // 2, y + 5, x + w // 2, y + h - 5],
               fill=(244, 246, 240), width=2)
        d.ellipse([x + w // 2 - 12, y + h // 2 - 12, x + w // 2 + 12,
                   y + h // 2 + 12], outline=(244, 246, 240), width=2)
        d.ellipse([x + w // 2 + 28, y + h // 2 - 6, x + w // 2 + 40,
                   y + h // 2 + 6], fill=(248, 248, 248))
    elif kind == "tennis":
        d.rectangle([x, y, x + w, y + h], fill=(36, 104, 168))
        d.rectangle([x + 8, y + 6, x + 122, y + h - 6],
                    outline=(244, 246, 240), width=2)
        d.line([x + 65, y + 6, x + 65, y + h - 6], fill=(16, 16, 18), width=4)
        d.line([x + 8, y + h // 2, x + 122, y + h // 2],
               fill=(244, 246, 240), width=2)
        d.ellipse([x + 96, y + 8, x + 112, y + 24], fill=(216, 226, 60))
        d.ellipse([x + 138, y + h - 18, x + 150, y + h - 6], fill=(216, 226, 60))
    elif kind in ("golf", "golf2", "golf3"):
        base = {"golf": (52, 146, 66), "golf2": (44, 128, 92),
                "golf3": (66, 156, 60)}[kind]
        d.rectangle([x, y, x + w, y + h], fill=base)
        d.ellipse([x + 6, y + h - 17, x + 132, y + h - 2], fill=(92, 180, 96))
        fx = x + (148 if kind != "golf3" else 40)
        d.line([fx, y + 4, fx, y + h - 4], fill=OFFWHITE, width=3)
        d.polygon([(fx, y + 4), (fx + 17, y + 10), (fx, y + 16)], fill=ACCENT)
        d.ellipse([fx - 6, y + h - 9, fx + 6, y + h - 3], fill=(24, 24, 24))
        d.ellipse([x + 26, y + 9, x + 34, y + 17], fill=(248, 248, 248))
    elif kind in ("sumo", "sumo2"):
        d.rectangle([x, y, x + w, y + h], fill=(214, 168, 96))
        d.ellipse([x + 42, y + 1, x + 118, y + h - 1], outline=OFFWHITE, width=4)
        d.ellipse([x + 62, y + 11, x + 82, y + 31], fill=(46, 38, 34))
        d.ellipse([x + 80, y + 11, x + 100, y + 31],
                  fill=(66, 54, 48) if kind == "sumo" else (96, 60, 40))
        d.rectangle([x + 66, y + 28, x + 96, y + 36], fill=(90, 40, 90))
    elif kind == "rsm":
        d.rectangle([x, y, x + w, y + h], fill=(42, 92, 140))
        for i in range(3):
            bx = x + 18 + i * 42
            d.rectangle([bx, y + 14, bx + 26, y + h - 3], fill=(240, 236, 220))
        put(d, (x + w // 2, y + 1), "-9", bold(14), OFFWHITE, anchor="ma")
    elif kind == "nfl":
        d.rectangle([x, y, x + w, y + h], fill=(40, 116, 54))
        for i in range(6):
            lx = x + 10 + i * 26
            d.line([lx, y + 4, lx, y + h - 4], fill=(244, 246, 240), width=2)
        d.ellipse([x + w // 2 - 16, y + h // 2 - 9, x + w // 2 + 16,
                   y + h // 2 + 9], fill=(158, 96, 44))
        d.line([x + w // 2 - 8, y + h // 2, x + w // 2 + 8, y + h // 2],
               fill=OFFWHITE, width=2)
    elif kind in ("bat", "bat2"):
        d.rectangle([x, y, x + w, y + h],
                    fill=(30, 110, 150) if kind == "bat" else (150, 84, 40))
        # one giant bat + ball
        d.polygon([(x + 30, y + h - 4), (x + 52, y + h - 4), (x + 96, y + 6),
                   (x + 82, y + 2)], fill=(226, 198, 148))
        d.ellipse([x + 108, y + 22, x + 140, y + 44], fill=(196, 36, 48))
    elif kind == "un":
        d.rectangle([x, y, x + w, y + h], fill=(52, 120, 170))
        d.rectangle([x + 18, y + 12, x + w - 18, y + h - 4], fill=(238, 240, 244))
        for i in range(5):
            cx = x + 30 + i * 22
            d.rectangle([cx, y + 18, cx + 8, y + h - 10], fill=(52, 120, 170))
        d.polygon([(x + 12, y + 12), (x + w - 12, y + 12), (x + w // 2, y + 2)],
                  fill=(238, 240, 244))
    elif kind == "intercept":
        d.rectangle([x, y, x + w, y + h], fill=(96, 60, 130))
        dash_line(d, (x + w - 8, y + 4), (x + 60, y + h - 10),
                  (250, 220, 150), width=4)
        ray_burst(d, x + 48, y + h - 14, 15, (250, 196, 70))
        d.rectangle([x + 8, y + 6, x + 44, y + 16], fill=(220, 224, 230))


# ------------------------------------------------------------------ map
def paint_map(d, x, y, w, h):
    from mapdata import WORLD
    d.rectangle([x, y, x + w, y + h], fill=(205, 225, 235))
    mx0, my0, mw, mh = x + 6, y + 6, w - 12, h - 12

    def project(lon, lat):
        lat = max(-60.0, min(85.0, lat))
        return (mx0 + (lon + 180.0) / 360.0 * mw,
                my0 + (85.0 - lat) / 145.0 * mh)

    for polys in WORLD.values():
        for poly in polys.split("|"):
            pts = []
            for pair in poly.split(","):
                if ":" not in pair:
                    continue
                lo, la = pair.split(":")
                pts.append(project(float(lo), float(la)))
            if len(pts) >= 3:
                d.polygon(pts, fill=(222, 205, 180))
    region_of = {}
    for c in LEAD_STORIES + MINI_STORIES:
        region_of[c["n"]] = c["region"]
    for i, (reg, _t, _s) in enumerate(BRIEF_ITEMS):
        region_of[22 + i] = reg
    for num in range(1, 38):
        lon, lat = PIN_SPOTS[num]
        px, py = project(lon, lat)
        dia = 15 if num <= 21 else 13
        d.ellipse([px - dia / 2, py - dia / 2, px + dia / 2, py + dia / 2],
                  fill=REGION_INK[region_of[num]], outline=OFFWHITE, width=1)
        put(d, (px, py - 4), str(num), bold(8), OFFWHITE, anchor="ma")


# ----------------------------------------------------------------- build
def render():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)

    # paper-name bar (name text 12px, well under the 20px cap)
    d.rectangle([0, 0, PAGE, 22], fill=NAVY)
    put(d, (MARGIN, 4), "THE DAILY ATLAS · THE WORLD IN ONE DAY", bold(12), OFFWHITE)
    total = len(LEAD_STORIES) + len(MINI_STORIES) + len(BRIEF_ITEMS)
    assert total == 37, total
    put(d, (PAGE - MARGIN, 4), f"{total} STORIES · 6 REGIONS · ALL FROM TODAY",
        bold(12), OFFWHITE, anchor="ra")

    # the DATE is the masthead: own layer, ink 958x88
    date_layer = Image.new("RGBA", (1750, 160), (0, 0, 0, 0))
    ImageDraw.Draw(date_layer).text((6, 6), "SUNDAY 22 NOVEMBER 2026",
                                    font=serif(118), fill=BLACK + (255,))
    layer = date_layer.crop(date_layer.getbbox()).resize((958, 88), Image.LANCZOS)
    img.paste(layer, (MARGIN + (SPAN - layer.size[0]) // 2, 26), layer)
    d = ImageDraw.Draw(img)
    print(f"MASTHEAD ink {layer.size[0]}x{layer.size[1]}")

    # D4 subdeck: italic serif ~19px, the three lead headlines joined.
    sub = " · ".join(c["head"] for c in LEAD_STORIES)
    size = 19
    while size > 14 and width_of(d, sub, serif(size)) > SPAN - 8:
        size -= 1
    sub_layer = Image.new("RGBA", (SPAN + 80, 44), (0, 0, 0, 0))
    ImageDraw.Draw(sub_layer).text((30, 4), sub, font=serif(size),
                                   fill=(70, 52, 30, 255))
    sub_layer = sub_layer.transform(sub_layer.size, Image.AFFINE,
                                    (1, 0.22, -10, 0, 1, 0), resample=Image.BICUBIC)
    bb = sub_layer.getbbox()
    sub_layer = sub_layer.crop(bb)
    img.paste(sub_layer, (MARGIN + (SPAN - sub_layer.size[0]) // 2, 118), sub_layer)
    d = ImageDraw.Draw(img)
    print(f"SUBDECK serif {size}px ink {sub_layer.size[0]}x{sub_layer.size[1]}")

    # red figure strip (digits keep the r2 40px ink)
    fig_y = 148
    d.line([MARGIN, fig_y - 5, PAGE - MARGIN, fig_y - 5], fill=ACCENT, width=2)
    segw = SPAN // 6
    probe = Image.new("L", (300, 90), 0)
    ImageDraw.Draw(probe).text((4, 2), "720/9", font=bold(50), fill=255)
    bb = probe.getbbox()
    digit_ink = bb[3] - bb[1]
    for i, (num, cap) in enumerate(FIGURE_STRIP):
        cx = MARGIN + i * segw
        put(d, (cx + 2, fig_y), num, bold(50), ACCENT)
        put(d, (cx + 2, fig_y + 54),
            fit_line(d, cap, bold(8), segw - 8), bold(8), BLACK)
    print(f"FIGURES digit ink {digit_ink}px, strip top y={fig_y}")

    # region tally bar: 16px, labels inside segments, widths proportional
    tally = {}
    for c in LEAD_STORIES + MINI_STORIES:
        tally[c["region"]] = tally.get(c["region"], 0) + 1
    for reg, _t, _s in BRIEF_ITEMS:
        tally[reg] = tally.get(reg, 0) + 1
    tally_sum = sum(tally.values())
    assert tally_sum == total, (tally_sum, total)
    tally_y, tally_h = 218, 16
    order = ["MIDEAST", "GLOBAL", "OCEANIA", "ASIA", "EUROPE", "AMERICAS"]
    tx = MARGIN
    for reg in order:
        seg_w = int(round(SPAN * tally[reg] / tally_sum))
        if reg == order[-1]:
            seg_w = MARGIN + SPAN - tx
        d.rectangle([tx, tally_y, tx + seg_w, tally_y + tally_h],
                    fill=REGION_INK[reg])
        label = f"{reg} {tally[reg]}"
        if width_of(d, label, bold(9)) + 8 <= seg_w:
            put(d, (tx + seg_w // 2, tally_y + 4), label, bold(9),
                OFFWHITE, anchor="ma")
        tx += seg_w
    print(f"TALLY {tally} sum={tally_sum} total={total}")

    # three leads: slug 20px, scene 110px, caption, headline ~18px pitch 19
    lead_y, scene_h = 242, 110
    lead_w = (SPAN - 16) // 3
    for i, c in enumerate(LEAD_STORIES):
        cx = MARGIN + i * (lead_w + 8)
        slug_bar(d, cx, lead_y, lead_w, 20, c["region"], c["slug"])
        LEAD_ART[c["art"]](d, cx, lead_y + 20, lead_w, scene_h)
        number_badge(d, cx, lead_y + 20, lead_w, scene_h, c["region"], c["n"])
        ky = lead_y + 20 + scene_h + 4
        put(d, (cx, ky), f"{c['n']} · {c['place']} · {c['region']}",
            bold(10), REGION_INK[c["region"]])
        hy = ky + 14
        for ln in wrapped(d, c["head"], serif(18), lead_w - 2)[:2]:
            put(d, (cx, hy), ln, serif(18), BLACK)
            hy += 19
        dy = hy + 2
        for ln in wrapped(d, c["deck"], med(11), lead_w - 2)[:2]:
            put(d, (cx, dy), ln, med(11), BLACK)
            dy += 13
        put(d, (cx, dy + 1), c["src"], bold(8), MUTED)
    lead_end = lead_y + 20 + scene_h + 4 + 14 + 38 + 2 + 26 + 12
    print(f"LEADS slug 20px scene {scene_h}px headline 18px, ends ~{lead_end}")

    # section header for the mini grid
    hdr_y = lead_end + 4
    put(d, (MARGIN, hdr_y), "MORE FROM SUNDAY · STORIES 4–21", bold(12), ACCENT)
    d.line([MARGIN, hdr_y + 16, PAGE - MARGIN, hdr_y + 16], fill=ACCENT, width=1)

    # mini cards: 6 cols x 3 rows, deck-less (D2)
    mini_w = (SPAN - 40) // 6
    grid_y = hdr_y + 22
    row_pitch = 100
    for idx, c in enumerate(MINI_STORIES):
        r_i, i = divmod(idx, 6)
        cx = MARGIN + i * (mini_w + 8)
        ry = grid_y + r_i * row_pitch
        slug_bar(d, cx, ry, mini_w, 15, c["region"], c["slug"])
        mini_scene(d, cx, ry + 15, mini_w, 45, c["art"])
        number_badge(d, cx, ry + 15, mini_w, 45, c["region"], c["n"])
        hy = ry + 63
        head_lines = wrapped(d, c["head"], serif(13), mini_w - 2)
        assert len(head_lines) <= 2, (c["n"], head_lines)
        for ln in head_lines:
            put(d, (cx, hy), ln, serif(13), BLACK)
            hy += 12
        put(d, (cx, ry + 89), c["src"], bold(8), MUTED)
    grid_end = grid_y + 3 * row_pitch
    print(f"MINIS slug 15px scene 45px headline 13px, grid ends {grid_end}")

    # bottom zone: light map left, briefs right (D5 format)
    bot_y = grid_end + 2
    put(d, (MARGIN, bot_y), "WHERE IT HAPPENED · ALL 37 STORIES", bold(11), ACCENT)
    bx0 = MARGIN + 464
    put(d, (bx0, bot_y), f"ALSO ON SUNDAY · STORIES 22–37", bold(11), ACCENT)
    bot_y += 15
    bot_h = 128
    paint_map(d, MARGIN, bot_y, 452, bot_h)
    bw = PAGE - MARGIN - bx0
    col_w = bw // 2
    half = (len(BRIEF_ITEMS) + 1) // 2
    for i, (reg, txt, src) in enumerate(BRIEF_ITEMS):
        col = 0 if i < half else 1
        row = i if i < half else i - half
        by = bot_y + 4 + row * 13
        cx = bx0 + col * col_w
        num = 22 + i
        d.ellipse([cx, by, cx + 13, by + 13], fill=REGION_INK[reg],
                  outline=OFFWHITE, width=1)
        put(d, (cx + 6.5, by + 2), str(num), bold(8), OFFWHITE, anchor="ma")
        lx = cx + 17
        lab = reg
        put(d, (lx, by + 2), lab, bold(9), REGION_INK[reg])
        lx += int(width_of(d, lab, bold(9))) + 5
        line = fit_line(d, f"{txt} ({src})", med(10), cx + col_w - 4 - lx)
        put(d, (lx, by + 2), line, med(10), BLACK)

    # DATE CHECK: three parts, content unchanged from r3, no chips
    dc_y = bot_y + bot_h + 8
    d.rectangle([MARGIN, dc_y, PAGE - MARGIN, dc_y + 52], outline=ACCENT, width=2)
    put(d, (MARGIN + 8, dc_y + 5), "DATE CHECK", bold(11), ACCENT)
    lx = MARGIN + 104
    put(d, (lx, dc_y + 4), "LEFT OUT", bold(9), ACCENT)
    for ln in wrapped(d, LEFT_OUT, med(9), SPAN - 118)[:1]:
        put(d, (lx + 52, dc_y + 4), ln, med(9), BLACK)
    put(d, (lx, dc_y + 17), "NOT YET", bold(9), ACCENT)
    for ln in wrapped(d, NOT_YET, med(9), SPAN - 118)[:1]:
        put(d, (lx + 52, dc_y + 17), ln, med(9), BLACK)
    put(d, (lx, dc_y + 30), "UNCONFIRMED", bold(9), ACCENT)
    for ln in wrapped(d, UNCONFIRMED, med(9), SPAN - 118)[:1]:
        put(d, (lx + 78, dc_y + 30), ln, med(9), BLACK)
    put(d, (MARGIN, dc_y + 58),
        "Every story happened, or was first reported, on Sunday 22 "
        "November 2026. Contested claims are attributed as claims.",
        med(9), MUTED)
    put(d, (PAGE - MARGIN, dc_y + 58), "Original drawings · POOL22-BARU v3",
        med(9), MUTED, anchor="ra")

    # save (palette-compressed, sharp text)
    q = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
    out = os.path.join(BASE, "entry.png")
    q.save(out, optimize=True)
    size = os.path.getsize(out)
    if size > 160 * 1024:
        img.quantize(colors=192, method=Image.MEDIANCUT,
                     dither=Image.NONE).save(out, optimize=True)
        size = os.path.getsize(out)
    img.resize((300, 300), Image.LANCZOS).save(os.path.join(BASE, "entry-300.png"))
    print(f"entry.png bytes: {size}")

    cards = LEAD_STORIES + MINI_STORIES
    avg = sum(c["nfact"] for c in cards) / len(cards)
    slug_fact = sum(1 for c in MINI_STORIES
                    if any(ch.isdigit() for ch in c["slug"]))
    print(f"AUDIT pictured={len(cards)} avg_facts={avg:.2f} "
          f"stories={total} briefs={len(BRIEF_ITEMS)} tally_sum={tally_sum} "
          f"slug_fact_minis={slug_fact}/{len(MINI_STORIES)} "
          f"badges={len(cards)}/{len(cards)} pins={len(PIN_SPOTS)}/{total}")


if __name__ == "__main__":
    render()
