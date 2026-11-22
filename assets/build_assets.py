"""Regenerate the README artwork in assets/ (banner, section headers, diagrams, footer).

GitHub can't load web fonts in a README, so each SVG carries its own subset of the
fonts (Bungee + Press Start 2P, both SIL Open Font License) as a base64 WOFF2.

    py -m pip install fonttools brotli
    py assets/build_assets.py

Fonts are downloaded once into assets/.fontcache/ (git-ignored).
"""
import base64
import io
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
CACHE = HERE / ".fontcache"
FONTS = {
    "Bungee": "ofl/bungee/Bungee-Regular.ttf",
    "PressStart": "ofl/pressstart2p/PressStart2P-Regular.ttf",
}
CHARS = "".join(chr(c) for c in range(0x20, 0x7F))

NAVY, NAVY2, INK = "#0b1d3a", "#16325e", "#070c16"
BALL, STITCH, AMBER, LED, CHALK = "#e8f53a", "#d7263d", "#ffb627", "#ff4d4d", "#f4f7fb"


def font_face(family):
    CACHE.mkdir(exist_ok=True)
    ttf = CACHE / Path(FONTS[family]).name
    if not ttf.exists():
        url = "https://raw.githubusercontent.com/google/fonts/main/" + FONTS[family]
        ttf.write_bytes(urllib.request.urlopen(url, timeout=60).read())
    font = TTFont(ttf)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = []
    sub = subset.Subsetter(opts)
    sub.populate(text=CHARS)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{b64}) format('woff2')}}"


STYLE = None


def style():
    global STYLE
    if STYLE is None:
        STYLE = (
            "<style>" + font_face("Bungee") + font_face("PressStart")
            + ".b{font-family:'Bungee',Impact,sans-serif}"
            + ".p{font-family:'PressStart','Courier New',monospace}"
            + "</style>"
        )
    return STYLE


def softball(cx, cy, r, spin_s=0, gid="ball"):
    """A softball with red stitches; spins if spin_s > 0."""
    k = r / 100
    seam_l = f"M{cx - 62*k:.1f} {cy - 78*k:.1f} C{cx - 18*k:.1f} {cy - 30*k:.1f} {cx - 18*k:.1f} {cy + 30*k:.1f} {cx - 62*k:.1f} {cy + 78*k:.1f}"
    seam_r = f"M{cx + 62*k:.1f} {cy - 78*k:.1f} C{cx + 18*k:.1f} {cy - 30*k:.1f} {cx + 18*k:.1f} {cy + 30*k:.1f} {cx + 62*k:.1f} {cy + 78*k:.1f}"
    spin = (f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
            f'to="360 {cx} {cy}" dur="{spin_s}s" repeatCount="indefinite"/>') if spin_s else ""
    sw, tick = max(1.2, 2.2 * k), max(3, 9 * k)
    dash = f"{max(1.5, 3*k):.1f} {max(3, 8*k):.1f}"
    return f"""
  <defs><radialGradient id="{gid}" cx="0.36" cy="0.32" r="0.8">
    <stop offset="0" stop-color="#fbff9e"/><stop offset="0.55" stop-color="{BALL}"/><stop offset="1" stop-color="#9fae00"/>
  </radialGradient><clipPath id="{gid}c"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>
  <g clip-path="url(#{gid}c)">{spin}
    <path d="{seam_l}" fill="none" stroke="{STITCH}" stroke-width="{sw:.1f}"/>
    <path d="{seam_r}" fill="none" stroke="{STITCH}" stroke-width="{sw:.1f}"/>
    <path d="{seam_l}" fill="none" stroke="{STITCH}" stroke-width="{tick:.1f}" stroke-dasharray="{dash}"/>
    <path d="{seam_r}" fill="none" stroke="{STITCH}" stroke-width="{tick:.1f}" stroke-dasharray="{dash}"/>
  </g>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="{max(1, 3*k):.1f}"/>"""


