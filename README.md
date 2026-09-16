# EUMMA

**Website for the Emory Undergraduate MatheMatics Association.**

### → **[mingketian.github.io/eumma-website](https://mingketian.github.io/eumma-website/)**

A single self-contained HTML file. No framework, no build pipeline, no
dependencies, no server. It opens correctly by double-clicking it, and GitHub
Pages serves the same file unchanged.

That is a deliberate choice: this site has to be maintained by whoever is on the
board in four years, and the surest way for a student project to die is to
require a toolchain nobody remembers how to install.

---

## Layout

| Path | Contents |
| --- | --- |
| `src/index.html` | **Working source.** Carries the DRAFT banner and the internal "needs board input" notes. Edit this. |
| `docs/index.html` | **What the public sees.** Generated from `src/`; GitHub Pages serves this folder. Never edit by hand. |
| `assets/` | Poster, QR codes, per-event posters, logo. |
| `tools/` | The three scripts below. |

## Editing the site

Edit `src/index.html`, then regenerate the public copy and push:

```bash
python3 tools/build_public.py
git add -A && git commit -m "describe the change" && git push
```

The live site updates within a minute or two. `build_public.py` strips the DRAFT
banner, the internal board notes, and any unfilled placeholder rows, and removes
sections that are left empty as a result. It prints what it removed and checks
that every HTML tag is still balanced.

## Adding an event

Every event lives in one `EVENTS` array near the top of the `<script>` block.
The month calendar, the archive, the category filters and the poster gallery all
read from it, so one entry is the whole job:

```js
{d:"2026-10-16", t:"Research Panel", time:"5:30–6:30 PM", room:"MSC N304",
 cat:"research", desc:"One or two sentences about what it covers."}
```

| Field | Notes |
| --- | --- |
| `d` | `YYYY-MM-DD`. Use `00` for the day when only the month is known (`2025-10-00`) — it still files under the correct term, it just will not appear on the day grid. |
| `cat` | One of `research` · `connect` · `study` · `social` · `compete` · `ai`. This drives the colour used across the site. |
| `room` | Leave `""` if unknown rather than guessing. |

Events sort themselves, group themselves by term, and count themselves.

## Adding images

Drop a file in and it appears. Leave it out and the block hides itself — there
are no broken-image placeholders on the live site.

| File | Where it shows |
| --- | --- |
| `assets/poster/eumma-poster-2025.png` | Join page |
| `assets/qr/qr-groupme.png`, `assets/qr/qr-wechat.png` | Join page |
| `assets/posters/<date>-<slug>.png` | Events page gallery |

Event poster filenames are derived from the event itself, so no second list is
maintained: `2024-10-30-grad-panel.png`, `2024-11-07-game-night.png`.

## Tools

| Script | What it does |
| --- | --- |
| `tools/build_public.py` | Builds `docs/` from `src/`. Run before every push. |
| `tools/make_qr.py` | Generates a QR code in the site's own palette. `python3 tools/make_qr.py groupme "https://groupme.com/join_group/…"` |
| `tools/poster_edit.py` | Edits the recruitment poster: retitles it and replaces the board-positions panel, preserving the coloured MATH lettering as a sprite. |

## Design

White ground, `#9E1B25` crimson as the only interface colour, and six subject
hues derived from the four coloured letters of **MATH** in the club's own logo.
Those hues are a legend, not decoration: the same colour follows a category
through the activity cards, the event tags and the calendar dots.

Typography is one IBM Plex superfamily — Serif for headings, Sans for text, Mono
for anything with a number in it — plus Fredoka for the masthead wordmark alone,
where it echoes the poster.

The masthead is a live drawing: level sets of a non-convex objective *f*, with an
ensemble of momentum gradient-descent trajectories running on it. It respects
`prefers-reduced-motion` and pauses when off-screen.

## Handover

This repository currently sits under a personal account. **Before the current
board graduates it should be transferred to a GitHub organisation owned by the
club**, with the outgoing and incoming boards both listed as owners. GitHub
redirects the old URL after a transfer, but anything already printed is safer
pointing at a custom domain — which can be attached at any time and survives
every future move.

Officers graduate. The site should not leave with them.
