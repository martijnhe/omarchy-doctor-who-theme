import sys, tomllib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

THEME = sys.argv[1]
SRC = sys.argv[2]  # omarchy theme with an unlock.png to borrow the logo shape from
c = tomllib.load(open(f'{THEME}/colors.toml', 'rb'))
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# unlock.png: the Omarchy wordmark in Gallifreyan gold
logo = Image.open(f'{SRC}/unlock.png').convert('RGBA')
alpha = logo.getchannel('A')
gold = Image.new('RGBA', logo.size, rgb(c['accent']) + (255,))
gold.putalpha(alpha)
gold.save(f'{THEME}/unlock.png', optimize=True)

# preview.png: a mock desktop on the vortex wallpaper
W, H = 1800, 1012
bg = Image.open(f'{THEME}/backgrounds/1-time-vortex.webp').convert('RGB').resize((W, H), Image.LANCZOS)
img = bg.convert('RGBA')
d = ImageDraw.Draw(img)
mono = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
monob = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
f = ImageFont.truetype(mono, 17); fb = ImageFont.truetype(monob, 17); fs = ImageFont.truetype(mono, 15)

# top bar
d.rectangle([0, 0, W, 30], fill=rgb(c['background']))
for i, n in enumerate('12345'):
    d.text((14 + i * 24, 6), n, font=fs, fill=rgb(c['accent'] if i == 0 else c['foreground']))
d.text((W / 2 - 70, 6), 'Monday 5 October', font=fs, fill=rgb(c['foreground']))

def window(x0, y0, x1, y1):
    # gradient border gold -> blue at 45deg
    grad = Image.new('RGBA', (x1 - x0 + 4, y1 - y0 + 4))
    a = np.array(rgb(c['accent']), float); b = np.array(rgb(c['blue']), float)
    gw, gh = grad.size
    yy, xx = np.mgrid[0:gh, 0:gw]
    t = ((xx / gw) + (1 - yy / gh)) / 2
    arr = (a * (1 - t[..., None]) + b * t[..., None]).astype(np.uint8)
    grad = Image.fromarray(np.dstack([arr, np.full((gh, gw), 255, np.uint8)]), 'RGBA')
    img.alpha_composite(grad, (x0 - 2, y0 - 2))
    d.rectangle([x0, y0, x1, y1], fill=rgb(c['background']))

