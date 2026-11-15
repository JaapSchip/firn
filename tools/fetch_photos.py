#!/usr/bin/env python3
"""Zoekt vrij te gebruiken foto's op Wikimedia Commons voor de activiteiten en zet kandidaten
in photos-cand/ met auteur en licentie, zodat we er per activiteit een kunnen kiezen."""
import json, os, re, sys, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'photos-cand'); os.makedirs(OUT, exist_ok=True)
Q = {'sled': 'Schlitteln Grindelwald winter', 'hike': 'Winterwanderweg Männlichen Kleine Scheidegg', 'jfj': 'Jungfraujoch Sphinx winter', 'piz': 'Piz Gloria Schilthorn',
     'birg': 'Birg Thrill Walk Schilthorn', 'cliff': 'First Cliff Walk Grindelwald', 'fly': 'First Flieger Grindelwald', 'velo': 'Velogemel Grindelwald',
     'ice': 'Wengen Eisbahn winter', 'park': 'Snowpark Grindelwald First'}
UA = {'User-Agent': 'firn-app/1.0 (https://github.com/JaapSchip/firn)'}
def api(**p):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(dict(p, format='json'))
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
OK = re.compile(r'^(CC BY(-SA)? [0-9.]+|CC0|Public domain)', re.I)
res = {}
for k, q in Q.items():
    j = api(action='query', generator='search', gsrsearch=q + ' filetype:bitmap', gsrnamespace=6, gsrlimit=12, prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=1400)
    c = []
    for pg in sorted((j.get('query', {}).get('pages', {}) or {}).values(), key=lambda x: x.get('index', 99)):
        ii = (pg.get('imageinfo') or [{}])[0]; m = ii.get('extmetadata', {})
        lic = m.get('LicenseShortName', {}).get('value', '')
        if not OK.match(lic) or ii.get('width', 0) < 1200 or not ii.get('thumburl'): continue
        art = re.sub(r'<[^>]+>', '', m.get('Artist', {}).get('value', '')).strip()[:80]
        c.append({'title': pg['title'], 'lic': lic, 'artist': art, 'url': ii['thumburl'], 'page': ii.get('descriptionurl', ''), 'w': ii['width'], 'h': ii['height']})
        if len(c) == 4: break
    for i, x in enumerate(c):
        try:
            b = urllib.request.urlopen(urllib.request.Request(x['url'], headers=UA), timeout=90).read()
            x['file'] = f'{k}-{i}.jpg'; open(os.path.join(OUT, x['file']), 'wb').write(b)
        except Exception as e: print('mis', k, i, e)
    res[k] = c; print(k, len(c), [x['title'][:40] for x in c])
json.dump(res, open(os.path.join(OUT, 'credits.json'), 'w'), ensure_ascii=False, indent=1)
