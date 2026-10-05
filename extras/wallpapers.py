import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 3840, 2160
OUT = sys.argv[1]
rng = np.random.default_rng(1963)

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float) / 255

BG = hexc('#0a1424'); DARK = hexc('#040912'); TARDIS = hexc('#123d7a'); BLUE = hexc('#3d8be0')
CYAN = hexc('#5ec8e5'); GOLD = hexc('#f0b44c'); ORANGE = hexc('#f08a3c'); PURPLE = hexc('#6a3fb8')
WHITE = hexc('#f5f8fc')

def save(arr, name):
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    img.save(f'{OUT}/{name}.webp', quality=92, method=6)
    return img

def ramp(t, stops):
    t = np.clip(t, 0, 1)[..., None]
    out = np.zeros(t.shape[:-1] + (3,))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t[..., 0] >= p0) & (t[..., 0] <= p1)
        k = ((t - p0) / (p1 - p0))[m]
        out[m] = c0 * (1 - k) + c1 * k
    return out

def vnoise(u, v, pu, pv, seed):
    """Value noise, periodic with period pu x pv grid cells."""
    g = np.random.default_rng(seed).random((pv, pu))
    iu, iv = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - iu, v - iv
    fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)
    a = g[iv % pv, iu % pu]; b = g[iv % pv, (iu + 1) % pu]
    c = g[(iv + 1) % pv, iu % pu]; d = g[(iv + 1) % pv, (iu + 1) % pu]
    return (a * (1 - fu) + b * fu) * (1 - fv) + (c * (1 - fu) + d * fu) * fv

def fbm(u, v, pu, pv, octaves=5, seed=0):
    total, amp, norm = 0, 1.0, 0
    for o in range(octaves):
        s = 2 ** o
        total = total + amp * vnoise(u * s, v * s, pu * s, pv * s, seed + o)
        norm += amp; amp *= 0.5
    return total / norm

def stars(arr, n, seed, maxsize=1.6, tint=WHITE):
    r = np.random.default_rng(seed)
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = r.random() * W, r.random() * H
        s = r.random() ** 4 * maxsize + 0.4
        d.ellipse([x - s, y - s, x + s, y + s], fill=int(120 + r.random() * 135))
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(2.5)), float) / 255
    a = np.asarray(img, float) / 255 + glow * 0.6
    return arr * (1 - a[..., None]) + tint * a[..., None]

yy, xx = np.mgrid[0:H, 0:W].astype(float)

# 1. Time vortex ----------------------------------------------------------
def vortex():
    cx, cy = W * 0.5, H * 0.5
    dx, dy = (xx - cx) / H, (yy - cy) / H
    r = np.sqrt(dx * dx + dy * dy) + 1e-4
    th = np.arctan2(dy, dx)
    depth = -np.log(r)                       # tunnel depth coordinate
    twist = th / (2 * np.pi) + depth * 0.22  # spiral twist
    P = 12
    u = (twist % 1.0) * P
    v = depth * 3.0 + 10
    n = fbm(u, v, P, 2048, octaves=6, seed=7)
    n2 = fbm(u * 1.0 + 3.3, v * 0.7, P, 2048, octaves=4, seed=42)
    bands = 0.5 + 0.5 * np.sin((twist * 2 * np.pi * 3) + n * 6)
    t = np.clip(0.55 * n + 0.35 * bands + 0.15 * n2, 0, 1)
    col = ramp(t, [(0, DARK), (0.35, TARDIS), (0.55, BLUE), (0.68, PURPLE), (0.8, ORANGE), (0.92, GOLD), (1, WHITE)])
    # vignette toward the rim, bright eye in the center
    rim = np.clip(r / 0.95, 0, 1)
    col = col * (1 - 0.75 * rim[..., None] ** 1.5)
    eye = np.exp(-(r / 0.06) ** 2)
    col = col + (GOLD * 0.6 + WHITE * 0.4) * eye[..., None]
    col = col * (0.6 + 0.4 * np.clip(t * 1.6, 0, 1))[..., None]
    return np.clip(col, 0, 1)

