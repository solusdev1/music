#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import re
import statistics
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path('/root/youtube_music_ops')
OUT = ROOT / 'radar' / 'multi_niche' / dt.datetime.now().strftime('%Y-%m-%d')
ENV_FILE = Path('/root/.hermes/.env')
UA = 'HermesAgent/MultiNicheRadar/2026-08-06'

QUERY_GROUPS = {
    # Nichos atuais do usuário
    'current_ptbr_country_gospel_blues': [
        'Country Gospel Blues português 1 hora louvores para acalmar o coração',
        'Sertanejo Country Gospel 1 hora Deus conhece sua dor',
        'Country Blues Gospel português playlist completa oração madrugada',
        'Louvores Country Gospel para renovar fé 1H30',
    ],
    'current_spanish_gospel_blues': [
        'Gospel Blues en español 1 hora alabanzas para orar dormir',
        'Dios conoce tu dolor Gospel Blues en Español 1 hora',
        'Música cristiana blues español para descansar oración',
        'Blues Cristiano en español alabanzas cristianas 1H30',
    ],
    'current_dark_deep_house_noir_pulse': [
        'dark deep house mix no vocals 2 hour night drive',
        'after 2am dark deep house mix focus no vocals',
        'dark progressive house mix no vocals 1 hour 2026',
        'medieval castle rave dark deep house mix',
    ],
    'current_jazz_lounge': [
        'cozy night jazz 1 hour smooth jazz for work study coffee',
        'smooth jazz lounge 1 hour 30 relaxing instrumental',
        'rainy night jazz coffee shop ambience 2026',
        'jazz cafe music for work study relaxing 1 hour',
    ],

    # Novas descobertas / oportunidades adjacentes long-form
    'discovery_christian_sleep_ambient': [
        'christian sleep music 8 hours healing prayer instrumental',
        'soaking worship instrumental sleep music no words',
        'bible sleep music peaceful instrumental 3 hours',
    ],
    'discovery_dark_academia_piano': [
        'dark academia classical music 1 hour studying rain',
        'dark academia piano playlist for reading 1 hour',
        'gothic study music dark academia ambience',
    ],
    'discovery_afro_deep_house': [
        'afro deep house mix 2026 1 hour no vocals',
        'afro house sunset mix 1 hour deep house',
        'afro melodic house mix 2026 long mix',
    ],
    'discovery_latin_gospel_lofi': [
        'música cristiana lofi para estudiar orar 1 hora',
        'lofi cristiano en español para dormir estudiar',
        'christian lofi beats prayer study 1 hour',
    ],
    'discovery_cinematic_celtic_ambient': [
        'celtic ambient music 1 hour medieval fantasy relaxing',
        'medieval ambient music castle rain 1 hour',
        'dark celtic ambient music for studying 1 hour',
    ],
}

STOP = set('the and for with from into para por com sem uma que você voce deus dios your music música musica mix hour hora horas 2026'.split())


