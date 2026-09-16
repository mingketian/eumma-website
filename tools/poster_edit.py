#!/usr/bin/env python3
"""
Edit the EUMMA recruitment poster without touching anything that must not move.

Three changes:
  1. "Emory University"  ->  "Emory Undergraduate"   (title line redrawn; the
     coloured MATH bubble letters are lifted out as a sprite and pasted back,
     so the hardest part of the artwork is preserved rather than imitated)
  2. "We are the only Math Club at Emory"  ->  "We are Emory's math club since
     2005"  (only the first line of the centred paragraph is redrawn)
  3. the black Executive Board panel  ->  a white rounded card with a soft
     shadow, in the same visual language as the Kaggle card

Usage
  python3 tools/poster_edit.py assets/poster/eumma-poster-2025.png --probe
      detect regions, write *-probe.png with the detection drawn on top,
      change nothing.
  python3 tools/poster_edit.py assets/poster/eumma-poster-2025.png
      write *-v2.png
"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

# ---------------------------------------------------------------- detection
def dark_mask(px, w, h, thr=110):
    return [[max(px[x, y][:3]) < thr for x in range(w)] for y in range(h)]

def row_dark_counts(im, x0, x1, thr=110):
    px = im.load(); w, h = im.size
    out = []
    for y in range(h):
        c = 0
        for x in range(x0, x1, 2):
            if max(px[x, y][:3]) < thr: c += 1
        out.append(c * 2)
    return out

def bands(counts, lo, hi, minrun, floor):
    """contiguous row runs between lo..hi whose dark count exceeds floor"""
    runs, s = [], None
    for y in range(lo, hi):
        if counts[y] > floor:
            if s is None: s = y
        else:
            if s is not None and y - s >= minrun: runs.append((s, y))
            s = None
    if s is not None and hi - s >= minrun: runs.append((s, hi))
    return runs

def find_title(im):
    w, h = im.size
    counts = row_dark_counts(im, int(w * .12), int(w * .88))
    rs = bands(counts, int(h * .04), int(h * .22), max(6, h // 120), w * .012)
    if not rs: raise SystemExit("could not find the title line")
    return max(rs, key=lambda r: r[1] - r[0])

def find_colour_group(im, y0, y1):
    """the saturated MATH bubble letters inside the title band"""
    px = im.load(); w, _ = im.size
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(w):
            r, g, b = px[x, y][:3]
            mx, mn = max(r, g, b), min(r, g, b)
            if mx > 90 and (mx - mn) > 70:
                xs.append(x); ys.append(y)
    if not xs: raise SystemExit("could not find the coloured MATH letters")
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1

def find_black_panel(im):
    """largest near-black filled region — the Executive Board box"""
    px = im.load(); w, h = im.size
    step = 3
    best = None
    rows = {}
    for y in range(int(h * .25), int(h * .70), step):
        run_s, runs = None, []
        for x in range(0, w, step):
            r, g, b = px[x, y][:3]
            blk = (r < 70 and g < 70 and b < 70)
            if blk:
                if run_s is None: run_s = x
            else:
                if run_s is not None and x - run_s > w * .20: runs.append((run_s, x))
                run_s = None
        if run_s is not None and w - run_s > w * .20: runs.append((run_s, w))
        if runs: rows[y] = max(runs, key=lambda r: r[1] - r[0])
    if not rows: raise SystemExit("could not find the black panel")
    ys = sorted(rows)
    groups, cur = [], [ys[0]]
    for a, b in zip(ys, ys[1:]):
        if b - a <= step * 3: cur.append(b)
        else: groups.append(cur); cur = [b]
    groups.append(cur)
    g = max(groups, key=len)
    x0 = min(rows[y][0] for y in g); x1 = max(rows[y][1] for y in g)
    return x0, g[0] - step, x1, g[-1] + step

def find_paragraph_first_line(im, title_bottom):
    """the 'Who Are We?' heading, then the first body line under it"""
    w, h = im.size
    counts = row_dark_counts(im, int(w * .20), int(w * .80))
    rs = bands(counts, title_bottom + int(h * .012), int(h * .40),
               max(4, h // 200), w * .008)
    if len(rs) < 3: raise SystemExit("could not find the body paragraph")
    # rs[0] = tagline, rs[1] = "Who Are We?", rs[2] = first body line
    return rs[1], rs[2]

# ---------------------------------------------------------------- painting
def row_bg(im, y, exclude=None):
    """modal light colour of a row — the poster ground, which is near-flat"""
    px = im.load(); w, _ = im.size
    buckets = {}
    for x in range(0, w, 2):
        if exclude and exclude[0] <= x < exclude[1]: continue
        r, g, b = px[x, y][:3]
        if min(r, g, b) > 205:
            k = (r // 3 * 3, g // 3 * 3, b // 3 * 3)
            buckets[k] = buckets.get(k, 0) + 1
    if not buckets: return (245, 245, 245)
    return max(buckets.items(), key=lambda kv: kv[1])[0]

def erase(im, box, sample_from=None):
    """fill a box with the ground colour, sampled row by row so any vertical
       gradient in the poster survives"""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        src = y if sample_from is None else sample_from
        d.line([(x0, y), (x1, y)], fill=row_bg(im, src, exclude=(x0, x1)))

def ink_colour(im, box, dark=True):
    px = im.load(); x0, y0, x1, y1 = box
    best, cnt = None, {}
    for y in range(y0, y1):
        for x in range(x0, x1, 2):
            r, g, b = px[x, y][:3]
            if dark and max(r, g, b) < 90:
                k = (r // 6 * 6, g // 6 * 6, b // 6 * 6); cnt[k] = cnt.get(k, 0) + 1
    return max(cnt.items(), key=lambda kv: kv[1])[0] if cnt else (17, 17, 17)

def crimson(im):
    """sample the red banner"""
    px = im.load(); w, h = im.size
    cnt = {}
    for y in range(int(h * .50), int(h * .68), 2):
        for x in range(int(w * .25), int(w * .75), 3):
            r, g, b = px[x, y][:3]
            if r > 95 and g < 75 and b < 75:
                k = (r // 6 * 6, g // 6 * 6, b // 6 * 6); cnt[k] = cnt.get(k, 0) + 1
    return max(cnt.items(), key=lambda kv: kv[1])[0] if cnt else (140, 21, 21)

def fit_size(text, fpath, target_cap, lo=10, hi=400):
    """pick the point size whose cap height matches the original"""
    best, bd = lo, 1e9
    for s in range(lo, hi):
        f = font(fpath, s)
        a, b = f.getbbox("H")[1], f.getbbox("H")[3]
        d = abs((b - a) - target_cap)
        if d < bd: bd, best = d, s
        if (b - a) > target_cap * 1.6: break
    return best

def cap_height(im, box):
    """height of the leftmost all-caps cluster in a band ('EUMMA')"""
    px = im.load(); x0, y0, x1, y1 = box
    cols = []
    for x in range(x0, x1):
        if any(max(px[x, y][:3]) < 110 for y in range(y0, y1)): cols.append(x)
    if not cols: return y1 - y0
    lead_end = cols[0]
    for a, b in zip(cols, cols[1:]):
        if b - a > (x1 - x0) * .02: break
        lead_end = b
    ys = [y for y in range(y0, y1)
          if any(max(px[x, y][:3]) < 110 for x in range(cols[0], lead_end + 1))]
    return (max(ys) - min(ys) + 1) if ys else (y1 - y0)

def rounded_card(im, box, radius, fill=(255, 255, 255), shadow=True):
    x0, y0, x1, y1 = box
    if shadow:
        pad = int((y1 - y0) * .5)
        lay = Image.new("RGBA", (im.width, im.height), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle(
            [x0 + 2, y0 + int((y1 - y0) * .07), x1 + 2, y1 + int((y1 - y0) * .09)],
            radius=radius, fill=(90, 80, 85, 62))
        lay = lay.filter(ImageFilter.GaussianBlur(pad * .30))
        im.alpha_composite(lay) if im.mode == "RGBA" else \
            im.paste(Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB"), (0, 0))
    ImageDraw.Draw(im).rounded_rectangle(box, radius=radius, fill=fill)

def centre_text(d, cx, cy, text, f, fill):
    b = d.textbbox((0, 0), text, font=f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), text, font=f, fill=fill)

# ---------------------------------------------------------------- main
def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    src = sys.argv[1]; probe = "--probe" in sys.argv
    im = Image.open(src).convert("RGB")
    W, H = im.size
    print(f"poster: {W}x{H}")

    ty0, ty1 = find_title(im)
    tpad = max(4, H // 150)
    tband = (0, max(0, ty0 - tpad), W, min(H, ty1 + tpad))
    cx0, cy0, cx1, cy1 = find_colour_group(im, ty0, ty1)
    bx = find_black_panel(im)
    whoami, line1 = find_paragraph_first_line(im, ty1)
    cap = cap_height(im, (int(W * .12), ty0, int(W * .45), ty1))
    ink = ink_colour(im, (int(W * .12), ty0, int(W * .45), ty1))
    red = crimson(im)
    print(f"  title band   y {ty0}-{ty1}   cap height {cap}px   ink {ink}")
    print(f"  MATH sprite  x {cx0}-{cx1}  y {cy0}-{cy1}")
    print(f"  black panel  {bx}")
    print(f"  'Who Are We' y {whoami[0]}-{whoami[1]} | first body line y {line1[0]}-{line1[1]}")
    print(f"  crimson      {red}")

    if probe:
        pv = im.copy(); d = ImageDraw.Draw(pv)
        d.rectangle(tband, outline=(255, 0, 0), width=3)
        d.rectangle((cx0, cy0, cx1, cy1), outline=(0, 160, 255), width=3)
        d.rectangle(bx, outline=(0, 200, 80), width=4)
        d.rectangle((int(W * .18), line1[0], int(W * .82), line1[1]), outline=(255, 140, 0), width=3)
        out = os.path.splitext(src)[0] + "-probe.png"; pv.save(out)
        print("wrote", out); return

    # ---- 1. title -------------------------------------------------------
    sprite = im.crop((cx0, tband[1], cx1, tband[3]))
    erase(im, tband, sample_from=max(0, tband[1] - tpad * 3))
    size = fit_size("EUMMA", "poppins-600.ttf", cap)
    f = font("poppins-600.ttf", size)
    pre, post = "EUMMA (Emory Undergraduate ", "eMatics Association)"
    d = ImageDraw.Draw(im)
    wpre = d.textlength(pre, font=f); wpost = d.textlength(post, font=f)
    wspr = sprite.width
    total = wpre + wspr + wpost
    x = (W - total) / 2
    base = ty0 - f.getbbox("H")[1] + (cap - (f.getbbox("H")[3] - f.getbbox("H")[1])) / 2
    d.text((x, base), pre, font=f, fill=ink)
    im.paste(sprite, (int(round(x + wpre)), tband[1]))
    d.text((x + wpre + wspr, base), post, font=f, fill=ink)
    print(f"  title redrawn at {size}pt Poppins SemiBold, MATH sprite preserved")

    # ---- 2. first body line --------------------------------------------
    bpad = max(2, H // 400)
    bband = (int(W * .15), line1[0] - bpad, int(W * .85), line1[1] + bpad)
    bcap = cap_height(im, (int(W * .22), line1[0], int(W * .50), line1[1]))
    berase = (0, bband[1], W, bband[3])
    erase(im, berase, sample_from=max(0, bband[1] - bpad * 4))
    bsize = fit_size("W", "poppins-600.ttf", bcap)
    bf = font("poppins-600.ttf", bsize)
    newline = "We are Emory's math club since 2005, a student-led community exploring mathematics and"
    d = ImageDraw.Draw(im)
    bbase = line1[0] - bf.getbbox("H")[1] + (bcap - (bf.getbbox("H")[3] - bf.getbbox("H")[1])) / 2
    d.text((W / 2 - d.textlength(newline, font=bf) / 2, bbase), newline, font=bf, fill=ink)
    print(f"  'only Math Club' line redrawn at {bsize}pt")

    # ---- 3. black panel -> white card -----------------------------------
    px0, py0, px1, py1 = bx
    erase(im, (px0 - 6, py0 - 6, px1 + 6, py1 + 6), sample_from=max(0, py0 - 30))
    rad = int((py1 - py0) * .22)
    rounded_card(im, (px0, py0, px1, py1), rad)
    d = ImageDraw.Draw(im)
    ch = (py1 - py0)
    f1 = font("poppins-600.ttf", fit_size("H", "poppins-600.ttf", int(ch * .21)))
    f2 = font("poppins-500.ttf", fit_size("H", "poppins-500.ttf", int(ch * .155)))
    centre_text(d, (px0 + px1) / 2, py0 + ch * .38, "No dues  ·  No application", f1, red)
    centre_text(d, (px0 + px1) / 2, py0 + ch * .68, "Every major welcome", f2, (60, 56, 62))
    print("  black panel replaced with a white card")

    out = os.path.splitext(src)[0] + "-v2.png"
    im.save(out); print("wrote", out)

main()
