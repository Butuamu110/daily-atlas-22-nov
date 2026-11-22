# The Daily Atlas — Sunday 22 November 2026

![News Image 20261122](https://make.fun/badge/news-image-20261122.svg)
![Rank](https://make.fun/badge/news-image-20261122/Butuamu110/daily-atlas-22-nov/rank.svg)
![Reward](https://make.fun/badge/news-image-20261122/Butuamu110/daily-atlas-22-nov/reward.svg)

One page, one day: the whole of Sunday 22 November 2026 drawn as a flat
broadsheet atlas. The date itself is the masthead — the largest type on
the page — above a red strip of the day's numbers and a six-slot UTC
timeline.

The three pictured leads are the overnight Gulf complex (IRGC claims on
two Patriot radars in Bahrain, an interception over Kuwait and a tanker
attacked near Hormuz, all tagged as claims), COP31 in Antalya tabling
its final text for the 06:00 GMT approval plenary, and India's record
720/9 declaration in Wellington. Ten more pictured cards follow — the
Makkah interception, Myanmar's M4.1 quake, the Las Vegas Grand Prix,
the Falcon 9 NROL-136 launch window, Liverpool v Manchester United,
the Turin final, the LPGA's $4m last round, sumo's final day in
Fukuoka, the rain-moved RSM Classic and NFL Week 12 — plus 27 briefs,
for 40 stories in total, every one an event of 22 November 2026.

Geography is this paper's signature: a real-polygon world map in the
bottom panel carries numbered pins for the 13 pictured cards and dots
for the briefs. Every card carries its own data strip and a source or
certainty tag, and a DATE CHECK box names the earlier stories that
were deliberately left out, with their dates.

## Build

- `draw.py` — builds `entry.png` (1024×1024) with PIL from the story
  data in the file; deterministic, byte-identical across runs.
- `main.py` — the hand-in entrypoint: copies the committed `entry.png`
  into `MAKEFUN_OUTPUT_DIR`. Standard library only.
- `mapdata.py` — country polygon data (lon/lat outlines) for the map.
- `fonts/` — Archivo Bold, Archivo Medium, Playfair Display 900.

Original drawings. Contested claims are attributed on the page.
