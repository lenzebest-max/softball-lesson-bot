<p align="center">
  <img src="assets/banner.svg" alt="Softball Lesson Bot" width="100%">
</p>

<p align="center">
  <a href="../../actions/workflows/book.yml"><img alt="Booking bot" src="https://github.com/lenzebest-max/softball-lesson-bot/actions/workflows/book.yml/badge.svg"></a>
  <img alt="Python 3.12" src="https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="Playwright" src="https://img.shields.io/badge/Playwright-Chromium-2EAD33?logo=playwright&logoColor=white">
  <img alt="Runs every 5 minutes" src="https://img.shields.io/badge/schedule-every%205%20min-f2c94c">
  <img alt="No personal data in repo" src="https://img.shields.io/badge/personal%20info-secrets%20only-0b1d3a">
</p>

<h3 align="center">🥎 Never miss a Thursday pitching lesson again.</h3>

Coach Giana LaCedra's lessons fill up fast. This bot watches her
[Calendly page](https://calendly.com/gl-softball-lessons) around the clock and books
the **Thursday 7:00 PM (Eastern)** lesson as soon as it opens up. If 7 PM is taken, it
grabs **6:00 PM** instead.

---

## ✨ What it does

| | |
|---|---|
| ⏱️ **Checks every 5 minutes** | A GitHub Actions cron job, so nothing has to run on your computer |
| 🎯 **Targets the right slot** | Thursday 7 PM ET first, 6 PM ET as the fallback, up to 15 days ahead |
| 📝 **Fills the form like a person** | Name, email, phone, and the player's name in the *player* question |
| 🔁 **Never double-books** | Every booked date goes into [`booked.json`](booked.json) and is skipped afterwards |
| 🔒 **Keeps personal info private** | Everything personal lives in encrypted repo secrets, never in the code |
| 📸 **Shows its work** | Screenshots of each run are saved as a downloadable artifact for one day |

## 🧭 How it works

```mermaid
flowchart LR
    A[⏰ Every 5 min] --> B{Bot enabled?}
    B -- no --> Z[💤 Skip]
    B -- yes --> C[🔎 Ask Calendly for open spots]
    C --> D{Thursday 7 PM<br/>or 6 PM open?}
    D -- no --> Z
    D -- yes --> E{Already booked<br/>that Thursday?}
    E -- yes --> Z
    E -- no --> F[🌐 Open the booking page<br/>in headless Chrome]
    F --> G[📝 Fill the form]
    G --> H[✅ Schedule Event]
    H --> I[🗂️ Save date to booked.json]
```

## ⚙️ Setup

**Secrets** (*Settings → Secrets and variables → Actions → Secrets*)

| Secret | What it is |
|---|---|
| `BOOK_NAME` | Name on the booking |
| `BOOK_EMAIL` | Email that gets the confirmation |
| `BOOK_PHONE` | Phone number, used if the form asks for one |
| `BOOK_NOTES` | Player's name, typed into the question that asks for the player |

**Variables** (same page → *Variables*)

| Variable | What it does |
|---|---|
| `EVENT_SLUG` | Which lesson type to book. Set to `individual-pitching-lesson-1`. Every run's log lists the available types. |
| `BOT_ENABLED` | `true` lets the 5-minute schedule book for real. Anything else pauses it. |

## 🧪 Testing without booking

| Test | Command | What you get |
|---|---|---|
| **Dry run** | `gh workflow run book.yml -f dry_run=true` | Fills the real form for an open slot and saves `form.png`. Doesn't submit. |
| **Simulated opening** | `gh workflow run book.yml -f simulate_open_slot=true` | Pretends next Thursday 7 PM is open. Fills the real Calendly form (`real_form.png`, no submit), then runs the whole flow, including *Schedule Event*, against a local copy of the form (`mock_form.png`, `confirmed.png`). |

Screenshots appear under the run's **Artifacts → screenshots**.

## ⏸️ Turning it off

```bash
gh variable set BOT_ENABLED --body false   # pause scheduled bookings
gh workflow disable book.yml               # or switch the workflow off completely
```

Turn it back on with `gh variable set BOT_ENABLED --body true` (or `gh workflow enable book.yml`).

## 🗂️ Files

```
📁 .github/workflows/book.yml   the 5-minute schedule
🐍 book.py                      finds the slot and fills the form
🗒️ booked.json                  Thursdays already booked
🧪 tests/mock_booking.html      Calendly-style form for the simulation
🎨 assets/banner.svg            the banner above
```

<p align="center"><sub>Made for one softball family. Books at most one lesson per Thursday. 🥎</sub></p>
