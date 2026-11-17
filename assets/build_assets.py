"""Regenerate the README artwork in assets/ (banner, section headers, footer).

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
        ("NEXT UP", "THU  7:00 PM ET", AMBER),
        ("BACKUP", "THU  6:00 PM ET", AMBER),
        ("CHECKS", "EVERY 60 SEC", LED),
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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Softball Lesson Bot: books Thursday 7 PM lessons, checks every minute">
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
    <text class="p" x="396" y="76" font-size="13" fill="#fff" text-anchor="middle">HOME OF THE THURSDAY LESSON</text>
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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="See you Thursday at 7 PM">
  {style()}
  <defs><clipPath id="f"><rect width="{W}" height="{H}" rx="24"/></clipPath></defs>
  <g clip-path="url(#f)">
    <rect width="{W}" height="{H}" fill="{NAVY}"/>
    <path d="M0 108 Q600 84 1200 108 L1200 150 L0 150 Z" fill="#1d6b38"/>
    <path d="M0 108 Q600 84 1200 108" fill="none" stroke="#ffd23f" stroke-width="4"/>
    <text class="b" x="600" y="62" font-size="40" fill="#ffd23f" text-anchor="middle">SEE YOU THURSDAY</text>
    <text class="p" x="600" y="90" font-size="13" fill="{CHALK}" text-anchor="middle">7:00 PM ET  *  6:00 PM IF WE MUST  *  NEVER TWICE</text>
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


def main():
    (HERE / "banner.svg").write_text(banner(), encoding="utf-8")
    for num, title, kicker in HEADERS:
        (HERE / f"h{num}.svg").write_text(header(num, title, kicker), encoding="utf-8")
    (HERE / "footer.svg").write_text(footer(), encoding="utf-8")
    for p in sorted(HERE.glob("*.svg")):
        print(f"{p.name:12} {p.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
