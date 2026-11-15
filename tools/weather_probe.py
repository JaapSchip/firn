import json, urllib.request
B='https://data.geo.admin.ch/'
def get(u, n=None):
    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'firn-app (github.com/JaapSchip/firn)'}),timeout=60)
    return r.read(n) if n else r.read()
for f in ('ogd-local-forecasting_meta_point.csv','ogd-local-forecasting_meta_parameters.csv'):
    t=get(B+'ch.meteoschweiz.ogd-local-forecasting/'+f).decode('latin1').splitlines()
    print(f,len(t));print('\n'.join(t[:4]))
    if 'point' in f:
        for l in t:
            if any(k in l for k in ('Wengen','rren','Grindelwald','Scheidegg','nnlichen','Schilthorn','Jungfraujoch','Lauterbrunnen','Eigergletscher','First')): print(l)
j=json.loads(get(B+'api/stac/v1/collections/ch.meteoschweiz.ogd-local-forecasting/items?limit=5'))
print('links',[(l.get('rel'),l.get('href')) for l in j.get('links',[])])
for it in j['features']:
    a=it['assets'];ks=list(a)
    print(it['id'],it['properties'].get('datetime'),len(ks),ks[:3],ks[-3:])
it=j['features'][0];k=[x for x in it['assets'] if 'tre200h0' in x] or list(it['assets'])[:1]
print(k[0],it['assets'][k[0]]);print(get(it['assets'][k[0]]['href'],600).decode('latin1'))
k=[x for x in it['assets'] if 'jww003i0' in x]
if k: print(get(it['assets'][k[0]]['href'],400).decode('latin1'))