def load_env(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def api_search(q: str, limit: int = 12) -> dict[str, Any]:
    key = os.environ.get('TRANSCRIPT_API_KEY')
    if not key:
        raise RuntimeError('TRANSCRIPT_API_KEY missing')
    params = urllib.parse.urlencode({'q': q, 'type': 'video', 'limit': limit})
    url = f'https://transcriptapi.com/api/v2/youtube/search?{params}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {key}', 'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def parse_views_text(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if value is None:
        return None
    s = str(value).lower().strip().replace(',', '')
    mult = 1
    if 'b' in s or 'bil' in s:
        mult = 1_000_000_000
    elif 'mi' in s or 'million' in s or re.search(r'\bm\b', s):
        mult = 1_000_000
    elif 'mil' in s or 'k' in s:
        mult = 1_000
    m = re.search(r'(\d+(?:[\.,]\d+)?)', s)
    if not m:
        return None
    return int(float(m.group(1).replace(',', '.')) * mult)


def parse_duration_seconds(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if not value:
        return None
    parts = [int(p) for p in re.findall(r'\d+', str(value))]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    if len(parts) == 1:
        return parts[0]
    return None


def parse_age_days(value: Any) -> float | None:
    if not value:
        return None
    s = str(value).lower()
    n_match = re.search(r'(\d+)', s)
    n = int(n_match.group(1)) if n_match else 1
    if any(w in s for w in ['minute', 'minuto', 'hour', 'hora', 'today', 'hoje']):
        return 0.5
    if any(w in s for w in ['day', 'dia']):
        return max(n, 0.5)
    if any(w in s for w in ['week', 'semana']):
        return n * 7
    if any(w in s for w in ['month', 'mês', 'mes']):
        return n * 30
    if any(w in s for w in ['year', 'ano']):
        return n * 365
    return None


def normalize(item: dict[str, Any], niche: str, query: str) -> dict[str, Any]:
    title = item.get('title') or item.get('videoTitle') or item.get('name') or ''
    vid = item.get('videoId') or item.get('id') or item.get('video_id')
    views = item.get('viewCount') or parse_views_text(item.get('viewCountText') or item.get('viewsText'))
    if not isinstance(views, int):
        views = parse_views_text(views)
    dur = item.get('duration') or item.get('durationSeconds') or parse_duration_seconds(item.get('lengthText') or item.get('durationText'))
    if not isinstance(dur, int):
        dur = parse_duration_seconds(dur)
    pub = item.get('published') or item.get('publishedTimeText') or item.get('publishDate')
    age = parse_age_days(pub)
    vpd = round(views / age, 2) if views is not None and age else None
    score = 0.0
    if vpd is not None:
        score += min(vpd / 500, 60)
    if dur and dur >= 3600:
        score += 20
    if dur and dur >= 5400:
        score += 10
    if dur and dur >= 7200:
        score += 5
    if views and views >= 100000:
        score += 10
    return {
        'niche': niche,
        'query': query,
        'video_id': vid,
        'url': item.get('url') or item.get('videoUrl') or (f'https://www.youtube.com/watch?v={vid}' if vid else ''),
        'title': title,
        'channel': item.get('channelTitle') or item.get('author_name') or item.get('channel') or item.get('author') or '',
        'channel_handle': item.get('channelHandle') or '',
        'views': views,
        'views_text': item.get('viewCountText') or item.get('viewsText') or '',
        'published': pub,
        'age_days_est': age,
        'views_per_day_est': vpd,
        'duration_seconds': dur,
        'duration_minutes': round(dur/60, 2) if dur else None,
        'is_long_1h_plus': bool(dur and dur >= 3600),
        'score': round(score, 2),
    }


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for r in rows:
        key = r.get('video_id') or r.get('url') or hashlib.sha1((r.get('title','')+r.get('channel','')).encode()).hexdigest()
        niche_key = (r['niche'], key)
        if niche_key in seen:
            continue
        seen.add(niche_key)
        out.append(r)
    return out


def fmt_int(x):
    return f'{x:,}'.replace(',', '.') if isinstance(x, int) else 'N/A'


def main() -> int:
    load_env()
    OUT.mkdir(parents=True, exist_ok=True)
    raw_by_query = {}
    rows = []
    errors = []
    for niche, queries in QUERY_GROUPS.items():
        for q in queries:
            try:
                data = api_search(q, limit=12)
                raw_by_query[f'{niche}::{q}'] = data
                results = data.get('results') or data.get('videos') or []
                for item in results:
                    if isinstance(item, dict):
                        rows.append(normalize(item, niche, q))
                time.sleep(0.15)
            except Exception as e:
                errors.append({'niche': niche, 'query': q, 'error': str(e)})
    rows = dedupe(rows)
    rows_sorted = sorted(rows, key=lambda r: r.get('score') or 0, reverse=True)

    raw_path = OUT / 'raw_by_query.json'
    rows_path = OUT / 'multi_niche_rows.csv'
    summary_path = OUT / 'multi_niche_summary.md'
    errors_path = OUT / 'errors.json'
    raw_path.write_text(json.dumps(raw_by_query, ensure_ascii=False, indent=2), encoding='utf-8')
    errors_path.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')

    fields = ['niche','query','score','video_id','url','title','channel','channel_handle','views','views_text','published','age_days_est','views_per_day_est','duration_seconds','duration_minutes','is_long_1h_plus']
    with rows_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows_sorted)

    by = defaultdict(list)
    for r in rows_sorted:
        by[r['niche']].append(r)

    lines = [
        '# Radar multi-nicho YouTube Music — 2026-08-06', '',
        'Fonte: TranscriptAPI YouTube Search. Métricas são públicas/direcionais; não incluem CTR, impressões, retenção, AVD, inscritos ganhos ou watch hours reais.', '',
        f'Consultas: {sum(len(v) for v in QUERY_GROUPS.values())}',
        f'Vídeos únicos por nicho/query: {len(rows)}',
        f'Erros: {len(errors)}', '',
        '## Resumo por nicho', '',
        '| Nicho | Vídeos | Mediana views | Máx views/dia est. | 1h+ | Melhor leitura |',
        '| --- | ---: | ---: | ---: | ---: | --- |',
    ]

    niche_notes = {
        'current_ptbr_country_gospel_blues': 'Manter dor + consolo + uso devocional; playlist 1h+ continua central.',
        'current_spanish_gospel_blues': 'Boa continuidade para oração/descanso em espanhol; títulos humanos superam genéricos.',
        'current_dark_deep_house_noir_pulse': 'No vocals + dark/after 2AM/night/castle funciona como ângulo visual diferenciado.',
        'current_jazz_lounge': 'Nicho forte e saturado; precisa embalagem clara: cozy/night/coffee/work/study.',
        'discovery_christian_sleep_ambient': 'Oportunidade longíssima 3h–8h; baixa fricção visual, foco em sleep/prayer/healing.',
        'discovery_dark_academia_piano': 'Boa adjacência visual e longa duração; combina com study/reading/rain/castle.',
        'discovery_afro_deep_house': 'Oportunidade eletrônica adjacente; cuidado para não misturar com Noir Pulse se identidade for dark europeu.',
        'discovery_latin_gospel_lofi': 'Possível extensão para público cristão jovem/espanhol; testar antes de canal dedicado.',
        'discovery_cinematic_celtic_ambient': 'Ângulo medieval/castelo/ambient pode alimentar visual e nicho instrumental sem voz.',
    }

    for niche, rs in by.items():
        views = [r['views'] for r in rs if isinstance(r.get('views'), int)]
        vpd = [r['views_per_day_est'] for r in rs if isinstance(r.get('views_per_day_est'), (int,float))]
        long_count = sum(1 for r in rs if r.get('is_long_1h_plus'))
        lines.append(f"| {niche} | {len(rs)} | {fmt_int(int(statistics.median(views))) if views else 'N/A'} | {max(vpd) if vpd else 'N/A'} | {long_count} | {niche_notes.get(niche,'')} |")

    for niche, rs in by.items():
        words = Counter()
        channels = Counter()
        for r in rs:
            channels[r.get('channel') or 'N/A'] += 1
            for w in re.findall(r'[\wÀ-ÿ]+', (r.get('title') or '').lower()):
                if len(w) > 3 and w not in STOP:
                    words[w] += 1
        lines += ['', f'## {niche}', '', f'Coletados: {len(rs)} vídeos', f'Canais recorrentes: {", ".join([c for c,_ in channels.most_common(5)])}', f'Palavras recorrentes: {", ".join([w for w,_ in words.most_common(18)])}', '', '| Score | Views/dia | Views | Duração | Título | Canal | URL |', '| ---: | ---: | ---: | ---: | --- | --- | --- |']
        for r in rs[:10]:
            title = (r.get('title') or '').replace('|','/')[:110]
            lines.append(f"| {r.get('score')} | {r.get('views_per_day_est') or 'N/A'} | {fmt_int(r.get('views'))} | {r.get('duration_minutes') or 'N/A'} min | {title} | {(r.get('channel') or '').replace('|','/')[:45]} | {r.get('url')} |")

    lines += ['', '## Oportunidades recomendadas para próximos testes', '',
        '1. Country Blues e Fé: mais uma playlist irmã de 1h30–1h55 com variação de “Deus conhece sua dor”: “DEUS VIU SUAS LÁGRIMAS”, “QUANDO VOCÊ NÃO AGUENTA MAIS”, “DEUS NÃO ESQUECEU VOCÊ”.',
        '2. Spanish Gospel Blues: 1h40 com título humano “DIOS CONOCE TU DOLOR” ou “CUANDO YA NO PUEDES MÁS”; evitar mistura de português.',
        '3. Noir Pulse: usar o gancho visual “Medieval Castle Rave” como diferenciação, mantendo SEO de Dark Deep House / No Vocals / 1H30.',
        '4. Jazz: testar “Cozy Night Jazz / Coffee / Work / Study” antes de subnichar demais; thumbnail simples.',
        '5. Nova descoberta prioritária: Christian Sleep Ambient / Soaking Worship Instrumental 3h–8h — encaixa em long-form e pode virar canal/playlist de alto tempo de sessão.',
        '6. Nova descoberta visual adjacente: Dark Academia Piano / Gothic Study / Castle Rain — combina com estética medieval e público de estudo.',
        '', '## Arquivos', '',
        f'- CSV: {rows_path}', f'- Raw JSON: {raw_path}', f'- Erros: {errors_path}', f'- Relatório: {summary_path}',
    ]
    summary_path.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'rows': len(rows), 'errors': len(errors), 'summary': str(summary_path), 'csv': str(rows_path), 'raw': str(raw_path)}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
