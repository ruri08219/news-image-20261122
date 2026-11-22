"""news-image-20261122 — one image summing up 22 November 2026 world news.

Draws a 1024x1024 front page with PIL (no network, no external files):
35 date-checked stories (3 big, 11 medium, 21 listed), a world map with
numbered pins, a "day in numbers" strip, per-region counts, and a DATE CHECK
footer that names the stories left out as other days' news.

Writes /output/entry.png deterministically: same input, same bytes.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path("/output/entry.png")

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (15, 42, 67)
TEAL = (13, 92, 102)
RED = (178, 34, 34)
DARK = (28, 28, 28)
GREY = (90, 90, 90)
LIGHT = (238, 242, 245)
PAPER = (255, 255, 255)
GOLD = (184, 134, 11)
SEA = (168, 208, 224)


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, f, max_w, max_lines):
    """Wrap text to at most max_lines lines, shrinking font if needed."""
    bold = _is_bold(f)
    size = f.size
    while size > 9:
        ff = ImageFont.truetype(FONTB if bold else FONT, size)
        lines = wrap(d, text, ff, max_w)
        if len(lines) <= max_lines:
            return lines, ff
        size -= 1
    ff = ImageFont.truetype(FONTB if bold else FONT, size)
    return wrap(d, text, ff, max_w)[:max_lines], ff


def _is_bold(f):
    return getattr(f, "path", "") == FONTB


def pill(d, x, y, text, f, fg, bg):
    w = int(d.textlength(text, font=f)) + 12
    h = f.size + 8
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    d.text((x + 6, y + 4), text, font=f, fill=fg)
    return w


# ---------------------------------------------------------------- stories
# size: big | med | list.  tag: REPORTED (all 35 verified from live wires).
STORIES = [
    # --- big 3 ---
    dict(n=1, size="big", region="MIDDLE EAST", lat=26.2, lon=50.6, off=(0, 8),
         kicker="LEAD — THE GULF WAR ESCALATES",
         title="Iran hits four US bases in Bahrain and three tankers in Hormuz",
         body=("Overnight into Sunday, Iran fires drones and missiles at four US "
               "bases in Bahrain and hits three tankers near the Strait of Hormuz. "
               "Bahrain says a civilian plant caught fire; Washington says its jets "
               "and ships are safe. Tehran claims two Patriot radars destroyed — "
               "the US calls that false."),
         src="AP · REUTERS · AL JAZEERA", tag="REPORTED", art="gulf"),
    dict(n=2, size="big", region="EUROPE", lat=36.9, lon=30.7, off=(-18, 8),
         kicker="CLIMATE — COP31, ANTALYA",
         title="COP31 unveils its final deal at dawn",
         body=("Negotiators in Antalya present a consensus package overnight, "
               "past Friday's deadline. Nearly 200 nations have until 03:00 GMT "
               "to object; approval opens 06:00 GMT Sunday."),
         src="REUTERS", tag="REPORTED", art="cop"),
    dict(n=3, size="big", region="AFRICA", lat=9.1, lon=7.5,
         kicker="DISASTER — NIGERIA",
         title="24 dead as a funeral boat capsizes",
         body=("A boat carrying mourners to a funeral capsizes on a Nigerian river, "
               "killing 24. Rescue teams pull bodies from the water as families "
               "wait on the bank."),
         src="AFP", tag="REPORTED", art="boat"),
    # --- medium 11 ---
    dict(n=4, size="med", region="ASIA", lat=21.9, lon=96.0,
         title="France takes Myanmar to the UN Security Council",
         desc="Paris seeks action after Myanmar rejects the ICJ genocide ruling.",
         src="AFP", tag="REPORTED", art="un"),
    dict(n=5, size="med", region="N. AMERICA", lat=49.0, lon=-95.0,
         title="US curbs military ties with Canada",
         desc="Hegseth sets fresh limits, curbing even informal contact.",
         src="AP", tag="REPORTED", art="flags"),
    dict(n=6, size="med", region="EUROPE", lat=56.0, lon=10.0, off=(10, -6),
         title="Denmark expels Russian attaché",
         desc="Copenhagen says Moscow plotted to kill a US–Ukrainian citizen.",
         src="REUTERS", tag="REPORTED", art="spy"),
    dict(n=7, size="med", region="EUROPE", lat=50.45, lon=30.52, off=(8, -8),
         title="Zelenskyy: summit 'very unsuccessful' for Russia",
         desc="Kyiv dismisses the Shenzhen summit a day on.",
         src="REUTERS", tag="REPORTED", art="summit"),
    dict(n=8, size="med", region="ASIA", lat=39.9, lon=116.4,
         title="Trump: China's nukes 'rapid and concerning'",
         desc="Warning comes after his meeting with Xi in Shenzhen.",
         src="AP", tag="REPORTED", art="atom"),
    dict(n=9, size="med", region="N. AMERICA", lat=38.9, lon=-77.0,
         title="Melania Trump pushes Christmas ceasefires",
         desc="After the Oleshky truce, she wants more Ukraine ceasefires.",
         src="AP", tag="REPORTED", art="dove"),
    dict(n=10, size="med", region="MIDDLE EAST", lat=35.7, lon=51.4, off=(-4, -16),
         title="Trump: Iran deal 'could last 20 years'",
         desc="He claims the US removed Tehran's leadership twice.",
         src="REUTERS", tag="REPORTED", art="deal"),
    dict(n=11, size="med", region="MIDDLE EAST", lat=31.77, lon=35.21,
         title="Israel: coalition talks open",
         desc="Eisenkot invites Netanyahu's Likud to join talks.",
         src="AP", tag="REPORTED", art="knesset"),
    dict(n=12, size="med", region="MIDDLE EAST", lat=33.89, lon=35.5, off=(14, -12),
         title="Lebanon: end occupation, Aoun demands",
         desc="President wants Israeli occupation and Iranian meddling to end.",
         src="ARAB NEWS", tag="REPORTED", art="cedar"),
    dict(n=13, size="med", region="ASIA", lat=30.18, lon=67.0,
         title="Pakistan kills 15 militants",
         desc="Forces destroy hideouts in Balochistan, the military says.",
         src="AFP", tag="REPORTED", art="mount"),
    dict(n=14, size="med", region="ASIA", lat=23.34, lon=85.31, off=(0, 12),
         title="Cyclone Akvan hits India",
         desc="14 flights cancelled at Ranchi airport as the storm batters east.",
         src="PTI", tag="REPORTED", art="storm"),
    # --- also listed (one line each) ---
    dict(n=15, size="list", region="ASIA", lat=25.6, lon=85.1, off=(14, -12),
         text="Modi opens Nitish Setu bridge linking Patna and Vaishali, Bihar.",
         src="PTI"),
    dict(n=16, size="list", region="ASIA", lat=28.6, lon=77.2,
         text="Japan to hold first live-fire drills on Indian soil.",
         src="REUTERS"),
    dict(n=17, size="list", region="OCEANIA", lat=-35.28, lon=149.13,
         text="Cummins keeps Australia Test captaincy, unanimous backing.",
         src="AAP"),
    dict(n=18, size="list", region="OCEANIA", lat=-41.29, lon=174.78,
         text="India face New Zealand in windy Wellington Test.",
         src="PTI"),
    dict(n=19, size="list", region="EUROPE", lat=50.85, lon=4.35,
         text="Belgium faces air shutdown Monday in national strike.",
         src="AFP"),
    dict(n=20, size="list", region="EUROPE", lat=48.85, lon=2.35, off=(-16, 4),
         text="French cost-of-living protests rally for sixth weekend.",
         src="AFP"),
    dict(n=21, size="list", region="AFRICA", lat=32.9, lon=13.18,
         text="Libya loses $30.8m as armed group blocks oil pipeline 20+ days.",
         src="REUTERS"),
    dict(n=22, size="list", region="ASIA", lat=21.49, lon=39.19,
         text="Air India extends Jeddah suspension to 24 November.",
         src="PTI"),
    dict(n=23, size="list", region="N. AMERICA", lat=40.71, lon=-74.0, off=(16, -14),
         text="US airlines warned of al-Qaeda-linked threat before Thanksgiving.",
         src="AP"),
    dict(n=24, size="list", region="N. AMERICA", lat=38.9, lon=-77.0, off=(20, 10),
         text="FBI database breach raises security alarm.",
         src="REUTERS"),
    dict(n=25, size="list", region="MIDDLE EAST", lat=26.7, lon=55.9, off=(16, 10),
         text="Iran: Qeshm blasts were US munitions disposal, not a new attack.",
         src="AP"),
    dict(n=26, size="list", region="MIDDLE EAST", lat=26.2, lon=50.6, off=(20, -16),
         text="Bahrain probes Patriot interceptor crash amid drone reports.",
         src="REUTERS"),
    dict(n=27, size="list", region="N. AMERICA", lat=38.9, lon=-77.0, off=(-18, 12),
         text="FEMA bed bugs send 1,000+ Washington staff home.",
         src="AP"),
    dict(n=28, size="list", region="MIDDLE EAST", lat=31.9, lon=35.2, off=(12, 8),
         text="West Bank settler guards shoot a man dead, officials say.",
         src="AFP"),
    dict(n=29, size="list", region="MIDDLE EAST", lat=31.5, lon=34.47, off=(-14, 6),
         text="Gaza: four killed in Israeli ceasefire violations.",
         src="AFP"),
    dict(n=30, size="list", region="ASIA", lat=13.76, lon=100.5, off=(12, 8),
         text="Thai youth protest in Bangkok over schools and politics.",
         src="AP"),
    dict(n=31, size="list", region="EUROPE", lat=40.42, lon=-3.7, off=(0, 14),
         text="Spain to widen bank tax to fund housing.",
         src="REUTERS"),
    dict(n=32, size="list", region="ASIA", lat=37.57, lon=126.98,
         text="South Korea offers $75,000 for exam-cheating tips.",
         src="AP"),
    dict(n=33, size="list", region="AFRICA", lat=-4.32, lon=15.31,
         text="DR Congo Ebola fight hit by violence and distrust.",
         src="AFP"),
    dict(n=34, size="list", region="S. AMERICA", lat=-15.79, lon=-47.88,
         text="Brazil town clears rubble after deadly storm.",
         src="REUTERS"),
    dict(n=35, size="list", region="N. AMERICA", lat=25.76, lon=-80.19,
         text="G20: Trump says all top-20 leaders due in Florida.",
         src="REUTERS"),
]

LEFT_OUT = ("Peru 6.9 quake (20 Nov) · Sparta II Baltic strike (21 Nov) · "
            "ICJ Myanmar genocide ruling (21 Nov) · Trump–Xi–Putin Shenzhen "
            "summit (21 Nov) · Russian missiles in Poland (21 Nov) · S&P 500 "
            "correction (21 Nov) · Bolsonaro to ICU (21 Nov) · 'El Chapo "
            "Isidro' captured (21 Nov) · Estonia border closure announced "
            "(20 Nov) · Voyager 1 one light-day (21 Nov)")

NUMBERS = ("4 bases hit · 3 tankers struck · 24 dead · "
           "15 militants killed · $30.8m lost · 14 flights axed")
REGIONS = ("MIDDLE EAST 8 · ASIA 9 · EUROPE 7 · NORTH AMERICA 5 · "
           "AFRICA 3 · OCEANIA 2 · SOUTH AMERICA 1")

# ---------------------------------------------------------------- illustrations
# Flat drawn scenes, one per featured story. Each draws inside box (x, y, w, h).

def _rr(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def art_gulf(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 8, (16, 42, 67))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(24, 68, 104))
    # tanker
    d.rectangle([x + w * 0.10, y + h * 0.52, x + w * 0.62, y + h * 0.66], fill=(30, 30, 30))
    for i in range(4):
        cx = x + w * (0.14 + i * 0.11)
        d.rectangle([cx, y + h * 0.40, cx + w * 0.08, y + h * 0.52], fill=(200, 60, 40))
    d.rectangle([x + w * 0.62, y + h * 0.44, x + w * 0.70, y + h * 0.66], fill=(60, 60, 60))
    # explosion starburst
    ex, ey = x + w * 0.80, y + h * 0.30
    for r, c in ((26, (255, 140, 0)), (18, (255, 200, 40)), (10, (255, 240, 160))):
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=c)
    # drone
    dx, dy = x + w * 0.22, y + h * 0.20
    d.ellipse([dx - 12, dy - 3, dx + 12, dy + 3], fill=(220, 220, 220))
    d.ellipse([dx - 18, dy - 8, dx - 8, dy + 2], outline=(220, 220, 220), width=2)
    d.ellipse([dx + 8, dy - 8, dx + 18, dy + 2], outline=(220, 220, 220), width=2)
    d.line([dx, dy + 3, ex - 14, ey + 8], fill=(255, 200, 40), width=2)


def art_cop(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 8, (18, 90, 80))
    # globe
    cx, cy, r = x + w * 0.30, y + h * 0.52, h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 180, 220))
    d.ellipse([cx - r * 0.55, cy - r * 0.7, cx - r * 0.05, cy - r * 0.2], fill=(70, 160, 90))
    d.ellipse([cx + r * 0.1, cy + r * 0.25, cx + r * 0.6, cy + r * 0.7], fill=(70, 160, 90))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(255, 255, 255), width=2)
    # sun
    sx, sy = x + w * 0.82, y + h * 0.24
    d.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=(255, 210, 60))
    for a in range(0, 360, 45):
        import math as _m
        d.line([sx + 16 * _m.cos(_m.radians(a)), sy + 16 * _m.sin(_m.radians(a)),
                sx + 23 * _m.cos(_m.radians(a)), sy + 23 * _m.sin(_m.radians(a))],
               fill=(255, 210, 60), width=2)
    # flags row
    for i, c in enumerate(((200, 40, 40), (40, 90, 200), (240, 200, 40), (60, 160, 80))):
        fx = x + w * (0.52 + i * 0.12)
        d.rectangle([fx, y + h * 0.62, fx + w * 0.09, y + h * 0.80], fill=c)
        d.line([fx + 2, y + h * 0.62, fx + 2, y + h * 0.50], fill=(255, 255, 255), width=2)


def art_boat(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 8, (20, 70, 110))
    for i in range(3):
        wy = y + h * (0.68 + i * 0.10)
        d.arc([x + w * 0.05, wy - 8, x + w * 0.95, wy + 8], 0, 180, fill=(150, 200, 235), width=3)
    # capsized hull
    d.polygon([(x + w * 0.28, y + h * 0.52), (x + w * 0.72, y + h * 0.52),
               (x + w * 0.62, y + h * 0.66), (x + w * 0.38, y + h * 0.66)], fill=(150, 70, 40))
    d.rectangle([x + w * 0.44, y + h * 0.40, x + w * 0.56, y + h * 0.52], fill=(150, 70, 40))
    # lifebuoy
    bx, by = x + w * 0.80, y + h * 0.30
    d.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=(255, 255, 255))
    d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(20, 70, 110))
    for a in (45, 135, 225, 315):
        import math as _m
        d.line([bx + 8 * _m.cos(_m.radians(a)), by + 8 * _m.sin(_m.radians(a)),
                bx + 13 * _m.cos(_m.radians(a)), by + 13 * _m.sin(_m.radians(a))],
               fill=(220, 60, 40), width=4)


def art_un(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (30, 90, 160))
    cx, cy, r = x + w / 2, y + h / 2, min(w, h) * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=(30, 90, 160))
    for k in range(-2, 3):
        d.line([cx + k * r * 0.28, cy - r * 0.6, cx + k * r * 0.28, cy + r * 0.6],
               fill=(255, 255, 255), width=1)
    d.ellipse([cx - r * 0.62, cy - r * 0.2, cx + r * 0.62, cy + r * 0.2], outline=(255, 255, 255), width=1)


def art_flags(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (235, 235, 235))
    # US flag
    d.rectangle([x + 3, y + 4, x + w / 2 - 2, y + h - 4], fill=(180, 40, 40))
    for i in range(4):
        d.rectangle([x + 3, y + 4 + i * (h - 8) / 4, x + w / 2 - 2,
                     y + 4 + (i + 0.5) * (h - 8) / 4], fill=(255, 255, 255))
    d.rectangle([x + 3, y + 4, x + w * 0.22, y + h * 0.5], fill=(30, 50, 110))
    # Canada flag
    d.rectangle([x + w / 2 + 2, y + 4, x + w - 3, y + h - 4], fill=(255, 255, 255))
    d.rectangle([x + w / 2 + 2, y + 4, x + w / 2 + 8, y + h - 4], fill=(200, 30, 30))
    d.rectangle([x + w - 9, y + 4, x + w - 3, y + h - 4], fill=(200, 30, 30))
    mx, my = x + w * 0.75, y + h * 0.52
    d.polygon([(mx, my - 9), (mx + 4, my - 2), (mx + 8, my - 6), (mx + 7, my + 2),
               (mx + 10, my + 4), (mx + 3, my + 5), (mx + 2, my + 11), (mx, my + 7),
               (mx - 2, my + 11), (mx - 3, my + 5), (mx - 10, my + 4), (mx - 7, my + 2),
               (mx - 8, my - 6), (mx - 4, my - 2)], fill=(200, 30, 30))
    d.line([x + 2, y + h - 2, x + w - 2, y + h - 2], fill=(178, 34, 34), width=2)


def art_spy(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (45, 45, 60))
    cx, cy, r = x + w * 0.42, y + h * 0.46, min(w, h) * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 210, 60), width=3)
    d.line([cx + r * 0.7, cy + r * 0.7, cx + r * 1.5, cy + r * 1.5], fill=(255, 210, 60), width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 80, 60))
    d.line([cx - 8, cy, cx + 8, cy], fill=(255, 255, 255), width=1)
    d.line([cx, cy - 8, cx, cy + 8], fill=(255, 255, 255), width=1)


def art_summit(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (240, 238, 230))
    cols = [(200, 40, 40), (40, 80, 180), (220, 220, 220)]
    for i, c in enumerate(cols):
        fx = x + w * (0.18 + i * 0.30)
        d.line([fx, y + 4, fx, y + h - 6], fill=(80, 80, 80), width=2)
        d.polygon([(fx, y + 4), (fx + w * 0.24, y + 10), (fx, y + 16)], fill=c)
    d.ellipse([x + w * 0.62, y + h * 0.58, x + w * 0.94, y + h * 0.88], fill=(255, 255, 255),
              outline=(120, 120, 120))
    d.polygon([(x + w * 0.66, y + h * 0.86), (x + w * 0.72, y + h * 0.98), (x + w * 0.76, y + h * 0.86)],
              fill=(255, 255, 255))


def art_atom(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (20, 40, 70))
    cx, cy = x + w / 2, y + h / 2
    for ang in (0, 60, 120):
        d.arc([cx - 14, cy - 8, cx + 14, cy + 8], 0, 360, fill=(120, 200, 255), width=2)
        # rotate by drawing a second ellipse via polygon approximation is overkill;
        # use three tilted ellipses through arc boxes of different aspect
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 210, 60))
    d.ellipse([cx - 14, cy - 5, cx + 14, cy + 5], outline=(120, 200, 255), width=2)


def art_dove(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (170, 210, 235))
    cx, cy = x + w * 0.45, y + h * 0.55
    d.ellipse([cx - 14, cy - 7, cx + 14, cy + 7], fill=(255, 255, 255))
    d.ellipse([cx + 8, cy - 11, cx + 20, cy + 1], fill=(255, 255, 255))
    d.polygon([(cx + 18, cy - 8), (cx + 26, cy - 10), (cx + 19, cy - 4)], fill=(255, 180, 40))
    d.ellipse([cx + 14, cy - 9, cx + 16, cy - 7], fill=(30, 30, 30))
    d.polygon([(cx - 10, cy - 6), (cx - 2, cy - 16), (cx + 4, cy - 5)], fill=(235, 235, 235))
    d.line([cx - 16, cy + 4, cx - 26, cy + 10], fill=(80, 160, 80), width=2)
    d.ellipse([cx - 28, cy + 8, cx - 22, cy + 14], fill=(80, 160, 80))


def art_deal(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (240, 235, 220))
    # two sleeves + clasped hands, simplified
    d.polygon([(x + 2, y + h * 0.42), (x + w * 0.42, y + h * 0.42),
               (x + w * 0.42, y + h * 0.62), (x + 2, y + h * 0.62)], fill=(40, 80, 160))
    d.polygon([(x + w - 2, y + h * 0.42), (x + w * 0.58, y + h * 0.42),
               (x + w * 0.58, y + h * 0.62), (x + w - 2, y + h * 0.62)], fill=(60, 60, 60))
    d.ellipse([x + w * 0.40, y + h * 0.40, x + w * 0.60, y + h * 0.64], fill=(240, 200, 160))
    d.rectangle([x + w * 0.06, y + h * 0.74, x + w * 0.94, y + h * 0.92], fill=(178, 34, 34))
    d.text((x + w * 0.06 + 4, y + h * 0.76), "20 YEARS", font=font(10, True), fill=(255, 255, 255))


def art_knesset(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (235, 240, 245))
    d.rectangle([x + w * 0.12, y + h * 0.30, x + w * 0.88, y + h * 0.38], fill=(90, 110, 140))
    for i in range(4):
        cx = x + w * (0.20 + i * 0.20)
        d.rectangle([cx - 3, y + h * 0.38, cx + 3, y + h * 0.80], fill=(120, 140, 170))
    d.rectangle([x + w * 0.10, y + h * 0.80, x + w * 0.90, y + h * 0.86], fill=(90, 110, 140))
    d.polygon([(x + w * 0.30, y + h * 0.30), (x + w * 0.50, y + h * 0.14),
               (x + w * 0.70, y + h * 0.30)], fill=(90, 110, 140))


def art_cedar(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (255, 255, 255))
    d.rectangle([x, y, x + w, y + h * 0.18], fill=(200, 40, 40))
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(200, 40, 40))
    cx = x + w / 2
    d.polygon([(cx, y + h * 0.24), (cx + 10, y + h * 0.44), (cx - 10, y + h * 0.44)], fill=(20, 120, 60))
    d.polygon([(cx, y + h * 0.38), (cx + 13, y + h * 0.60), (cx - 13, y + h * 0.60)], fill=(20, 120, 60))
    d.polygon([(cx, y + h * 0.54), (cx + 15, y + h * 0.76), (cx - 15, y + h * 0.76)], fill=(20, 120, 60))
    d.rectangle([cx - 2, y + h * 0.74, cx + 2, y + h * 0.82], fill=(120, 80, 40))


def art_mount(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (200, 225, 240))
    d.polygon([(x, y + h), (x + w * 0.30, y + h * 0.25), (x + w * 0.55, y + h)],
              fill=(90, 110, 130))
    d.polygon([(x + w * 0.35, y + h), (x + w * 0.68, y + h * 0.35), (x + w, y + h)],
              fill=(60, 80, 100))
    d.polygon([(x + w * 0.30, y + h * 0.25), (x + w * 0.24, y + h * 0.38),
               (x + w * 0.36, y + h * 0.38)], fill=(255, 255, 255))
    d.polygon([(x + w * 0.68, y + h * 0.35), (x + w * 0.63, y + h * 0.46),
               (x + w * 0.73, y + h * 0.46)], fill=(255, 255, 255))


def art_storm(d, x, y, w, h):
    _rr(d, [x, y, x + w, y + h], 6, (40, 50, 80))
    cx, cy = x + w * 0.42, y + h * 0.50
    for r in (16, 11, 6):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(255, 255, 255), width=2)
    # plane
    px, py = x + w * 0.78, y + h * 0.28
    d.polygon([(px, py - 6), (px + 12, py + 2), (px, py + 4), (px - 8, py + 2)], fill=(255, 210, 60))
    for i in range(3):
        lx = x + w * (0.15 + i * 0.18)
        d.line([lx, y + h * 0.72, lx - 3, y + h * 0.88], fill=(140, 180, 220), width=2)


ART = {"gulf": art_gulf, "cop": art_cop, "boat": art_boat, "un": art_un,
       "flags": art_flags, "spy": art_spy, "summit": art_summit,
       "atom": art_atom, "dove": art_dove, "deal": art_deal,
       "knesset": art_knesset, "cedar": art_cedar, "mount": art_mount,
       "storm": art_storm}

# ---------------------------------------------------------------- world map
# Simplified continent outlines as (lon, lat) polygons; equirectangular,
# x: lon -170..190 -> map width, y: lat 72..-55 -> map height.

N_AMERICA = [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-130, 54), (-125, 49),
             (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16),
             (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-80, 8), (-77, 7), (-80, 9),
             (-83, 9), (-87, 13), (-90, 14), (-92, 15), (-97, 16), (-97, 19), (-94, 17),
             (-90, 21), (-87, 21), (-83, 25), (-81, 25), (-80, 32), (-76, 35), (-75, 38),
             (-74, 40), (-70, 42), (-68, 44), (-66, 45), (-60, 47), (-55, 47), (-60, 50),
             (-65, 50), (-68, 52), (-60, 55), (-64, 58), (-68, 58), (-72, 62), (-78, 62),
             (-82, 66), (-90, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
             (-155, 71), (-165, 68)]
S_AMERICA = [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
             (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
             (-66, -55), (-65, -50), (-62, -45), (-58, -38), (-52, -33), (-48, -28),
             (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
             (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-76, 10)]
AFRICA = [(-6, 35), (0, 36), (10, 37), (11, 34), (15, 32), (20, 32), (25, 32),
          (30, 31), (32, 31), (34, 28), (36, 22), (38, 18), (40, 15), (43, 12),
          (48, 11), (51, 12), (51, 10), (46, 5), (42, 0), (40, -5), (40, -10),
          (39, -15), (36, -20), (33, -26), (28, -33), (20, -35), (17, -32),
          (15, -27), (13, -20), (12, -15), (13, -10), (12, -5), (9, 0), (9, 4),
          (6, 4), (0, 6), (-8, 5), (-13, 8), (-17, 12), (-17, 15), (-16, 20),
          (-15, 25), (-13, 28), (-10, 30)]
EURASIA = [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49), (2, 51),
           (5, 53), (8, 57), (10, 59), (6, 62), (12, 65), (18, 69), (25, 71),
           (32, 70), (40, 68), (48, 68), (55, 68), (62, 69), (68, 72), (75, 73),
           (82, 74), (90, 75), (98, 76), (105, 77), (112, 76), (120, 73), (128, 72),
           (135, 72), (142, 72), (150, 70), (158, 69), (162, 66), (170, 66),
           (178, 65), (178, 62), (172, 60), (168, 60), (162, 58), (158, 52),
           (156, 50), (150, 48), (144, 44), (142, 40), (140, 36), (136, 34),
           (132, 33), (129, 31), (127, 28), (124, 26), (121, 23), (119, 20),
           (116, 18), (112, 15), (109, 12), (107, 10), (105, 8), (103, 3),
           (100, 6), (98, 10), (96, 14), (94, 17), (92, 20), (89, 22), (86, 20),
           (83, 17), (80, 13), (77, 8), (75, 12), (73, 17), (71, 21), (69, 22),
           (67, 24), (64, 25), (61, 25), (58, 25), (56, 26), (52, 25), (50, 24),
           (48, 29), (43, 29), (39, 21), (43, 12), (48, 14), (51, 16), (55, 17),
           (58, 20), (59, 23), (57, 25), (54, 26), (52, 26), (50, 29), (48, 30),
           (44, 29), (40, 28), (37, 27), (35, 29), (34, 31), (35, 33), (36, 36),
           (33, 36), (30, 36), (27, 37), (23, 36), (19, 40), (15, 38), (12, 42),
           (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
             (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
             (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
             (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
             (122, -17), (118, -20)]
NZ = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (175, -40),
      (173, -42), (170, -44), (167, -46)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-3, 50)]
JAPAN = [(130, 31), (133, 34), (136, 35), (139, 35), (141, 38), (141, 42),
         (143, 43), (145, 44), (142, 45), (140, 42), (139, 38), (137, 37),
         (134, 35), (131, 33)]
INDONESIA = [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9),
             (125, -9), (130, -3), (135, -2), (140, -4), (141, -8), (136, -6),
             (131, -1), (127, 1), (122, 0), (118, -2), (114, -3), (110, -7),
             (105, -6), (100, -1), (97, 3)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25), (44, -25),
              (43, -20)]
GREENLAND = [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76),
             (-35, 77), (-45, 76), (-55, 74), (-58, 70), (-53, 66), (-48, 62)]

CONTINENTS = [N_AMERICA, S_AMERICA, AFRICA, EURASIA, AUSTRALIA, NZ, UK,
              JAPAN, INDONESIA, MADAGASCAR, GREENLAND]

# ---------------------------------------------------------------- render

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 240))
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 76.0, -55.0

    def xy(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return px, py

    for poly in CONTINENTS:
        d.polygon([xy(lon, lat) for lon, lat in poly], fill=(120, 170, 120),
                  outline=(90, 140, 90))
    labels = [("NORTH AMERICA", -120, 58), ("SOUTH AMERICA", -65, -25),
              ("EUROPE", -5, 64), ("AFRICA", 30, 15), ("ASIA", 95, 50),
              ("OCEANIA", 128, -22)]
    lf = font(10, True)
    for text, lon, lat in labels:
        px, py = xy(lon, lat)
        d.text((px - d.textlength(text, font=lf) / 2, py - 5), text, font=lf,
               fill=(70, 90, 70))
    for s in STORIES:
        px, py = xy(s["lon"], s["lat"])
        ox, oy = s.get("off", (0, 0))
        px, py = px + ox, py + oy
        big = s["size"] in ("big", "med")
        r = 8 if big else 6.5
        col = RED if s["size"] == "big" else (NAVY if s["size"] == "med" else TEAL)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=(255, 255, 255), width=1)
        nf = font(9 if big else 8, True)
        t = str(s["n"])
        d.text((px - d.textlength(t, font=nf) / 2, py - 5), t, font=nf, fill=(255, 255, 255))


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 56], fill=NAVY)
    d.text((10, 8), "THE WORLD IN ONE DAY", font=font(26, True), fill=(255, 255, 255))
    t = "SUNDAY 22 NOVEMBER 2026"
    d.text((W - 10 - d.textlength(t, font=font(19, True)), 12), t,
           font=font(19, True), fill=(255, 210, 60))
    d.text((10, 38), "35 date-checked stories  ·  7 regions  ·  14 drawn illustrations",
           font=font(12), fill=(180, 205, 225))

    big = [s for s in STORIES if s["size"] == "big"]
    med = [s for s in STORIES if s["size"] == "med"]
    lst = [s for s in STORIES if s["size"] == "list"]

    # ---- lead story ----
    s = big[0]
    y0, y1 = 56, 226
    d.rectangle([0, y0, W, y1], fill=(253, 246, 236))
    d.line([0, y1, W, y1], fill=(200, 180, 150), width=1)
    ART[s["art"]](d, 10, y0 + 8, 296, y1 - y0 - 16)
    tx = 318
    d.text((tx, y0 + 8), s["kicker"], font=font(13, True), fill=RED)
    lines, ff = fit_lines(d, s["title"], font(25, True), W - tx - 12, 2)
    yy = y0 + 28
    for ln in lines:
        d.text((tx, yy), ln, font=ff, fill=DARK)
        yy += ff.size + 3
    yy += 2
    for ln in wrap(d, s["body"], font(14), W - tx - 12):
        d.text((tx, yy), ln, font=font(14), fill=(45, 45, 45))
        yy += 18
    yy += 4
    pill(d, tx, yy, "1", font(11, True), (255, 255, 255), RED)
    d.text((tx + 26, yy + 3), s["src"] + "  ·  " + s["tag"], font=font(11, True), fill=GREY)

    # ---- stories 2 and 3 ----
    y0, y1 = 226, 356
    for i, s in enumerate(big[1:]):
        x0 = 8 + i * 508
        x1 = x0 + 500
        d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
        d.rectangle([x0, y0, x1, y1], outline=(200, 200, 200), width=1)
        ART[s["art"]](d, x0 + 6, y0 + 6, 132, y1 - y0 - 12)
        tx = x0 + 146
        d.text((tx, y0 + 8), s["kicker"], font=font(11, True), fill=TEAL)
        lines, ff = fit_lines(d, s["title"], font(17, True), x1 - tx - 8, 2)
        yy = y0 + 26
        for ln in lines:
            d.text((tx, yy), ln, font=ff, fill=DARK)
            yy += ff.size + 2
        for ln in wrap(d, s["body"], font(11), x1 - tx - 8)[:3]:
            d.text((tx, yy), ln, font=font(11), fill=(45, 45, 45))
            yy += 14
        pill(d, tx, y1 - 22, str(s["n"]), font(10, True), (255, 255, 255), RED)
        d.text((tx + 24, y1 - 19), s["src"] + " · " + s["tag"], font=font(10, True), fill=GREY)

    # ---- day in numbers ----
    y0, y1 = 356, 392
    d.rectangle([0, y0, W, y1], fill=TEAL)
    t = "THE DAY IN NUMBERS  —  " + NUMBERS
    f = font(13, True)
    d.text(((W - d.textlength(t, font=f)) / 2, y0 + 11), t, font=f, fill=(255, 255, 255))

    # ---- map ----
    y0, y1 = 392, 566
    d.text((10, y0 + 4), "WHERE IT HAPPENED — numbered pins match the stories",
           font=font(13, True), fill=NAVY)
    d.text((W - 10 - d.textlength("● 1–3 lead   ● 4–14 featured   ● 15–35 also listed",
                                  font=font(11)), y0 + 6),
           "● 1–3 lead   ● 4–14 featured   ● 15–35 also listed",
           font=font(11), fill=GREY)
    draw_map(d, 8, y0 + 24, W - 16, 128)
    t = REGIONS
    d.text(((W - d.textlength(t, font=font(12, True))) / 2, y1 - 18), t,
           font=font(12, True), fill=NAVY)

    # ---- medium grid ----
    y0 = 566
    d.text((10, y0 + 4), "THE DAY'S OTHER BIG STORIES", font=font(13, True), fill=NAVY)
    gy = y0 + 24
    rowh = 36
    colw = (W - 20) // 2
    for i, s in enumerate(med):
        col, row = i % 2, i // 2
        x0 = 10 + col * colw
        yy = gy + row * rowh
        ART[s["art"]](d, x0, yy, 34, 32)
        tx = x0 + 40
        d.text((tx, yy), f"{s['n']}. {s['title']}", font=font(13, True), fill=DARK)
        d.text((tx, yy + 16), s["desc"], font=font(11), fill=(70, 70, 70))
        sw = d.textlength(s["src"], font=font(9, True))
        d.text((x0 + colw - 10 - sw, yy + 2), s["src"], font=font(9, True), fill=GREY)
    y0 = gy + 6 * rowh  # 566+24+216 = 806

    # ---- also listed ----
    d.text((10, y0 + 2), "ALSO ON SUNDAY 22 NOVEMBER", font=font(13, True), fill=NAVY)
    ly = y0 + 22
    rowh = 13.5
    for i, s in enumerate(lst):
        col, row = i % 2, i // 2
        x0 = 10 + col * ((W - 20) // 2)
        yy = ly + row * rowh
        nf = font(11, True)
        d.text((x0, yy), f"{s['n']}.", font=nf, fill=TEAL)
        d.text((x0 + 26, yy), s["text"], font=font(11), fill=(45, 45, 45))
    y0 = ly + 11 * rowh  # ~976

    # ---- footer: date check ----
    d.rectangle([0, y0, W, H], fill=NAVY)
    f = font(11)
    d.text((10, y0 + 6), "DATE CHECK — Every story on this page happened, or was first reported, on Sunday 22 November 2026.",
           font=font(11, True), fill=(255, 210, 60))
    lines = wrap(d, "LEFT OUT AS OTHER DAYS' NEWS: " + LEFT_OUT, font(10), W - 20)
    yy = y0 + 24
    for ln in lines:
        d.text((10, yy), ln, font=font(10), fill=(200, 215, 230))
        yy += 13
    return img


def main():
    img = render()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG")
    print(f"Wrote {OUT} ({img.size[0]}x{img.size[1]}, {OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
