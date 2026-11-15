#!/usr/bin/env python3
"""Haalt de hoogte op van het begin- en eindpunt van elke piste en lift (swisstopo, swissALTI3D)
en bewaart die in data/heights.json. Daarmee rekent build_map.py het hoogteverschil uit."""
import json, os, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def lv95(lat, lon):
    p = (lat * 3600 - 169028.66) / 10000; l = (lon * 3600 - 26782.5) / 10000
    e = 2600072.37 + 211455.93 * l - 10938.51 * l * p - 0.36 * l * p * p - 44.54 * l ** 3
    n = 1200147.07 + 308807.95 * p + 3745.25 * l * l + 76.63 * p * p - 194.56 * l * l * p + 119.79 * p ** 3
    return e, n
els = json.load(open(os.path.join(ROOT, 'data', 'osm.json'), encoding='utf8'))['elements']
pts = set()
for e in els:
    t = e.get('tags', {})
    if e['type'] == 'way' and (t.get('piste:type') in ('downhill', 'sled', 'hike') or 'aerialway' in t):
        g = [p for p in e.get('geometry', []) if p]
        if len(g) > 1:
            for p in (g[0], g[-1], g[len(g) // 2]): pts.add((round(p['lat'], 5), round(p['lon'], 5)))
fp = os.path.join(ROOT, 'data', 'heights.json')
H = json.load(open(fp)) if os.path.exists(fp) else {}
todo = [p for p in sorted(pts) if f'{p[0]},{p[1]}' not in H]
print(len(pts), 'punten,', len(todo), 'nieuw'); bad = 0
for i, (la, lo) in enumerate(todo):
    e, n = lv95(la, lo)
    try:
        r = urllib.request.urlopen(urllib.request.Request(f'https://api3.geo.admin.ch/rest/services/height?easting={e:.1f}&northing={n:.1f}&sr=2056', headers={'User-Agent': 'firn-app (github.com/JaapSchip/firn)', 'Referer': 'https://jaapschip.github.io/firn/'}), timeout=30)
        H[f'{la},{lo}'] = round(float(json.load(r)['height']))
    except Exception as ex:
        bad += 1
        if bad < 4: print('mis', la, lo, ex)
        if bad > 40: break
    time.sleep(0.06)
json.dump(H, open(fp, 'w'), separators=(',', ':'))
print(len(H), 'hoogtes', bad, 'mislukt'); print('controle Kleine Scheidegg', lv95(46.585031, 7.960672))
if len(H) < len(pts) * 0.8: sys.exit('te weinig hoogtes')
