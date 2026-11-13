"""Auto-book a Thursday 7:00 PM (fallback 6:00 PM) Eastern softball lesson on Calendly.

All personal info comes from environment variables (GitHub secrets):
  BOOK_NAME, BOOK_EMAIL, BOOK_PHONE, BOOK_NOTES (player's name)
Optional: EVENT_SLUG (lesson type), DRY_RUN=true (fill + screenshot, never submit).
"""
import json
import os
import re
import sys
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


def book(slug, start_time, local_date):
    from playwright.sync_api import sync_playwright

    month = local_date[:7]
    url = (f"https://calendly.com/{PROFILE}/{slug}/{urllib.parse.quote(start_time, safe='')}"
           f"?month={month}&date={local_date}")
    print(f"Opening {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1600}, locale="en-US",
                                timezone_id=TZ_NAME)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("input[name=email]", timeout=45000)
            for txt in ("Accept All Cookies", "Accept All", "I understand"):
                btn = page.get_by_role("button", name=txt)
                if btn.count() and btn.first.is_visible():
                    btn.first.click()
                    break

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
                if player_box is None and re.search(r"player|athlete|softball|daughter|son\b|child|pitcher",
                                                    label, re.I):
                    player_box = q
            if player_box is None and questions.count():
                print("No question mentions the player; using the first question box")
                player_box = questions.first
            if player_box is not None and NOTES:
                player_box.fill(NOTES)

            # Required radio/checkbox questions would block submission; report them.
            for kind in ("radio", "checkbox"):
                n = page.locator(f"input[type={kind}]").count()
                if n:
                    print(f"  note: form has {n} {kind} input(s)")

            page.screenshot(path="form.png", full_page=True)
            if DRY_RUN:
                print("DRY_RUN: form filled, screenshot saved to form.png, NOT submitting")
                return True

            page.get_by_role("button", name=re.compile("Schedule Event", re.I)).click()
            page.wait_for_url(re.compile(r"/invitees/"), timeout=60000)
            page.screenshot(path="confirmed.png", full_page=True)
            print(f"Booked! Confirmation: {page.url}")
            return True
        except Exception:
            try:
                page.screenshot(path="error.png", full_page=True)
            except Exception:
                pass
            raise
        finally:
            browser.close()


def main():
    missing = [k for k, v in (("BOOK_NAME", NAME), ("BOOK_EMAIL", EMAIL)) if not v]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

    et = pick_event_type()
    print(f"Using lesson type: {et['name'].strip()} ({et['slug']})")
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


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e!r}", file=sys.stderr)
        sys.exit(1)
