#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, datetime as dt, hashlib, json, os, re, shutil, statistics, subprocess, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get('MUSIC_OPS_ROOT', Path(__file__).resolve().parents[1]))
DEFAULT_CONFIG = ROOT / 'config' / 'daily_opportunity_radar_queries.json'
ENV_FILE = Path('/root/.hermes/.env')
UA = 'HermesAgent/DailyOpportunityRadar'
STOP = set('the and for with from into para por com sem uma que você voce deus dios your music música musica mix hour hora horas 2026 2025'.split())


def load_env(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def api_search(q: str, limit: int, timeout: int = 70) -> dict[str, Any]:
    key = os.environ.get('TRANSCRIPT_API_KEY')
    if not key:
        raise RuntimeError('TRANSCRIPT_API_KEY missing')
    params = urllib.parse.urlencode({'q': q, 'type': 'video', 'limit': limit})
    req = urllib.request.Request(
        'https://transcriptapi.com/api/v2/youtube/search?' + params,
        headers={'Authorization': 'Bearer ' + key, 'User-Agent': UA},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def flat_search(q: str, limit: int, timeout: int = 120) -> dict[str, Any]:
    """Fallback discovery-only search via yt-dlp CLI.

    This usually lacks views/dates/duration, but preserves titles, channels and URLs
    so the daily radar still surfaces packaging/keyword opportunities when
    TranscriptAPI is unavailable or out of credits.
    """
    exe = shutil.which('yt-dlp') or '/root/hermes-env/bin/yt-dlp'
    if not Path(exe).exists():
        raise RuntimeError('yt-dlp not found for flat-search fallback')
    cmd = [exe, '--dump-single-json', '--flat-playlist', f'ytsearch{limit}:{q}']
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or '').strip()[:500])
    data = json.loads(proc.stdout)
    results = []
    for e in data.get('entries') or []:
        if not isinstance(e, dict):
            continue
        vid = e.get('id') or e.get('url')
        results.append({
            'videoId': vid,
            'url': e.get('webpage_url') or (f'https://www.youtube.com/watch?v={vid}' if vid else ''),
            'title': e.get('title') or '',
            'channelTitle': e.get('uploader') or e.get('channel') or '',
            'channelHandle': e.get('channel_id') or '',
            'duration': e.get('duration'),
            'viewCount': e.get('view_count'),
            'published': e.get('upload_date') or e.get('release_timestamp'),
            'source': 'yt-dlp-flat-search',
        })
    return {'results': results, 'source': 'yt-dlp-flat-search', 'discovery_only': True}


def search_with_fallback(q: str, limit: int, timeout: int = 70) -> tuple[dict[str, Any], str]:
    try:
        return api_search(q, limit, timeout), 'transcriptapi'
    except Exception as e:
        if '402' not in str(e) and 'Payment Required' not in str(e):
            raise
        data = flat_search(q, limit)
        data['fallback_reason'] = str(e)
        return data, 'yt-dlp-flat-search'


def parse_views(value: Any) -> int | None:
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
    return int(float(m.group(1).replace(',', '.')) * mult) if m else None


