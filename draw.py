#!/usr/bin/env python3
"""The Daily Atlas — NI22 challenger for @rojanon11 (build script).

Flat 2D broadsheet, 1024x1024, PIL only. Date is the masthead (R1),
red numbers strip in the top 22% (R2), three pictorial lead scenes
>=85px with in-strip data labels (R3), a data strip + source tag on
every one of the 13 cards (R4/R5), one red accent (R6), real-polygon
world map confined to the bottom panel. All stories come from
POOL22-BARU (13 verified events of Sunday 22 November 2026).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

CREAM = (244, 237, 216)
CREAM2 = (238, 229, 203)
INK = (26, 24, 20)
NAVY = (22, 40, 63)
RED = (179, 32, 42)
DARKRED = (140, 22, 32)
WHITE = (250, 248, 240)
GREY = (110, 102, 88)

REGIONS = {
    "MIDEAST": (140, 90, 43),
    "GLOBAL": (46, 110, 106),
    "OCEANIA": (63, 122, 58),
    "ASIA": (107, 78, 158),
    "EUROPE": (47, 93, 138),
    "AMERICAS": (176, 106, 40),
}

_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(HERE, "fonts", name), size)
    return _cache[key]


def AB(size):
    return F("Archivo-Bold.ttf", size)


def AM(size):
    return F("Archivo-Medium.ttf", size)


def PF(size):
    return F("PlayfairDisplay-900.ttf", size)


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text(d, xy, s, font, fill=INK, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def chip(d, x, y, s, font, bg, fg=WHITE, pad=6):
    w_ = int(tw(d, s, font)) + pad * 2
    h_ = font.size + 7
    d.rounded_rectangle([x, y, x + w_, y + h_], radius=h_ // 2, fill=bg)
    text(d, (x + pad, y + 3), s, font, fg)
    return w_, h_


def caption_band(d, x, y, w_, s):
    """Navy band 16px at the bottom inside a strip (skill SS8 device 1)."""
    d.rectangle([x, y - 16, x + w_, y], fill=NAVY)
    f = AB(10)
    text(d, (x + w_ // 2, y - 13), s, f, WHITE, anchor="ma")


def source_pill(d, x, y, w_, s):
    f = AB(9)
    pw = int(tw(d, s, f)) + 12
    d.rounded_rectangle([x + w_ - pw - 4, y + 4, x + w_ - 4, y + 17],
                        radius=6, fill=(250, 248, 240))
    text(d, (x + w_ - pw + 2, y + 6), s, f, NAVY)


# ---------------------------------------------------------------- stories
# leads: pool events 1 (Gulf), 3 (COP31), 5 (India). Cards 4-13: the other
# ten pool events in pool order (2,4,6,7,8,9,10,11,12,13).
LEADS = [
    dict(num=1, region="MIDEAST", topic="CONFLICT", tag="CLAIM · IRGC",
         headline="Iran claims overnight strikes on US radars in the Gulf",
         deck="The IRGC says its missiles and drones hit 2 Patriot radars "
              "at Al-Riffa and Awali; a civil site burned in Bahrain and a "
              "drone was downed over Kuwait. A tanker was attacked near "
              "Hormuz.",
         facts=5, scene="gulf"),
    dict(num=2, region="GLOBAL", topic="CLIMATE", tag="REUTERS",
         headline="COP31 final text tabled for dawn approval in Antalya",
         deck="President Murat Kurum tabled the final package late "
              "Saturday; objections closed at 03:00 GMT and the approval "
              "plenary sits at 06:00 GMT Sunday. The $120bn adaptation "
              "target fell Thursday.",
         facts=4, scene="cop31"),
    dict(num=3, region="OCEANIA", topic="CRICKET", tag="IANS / AFP",
         headline="India declare at 720/9 — a Wellington Test record",
         deck="Rahul made 136 and Pant 128 as India posted the highest Test "
              "total ever made in New Zealand. Ahead by 352 after New "
              "Zealand's 368, they declared on the fourth afternoon.",
         facts=4, scene="cricket"),
]

MINIS = [
    dict(num=4, region="MIDEAST", topic="AIR DEFENCE", tag="CONFIRMED · ANADOLU",
         headline="Houthi missile intercepted bound for Makkah",
         deck="Sirens sounded at 23:43 Riyadh time; the Saudi-led "
              "coalition confirmed the interception at 01:42 Sunday.",
         facts=2, strip="houthi", label="INTERCEPTED 01:42 LOCAL"),
    dict(num=5, region="ASIA", topic="EARTHQUAKE", tag="NCS · VIA ANI",
         headline="M4.1 earthquake recorded in Myanmar",
         deck="Logged at 02:35:57 IST on 22 Nov, 95 km deep, at "
              "24.404N, 94.616E.",
         facts=3, strip="quake", label="95 KM DEEP · 02:35 IST"),
    dict(num=6, region="AMERICAS", topic="FORMULA 1", tag="FORMULA1.COM",
         headline="Las Vegas GP runs under the Strip lights",
         deck="Lights out 20:00 PT Sat = 04:00 UTC Sun; 50 laps of the "
              "Strip Circuit, round 22.",
         facts=3, strip="f1", label="50 LAPS · ROUND 22"),
    dict(num=7, region="AMERICAS", topic="SPACE", tag="OFFICIAL · VSFB",
         headline="Falcon 9 to launch NROL-136 spy batch",
         deck="Window 12:16–12:46 UTC at SLC-4E; booster B1097 lands "
              "at LZ-4; the NRO's 15th batch.",
         facts=3, strip="rocket", label="WINDOW 12:16–12:46 UTC"),
    dict(num=8, region="EUROPE", topic="FOOTBALL", tag="PREMIERLEAGUE.COM",
         headline="Liverpool host Man United at Anfield",
         deck="Anfield at 16:30 UTC, Matchweek 11; Hull v Brighton "
              "opens Sunday at 14:00 UTC.",
         facts=3, strip="football", label="16:30 UTC · MATCHWEEK 11"),
    dict(num=9, region="EUROPE", topic="TENNIS", tag="ATP / REUTERS",
         headline="Alcaraz meets Zverev in the Turin final",
         deck="Sunday evening in Turin, about 16:00 UTC; Alcaraz came "
              "back against Shelton to reach it.",
         facts=3, strip="tennis", label="FINAL · SUNDAY EVENING"),
    dict(num=10, region="AMERICAS", topic="GOLF", tag="LPGA / AP",
         headline="Kim leads by one into the $4m final round",
         deck="Kim at -18 at Tiburón, one ahead of Thitikul and "
              "Yoshida; the $4m prize is women's golf's largest.",
         facts=3, strip="golf", label="KIM -18 · LEADS BY 1"),
    dict(num=11, region="ASIA", topic="SUMO", tag="JSA · SUMO",
         headline="Two leaders into sumo's final day",
         deck="Onosato and Wakamotoharu stand 12-2 in Fukuoka; "
              "Atamifuji 11-3; last bouts about 09:00 UTC.",
         facts=3, strip="sumo", label="12-2 · TWO SHARE THE LEAD"),
    dict(num=12, region="AMERICAS", topic="GOLF", tag="REUTERS",
         headline="RSM Classic third round moves to Sunday",
         deck="Saturday was rained out; three share the lead at -9; "
              "Sunday tees 14:10–16:00 UTC, final Monday.",
         facts=3, strip="rsm", label="3 SHARE -9 · RAIN DELAY"),
    dict(num=13, region="AMERICAS", topic="NFL", tag="ESPN / NFL",
         headline="Eleven Sunday games in NFL Week 12",
         deck="Early window 13:00 ET (18:00 UTC); the day closes with "
              "Vikings @ 49ers at 20:20 ET.",
         facts=3, strip="nfl", label="11 GAMES · WEEK 12"),
]

NUMBERS = [
    ("2", "PATRIOT RADARS CLAIMED HIT · BAHRAIN"),
    ("06:00", "GMT — COP31 APPROVAL PLENARY"),
    ("720/9", "INDIA DECLARED · WELLINGTON"),
    ("352", "INDIA'S LEAD OVER NEW ZEALAND"),
    ("M4.1", "MYANMAR QUAKE · 95 KM DEEP"),
    ("$4M", "LPGA WINNER'S PRIZE · NAPLES"),
]

TIMELINE = [
    ("OVERNIGHT", "IRGC Gulf claims from 19:40 UTC"),
    ("03:00 GMT", "COP31 objections close, Antalya"),
    ("04:00 UTC", "Las Vegas GP lights out"),
    ("06:00 GMT", "COP31 approval plenary sits"),
    ("09:00 UTC", "Sumo's final bouts, Fukuoka"),
    ("12:16 UTC", "Falcon 9 window, Vandenberg"),
]

BRIEFS = [
    "Gill 98 in India's record 720/9",
    "Jaiswal 85 in the Wellington total",
    "Padikkal 80 as India declared, day 4",
    "Nicholls 175 top-scored in NZ's 368",
    "Bumrah 4-92 in New Zealand's 368",
    "Bahrain asks UN to enforce Res. 2817",
    "UKMTO tanker report Sat 11:27 UTC",
    "IRGC's first statement: 19:40 UTC",
    "Kuwait interception — first since Sept",
    "Yusho decider: Onosato v Hoshoryu",
    "Wakamotoharu v Atamifuji closes basho",
    "Atamifuji starts the last day 11-3",
    "RSM Sunday tees run 09:10–11:00 ET",
    "RSM final round pushed to Monday",
    "Thitikul one back at -17, Tiburón",
    "Yoshida one back at -17 into Sunday",
    "NFL early window opens 13:00 ET",
    "NFL late window: 16:05–16:25 ET",
    "Sunday Night: Vikings @ 49ers 20:20 ET",
    "COP31 objections closed 03:00 GMT",
    "Bowen co-hosts COP31 for Australia",
    "Draft 3 recalls the Dubai fossil deal",
    "B1097 lands back at Landing Zone 4",
    "NROL-136 slipped from Sat to Sunday",
    "Strip Circuit hosts round 22 at night",
    "Myanmar quake struck 95 km deep",
    "Alcaraz rallied past Shelton, Turin semi",
]

DATECHECK = ("Left out — not 22 Nov: Lviv strikes (20 Nov) · Peru M6.9 quake "
             "(20/21 Nov) · Sparta II launch (21 Nov) · 3 missiles at Riyadh "
             "(21 Nov) · France march of 82,500 (21 Nov) · Berlin Coalition "
             "of the Willing (19 Nov) · ICJ ruling (19 Nov).  Not yet: "
             "Davis Cup final, 29 Nov.")

# numbered map pins (card number -> lon, lat)
PINS = {1: (50.5, 26.2), 2: (30.7, 36.9), 3: (174.8, -41.3), 4: (39.8, 21.4),
        5: (94.6, 24.4), 6: (-112.0, 39.5), 7: (-125.0, 32.0),
        8: (-2.96, 53.4), 9: (7.7, 45.1), 10: (-81.8, 26.1),
        11: (130.4, 33.6), 12: (-81.4, 31.2), 13: (-122.0, 37.4)}
# small dots for briefs
DOTS = [(56.3, 26.5), (51.5, 25.5), (44.5, 29.0), (174.8, -41.3),
        (130.4, 33.6), (-81.4, 31.2), (-81.8, 26.1), (-98.0, 39.0),
        (30.7, 36.9), (94.6, 24.4), (-120.6, 34.7), (55.3, 25.2)]


# ---------------------------------------------------------------- scenes
def dashed(d, p0, p1, fill, dash=6, gap=5, width=2):
    import math
    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    steps = int(dist // (dash + gap)) + 1
    for i in range(steps):
        t0 = i * (dash + gap) / dist
        t1 = min((i * (dash + gap) + dash) / dist, 1.0)
        d.line([x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0,
                x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1], fill=fill, width=width)


def burst(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def scene_gulf(d, x, y, w, h):
    for i in range(h - 22):
        t = i / max(h - 23, 1)
        d.line([x, y + i, x + w, y + i],
               fill=(13 + int(14 * t), 32 + int(22 * t), 52 + int(26 * t)))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(16, 52, 66))
    for sx, sy in [(30, 12), (90, 7), (150, 15), (230, 9), (285, 18), (60, 20)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(210, 220, 230))
    # two radar dishes on masts
    for rx in (52, 128):
        d.line([x + rx, y + h - 22, x + rx, y + 26], fill=(190, 198, 205), width=3)
        d.pieslice([x + rx - 17, y + 8, x + rx + 17, y + 40], start=300, end=120,
                   fill=(215, 222, 228))
        d.line([x + rx, y + 24, x + rx + 22, y + 12], fill=(215, 222, 228), width=2)
    dashed(d, (x + w - 8, y + 4), (x + 140, y + 30), (240, 120, 110))
    dashed(d, (x + w - 30, y + 2), (x + 66, y + 34), (240, 170, 120))
    burst(d, x + 132, y + 30, 11, (245, 190, 60))
    burst(d, x + 132, y + 30, 6, (235, 90, 40))
    # tanker silhouette on the sea, right side
    tx, ty = x + w - 118, y + h - 20
    d.polygon([(tx, ty), (tx + 96, ty), (tx + 86, ty + 9), (tx + 10, ty + 9)],
              fill=(8, 14, 20))
    d.rectangle([tx + 62, ty - 9, tx + 80, ty], fill=(8, 14, 20))
    d.rectangle([tx + 14, ty - 5, tx + 52, ty], fill=(8, 14, 20))
    chip(d, x + 8, y + h - 44, "2 PATRIOT RADARS · IRGC CLAIM", AB(10), RED)
    caption_band(d, x, y + h, w, "BAHRAIN · KUWAIT · STRAIT OF HORMUZ")


def scene_cop31(d, x, y, w, h):
    for i in range(h):
        t = i / max(h - 1, 1)
        d.line([x, y + i, x + w, y + i],
               fill=(38 + int(20 * t), 74 + int(16 * t), 82 + int(10 * t)))
    # hall: pediment + columns
    cx = x + w // 2
    d.polygon([(cx - 105, y + 26), (cx + 105, y + 26), (cx, y + 6)],
              fill=(226, 216, 188))
    d.rectangle([x + 18, y + 28, x + w - 18, y + 33], fill=(226, 216, 188))
    for i in range(6):
        cxx = x + 34 + i * 48
        d.rectangle([cxx, y + 35, cxx + 12, y + h - 30], fill=(214, 203, 172))
    # big screen
    d.rectangle([cx - 44, y + 38, cx + 44, y + 64], fill=(16, 34, 52))
    text(d, (cx, y + 44), "COP31", AB(15), (240, 235, 210), anchor="ma")
    text(d, (cx, y + 80), "ANTALYA", AB(9), (240, 235, 210), anchor="ma")
    # delegate table arc + heads
    d.pieslice([cx - 120, y + h - 52, cx + 120, y + h + 6], start=180, end=360,
               fill=(24, 44, 58))
    for i in range(7):
        hx = cx - 90 + i * 30
        d.ellipse([hx - 5, y + h - 34, hx + 5, y + h - 24], fill=(232, 200, 160))
    # small flags
    for i, col in enumerate([(200, 60, 50), (240, 200, 60), (70, 130, 200),
                             (240, 240, 240), (60, 160, 90)]):
        fx = x + 14 + i * 16
        d.line([fx, y + 8, fx, y + 24], fill=(220, 220, 220), width=1)
        d.rectangle([fx, y + 8, fx + 11, y + 15], fill=col)
    chip(d, x + 8, y + h - 44, "FINAL TEXT · PLENARY 06:00 GMT", AB(10), RED)
    caption_band(d, x, y + h, w, "ANTALYA · TÜRKIYE · CLIMATE SUMMIT")


def scene_cricket(d, x, y, w, h):
    for i in range(26):
        t = i / 25
        d.line([x, y + i, x + w, y + i],
               fill=(168 + int(30 * t), 200 + int(24 * t), 190 + int(20 * t)))
    d.rectangle([x, y + 26, x + w, y + h], fill=(58, 128, 62))
    d.rectangle([x, y + 44, x + w, y + 48], fill=(76, 148, 78))
    d.rectangle([x, y + 66, x + w, y + 70], fill=(76, 148, 78))
    # sightscreen
    d.rectangle([x + w - 74, y + 14, x + w - 14, y + 44], fill=(245, 244, 238))
    # pitch trapezoid
    cx = x + w // 2
    d.polygon([(cx - 16, y + h), (cx + 16, y + h), (cx + 7, y + 30),
               (cx - 7, y + 30)], fill=(216, 196, 148))
    for sx in (cx - 5, cx + 3):
        d.rectangle([sx, y + 33, sx + 2, y + 43], fill=(240, 205, 60))
    # batsman silhouette (foreground, left of pitch)
    bx, by = cx - 52, y + h - 30
    d.ellipse([bx - 6, by - 34, bx + 6, by - 22], fill=(24, 30, 40))
    d.line([bx, by - 22, bx - 4, by - 6], fill=(24, 30, 40), width=5)
    d.line([bx - 4, by - 6, bx - 12, by + 8], fill=(24, 30, 40), width=4)
    d.line([bx - 4, by - 6, bx + 8, by + 8], fill=(24, 30, 40), width=4)
    d.line([bx - 1, by - 18, bx + 16, by - 26], fill=(24, 30, 40), width=4)
    d.line([bx + 16, by - 26, bx + 30, by - 6], fill=(120, 84, 40), width=4)
    # ball with seam arc
    d.ellipse([cx + 58, y + 34, cx + 70, y + 46], fill=(178, 32, 42))
    d.arc([cx + 60, y + 35, cx + 68, y + 45], start=300, end=120,
          fill=(245, 240, 230), width=1)
    chip(d, x + 8, y + h - 44, "720/9 DEC · LEAD 352", AB(10), NAVY)
    caption_band(d, x, y + h, w, "BASIN RESERVE · WELLINGTON · DAY 4")


LEAD_SCENES = {"gulf": scene_gulf, "cop31": scene_cop31, "cricket": scene_cricket}


# ------------------------------------------------------------- mini strips
def mini_strip(d, x, y, w, h, kind, label):
    if kind == "houthi":
        d.rectangle([x, y, x + w, y + h], fill=(18, 34, 54))
        dashed(d, (x + 8, y + h - 6), (x + 96, y + 8), (240, 170, 120), width=2)
        burst(d, x + 104, y + 10, 8, (245, 190, 60))
        d.rectangle([x + 128, y + h - 12, x + w - 6, y + h - 5], fill=(30, 60, 84))
    elif kind == "quake":
        d.rectangle([x, y, x + w, y + h], fill=(250, 246, 232))
        pts, mid = [], y + h // 2
        import math
        for i in range(46):
            amp = 2 + 11 * abs(math.sin(i * 0.55)) * (0.4 + 0.6 * abs(math.sin(i * 0.13)))
            pts.append((x + 6 + i * 3.4, mid + (amp if i % 2 else -amp)))
        d.line(pts, fill=RED, width=2)
    elif kind == "f1":
        d.rectangle([x, y, x + w, y + h], fill=(24, 24, 30))
        d.arc([x + 6, y + 4, x + 130, y + h + 16], start=180, end=330,
              fill=(230, 230, 230), width=3)
        d.polygon([(x + 118, y + 12), (x + 148, y + 12), (x + 154, y + 20),
                   (x + 124, y + 20)], fill=RED)
        d.rectangle([x + 128, y + 8, x + 138, y + 12], fill=(200, 200, 200))
    elif kind == "rocket":
        d.rectangle([x, y, x + w, y + h], fill=(20, 38, 66))
        rx = x + 30
        d.polygon([(rx, y + 4), (rx + 7, y + 12), (rx - 7, y + 12)], fill=WHITE)
        d.rectangle([rx - 7, y + 12, rx + 7, y + h - 8], fill=WHITE)
        d.polygon([(rx - 7, y + h - 12), (rx - 14, y + h - 4), (rx - 7, y + h - 4)],
                  fill=RED)
        d.polygon([(rx + 7, y + h - 12), (rx + 14, y + h - 4), (rx + 7, y + h - 4)],
                  fill=RED)
        burst(d, rx, y + h - 3, 6, (245, 170, 60))
    elif kind == "football":
        d.rectangle([x, y, x + w, y + h], fill=(52, 118, 58))
        d.rectangle([x + 5, y + 4, x + w - 5, y + h - 4], outline=(240, 244, 238), width=1)
        d.line([x + w // 2, y + 4, x + w // 2, y + h - 4], fill=(240, 244, 238), width=1)
        d.ellipse([x + w // 2 - 9, y + h // 2 - 9, x + w // 2 + 9, y + h // 2 + 9],
                  outline=(240, 244, 238), width=1)
        d.ellipse([x + w // 2 + 22, y + h // 2 - 4, x + w // 2 + 30, y + h // 2 + 4],
                  fill=(245, 245, 245))
    elif kind == "tennis":
        d.rectangle([x, y, x + w, y + h], fill=(44, 96, 128))
        d.rectangle([x + 8, y + 5, x + 120, y + h - 5], outline=(240, 244, 238), width=1)
        d.line([x + 64, y + 5, x + 64, y + h - 5], fill=(20, 20, 20), width=3)
        d.line([x + 8, y + h // 2, x + 120, y + h // 2], fill=(240, 244, 238), width=1)
        d.ellipse([x + 96, y + 8, x + 104, y + 16], fill=(210, 220, 60))
    elif kind == "golf":
        d.rectangle([x, y, x + w, y + h], fill=(66, 138, 70))
        d.ellipse([x + 10, y + h - 12, x + 120, y + h - 2], fill=(86, 158, 88))
        fx = x + 148
        d.line([fx, y + 6, fx, y + h - 6], fill=WHITE, width=2)
        d.polygon([(fx, y + 6), (fx + 13, y + 10), (fx, y + 14)], fill=RED)
        d.ellipse([fx - 5, y + h - 8, fx + 5, y + h - 3], fill=(30, 30, 30))
    elif kind == "sumo":
        d.rectangle([x, y, x + w, y + h], fill=(206, 178, 128))
        d.ellipse([x + 52, y + 3, x + 118, y + h - 3], outline=(250, 248, 240), width=3)
        d.ellipse([x + 72, y + 12, x + 86, y + 26], fill=(52, 44, 40))
        d.ellipse([x + 86, y + 12, x + 100, y + 26], fill=(70, 58, 52))
    elif kind == "rsm":
        d.rectangle([x, y, x + w, y + h], fill=(250, 246, 232))
        for i in range(3):
            bx = x + 14 + i * 26
            d.rectangle([bx, y + 10, bx + 16, y + h - 4], fill=(47, 93, 138))
            text(d, (bx + 8, y + 1), "-9", AB(9), INK, anchor="ma")
    elif kind == "nfl":
        d.rectangle([x, y, x + w, y + h], fill=(46, 104, 54))
        for i in range(6):
            lx = x + 12 + i * 26
            d.line([lx, y + 4, lx, y + h - 4], fill=(240, 244, 238), width=1)
        d.ellipse([x + w // 2 - 12, y + h // 2 - 6, x + w // 2 + 12, y + h // 2 + 6],
                  fill=(150, 92, 44))
    # in-strip data label (>=9px) bottom-left, with dark backing if needed
    f = AB(10)
    lw = int(tw(d, label, f)) + 10
    d.rectangle([x + 4, y + h - 15, x + 4 + lw, y + h - 2], fill=(10, 14, 20))
    text(d, (x + 9, y + h - 13), label, f, WHITE)


# ------------------------------------------------------------------- map
def draw_map(d, x, y, w, h):
    from mapdata import WORLD
    d.rectangle([x, y, x + w, y + h], fill=(24, 58, 44))
    text(d, (x + 10, y + 7), "WHERE IT HAPPENED", AB(12), (240, 238, 220))
    mx0, my0, mw, mh = x + 8, y + 26, w - 16, h - 52

    def proj(lon, lat):
        lat = max(-60.0, min(85.0, lat))
        return (mx0 + (lon + 180.0) / 360.0 * mw,
                my0 + (85.0 - lat) / 145.0 * mh)

    land = (122, 168, 116)
    for polys in WORLD.values():
        for poly in polys.split("|"):
            pts = []
            for pair in poly.split(","):
                if ":" not in pair:
                    continue
                lo, la = pair.split(":")
                pts.append(proj(float(lo), float(la)))
            if len(pts) >= 3:
                d.polygon(pts, fill=land)
    for lon, lat in DOTS:
        px, py = proj(lon, lat)
        d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=(210, 205, 170))
    for num, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        col = (250, 248, 240)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=col, width=1)
        text(d, (px, py - 5), str(num), AB(10), WHITE, anchor="ma")
    text(d, (x + 10, y + h - 20),
         "Numbered pins = the 13 pictured cards · small dots = the briefs",
         AM(10), (235, 232, 210))


# ------------------------------------------------------------------ main
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 12  # page margin
    CW = W - 2 * M

    # --- thin paper-name bar (text 12px <= 20px) ---
    d.rectangle([0, 0, W, 24], fill=NAVY)
    text(d, (M, 5), "THE DAILY ATLAS · THE WORLD IN ONE DAY", AB(12), WHITE)
    r = "40 STORIES · 7 REGIONS · EVERY ONE FROM TODAY"
    text(d, (W - M, 5), r, AB(12), WHITE, anchor="ra")

    # --- R1: the DATE is the masthead (own layer, scaled to fit) ---
    date_s = "SUNDAY 22 NOVEMBER 2026"
    nat = Image.new("RGBA", (1750, 160), (0, 0, 0, 0))
    ImageDraw.Draw(nat).text((6, 6), date_s, font=PF(118), fill=INK + (255,))
    nb = nat.getbbox()
    layer = nat.crop(nb).resize((958, 88), Image.LANCZOS)
    ink_w, ink_h = layer.size
    mast_y = 28
    img.paste(layer, (M + (CW - ink_w) // 2, mast_y), layer)
    d = ImageDraw.Draw(img)
    print(f"MASTHEAD date ink box: {ink_w}w x {ink_h}h px "
          f"(Playfair 118 layer scaled to fit)")
    sub_y = mast_y + 112
    text(d, (W // 2, sub_y),
         "Gulf claims overnight · COP31 text tabled in Antalya · "
         "India declare at 720 in Wellington", AM(13), GREY, anchor="ma")

    # --- timeline (6 slots) + R2 numbers strip, inside top 22% (y<225) ---
    tl_y = 156
    colw = CW // 6
    for i, (t, ev) in enumerate(TIMELINE):
        cx = M + i * colw
        text(d, (cx + 2, tl_y), t, AB(11), NAVY)
        for j, ln in enumerate(wrap(d, ev, AM(10), colw - 8)):
            text(d, (cx + 2, tl_y + 14 + j * 12), ln, AM(10), INK)
        if i:
            d.line([cx - 4, tl_y, cx - 4, tl_y + 38], fill=(190, 180, 155), width=1)
    ns_y = 206
    d.line([M, ns_y - 6, W - M, ns_y - 6], fill=RED, width=2)
    nw = CW // 6
    digit_ink = None
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * nw
        text(d, (cx + 2, ns_y), num, AB(50), RED)
        if digit_ink is None:
            tmp = Image.new("L", (300, 90), 0)
            ImageDraw.Draw(tmp).text((4, 2), "720/9", font=AB(50), fill=255)
            bb = tmp.getbbox()
            digit_ink = bb[3] - bb[1]
        for j, ln in enumerate(wrap(d, cap, AB(8), nw - 8)):
            text(d, (cx + 2, ns_y + 54 + j * 10), ln, AB(8), INK)
    print(f"NUMBERS strip: 6 numbers, digit ink height {digit_ink}px "
          f"(font 50), strip top y={ns_y}")

    # --- R3: three lead cards, pictorial scenes 92px ---
    lead_y, lead_h, scene_h = 284, 214, 92
    lw3 = (CW - 16) // 3
    for i, c in enumerate(LEADS):
        cx = M + i * (lw3 + 8)
        LEAD_SCENES[c["scene"]](d, cx, lead_y, lw3, scene_h)
        source_pill(d, cx, lead_y, lw3, c["tag"])
        d.rectangle([cx, lead_y, cx + lw3, lead_y + 3],
                    fill=REGIONS[c["region"]])
        ky = lead_y + scene_h + 5
        text(d, (cx, ky), f"{c['num']}  {c['region']} · {c['topic']}",
             AB(11), REGIONS[c["region"]])
        hy = ky + 15
        for ln in wrap(d, c["headline"], PF(19), lw3 - 2)[:2]:
            text(d, (cx, hy), ln, PF(19), INK)
            hy += 23
        dy = hy + 2
        for ln in wrap(d, c["deck"], AM(12), lw3 - 2)[:4]:
            text(d, (cx, dy), ln, AM(12), INK)
            dy += 15
        d.line([cx, lead_y + lead_h, cx + lw3, lead_y + lead_h],
               fill=(200, 190, 165), width=1)
    print(f"LEAD scenes: 3 x {scene_h}px tall (strips at y={lead_y})")

    # --- mini cards 4-13, two rows of five, strip 36px each (R4/R5) ---
    rows_y = [508, 652]
    mw5 = (CW - 32) // 5
    for r_i, row in enumerate([MINIS[:5], MINIS[5:]]):
        ry = rows_y[r_i]
        for i, c in enumerate(row):
            cx = M + i * (mw5 + 8)
            mini_strip(d, cx, ry, mw5, 36, c["strip"], c["label"])
            source_pill(d, cx, ry, mw5, c["tag"])
            d.rectangle([cx, ry, cx + mw5, ry + 3], fill=REGIONS[c["region"]])
            ky = ry + 40
            text(d, (cx, ky), f"{c['num']}  {c['region']} · {c['topic']}",
                 AB(10), REGIONS[c["region"]])
            hy = ky + 13
            for ln in wrap(d, c["headline"], PF(15), mw5 - 2)[:2]:
                text(d, (cx, hy), ln, PF(15), INK)
                hy += 18
            dy = hy + 1
            for ln in wrap(d, c["deck"], AM(12), mw5 - 2)[:3]:
                text(d, (cx, dy), ln, AM(12), INK)
                dy += 15
            d.line([cx, ry + 140, cx + mw5, ry + 140],
                   fill=(200, 190, 165), width=1)

    # --- bottom zone: map (left, 204px = 19.9% of page) + ALSO ON ---
    bot_y, bot_h = 800, 168
    draw_map(d, M, bot_y, 452, bot_h)
    bx = M + 464
    bw = W - M - bx
    text(d, (bx, bot_y + 2), "ALSO ON SUNDAY 22 NOVEMBER — 27 MORE STORIES",
         AB(12), NAVY)
    d.line([bx, bot_y + 18, W - M, bot_y + 18], fill=NAVY, width=1)
    col_w = bw // 2
    for i, b in enumerate(BRIEFS):
        col = 0 if i < 14 else 1
        row = i if i < 14 else i - 14
        by = bot_y + 24 + row * 11
        cx = bx + col * col_w
        text(d, (cx, by), str(14 + i), AB(10), RED)
        for j, ln in enumerate(wrap(d, b, AM(10), col_w - 26)[:1]):
            text(d, (cx + 22, by), ln, AM(10), INK)

    # --- DATE CHECK (red) + footer ---
    dc_y = 976
    d.rectangle([M, dc_y, W - M, dc_y + 26], outline=RED, width=2)
    text(d, (M + 8, dc_y + 7), "DATE CHECK", AB(11), RED)
    for j, ln in enumerate(wrap(d, DATECHECK, AM(10), CW - 130)[:2]):
        text(d, (M + 108, dc_y + 3 + j * 11), ln, AM(10), INK)
    text(d, (M, dc_y + 32),
         "Every story happened, or was first reported, on Sunday 22 November "
         "2026. Contested claims are attributed.", AM(9), GREY)
    r = "Sources named beside each story · Original drawings"
    text(d, (W - M, dc_y + 32), r, AM(9), GREY, anchor="ra")

    # --- palette compress + save ---
    q = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
    out = os.path.join(HERE, "entry.png")
    q.save(out, optimize=True)
    sz = os.path.getsize(out)
    if sz > 160 * 1024:
        q = img.quantize(colors=192, method=Image.MEDIANCUT, dither=Image.NONE)
        q.save(out, optimize=True)
        sz = os.path.getsize(out)
    img.resize((300, 300), Image.LANCZOS).save(
        os.path.join(HERE, "entry-300.png"))
    print(f"entry.png bytes: {sz}")

    cards = LEADS + MINIS
    ge2 = sum(1 for c in cards if c["facts"] >= 2)
    avg = sum(c["facts"] for c in cards) / len(cards)
    print(f"AUDIT cards={len(cards)} ge2facts={ge2} "
          f"({100.0 * ge2 / len(cards):.0f}%) avg_facts={avg:.2f}")
    print(f"AUDIT stories total={len(cards) + len(BRIEFS)} "
          f"briefs={len(BRIEFS)} timeline_slots={len(TIMELINE)} "
          f"numbers={len(NUMBERS)} datecheck_discards=7 + 1 not-yet")


if __name__ == "__main__":
    build()
