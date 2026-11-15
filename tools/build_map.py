#!/usr/bin/env python3
"""Maakt van data/osm.json een compact kaartbestand app/kaart/map-data.js.
Kaartdata © OpenStreetMap-bijdragers, ODbL."""
import json, math, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
els = json.load(open(os.path.join(ROOT, 'data', 'osm.json'), encoding='utf8'))['elements']

HP = os.path.join(ROOT, 'data', 'heights.json')
HT = json.load(open(HP)) if os.path.exists(HP) else {}
def hts(c):
    a, b, m = HT.get(f'{c[0][0]},{c[0][1]}'), HT.get(f'{c[-1][0]},{c[-1][1]}'), HT.get(f'{c[len(c)//2][0]},{c[len(c)//2][1]}')
    return [a, b, m] if a is not None and b is not None else None
def line(e):
    return [[round(p['lat'], 5), round(p['lon'], 5)] for p in e.get('geometry', []) if p]
def length(c):
    t = 0
    for (a, b), (c2, d) in zip(c, c[1:]):
        x = math.radians(d - b) * math.cos(math.radians((a + c2) / 2)); y = math.radians(c2 - a)
        t += math.hypot(x, y) * 6371000
    return round(t)
def pt(e):
    if e['type'] == 'node': return [round(e['lat'], 5), round(e['lon'], 5)]
    g = [p for p in e.get('geometry', []) if p]
    if not g and 'bounds' in e:
        b = e['bounds']; return [round((b['minlat'] + b['maxlat']) / 2, 5), round((b['minlon'] + b['maxlon']) / 2, 5)]
    if not g: return None
    return [round(sum(p['lat'] for p in g) / len(g), 5), round(sum(p['lon'] for p in g) / len(g), 5)]
def rings(e):
    if e['type'] == 'way': return [line(e)]
    return [[[round(p['lat'], 5), round(p['lon'], 5)] for p in m.get('geometry', [])] for m in e.get('members', []) if m.get('role') == 'outer' and m.get('geometry')]