G = 12
L, T, R, B = G, 30 + G, W - G, H - G
mid = W // 2 + 120
window(L, T, mid - G // 2, B)
window(mid + G // 2, T, R, T + (B - T) // 2 - G // 2)
window(mid + G // 2, T + (B - T) // 2 + G // 2, R, B)

# left: editor with some Python
fg, mu, ac = rgb(c['foreground']), rgb(c['muted']), rgb(c['accent'])
K, S_, F, N, Cy, Y = rgb(c['magenta']), rgb(c['green']), rgb(c['blue']), rgb(c['orange']), rgb(c['cyan']), rgb(c['yellow'])
code = [
    [(mu, '# tardis.py - bigger on the inside')],
    [(K, 'from'), (fg, ' vortex '), (K, 'import'), (fg, ' Coordinates, Era')],
    [],
    [(K, 'class '), (Y, 'Tardis'), (fg, ':')],
    [(fg, '    '), (Cy, 'chameleon_circuit'), (fg, ' = '), (N, 'False')],
    [(fg, '    '), (Cy, 'interior_m3'), (fg, ' = '), (N, 'float'), (fg, '('), (S_, '"inf"'), (fg, ')')],
    [],
    [(fg, '    '), (K, 'def '), (F, 'materialise'), (fg, '(self, where: Coordinates, when: Era):')],
    [(fg, '        '), (mu, '# vworp vworp')],
    [(fg, '        '), (K, 'if '), (fg, 'self.'), (F, 'handbrake_on'), (fg, '():')],
    [(fg, '            '), (K, 'raise '), (rgb(c['red']), 'TemporalError'), (fg, '('), (S_, '"brakes left on, again"'), (fg, ')')],
    [(fg, '        '), (K, 'for '), (fg, 'phase '), (K, 'in '), (F, 'range'), (fg, '('), (N, '3'), (fg, '):')],
    [(fg, '            self.'), (F, 'groan'), (fg, '(pitch='), (N, '0.42'), (fg, ' * phase)')],
    [(fg, '        '), (K, 'return '), (fg, 'self.'), (F, 'land'), (fg, '(where, when)')],
    [],
    [(K, 'if '), (fg, '__name__ == '), (S_, '"__main__"'), (fg, ':')],
    [(fg, '    '), (Y, 'Tardis'), (fg, '().'), (F, 'materialise'), (fg, '(Coordinates.'), (Cy, 'GALLIFREY'), (fg, ', Era.'), (Cy, 'ANY'), (fg, ')')],
]
lh = 26
d.rectangle([L, T, L + 46, B], fill=rgb(c['dark_background']))
for i, line in enumerate(code):
    y = T + 16 + i * lh
    if i == 7:
        d.rectangle([L + 47, y - 3, mid - G // 2, y + lh - 5], fill=rgb(c['lighter_background']))
    d.text((L + 10, y), f'{i + 1:>3}', font=fs, fill=rgb(c['dark_foreground'] if i != 7 else c['accent']))
    x = L + 62
    for col, txt in line:
        d.text((x, y), txt, font=f, fill=col); x += d.textlength(txt, font=f)
d.rectangle([L, B - 30, mid - G // 2, B], fill=rgb(c['lighter_background']))
d.rectangle([L, B - 30, L + 90, B], fill=rgb(c['blue']))
d.text((L + 14, B - 25), 'NORMAL', font=fb, fill=rgb(c['background']))
d.text((L + 104, B - 25), 'tardis.py', font=fs, fill=fg)

# right top: shell
x0, y0 = mid + G // 2 + 14, T + 14
sh = [
    [(ac, '~/tardis '), (F, 'main '), (fg, '❯ '), (fg, 'git log --oneline')],
    [(Y, 'a1b2c3d'), (fg, ' Reverse the polarity of the neutron flow')],
    [(Y, 'e4f5a6b'), (fg, ' Fix chameleon circuit (it still is not)')],
    [(Y, '0c1d2e3'), (fg, ' Add jelly baby dispenser to console')],
    [(ac, '~/tardis '), (F, 'main '), (fg, '❯ '), (fg, 'ls')],
    [(F, 'console/  '), (F, 'library/  '), (F, 'pool/  '), (S_, 'tardis.py  '), (fg, 'README.md')],
    [(ac, '~/tardis '), (F, 'main '), (fg, '❯ '), (fg, 'whoami')],
    [(K, 'doctor')],
    [(ac, '~/tardis '), (F, 'main '), (fg, '❯ '), (fg, '█')],
]
for i, line in enumerate(sh):
    x = x0
    for col, txt in line:
        d.text((x, y0 + i * lh), txt, font=f, fill=col); x += d.textlength(txt, font=f)

# right bottom: palette swatches
y0 = T + (B - T) // 2 + G // 2 + 18
d.text((x0, y0), 'Doctor Who', font=ImageFont.truetype(monob, 26), fill=ac)
d.text((x0, y0 + 36), 'TARDIS blue, Gallifreyan gold, time vortex', font=fs, fill=rgb(c['dark_foreground']))
names = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'accent']
sw = (R - x0 - 14) // len(names)
for row, prefix in enumerate(['', 'bright_']):
    for i, n in enumerate(names):
        key = (prefix + n) if (prefix + n) in c else n
        yy0 = y0 + 80 + row * 70
        d.rounded_rectangle([x0 + i * sw, yy0, x0 + (i + 1) * sw - 8, yy0 + 58], radius=6, fill=rgb(c[key]))
for i, n in enumerate(['background', 'lighter_background', 'selection', 'muted', 'dark_foreground', 'foreground', 'bright_foreground']):
    yy0 = y0 + 220
    w7 = (R - x0 - 14) // 7
    d.rounded_rectangle([x0 + i * w7, yy0, x0 + (i + 1) * w7 - 8, yy0 + 40], radius=6, fill=rgb(c[n]), outline=mu)

img.convert('RGB').save(f'{THEME}/preview.png', optimize=True)
print('ok')
