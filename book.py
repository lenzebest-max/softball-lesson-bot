"""Auto-book a Thursday 7:00 PM (fallback 6:00 PM) Eastern softball lesson on Calendly.

All personal info comes from environment variables (GitHub secrets):
  BOOK_NAME, BOOK_EMAIL, BOOK_PHONE, BOOK_NOTES (player's name)
Optional: EVENT_SLUG (lesson type), DRY_RUN=true (fill + screenshot, never submit),
          SIMULATE_OPEN_SLOT=true (pretend next Thursday 7 PM is open; never books),
          WATCH_MINUTES=N (keep checking every WATCH_INTERVAL seconds, default 60, for N minutes).
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

PROFILE = "gl-softball-lessons"
TZ_NAME = "America/New_York"
TZ = ZoneInfo(TZ_NAME)
THURSDAY = 3
PREFERRED_HOURS = (19, 18)  # 7 PM first, then 6 PM
LOOKAHEAD_DAYS = 15
BOOKED_FILE = Path(__file__).with_name("booked.json")
UA = "Mozilla/5.0 (softball-lesson-bot)"

NAME = os.environ.get("BOOK_NAME", "").strip()
EMAIL = os.environ.get("BOOK_EMAIL", "").strip()
PHONE = os.environ.get("BOOK_PHONE", "").strip()
NOTES = os.environ.get("BOOK_NOTES", "").strip()
EVENT_SLUG = os.environ.get("EVENT_SLUG", "").strip()
DRY_RUN = os.environ.get("DRY_RUN", "").strip().lower() in ("1", "true", "yes")
SIMULATE = os.environ.get("SIMULATE_OPEN_SLOT", "").strip().lower() in ("1", "true", "yes")
WATCH_MINUTES = float(os.environ.get("WATCH_MINUTES", "0") or 0)
WATCH_INTERVAL = float(os.environ.get("WATCH_INTERVAL", "60") or 60)


# ─── ascii art for the run logs ───────────────────────────────────────────────────────────────
BANNER = r"""
        .-"````"-.          _____  ____  ______ _______ ____          _      _
      .'  )    (  '.       / ____|/ __ \|  ____|__   __|  _ \   /\   | |    | |
     /   (      )   \     | (___ | |  | | |__     | |  | |_) | /  \  | |    | |
    |     )    (     |     \___ \| |  | |  __|    | |  |  _ < / /\ \ | |    | |
    |    (      )    |     ____) | |__| | |       | |  | |_) / ____ \| |____| |____
     \    )    (    /     |_____/ \____/|_|       |_|  |____/_/    \_\______|______|
      '. (      ) .'                 _    ___ ___ ___  ___  _  _   ___  ___ _____
        '-......-'                  | |  | __/ __/ __|/ _ \| \| | | _ )/ _ \_   _|
                                    | |__| _|\__ \__ \ (_) | .` | | _ \ (_) || |
                                    |____|___|___/___/\___/|_|\_| |___/\___/ |_|
   ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
"""

BOOKED_ART = r"""
   ______  _____  _____ _   __ ___________ _
   | ___ \|  _  ||  _  | | / /|  ___|  _  \ |
   | |_/ /| | | || | | | |/ / | |__ | | | | |
   | ___ \| | | || | | |    \ |  __|| | | | |
   | |_/ /\ \_/ /\ \_/ / |\  \| |___| |/ /|_|
   \____/  \___/  \___/\_| \_/\____/|___/ (_)
"""


def scoreboard(title, rows, width=56):
    """Rows of (label, value) drawn as a little stadium scoreboard."""
    inner = width - 2
    out = ["╔" + "═" * inner + "╗",
           "║" + f"  {title}".ljust(inner) + "║",
           "╠" + "═" * inner + "╣"]
    for label, value in rows:
        out.append("║" + f"  {label} {'.' * max(2, 14 - len(label))} {value}".ljust(inner)[:inner] + "║")
    out.append("╚" + "═" * inner + "╝")
    return "\n".join(out)


def say_art(text):
    """Print art without ever letting a console encoding problem stop the bot."""
    try:
        print(text, flush=True)
    except Exception:
        pass


def job_summary(markdown):
    """Add to the GitHub Actions run page (no-op outside Actions)."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown + "\n")
    except Exception:
        pass


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def load_booked():
    if BOOKED_FILE.exists():
        return set(json.loads(BOOKED_FILE.read_text() or "[]"))
    return set()


def save_booked(booked):
    BOOKED_FILE.write_text(json.dumps(sorted(booked), indent=2) + "\n")


def pick_event_type():
    types = get_json(f"https://calendly.com/api/booking/profiles/{PROFILE}/event_types")
    print("Lesson types:")
    for t in types:
        dur = t.get("duration") or (re.search(r"(\d+)\s*min", t.get("description", "")) or [None, "?"])[1]
        print(f"  slug={t['slug']!r} name={t['name'].strip()!r} duration={dur} min")
    if EVENT_SLUG:
        for t in types:
            if t["slug"] == EVENT_SLUG:
                return t
        raise SystemExit(f"EVENT_SLUG {EVENT_SLUG!r} not found among lesson types")
    print("EVENT_SLUG not set, using the first lesson type")
    return types[0]


def available_spots(uuid, start, end):
    """All available spots between start and end (inclusive), queried in 7-day chunks."""
    spots = []
    day = start
    while day <= end:
        chunk_end = min(day + timedelta(days=6), end)
        q = urllib.parse.urlencode({
            "timezone": TZ_NAME, "diagnostics": "false",
            "range_start": day.isoformat(), "range_end": chunk_end.isoformat(),
        })
        data = get_json(f"https://calendly.com/api/booking/event_types/{uuid}/calendar/range?{q}")
        for d in data.get("days", []):
            for s in d.get("spots", []):
                if s.get("status") == "available":
                    spots.append(s["start_time"])
        day = chunk_end + timedelta(days=1)
    return spots


def pick_thursday_spot(spots, booked):
    by_date = {}
    for st in spots:
        local = datetime.fromisoformat(st).astimezone(TZ)
        if local.weekday() != THURSDAY or local.minute != 0:
            continue
        by_date.setdefault(local.date().isoformat(), {})[local.hour] = st
    for d in sorted(by_date):
        if d in booked:
            print(f"  {d}: already booked, skipping")
            continue
        for hour in PREFERRED_HOURS:
            if hour in by_date[d]:
                return d, by_date[d][hour]
    return None, None


def field_label(page, el):
    """Text of the label/question attached to a form element."""
    return el.evaluate(
        """(el) => {
            if (el.id) {
                const l = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
                if (l) return l.innerText;
            }
            const by = el.getAttribute('aria-labelledby');
            if (by) return by.split(' ').map(i => document.getElementById(i)?.innerText || '').join(' ');
            let n = el.parentElement;
            for (let i = 0; i < 5 && n; i++, n = n.parentElement) {
                const l = n.querySelector('label, legend');
                if (l) return l.innerText;
            }
            return el.getAttribute('aria-label') || el.name || '';
        }"""
    ).strip()


MOCK_ORIGIN = "https://mock-calendly.test"
MOCK_HTML = Path(__file__).with_name("tests") / "mock_booking.html"


def dismiss_cookies(page):
    for txt in ("Accept All Cookies", "Accept All", "I understand"):
        btn = page.get_by_role("button", name=txt)
        if btn.count() and btn.first.is_visible():
            btn.first.click()
            return


def fill_form(page):
    """Fill name, email, phone and the player question. Returns nothing; raises on failure."""
    dismiss_cookies(page)
    if page.locator("input[name=full_name]").count():
        page.fill("input[name=full_name]", NAME)
    else:
        first, _, last = NAME.partition(" ")
        page.fill("input[name=first_name]", first)
        page.fill("input[name=last_name]", last or first)
    page.fill("input[name=email]", EMAIL)

    tel = page.locator("input[type=tel]")
    if tel.count() and PHONE:
        tel.first.click()
        tel.first.fill(PHONE)

    # Custom questions: put the player's name in the one that asks for the player.
    questions = page.locator("textarea, input[name^=question]")
    player_box = None
    print("Custom questions on the form:")
    for i in range(questions.count()):
        q = questions.nth(i)
        label = field_label(page, q)
        required = q.get_attribute("required") is not None or q.get_attribute("aria-required") == "true"
        print(f"  [{i}] required={required} label={label!r}")
        if player_box is None and re.search(
                r"player|athlete|softball|daughter|son\b|child|pitcher|kid", label, re.I):
            player_box = q
    if player_box is None and questions.count():
        print("No question mentions the player; using the first question box")
        player_box = questions.first
    if player_box is not None and NOTES:
        player_box.fill(NOTES)

    for kind in ("radio", "checkbox"):
        n = page.locator(f"input[type={kind}]").count()
        if n:
            print(f"  note: form has {n} {kind} input(s)")


def submit(page):
    page.get_by_role("button", name=re.compile("Schedule Event", re.I)).click()
    # Success = Calendly's /invitees/ confirmation page, or the coach's external redirect page
    # ("You will be redirected to an external site" is shown under the button).
    form_host = urllib.parse.urlparse(page.url).hostname
    page.wait_for_url(lambda u: "/invitees/" in u or urllib.parse.urlparse(u).hostname != form_host,
                      timeout=60000)
    page.screenshot(path="confirmed.png", full_page=True)
    print(f"Booked! Confirmation: {page.url}")


def new_page(browser):
    return browser.new_page(viewport={"width": 1280, "height": 1600}, locale="en-US",
                            timezone_id=TZ_NAME)


def book(slug, start_time, local_date):
    from playwright.sync_api import sync_playwright

    month = local_date[:7]
    url = (f"https://calendly.com/{PROFILE}/{slug}/{urllib.parse.quote(start_time, safe='')}"
           f"?month={month}&date={local_date}")
    print(f"Opening {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = new_page(browser)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("input[name=email]", timeout=45000)
            fill_form(page)
            page.screenshot(path="form.png", full_page=True)
            if DRY_RUN:
                print("DRY_RUN: form filled, screenshot saved to form.png, NOT submitting")
                return True
            submit(page)
            return True
        except Exception:
            try:
                page.screenshot(path="error.png", full_page=True)
            except Exception:
                pass
            raise
        finally:
            browser.close()


def simulate(slug, start_time, local_date):
    """Pretend a Thursday slot is open. Never books anything with Calendly.

    1. Opens the REAL Calendly form for that time, fills it, screenshots real_form.png (no submit).
    2. Runs the full flow, including clicking "Schedule Event", against a local copy of
       Calendly's form (tests/mock_booking.html) and screenshots mock_form.png + confirmed.png.
    """
    from playwright.sync_api import sync_playwright

    month = local_date[:7]
    real_url = (f"https://calendly.com/{PROFILE}/{slug}/{urllib.parse.quote(start_time, safe='')}"
                f"?month={month}&date={local_date}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        print(f"SIMULATE 1/2: real Calendly form at {real_url} (fill only, never submitted)")
        page = new_page(browser)
        try:
            page.goto(real_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("input[name=email]", timeout=30000)
            fill_form(page)
            page.screenshot(path="real_form.png", full_page=True)
            print("  real form filled -> real_form.png")
        except Exception as e:
            page.screenshot(path="real_page.png", full_page=True)
            print(f"  Calendly did not show a form for this (actually taken) time: {e.__class__.__name__}"
                  " -> real_page.png")
        finally:
            page.close()

        print("SIMULATE 2/2: full booking flow against the local Calendly-style mock form")
        page = new_page(browser)
        html = MOCK_HTML.read_text(encoding="utf-8")
        page.route(f"{MOCK_ORIGIN}/**", lambda route: route.fulfill(
            status=200, content_type="text/html", body=html))
        try:
            page.goto(f"{MOCK_ORIGIN}/{PROFILE}/{slug}/{urllib.parse.quote(start_time, safe='')}"
                      f"?month={month}&date={local_date}")
            page.wait_for_selector("input[name=email]", timeout=10000)
            fill_form(page)
            page.screenshot(path="mock_form.png", full_page=True)
            submit(page)
        except Exception:
            page.screenshot(path="error.png", full_page=True)
            raise
        finally:
            browser.close()


def next_thursday_7pm():
    now = datetime.now(TZ)
    days = (THURSDAY - now.weekday()) % 7 or 7
    t = (now + timedelta(days=days)).replace(hour=19, minute=0, second=0, microsecond=0)
    return t.date().isoformat(), t.isoformat()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    say_art(BANNER)
    mode = ("SIMULATION" if SIMULATE else "DRY RUN" if DRY_RUN
            else "LIVE WATCH" if WATCH_MINUTES > 0 else "LIVE (ONE CHECK)")
    say_art(scoreboard("T O D A Y ' S   G A M E", [
        ("MODE", mode),
        ("TARGET", "Thursday 7:00 PM ET"),
        ("BACKUP", "Thursday 6:00 PM ET"),
        ("LOOK AHEAD", f"{LOOKAHEAD_DAYS} days"),
        ("CHECK EVERY", f"{WATCH_INTERVAL:.0f} s for {WATCH_MINUTES:.0f} min" if WATCH_MINUTES > 0 else "once"),
    ]) + "\n")

    missing = [k for k, v in (("BOOK_NAME", NAME), ("BOOK_EMAIL", EMAIL)) if not v]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

    et = pick_event_type()
    print(f"Using lesson type: {et['name'].strip()} ({et['slug']})")
    if SIMULATE:
        local_date, start_time = next_thursday_7pm()
        print(f"SIMULATE_OPEN_SLOT: pretending {local_date} 7:00 PM ET is open (nothing will be booked)")
        simulate(et["slug"], start_time, local_date)
        print("SIMULATE_OPEN_SLOT: done, booked.json untouched")
        return
    if WATCH_MINUTES > 0 and not DRY_RUN:
        watch(et)
        return
    booked = load_booked()
    today = datetime.now(TZ).date()
    spots = available_spots(et["uuid"], today, today + timedelta(days=LOOKAHEAD_DAYS))
    print(f"{len(spots)} available spot(s) in the next {LOOKAHEAD_DAYS} days")
    local_date, start_time = pick_thursday_spot(spots, booked)

    if not start_time:
        if not DRY_RUN:
            print("No open Thursday 7 PM / 6 PM lesson right now.")
            return
        # Dry run with nothing bookable: look further out for ANY open spot so the form can be tested.
        print("DRY_RUN: no Thursday 7/6 PM spot; using any open spot (up to 90 days) to test the form")
        spots = available_spots(et["uuid"], today, today + timedelta(days=90))
        if not spots:
            print("DRY_RUN: no open spots at all in the next 90 days; nothing to test against.")
            return
        start_time = spots[0]
        local_date = datetime.fromisoformat(start_time).astimezone(TZ).date().isoformat()

    print(f"Target: {local_date} at {datetime.fromisoformat(start_time).astimezone(TZ):%I:%M %p} ET")
    book(et["slug"], start_time, local_date)
    if not DRY_RUN:
        booked.add(local_date)
        save_booked(booked)
        print(f"Recorded {local_date} in booked.json")
        say_art(BOOKED_ART)


def push_booked(local_date):
    """Commit + push booked.json right away so a later crash can't forget a booking."""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    cmds = [
        ["git", "config", "user.name", "github-actions[bot]"],
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        ["git", "add", "booked.json"],
        ["git", "commit", "-m", f"Record booked lesson {local_date}"],
        ["git", "pull", "--rebase", "--quiet"],
        ["git", "push", "--quiet"],
    ]
    for c in cmds:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  warning: {' '.join(c)} failed: {(r.stderr or r.stdout).strip()}")
            return


def watch(et):
    """Check every WATCH_INTERVAL seconds for WATCH_MINUTES, booking any open Thursday 7/6 PM."""
    deadline = time.monotonic() + WATCH_MINUTES * 60
    booked = load_booked()
    checks = failures = most_spots = 0
    new_bookings = []
    started = datetime.now(TZ)
    print(f"WATCH: checking every {WATCH_INTERVAL:.0f}s for {WATCH_MINUTES:.0f} min", flush=True)
    while True:
        checks += 1
        try:
            today = datetime.now(TZ).date()
            spots = available_spots(et["uuid"], today, today + timedelta(days=LOOKAHEAD_DAYS))
            most_spots = max(most_spots, len(spots))
            local_date, start_time = pick_thursday_spot(spots, booked)
            stamp = datetime.now(TZ).strftime("%m-%d %I:%M %p ET")
            if start_time:
                print(f"[{stamp}] OPEN: {local_date} at "
                      f"{datetime.fromisoformat(start_time).astimezone(TZ):%I:%M %p} ET, booking now",
                      flush=True)
                book(et["slug"], start_time, local_date)
                booked.add(local_date)
                save_booked(booked)
                print(f"Recorded {local_date} in booked.json", flush=True)
                push_booked(local_date)
                when = f"{local_date} {datetime.fromisoformat(start_time).astimezone(TZ):%I:%M %p} ET"
                new_bookings.append(when)
                say_art(BOOKED_ART + f"   >>> Thursday {when}  -  see you at the field! <<<\n")
            elif checks == 1 or checks % 30 == 0:
                print(f"[{stamp}] check #{checks}: {len(spots)} open spot(s), no Thursday 7/6 PM yet",
                      flush=True)
        except Exception as e:
            failures += 1
            print(f"check #{checks} failed, will retry: {e!r}", flush=True)
        if time.monotonic() + WATCH_INTERVAL > deadline:
            break
        time.sleep(WATCH_INTERVAL)
    print(f"WATCH: done after {checks} checks", flush=True)
    board = scoreboard("F I N A L   S C O R E", [
        ("INNINGS", f"{started:%m-%d %I:%M %p} - {datetime.now(TZ):%I:%M %p} ET"),
        ("CHECKS", str(checks)),
        ("ERRORS", str(failures)),
        ("MOST SPOTS", f"{most_spots} open on Calendly"),
        ("RESULT", "BOOKED " + ", ".join(new_bookings) if new_bookings else "no Thursday 7/6 PM yet"),
    ], width=64)
    say_art("\n" + board)
    job_summary("### 🥎 Softball Lesson Bot\n\n```text\n" + board + "\n```")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e!r}", file=sys.stderr)
        sys.exit(1)