def parse_duration(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if not value:
        return None
    parts = [int(p) for p in re.findall(r'\d+', str(value))]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 1:
        return parts[0]
    return None


def parse_age_days(value: Any) -> float | None:
    if not value:
        return None
    s = str(value).lower()
    m = re.search(r'(\d+)', s)
    n = int(m.group(1)) if m else 1
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


def normalize(item: dict[str, Any], niche: str, niche_type: str, priority: int, query: str) -> dict[str, Any]:
    vid = item.get('videoId') or item.get('id') or item.get('video_id')
    title = item.get('title') or item.get('videoTitle') or item.get('name') or ''
    views = item.get('viewCount') or parse_views(item.get('viewCountText') or item.get('viewsText'))
    if not isinstance(views, int):
        views = parse_views(views)
    dur = item.get('duration') or item.get('durationSeconds') or parse_duration(item.get('lengthText') or item.get('durationText'))
    if not isinstance(dur, int):
        dur = parse_duration(dur)
    pub = item.get('published') or item.get('publishedTimeText') or item.get('publishDate')
    age = parse_age_days(pub)
    vpd = round(views / age, 2) if views is not None and age else None
    long_bonus = 0
    if dur and dur >= 3600: long_bonus += 20
    if dur and dur >= 5400: long_bonus += 10
    if dur and dur >= 7200: long_bonus += 5
    score = (min((vpd or 0) / 500, 60) + long_bonus + (10 if views and views >= 100000 else 0) + max(0, 10 - priority))
    return {
        'niche': niche,
        'niche_type': niche_type,
        'priority': priority,
        'query': query,
        'score': round(score, 2),
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
        'duration_minutes': round(dur / 60, 2) if dur else None,
        'is_long_1h_plus': bool(dur and dur >= 3600),
    }


def aggregate_channels(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Agrega os vídeos por canal, dentro de cada nicho.

    A busca devolve vídeos; o que interessa estrategicamente é o canal por trás
    deles. Um canal que aparece em 5 das 6 queries do nicho é estrutural; um que
    aparece uma vez pode ser acaso do ranking daquele dia.
    """
    por_nicho: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for r in rows:
        nome = (r.get('channel') or '').strip()
        if not nome:
            continue
        c = por_nicho[r['niche']].setdefault(nome, {
            'channel': nome, 'handle': r.get('channel_handle') or '',
            'videos': 0, 'queries': set(), 'views': [], 'long_form': 0,
        })
        c['videos'] += 1
        c['queries'].add(r.get('query'))
        if isinstance(r.get('views'), int):
            c['views'].append(r['views'])
        if r.get('is_long_1h_plus'):
            c['long_form'] += 1

    saida: dict[str, list[dict[str, Any]]] = {}
    for niche, canais in por_nicho.items():
        lista = []
        for c in canais.values():
            views = sorted(c['views'])
            lista.append({
                'channel': c['channel'], 'handle': c['handle'],
                'videos_no_radar': c['videos'], 'queries_distintas': len(c['queries']),
                'views_mediana': int(statistics.median(views)) if views else None,
                'views_max': max(views) if views else None,
                'long_form': c['long_form'],
            })
        lista.sort(key=lambda c: (-c['queries_distintas'], -c['videos_no_radar']))
        saida[niche] = lista
    return saida


def mark_breakouts(rows: list[dict[str, Any]], canais_por_nicho: dict[str, list[dict[str, Any]]]) -> None:
    """Marca o que está COMEÇANDO a viralizar, não o que já é grande.

    Esta fonte não expõe inscritos, então o multiplicador usa como base a
    MEDIANA do próprio canal na amostra: um vídeo muito acima do que aquele
    canal costuma fazer é o sinal de formato novo pegando. Só vale com 3+
    vídeos do canal na amostra — com menos, a mediana é ruído e o campo fica
    nulo em vez de inventar número.
    """
    medianas = {
        (niche, c['channel']): c['views_mediana']
        for niche, lista in canais_por_nicho.items() for c in lista
        if c['videos_no_radar'] >= 3 and c['views_mediana']
    }
    for r in rows:
        base = medianas.get((r['niche'], (r.get('channel') or '').strip()))
        views, idade = r.get('views'), r.get('age_days_est')
        mult = round(views / base, 2) if base and isinstance(views, int) and base > 0 else None
        r['canal_mediana_views'] = base
        r['multiplicador_vs_canal'] = mult
        # "começando" = novo o bastante para o formato ainda estar aberto
        r['is_breakout'] = bool(
            idade is not None and idade <= 30
            and ((mult is not None and mult >= 2.0)
                 or (r.get('views_per_day_est') or 0) >= 5000)
        )


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for r in rows:
        key = r.get('video_id') or r.get('url') or hashlib.sha1((r.get('title','') + r.get('channel','')).encode()).hexdigest()
        nkey = (r['niche'], key)
        if nkey in seen:
            continue
        seen.add(nkey); out.append(r)
    return out


def fmt_int(x):
    return f'{x:,}'.replace(',', '.') if isinstance(x, int) else 'N/A'


def write_report(config: dict[str, Any], rows: list[dict[str, Any]], raw: dict[str, Any], errors: list[dict[str, Any]], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / 'raw_by_query.json'
    csv_path = out_dir / 'daily_opportunity_rows.csv'
    errors_path = out_dir / 'errors_and_retries.json'
    report_path = out_dir / 'daily_opportunity_summary.md'
    raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding='utf-8')
    errors_path.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['niche','niche_type','priority','query','score','video_id','url','title','channel','channel_handle','views','views_text','published','age_days_est','views_per_day_est','duration_seconds','duration_minutes','is_long_1h_plus','canal_mediana_views','multiplicador_vs_canal','is_breakout']
    rows_sorted = sorted(rows, key=lambda r: r.get('score') or 0, reverse=True)
    canais = aggregate_channels(rows_sorted)
    mark_breakouts(rows_sorted, canais)
    channels_path = out_dir / 'channels_by_niche.json'
    channels_path.write_text(json.dumps(canais, ensure_ascii=False, indent=2), encoding='utf-8')
    # formato que o music-factory ingere direto (cli.py breakout-ingest)
    breakout_path = out_dir / 'breakouts.json'
    breakout_path.write_text(json.dumps({'videos': [
        {'videoTitle': r.get('title'), 'viewCount': r.get('views'),
         'channelTitle': r.get('channel'), 'ageDays': r.get('age_days_est'),
         'videoId': r.get('video_id'), 'url': r.get('url'),
         'duration': r.get('duration_seconds'), 'niche': r.get('niche'),
         'multiplicadorVsCanal': r.get('multiplicador_vs_canal')}
        for r in rows_sorted if r.get('is_breakout')
    ]}, ensure_ascii=False, indent=2), encoding='utf-8')
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows_sorted)
    by = defaultdict(list)
    for r in rows_sorted: by[r['niche']].append(r)
    source_counts = Counter((v.get('source') or 'transcriptapi') for v in raw.values() if isinstance(v, dict))
    source_label = ', '.join(f'{k}: {v}' for k, v in source_counts.items()) or 'N/A'
    lines = ['# Radar diário de oportunidades musicais', '', f'Data: {dt.datetime.now().isoformat(timespec="seconds")}', '', config.get('purpose',''), '', f'Fonte(s): {source_label}. TranscriptAPI traz métricas públicas/direcionais; yt-dlp flat-search é descoberta por título/canal/URL e pode não incluir views/duração/data. Nenhuma fonte inclui CTR, impressões, retenção, inscritos ganhos ou watch hours reais.', '', f'Vídeos únicos: {len(rows_sorted)}', f'Erros finais: {sum(1 for e in errors if not e.get("recovered"))}', '', '## Resumo por nicho', '', '| Nicho | Tipo | Prioridade | Vídeos | Mediana views | Máx views/dia est. | 1h+ | Leitura |', '| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for niche in config.get('priority_order', by.keys()):
        rs = by.get(niche, [])
        meta = config['niches'].get(niche, {})
        views = [r['views'] for r in rs if isinstance(r.get('views'), int)]
        vpd = [r['views_per_day_est'] for r in rs if isinstance(r.get('views_per_day_est'), (int, float))]
        long_count = sum(1 for r in rs if r.get('is_long_1h_plus'))
        lines.append(f"| {niche} | {meta.get('type','')} | {meta.get('priority','')} | {len(rs)} | {fmt_int(int(statistics.median(views))) if views else 'N/A'} | {max(vpd) if vpd else 'N/A'} | {long_count} | {meta.get('read','')} |")
    for niche in config.get('priority_order', by.keys()):
        rs = by.get(niche, [])
        meta = config['niches'].get(niche, {})
        words = Counter()
        for r in rs:
            for w in re.findall(r'[\wÀ-ÿ]+', (r.get('title') or '').lower()):
                if len(w) > 3 and w not in STOP: words[w] += 1
        lines += ['', f'## {niche}', '', f'Tipo: {meta.get("type")}. Prioridade: {meta.get("priority")}.', meta.get('read',''), '', f'Palavras recorrentes: {", ".join(w for w,_ in words.most_common(20))}', '', '| Score | Views/dia | Views | Duração | Título | Canal | URL |', '| ---: | ---: | ---: | ---: | --- | --- | --- |']
        for r in rs[:10]:
            lines.append(f"| {r.get('score')} | {r.get('views_per_day_est') or 'N/A'} | {fmt_int(r.get('views'))} | {r.get('duration_minutes') or 'N/A'} min | {(r.get('title') or '').replace('|','/')[:110]} | {(r.get('channel') or '').replace('|','/')[:45]} | {r.get('url')} |")

        brk = [r for r in rs if r.get('is_breakout')]
        lines += ['', f'### Começando a viralizar — {niche}', '']
        if not brk:
            lines.append('Nada na janela de 30 dias bateu o corte (2x a mediana do canal ou 5k views/dia).')
        else:
            lines += ['Vídeos novos (≤30d) muito acima do normal do próprio canal — é o formato a replicar.', '', '| xCanal | Views/dia | Views | Idade | Título | Canal |', '| ---: | ---: | ---: | ---: | --- | --- |']
            for r in brk[:8]:
                mult = f"{r['multiplicador_vs_canal']}x" if r.get('multiplicador_vs_canal') else 'N/A'
                lines.append(f"| {mult} | {r.get('views_per_day_est') or 'N/A'} | {fmt_int(r.get('views'))} | {r.get('age_days_est')}d | {(r.get('title') or '').replace('|','/')[:90]} | {(r.get('channel') or '').replace('|','/')[:35]} |")

        cl = canais.get(niche, [])
        lines += ['', f'### Canais do nicho — {niche}', '']
        if not cl:
            lines.append('Nenhum canal identificado nesta coleta.')
        else:
            lines += [f'{len(cl)} canal(is) distinto(s). Recorrer em várias queries indica canal estrutural, não acaso do ranking.', '', '| Queries | Vídeos | Mediana views | Máx views | 1h+ | Canal |', '| ---: | ---: | ---: | ---: | ---: | --- |']
            for c in cl[:12]:
                lines.append(f"| {c['queries_distintas']} | {c['videos_no_radar']} | {fmt_int(c['views_mediana'])} | {fmt_int(c['views_max'])} | {c['long_form']} | {c['channel'].replace('|','/')[:45]} |")
    lines += ['', '## Regras de decisão', '', '- Current niches primeiro; novas descobertas entram como testes, não distração.', '- Playlist/long-form continua sendo o produto principal.', '- Christian Sleep Ambient e Dark Academia passam a ser observados diariamente como novas oportunidades prioritárias.', '- Afro Deep House tem sinal forte, mas deve ficar separado de Noir Pulse para não confundir a identidade dark europeia/noir.', '- Latin Gospel Lofi fica em observação/teste, prioridade menor.', '', '## Arquivos', '', f'- CSV: {csv_path}', f'- Raw JSON: {raw_path}', f'- Canais por nicho: {channels_path}', f'- Breakouts (ingerível pelo music-factory): {breakout_path}', f'- Erros/retries: {errors_path}', f'- Relatório: {report_path}', '', '## Replicar o que está começando', '', 'Os breakouts saem em `breakouts.json` no formato que o music-factory ingere:', '', '```bash', 'python3 music-factory/cli.py breakout-ingest --niche <nicho> --file breakouts.json', '```', '', 'Lá eles são repontuados por inscritos do canal (que esta fonte não expõe),', 'e o relatório mostra a embalagem recorrente a copiar.', '']
    report_path.write_text('\n'.join(lines), encoding='utf-8')
    return {'report': str(report_path), 'csv': str(csv_path), 'raw': str(raw_path), 'channels': str(channels_path), 'breakouts': str(breakout_path), 'errors': str(errors_path)}


def main() -> int:
    ap = argparse.ArgumentParser(description='Daily music opportunity radar: current niches + new discoveries.')
    ap.add_argument('--config', default=str(DEFAULT_CONFIG))
    ap.add_argument('--limit', type=int, default=12)
    ap.add_argument('--date', default=dt.datetime.now().strftime('%Y-%m-%d'))
    ap.add_argument('--only-niche', action='append', default=[], help='Run only one or more niche keys; can be repeated.')
    ap.add_argument('--max-queries', type=int, default=0, help='Stop after N total queries; useful for smoke tests.')
    args = ap.parse_args()
    load_env()
    config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    rows, raw, errors = [], {}, []
    executed_queries = 0
    niche_order = config.get('priority_order', config['niches'].keys())
    if args.only_niche:
        selected = set(args.only_niche)
        niche_order = [n for n in niche_order if n in selected]
    for niche in niche_order:
        meta = config['niches'][niche]
        for query in meta['queries']:
            if args.max_queries and executed_queries >= args.max_queries:
                break
            key = f'{niche}::{query}'
            attempts = []
            executed_queries += 1
            for attempt in range(3):
                try:
                    data, source = search_with_fallback(query, args.limit, timeout=70 + attempt * 20)
                    raw[key] = data
                    for item in data.get('results') or data.get('videos') or []:
                        if isinstance(item, dict):
                            rows.append(normalize(item, niche, meta.get('type',''), int(meta.get('priority', 99)), query))
                    if attempts:
                        errors.append({'niche': niche, 'query': query, 'attempts': attempts, 'recovered': True})
                    break
                except Exception as e:
                    attempts.append(str(e)); time.sleep(1 + attempt)
            else:
                errors.append({'niche': niche, 'query': query, 'attempts': attempts, 'recovered': False})
            time.sleep(0.1)
    paths = write_report(config, dedupe(rows), raw, errors, ROOT / 'radar' / 'daily_opportunity' / args.date)
    print(json.dumps({'ok': True, 'rows': len(dedupe(rows)), 'final_errors': sum(1 for e in errors if not e.get('recovered')), **paths}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
