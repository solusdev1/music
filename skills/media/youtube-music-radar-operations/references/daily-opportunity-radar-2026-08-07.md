# Daily opportunity radar update — 2026-08-07

Session learning from converting the one-off multi-niche radar into a durable daily workflow.

## Durable artifacts

- Config: `/root/youtube_music_ops/config/daily_opportunity_radar_queries.json`
- Runner: `/root/youtube_music_ops/scripts/run_daily_opportunity_radar.py`
- Cron wrapper: `/root/.hermes/scripts/run_daily_opportunity_radar.sh`
- Output directory: `/root/youtube_music_ops/radar/daily_opportunity/YYYY-MM-DD/`

Expected daily outputs:

- `daily_opportunity_summary.md`
- `daily_opportunity_rows.csv`
- `raw_by_query.json`
- `errors_and_retries.json`

## Niche priority order encoded in config

1. `current_ptbr_country_gospel_blues`
2. `current_spanish_gospel_blues`
3. `current_dark_deep_house_noir_pulse`
4. `current_jazz_lounge`
5. `discovery_christian_sleep_ambient`
6. `discovery_dark_academia_piano`
7. `discovery_afro_deep_house`
8. `discovery_cinematic_celtic_ambient`
9. `discovery_latin_gospel_lofi`

Operating rules encoded in the config:

- Playlists/long-form remain the main product.
- Keep current channels/niches separate from new discovery buckets.
- Christian Sleep Ambient and Dark Academia are daily-priority new discoveries.
- Afro Deep House may be strong but should stay separate from Noir Pulse unless the user explicitly asks to mix/create a separate series.
- Latin Gospel Lofi is lower-priority observation/test material.

## TranscriptAPI payment/credit fallback

A real run hit `HTTP Error 402: Payment Required` from TranscriptAPI. The useful durable fix was not to stop: add automatic fallback to `yt-dlp --dump-single-json --flat-playlist ytsearchN:<query>`.

Fallback expectations:

- Usually enough for title, channel, URL, and often view/duration discovery.
- May lack reliable dates, views/day, likes, comments, and precise velocity.
- Mark outputs as discovery-only/public-directional when flat-search is used.
- Continue writing all normal artifacts so the daily workflow does not break.

Smoke-test pattern after editing the runner:

```bash
python3 -m py_compile /root/youtube_music_ops/scripts/run_daily_opportunity_radar.py
python3 /root/youtube_music_ops/scripts/run_daily_opportunity_radar.py --limit 2 --max-queries 2 --date smoke-test
```

Full run pattern:

```bash
python3 /root/youtube_music_ops/scripts/run_daily_opportunity_radar.py --limit 4
```

Cron wrapper test:

```bash
chmod +x /root/.hermes/scripts/run_daily_opportunity_radar.sh
/root/.hermes/scripts/run_daily_opportunity_radar.sh
```

## Scheduling note

In CLI sessions, cron `deliver=local` saves output locally and does not message the terminal. If the user wants active notifications, create/update the cron with a gateway-connected delivery target such as Telegram/Discord/all.