# 2. Console room roundels -------------------------------------------------
def roundels():
    base = ramp(yy / H, [(0, hexc('#0d1c33')), (1, hexc('#060d18'))])
    cell = 300.0
    # offset rows for a hex-ish layout
    row = np.floor(yy / cell)
    ox = (row % 2) * cell / 2
    lx = ((xx + ox) % cell) - cell / 2
    ly = (yy % cell) - cell / 2
    d = np.sqrt(lx * lx + ly * ly)
    R = cell * 0.36
    inside = np.clip((R - d) / 2.0, 0, 1)
    # recessed bowl shading, light from upper left
    nx, ny = lx / R, ly / R
    bowl = np.clip(0.55 + 0.45 * (nx * 0.6 + ny * 0.8), 0, 1)
    shade = base * (1 - inside[..., None]) + (base * 0.55 + TARDIS * 0.25 * bowl[..., None]) * inside[..., None]
    # rim highlight in gold where the light catches
    ring = np.exp(-((d - R) / 3.5) ** 2)
    catch = np.clip(-(nx * 0.6 + ny * 0.8), 0, 1)
    shade = shade + GOLD * (ring * (0.15 + 0.55 * catch))[..., None]
    # warm glow from the center of the room (console light)
    cxg, cyg = W * 0.5, H * 1.1
    g = np.exp(-(((xx - cxg) / (W * 0.45)) ** 2 + ((yy - cyg) / (H * 0.7)) ** 2))
    shade = shade + (ORANGE * 0.25 + GOLD * 0.15) * g[..., None]
    cool = np.exp(-(((xx - W * 0.15) / (W * 0.4)) ** 2 + ((yy + H * 0.1) / (H * 0.6)) ** 2))
    shade = shade + CYAN * 0.08 * cool[..., None]
    return np.clip(shade, 0, 1)

# 3. Circular script (Gallifreyan-inspired, procedurally invented) ----------
def script():
    base = ramp(np.sqrt(((xx - W * .5) / W) ** 2 + ((yy - H * .5) / H) ** 2) * 1.6,
                [(0, hexc('#0e2140')), (1, hexc('#040912'))])
    base = stars(base, 1400, 11, maxsize=1.3, tint=hexc('#c9d8ee'))
    S = 2
    img = Image.new('L', (W * S, H * S), 0)
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(5)
    CX, CY, RB = W * S * 0.5, H * S * 0.5, H * S * 0.40

    def circ(x, y, rad, w):
        d.ellipse([x - rad, y - rad, x + rad, y + rad], outline=255, width=int(w))

    circ(CX, CY, RB, 10); circ(CX, CY, RB * 1.06, 4)
    words = []
    n_words = 7
    for i in range(n_words):
        a = i / n_words * 2 * math.pi + 0.3
        wr = RB * (0.22 + r.random() * 0.08)
        dist = RB - wr * 0.55
        x, y = CX + math.cos(a) * dist, CY + math.sin(a) * dist
        circ(x, y, wr, 7)
        words.append((x, y, wr))
        for j in range(r.integers(2, 5)):
            b = r.random() * 2 * math.pi
            lr = wr * (0.18 + r.random() * 0.15)
            ld = wr * (0.45 + r.random() * 0.25)
            lx, ly = x + math.cos(b) * ld, y + math.sin(b) * ld
            kind = r.integers(0, 4)
            if kind == 0:
                circ(lx, ly, lr, 5)
            elif kind == 1:
                circ(lx, ly, lr, 5); circ(lx, ly, lr * 0.7, 3)
            elif kind == 2:
                d.arc([lx - lr, ly - lr, lx + lr, ly + lr], math.degrees(b) + 30, math.degrees(b) + 330, fill=255, width=5)
            else:
                d.ellipse([lx - lr * .5, ly - lr * .5, lx + lr * .5, ly + lr * .5], fill=255)
            for k in range(r.integers(0, 4)):
                c = b + (k - 1.5) * 0.35
                pr = 9
                px, py = lx + math.cos(c) * (lr + 22), ly + math.sin(c) * (lr + 22)
                d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=255)
    # connecting lines between words through the center ring
    for i in range(n_words):
        if r.random() < 0.6:
            x1, y1, w1 = words[i]; x2, y2, w2 = words[(i + 3) % n_words]
            d.line([x1, y1, x2, y2], fill=160, width=4)
    circ(CX, CY, RB * 0.28, 6)
    d.ellipse([CX - 18, CY - 18, CX + 18, CY + 18], fill=255)
    for k in range(48):
        a = k / 48 * 2 * math.pi
        x1, y1 = CX + math.cos(a) * RB * 1.06, CY + math.sin(a) * RB * 1.06
        x2, y2 = CX + math.cos(a) * RB * (1.09 if k % 4 else 1.13), CY + math.sin(a) * RB * (1.09 if k % 4 else 1.13)
        d.line([x1, y1, x2, y2], fill=200, width=5)
    img = img.resize((W, H), Image.LANCZOS)
    glow = img.filter(ImageFilter.GaussianBlur(14))
    a = np.asarray(img, float) / 255
    g = np.asarray(glow, float) / 255
    col = base + ORANGE * (g * 0.55)[..., None]
    col = col * (1 - a[..., None]) + GOLD * a[..., None]
    return np.clip(col, 0, 1)