DIFF = {'novice': 'b', 'easy': 'b', 'intermediate': 'r', 'advanced': 'k', 'expert': 'k', 'freeride': 'f'}
SKIP_LIFT = {'zip_line', 'goods', 'station', 'pylon', 'yes'}
out = {k: [] for k in ('wc', 'hike', 'pistes', 'areas', 'sled', 'lifts', 'rail', 'stations', 'places', 'peaks', 'food', 'parking', 'shops', 'rivers', 'ice', 'water', 'roads')}
for e in els:
    t = e.get('tags', {}); n = t.get('name', '')
    pt_ = t.get('piste:type')
    if e['type'] == 'way' and pt_ == 'downhill':
        c = line(e)
        if len(c) < 2: continue
        d = DIFF.get(t.get('piste:difficulty'), 'r' if not t.get('piste:difficulty') else 'b')
        if t.get('area') == 'yes': out['areas'].append({'c': c, 'd': d})
        else: out['pistes'].append({'c': c, 'd': d, 'n': n, 'ref': t.get('piste:ref') or t.get('ref', ''), 'm': length(c), 'g': t.get('piste:grooming', ''), 'h': hts(c)})
    elif e['type'] == 'way' and pt_ and 'sled' in pt_:
        c = line(e)
        if len(c) > 1: out['sled'].append({'c': c, 'n': n, 'm': length(c), 'h': hts(c)})
    elif e['type'] == 'way' and pt_ == 'hike':
        c = line(e)
        if len(c) > 1: out['hike'].append({'c': c, 'n': n, 'm': length(c)})
    elif e['type'] == 'way' and 'aerialway' in t and t['aerialway'] not in SKIP_LIFT:
        c = line(e)
        if len(c) > 1: out['lifts'].append({'c': c, 'n': n, 't': t['aerialway'], 'm': length(c), 'cap': t.get('aerialway:occupancy', ''), 'h': hts(c)})
    elif e['type'] == 'way' and t.get('railway') in ('rail', 'narrow_gauge', 'funicular') and t.get('service') not in ('yard', 'siding', 'spur', 'crossover'):
        c = line(e)
        if len(c) > 1: out['rail'].append({'c': c, 'u': 1 if t.get('tunnel') == 'yes' else 0, 'f': 1 if t['railway'] == 'funicular' else 0})
    elif e['type'] == 'node' and t.get('railway') in ('station', 'halt') and n:
        out['stations'].append({'p': pt(e), 'n': n})
    elif e['type'] == 'node' and t.get('place') in ('town', 'village', 'hamlet') and n:
        out['places'].append({'p': pt(e), 'n': n, 'k': {'town': 0, 'village': 1, 'hamlet': 2}[t['place']]})
    elif e['type'] == 'node' and t.get('natural') == 'peak' and n and t.get('ele'):
        try: out['peaks'].append({'p': pt(e), 'n': n, 'e': int(float(t['ele'].replace(',', '.').split()[0]))})
        except ValueError: pass
    elif (t.get('amenity') in ('restaurant', 'cafe', 'bar') or t.get('tourism') == 'alpine_hut') and n and pt(e):
        out['food'].append({'p': pt(e), 'n': n, 't': t.get('amenity') or 'hut', 'w': t.get('website') or t.get('contact:website', ''), 'c': t.get('cuisine', ''), 'ph': (t.get('phone') or t.get('contact:phone', '')).split(';')[0].strip()})
    elif (t.get('shop') in ('sports', 'ski', 'outdoor') or t.get('amenity') == 'ski_rental') and n and pt(e):
        rent = t.get('amenity') == 'ski_rental' or t.get('shop') == 'ski' or 'yes' in (t.get('rental', ''), t.get('ski:rental', ''), t.get('service:ski:rental', '')) or 'ski' in t.get('rental', '')
        out['shops'].append({'p': pt(e), 'n': n, 'r': 1 if rent else 0, 'w': t.get('website') or t.get('contact:website', ''), 'ph': (t.get('phone') or t.get('contact:phone', '')).split(';')[0].strip()})
    elif t.get('amenity') == 'toilets' and pt(e) and t.get('access') not in ('private', 'customers', 'no'):
        out['wc'].append({'p': pt(e), 'n': n, 'fee': t.get('fee', '')})
    elif t.get('amenity') == 'parking' and pt(e) and t.get('access') not in ('private', 'customers', 'no', 'permit'):
        cap = int(t['capacity']) if t.get('capacity', '').isdigit() else 0
        if n or cap >= 40 or t.get('parking') in ('multi-storey', 'underground'):
            out['parking'].append({'p': pt(e), 'n': n, 'cap': cap, 'fee': t.get('fee', '')})
    elif e['type'] == 'way' and t.get('waterway') == 'river':
        out['rivers'].append(line(e)[::2] + line(e)[-1:])
    elif t.get('natural') == 'glacier' and e['type'] != 'node':
        out['ice'] += [r[::3] + r[-1:] for r in rings(e) if len(r) > 3]
    elif t.get('natural') == 'water' and e['type'] != 'node':
        out['water'] += [r for r in rings(e) if len(r) > 3]
    elif e['type'] == 'way' and t.get('highway') in ('primary', 'secondary', 'tertiary'):
        out['roads'].append(line(e)[::2] + line(e)[-1:])
keep = {'Eiger', 'Mönch', 'Jungfrau', 'Schilthorn', 'Männlichen', 'Lauberhorn', 'Tschuggen', 'Faulhorn', 'Schwarzhorn', 'Wetterhorn', 'Schreckhorn', 'Birg', 'Silberhorn', 'Breithorn', 'Gspaltenhorn'}
MAINPK = {'Eiger', 'Mönch', 'Jungfrau', 'Schilthorn', 'Männlichen', 'Lauberhorn', 'Faulhorn', 'Wetterhorn'}
cand = sorted([p for p in out['peaks'] if p['n'] in keep or p['e'] >= 3400], key=lambda p: (p['n'] not in MAINPK, -p['e']))
pk = []
for p in cand:
    if all(math.hypot((p['p'][0] - q['p'][0]) * 111, (p['p'][1] - q['p'][1]) * 76) > 1.6 for q in pk): pk.append(p)
for p in pk: p['k'] = 0 if p['n'] in MAINPK else 1
out['peaks'] = pk[:24]
MAINPL = {'Wengen', 'Mürren', 'Grindelwald', 'Lauterbrunnen', 'Stechelberg', 'Interlaken'}
for p in out['places']: p['k'] = 1 if p['n'] in MAINPL else 2
out['built'] = __import__('datetime').date.today().isoformat()
js = 'window.FIRN_MAP=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';'
open(os.path.join(ROOT, 'app', 'kaart', 'map-data.js'), 'w', encoding='utf8').write(js)
print({k: len(v) for k, v in out.items() if isinstance(v, list)}, len(js) // 1024, 'KB')
print('km piste', round(sum(p['m'] for p in out['pistes']) / 1000), 'liften', sorted({l['t'] for l in out['lifts']}))
