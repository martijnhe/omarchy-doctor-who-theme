"""Original Doctor Who style unlock-screen logos for the Omarchy theme.

Every logo is drawn here from basic shapes and a stock font, so nothing is
copied from BBC artwork. Output: <theme>/unlock-logos/<name>.png plus a
<theme>/unlock-logos/previews/<name>.png mock of the unlock screen.
"""
import sys, math, os, tomllib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

THEME = sys.argv[1]
OMARCHY_LOGO = sys.argv[2]  # the theme's gold Omarchy wordmark (unlock.png)
OUT = f'{THEME}/unlock-logos'
os.makedirs(f'{OUT}/previews', exist_ok=True)
c = tomllib.load(open(f'{THEME}/colors.toml', 'rb'))
def rgb(h, a=255): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

GOLD = rgb(c['accent']); BLUE = rgb('#1f5fb0'); DEEP = rgb('#123d7a'); LAMP = rgb('#fff1c9')
S = 4
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def canvas(w, h):
    img = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

def finish(img, name):
    img = img.resize((img.width // S, img.height // S), Image.LANCZOS)
    img.save(f'{OUT}/{name}.png', optimize=True)
    return img

def ring(d, cx, cy, r, w, fill=GOLD):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=int(w))

def dot(d, cx, cy, r, fill=GOLD):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

# 1. Seal: circular script, like the wallpaper but compact -----------------
def seal():
    W = H = 320
    img, d = canvas(W, H)
    cx, cy, R = W * S / 2, H * S / 2, 140 * S
    ring(d, cx, cy, R, 4 * S); ring(d, cx, cy, R - 12 * S, 2 * S)
    for k in range(60):
        a = k / 60 * 2 * math.pi
        r1, r2 = R - 12 * S, R - (22 if k % 5 == 0 else 17) * S
        d.line([cx + math.cos(a) * r1, cy + math.sin(a) * r1, cx + math.cos(a) * r2, cy + math.sin(a) * r2], fill=GOLD, width=2 * S)
    rnd = np.random.default_rng(12)
    for i in range(6):
        a = i / 6 * 2 * math.pi - math.pi / 2
        wr = 30 * S
        x, y = cx + math.cos(a) * 78 * S, cy + math.sin(a) * 78 * S
        ring(d, x, y, wr, 3 * S)
        kind = i % 3
        if kind == 0:
            dot(d, x, y, 8 * S)
        elif kind == 1:
            ring(d, x + 8 * S, y - 6 * S, 11 * S, 2 * S); dot(d, x - 12 * S, y + 12 * S, 4 * S)
        else:
            d.arc([x - 16 * S, y - 16 * S, x + 16 * S, y + 16 * S], 200, 520, fill=GOLD, width=3 * S)
        d.line([cx + math.cos(a) * 40 * S, cy + math.sin(a) * 40 * S, cx + math.cos(a) * 48 * S, cy + math.sin(a) * 48 * S], fill=GOLD, width=3 * S)
    ring(d, cx, cy, 40 * S, 3 * S)
    dot(d, cx, cy, 10 * S)
    return finish(img, 'seal')

# 2. Blue box: a police box icon with a lit lamp ---------------------------
def blue_box():
    W, H = 190, 340
    img, d = canvas(W, H)
    s = S
    ox, oy, bw, bh = 25 * s, 70 * s, 140 * s, 250 * s
    out = 3 * s
    def rect(x0, y0, x1, y1, fill):
        d.rectangle([x0, y0, x1, y1], fill=fill, outline=GOLD, width=out)
    rect(ox - 10 * s, oy + bh - 2 * s, ox + bw + 10 * s, oy + bh + 14 * s, DEEP)    # base
    rect(ox, oy, ox + bw, oy + bh, BLUE)                                           # body
    rect(ox - 6 * s, oy - 4 * s, ox + bw + 6 * s, oy + 26 * s, DEEP)             # sign band
    d.rectangle([ox + 14 * s, oy + 6 * s, ox + bw - 14 * s, oy + 20 * s], fill=(12, 16, 26, 255))
    rect(ox - 2 * s, oy - 18 * s, ox + bw + 2 * s, oy - 4 * s, BLUE)              # roof
    rect(ox + 10 * s, oy - 30 * s, ox + bw - 10 * s, oy - 18 * s, DEEP)
    lx = ox + bw // 2
    # lamp glow
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([lx - 34 * s, oy - 78 * s, lx + 34 * s, oy - 10 * s], fill=GOLD[:3] + (150,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14 * s)))
    d = ImageDraw.Draw(img)
    rect(lx - 9 * s, oy - 54 * s, lx + 9 * s, oy - 30 * s, LAMP)
    rect(lx - 13 * s, oy - 60 * s, lx + 13 * s, oy - 54 * s, DEEP)
    d.rectangle([lx - 4 * s, oy + 28 * s, lx + 4 * s, oy + bh - 4 * s], fill=DEEP)   # centre post
    pw = (bw - 4 * 10 * s) // 2 + 6 * s
    for side in (0, 1):
        px = ox + 10 * s + side * (bw // 2)
        for k in range(4):
            py = oy + 34 * s + k * 53 * s
            d.rectangle([px, py, px + pw - 8 * s, py + 45 * s], outline=GOLD, width=2 * s)
            if k == 0:
                gw = (pw - 8 * s - 8 * s) / 3
                for gx in range(3):
                    for gy in range(2):
                        x0 = px + 4 * s + gx * gw; y0 = py + 4 * s + gy * 19 * s
                        d.rectangle([x0 + s, y0 + s, x0 + gw - 2 * s, y0 + 17 * s], fill=LAMP)
    return finish(img, 'blue-box')

# 3. Vortex: a spiral emblem --------------------------------------------------
def vortex():
    W = H = 320
    img, d = canvas(W, H)
    cx, cy = W * S / 2, H * S / 2
    for arm in range(3):
        pts = []
        for i in range(400):
            t = i / 399
            r = (8 + t * 140) * S
            a = arm * 2 * math.pi / 3 + t * 3.4 * math.pi
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r, t))
        for (x0, y0, t0), (x1, y1, t1) in zip(pts, pts[1:]):
            w = int((1.5 + 9 * (1 - abs(t0 - 0.55) * 1.6)) * S)
            col = GOLD if arm == 0 else (rgb(c['orange']) if arm == 1 else rgb(c['blue']))
            d.line([x0, y0, x1, y1], fill=col, width=max(w, S))
    dot(d, cx, cy, 14 * S, LAMP)
    ring(d, cx, cy, 152 * S, 3 * S)
    return finish(img, 'vortex')