# 4. Blue box adrift --------------------------------------------------------
def bluebox():
    nx, ny = xx / H, yy / H
    n = fbm(nx * 3, ny * 3, 256, 256, octaves=6, seed=99)
    n2 = fbm(nx * 2 + 5, ny * 2 + 9, 256, 256, octaves=5, seed=123)
    neb = np.clip((n - 0.45) * 2.2, 0, 1) ** 1.5
    neb2 = np.clip((n2 - 0.5) * 2.5, 0, 1) ** 2
    lane = np.exp(-((ny - 0.35 - 0.25 * (nx / (W / H))) / 0.28) ** 2)
    col = ramp(ny * 0.8 + 0.1, [(0, hexc('#081428')), (1, DARK)])
    col = col + TARDIS * (neb * lane * 1.2)[..., None] + PURPLE * (neb2 * lane * 0.5)[..., None]
    col = col + ORANGE * (neb2 * neb * lane * 0.35)[..., None]
    col = stars(col, 2600, 21, maxsize=1.8)

    # the box: tilted, small, lower right third
    S = 4
    bw, bh = 150 * S, 300 * S
    box = Image.new('RGBA', (bw + 80 * S, bh + 160 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    ox, oy = 40 * S, 110 * S
    tb = (18, 61, 122, 255); dk = (11, 40, 84, 255); lite = (250, 220, 150, 255)
    d.rectangle([ox - 10 * S, oy + bh - 8 * S, ox + bw + 10 * S, oy + bh + 6 * S], fill=dk)        # base
    d.rectangle([ox, oy, ox + bw, oy + bh], fill=tb)                                                # body
    d.rectangle([ox - 6 * S, oy - 4 * S, ox + bw + 6 * S, oy + 26 * S], fill=dk)                  # sign band
    d.rectangle([ox + 12 * S, oy + 4 * S, ox + bw - 12 * S, oy + 20 * S], fill=(20, 22, 30, 255))  # sign plate
    d.rectangle([ox - 2 * S, oy - 18 * S, ox + bw + 2 * S, oy - 4 * S], fill=tb)                   # roof steps
    d.rectangle([ox + 8 * S, oy - 30 * S, ox + bw - 8 * S, oy - 18 * S], fill=dk)
    d.rectangle([ox + 66 * S, oy - 52 * S, ox + 84 * S, oy - 30 * S], fill=lite)                  # lamp
    d.rectangle([ox + 63 * S, oy - 56 * S, ox + 87 * S, oy - 52 * S], fill=dk)
    d.rectangle([ox + 71 * S, oy + 30 * S, ox + 79 * S, oy + bh - 8 * S], fill=dk)                # center post
    for side in (0, 1):
        px = ox + 12 * S + side * 67 * S
        for k in range(4):
            py = oy + 36 * S + k * 64 * S
            d.rectangle([px, py, px + 59 * S, py + 54 * S], outline=dk, width=4 * S)
            if k == 0:
                for gx in range(3):
                    for gy in range(2):
                        cx0 = px + 6 * S + gx * 17 * S; cy0 = py + 6 * S + gy * 22 * S
                        d.rectangle([cx0, cy0, cx0 + 14 * S, cy0 + 19 * S], fill=lite)
    d.rectangle([ox, oy, ox + 8 * S, oy + bh], fill=dk); d.rectangle([ox + bw - 8 * S, oy, ox + bw, oy + bh], fill=dk)
    Z = 1.35
    pre = (int(box.width / S * Z), int(box.height / S * Z))
    box = box.resize(pre, Image.LANCZOS)
    ang = 17
    lx0, ly0 = (ox + 75 * S) / S * Z - pre[0] / 2, (oy - 41 * S) / S * Z - pre[1] / 2
    box = box.rotate(ang, expand=True, resample=Image.BICUBIC)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    lamp_x = ca * lx0 + sa * ly0 + box.width / 2
    lamp_y = -sa * lx0 + ca * ly0 + box.height / 2

    base = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    px, py = int(W * 0.68), int(H * 0.40)
    # halo behind the box and its lamp
    halo = Image.new('L', (W, H), 0); hd = ImageDraw.Draw(halo)
    cxh, cyh = px + box.width // 2, py + box.height // 2
    hd.ellipse([cxh - 320, cyh - 380, cxh + 320, cyh + 380], fill=140)
    halo = np.asarray(halo.filter(ImageFilter.GaussianBlur(120)), float) / 255
    arr = np.asarray(base, float)[..., :3] / 255 + BLUE * (halo * 0.55)[..., None]
    lamp = Image.new('L', (W, H), 0); ld = ImageDraw.Draw(lamp)
    lx, ly = px + lamp_x, py + lamp_y
    ld.ellipse([lx - 22, ly - 22, lx + 22, ly + 22], fill=255)
    lamp = np.asarray(lamp.filter(ImageFilter.GaussianBlur(26)), float) / 255
    arr = arr + (WHITE * 0.5 + GOLD * 0.5) * (lamp * 0.9)[..., None]
    base = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    base.alpha_composite(box, (px, py))
    return np.asarray(base.convert('RGB'), float) / 255

which = sys.argv[2:] or ['vortex', 'roundels', 'script', 'bluebox']
names = {'vortex': '1-time-vortex', 'roundels': '2-roundels', 'script': '3-circular-script', 'bluebox': '4-blue-box-adrift'}
for w in which:
    save(globals()[w](), names[w]); print('wrote', names[w])
