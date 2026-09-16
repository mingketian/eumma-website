# EUMMA — Emory Undergraduate MatheMatics Association

The club's website. One self-contained `index.html`; no build step, no dependencies,
no framework. Served by GitHub Pages straight from this repository.

## Editing

The source of truth is `prototype/index.html` in the working repository
(`~/Desktop/eumma-website`). Edit there, then regenerate this folder:

```bash
python3 tools/build_public.py
```

That strips the DRAFT banner, the internal "Needs board input" notes and any
unfilled placeholder rows, then writes `site/index.html`.

## Changing events

All events live in one `EVENTS` array inside `index.html`. The calendar, the
archive, the category filters and the poster gallery all read from it, so adding
an event is one entry:

```js
{d:"2026-10-16", t:"Research Panel", time:"5:30–6:30 PM", room:"MSC N304",
 cat:"research", desc:"One or two sentences."}
```

`d` is `YYYY-MM-DD`. Use `00` for the day when only the month is known
(`2025-10-00`); the entry still files under the right term, it just will not
appear on the day grid.

`cat` is one of: `research` · `connect` · `study` · `social` · `compete` · `ai`.

## Images

Drop files in and they appear; leave them out and the block hides itself.

| Path | What |
| --- | --- |
| `eumma-poster-2025.png` | recruitment poster, shown on Join |
| `qr-groupme.png`, `qr-wechat.png` | join QR codes |
| `posters/<date>-<slug>.png` | per-event posters, e.g. `2024-10-30-grad-panel.png` |

## Handover

This repository should be owned by a GitHub **organization**, not a personal
account, with the outgoing and incoming board both listed as owners. Officers
graduate; the site should not leave with them.
