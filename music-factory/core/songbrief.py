"""Pauta de criação musical — o núcleo do sistema.

Substitui o prompt único que pedia "5 letras no mesmo tema". Aquele desenho
produzia cinco variações da mesma música: mesmo tema, mesmo ângulo narrativo
e o MESMO style prompt para todas as faixas — igual na letra e igual no som.

Aqui cada faixa do lote recebe:
  · um ângulo narrativo próprio (de quem é a história)
  · uma variação de som própria (para o Suno não devolver a mesma faixa 5x)
  · um papel definido dentro do lote
  · a lista do que já está gasto no acervo

O tema continua compartilhado — é o que dá unidade ao lote —, mas tudo o que
faz duas músicas soarem iguais passa a ser deliberadamente diferente.
"""

from datetime import date
from pathlib import Path

from . import catalog, quality


def _rodizio(lista, i, fallback=""):
    return lista[i % len(lista)] if lista else fallback


def montar_lote(conn, cfg, tema, n_musicas, *, evitar=None):
    """Especifica cada faixa do lote antes de qualquer texto ser escrito."""
    angulos = list(cfg.get("angulos", []))
    variacoes = list(cfg.get("variacoes_estilo", []))
    papeis = list(cfg.get("papeis", []))
    instrumental = cfg.get("formato") == "instrumental"

    # ângulos rotacionam por uso histórico: o lote de amanhã não repete o de hoje
    usados = {
        r["hook"]: r["last"]
        for r in conn.execute(
            "SELECT hook, MAX(used_at) AS last FROM hook_usage WHERE niche=? GROUP BY hook",
            (cfg["niche"] + "::angulo",),
        )
    } if angulos else {}
    ordenados = sorted(angulos, key=lambda a: usados.get(a, "")) if angulos else []

    faixas = []
    for i in range(n_musicas):
        faixas.append({
            "n": i + 1,
            "angulo": _rodizio(ordenados, i, "livre"),
            "variacao": _rodizio(variacoes, i, ""),
            "papel": _rodizio(papeis, i, "faixa de retenção"),
            "mood": "calm" if i == n_musicas - 1 else "retain",
            "style_prompt": _style_da_faixa(cfg, _rodizio(variacoes, i, "")),
            "instrumental": instrumental,
        })
    return faixas


def _style_da_faixa(cfg, variacao):
    """Identidade do canal + instrumentação da faixa.

    Usa `style_base` (só o que nunca muda) quando existe. Concatenar a
    variação ao style_prompt completo criava contradição — a base afirmava
    "slide guitar, coral final" enquanto a variação pedia "quase acústico,
    sem coral", e o Suno responde mal a prompt que se contradiz.
    """
    base = cfg.get("style_base") or cfg["style_prompt"]
    return f"{base}, {variacao}" if variacao else base


def registrar_angulos(conn, niche, faixas):
    for f in faixas:
        if f["angulo"] != "livre":
            catalog.register_hook(conn, niche + "::angulo", f["angulo"])


def _bloco_evitar(evitar):
    if not evitar or not evitar.get("palavras"):
        return ""
    linhas = [f"\n### Já gasto no acervo ({evitar['n_musicas']} letras analisadas)",
              f"**Não use estas imagens:** {', '.join(evitar['palavras'])}"]
    if evitar.get("rimas"):
        linhas.append(f"**Não feche verso com:** {', '.join(evitar['rimas'])}")
    linhas.append("Se a emoção pedir uma delas, mostre o gesto de alguém diante da cena, "
                  "ou o detalhe que ninguém repara.")
    return "\n".join(linhas)


def _bloco_cultura(cfg):
    cul = cfg.get("cultura") or {}
    if not cul:
        return ""
    L = [f"\n### Cultura — {cfg.get('pais','?')} / {cfg.get('idioma','?')}",
         "Escreva nativo deste país, não traduzido."]
    if cul.get("referencias"):
        L.append(f"**Repertório desta cultura:** {', '.join(cul['referencias'])}")
    if cul.get("proibido"):
        L.append(f"**Nunca transponha:** {', '.join(cul['proibido'])}")
    if cul.get("nota"):
        L.append(cul["nota"])
    return "\n".join(L)


