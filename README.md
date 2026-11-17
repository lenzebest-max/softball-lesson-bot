<p align="center">
  <img src="assets/banner.svg" alt="Softball Lesson Bot: books the Thursday 7 PM pitching lesson, checks every minute" width="100%">
</p>

<p align="center">
  <a href="../../actions/workflows/book.yml"><img alt="Booking bot" src="https://github.com/lenzebest-max/softball-lesson-bot/actions/workflows/book.yml/badge.svg"></a>
  <img alt="Python 3.12" src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Playwright" src="https://img.shields.io/badge/Playwright-Chromium-2EAD33?style=for-the-badge&logo=playwright&logoColor=white">
  <img alt="Checks every 60 s" src="https://img.shields.io/badge/checks-every%2060%20s-ffb627?style=for-the-badge">
  <img alt="Personal info: secrets only" src="https://img.shields.io/badge/personal%20info-secrets%20only-d7263d?style=for-the-badge">
</p>

<h3 align="center">🥎 Never miss a Thursday pitching lesson again.</h3>

```text
      __O                                                                 ┌──────────────────────┐
     / /|\__    ·   ˙   ·   .   ·   ˙   ·   .   ·   ˙   ·   .   ·   ˙   · │ THU 7:00 PM ET       │
       / \    ● ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ > │ [ SCHEDULE EVENT ]   │
    ═══════════                                                           └──────────────────────┘

      THE BOT       <──────────────────── 43 ft ────────────────────>    CALENDLY
```

