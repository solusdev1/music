"""Geração da pauta diária: tema, títulos, prompt de letras e pacote da playlist.

Divisão de responsabilidade — o Python cuida de ESTADO e MONTAGEM
(o que já foi usado, o que entra hoje, em que ordem, com que timestamp);
a escrita criativa das letras continua sendo tarefa do modelo, e este
módulo entrega o prompt pronto para isso.
"""

import json
from datetime import date
from pathlib import Path

from . import catalog, learn, opportunity, playlist, quality, songbrief


def load_niche(niches_dir, niche):
    path = Path(niches_dir) / f"{niche}.json"
    if not path.exists():
        disponiveis = sorted(p.stem for p in Path(niches_dir).glob("*.json"))
        raise FileNotFoundError(
            f"nicho {niche!r} não configurado em {niches_dir}. Disponíveis: {disponiveis or 'nenhum'}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_group(niches_dir, cfg):
    """Nichos irmãos (mesmo `grupo`), incluindo o próprio. Sem grupo: só ele."""
    grupo = cfg.get("grupo")
    if not grupo:
        return [cfg["niche"]], []
    irmaos, nomes = [], []
    for path in sorted(Path(niches_dir).glob("*.json")):
        outro = json.loads(path.read_text(encoding="utf-8"))
        if outro.get("grupo") == grupo:
            irmaos.append(outro["niche"])
            if outro["niche"] != cfg["niche"]:
                nomes.append(outro.get("nome_exibicao", outro["niche"]))
    return irmaos or [cfg["niche"]], nomes


def _rotulo_duracao(total_sec, idioma="pt"):
    """Rótulo honesto de duração para o título.

    Anunciar '1 Hour' numa playlist de 26 minutos quebra a promessa logo
    nos primeiros segundos — e é o tipo de coisa que derruba retenção e
    rende comentário ruim. O rótulo sai do total real.
    """
    if not total_sec:
        return ""
    m = total_sec // 60
    en = str(idioma)[:2].lower() == "en"
    if m >= 55:
        h = round(total_sec / 3600)
        return f"{h} Hour{'s' if h > 1 else ''}" if en else f"{h} Hora{'s' if h > 1 else ''}"
    dez = max(10, (m // 10) * 10)
    return f"{dez} Minutes" if en else f"{dez} Minutos"


def make_titles(conn, cfg, n=3, *, total_sec=None):
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
            "titulo": (formula.replace("{GANCHO}", ganchos[i])
                              .replace("{BENEFICIO}", beneficios[i % len(beneficios)])
                              .replace("{DURACAO}", _rotulo_duracao(
                                  total_sec, cfg.get("idioma", "pt")))),
        })
    return titulos


def _bloco_qualidade(evitar):
    """Trecho do prompt que carrega o aprendizado do acervo."""
    if not evitar or evitar["n_musicas"] == 0:
        return ""
    partes = [
        f"\n## ⚠️ ANTI-REPETIÇÃO (extraído de {evitar['n_musicas']} letras já no acervo)",
        "Estes recursos já estão gastos. **Não use** — encontre imagem nova para a mesma emoção.",
    ]
    if evitar["palavras"]:
        partes.append(f"\n**Imagens saturadas:** {', '.join(evitar['palavras'])}")
    if evitar["rimas"]:
        partes.append(
            f"**Terminações de verso viciadas:** {', '.join(evitar['rimas'])} "
            "— varie a rima, não feche todo verso igual."
        )
    partes.append(
        "\nSe a emoção pedir uma dessas imagens, troque o ângulo concreto: "
        "em vez de repetir o objeto, mostre o gesto de alguém diante dele, "
        "ou o detalhe que ninguém repara na mesma cena."
    )
    return "\n".join(partes)


def _bloco_cultura(cfg):
    """Registro cultural do canal — o que faz a letra soar nativa, não traduzida."""
    cul = cfg.get("cultura") or {}
    if not cul:
        return ""
    L = [f"\n## 🌎 CULTURA — {cfg.get('pais', '?')} / {cfg.get('idioma', '?')}"]
    L.append(
        "Escreva **nativo deste país**, não traduzido. A mesma emoção existe em "
        "toda cultura, mas as imagens que a carregam mudam."
    )
    if cul.get("referencias"):
        L.append(f"\n**Repertório de imagens desta cultura:** {', '.join(cul['referencias'])}")
    if cul.get("proibido"):
        L.append(
            f"**Não transponha de outra cultura:** {', '.join(cul['proibido'])} "
            "— soam falsos neste canal."
        )
    if cul.get("nota"):
        L.append(f"\n{cul['nota']}")
    return "\n".join(L)


def _bloco_irmaos(cfg, tema, irmaos):
    """Aviso de canais irmãos — impede que o mesmo tema vire a mesma música."""
    if not irmaos:
        return ""
    return (
        f"\n## ⚠️ CANAIS IRMÃOS\n"
        f"Este grupo tem também: {', '.join(irmaos)}.\n"
        f"O tema «{tema}» pode já ter sido usado lá em outro idioma. "
        "Não escreva uma versão traduzida: mude o ângulo narrativo, o cenário "
        "e o personagem. Mesma verdade, outra história."
    )


def lyrics_prompt(cfg, tema, n_musicas, titulos, evitar=None, irmaos=()):
    """Prompt do dia, montado a partir da config do nicho."""
    instrumental = cfg.get("formato") == "instrumental"
    unidade = "faixas instrumentais" if instrumental else "letras completas"

    regras = list(cfg.get("regras_extra", []))
    papeis = cfg.get("papeis", [])
    bloco_papeis = ""
    if papeis:
        bloco_papeis = "\n- Varie o papel de cada faixa na playlist:\n" + "\n".join(
            f"  {i}. {p}" for i, p in enumerate(papeis, 1)
        )

    if instrumental:
        formato_saida = """```
TITULO: ...
MOOD: retain|open|calm
ESTRUTURA: [Intro Xmin][Tema Ymin][Sustain Zmin][Fade Wmin]
DIREÇÃO SONORA: instrumentos, andamento, arco dinâmico
```"""
    else:
        formato_saida = """```
TITULO: ...
MOOD: retain|open|calm
LETRA:
[Intro]
...
```"""

    return f"""# PAUTA — {cfg['nome_exibicao']} — {date.today().isoformat()}

Gere **{n_musicas} {unidade}** para Suno, canal "{cfg['canal']}".
Idioma: **{cfg.get('idioma', 'pt-BR')}** · País-alvo: **{cfg.get('pais', 'BR')}**

**Tema do dia:** {tema}

**Style prompt (idêntico para todas):**
{cfg['style_prompt']}

**Exclude styles:**
{cfg['exclude_styles']}

## Estrutura
{cfg.get('estrutura', '[Intro] [Verse 1] [Chorus] [Verse 2] [Bridge] [Final Chorus] [Outro]')}

## Regras
{chr(10).join('- ' + r for r in regras) if regras else '- (sem regras extras configuradas)'}{bloco_papeis}
{_bloco_cultura(cfg)}
{_bloco_irmaos(cfg, tema, irmaos)}
{_bloco_qualidade(evitar)}

## Para cada faixa, devolva
{formato_saida}

## Títulos de playlist já reservados (não repetir gancho)
{chr(10).join('- ' + t['titulo'] for t in titulos)}

Depois de gerar, registre cada faixa:
`python3 cli.py add-song --niche {cfg['niche']} --title "..." --mood ... --lyrics arquivo.txt`
"""


DESCRICAO_PADRAO = {
    "pt": """{titulo}

Esta playlist foi preparada para acompanhar quem precisa descansar e renovar
as forças. Inspirada em {tema}.

Dê play, respire fundo e deixe a música falar com você.

⏱️ FAIXAS
{chapters}

🙏 Se algo aqui falou com você, inscreva-se no canal {canal}, ative o sininho
e compartilhe com alguém que precisa ouvir isso hoje.

{hashtags}

---
Música criada com auxílio de inteligência artificial.""",

    "en": """{titulo}

Made for anyone who needs to set the weight down for a while. Inspired by {tema}.

Press play, let your shoulders come down, and let it sit with you.

⏱️ TRACKS
{chapters}

🙏 If something here found you tonight, subscribe to {canal}, tap the bell,
and send it to somebody walking a hard road right now.

{hashtags}

---
Music created with the assistance of artificial intelligence.""",

    "es": """{titulo}

Preparada para acompañar a quien necesita descansar y renovar las fuerzas.
Inspirada en {tema}.

Dale play, respira hondo y deja que la música te hable.

⏱️ CANCIONES
{chapters}

🙏 Si algo aquí habló contigo, suscríbete al canal {canal}, activa la
campanita y compártelo con alguien que lo necesite hoy.

{hashtags}

---
Música creada con ayuda de inteligencia artificial.""",
}


def descricao(cfg, tema, chapters, titulo):
    """Descrição no idioma do canal.

    O template vem do config quando existe; senão usa o padrão do idioma.
    Antes isto era português fixo, o que gerava descrição em PT num canal
    em inglês.
    """
    tpl = cfg.get("descricao_template") or DESCRICAO_PADRAO.get(
        str(cfg.get("idioma", "pt"))[:2].lower(), DESCRICAO_PADRAO["pt"])
    return tpl.format(titulo=titulo, tema=tema, chapters=chapters,
                      canal=cfg["canal"], hashtags=" ".join(cfg["hashtags"]))


def generate(conn, cfg, out_root, *, today=None, n_songs=None, niches_dir=None,
             com_playlist=False):
    """Gera a pasta da pauta do dia. Retorna caminho e avisos."""
    today = today or date.today().isoformat()
    n_songs = n_songs or cfg.get("songs_per_day", 5)
    niche = cfg["niche"]
    niches_dir = niches_dir or Path(__file__).resolve().parent.parent / "niches"
    avisos = []

    cooldown_tema = cfg.get("cooldown_tema_dias", 60)
    grupo_niches, irmaos = load_group(niches_dir, cfg)
    if irmaos:
        avisos.append(
            f"cooldown de tema compartilhado com {len(irmaos)} canal(is) irmão(s): "
            f"{', '.join(irmaos)}"
        )
    tema, motivo = opportunity.pick_theme_by_opportunity(
        conn, niche, cfg["temas"], cooldown_days=cooldown_tema,
        grupo_niches=grupo_niches,
        cooldown_grupo_days=cfg.get("cooldown_tema_grupo_dias", 14),
    )
    if tema:
        criterio = f"maior oportunidade — {motivo}"
    else:
        avisos.append(f"tema por rodízio simples (sem dado de oportunidade: {motivo})")
        tema, aviso_tema = catalog.pick_theme(
            conn, niche, cfg["temas"], cooldown_days=cooldown_tema,
            grupo_niches=grupo_niches,
            cooldown_grupo_days=cfg.get("cooldown_tema_grupo_dias", 14),
        )
        criterio = f"rodízio — não usado nos últimos {cooldown_tema} dias"
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

    # Playlist só é montada quando pedida — não é caminho diário
    plano, chapters = None, ""
    if com_playlist:
        plano = playlist.build(
            conn, niche, new_track_ids=novas_ids,
            target_sec=cfg.get("target_sec", 3600),
            cooldown_days=cfg.get("cooldown_faixa_dias", 21),
        )
        avisos.extend(plano["warnings"])
        chapters = playlist.render_chapters(plano)

    out = Path(out_root) / today / niche
    out.mkdir(parents=True, exist_ok=True)

    evitar = quality.avoid_list(conn, niche, protegidas=cfg.get("palavras_protegidas", ()),
                               idioma=cfg.get("idioma"))
    if evitar["palavras"]:
        avisos.append(
            f"{len(evitar['palavras'])} imagem(ns) saturada(s) no acervo "
            f"({', '.join(evitar['palavras'][:5])}…) — a pauta já manda evitar."
        )

    # ── NÚCLEO: a pauta de criação musical ──
    faixas = songbrief.montar_lote(conn, cfg, tema, n_songs, evitar=evitar)
    songbrief.escrever_pasta(cfg, tema, faixas, out, evitar=evitar, irmaos=irmaos)
    songbrief.registrar_angulos(conn, niche, faixas)

    # ── OPCIONAL: pacote de playlist, fora do caminho diário ──
    if com_playlist:
        p = out / "playlist"
        p.mkdir(parents=True, exist_ok=True)
        p.joinpath("titulo-variacoes.txt").write_text(
            "\n".join(f"{i}. {t['titulo']}" for i, t in enumerate(titulos, 1)), encoding="utf-8")
        p.joinpath("tracklist-chapters.txt").write_text(chapters, encoding="utf-8")
        p.joinpath("descricao.txt").write_text(
            descricao(cfg, tema, chapters, titulos[0]["titulo"]), encoding="utf-8")
        p.joinpath("hashtags.txt").write_text(" ".join(cfg["hashtags"]), encoding="utf-8")
        p.joinpath("tags-youtube.txt").write_text(", ".join(cfg["tags_youtube"]), encoding="utf-8")
        p.joinpath("comentario-fixado.txt").write_text(cfg["comentario_fixado"], encoding="utf-8")
        p.joinpath("prompt-thumbnail.txt").write_text(cfg["prompt_thumbnail"], encoding="utf-8")

    resumo = f"""# PAUTA DO DIA — {cfg['nome_exibicao']} — {today}

## Tema do lote
**{tema}**
_Critério: {criterio}._

## As {n_songs} faixas
| # | papel | ângulo | cor sonora |
|---|-------|--------|------------|
""" + "\n".join(
        f"| {f['n']} | {f['papel'][:26]} | {f['angulo'][:44]} | {(f['variacao'] or '—')[:40]} |"
        for f in faixas
    ) + f"""

## O que fazer
1. Cole `01-PROMPT-LETRAS.md` no Claude → recebe as {n_songs} {'direções sonoras' if cfg.get('formato')=='instrumental' else 'letras'}
2. Salve cada uma em `musicas/NN-*/03-lyrics-suno.txt` (style e exclude já estão prontos)
3. Gere no Suno e registre: `cli.py add-song --niche {niche} ...`

## Avisos
{chr(10).join('- ⚠️ ' + a for a in avisos) if avisos else '- nenhum'}
"""
    (out / "00-PAUTA-DO-DIA.md").write_text(resumo, encoding="utf-8")

    if com_playlist and plano:
        playlist.save(conn, plano, slug=f"{niche}-{today}", title=titulos[0]["titulo"])
    catalog.register_theme(conn, niche, tema)
    catalog.register_hook(conn, niche, titulos[0]["gancho"])

    return {"out_dir": out, "plano": plano, "tema": tema, "faixas": faixas,
            "titulos": titulos, "avisos": avisos}
