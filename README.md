# Firn

Onafhankelijke ski-app voor het Jungfrau-gebied (Wengen, Mürren, Grindelwald).

- `app/` – de app: Ontdek, Live, Kaart en Spelen, in vier talen. Online op https://jaapschip.github.io/firn/
- `app/kaart/` – de kaart: pistes, liften, eten, parkeren, reliëf en je eigen positie.
- `data/osm-query.txt` – welke kaartdata we ophalen. `data/osm.json` is het ruwe antwoord.
- `tools/build_map.py` – maakt van de ruwe data het compacte kaartbestand `app/kaart/map-data.js`.
- `.github/workflows/osm.yml` – haalt de kaartdata op bij OpenStreetMap.

Kaartdata © OpenStreetMap-bijdragers, beschikbaar onder de Open Database License (ODbL).

Reliëf © swisstopo. Foto's © Jaap Schippers.
