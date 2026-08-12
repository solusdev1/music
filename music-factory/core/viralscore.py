"""Score 0–100 de uma faixa pronta, antes de virar áudio.

O sistema já mede o acervo (`quality`) e o que foi publicado (`learn`). O que
faltava era o passo do meio: a letra que acabou de sair do modelo, ainda com
tempo de ser refeita. Uma faixa ruim que passa daqui custa geração no Suno,
render e uma vaga na playlist.

Os cinco critérios são os que o histórico do próprio portfólio mostrou
importar, não uma lista genérica de boas práticas:

  estrutura      — faixa sem ponte/outro sai curta e sem arco
  refrão         — refrão longo demais não é cantado junto; é o que retém
  gancho em 3s   — abertura longa é onde a retenção morre
  título         — gancho fora do banco não alimenta o cooldown (a causa
                   medida da canibalização do Country Blues e Fé)
  originalidade  — imagens já saturadas no acervo, medidas pelo `quality`

Só se aplica a canal de canção. Em canal instrumental os critérios de letra
não têm sentido e o módulo diz isso em vez de devolver um número inventado.
"""

import re
import unicodedata

from . import quality

_SECAO = re.compile(r"^\s*\[([^\]]+)\]\s*$")

_TIPOS = {
    "intro": ("intro",),
    "verso": ("verse", "verso", "estrofe"),
    "refrao": ("chorus", "refrao", "refrão", "estribillo", "coro"),
    "ponte": ("bridge", "ponte", "puente"),
    "outro": ("outro", "final", "fade", "ending"),
}

MAX_PALAVRAS_REFRAO = 8   # acima disso o público não acompanha em coro
MAX_PALAVRAS_ABERTURA = 8  # o que cabe nos primeiros ~3 segundos

BANDAS = (
    (90, "🔥 alta probabilidade viral", "publicar com prioridade"),
    (75, "✅ bom potencial", "publicar normalmente"),
    (60, "⚠️ potencial médio", "revisar os critérios em falta"),
    (0, "❌ baixo potencial", "reescrever antes de publicar"),
)


