#!/usr/bin/env python3
"""v19 ronda 2: nota de «las fuentes difieren» (campo disc) para Peter Denis Hassall (Jersey, n13021664958).
El nodo OSM dice memorial:addr «Winchester House, Winchester Street» y su coordenada está a 2,5 m de Winchester Street (w116347753);
BBC, Jersey Evening Post, Bailiwick Express y la Wikipedia alemana dan «Northfields, Byron Lane» (a ~243-334 m); la etiqueta image del propio nodo
se llama «Stolperstein Byron Lane (Jersey).jpg». No se mueve la coordenada (no hay dato abierto que diga dónde está la piedra); solo se avisa en la ficha.
Idempotente. Uso: v19_notes.py  → actualiza data/stones.json"""
import json
from pathlib import Path
R = Path(__file__).resolve().parents[2]
DISC = {'n13021664958': {
    'alt': 'Northfields, Byron Lane',
    'alt_src': ['https://www.bbc.co.uk/news/articles/cldyp4pkr9go',
                'https://jerseyeveningpost.com/news/2024/04/11/islanders-deported-during-the-war-to-be-memorialised/',
                'https://www.bailiwickexpress.com/news/channel-islands-claim-role-stones/',
                'https://de.wikipedia.org/wiki/Liste_der_Stolpersteine_auf_den_Kanalinseln'],
    'main_src': ['https://www.frankfallaarchive.org/people/peter-hassall/',
                 'https://www.liberationroute.com/en/pois/2272/stolperstein-in-honour-of-peter-hassall']}}
data = json.load(open(R / 'data/stones.json', encoding='utf-8'))
for s in data['stones']:
    if s['id'] in DISC: s['disc'] = DISC[s['id']]
(R / 'data/stones.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print('ok', [s['id'] for s in data['stones'] if s.get('disc')])
