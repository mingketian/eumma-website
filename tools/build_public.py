#!/usr/bin/env python3
"""
Build the public site from the working source.

Reads  src/index.html   (working copy: DRAFT banner, board notes, placeholders)
Writes docs/index.html  (what GitHub Pages serves)

Removes, in this order:
  1. the DRAFT status bar at the top of every page
  2. every red-ruled "Needs board input" note
  3. any leftover "To be added" placeholder rows on the Team page

Everything else is copied through untouched, including the assets folder.

    python3 tools/build_public.py          # writes docs/
    python3 tools/build_public.py --check  # just report what would be removed
"""
import io, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "src", "index.html")
OUT  = os.path.join(ROOT, "docs")
ASSETS = os.path.join(ROOT, "assets")

def main():
    check = "--check" in sys.argv
    s = io.open(SRC, encoding="utf-8").read()
    report = []

    n = len(re.findall(r'<div class="proto" id="protobar">', s))
    s = re.sub(r'<a class="skip"[^>]*>.*?</a>\n', '', s, flags=re.S)
    s = re.sub(r'<div class="proto" id="protobar">.*?</div>\s*</div>\n', '', s, flags=re.S)
    report.append(f"DRAFT bar removed: {n}")

    n = len(re.findall(r'<div class="tbd"', s))
    s = re.sub(r'\s*<div class="tbd"[^>]*>.*?</div>', '', s, flags=re.S)
    report.append(f'"Needs board input" notes removed: {n}')

    n = len(re.findall(r'<h3>To be added</h3>', s))
    s = re.sub(r'\s*<div class="person">\s*<div class="ph"[^>]*></div>\s*'
               r'<div class="info">\s*<h3>To be added</h3>.*?</div>\s*</div>', '', s, flags=re.S)
    report.append(f'"To be added" placeholder rows removed: {n}')

    # the prototype bar's JS has nothing left to hook up
    s = re.sub(r'\s*var pb=document\.getElementById\("protobar"\)[^\n]*\n\s*if\(pc\)[^\n]*\n', '\n', s)

    # a section whose only content was placeholders should not ship as an empty heading
    for marker in ("Past Executive Board Members",):
        i = s.find(marker)
        if i < 0: continue
        start = s.rindex("<section", 0, i)
        end = s.index("</section>", i) + len("</section>")
        block = s[start:end]
        if not re.search(r'<div class="person[ "]', block):
            s = s[:start] + s[end:]
            report.append(f'empty section removed: {marker}')

    # the skip link is re-added without the prototype bar above it
    s = s.replace('<header class="site">', '<a class="skip" href="#p-home">Skip to content</a>\n<header class="site">', 1)

    for line in report: print("  " + line)
    # sanity: tags still balanced
    body = s[:s.index("<script>")]
    for tag in ("div", "section", "main", "figure"):
        o = len(re.findall(r"<%s[\s>]" % tag, body)); c = body.count("</%s>" % tag)
        print(f"  {tag}: {o}/{c} {'OK' if o == c else '** MISMATCH **'}")
    if check:
        print("\n--check: nothing written."); return

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(s)
    io.open(os.path.join(OUT, ".nojekyll"), "w").write("")
    # ---- assets -------------------------------------------------------
    # Images are resized for the web on the way in: a 6 MB camera PNG makes the
    # page unusable on a phone, and nothing here is displayed above ~1200px.
    from PIL import Image

    MAXW = 1800
    def emit(src, dst):
        try:
            im = Image.open(src)
        except Exception:
            shutil.copy2(src, dst); return os.path.getsize(dst)
        if im.width > MAXW:
            im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
        if dst.lower().endswith(".png"):
            im.convert("RGBA" if im.mode in ("RGBA", "LA") else "RGB").save(dst, "PNG", optimize=True)
        else:
            im.convert("RGB").save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        return os.path.getsize(dst)

    # start from a clean slate so renamed or removed assets do not linger
    for f in os.listdir(OUT):
        full = os.path.join(OUT, f)
        if os.path.isfile(full) and f not in ("index.html", ".nojekyll"):
            os.remove(full)

    total = 0
    for sub in ("poster", "qr"):
        d = os.path.join(ASSETS, sub)
        if not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            if f.startswith("."): continue
            total += emit(os.path.join(d, f), os.path.join(OUT, f))
            print(f"  {f}")
    for sub in ("posters", "people", "photos"):
        srcd, dstd = os.path.join(ASSETS, sub), os.path.join(OUT, sub)
        shutil.rmtree(dstd, ignore_errors=True)
        if not os.path.isdir(srcd): continue
        files = [f for f in sorted(os.listdir(srcd)) if not f.startswith(".")]
        if not files: continue
        os.makedirs(dstd, exist_ok=True)
        for f in files:
            total += emit(os.path.join(srcd, f), os.path.join(dstd, f))
        print(f"  {sub}/  {len(files)} file(s)")
    if total: print(f"  images total: {total//1024} KB")

    print(f"\nwrote {OUT}/index.html")

main()
