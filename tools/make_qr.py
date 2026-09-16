#!/usr/bin/env python3
"""
Generate a QR code in the site's own style (crimson on white, hairline frame).

    python3 tools/make_qr.py groupme "https://groupme.com/join_group/XXXXXXXX/YYYYYYYY"
    python3 tools/make_qr.py wechat  "https://weixin.qq.com/g/..."

Writes assets/qr/qr-<name>.png at 1200px. Sharper than a screenshot, and it
matches the site's palette instead of sitting on it as a foreign blue square.
"""
import os, sys, segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assets", "qr")
CRIMSON = "#9E1B25"

def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    name, data = sys.argv[1], sys.argv[2]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"qr-{name}.png")
    qr = segno.make(data, error="h")          # high correction: survives printing
    qr.save(path, scale=20, border=3, dark=CRIMSON, light="#FFFFFF")
    print(f"wrote {path}  ({qr.designator}, {os.path.getsize(path)//1024} KB)")
    print(f"encodes: {data}")

main()
