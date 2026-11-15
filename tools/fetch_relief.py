#!/usr/bin/env python3
"""Haalt reliëftegels (swissALTI3D-schaduwreliëf, © swisstopo) op voor het skigebied
en zet ze in app/kaart/relief/{z}/{x}/{y}.png, zodat de kaart ook offline reliëf heeft."""
import math, os, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, W, N, E = 46.52, 7.80, 46.70, 8.13
LAYERS = ['ch.swisstopo.swissalti3d-reliefschattierung', 'ch.swisstopo.swissalti3d-reliefschattierung_monodirektional']
def tile(lat, lon, z):
    n = 2 ** z
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'firn-app (github.com/JaapSchip/firn)', 'Referer': 'https://jaapschip.github.io/firn/'})
    with urllib.request.urlopen(req, timeout=30) as r: return r.read()
layer = None
for l in LAYERS:
    x, y = tile(46.6, 7.95, 12)
    try:
        if len(get(f'https://wmts.geo.admin.ch/1.0.0/{l}/default/current/3857/12/{x}/{y}.png')) > 500: layer = l; break
    except Exception as e: print('niet beschikbaar:', l, e)
if not layer: sys.exit('geen relieflaag gevonden')
print('laag:', layer); ok = 0; size = 0
for z in range(11, 15):
    x0, y0 = tile(N, W, z); x1, y1 = tile(S, E, z)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            p = os.path.join(ROOT, 'app', 'kaart', 'relief', str(z), str(x), f'{y}.png')
            os.makedirs(os.path.dirname(p), exist_ok=True)
            try:
                b = get(f'https://wmts.geo.admin.ch/1.0.0/{layer}/default/current/3857/{z}/{x}/{y}.png')
                open(p, 'wb').write(b); ok += 1; size += len(b)
            except Exception as e: print('mis', z, x, y, e)
            time.sleep(0.05)
print(ok, 'tegels', size // 1024, 'KB')
if ok < 50: sys.exit('te weinig tegels')