# 4. Wordmark: DOCTOR WHO in a spaced serif between rules ------------------
def wordmark():
    W, H = 760, 200
    img, d = canvas(W, H)
    f = ImageFont.truetype(SERIF, 70 * S)
    text = 'DOCTOR  WHO'
    # letter-spaced layout
    spacing = 6 * S
    widths = [d.textlength(ch, font=f) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = (W * S - total) / 2
    y = 56 * S
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=f, fill=GOLD); x += w + spacing
    d.line([60 * S, 30 * S, W * S - 60 * S, 30 * S], fill=GOLD, width=3 * S)
    d.line([60 * S, 170 * S, W * S - 60 * S, 170 * S], fill=GOLD, width=3 * S)
    for x0 in (60 * S, W * S - 60 * S):
        for y0 in (30 * S, 170 * S):
            dot(d, x0, y0, 7 * S)
    return finish(img, 'wordmark')

# 5. Sonic: a screwdriver icon ------------------------------------------------
def sonic():
    W, H = 700, 160
    img, d = canvas(W, H)
    cy = H * S / 2
    x = 40 * S
    def seg(x0, x1, h, fill, outline=GOLD):
        d.rounded_rectangle([x0, cy - h / 2, x1, cy + h / 2], radius=min(h / 3, 10 * S), fill=fill, outline=outline, width=3 * S)
    seg(40 * S, 120 * S, 46 * S, DEEP)                       # pommel
    seg(118 * S, 330 * S, 60 * S, (40, 44, 56, 255))         # grip
    for k in range(7):
        gx = 140 * S + k * 26 * S
        d.line([gx, cy - 24 * S, gx, cy + 24 * S], fill=GOLD, width=3 * S)
    seg(328 * S, 380 * S, 72 * S, DEEP)                      # collar
    seg(378 * S, 560 * S, 40 * S, (52, 58, 72, 255))         # shaft
    d.line([400 * S, cy, 540 * S, cy], fill=GOLD, width=3 * S)
    seg(558 * S, 600 * S, 62 * S, DEEP)                      # emitter housing
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([600 * S, cy - 50 * S, 690 * S, cy + 50 * S], fill=rgb(c['cyan'])[:3] + (190,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16 * S)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([598 * S, cy - 22 * S, 640 * S, cy + 22 * S], radius=12 * S, fill=rgb(c['bright_cyan']), outline=GOLD, width=3 * S)
    return finish(img, 'sonic')

def omarchy():
    im = Image.open(OMARCHY_LOGO).convert('RGBA')
    im.save(f'{OUT}/omarchy.png', optimize=True)
    return im

logos = {'seal': seal(), 'blue-box': blue_box(), 'vortex': vortex(), 'wordmark': wordmark(), 'sonic': sonic(), 'omarchy': omarchy()}

# Unlock-screen mockups, same layout as Omarchy's Plymouth script:
# logo centred, password entry 40px below it, all on the theme background.
bg = rgb(c['background']); fg = rgb(c['foreground'])
def mock(logo):
    W, H = 1920, 1080
    im = Image.new('RGBA', (W, H), bg)
    lx, ly = W // 2 - logo.width // 2, H // 2 - logo.height // 2
    im.alpha_composite(logo, (lx, ly))
    d = ImageDraw.Draw(im)
    ey = ly + logo.height + 40
    ex0 = W // 2 - 143
    d.rectangle([ex0, ey, ex0 + 286, ey + 48], outline=fg, width=2)
    for i in range(4):
        dot(d, ex0 + 24 + i * 18, ey + 24, 4, fg)
    # padlock
    px, py = ex0 - 60, ey + 6
    d.rounded_rectangle([px, py + 14, px + 34, py + 40], radius=4, fill=fg)
    d.arc([px + 5, py, px + 29, py + 28], 180, 360, fill=fg, width=5)
    return im.convert('RGB')

# A tile for the picker's "random" choice
rimg, rd = canvas(320, 320)
rd.text((160 * S, 150 * S), '?', font=ImageFont.truetype(SERIF, 220 * S), fill=GOLD, anchor='mm')
ring(rd, 160 * S, 160 * S, 150 * S, 4 * S)
rimg = rimg.resize((320, 320), Image.LANCZOS)
rmock = mock(rimg)
ImageDraw.Draw(rmock).text((960, 860), 'RANDOM', font=ImageFont.truetype(SANS, 40), fill=rgb(c['foreground'])[:3], anchor='mm')
rmock.save(f'{OUT}/previews/random.png', optimize=True)

for name, logo in logos.items():
    mock(logo).save(f'{OUT}/previews/{name}.png', optimize=True)
# The theme-level preview Omarchy's Style > Unlock picker shows
mock(logos['seal']).save(f'{THEME}/preview-unlock.png', optimize=True)
logos['seal'].save(f'{THEME}/unlock.png', optimize=True)
for n, l in logos.items():
    print(n, l.size)