def _norm(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def _tipo_secao(nome):
    n = _norm(nome)
    for tipo, chaves in _TIPOS.items():
        if any(_norm(c) in n for c in chaves):
            return tipo
    return "outra"


def parse_secoes(letra):
    """[(tipo, [linhas cantadas])] na ordem em que aparecem na letra."""
    secoes, atual = [], None
    for linha in letra.splitlines():
        m = _SECAO.match(linha)
        if m:
            atual = (_tipo_secao(m.group(1)), [])
            secoes.append(atual)
        elif linha.strip() and atual is not None:
            atual[1].append(linha.strip())
    return secoes


def _palavras(linha):
    return [p for p in re.findall(r"[a-zA-ZÀ-ÿ']+", linha) if p]


def _conteudo(linha, idioma=None):
    return {w for w in quality._content_words(linha, idioma)}


def _c_estrutura(secoes):
    presentes = {t for t, _ in secoes}
    faltando = [t for t in ("intro", "verso", "refrao", "ponte", "outro")
                if t not in presentes]
    pts = 20 - 4 * len(faltando)
    nota = "completa" if not faltando else f"faltando: {', '.join(faltando)}"
    return max(pts, 0), nota


def _c_refrao(secoes):
    refroes = [linhas for t, linhas in secoes if t == "refrao" and linhas]
    if not refroes:
        return 0, "sem seção de refrão"

    linhas = refroes[0]
    longas = [l for l in linhas if len(_palavras(l)) > MAX_PALAVRAS_REFRAO]
    pts_curto = 10 if not longas else max(0, 10 - 3 * len(longas))

    repetido = len(refroes) >= 2
    pts_rep = 10 if repetido else 0

    nota = []
    nota.append("linhas curtas" if not longas
                else f"{len(longas)} linha(s) acima de {MAX_PALAVRAS_REFRAO} palavras")
    nota.append(f"repetido {len(refroes)}x" if repetido else "refrão aparece uma vez só")
    return pts_curto + pts_rep, "; ".join(nota)


def _c_gancho(secoes, idioma=None):
    """Os primeiros segundos: entrada curta e já apontando para o refrão."""
    cantadas = [l for t, linhas in secoes for l in linhas]
    if not cantadas:
        return 0, "letra sem linhas cantadas"

    refroes = [linhas for t, linhas in secoes if t == "refrao" and linhas]
    ancora = _conteudo(refroes[0][0], idioma) if refroes else set()

    primeira = cantadas[0]
    pts_curta = 10 if len(_palavras(primeira)) <= MAX_PALAVRAS_ABERTURA else 0
    casou = any(_conteudo(l, idioma) & ancora for l in cantadas[:4]) if ancora else False
    pts_ancora = 10 if casou else 0

    nota = []
    nota.append("abertura curta" if pts_curta else
                f"abertura de {len(_palavras(primeira))} palavras — longa demais para 3s")
    nota.append("aponta para o refrão nas 4 primeiras linhas" if casou
                else "as 4 primeiras linhas não anunciam o refrão")
    return pts_curta + pts_ancora, "; ".join(nota)


def _c_titulo(conn, cfg, titulo):
    if not titulo:
        return 0, "título não informado"

    t = _norm(titulo)
    gancho = next((g for g in cfg.get("ganchos", []) if _norm(g) in t), None)
    beneficio = next((b for b in cfg.get("beneficios", []) if _norm(b) in t), None)

    pts = (10 if gancho else 0) + (5 if beneficio else 0)
    nota = []
    nota.append(f"gancho «{gancho}» do banco" if gancho
                else "gancho fora do banco — não alimenta o cooldown de gancho")
    nota.append("benefício presente" if beneficio else "sem benefício do banco")

    if gancho and conn is not None:
        livres = {_norm(h) for h in _hooks_livres(conn, cfg)}
        if _norm(gancho) in livres:
            pts += 5
            nota.append("fora do descanso")
        else:
            nota.append("⚠️ gancho ainda em descanso — foi usado há pouco")
    return pts, "; ".join(nota)


def _hooks_livres(conn, cfg):
    """Ganchos liberados hoje. Import tardio evita ciclo com `catalog`."""
    from . import catalog
    return catalog.pick_hook(conn, cfg["niche"], cfg.get("ganchos", []),
                             cooldown_days=cfg.get("cooldown_gancho_dias", 30))


def _c_originalidade(conn, cfg, letra):
    evitar = quality.avoid_list(conn, cfg["niche"],
                                protegidas=cfg.get("palavras_protegidas", ()),
                                idioma=cfg.get("idioma"))
    if evitar["n_musicas"] == 0:
        return 20, "acervo vazio — critério não avaliado"

    texto = {w for w in quality._content_words(letra, cfg.get("idioma"))}
    repetidas = [p for p in evitar["palavras"] if p in texto]
    pts = max(0, 20 - 4 * len(repetidas))
    if not repetidas:
        return pts, f"nenhuma imagem saturada do acervo ({evitar['n_musicas']} letras)"
    return pts, f"reusa imagem saturada: {', '.join(repetidas[:6])}"


def score(conn, cfg, letra, *, titulo=None):
    """Devolve total, banda e o detalhamento por critério."""
    if cfg.get("formato") == "instrumental":
        raise ValueError(
            f"{cfg['niche']} é canal instrumental: os critérios de letra não se "
            "aplicam. Avalie a direção sonora e a duração da faixa.")

    secoes = parse_secoes(letra)
    idioma = cfg.get("idioma")

    criterios = []
    for nome, (pts, nota) in (
        ("estrutura", _c_estrutura(secoes)),
        ("refrão", _c_refrao(secoes)),
        ("gancho em 3s", _c_gancho(secoes, idioma)),
        ("título", _c_titulo(conn, cfg, titulo)),
        ("originalidade", _c_originalidade(conn, cfg, letra)),
    ):
        criterios.append({"criterio": nome, "pontos": pts, "nota": nota})

    total = sum(c["pontos"] for c in criterios)
    banda, acao = next((b, a) for piso, b, a in BANDAS if total >= piso)
    return {"total": total, "banda": banda, "acao": acao, "criterios": criterios}


def format_report(conn, cfg, letra, *, titulo=None):
    r = score(conn, cfg, letra, titulo=titulo)
    L = [f"🎯 SCORE — {cfg['nome_exibicao']} — {r['total']}/100  {r['banda']}", ""]
    if titulo:
        L += [f"   título: {titulo}", ""]
    for c in r["criterios"]:
        marca = "✅" if c["pontos"] >= 16 else ("⚠️ " if c["pontos"] >= 10 else "❌")
        L.append(f"  {marca} {c['criterio']:<14} {c['pontos']:>2}/20  {c['nota']}")
    L += ["", f"→ {r['acao']}"]
    return "\n".join(L)
