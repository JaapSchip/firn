#!/usr/bin/env python3
"""Zoekt vrij te gebruiken foto's op Wikimedia Commons voor de activiteiten en zet kandidaten
in photos-cand/ met auteur en licentie, zodat we er per activiteit een kunnen kiezen."""
import json, os, re, sys, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'photos-cand'); os.makedirs(OUT, exist_ok=True)
Q = {'sled': ['Schlitteln Grindelwald', 'sledging Grindelwald', 'Schlittelweg Jungfrau', 'Rodeln Wengen'], 'hike': ['Winterwandern Männlichen', 'Winterwanderweg Grindelwald', 'winter hiking Mürren', 'Männlichen winter'],
     'jfj': ['Jungfraujoch Sphinx', 'Jungfraujoch Top of Europe', 'Jungfraujoch'], 'piz': ['Piz Gloria Schilthorn'], 'birg': ['Thrill Walk Birg', 'Skyline Walk Birg', 'Birg Schilthornbahn'],
     'cliff': ['First Cliff Walk Grindelwald'], 'fly': ['First Flieger', 'First Glider Grindelwald', 'Grindelwald First zip line'], 'velo': ['Velogemel'],
     'ice': ['Eisbahn Wengen', 'Wengen curling', 'Wengen ice rink', 'Wengen winter village'], 'park': ['Snowpark Grindelwald', 'Grindelwald First snowboard', 'Snowpark Schilthorn']}
UA = {'User-Agent': 'firn-app/1.0 (https://github.com/JaapSchip/firn)'}
def api(**p):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(dict(p, format='json'))
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
OK = re.compile(r'^(CC BY(-SA)? [0-9.]+|CC0|Public domain)', re.I)
res = {}
for k, qs in Q.items():
  c = []; seen = set()
  for q in qs:
    if len(c) >= 4: break
    j = api(action='query', generator='search', gsrsearch=q + ' filetype:bitmap', gsrnamespace=6, gsrlimit=15, prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=1400)
    for pg in sorted((j.get('query', {}).get('pages', {}) or {}).values(), key=lambda x: x.get('index', 99)):
        if pg['title'] in seen: continue
        seen.add(pg['title'])
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
# start
