#!/usr/bin/env python3
"""
Radar Gospel Blues Viral

Coleta vídeos públicos do YouTube via yt-dlp search, calcula score de oportunidade
para canais dark de música gospel/country/blues e gera relatório de tendências.

Uso:
  uv run --with yt-dlp python scripts/radar_gospel_blues_viral.py --max-results 5
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yt_dlp
except Exception as exc:
    print("ERRO: yt-dlp não encontrado. Rode com: uv run --with yt-dlp python scripts/radar_gospel_blues_viral.py", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
RAW = ROOT / "data_raw"
PROCESSED = ROOT / "data_processed"
REPORTS = ROOT / "reports"
GENERATED = ROOT / "generated_songs"
LOGS = ROOT / "logs"
INPUTS = ROOT / "inputs"

PT_STOP = {
    "de", "da", "do", "das", "dos", "e", "a", "o", "as", "os", "em", "com", "para", "por", "um", "uma",
    "the", "and", "or", "to", "of", "in", "for", "with", "on", "official", "video", "music"
}

THEME_PATTERNS = {
    "oração de madrugada": ["madrugada", "oração", "oracion", "prayer", "night prayer", "late night"],
    "estrada e recomeço": ["estrada", "camino", "road", "highway", "recomeço", "voltei", "back"],
    "cruz e redenção": ["cruz", "cross", "redeemed", "redemption", "salvação", "salvation"],
    "tempestade e promessa": ["tempestade", "storm", "rain", "chuva", "promessa", "promise"],
    "casa simples / varanda": ["home", "casa", "varanda", "porch", "farm", "fazenda", "rural"],
    "perdão e graça": ["perdão", "perdao", "forgiveness", "grace", "graça", "mercy", "misericórdia"],
    "sono / playlist longa": ["sleep", "dormir", "playlist", "1 hour", "3 hours", "relax", "calm"],
    "batalha espiritual": ["battle", "warfare", "luta", "guerra", "deliverance", "libertação"],
    "salmos / proteção espiritual": ["psalm", "salmo", "salmos", "91", "protection", "proteção", "cover you", "feathers"],
}

TITLE_FORMULAS = [
    "Deus me encontrou na [imagem forte]",
    "Voltei pra [cruz/casa/fé]",
    "Oração na [madrugada/estrada/tempestade]",
    "Quando [a noite/a chuva/o galo] [ação]",
    "Louvor country gospel para [orar/dormir/recomeçar]",
    "[Objeto rural] com [símbolo espiritual]",
    "No fim da [estrada/noite/tempestade]",
]

VISUAL_FORMULAS = [
    "homem rural com chapéu + violão + cruz distante + luz âmbar",
    "estrada de terra vazia + cerca velha + tempestade abrindo",
    "varanda/casa simples + Bíblia aberta + café + lamparina",
    "cruz de madeira contra céu escuro + raio de sol dourado",
    "chuva em telhado de zinco + janela com luz quente",
]

@dataclass
class VideoRecord:
    query: str
    title: str
    url: str
    channel: str
    channel_url: str
    upload_date: str
    duration: int
    view_count: int
    like_count: int
    comment_count: int
    thumbnail: str
    description: str
    tags: str
    age_days: float
    views_per_day: float
    likes_per_1000: float
    comments_per_1000: float
    detected_themes: str
    viral_score: float
    opportunity_class: str


def safe_int(x: Any) -> int:
    try:
        if x is None:
            return 0
        return int(x)
    except Exception:
        return 0


def parse_upload_date(s: str | None) -> tuple[str, float]:
    if not s:
        return "", 365.0
    try:
        dt = datetime.strptime(s, "%Y%m%d").replace(tzinfo=timezone.utc)
        age = max(1.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0)
        return dt.date().isoformat(), age
    except Exception:
        return str(s), 365.0


def normalize_score(value: float, cap: float) -> float:
    if cap <= 0:
        return 0.0
    return min(100.0, max(0.0, 100.0 * value / cap))


def detect_themes(title: str, desc: str) -> list[str]:
    text = f"{title} {desc}".lower()
    found = []
    for theme, words in THEME_PATTERNS.items():
        if any(w.lower() in text for w in words):
            found.append(theme)
    return found or ["tema espiritual genérico"]


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-záàãâéêíóôõúüçñ]+", text.lower()) if len(w) >= 4 and w not in PT_STOP]


def ydl_options(extract_flat: bool = False, playlistend: int | None = None, noplaylist: bool = True) -> dict[str, Any]:
    opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": extract_flat,
        "ignoreerrors": True,
        "noplaylist": noplaylist,
        "socket_timeout": 20,
        "retries": 2,
        "fragment_retries": 1,
    }
    if playlistend:
        opts["playlistend"] = playlistend
    return opts


def extract_search(query: str, max_results: int) -> list[dict[str, Any]]:
    search = f"ytsearch{max_results}:{query}"
    with yt_dlp.YoutubeDL(ydl_options()) as ydl:
        info = ydl.extract_info(search, download=False)
    entries = []
    if info and info.get("entries"):
        entries = [e for e in info["entries"] if e]
    return entries


def looks_like_channel_url(url: str) -> bool:
    u = url.lower()
    return any(x in u for x in ["youtube.com/@", "/channel/", "/c/", "/user/"]) and "/watch" not in u


def extract_url(url: str, channel_video_limit: int = 10) -> dict[str, Any] | None:
    if looks_like_channel_url(url):
        channel_url = url.rstrip("/")
        if not channel_url.endswith("/videos"):
            channel_url += "/videos"
        with yt_dlp.YoutubeDL(ydl_options(extract_flat=True, playlistend=channel_video_limit, noplaylist=False)) as ydl:
            info = ydl.extract_info(channel_url, download=False)
    else:
        with yt_dlp.YoutubeDL(ydl_options()) as ydl:
            info = ydl.extract_info(url, download=False)
    return info if info else None


def extract_urls_from_text(text: str) -> list[str]:
    pattern = r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s)\]\"']+"
    urls = []
    seen = set()
    for m in re.findall(pattern, text):
        clean = m.strip().rstrip('.,;')
        if clean not in seen:
            seen.add(clean)
            urls.append(clean)
    return urls


def read_manual_urls(*paths: Path) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    seen = set()
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() in {".txt", ".md", ".csv"}:
            candidates = extract_urls_from_text(text)
            if not candidates:
                candidates = [line.strip() for line in text.splitlines() if line.strip().startswith(("http://", "https://"))]
        else:
            candidates = extract_urls_from_text(text)
        for url in candidates:
            if url not in seen:
                seen.add(url)
                out.append((path.name, url))
    return out


def build_record(query: str, e: dict[str, Any]) -> VideoRecord:
    title = e.get("title") or ""
    url = e.get("webpage_url") or e.get("original_url") or e.get("url") or ""
    channel = e.get("channel") or e.get("uploader") or ""
    channel_url = e.get("channel_url") or e.get("uploader_url") or ""
    upload_date, age_days = parse_upload_date(e.get("upload_date"))
    view_count = safe_int(e.get("view_count"))
    like_count = safe_int(e.get("like_count"))
    comment_count = safe_int(e.get("comment_count"))
    duration = safe_int(e.get("duration"))
    desc = (e.get("description") or "")[:1000]
    tags = ", ".join(e.get("tags") or [])[:800]
    thumbs = e.get("thumbnails") or []
    thumbnail = ""
    if thumbs:
        thumbnail = thumbs[-1].get("url") or ""
    elif e.get("thumbnail"):
        thumbnail = e.get("thumbnail") or ""

    views_per_day = view_count / max(1.0, age_days)
    likes_per_1000 = like_count / max(1, view_count) * 1000 if view_count else 0
    comments_per_1000 = comment_count / max(1, view_count) * 1000 if view_count else 0
    themes = detect_themes(title, desc)

    recency = max(0.0, 100.0 - min(age_days, 365.0) / 365.0 * 100.0)
    # Para nichos musicais dark/gospel, 10k views/dia já é sinal forte.
    views_day_score = normalize_score(views_per_day, 10000)
    raw_views_score = normalize_score(math.log10(view_count + 1), 7)  # 10M ~= 100
    likes_score = normalize_score(likes_per_1000, 80)
    comments_score = normalize_score(comments_per_1000, 20)

    viral_score = (
        0.35 * views_day_score
        + 0.20 * raw_views_score
        + 0.15 * likes_score
        + 0.15 * comments_score
        + 0.15 * recency
    )
    viral_score = round(min(100.0, max(0.0, viral_score)), 2)
    if viral_score >= 80:
        klass = "tendência forte"
    elif viral_score >= 60:
        klass = "tendência promissora"
    elif viral_score >= 40:
        klass = "observar"
    else:
        klass = "referência fraca"

    return VideoRecord(
        query=query,
        title=title,
        url=url,
        channel=channel,
        channel_url=channel_url,
        upload_date=upload_date,
        duration=duration,
        view_count=view_count,
        like_count=like_count,
        comment_count=comment_count,
        thumbnail=thumbnail,
        description=desc.replace("\n", " "),
        tags=tags,
        age_days=round(age_days, 1),
        views_per_day=round(views_per_day, 2),
        likes_per_1000=round(likes_per_1000, 2),
        comments_per_1000=round(comments_per_1000, 2),
        detected_themes=", ".join(themes),
        viral_score=viral_score,
        opportunity_class=klass,
    )


def dedupe(records: list[VideoRecord]) -> list[VideoRecord]:
    seen = set()
    out = []
    for r in sorted(records, key=lambda x: x.viral_score, reverse=True):
        key = r.url or (r.channel, r.title)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def write_outputs(records: list[VideoRecord], day: str) -> tuple[Path, Path]:
    raw_path = RAW / f"videos_raw_{day}.jsonl"
    csv_path = PROCESSED / f"videos_ranked_{day}.csv"
    with raw_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = list(asdict(records[0]).keys()) if records else ["title"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            w.writerow(asdict(r))
    return raw_path, csv_path


def trend_analysis(records: list[VideoRecord]) -> dict[str, Any]:
    theme_counter = Counter()
    word_counter = Counter()
    channel_counter = Counter()
    for r in records:
        for t in r.detected_themes.split(", "):
            theme_counter[t] += 1
        word_counter.update(words(r.title))
        if r.channel:
            channel_counter[r.channel] += 1
    return {
        "themes": theme_counter.most_common(10),
        "words": word_counter.most_common(20),
        "channels": channel_counter.most_common(15),
    }


def idea_bank(analysis: dict[str, Any]) -> list[dict[str, str]]:
    themes = [t for t, _ in analysis.get("themes", [])] or ["estrada e recomeço", "oração de madrugada", "cruz e redenção"]
    core = [
        ("Deus na Estrada de Barro", "estrada e recomeço", "A poeira subiu, mas a graça também."),
        ("Oração no Banco da Varanda", "oração de madrugada", "Quando a casa dorme, o céu ainda me ouve."),
        ("A Cruz Depois da Chuva", "tempestade e promessa", "Toda tempestade termina ajoelhada diante da promessa."),
        ("Café, Bíblia e Perdão", "casa simples / varanda", "O dia começa melhor quando a culpa perde a voz."),
        ("Voltei Quando o Sino Tocou", "cruz e redenção", "Eu fugi pela estrada, mas o amor tocou o sino pra eu voltar."),
        ("Misericórdia no Telhado de Zinco", "perdão e graça", "A chuva bate fora, mas Deus lava por dentro."),
        ("No Fim da Noite Eu Vi a Luz", "oração de madrugada", "A madrugada não venceu quem aprendeu a orar."),
    ]
    out = []
    for i, (title, theme, hook) in enumerate(core, 1):
        if i <= len(themes):
            theme = themes[i-1]
        out.append({"title": title, "theme": theme, "hook": hook})
    return out


def suno_package(idea: dict[str, str]) -> str:
    title = idea["title"]
    hook = idea["hook"]
    style = "Brazilian country blues gospel, sertanejo roots influence, dark but hopeful, 74 BPM, minor key verses resolving into warm hopeful chorus, acoustic guitar, resonator slide guitar, subtle viola caipira, brushed drums, upright bass, soft organ pad, weathered raspy male baritone vocal, distant gospel choir in final chorus, rural dusty road atmosphere, vintage analog warmth, cinematic but simple."
    exclude = "EDM, trap, rap, funk, glossy pop worship, children vocals, heavy autotune, metal, upbeat dance, synthetic drums, artist imitation."
    lyrics = f"""[Intro]\n[Low Energy, Acoustic Guitar]\nA noite caiu sobre o meu caminho\nE a poeira cobriu minha direção\nMas eu ouvi Deus falar baixinho\nFilho, ainda existe perdão\n\n[Verse 1]\nEu trouxe no peito uma cerca quebrada\nE nos olhos a marca de tanto lutar\nMinha alma cansada parou na estrada\nSem saber se podia voltar\n\n[Pre-Chorus]\nQuando eu não tinha mais força pra cantar\nTua graça começou a me chamar\n\n[Chorus]\n{hook}\nTua luz me achou no chão\nSe eu pensei que era o fim da estrada\nEra o começo da salvação\n{hook}\nEu não caminho mais só\nDeus transformou minha noite escura\nEm promessa no meio do pó\n\n[Verse 2]\nA cruz no horizonte ficou mais clara\nQuando o sol rasgou o temporal\nTua misericórdia me deu casa\nE fez do meu pranto um sinal\n\n[Bridge]\n[Building Energy, Slide Guitar]\nNão foi acaso, foi Teu cuidado\nNão foi sorte, foi Tua mão\nEu estava perdido e quebrado\nMas Tu chamaste meu coração\n\n[Final Chorus]\n[Powerful, Choir Response]\n{hook}\nTua luz me achou no chão\nSe eu pensei que era o fim da estrada\nEra o começo da salvação\n{hook}\nEu não caminho mais só\nDeus transformou minha noite escura\nEm promessa no meio do pó\n\n[Outro]\n[Fade Out]\nA poeira baixou devagar\nE a fé ficou pra me guiar"""
    loop = "Cinematic rural dirt road at dawn, old wooden fence, acoustic guitar leaning near a wooden cross, amber sunrise breaking through dark storm clouds, dust and mist drifting slowly, dark country gospel blues atmosphere, slow push-in, seamless 16:9 loop, no people, no text, no logos."
    youtube = f"""Title options:\n1. {title} | Country Blues Gospel\n2. {hook} | Country Blues e Fé\n3. Louvor Country Gospel Para Recomeçar\n\nDescription:\n{title} é uma música country blues gospel original sobre {idea['theme']}. Uma canção de fé rural, estrada, cruz, poeira e esperança depois da luta.\n\nHashtags:\n#CountryBluesEFé #GospelBlues #CountryGospel #SertanejoGospel #Louvor\n\nTags:\ncountry blues gospel, country blues e fé, gospel blues brasileiro, sertanejo gospel raiz, louvor country, música gospel rural, oração gospel\n\nPinned comment:\nQual parte dessa música falou com você hoje? Escreva sua oração nos comentários.\n\nThumbnail text:\n{title.upper()[:32]}\n\nHypothesis:\nTestar como música de recomeço/oração. Medir CTR, retenção nos primeiros 30s, comentários e inscritos ganhos em 72h.\n"""
    return f"""# {title}\n\n## Tema detectado\n{idea['theme']}\n\n## Hook emocional\n{hook}\n\n## Suno Style Prompt\n{style}\n\n## Exclude Styles\n{exclude}\n\n## Lyrics for Suno\n{lyrics}\n\n## Loop Video Prompt\n{loop}\n\n## YouTube Package\n{youtube}\n"""