Coach Giana LaCedra's lessons fill up fast. This bot watches her
[Calendly page](https://calendly.com/gl-softball-lessons) around the clock and books the
**Thursday 7:00 PM (Eastern)** lesson the moment it opens up. If 7 PM is taken, it grabs
**6:00 PM** instead.

```text
            .-"````"-.
          .'  )    (  '.
         /   (      )   \         BOOKS ONE LESSON PER THURSDAY.
        |     )    (     |        NEVER TWICE. NEVER ON YOUR COMPUTER.
        |    (      )    |        NEVER WITH YOUR INFO IN THE CODE.
         \    )    (    /
          '. (      ) .'
            '-......-'
```

<p align="center"><img src="assets/h01.svg" alt="01 The lineup: what the bot does" width="100%"></p>

```text
╔════╤════════════════════════╤═══════════════════════════════════════════════════╗
║ #  │ PLAYER                 │ JOB                                               ║
╟────┼────────────────────────┼───────────────────────────────────────────────────╢
║ 1  │ The Watcher         CF │ checks Calendly every 60 s, day and night         ║
║ 2  │ The Picker          SS │ Thursday 7 PM ET first, 6 PM ET as backup         ║
║ 3  │ The Form-Filler      P │ name, email, phone and the athlete's name         ║
║ 4  │ The Scorekeeper      C │ booked.json, so a Thursday is never booked twice  ║
║ 5  │ The Vault           1B │ personal info lives only in encrypted secrets     ║
║ 6  │ The Photographer    RF │ screenshots of every run, kept for one day        ║
║ 7  │ The Relay           2B │ hands off to a fresh watcher every ~5 h 40 m      ║
╚════╧════════════════════════╧═══════════════════════════════════════════════════╝
```

<p align="center"><img src="assets/h02.svg" alt="02 The play: how a booking happens" width="100%"></p>

Every minute, the bot runs the bases. If there's no Thursday spot at 2nd base, that's a
**foul ball**: back to the dugout, try again in 60 seconds.

```text
                                ┌─────────────────────────────┐
                                │ 3  2ND BASE                 │
                                │    Thursday 7 PM open?      │
                                │    no? then 6 PM            │
                                └──────────────┬──────────────┘
                                               ●
                                             ╱   ╲
                                           ╱       ╲
                                         ╱           ╲
                                       ╱               ╲
┌─────────────────────────┐          ╱                   ╲       ┌────────────────────────┐
│ 4  3RD BASE             │        ╱                       ╲     │ 2  1ST BASE            │
│    open the page, fill  │──────●                           ●───│    ask Calendly for    │
│    it, Schedule Event   │        ╲                       ╱     │    every open spot     │
└─────────────────────────┘          ╲                   ╱       └────────────────────────┘
                                       ╲               ╱
                                         ╲           ╱
                                           ╲       ╱
                                             ╲   ╱
                                               ●
                                               │
                          ┌────────────────────┴────────────────────┐
                          │ 1  HOME  wake up, every 60 s            │
                          │ 5  RUN SCORES  save booked.json         │
                          └─────────────────────────────────────────┘
```

<p align="center"><img src="assets/h03.svg" alt="03 The window: when spots open up" width="100%"></p>

Coach LaCedra's Calendly says *"Booking opens 14 days in advance and closes 2 hours before
same-day lessons."* So each Thursday becomes bookable exactly two weeks ahead, at the far
edge of the calendar, and everything inside the window is usually gone already.

```text
  TODAY                                                   TODAY + 14
    ▼                                                       ▼
  ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐ - - - - - -
  │ TH│ FR│ SA│ SU│ MO│ TU│ WE│ TH│ FR│ SA│ SU│ MO│ TU│ WE│ TH│   not open yet
  │ x │ x │ x │ x │ x │ x │ x │ x │ x │ x │ x │ x │ x │ x │NEW│
  └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘ - - - - - -
                                                            ▲ the race starts here
   x  = already taken by other families
```

That's why the bot never sleeps: a Thursday spot only shows up when a new day enters the
window or when somebody cancels, and either way the first family to click gets it.

<p align="center"><img src="assets/h04.svg" alt="04 The relay: the always-on watcher" width="100%"></p>

GitHub's built-in schedule can run hours late, so every live run is a **watcher**: it checks
Calendly once a minute for about 5 h 40 m (just under GitHub's 6-hour job limit), books the
moment a Thursday 7 PM / 6 PM slot opens, then starts the next watcher itself. Only one watcher
runs at a time, and the repo is public, so the minutes are free.

```text
  0h        1h        2h        3h        4h        5h  5h40m
  ├─────────┼─────────┼─────────┼─────────┼─────────┼──────┤
  ═════════════════════════════════════════════════════════┐  watcher #1
                                                           │ "your turn!"
                                                           └═════════════════════>  watcher #2 ...

  · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·
  one check a minute  ≈  340 checks per watcher, 24/7
```

The `*/5` schedule is just a backup: if the relay ever breaks, the next scheduled run starts it
again. A watcher that dies within 20 minutes doesn't relay, so a broken setup can't spin.

Every run starts its log like this, and ends with a **final score** on the run's summary page:

```text
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

╔══════════════════════════════════════════════════════╗
║  T O D A Y ' S   G A M E                             ║
╠══════════════════════════════════════════════════════╣
║  MODE .......... LIVE WATCH                          ║
║  TARGET ........ Thursday 7:00 PM ET                 ║
║  BACKUP ........ Thursday 6:00 PM ET                 ║
║  LOOK AHEAD .... 15 days                             ║
║  CHECK EVERY ... 60 s for 340 min                    ║
╚══════════════════════════════════════════════════════╝

WATCH: checking every 60s for 340 min
[11-16 02:26 PM ET] check #1: 0 open spot(s), no Thursday 7/6 PM yet
[11-16 02:56 PM ET] check #30: 0 open spot(s), no Thursday 7/6 PM yet
...
```

Restart the relay by hand: `gh workflow run book.yml -f dry_run=false`

<p align="center"><img src="assets/h05.svg" alt="05 Spring training: setup and secrets" width="100%"></p>

```text
  ┌── LOCKER ROOM · encrypted repo secrets ────────────────────────┐
  │ BOOK_NAME    ************       name on the booking            │
  │ BOOK_EMAIL   ****************   gets the confirmation          │
  │ BOOK_PHONE   **********         if the form asks               │
  │ BOOK_NOTES   ********           the athlete's name             │
  └────────────────────────────────────────────────────────────────┘
```

**Secrets** live under *Settings → Secrets and variables → Actions → Secrets*. Nothing personal is
ever written into the code.

| Secret | What it is |
|---|---|
| `BOOK_NAME` | Name on the booking |
| `BOOK_EMAIL` | Email that gets the confirmation |
| `BOOK_PHONE` | Phone number, used if the form asks for one |
| `BOOK_NOTES` | Player's name, typed into the "Athletes name" question |

**Variables** (same page → *Variables*)

| Variable | What it does |
|---|---|
| `EVENT_SLUG` | Which lesson type to book. Set to `individual-pitching-lesson-1`. Every run's log lists the available types. |
| `BOT_ENABLED` | `true` lets the bot book for real. Anything else pauses every real booking, however the run was started. |

<p align="center"><img src="assets/h06.svg" alt="06 Batting practice: testing without booking" width="100%"></p>

| Test | Command | What you get |
|---|---|---|
| ⚾ **Dry run** | `gh workflow run book.yml -f dry_run=true` | Fills the real form for an open slot and saves `form.png`. Doesn't submit. |
| 🎯 **Simulated opening** | `gh workflow run book.yml -f simulate_open_slot=true` | Pretends next Thursday 7 PM is open. Fills the real Calendly form (`real_form.png`, no submit), then runs the whole flow, including *Schedule Event*, against a local copy of the form (`mock_form.png`, `confirmed.png`). |

Screenshots appear under the run's **Artifacts → screenshots**.

<p align="center"><img src="assets/h07.svg" alt="07 Rain delay: turning it off" width="100%"></p>

```text
            .--.                 .-.
         .-(    ).            .-(   ).
        (___.__)__)  /        (___.__)__)
         ' ' ' ' '              ' ' ' '
         ' ' ' '     R A I N   D E L A Y    ' ' '
```

```bash
gh variable set BOT_ENABLED --body false               # stops the relay after the current watcher
gh run list --workflow book.yml --status in_progress   # then cancel the running watcher now:
gh run cancel <run id>
gh workflow disable book.yml                           # or switch the workflow off completely
```

Back on the field: `gh variable set BOT_ENABLED --body true` (or `gh workflow enable book.yml`).

<p align="center"><img src="assets/h08.svg" alt="08 The dugout: what's in the repo" width="100%"></p>

```text
  ┌── THE DUGOUT ────────────────────────────────────────────────────────┐
  │ .github/workflows/book.yml   the watcher relay + backup schedule     │
  │ book.py                      finds the slot, fills the form          │
  │ booked.json                  Thursdays already booked                │
  │ tests/mock_booking.html      Calendly-style form for practice        │
  │ assets/build_assets.py       draws the banner + headers              │
  │ assets/*.svg                 the scoreboard art you see here         │
  └──────────────────────────────────────────────────────────────────────┘
```

<p align="center"><img src="assets/footer.svg" alt="See you Thursday at 7 PM" width="100%"></p>

<p align="center"><sub>Made for one softball family. Books at most one lesson per Thursday. 🥎</sub></p>
<p align="center"><sub>Fonts: <a href="https://fonts.google.com/specimen/Bungee">Bungee</a> by David Jonathan Ross and
<a href="https://fonts.google.com/specimen/Press+Start+2P">Press Start 2P</a> by CodeMan38, both under the SIL Open Font License.</sub></p>