def prompt_lote(cfg, tema, faixas, *, evitar=None, irmaos=()):
    """Prompt do dia: cada faixa especificada individualmente."""
    instrumental = cfg.get("formato") == "instrumental"
    unidade = "faixa instrumental" if instrumental else "letra"

    blocos = []
    for f in faixas:
        b = [f"### FAIXA {f['n']} — papel: {f['papel']}"]
        if not instrumental:
            b.append(f"**Ângulo narrativo (obrigatório, não repita o das outras):** {f['angulo']}")
        b.append(f"**Cor sonora desta faixa:** {f['variacao'] or 'padrão do canal'}")
        b.append(f"**Mood:** {f['mood']}")
        blocos.append("\n".join(b))

    if instrumental:
        saida = ("```\nFAIXA n\nTITULO: ...\nESTRUTURA: [Intro Xmin][Tema Ymin][Sustain Zmin][Fade Wmin]\n"
                 "DIREÇÃO SONORA: instrumentação, andamento, arco dinâmico\n```")
        regra_extra = ""
    else:
        saida = "```\nFAIXA n\nTITULO: ...\nLETRA:\n[Intro]\n...\n```"
        regra_extra = (
            "\n- **Cada faixa é uma história diferente.** Mesmo tema, personagens e "
            "cenas distintas. Se duas faixas puderem trocar de título sem ninguém "
            "notar, refaça.")

    irmaos_txt = ""
    if irmaos:
        irmaos_txt = (f"\n> ⚠️ Canais irmãos: {', '.join(irmaos)}. Este tema pode ter saído "
                      f"lá em outro idioma — mude ângulo, cenário e personagem, não traduza.\n")

    regras = "\n".join("- " + r for r in cfg.get("regras_extra", []))

    return f"""# PAUTA DE MÚSICAS — {cfg['nome_exibicao']} — {date.today().isoformat()}

Gere **{len(faixas)} {unidade}s** para Suno. Canal "{cfg['canal']}" · {cfg.get('idioma','pt-BR')}

**Tema que une o lote:** {tema}
{irmaos_txt}
## Estrutura
{cfg.get('estrutura', '[Intro] [Verse 1] [Chorus] [Verse 2] [Bridge] [Final Chorus] [Outro]')}

## Regras
{regras}{regra_extra}
{_bloco_cultura(cfg)}
{_bloco_evitar(evitar)}

---

## As {len(faixas)} faixas deste lote

{chr(10).join(chr(10) + b for b in blocos)}

---

## Formato de resposta
{saida}

Os arquivos de style e exclude já estão prontos em `musicas/NN-*/`.
Cole a letra de cada faixa em `03-lyrics-suno.txt` e registre:
`python3 cli.py add-song --niche {cfg['niche']} --title "..." --mood ... --lyrics <arquivo>`
"""


def escrever_pasta(cfg, tema, faixas, out_dir, *, evitar=None, irmaos=()):
    """Escreve a pauta e os arquivos Suno prontos de cada faixa."""
    out = Path(out_dir)
    (out / "musicas").mkdir(parents=True, exist_ok=True)

    (out / "01-PROMPT-LETRAS.md").write_text(
        prompt_lote(cfg, tema, faixas, evitar=evitar, irmaos=irmaos), encoding="utf-8")

    for f in faixas:
        pasta = out / "musicas" / f"{f['n']:02d}-{catalog.slugify(f['papel'])[:28]}"
        pasta.mkdir(parents=True, exist_ok=True)
        pasta.joinpath("01-style-prompt-suno.txt").write_text(f["style_prompt"] + "\n", encoding="utf-8")
        pasta.joinpath("02-exclude-styles-suno.txt").write_text(cfg["exclude_styles"] + "\n", encoding="utf-8")
        pasta.joinpath("03-lyrics-suno.txt").write_text(
            f"(cole aqui a letra da FAIXA {f['n']})\n", encoding="utf-8")
        pasta.joinpath("00-BRIEFING.txt").write_text(
            f"FAIXA {f['n']}\n"
            f"Tema do lote : {tema}\n"
            f"Ângulo       : {f['angulo']}\n"
            f"Papel        : {f['papel']}\n"
            f"Cor sonora   : {f['variacao'] or 'padrão do canal'}\n"
            f"Mood         : {f['mood']}\n", encoding="utf-8")
    return out
