#!/usr/bin/env python3
"""Music Factory — motor de produção diária para canais de música.

Fase 1: catálogo, anti-repetição, montador de playlist e pauta diária.

Uso típico (um nicho, um dia):
    python3 cli.py daily-brief --niche country_blues_fe
    python3 cli.py add-song --niche country_blues_fe --title "..." --mood calm
    python3 cli.py set-audio --slug ... --file audio.mp3 --duration 265
    python3 cli.py build-playlist --niche country_blues_fe
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import brief, catalog, db, learn, opportunity, playlist, quality  # noqa: E402

BASE = Path(__file__).resolve().parent
NICHES_DIR = BASE / "niches"
OUT_ROOT = BASE / "out"


def cmd_daily_brief(args, conn):
    cfg = brief.load_niche(args.niches_dir, args.niche)
    r = brief.generate(conn, cfg, args.out, n_songs=args.songs,
                       niches_dir=args.niches_dir, com_playlist=args.com_playlist)
    print(f"✅ Pauta gerada: {r['out_dir']}")
    print(f"   Tema do lote: {r['tema']}")
    for f in r["faixas"]:
        print(f"   {f['n']}. {f['papel'][:24]:<24} | {f['angulo'][:40]}")
    for a in r["avisos"]:
        print(f"   ⚠️  {a}")
    print(f"\n👉 Cole no Claude: {r['out_dir']}/01-PROMPT-LETRAS.md")


def cmd_add_song(args, conn):
    t = catalog.add_track(
        conn, args.niche, args.title, theme=args.theme, mood=args.mood,
        lyrics_path=args.lyrics, duration_sec=args.duration,
        status="suno_ready" if args.lyrics else "draft",
    )
    print(f"✅ Faixa registrada: [{t['id']}] {t['title']}  (slug: {t['slug']}, mood: {t['mood']})")


def cmd_set_audio(args, conn):
    catalog.set_audio(conn, args.slug, args.file, args.duration)
    print(f"✅ Áudio registrado em {args.slug}: {args.duration}s (duração real)")


def cmd_import_acervo(args, conn):
    linhas = catalog.import_suno_folder(conn, args.folder, args.niche)
    print(f"✅ {len(linhas)} faixa(s) importada(s) para o nicho {args.niche}:")
    for t in linhas:
        print(f"   [{t['id']}] {t['title']}")
    print("\n⚠️  Durações são ESTIMADAS. Rode 'set-audio' quando tiver os arquivos.")


def cmd_build_playlist(args, conn):
    cfg = brief.load_niche(args.niches_dir, args.niche)
    plano = playlist.build(
        conn, args.niche, target_sec=args.target or cfg.get("target_sec", 3600),
        cooldown_days=cfg.get("cooldown_faixa_dias", 21),
    )
    print(f"🎵 {cfg['nome_exibicao']} — {len(plano['sequence'])} faixas, "
          f"{playlist._fmt_ts(plano['total_sec'])}\n")
    print(playlist.render_chapters(plano))
    for a in plano["warnings"]:
        print(f"\n⚠️  {a}")
    if args.save:
        pid = playlist.save(conn, plano, slug=args.save)
        print(f"\n✅ Salva como playlist #{pid} ({args.save})")


def cmd_catalog(args, conn):
    q = "SELECT * FROM tracks"
    params = ()
    if args.niche:
        q += " WHERE niche=?"
        params = (args.niche,)
    q += " ORDER BY niche, created_at DESC"
    rows = conn.execute(q, params).fetchall()
    if not rows:
        print("Catálogo vazio. Use 'import-acervo' ou 'daily-brief'.")
        return
    print(f"{'ID':>4}  {'STATUS':<11} {'MOOD':<7} {'DUR':>6}  TÍTULO")
    print("-" * 78)
    for r in rows:
        dur = f"{r['duration_sec'] or 0}s" + ("*" if r["duration_estimated"] else "")
        print(f"{r['id']:>4}  {r['status']:<11} {r['mood']:<7} {dur:>6}  {r['title'][:44]}")
    print(f"\n{len(rows)} faixa(s). (*) duração estimada")


def cmd_quality(args, conn):
    try:
        cfg = brief.load_niche(args.niches_dir, args.niche)
        prot = cfg.get("palavras_protegidas", ())
    except FileNotFoundError:
        prot = ()
    print(quality.format_report(conn, args.niche, protegidas=prot))


def cmd_opportunity(args, conn):
    cfg = brief.load_niche(args.niches_dir, args.niche)
    print(opportunity.format_report(conn, args.niche, cfg["temas"]))


def cmd_set_theme_score(args, conn):
    opportunity.save_theme_score(conn, args.niche, args.theme, args.score,
                                 keyword=args.keyword, fonte=args.fonte)
    print(f"✅ score {args.score} gravado para «{args.theme}» ({args.fonte})")


def cmd_add_published(args, conn):
    learn.add_published(conn, args.niche, args.title, args.date, args.views,
                        comments=args.comments, duration=args.duration,
                        video_url=args.url, hook=args.hook, formato=args.formato)
    print(f"✅ registrado: {args.title[:50]} ({args.views} views em {args.date})")


def cmd_cadence(args, conn):
    try:
        cfg = brief.load_niche(args.niches_dir, args.niche)
        spw = cfg.get("shorts_por_semana")
    except FileNotFoundError:
        spw = None
    print(learn.cadence_report(conn, args.niche, shorts_por_semana=spw))


def cmd_learn(args, conn):
    print(learn.format_report(conn, args.niche))
    if args.sync_vph:
        casados, total = learn.sync_vph(conn, args.niche)
        print(f"\n🔗 VPH sincronizado: {casados} de {total} vídeo(s) casaram com faixas do catálogo")


def cmd_health(args, conn):
    import glob as _glob
    import os as _os
    niches = [_os.path.basename(f)[:-5]
              for f in sorted(_glob.glob(_os.path.join(args.niches_dir, "*.json")))]
    print(learn.health_report(conn, niches, janela=args.janela, piso_vpd=args.piso))


def cmd_migrate(args, conn):
    migradas = catalog.migrate_tracks(conn, args.origem, args.destino,
                                      apenas_com_audio=not args.incluir_sem_audio)
    print(f"✅ {len(migradas)} faixa(s) migrada(s) de {args.origem} → {args.destino}")
    for t in migradas[:10]:
        print(f"   {t}")
    if len(migradas) > 10:
        print(f"   … e mais {len(migradas) - 10}")
    print("\n   As faixas chegam sem histórico de uso: o público do canal novo é outro.")


def cmd_radar(args, conn):
    cfg = brief.load_niche(args.niches_dir, args.niche)
    print(opportunity.radar_report(conn, args.niche, cfg["temas"]))


def cmd_radar_add(args, conn):
    opportunity.add_ideia(conn, args.niche, args.ideia, origem=args.origem, score=args.score)
    print(f"✅ ideia registrada em {args.niche}: {args.ideia}")


def cmd_radar_approve(args, conn):
    opportunity.aprovar_ideia(conn, args.niche, args.ideia)
    print(f"✅ aprovada. Copie para o campo `temas` de niches/{args.niche}.json")


def cmd_status(args, conn):
    print("📊 MUSIC FACTORY\n")
    for n in conn.execute("SELECT niche, COUNT(*) c FROM tracks GROUP BY niche"):
        pron = conn.execute(
            "SELECT COUNT(*) c FROM tracks WHERE niche=? AND status IN ('audio_ok','published')",
            (n["niche"],)).fetchone()["c"]
        eleg = len(catalog.eligible_tracks(conn, n["niche"]))
        print(f"  {n['niche']:<22} {n['c']:>3} faixas | {pron:>3} com áudio | {eleg:>3} elegíveis hoje")
    pls = conn.execute("SELECT COUNT(*) c FROM playlists").fetchone()["c"]
    print(f"\n  playlists montadas: {pls}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Music Factory — produção diária de canais de música")
    p.add_argument("--db-path", default=db.DEFAULT_DB, help="caminho do SQLite")
    p.add_argument("--niches-dir", default=str(NICHES_DIR))
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("daily-brief", help="gera a pauta do dia de um nicho")
    s.add_argument("--niche", required=True)
    s.add_argument("--out", default=str(OUT_ROOT))
    s.add_argument("--songs", type=int, default=None)
    s.add_argument("--com-playlist", action="store_true",
                   help="também gera o pacote de metadados da playlist")
    s.set_defaults(func=cmd_daily_brief)

    s = sub.add_parser("add-song", help="registra uma música no catálogo")
    s.add_argument("--niche", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--mood", default="retain", choices=catalog.MOODS)
    s.add_argument("--theme")
    s.add_argument("--lyrics", help="caminho do arquivo de letra")
    s.add_argument("--duration", type=int)
    s.set_defaults(func=cmd_add_song)

    s = sub.add_parser("set-audio", help="registra o áudio e a duração REAL")
    s.add_argument("--slug", required=True)
    s.add_argument("--file", required=True)
    s.add_argument("--duration", type=int, required=True)
    s.set_defaults(func=cmd_set_audio)

    s = sub.add_parser("import-acervo", help="importa lote Suno já gerado")
    s.add_argument("--niche", required=True)
    s.add_argument("--folder", required=True)
    s.set_defaults(func=cmd_import_acervo)

    s = sub.add_parser("build-playlist", help="monta playlist a partir do acervo")
    s.add_argument("--niche", required=True)
    s.add_argument("--target", type=int, help="duração alvo em segundos")
    s.add_argument("--save", help="slug para persistir a playlist")
    s.set_defaults(func=cmd_build_playlist)

    s = sub.add_parser("catalog", help="lista o catálogo")
    s.add_argument("--niche")
    s.set_defaults(func=cmd_catalog)

    s = sub.add_parser("quality", help="saturação de imagens, rimas e títulos")
    s.add_argument("--niche", required=True)
    s.set_defaults(func=cmd_quality)

    s = sub.add_parser("opportunity", help="ranking de temas por demanda real")
    s.add_argument("--niche", required=True)
    s.set_defaults(func=cmd_opportunity)

    s = sub.add_parser("set-theme-score", help="grava score de oportunidade de um tema")
    s.add_argument("--niche", required=True)
    s.add_argument("--theme", required=True)
    s.add_argument("--score", type=float, required=True)
    s.add_argument("--keyword")
    s.add_argument("--fonte", default="vidiq")
    s.set_defaults(func=cmd_set_theme_score)

    s = sub.add_parser("add-published", help="registra vídeo publicado (views reais)")
    s.add_argument("--niche", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--date", required=True, help="AAAA-MM-DD")
    s.add_argument("--views", type=int, required=True)
    s.add_argument("--comments", type=int, default=0)
    s.add_argument("--duration", help="1:54:49")
    s.add_argument("--url")
    s.add_argument("--hook", help="sobrescreve o gancho extraído do título")
    s.add_argument("--formato", choices=["short", "long"],
                   help="padrão: deduzido da duração (<=3min = short)")
    s.set_defaults(func=cmd_add_published)

    s = sub.add_parser("cadence", help="Shorts por semana × entrega dos longos")
    s.add_argument("--niche", required=True)
    s.set_defaults(func=cmd_cadence)

    s = sub.add_parser("learn", help="desempenho real e colisão de ganchos")
    s.add_argument("--niche", required=True)
    s.add_argument("--sync-vph", action="store_true",
                   help="copia views/dia para o catálogo (usado na abertura da playlist)")
    s.set_defaults(func=cmd_learn)

    s = sub.add_parser("health", help="saúde dos canais e decisão de abandono")
    s.add_argument("--janela", type=int, default=60,
                   help="dias de avaliação antes de julgar um canal (padrão 60)")
    s.add_argument("--piso", type=float, help="v/dia mínimo aceitável")
    s.set_defaults(func=cmd_health)

    s = sub.add_parser("migrate-tracks", help="leva o acervo para um canal novo")
    s.add_argument("--origem", required=True)
    s.add_argument("--destino", required=True)
    s.add_argument("--incluir-sem-audio", action="store_true")
    s.set_defaults(func=cmd_migrate)

    s = sub.add_parser("radar", help="ideias novas de música pendentes")
    s.add_argument("--niche", required=True)
    s.set_defaults(func=cmd_radar)

    s = sub.add_parser("radar-add", help="registra ideia de tema descoberta")
    s.add_argument("--niche", required=True)
    s.add_argument("--ideia", required=True)
    s.add_argument("--origem", default="radar")
    s.add_argument("--score", type=float)
    s.set_defaults(func=cmd_radar_add)

    s = sub.add_parser("radar-approve", help="aprova ideia para virar tema")
    s.add_argument("--niche", required=True)
    s.add_argument("--ideia", required=True)
    s.set_defaults(func=cmd_radar_approve)

    s = sub.add_parser("status", help="visão geral")
    s.set_defaults(func=cmd_status)

    args = p.parse_args(argv)
    conn = db.connect(args.db_path)
    try:
        args.func(args, conn)
    except (LookupError, ValueError, FileNotFoundError, NotADirectoryError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
