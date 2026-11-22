#!/usr/bin/env python3
"""Turn raw Overpass downloads (racks.json, ctx.json) into the compact files the page loads.
Usage: build_data.py <dir with racks.json and ctx.json>"""
import json, sys, datetime, pathlib
src = pathlib.Path(sys.argv[1]); out = pathlib.Path(__file__).resolve().parent.parent / 'data'
def pt(e):
    lat = e.get('lat', (e.get('center') or {}).get('lat')); lon = e.get('lon', (e.get('center') or {}).get('lon'))
    return (round(lat, 5), round(lon, 5)) if lat is not None else None
racks = []
for e in json.load(open(src / 'racks.json'))['elements']:
    p = pt(e); t = e.get('tags', {})
    if not p: continue
    r = {'a': p[0], 'o': p[1]}
    if t.get('bicycle_parking'): r['b'] = t['bicycle_parking'].lower()
    try:
        if int(t.get('capacity', '')) > 0: r['c'] = int(t['capacity'])
    except ValueError: pass
    if t.get('covered') == 'yes': r['v'] = 1
    if t.get('lit') == 'yes': r['l'] = 1
    if t.get('supervised') == 'yes': r['s'] = 2
    elif t.get('surveillance') in ('yes', 'cctv', 'camera', 'outdoor', 'public'): r['s'] = 1
    if t.get('access') and t['access'] not in ('yes', 'permissive', 'public'): r['x'] = t['access']
    if t.get('fee') == 'yes': r['f'] = 1
    k = t.get('check_date') or t.get('survey:date')
    if k: r['k'] = k[:10]
    racks.append(r)
today = datetime.date.today().isoformat()
json.dump({'date': today, 'racks': racks}, open(out / 'racks.json', 'w'), separators=(',', ':'))
print('racks', len(racks))
cp = src / 'ctx.json'
if cp.exists():
    cats = {'lamp': [], 'cam': [], 'active': [], 'station': [], 'market': []}
    for e in json.load(open(cp))['elements']:
        p = pt(e); t = e.get('tags', {})
        if not p: continue
        c = ('lamp' if t.get('highway') == 'street_lamp' else 'cam' if t.get('man_made') == 'surveillance' else
             'station' if t.get('railway') == 'station' else 'market' if t.get('amenity') in ('marketplace', 'cinema') else 'active')
        cats[c] += [p[0], p[1]]
    json.dump({'date': today, 'bbox': [-37.98, 144.78, -37.68, 145.20], **cats}, open(out / 'ctx.json', 'w'), separators=(',', ':'))
    print({k: len(v) // 2 for k, v in cats.items()})
