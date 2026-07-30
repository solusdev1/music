"""Geração da pauta diária: tema, títulos, prompt de letras e pacote da playlist.

Divisão de responsabilidade — o Python cuida de ESTADO e MONTAGEM
(o que já foi usado, o que entra hoje, em que ordem, com que timestamp);
a escrita criativa das letras continua sendo tarefa do modelo, e este
módulo entrega o prompt pronto para isso.
"""

import json
from datetime import date
from pathlib import Path

from . import catalog, playlist


def load_niche(niches_dir, niche):
    path = Path(niches_dir) / f"{niche}.json"
    if not path.exists():
        disponiveis = sorted(p.stem for p in Path(niches_dir).glob("*.json"))
        raise FileNotFoundError(
            f"nicho {niche!r} não configurado em {niches_dir}. Disponíveis: {disponiveis or 'nenhum'}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def make_titles(conn, cfg, n=3):
    """Gera títulos evitando ganchos usados recentemente."""
    ganchos = catalog.pick_hook(
        conn, cfg["niche"], cfg["ganchos"], cooldown_days=cfg.get("cooldown_gancho_dias", 30)
    )
    formulas = [cfg["formula_titulo"]] + list(cfg.get("formula_alt", []))
    beneficios = cfg["beneficios"]
    titulos = []
    for i in range(min(n, len(ganchos))):
        formula = formulas[i % len(formulas)]
        titulos.append({
            "gancho": ganchos[i],
            "titulo": formula.replace("{GANCHO}", ganchos[i])
                             .replace("{BENEFICIO}", beneficios[i % len(beneficios)]),
        })
    return titulos


def lyrics_prompt(cfg, tema, n_musicas, titulos):
    """Prompt pronto para colar no Claude e receber as letras do dia."""
    return f"""# PAUTA DE LETRAS — {cfg['nome_exibicao']} — {date.today().isoformat()}

Gere **{n_musicas} letras completas** para Suno, canal "{cfg['canal']}" ({cfg['idioma']}).

**Tema do dia:** {tema}

**Style prompt (idêntico para todas):**
{cfg['style_prompt']}

**Exclude styles:**
{cfg['exclude_styles']}

## Regras
- Estrutura com metatags Suno: [Intro], [Verse 1], [Pre-Chorus], [Chorus],
  [Verse 2], [Bridge], [Final Chorus], [Outro].
- Refrão repetível e fácil de lembrar (é playlist, não single).
- Linguagem concreta e rural: estrada, lamparina, poeira, chuva, varanda, mesa.
- Não inventar citação bíblica. O tema é inspiração, não citação literal.
- Variar o papel de cada música dentro da playlist:
  1. retenção (energia média, refrão forte)
  2. narrativa (história/testemunho, puxa comentário)
  3. oração (lenta, íntima)
  4. renovação (esperança, virada)
  5. descanso (fecho calmo, quase ambiente) → marcar mood **calm**

## Para cada música, devolva
```
TITULO: ...
MOOD: retain|open|calm
LETRA:
[Intro]
...
```

## Títulos de playlist já reservados (não repetir gancho)
{chr(10).join('- ' + t['titulo'] for t in titulos)}

Depois de gerar, salve cada letra e rode:
`python3 cli.py add-song --niche {cfg['niche']} --title "..." --mood ... --lyrics arquivo.txt`
"""


def descricao(cfg, tema, chapters, titulo):
    return f"""{titulo}

Se o seu coração está cansado, esta playlist foi preparada para te ajudar a
descansar em Deus e renovar suas forças. Inspirada em {tema}.

Nesta coletânea de Country Blues Gospel em português reunimos músicas novas
do canal {cfg['canal']} com louvores que já fazem parte da nossa caminhada.

Dê play, respire fundo e deixe Deus falar ao seu coração.

⏱️ TRACKLIST
{chapters}

🙏 Se essa playlist falou com você, inscreva-se no canal {cfg['canal']},
ative o sininho e compartilhe com alguém que precisa de esperança hoje.

{' '.join(cfg['hashtags'])}

---
Música gerada com auxílio de inteligência artificial.
"""


def generate(conn, cfg, out_root, *, today=None, n_songs=None):
    """Gera a pasta da pauta do dia. Retorna caminho e avisos."""
    today = today or date.today().isoformat()
    n_songs = n_songs or cfg.get("songs_per_day", 5)
    niche = cfg["niche"]
    avisos = []

    tema, aviso_tema = catalog.pick_theme(
        conn, niche, cfg["temas"], cooldown_days=cfg.get("cooldown_tema_dias", 60)
    )
    if aviso_tema:
        avisos.append(aviso_tema)

    titulos = make_titles(conn, cfg)

    # Cria os slots das músicas novas do dia (draft: letra e áudio ainda não existem)
    novas_ids = []
    for i in range(1, n_songs + 1):
        row = catalog.add_track(
            conn, niche, f"[{today} #{i}] a definir",
            slug=f"{niche}-{today}-{i}", theme=tema,
            mood="calm" if i == n_songs else "retain",
            style_prompt=cfg["style_prompt"], exclude_styles=cfg["exclude_styles"],
            duration_sec=cfg.get("duracao_media_faixa_sec", 270), status="draft",
        )
        novas_ids.append(row["id"])

    # Plano da playlist: novas do dia + acervo elegível
    plano = playlist.build(
        conn, niche, new_track_ids=novas_ids,
        target_sec=cfg.get("target_sec", 3600),
        cooldown_days=cfg.get("cooldown_faixa_dias", 21),
    )
    avisos.extend(plano["warnings"])
    chapters = playlist.render_chapters(plano)

    out = Path(out_root) / today / niche
    (out / "playlist").mkdir(parents=True, exist_ok=True)

    (out / "01-PROMPT-PARA-CLAUDE-LETRAS.md").write_text(
        lyrics_prompt(cfg, tema, n_songs, titulos), encoding="utf-8")
    p = out / "playlist"
    p.joinpath("titulo-variacoes.txt").write_text(
        "\n".join(f"{i}. {t['titulo']}" for i, t in enumerate(titulos, 1)), encoding="utf-8")
    p.joinpath("tracklist-chapters.txt").write_text(chapters, encoding="utf-8")
    p.joinpath("descricao.txt").write_text(
        descricao(cfg, tema, chapters, titulos[0]["titulo"]), encoding="utf-8")
    p.joinpath("hashtags.txt").write_text(" ".join(cfg["hashtags"]), encoding="utf-8")
    p.joinpath("tags-youtube.txt").write_text(", ".join(cfg["tags_youtube"]), encoding="utf-8")
    p.joinpath("comentario-fixado.txt").write_text(cfg["comentario_fixado"], encoding="utf-8")
    p.joinpath("prompt-thumbnail.txt").write_text(cfg["prompt_thumbnail"], encoding="utf-8")

    novas = sum(1 for i in plano["sequence"] if i["is_new"])
    resumo = f"""# PAUTA DO DIA — {cfg['nome_exibicao']} — {today}

## Tema escolhido
**{tema}**
_Selecionado automaticamente: não usado nos últimos {cfg.get('cooldown_tema_dias', 60)} dias._

## Playlist planejada
- Faixas: **{len(plano['sequence'])}** ({novas} novas + {len(plano['sequence']) - novas} do acervo)
- Duração: **{playlist._fmt_ts(plano['total_sec'])}** (alvo {playlist._fmt_ts(plano['target_sec'])})
- Abertura: **{plano['sequence'][0]['title']}** (maior VPH do acervo)

## Título recomendado
{titulos[0]['titulo']}

## O que fazer agora
1. Cole `01-PROMPT-PARA-CLAUDE-LETRAS.md` no Claude → recebe as {n_songs} letras
2. Registre cada letra: `cli.py add-song --niche {niche} ...`
3. Gere os áudios no Suno com o style prompt do nicho
4. Registre a duração real: `cli.py set-audio --slug ... --file ... --duration ...`
5. Refaça a playlist com timestamps corretos: `cli.py build-playlist --niche {niche}`

## Avisos
{chr(10).join('- ⚠️ ' + a for a in avisos) if avisos else '- nenhum'}

## Tracklist provisória
```
{chapters}
```
"""
    (out / "00-RESUMO-DO-DIA.md").write_text(resumo, encoding="utf-8")

    playlist.save(conn, plano, slug=f"{niche}-{today}", title=titulos[0]["titulo"])
    catalog.register_theme(conn, niche, tema)
    catalog.register_hook(conn, niche, titulos[0]["gancho"])

    return {"out_dir": out, "plano": plano, "tema": tema,
            "titulos": titulos, "avisos": avisos}
