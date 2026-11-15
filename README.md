# Firn

Onafhankelijke ski-app voor het Jungfrau-gebied (Wengen, Mürren, Grindelwald).

- `app/kaart/` – de kaart: pistes, liften, eten, parkeren en je eigen positie. Open `index.html`.
- `data/osm-query.txt` – welke kaartdata we ophalen. `data/osm.json` is het ruwe antwoord.
- `tools/build_map.py` – maakt van de ruwe data het compacte kaartbestand `app/kaart/map-data.js`.
- `.github/workflows/osm.yml` – haalt de kaartdata op bij OpenStreetMap.

Kaartdata © OpenStreetMap-bijdragers, beschikbaar onder de Open Database License (ODbL).
