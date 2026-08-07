# youtube_music_ops

Standalone opportunity-discovery radar: scrapes YouTube search results for a
list of query "niches" (real and prospective) and writes dated CSV/JSON/MD
reports. **Not integrated with `music-factory`** — its niche vocabulary
(e.g. `current_dark_deep_house_noir_pulse`, `discovery_afro_deep_house`) is
exploratory and does not correspond 1:1 to any channel configured in
`music-factory/niches/*.json`. Treat its reports as candidate-niche research,
not as a feed that automatically reaches production.

## Setup

```bash
cp .env.example /root/.hermes/.env   # or export TRANSCRIPT_API_KEY yourself
# edit /root/.hermes/.env with a real TRANSCRIPT_API_KEY
```

Without a key, the scripts still run: `api_search()` fails over to a
yt-dlp-based flat search automatically (see `run_daily_opportunity_radar.py`),
degraded (no publish dates, fewer fields) but functional.

## Scripts

- `scripts/run_daily_opportunity_radar.py` — daily run, config-driven via
  `config/daily_opportunity_radar_queries.json`, writes to `radar/daily_opportunity/<date>/`.
- `scripts/run_multi_niche_discovery_2026_08_06.py` — broader one-off
  discovery sweep, writes to `radar/multi_niche/<date>/`.
- `scripts/run_daily_opportunity_radar.sh` — thin cron/systemd wrapper.

## Known limitation

Neither script feeds its findings back into `music-factory`'s
`radar-add`/`radar-approve` workflow (`core/opportunity.py`). A theme
discovered here has to be manually copied into a niche's `temas` list in
`music-factory/niches/*.json` if it's meant to become a real song theme —
and a prospective *new-channel* niche found here has no automatic path into
a new `music-factory/niches/*.json` config at all; that remains an
operator decision.
