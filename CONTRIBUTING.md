# Maintaining this site

Written for whoever inherits it. It assumes no prior web experience.

## What you need

A Mac or Linux machine with `git` and `python3`. Both are already present on
macOS. Nothing else installs.

```bash
git clone https://github.com/mingketian/eumma-website.git
cd eumma-website
```

## The loop

1. Open `src/index.html` in any text editor.
2. Change what you need. To preview, just double-click the file — it opens in
   your browser and works exactly as the live site does.
3. Build and publish:

```bash
python3 tools/build_public.py
git add -A && git commit -m "what you changed" && git push
```

Wait a minute, then reload the live site.

## Things worth knowing before you edit

**Do not edit `docs/index.html`.** It is overwritten on every build. `src/` is
the real file.

**The DRAFT banner and the red-ruled "needs board input" notes never reach the
public site.** Use them freely in `src/` to leave messages for the rest of the
board; the build strips them.

**Dates drive everything.** Terms, sorting, "what is coming up", the archive
counts and which month the calendar opens on are all derived from the `EVENTS`
array. There is no second place to update.

**Do not invent a date.** If only the month is known write `2025-10-00`. A
made-up exact date is a false statement in a public archive, and the site is
built to display month-only entries correctly.

## Before anything goes live

- Anyone named on the site should be content to be named.
- Every external link should be opened once and confirmed, particularly
  department pages, which move.
- The course table under *Course Advising* is compiled from department documents
  that carry a 2016 revision date. Re-check it against the course atlas each
  August.
- WeChat group QR codes expire after seven days. Only a permanent code — an
  official-account code, or a personal code that leads to an invite — belongs on
  a website.

## If something looks broken

Almost every visual bug in this file's history has been a CSS brace problem: one
unclosed rule silently swallows every rule after it, and a whole section loses
its styling at once. Check that braces balance before looking anywhere else:

```bash
python3 - <<'PY'
import io
s = io.open('src/index.html', encoding='utf-8').read()
css = s[s.index('<style>')+7 : s.index('</style>')]
depth = 0
for n, line in enumerate(css.split('\n'), 1):
    depth += line.count('{') - line.count('}')
    if depth < 0:
        print('extra } at css line', n); depth = 0
print('final depth:', depth, '(0 is correct)')
PY
```
