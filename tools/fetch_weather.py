#!/usr/bin/env python3
"""Maakt app/data/weather.json: verwachting per hoogte voor het Jungfrau-gebied.
Bron: MeteoSwiss Open Data, lokale verwachtingen (ch.meteoschweiz.ogd-local-forecasting)."""
import json, os, sys, urllib.request, datetime as dt
from zoneinfo import ZoneInfo
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = 'https://data.geo.admin.ch/'
COL = 'ch.meteoschweiz.ogd-local-forecasting'
TZ = ZoneInfo('Europe/Zurich')
# (point_id, point_type_id): sleutel, naam, hoogte
PTS = {('380133', '2'): ('jfj', 'Jungfraujoch', 3450), ('1028', '3'): ('sch', 'Schilthorn', 2969),
       ('382302', '2'): ('eig', 'Eigergletscher', 2311), ('382301', '2'): ('ks', 'Kleine Scheidegg', 2061),
       ('4271', '1'): ('fir', 'First · Oberläger', 1980), ('382500', '2'): ('mur', 'Mürren', 1650),
       ('382300', '2'): ('wen', 'Wengen', 1277), ('381800', '2'): ('gw', 'Grindelwald', 1038),
       ('233', '1'): ('lau', 'Lauterbrunnen', 815)}
PARAMS = ['tre200h0', 'rre150h0', 'fu3010h0', 'fu3010h1', 'sre000h0', 'nprolohs', 'npromths', 'zprfr0hs']
def req(u): return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'firn-app (github.com/JaapSchip/firn)'}), timeout=120)
items = json.load(req(f'{B}api/stac/v1/collections/{COL}/items?limit=20'))['features']
runs = {}
for it in items:
    for k, a in it['assets'].items():
        p = k.split('.')
        if len(p) == 5 and p[3] in PARAMS: runs.setdefault(p[2], {})[p[3]] = a['href']
full = sorted(r for r, d in runs.items() if all(x in d for x in PARAMS[:5]))
if not full: sys.exit('geen volledige verwachting gevonden')
run = full[-1]; print('run', run)
data = {}  # (key, ts) -> {param: value}
for prm, href in runs[run].items():
    n = 0
    for raw in req(href):
        f = raw.decode('latin1').strip().split(';')
        if len(f) < 4 or (f[0], f[1]) not in PTS or f[3] in ('', '-'): continue
        try: data.setdefault((PTS[(f[0], f[1])][0], f[2]), {})[prm] = float(f[3]); n += 1
        except ValueError: pass
    print(prm, n)
now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
def icon(t, p, cl, sun=None):
    if p is not None and p >= 0.2: return 'snow' if (t is not None and t <= 1.0) else 'rain'
    if cl is None: return 'sun' if (sun or 0) >= 40 else 'part' if (sun or 0) >= 15 else 'cloud'
    return 'sun' if cl < 25 else 'part' if cl < 70 else 'cloud'
out = {'run': run, 'made': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'src': 'MeteoSwiss', 'pts': []}
for key, name, alt in sorted(PTS.values(), key=lambda x: -x[2]):
    rows = []
    for (k, ts), v in data.items():
        if k != key: continue
        u = dt.datetime.strptime(ts, '%Y%m%d%H%M').replace(tzinfo=dt.timezone.utc)
        if u < now: continue
        cl = max(v['nprolohs'], v.get('npromths', 0)) if 'nprolohs' in v else None
        rows.append((u, v.get('tre200h0'), v.get('rre150h0'), v.get('fu3010h0'), v.get('fu3010h1'), v.get('sre000h0'), cl, v.get('zprfr0hs')))
    rows.sort()
    if not rows: continue
    hours = [[u.astimezone(TZ).strftime('%Y-%m-%dT%H'), t, p, None if w is None else round(w), None if g is None else round(g), icon(t, p, cl, s), None if z is None else round(z / 50) * 50] for u, t, p, w, g, s, cl, z in rows[:36]]
    days = {}
    for u, t, p, w, g, s, cl, z in rows:
        l = u.astimezone(TZ); d = days.setdefault(l.strftime('%Y-%m-%d'), {'t': [], 'p': 0.0, 's': 0.0, 'g': [], 'cl': [], 'dt': [], 'n': 0})
        if t is not None: d['t'].append(t)
        d['p'] += p or 0; d['s'] += s or 0; d['n'] += 1
        if g is not None: d['g'].append(g)
        if 8 <= l.hour <= 17:
            if cl is not None: d['cl'].append(cl)
            if t is not None: d['dt'].append(t)
    dl = []
    for k2 in sorted(days)[:7]:
        d = days[k2]
        if d['n'] < 8 or not d['t']: continue
        cl = sum(d['cl']) / len(d['cl']) if d['cl'] else None; mt = sum(d['dt']) / len(d['dt']) if d['dt'] else sum(d['t']) / len(d['t'])
        dl.append([k2, round(min(d['t'])), round(max(d['t'])), round(d['p'], 1), round(d['s'] / 60, 1), icon(mt, d['p'] / 5 if d['p'] >= 1 else 0, cl, 30), round(max(d['g'])) if d['g'] else None])
    out['pts'].append({'k': key, 'n': name, 'alt': alt, 'h': hours, 'd': dl})
if len(out['pts']) < 5: sys.exit('te weinig punten: %d' % len(out['pts']))
os.makedirs(os.path.join(ROOT, 'app', 'data'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'app', 'data', 'weather.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('WXJSON ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')))
