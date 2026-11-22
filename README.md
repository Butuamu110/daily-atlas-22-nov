[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Butuamu110/daily-atlas-22-nov/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Butuamu110/daily-atlas-22-nov/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# The Daily Atlas — Sunday 22 November 2026




One page, one day: the whole of Sunday 22 November 2026 drawn as a flat
broadsheet atlas. The date itself is the masthead — the largest type on
the page — above a red strip of the day's numbers, a six-slot UTC
timeline, and a segmented region tally whose counts sum exactly to the
37 stories on the page.

Round 3 lifts the leads: each of the three pictured lead scenes is now
132px tall and holds one oversized subject — a giant radar dish over
the Gulf with a huge interception burst, a globe filling the COP31
strip, and the Wellington stadium seen from above — under 28px serif
headlines. The three leads are the overnight Gulf complex (IRGC claims
on two Patriot radars in Bahrain, an interception over Kuwait and a
tanker attacked near Hormuz, all tagged as claims), COP31 in Antalya
tabling its final text for the 06:00 GMT approval plenary, and India's
record 720/9 declaration in Wellington. Ten more pictured cards follow
on coloured 48px bands — the Makkah interception, Myanmar's M4.1 quake,
the Las Vegas Grand Prix, the Falcon 9 NROL-136 launch window,
Liverpool v Manchester United, the Turin final, the LPGA's $4m last
round, sumo's final day in Fukuoka, the rain-moved RSM Classic and NFL
Week 12 — plus 24 briefs, for 37 stories in total, every one an event
of 22 November 2026.

Every card carries a certainty chip instead of a plain source tag —
CONFIRMED (2+ major outlets), OFFICIAL (on the record), REPORTED (1
major outlet) or CLAIM (one-sided claim) — with the legend printed at
the foot of DATE CHECK. DATE CHECK itself now runs in three parts:
LEFT OUT names eight discarded stories with their real dates, NOT YET
lists the day's still-unfinished business (the COP31 final adoption,
the Liverpool v Man Utd result, the ATP Turin final result), and
UNCONFIRMED carries the contested IRGC radar claim and the Houthi
interception claim.

Geography is this paper's signature: a real-polygon world map in the
bottom panel carries numbered pins for the 13 pictured cards and dots
for the briefs.

## Build

- `draw.py` — builds `entry.png` (1024×1024) with PIL from the story
  data in the file; deterministic, byte-identical across runs.
- `main.py` — the hand-in entrypoint: copies the committed `entry.png`
  into `MAKEFUN_OUTPUT_DIR` (falling back to `/output`). Standard
  library only.
- `mapdata.py` — country polygon data (lon/lat outlines) for the map.
- `fonts/` — Archivo Bold, Archivo Medium, Playfair Display 900.

Original drawings. Contested claims are attributed on the page.