def write_report(records: list[VideoRecord], analysis: dict[str, Any], day: str) -> tuple[Path, Path]:
    top = records[:20]
    ideas = idea_bank(analysis)
    report_path = REPORTS / f"trend_report_{day}.md"
    ideas_path = GENERATED / f"production_ideas_{day}.md"

    lines = [
        f"# Radar Gospel Blues Viral - Relatório {day}",
        "",
        "## Resumo executivo",
        f"- Vídeos analisados: {len(records)}",
        "- Objetivo: encontrar padrões de demanda para criar músicas originais melhores, sem copiar terceiros.",
        "- Score combina velocidade de views, views totais, likes, comentários e recência.",
        "- O agente aceita URLs manuais e texto/export do NotebookLM em inputs/ para analisar suas próprias referências.",
        "",
        "## Top vídeos encontrados",
    ]
    for i, r in enumerate(top[:10], 1):
        lines += [
            f"### {i}. {r.title}",
            f"- Canal: {r.channel}",
            f"- URL: {r.url}",
            f"- Views: {r.view_count:,}".replace(',', '.'),
            f"- Views/dia: {r.views_per_day}",
            f"- Data: {r.upload_date or 'não disponível'}",
            f"- Score: {r.viral_score} ({r.opportunity_class})",
            f"- Temas detectados: {r.detected_themes}",
            "",
        ]
    lines += ["## Top canais encontrados"]
    for ch, n in analysis["channels"][:10]:
        lines.append(f"- {ch}: {n} vídeo(s) encontrado(s)")
    lines += ["", "## Tendências de tema"]
    for theme, n in analysis["themes"][:10]:
        lines.append(f"- {theme}: {n}")
    lines += ["", "## Palavras fortes em títulos"]
    for w, n in analysis["words"][:20]:
        lines.append(f"- {w}: {n}")
    lines += ["", "## Fórmulas de título recomendadas"]
    lines += [f"- {x}" for x in TITLE_FORMULAS]
    lines += ["", "## Fórmulas visuais recomendadas"]
    lines += [f"- {x}" for x in VISUAL_FORMULAS]
    lines += ["", "## Oportunidades para o canal"]
    lines += [
        "- Criar séries de oração de madrugada com country blues gospel lento.",
        "- Criar músicas de recomeço na estrada com refrão simples e repetível.",
        "- Explorar thumbnails com rosto expressivo, cruz distante e texto curto.",
        "- Fazer lotes de 7 músicas e comparar retenção/CTR após 72 horas.",
    ]
    lines += ["", "## 7 ideias originais"]
    for i, idea in enumerate(ideas, 1):
        lines += [f"### {i}. {idea['title']}", f"- Tema: {idea['theme']}", f"- Hook: {idea['hook']}", ""]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    idea_lines = [f"# Pacote de produção - {day}", "", "Conteúdo original gerado a partir de padrões de mercado, sem copiar letras ou melodias.", ""]
    for idea in ideas:
        idea_lines.append(suno_package(idea))
        idea_lines.append("\n---\n")
    ideas_path.write_text("\n".join(idea_lines), encoding="utf-8")
    return report_path, ideas_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-results", type=int, default=5, help="Resultados por query")
    ap.add_argument("--limit-queries", type=int, default=0, help="Limitar quantidade de queries para teste")
    ap.add_argument("--urls-file", default=str(INPUTS / "input_urls.txt"), help="Arquivo com URLs manuais do YouTube, uma por linha")
    ap.add_argument("--notebooklm-file", default=str(INPUTS / "notebooklm_export.md"), help="Texto/export do NotebookLM; URLs do YouTube serão extraídas automaticamente")
    ap.add_argument("--skip-search", action="store_true", help="Analisar somente URLs manuais/NotebookLM, sem busca por queries")
    ap.add_argument("--channel-video-limit", type=int, default=10, help="Quantos vídeos recentes analisar quando a URL manual for de canal")
    ap.add_argument("--no-enrich-channel-videos", action="store_true", help="Não abrir cada vídeo do canal para obter data/likes/comentários")
    args = ap.parse_args()

    day = datetime.now().date().isoformat()
    queries_path = CONFIG / "search_queries.txt"
    queries = [q.strip() for q in queries_path.read_text(encoding="utf-8").splitlines() if q.strip() and not q.strip().startswith("#")]
    if args.limit_queries:
        queries = queries[:args.limit_queries]

    records: list[VideoRecord] = []
    manual_sources = read_manual_urls(Path(args.urls_file), Path(args.notebooklm_file))
    log_path = LOGS / f"run_{day}.log"
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"START {datetime.now().isoformat()} queries={len(queries)} max={args.max_results} manual_urls={len(manual_sources)}\n")

        for source_name, url in manual_sources:
            print(f"[url:{source_name}] {url}")
            try:
                info = extract_url(url, args.channel_video_limit)
                if info and info.get("entries"):
                    channel_name = info.get("channel") or info.get("uploader") or info.get("title") or ""
                    channel_url = info.get("channel_url") or info.get("uploader_url") or url
                    for entry in [e for e in info.get("entries") or [] if e]:
                        if not args.no_enrich_channel_videos and entry.get("url"):
                            try:
                                full = extract_url(entry.get("url"), args.channel_video_limit)
                                if full and not full.get("entries"):
                                    entry = {**entry, **full}
                            except Exception as exc:
                                log.write(f"ENRICH_ERROR {entry.get('url')}: {exc}\n")
                        entry.setdefault("channel", channel_name.replace(" - Videos", ""))
                        entry.setdefault("uploader", channel_name.replace(" - Videos", ""))
                        entry.setdefault("channel_url", channel_url)
                        entry.setdefault("webpage_url", entry.get("url"))
                        records.append(build_record(f"channel:{source_name}", entry))
                    log.write(f"OK_CHANNEL {source_name}: {url} entries={len(info.get('entries') or [])}\n")
                elif info:
                    records.append(build_record(f"manual:{source_name}", info))
                    log.write(f"OK_URL {source_name}: {url}\n")
            except Exception as exc:
                print(f"[erro-url] {url}: {exc}", file=sys.stderr)
                log.write(f"ERROR_URL {source_name}: {url}: {exc}\n")

        if not args.skip_search:
            for q in queries:
                print(f"[busca] {q}")
                try:
                    entries = extract_search(q, args.max_results)
                    log.write(f"OK {q}: {len(entries)}\n")
                    for e in entries:
                        try:
                            records.append(build_record(q, e))
                        except Exception as exc:
                            log.write(f"RECORD_ERROR {q}: {exc}\n")
                except Exception as exc:
                    print(f"[erro] {q}: {exc}", file=sys.stderr)
                    log.write(f"ERROR {q}: {exc}\n")

    records = dedupe(records)
    if not records:
        print("Nenhum vídeo coletado. Verifique conexão/YouTube/yt-dlp.", file=sys.stderr)
        return 2

    raw_path, csv_path = write_outputs(records, day)
    analysis = trend_analysis(records)
    report_path, ideas_path = write_report(records, analysis, day)

    print("\nCONCLUÍDO")
    print(f"Vídeos analisados: {len(records)}")
    print(f"Raw: {raw_path}")
    print(f"Ranking CSV: {csv_path}")
    print(f"Relatório: {report_path}")
    print(f"Ideias de produção: {ideas_path}")
    print("\nTop 5:")
    for i, r in enumerate(records[:5], 1):
        print(f"{i}. {r.viral_score:05.2f} | {r.title[:90]} | {r.channel}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