def light_tower(x, y, flip=False):
    bulbs = "".join(
        f'<rect x="{x + c*16}" y="{y + rr*14}" width="11" height="9" rx="2" fill="#fffbe6"/>'
        for rr in range(3) for c in range(5)
    )
    beam_dir = -1 if flip else 1
    bx = x + 40
    beam = (f'<polygon points="{bx - 30},{y + 20} {bx + 30},{y + 20} {bx + beam_dir*420},{y + 430} '
            f'{bx + beam_dir*120},{y + 430}" fill="url(#beam)"/>')
    return f"""
  <circle cx="{x + 40}" cy="{y + 18}" r="120" fill="url(#glow)"/>
  {beam}
  <rect x="{x - 6}" y="{y - 6}" width="92" height="52" rx="6" fill="#1b2433"/>
  {bulbs}
  <rect x="{x + 36}" y="{y + 46}" width="8" height="80" fill="#1b2433"/>"""


def banner():
    W, H = 1200, 420
    stars = "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="0.6">'
        f'<animate attributeName="opacity" values="0.15;0.8;0.15" dur="{d}s" repeatCount="indefinite"/></circle>'
        for x, y, r, d in [(330, 40, 1.4, 3.1), (520, 26, 1.1, 4.3), (640, 58, 1.6, 2.6), (760, 30, 1.2, 3.7),
                           (880, 70, 1.0, 5.1), (420, 80, 1.0, 4.0), (1010, 36, 1.3, 3.3), (1110, 120, 1.1, 2.9)]
    )
    rows = [
        ("NEXT UP", "MON  5-7 PM ET", AMBER),
        ("PICKS", "LATEST OPEN", AMBER),
        ("CHECKS", "EVERY 10 SEC", LED),
        ("ON DECK", "24/7  RELAY", LED),
    ]
    row_svg = ""
    for i, (k, v, col) in enumerate(rows):
        y = 276 + i * 25
        row_svg += (f'<text class="p" x="96" y="{y}" font-size="14" fill="#7f8ba3">{k}</text>'
                    f'<text class="p" x="250" y="{y}" font-size="14" fill="{col}" filter="url(#ledglow)">{v}</text>')
    speed = "".join(
        f'<line x1="{x1}" y1="{y}" x2="{x1 + ln}" y2="{y}" stroke="{CHALK}" stroke-opacity="{o}" stroke-width="4" stroke-linecap="round">'
        f'<animate attributeName="x1" values="{x1};{x1 - 30};{x1}" dur="1.6s" repeatCount="indefinite"/></line>'
        for x1, y, ln, o in [(800, 170, 70, 0.35), (780, 205, 100, 0.5), (812, 240, 60, 0.3)]
    )
    grass = "".join(
        f'<rect x="{i*80}" y="356" width="40" height="64" fill="#2a8a4a" opacity="0.55"/>' for i in range(16)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Softball Lesson Bot: books the Monday 5 to 7 PM lesson, checks every 10 seconds">
  {style()}
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#050913"/><stop offset="0.7" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/>
    </linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="#fff6c8" stop-opacity="0.55"/><stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></radialGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6c8" stop-opacity="0.16"/><stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></linearGradient>
    <pattern id="led" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="#ffffff" opacity="0.045"/></pattern>
    <filter id="ledglow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="0" flood-color="#000" flood-opacity="0.45"/></filter>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#sky)"/>
    {stars}
    {light_tower(1080, 26, flip=True)}
    <!-- outfield -->
    <path d="M0 356 Q600 320 1200 356 L1200 420 L0 420 Z" fill="#1d6b38"/>
    {grass}
    <path d="M760 420 Q980 330 1200 372 L1200 420 Z" fill="#b8682f"/>
    <path d="M0 356 Q600 320 1200 356" fill="none" stroke="#ffd23f" stroke-width="5"/>
    <!-- scoreboard -->
    <rect x="56" y="38" width="680" height="350" rx="14" fill="#1b2433"/>
    <rect x="70" y="52" width="652" height="322" rx="8" fill="{INK}"/>
    <rect x="70" y="52" width="652" height="322" rx="8" fill="url(#led)"/>
    <rect x="70" y="52" width="652" height="34" rx="8" fill="{STITCH}"/>
    <rect x="70" y="74" width="652" height="12" fill="{STITCH}"/>
    <text class="p" x="396" y="76" font-size="13" fill="#fff" text-anchor="middle">HOME OF THE MONDAY LESSON</text>
    <text class="b" x="94" y="164" font-size="74" fill="#ffd23f" filter="url(#shadow)">SOFTBALL</text>
    <text class="b" x="94" y="232" font-size="58" fill="{CHALK}" filter="url(#shadow)">LESSON BOT</text>
    <line x1="94" y1="246" x2="698" y2="246" stroke="#2a3548" stroke-width="2" stroke-dasharray="6 6"/>
    {row_svg}
    <!-- live badge -->
    <rect x="590" y="282" width="108" height="34" rx="17" fill="#2a0f14" stroke="{LED}" stroke-width="2"/>
    <circle cx="612" cy="299" r="7" fill="{LED}"><animate attributeName="opacity" values="1;0.15;1" dur="1.2s" repeatCount="indefinite"/></circle>
    <text class="p" x="628" y="306" font-size="14" fill="{LED}">LIVE</text>
    <!-- the pitch -->
    {speed}
    {softball(975, 205, 104, spin_s=7)}
    <path d="M770 330 Q870 200 975 205" fill="none" stroke="{CHALK}" stroke-opacity="0.25" stroke-width="3" stroke-dasharray="2 12" stroke-linecap="round"/>
  </g>
</svg>
"""


def header(num, title, kicker):
    W, H = 1200, 104
    bulbs = "".join(
        f'<circle cx="{1004 + i*26}" cy="52" r="7" fill="{AMBER}">'
        f'<animate attributeName="opacity" values="0.2;1;0.2" dur="2.4s" begin="{i*0.3:.1f}s" repeatCount="indefinite"/></circle>'
        for i in range(6)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{num} {title}">
  {style()}
  <defs><pattern id="led" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="#fff" opacity="0.05"/></pattern></defs>
  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="{INK}" stroke="#1b2433" stroke-width="4"/>
  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="url(#led)"/>
  <rect x="2" y="2" width="132" height="{H - 4}" rx="18" fill="{STITCH}"/>
  <rect x="110" y="2" width="24" height="{H - 4}" fill="{STITCH}"/>
  <text class="b" x="68" y="70" font-size="46" fill="#fff" text-anchor="middle">{num}</text>
  <text class="p" x="164" y="50" font-size="24" fill="{CHALK}">{title}</text>
  <text class="p" x="164" y="80" font-size="12" fill="{AMBER}">{kicker}</text>
  {softball(958, 52, 22, spin_s=5, gid=f"hb{num}")}
  {bulbs}
</svg>
"""


def footer():
    W, H = 1200, 150
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="See you Monday">
  {style()}
  <defs><clipPath id="f"><rect width="{W}" height="{H}" rx="24"/></clipPath></defs>
  <g clip-path="url(#f)">
    <rect width="{W}" height="{H}" fill="{NAVY}"/>
    <path d="M0 108 Q600 84 1200 108 L1200 150 L0 150 Z" fill="#1d6b38"/>
    <path d="M0 108 Q600 84 1200 108" fill="none" stroke="#ffd23f" stroke-width="4"/>
    <text class="b" x="600" y="62" font-size="40" fill="#ffd23f" text-anchor="middle">SEE YOU MONDAY</text>
    <text class="p" x="600" y="90" font-size="13" fill="{CHALK}" text-anchor="middle">5 TO 7 PM ET  *  LATEST SLOT WINS  *  NEVER TWICE</text>
    {softball(110, 64, 34, spin_s=6, gid="f1")}
    {softball(1090, 64, 34, spin_s=6, gid="f2")}
  </g>
</svg>
"""


HEADERS = [
    ("01", "THE LINEUP", "WHAT THE BOT DOES"),
    ("02", "THE PLAY", "HOW A BOOKING HAPPENS"),
    ("03", "THE WINDOW", "WHEN SPOTS OPEN UP"),
    ("04", "THE RELAY", "THE ALWAYS-ON WATCHER"),
    ("05", "SPRING TRAINING", "SETUP AND SECRETS"),
    ("06", "BATTING PRACTICE", "TESTING WITHOUT BOOKING"),
    ("07", "RAIN DELAY", "TURNING IT OFF"),
    ("08", "THE DUGOUT", "WHAT'S IN THE REPO"),
]



# ─── diagrams that replace the old text drawings in the README ────────────────────────────────
PANEL, DIM, GREEN = "#1b2433", "#7f8ba3", "#2a8a4a"


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def txt(x, y, text, size, fill, cls="p", anchor="start", extra=""):
    return (f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{esc(text)}</text>')


def frame(w, h, label, body):
    """A dark scoreboard card with the LED-dot texture, holding `body`."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
  {style()}
  <defs>
    <pattern id="led" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="#fff" opacity="0.05"/></pattern>
    <filter id="ledglow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="18" fill="{INK}" stroke="{PANEL}" stroke-width="4"/>
  <rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="18" fill="url(#led)"/>
  {body}
</svg>
"""


def promises():
    cards = [
        ("ONE LESSON", "PER MONDAY", "cal"),
        ("NEVER ON YOUR", "COMPUTER", "screen"),
        ("NEVER YOUR INFO", "IN THE CODE", "lock"),
    ]
    out = ""
    for i, (a, b, icon) in enumerate(cards):
        x, y = 30 + i * 390, 30
        cx, cy = x + 62, y + 65
        out += f'<rect x="{x}" y="{y}" width="360" height="130" rx="14" fill="{PANEL}" stroke="#2a3548" stroke-width="2"/>'
        if icon == "cal":
            out += (f'<rect x="{cx - 28}" y="{cy - 28}" width="56" height="56" rx="8" fill="{CHALK}"/>'
                    f'<rect x="{cx - 28}" y="{cy - 28}" width="56" height="16" rx="8" fill="{STITCH}"/>'
                    f'<rect x="{cx - 28}" y="{cy - 18}" width="56" height="6" fill="{STITCH}"/>'
                    + txt(cx, cy + 20, "1", 30, INK, "b", "middle"))
        elif icon == "screen":
            out += (f'<rect x="{cx - 30}" y="{cy - 24}" width="60" height="40" rx="5" fill="none" stroke="{CHALK}" stroke-width="5"/>'
                    f'<rect x="{cx - 14}" y="{cy + 22}" width="28" height="6" rx="3" fill="{CHALK}"/>'
                    f'<line x1="{cx - 36}" y1="{cy + 30}" x2="{cx + 36}" y2="{cy - 34}" stroke="{LED}" stroke-width="7" stroke-linecap="round"/>')
        else:
            out += (f'<path d="M{cx - 14} {cy - 4} v-14 a14 14 0 0 1 28 0 v14" fill="none" stroke="{AMBER}" stroke-width="7"/>'
                    f'<rect x="{cx - 24}" y="{cy - 6}" width="48" height="38" rx="7" fill="{AMBER}"/>'
                    f'<circle cx="{cx}" cy="{cy + 10}" r="5" fill="{INK}"/><rect x="{cx - 2.5}" y="{cy + 10}" width="5" height="12" fill="{INK}"/>')
        out += txt(x + 118, y + 62, a, 22, CHALK, "b") + txt(x + 118, y + 96, b, 22, AMBER, "b")
    return frame(1200, 190, "Three promises: one lesson per Monday, never on your computer, never your info in the code", out)


def lineup():
    rows = [
        ("1", "CF", "The Watcher", "checks Calendly every 10 s, day and night"),
        ("2", "SS", "The Picker", "Monday 7 PM first, then 6 PM, then 5 PM ET"),
        ("3", "P", "The Form-Filler", "fills in name, email, phone, athlete"),
        ("4", "C", "The Scorekeeper", "booked.json: never book a Monday twice"),
        ("5", "1B", "The Vault", "personal info lives only in encrypted secrets"),
        ("6", "RF", "The Photographer", "screenshots of every run, kept for a day"),
        ("7", "2B", "The Relay", "hands off to a fresh watcher every 5 h 40 m"),
    ]
    out = f'<rect x="2" y="2" width="1196" height="58" rx="18" fill="{STITCH}"/><rect x="2" y="30" width="1196" height="30" fill="{STITCH}"/>'
    out += txt(40, 42, "#", 16, "#fff") + txt(104, 42, "POS", 16, "#fff") + txt(200, 42, "PLAYER", 16, "#fff") + txt(520, 42, "JOB", 16, "#fff")
    for i, (n, pos, name, job) in enumerate(rows):
        y = 70 + i * 62
        if i % 2 == 0:
            out += f'<rect x="14" y="{y}" width="1172" height="58" rx="10" fill="#ffffff" opacity="0.04"/>'
        out += (f'<circle cx="52" cy="{y + 29}" r="19" fill="{NAVY2}" stroke="{CHALK}" stroke-opacity="0.4" stroke-width="2"/>'
                + txt(52, y + 36, n, 18, CHALK, "b", "middle")
                + f'<rect x="100" y="{y + 11}" width="62" height="36" rx="18" fill="{AMBER}"/>'
                + txt(131, y + 36, pos, 15, INK, "p", "middle")
                + txt(200, y + 38, name, 26, CHALK, "b")
                + txt(520, y + 35, job, 12, "#c9d3e6"))
    return frame(1200, 70 + 7 * 62 + 20, "The lineup: the seven jobs the bot does, each with a baseball position", out)


def play():
    H, F, S, T = (600, 470), (850, 310), (600, 150), (350, 310)
    out = f'<polygon points="{H[0]},{H[1]} {F[0]},{F[1]} {S[0]},{S[1]} {T[0]},{T[1]}" fill="#b8682f" fill-opacity="0.32"/>'
    out += f'<polygon points="{H[0]},{H[1]} {F[0]},{F[1]} {S[0]},{S[1]} {T[0]},{T[1]}" fill="none" stroke="{CHALK}" stroke-opacity="0.75" stroke-width="4" stroke-linejoin="round"/>'
    for (x, y) in (F, S, T):
        out += f'<rect x="{x - 15}" y="{y - 15}" width="30" height="30" fill="{CHALK}" transform="rotate(45 {x} {y})"/>'
    out += f'<polygon points="{H[0] - 20},{H[1] - 14} {H[0] + 20},{H[1] - 14} {H[0] + 20},{H[1]} {H[0]},{H[1] + 16} {H[0] - 20},{H[1]}" fill="{CHALK}"/>'
    # the ball runs the bases
    out += ('<g><animateMotion dur="7s" repeatCount="indefinite" '
            'path="M600 470 L850 310 L600 150 L350 310 L600 470"/>'
            + softball(0, 0, 13, spin_s=2, gid="runball") + "</g>")

    def badge(x, y, n):
        return f'<circle cx="{x}" cy="{y}" r="17" fill="{STITCH}" stroke="#fff" stroke-width="2"/>' + txt(x, y + 7, n, 18, "#fff", "b", "middle")

    out += badge(558, 470, "1") + badge(642, 470, "5") + badge(F[0], F[1] - 36, "2") + badge(S[0], S[1] - 36, "3") + badge(T[0], T[1] - 36, "4")

    def card(x, y, w, title, l1, l2):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="98" rx="14" fill="{PANEL}" stroke="#2a3548" stroke-width="2"/>'
                + txt(x + 20, y + 36, title, 22, AMBER, "b") + txt(x + 20, y + 63, l1, 10, CHALK) + txt(x + 20, y + 83, l2, 10, CHALK))

    out += card(20, 396, 300, "1  HOME", "WAKE UP, EVERY", "10 SECONDS")
    out += card(880, 396, 300, "5  RUN SCORES", "SAVE BOOKED.JSON", "SO IT NEVER REPEATS")
    out += card(905, 262, 275, "2  1ST BASE", "ASK CALENDLY FOR", "EVERY OPEN SPOT")
    out += card(690, 70, 400, "3  2ND BASE", "MONDAY 7 PM OPEN?", "NO? 6 PM. NO? 5 PM.")
    out += card(20, 262, 275, "4  3RD BASE", "OPEN THE PAGE, FILL IT,", "CLICK SCHEDULE EVENT")
    out += txt(600, 546, "NO MONDAY SPOT = FOUL BALL. BACK TO THE DUGOUT, TRY AGAIN IN 10 S.", 11, AMBER, "p", "middle")
    return frame(1200, 570, "How a booking happens: wake up, ask Calendly for open spots, pick the latest Monday slot from 7 PM to 5 PM, fill the form and book, then save booked.json", out)


def window():
    days = ["MO", "TU", "WE", "TH", "FR", "SA", "SU", "MO", "TU", "WE", "TH", "FR", "SA", "SU", "MO"]
    x0, w, gap, y = 62, 64, 6, 120
    out = txt(62, 70, "TODAY", 14, CHALK) + txt(1138, 70, "TODAY + 14", 14, CHALK, "p", "end")
    out += f'<line x1="{x0 + w // 2}" y1="80" x2="{x0 + w // 2}" y2="{y - 8}" stroke="{CHALK}" stroke-width="3"/>'
    for i, d in enumerate(days):
        x = x0 + i * (w + gap)
        last = i == len(days) - 1
        fill = GREEN if last else NAVY2
        out += f'<rect x="{x}" y="{y}" width="{w}" height="104" rx="10" fill="{fill}" stroke="{AMBER if last else "#2a3548"}" stroke-width="{4 if last else 2}"/>'
        out += txt(x + w / 2, y + 34, d, 16, CHALK, "p", "middle")
        if last:
            out += txt(x + w / 2, y + 78, "NEW", 18, "#fff", "b", "middle")
            out += f'<rect x="{x - 4}" y="{y - 4}" width="{w + 8}" height="112" rx="12" fill="none" stroke="{AMBER}" stroke-width="3"><animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></rect>'
        else:
            out += txt(x + w / 2, y + 78, "X", 26, "#55627c", "b", "middle")
    out += f'<line x1="{x0 + 14 * (w + gap) + w + 18}" y1="{y + 8}" x2="{x0 + 14 * (w + gap) + w + 18}" y2="{y + 96}" stroke="{DIM}" stroke-width="3" stroke-dasharray="6 6"/>'
    out += txt(62, 268, "X  = ALREADY TAKEN BY OTHER FAMILIES", 12, DIM)
    out += txt(62, 296, "NEW = THE RACE STARTS HERE: A MONDAY ENTERS THE WINDOW", 12, AMBER)
    out += txt(62, 324, "BOOKING OPENS 14 DAYS AHEAD AND CLOSES 2 HOURS BEFORE SAME-DAY LESSONS", 12, DIM)
    return frame(1200, 350, "The booking window: 15 days from today, where only the newest Monday at the far edge is open", out)


def relay():
    x0, per_h = 90, 148
    out = txt(90, 56, "EVERY WATCHER LASTS ABOUT 5 H 40 M, THEN STARTS THE NEXT ONE", 13, AMBER)
    for h in range(0, 6):
        x = x0 + h * per_h
        out += f'<line x1="{x}" y1="90" x2="{x}" y2="262" stroke="#2a3548" stroke-width="2" stroke-dasharray="4 8"/>'
        out += txt(x, 82, f"{h} H", 12, DIM, "p", "middle")
    end = x0 + int(5.67 * per_h)
    out += txt(end, 82, "5 H 40", 12, DIM, "p", "middle")
    out += f'<rect x="{x0}" y="104" width="{end - x0}" height="50" rx="12" fill="{GREEN}"/>'
    out += txt(x0 + 22, 137, "WATCHER #1", 16, "#fff", "b")
    out += f'<rect x="{x0}" y="104" width="{end - x0}" height="50" rx="12" fill="none" stroke="{BALL}" stroke-width="2" stroke-dasharray="3 9"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="3s" repeatCount="indefinite"/></rect>'
    out += f'<path d="M{end} 154 C{end} 190 {end} 190 {end} 206" fill="none" stroke="{AMBER}" stroke-width="4"/>'
    out += f'<polygon points="{end - 9},202 {end + 9},202 {end},218" fill="{AMBER}"/>'
    out += txt(end + 22, 192, "YOUR TURN!", 13, AMBER)
    out += f'<rect x="{end}" y="220" width="1130 - {end}" height="44" rx="12" fill="{NAVY2}" stroke="{GREEN}" stroke-width="3" stroke-dasharray="10 8"/>'.replace("1130 - " + str(end), str(1130 - end))
    out += txt(end + 18, 249, "WATCHER #2 ...", 14, CHALK, "b")
    out += txt(90, 312, "ONE CHECK EVERY 10 SECONDS, ABOUT 2,000 CHECKS PER WATCHER, 24 HOURS A DAY", 12, CHALK)
    out += txt(90, 340, "IF THE RELAY EVER BREAKS, THE BACKUP SCHEDULE STARTS IT AGAIN", 12, DIM)
    return frame(1200, 372, "The relay: watcher number 1 checks Calendly for about 5 hours 40 minutes, then starts watcher number 2", out)


def scoreboard_card():
    rows = [("WINDOW", "02:26 PM - 08:06 PM ET"), ("CHECKS", "2,040"), ("ERRORS", "0"),
            ("MOST SPOTS", "1 OPEN ON CALENDLY"), ("RESULT", "NO MONDAY SLOT YET")]
    out = f'<rect x="2" y="2" width="1196" height="62" rx="18" fill="{STITCH}"/><rect x="2" y="34" width="1196" height="30" fill="{STITCH}"/>'
    out += txt(600, 46, "FINAL SCORE", 26, "#fff", "b", "middle")
    for i, (k, v) in enumerate(rows):
        y = 112 + i * 44
        out += txt(70, y, k, 15, DIM) + txt(400, y, v, 15, AMBER if i < 4 else LED, "p", "start", 'filter="url(#ledglow)"')
    out += txt(1130, 330, "EXAMPLE", 12, DIM, "p", "end")
    return frame(1200, 350, "Example final score at the end of a watcher: checks, errors, most open spots and result", out)


def locker():
    names = [("BOOK_NAME", "NAME ON THE BOOKING"), ("BOOK_EMAIL", "GETS THE CONFIRMATION"),
             ("BOOK_PHONE", "IF THE FORM ASKS"), ("BOOK_NOTES", "THE ATHLETE'S NAME")]
    out = txt(600, 52, "LOCKER ROOM: ENCRYPTED REPO SECRETS", 15, AMBER, "p", "middle")
    for i, (name, what) in enumerate(names):
        x, y, w, h = 36 + i * 292, 80, 268, 250
        out += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{NAVY2}" stroke="#2f4a7d" stroke-width="3"/>'
        for v in range(5):
            out += f'<rect x="{x + 40}" y="{y + 20 + v * 11}" width="{w - 80}" height="5" rx="2" fill="#0b1d3a"/>'
        out += f'<rect x="{x + w // 2 - 26}" y="{y + 100}" width="52" height="40" rx="8" fill="{AMBER}"/>'
        out += f'<path d="M{x + w // 2 - 15} {y + 100} v-16 a15 15 0 0 1 30 0 v16" fill="none" stroke="{AMBER}" stroke-width="7"/>'
        out += txt(x + w // 2, y + 182, name, 20, CHALK, "b", "middle")
        out += txt(x + w // 2, y + 208, "************", 13, LED, "p", "middle")
        out += txt(x + w // 2, y + 232, what, 10, DIM, "p", "middle")
    return frame(1200, 350, "Four encrypted secrets: BOOK_NAME, BOOK_EMAIL, BOOK_PHONE and BOOK_NOTES", out)


DIAGRAMS = {
    "promises.svg": promises, "lineup.svg": lineup, "play.svg": play, "window.svg": window,
    "relay.svg": relay, "scoreboard.svg": scoreboard_card, "locker.svg": locker,
}


def main():
    (HERE / "banner.svg").write_text(banner(), encoding="utf-8")
    for num, title, kicker in HEADERS:
        (HERE / f"h{num}.svg").write_text(header(num, title, kicker), encoding="utf-8")
    (HERE / "footer.svg").write_text(footer(), encoding="utf-8")
    for name, make in DIAGRAMS.items():
        (HERE / name).write_text(make(), encoding="utf-8")
    for p in sorted(HERE.glob("*.svg")):
        print(f"{p.name:12} {p.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
