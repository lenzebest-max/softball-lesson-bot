# softball-lesson-bot

Every 5 minutes, GitHub Actions checks Coach Giana LaCedra's Calendly
(https://calendly.com/gl-softball-lessons) for an open **Thursday 7:00 PM Eastern**
lesson (falling back to 6:00 PM) and books it. Each booked date is recorded in
`booked.json` so the same Thursday is never booked twice.

## Setup

Repo **secrets** (Settings → Secrets and variables → Actions → Secrets):

| Secret | Meaning |
| --- | --- |
| `BOOK_NAME` | Name on the booking |
| `BOOK_EMAIL` | Email for the confirmation |
| `BOOK_PHONE` | Phone number (used if the form asks for one) |
| `BOOK_NOTES` | Player's name (goes into the question that asks for the player) |

Repo **variables** (same page → Variables):

| Variable | Meaning |
| --- | --- |
| `EVENT_SLUG` | Which lesson type to book (the run log lists them). Defaults to the first type. |
| `BOT_ENABLED` | `true` to let the 5-minute schedule book for real. Anything else = off. |

## Test

Actions → *Book softball lesson* → *Run workflow* with **dry_run** checked. The bot fills
the form, saves `form.png` in the *screenshots* artifact and does not submit.

```
gh workflow run book.yml -f dry_run=true
```

## Turn it off

```
gh variable set BOT_ENABLED --body false     # stop scheduled bookings
gh workflow disable book.yml                 # or disable the workflow entirely
```
