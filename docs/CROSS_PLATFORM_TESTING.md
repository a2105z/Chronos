# Cross-Platform `.ics` Testing

This file tracks export compatibility across common calendar clients.

## Automated checks

Current backend tests verify that exported files:

- have valid calendar envelope markers
- include download headers
- can be parsed by `icalendar`
- include expected event fields (`SUMMARY`, `DTSTART`, `DTEND`, `UID`, `DTSTAMP`)
- use CRLF line endings

Run:

```bash
cd backend
pytest tests/test_schedule.py -k export_ics
```

## Manual import checks

Use the same exported file in each target:

- Apple Calendar (macOS)
- Outlook (Windows desktop)
- Google Calendar (web)

Pass condition: import succeeds and event title/time matches what Chronos generated.
