#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成品牌与分享图：站点 OG、app 图标、每个机场专属 OG 卡片。"""
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(BASE, "data", "airports.json"), encoding="utf-8"))
AIR = DATA["airports"]
os.makedirs(os.path.join(BASE, "assets", "og"), exist_ok=True)

BG = (6, 9, 23)
INK = (234, 238, 252)
MUT = (150, 160, 200)
CYAN = (53, 224, 212)

def hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ---- fonts (Noto Sans CJK SC / Windows 微软雅黑 fallback) ----
def load_cjk(bold=False):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc" % ("Bold" if bold else "Regular"),
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for f in candidates:
        if not os.path.exists(f):
            continue
        for idx in range(12):
            try:
                ft = ImageFont.truetype(f, 40, index=idx)
                name = ft.getname()[0]
                if "SC" in name or "YaHei" in name or "Hei" in name or "Sun" in name or idx == 0:
                    return f, idx
            except Exception:
                if idx == 0:
                    break
                continue
        try:
            ImageFont.truetype(f, 40)
            return f, 0
        except Exception:
            continue
    # last resort: PIL default (Latin only)
    return None, 0

REG_F, REG_I = load_cjk(False)
BLD_F, BLD_I = load_cjk(True)
def font(size, bold=False):
    path = BLD_F if bold else REG_F
    idx = BLD_I if bold else REG_I
    if not path:
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(path, size, index=idx)
    except Exception:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

def grad_h(w, h, c1, c2):
    img = Image.new("RGB", (w, h)); d = ImageDraw.Draw(img)
    for x in range(w):
        t = x / max(1, w - 1)
        d.line([(x, 0), (x, h)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return img

def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], r, fill=255); return m

def aurora(W, H):
    base = Image.new("RGB", (W, H), BG)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    blobs = [((-160, -160, W*0.5, H*0.7), (53, 224, 212, 115)),
             ((W*0.25, -120, W*0.85, H*0.75), (126, 123, 255, 95)),
             ((W*0.55, H*0.2, W*1.15, H*1.2), (255, 106, 213, 110))]
    for box, col in blobs:
        d.ellipse(box, fill=col)
    layer = layer.filter(ImageFilter.GaussianBlur(150))
    base = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    # faint dots texture
    d2 = ImageDraw.Draw(base, "RGBA")
    import random; random.seed(7)
    for _ in range(46):
        x, y = random.randint(0, W), random.randint(0, int(H*0.9))
        d2.ellipse([x, y, x+3, y+3], fill=(200, 210, 255, 60))
    return base

def emblem_img(a, s):
    c1, c2 = hx(a["accent"][0]), hx(a["accent"][1])
    g = grad_h(s, s, c1, c2).convert("RGBA"); g.putalpha(rounded_mask(s, s, int(s*0.26)))
    d = ImageDraw.Draw(g)
    ft = font(int(s*0.52), True)
    tb = d.textbbox((0, 0), a["initial"], font=ft)
    d.text(((s-(tb[2]-tb[0]))/2 - tb[0], (s-(tb[3]-tb[1]))/2 - tb[1]), a["initial"], font=ft, fill=(8, 18, 43))
    return g

def wrap(draw, text, ft, maxw):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=ft) <= maxw:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines

def mark(size):
    """AIRXVC 箭头标志（深色圆角底）。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size, size], int(size*0.23), fill=(10, 15, 36))
    cx = size/2
    # circle
    d.ellipse([size*0.19, size*0.19, size*0.81, size*0.81], outline=(126, 123, 255), width=max(2, int(size*0.035)))
    # arrow (paper plane) via gradient mask
    poly = [(cx, size*0.16), (size*0.66, size*0.80), (cx, size*0.67), (size*0.34, size*0.80)]
    g = grad_h(size, size, (53, 224, 212), (255, 106, 213)).convert("RGBA")
    pm = Image.new("L", (size, size), 0); ImageDraw.Draw(pm).polygon(poly, fill=255)
    img.paste(g, (0, 0), pm)
    d.ellipse([cx-size*0.055, size*0.5-size*0.055, cx+size*0.055, size*0.5+size*0.055], fill=(255, 255, 255))
    return img

def topbar(img, W):
    d = ImageDraw.Draw(img)
    m = mark(60); img.paste(m, (80, 60), m)
    d.text((156, 66), "AIRXVC", font=font(30, True), fill=INK)
    d.text((156, 104), "领航 · 机场推荐榜", font=font(20), fill=MUT)

# ---------------- site OG ----------------
def site_og():
    W, H = 1200, 630
    img = aurora(W, H); d = ImageDraw.Draw(img)
    topbar(img, W)
    d.text((80, 210), "机场推荐榜", font=font(96, True), fill=INK)
    d.text((80, 322), "2026 高速稳定 · 评测 · 优惠", font=font(52, True), fill=CYAN)
    d.text((80, 420), "按需求 3 分钟选对机场 — Mitce · 西部数据 · 糖果云", font=font(30), fill=MUT)
    d.line([(80, 512), (1120, 512)], fill=(255, 255, 255, 40), width=1)
    d.text((80, 536), "air-xvc.github.io", font=font(26), fill=MUT)
    tb = d.textbbox((0, 0), "独立机场评测", font=font(26))
    d.text((1120-(tb[2]-tb[0]), 536), "独立机场评测", font=font(26), fill=MUT)
    img.save(os.path.join(BASE, "assets", "og.png"))
    print("  ✓ assets/og.png")

# ---------------- app icons ----------------
def icons():
    for size, name in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")]:
        mark(size).convert("RGB").save(os.path.join(BASE, "assets", name))
        print("  ✓ assets/%s" % name)

# ---------------- per-airport OG ----------------
def airport_og(a):
    W, H = 1200, 630
    img = aurora(W, H); d = ImageDraw.Draw(img)
    topbar(img, W)
    em = emblem_img(a, 200); img.paste(em, (80, 200), em)
    x = 320
    d.text((x, 196), a["name"], font=font(76, True), fill=INK)
    nw = d.textlength(a["name"], font=font(76, True))
    d.text((x+nw+20, 236), a["en"], font=font(34), fill=MUT)
    # tagline
    ft = font(30); lines = wrap(d, a["tagline"], ft, W-x-80)[:2]
    for i, ln in enumerate(lines):
        d.text((x, 300+i*42), ln, font=ft, fill=(200, 208, 235))
    # chips
    chip = " · ".join([a["type_short"]+"线路", a["protocols"][0], "解锁 "+a["unlock"][0]])
    d.text((x, 300+len(lines)*42+16), chip, font=font(26, True), fill=CYAN)
    # bottom band
    d.line([(80, 512), (1120, 512)], fill=(255, 255, 255, 40), width=1)
    d.text((80, 536), "AIRXVC 领航 · 机场评测", font=font(26), fill=MUT)
    price = "%s 起 %s" % (a["price_from"], a["price_unit"])
    pw = d.textlength(price, font=font(28, True))
    d.text((1120-pw, 534), price, font=font(28, True), fill=hx(a["accent"][0]))
    img.save(os.path.join(BASE, "assets", "og", "%s.png" % a["slug"]))
    print("  ✓ assets/og/%s.png" % a["slug"])

if __name__ == "__main__":
    print("Fonts:", REG_F, "idx", REG_I)
    site_og(); icons()
    for a in AIR:
        airport_og(a)
    print("images done")
