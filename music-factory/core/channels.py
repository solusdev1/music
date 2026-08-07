"""Busca de canais e detecção do que está COMEÇANDO a viralizar.

Dois problemas que o radar antigo não resolvia:

1. **Canal não era entidade.** O radar guardava vídeos; o nome do canal era só
   um campo de texto. Não dava para perguntar "quem são os canais pequenos
   deste nicho" nem "esse canal já apareceu antes".

2. **O score premiava o que JÁ estourou.** Ordenar por views/dia coloca no topo
   o vídeo de 4M de views de um canal de 3M de inscritos — que é justamente o
   que NÃO dá para replicar. O que interessa é o oposto: vídeo novo, de canal
   pequeno, com views muito acima do que aquele canal costuma fazer.

O sinal aqui é o **multiplicador** (views ÷ inscritos) com peso de recência e
de porte. Um canal de 2k inscritos com 60k views em 5 dias é um formato
copiável. Um canal de 3M com 4M views é uma gravadora.

Nada aqui chama rede. O agente busca (MCP VIDIQ, radar do youtube_music_ops)
e entrega o JSON; estas funções normalizam, pontuam e gravam.
"""

import math
import re
import unicodedata
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS channels (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    niche           TEXT NOT NULL,
    chave           TEXT NOT NULL,
    chave_nome      TEXT NOT NULL,
    nome            TEXT NOT NULL,
    channel_id      TEXT,
    handle          TEXT,
    subs            INTEGER,
    total_views     INTEGER,
    videos          INTEGER,
    pais            TEXT,
    subs_growth_30d REAL,
    views_growth_30d REAL,
    origem          TEXT,
    vezes_visto     INTEGER NOT NULL DEFAULT 1,
    primeiro_visto  TEXT NOT NULL,
    ultimo_visto    TEXT NOT NULL,
    UNIQUE(niche, chave)
);

CREATE TABLE IF NOT EXISTS breakouts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    niche         TEXT NOT NULL,
    chave         TEXT NOT NULL,
    titulo        TEXT NOT NULL,
    video_id      TEXT,
    url           TEXT,
    canal         TEXT,
    canal_subs    INTEGER,
    views         INTEGER,
    idade_dias    REAL,
    duracao_sec   INTEGER,
    multiplicador REAL,
    velocidade    REAL,
    score         REAL NOT NULL,
    motivo        TEXT,
    origem        TEXT,
    coletado_em   TEXT NOT NULL,
    UNIQUE(niche, chave)
);

CREATE INDEX IF NOT EXISTS idx_channels_niche  ON channels(niche, subs);
CREATE INDEX IF NOT EXISTS idx_breakouts_niche ON breakouts(niche, score);
"""

# ─── parâmetros do score ──────────────────────────────────────────────────
# "Começando" tem prazo de validade: passou de 90 dias o formato já não é novo.
JANELA_QUENTE_DIAS = 14      # peso de recência cheio
JANELA_MAX_DIAS = 90         # além disso, não conta como breakout

# Canal minúsculo distorce o multiplicador (100 inscritos, 10k views = 100x).
# O piso evita que ruído de canal recém-criado domine o ranking.
PISO_SUBS = 500

TETO_SUBS_REPLICAVEL = 100_000   # acima disso, copiar o formato não basta

# Referências de nota cheia em cada eixo.
MULT_NOTA_CHEIA = 10.0       # 10x os inscritos
VEL_NOTA_CHEIA = 5_000.0     # 5k views/dia
VIEWS_NOTA_CHEIA = 50_000.0


def init(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def _agora():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _chave(*partes):
    """Chave estável para dedupe: sem acento, sem pontuação, minúscula."""
    bruto = " ".join(str(p) for p in partes if p).strip().lower()
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", bruto)
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", "-", sem_acento).strip("-")


def _int(v):
    """Aceita 12345, '12.345', '12,345', '1.2K', '3.4M', '1,2 mi' → int ou None."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    if v is None:
        return None
    s = str(v).strip().lower()
    if not s:
        return None
    mult = 1
    if re.search(r"\d\s*b\b|bilh|billion", s):
        mult = 1_000_000_000
    elif re.search(r"\d\s*m\b|milh|million|\bmi\b", s):
        mult = 1_000_000
    elif re.search(r"\d\s*k\b|\bmil\b|thousand", s):
        mult = 1_000
    m = re.search(r"\d[\d.,]*", s)
    if not m:
        return None
    num = m.group(0).rstrip(".,")
    if mult == 1:
        # sem sufixo, ponto/vírgula só pode ser separador de milhar
        return int(re.sub(r"[.,]", "", num))
    # com sufixo, o separador restante é decimal ("1.2K", "1,2 mi")
    return int(float(re.sub(r"[.,](?=\d{3}\b)", "", num).replace(",", ".")) * mult)


def _idade_dias(v):
    """Idade em dias a partir de idade, epoch (s ou ms) ou data ISO.

    O VIDIQ devolve `videoPublishedAt` como epoch em segundos, não idade. Sem
    converter, a recência fica neutra para todo mundo e o radar perde
    justamente o eixo que separa "começando" de "já aconteceu".
    """
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        if not re.fullmatch(r"-?\d+(\.\d+)?", s):
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            except ValueError:
                return None
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max((datetime.now(timezone.utc) - dt).total_seconds() / 86400, 0.0)
        v = float(s)
    v = float(v)
    if v < 0:
        return None
    if v > 1e11:        # epoch em milissegundos
        v /= 1000.0
    if v > 1e8:         # epoch em segundos (≈1973 em diante)
        agora = datetime.now(timezone.utc).timestamp()
        return max((agora - v) / 86400, 0.0)
    return v            # já veio em dias


# ═══════════════════════════════════════════════════════════════════════════
# CANAIS
# ═══════════════════════════════════════════════════════════════════════════

def porte(subs):
    """Classificação de porte — decide se dá para disputar com o canal."""
    if subs is None:
        return "desconhecido"
    if subs < 1_000:
        return "semente"
    if subs < 10_000:
        return "pequeno"
    if subs < 100_000:
        return "medio"
    if subs < 1_000_000:
        return "grande"
    return "gigante"


def peso_porte(subs):
    """Canal pequeno = formato copiável. Gigante = tem catálogo, verba e marca."""
    p = porte(subs)
    return {"semente": 1.0, "pequeno": 1.0, "medio": 0.8,
            "grande": 0.4, "gigante": 0.15, "desconhecido": 0.5}[p]


def _achar_channel(conn, niche, channel_id, handle, chave_nome):
    """Resolve a identidade do canal antes de gravar.

    O mesmo canal chega de fontes diferentes com chaves diferentes: a busca de
    canais traz `channelId`, o breakout traz só o nome que aparece no vídeo.
    Sem reconciliar, cada fonte cria uma linha e o mapa do nicho vira uma lista
    de duplicatas. Procura por ID, depois handle, depois nome normalizado.
    """
    for campo, valor in (("channel_id", channel_id), ("handle", handle),
                         ("chave_nome", chave_nome)):
        if not valor:
            continue
        row = conn.execute(
            f"SELECT * FROM channels WHERE niche=? AND {campo}=?", (niche, valor)
        ).fetchone()
        if row:
            return row
    return None


def save_channel(conn, niche, nome, *, channel_id=None, handle=None, subs=None,
                 total_views=None, videos=None, pais=None, subs_growth_30d=None,
                 views_growth_30d=None, origem="radar"):
    """Registra/atualiza um canal do nicho (idempotente).

    Reencontrar o mesmo canal incrementa `vezes_visto` — recorrência entre
    coletas é sinal de que ele é estrutural no nicho, não um acaso da busca.
    """
    init(conn)
    nome = (nome or "").strip()
    if not nome and not channel_id:
        return None
    chave_nome = _chave(nome) or _chave(channel_id)
    agora = _agora()

    existente = _achar_channel(conn, niche, channel_id, handle, chave_nome)
    if existente:
        conn.execute(
            """UPDATE channels SET
                   nome=COALESCE(NULLIF(?,''), nome),
                   channel_id=COALESCE(channel_id, ?),
                   handle=COALESCE(handle, ?),
                   subs=COALESCE(?, subs),
                   total_views=COALESCE(?, total_views),
                   videos=COALESCE(?, videos),
                   pais=COALESCE(?, pais),
                   subs_growth_30d=COALESCE(?, subs_growth_30d),
                   views_growth_30d=COALESCE(?, views_growth_30d),
                   vezes_visto=vezes_visto + 1,
                   ultimo_visto=?
               WHERE id=?""",
            (nome, channel_id, handle, _int(subs), _int(total_views), _int(videos),
             pais, subs_growth_30d, views_growth_30d, agora, existente["id"]),
        )
        conn.commit()
        return existente["chave"]

    chave = _chave(channel_id or handle or nome)
    conn.execute(
        """INSERT INTO channels (niche, chave, chave_nome, nome, channel_id, handle,
               subs, total_views, videos, pais, subs_growth_30d, views_growth_30d,
               origem, primeiro_visto, ultimo_visto)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(niche, chave) DO UPDATE SET
               vezes_visto=channels.vezes_visto + 1,
               ultimo_visto=excluded.ultimo_visto""",
        (niche, chave, chave_nome, nome, channel_id, handle, _int(subs),
         _int(total_views), _int(videos), pais, subs_growth_30d, views_growth_30d,
         origem, agora, agora),
    )
    conn.commit()
    return chave


def ingest_channels(conn, niche, payload, *, origem="vidiq"):
    """Ingere `vidiq_channel_search`, `vidiq_similar_channels` ou lista crua.

    Aceita as três formas em que esses payloads costumam chegar: {"channels":
    [...]}, {"results": [...]} ou a lista direta.
    """
    if isinstance(payload, list):
        itens = payload
    else:
        itens = (payload.get("channels") or payload.get("results")
                 or payload.get("items") or [])
    n = 0
    for c in itens:
        if not isinstance(c, dict):
            continue
        nome = (c.get("channelTitle") or c.get("title") or c.get("name")
                or c.get("channel") or "")
        cid = c.get("channelId") or c.get("id") or c.get("channel_id")
        if not nome and not cid:
            continue
        save_channel(
            conn, niche, nome,
            channel_id=cid,
            handle=c.get("channelHandle") or c.get("handle") or c.get("customUrl"),
            subs=c.get("subscriberCount") or c.get("subscribers") or c.get("subs"),
            total_views=c.get("viewCount") or c.get("totalViews"),
            videos=c.get("videoCount") or c.get("videos"),
            pais=c.get("country") or c.get("pais"),
            subs_growth_30d=c.get("subsGrowth30d"),
            views_growth_30d=c.get("viewsGrowth30d"),
            origem=origem,
        )
        n += 1
    return n


def listar_channels(conn, niche, *, max_subs=None, limite=30):
    init(conn)
    sql = "SELECT * FROM channels WHERE niche=?"
    args = [niche]
    if max_subs is not None:
        sql += " AND subs IS NOT NULL AND subs <= ?"
        args.append(max_subs)
    sql += " ORDER BY vezes_visto DESC, COALESCE(subs, 1e12) ASC LIMIT ?"
    args.append(limite)
    return conn.execute(sql, args).fetchall()


def concorrentes_replicaveis(conn, niche, *, limite=15):
    """Canais pequenos o bastante para servirem de modelo direto."""
    return listar_channels(conn, niche, max_subs=TETO_SUBS_REPLICAVEL, limite=limite)


def format_channels_report(conn, niche):
    init(conn)
    tot = conn.execute(
        "SELECT COUNT(*) c, MAX(ultimo_visto) u FROM channels WHERE niche=?", (niche,)
    ).fetchone()
    L = [f"📺 CANAIS — {niche}", ""]
    if not tot or tot["c"] == 0:
        L += ["  Nenhum canal mapeado.",
              f"  Colete com: cli.py channels-ingest --niche {niche} --file <json>",
              "  (JSON de vidiq_channel_search / vidiq_similar_channels)"]
        return "\n".join(L)

    L.append(f"  {tot['c']} canal(is) mapeado(s) · última coleta {tot['u'][:10]}")

    dist = conn.execute("SELECT subs FROM channels WHERE niche=?", (niche,)).fetchall()
    contagem = {}
    for r in dist:
        contagem[porte(r["subs"])] = contagem.get(porte(r["subs"]), 0) + 1
    ordem = ["semente", "pequeno", "medio", "grande", "gigante", "desconhecido"]
    L.append("  Porte: " + " · ".join(
        f"{p}={contagem[p]}" for p in ordem if p in contagem))

    L += ["", f"  REPLICÁVEIS (≤{TETO_SUBS_REPLICAVEL:,} inscritos)".replace(",", "."),
          f"  {'inscritos':>10} {'+subs30d':>9} {'vezes':>6}  canal", "  " + "-" * 66]
    linhas = concorrentes_replicaveis(conn, niche)
    if not linhas:
        L.append("  nenhum canal pequeno no mapa — o nicho pode estar dominado")
    for r in linhas:
        subs = f"{r['subs']:,}".replace(",", ".") if r["subs"] is not None else "—"
        cres = f"{r['subs_growth_30d']:+.0f}%" if r["subs_growth_30d"] is not None else "—"
        L.append(f"  {subs:>10} {cres:>9} {r['vezes_visto']:>6}  {r['nome'][:40]}")

    # crescimento de inscritos em 30d é o sinal de "começando" no nível do canal
    subindo = conn.execute(
        """SELECT nome, subs, subs_growth_30d FROM channels
           WHERE niche=? AND subs_growth_30d IS NOT NULL AND subs <= ?
           ORDER BY subs_growth_30d DESC LIMIT 8""",
        (niche, TETO_SUBS_REPLICAVEL),
    ).fetchall()
    if subindo:
        L += ["", "  SUBINDO MAIS RÁPIDO (crescimento de inscritos em 30 dias)",
              f"  {'+subs30d':>9} {'inscritos':>10}  canal", "  " + "-" * 66]
        for r in subindo:
            subs = f"{r['subs']:,}".replace(",", ".") if r["subs"] is not None else "—"
            L.append(f"  {r['subs_growth_30d']:>8.0f}% {subs:>10}  {r['nome'][:40]}")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# BREAKOUT — o que está COMEÇANDO a viralizar
# ═══════════════════════════════════════════════════════════════════════════

def peso_recencia(idade_dias):
    """1.0 nos primeiros 14 dias, decaindo até zerar aos 90."""
    if idade_dias is None:
        return 0.5          # sem data: não premia nem descarta
    if idade_dias <= JANELA_QUENTE_DIAS:
        return 1.0
    if idade_dias >= JANELA_MAX_DIAS:
        return 0.0
    return (JANELA_MAX_DIAS - idade_dias) / (JANELA_MAX_DIAS - JANELA_QUENTE_DIAS)


def _satura(x, referencia):
    """Curva 0→1 que cresce rápido e desacelera, sem nunca travar em 1.

    Um teto duro (`min(x/ref, 1)`) empata todos os candidatos fortes na nota
    máxima e perde justamente a ordem que interessa no topo. Aqui um sinal
    duas vezes maior continua pontuando mais, só que cada vez menos.
    """
    if not x or x <= 0:
        return 0.0
    return 1.0 - math.exp(-x / referencia)


def score_breakout(views, subs, idade_dias):
    """Nota 0-100 de "vale a pena replicar este formato".

    Três eixos somando ~100 no melhor caso, multiplicados por recência e porte:
      - 45 pts multiplicador (views ÷ inscritos) — o eixo que importa
      - 35 pts velocidade (views/dia)
      - 20 pts volume absoluto (evita premiar 3k views num canal de 300)
    """
    views = _int(views)
    subs = _int(subs)
    if not views or views <= 0:
        return {"score": 0.0, "multiplicador": None, "velocidade": None,
                "motivo": "sem contagem de views"}

    idade = max(float(idade_dias), 0.5) if idade_dias is not None else None
    mult = views / max(subs or 0, PISO_SUBS)
    vel = views / idade if idade else None

    c_mult = 45 * _satura(mult, MULT_NOTA_CHEIA)
    c_vel = 35 * _satura(vel, VEL_NOTA_CHEIA)
    c_vol = 20 * _satura(views, VIEWS_NOTA_CHEIA)
    score = (c_mult + c_vel + c_vol) * peso_recencia(idade) * peso_porte(subs)

    # sem inscritos o multiplicador usa o piso, então não é um "x" real
    partes = [f"{mult:.1f}x inscritos" if subs else "inscritos desconhecidos"]
    if vel:
        partes.append(f"{vel:,.0f} views/dia".replace(",", "."))
    if idade is not None:
        partes.append(f"{idade:.0f}d")
    partes.append(porte(subs))
    return {"score": round(score, 1),
            "multiplicador": round(mult, 2) if subs else None,
            "velocidade": round(vel, 1) if vel else None,
            "motivo": " · ".join(partes)}


def save_breakout(conn, niche, titulo, *, views=None, canal=None, canal_subs=None,
                  idade_dias=None, video_id=None, url=None, duracao_sec=None,
                  origem="radar"):
    """Grava um vídeo candidato a breakout, já pontuado."""
    init(conn)
    titulo = (titulo or "").strip()
    if not titulo:
        return None
    idade_dias = _idade_dias(idade_dias)
    s = score_breakout(views, canal_subs, idade_dias)
    chave = _chave(video_id or f"{titulo}|{canal or ''}")
    conn.execute(
        """INSERT INTO breakouts (niche, chave, titulo, video_id, url, canal,
               canal_subs, views, idade_dias, duracao_sec, multiplicador,
               velocidade, score, motivo, origem, coletado_em)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(niche, chave) DO UPDATE SET
               views=COALESCE(excluded.views, breakouts.views),
               canal_subs=COALESCE(excluded.canal_subs, breakouts.canal_subs),
               idade_dias=COALESCE(excluded.idade_dias, breakouts.idade_dias),
               multiplicador=excluded.multiplicador, velocidade=excluded.velocidade,
               score=excluded.score, motivo=excluded.motivo,
               coletado_em=excluded.coletado_em""",
        (niche, chave, titulo, video_id, url, canal, _int(canal_subs), _int(views),
         idade_dias, _int(duracao_sec), s["multiplicador"], s["velocidade"],
         s["score"], s["motivo"], origem, _agora()),
    )
    if canal:
        save_channel(conn, niche, canal, subs=canal_subs, origem=f"breakout·{origem}")
    conn.commit()
    return s


def ingest_outliers(conn, niche, payload, *, origem="vidiq-outliers"):
    """Ingere `vidiq_outliers` / `vidiq_trending_videos` e pontua cada vídeo.

    Diferente da versão antiga (que só jogava o título numa lista de ideias),
    aqui cada vídeo é pontuado por replicabilidade e o canal é mapeado junto.
    """
    itens = payload if isinstance(payload, list) else (
        payload.get("videos") or payload.get("results") or payload.get("items") or [])
    n = 0
    for v in itens:
        if not isinstance(v, dict):
            continue
        titulo = (v.get("videoTitle") or v.get("title") or "").strip()
        if not titulo:
            continue
        save_breakout(
            conn, niche, titulo,
            views=v.get("viewCount") or v.get("views"),
            canal=v.get("channelTitle") or v.get("channel"),
            canal_subs=v.get("subscriberCount") or v.get("channelSubscribers"),
            idade_dias=(v.get("ageDays") or v.get("age_days_est")
                        or v.get("daysSincePublished")
                        or v.get("videoPublishedAt") or v.get("publishedAt")),
            video_id=v.get("videoId") or v.get("id"),
            url=v.get("url") or v.get("videoUrl"),
            duracao_sec=v.get("duration") or v.get("durationSeconds"),
            origem=origem,
        )
        n += 1
    return n


def listar_breakouts(conn, niche, *, score_min=0.0, limite=15):
    init(conn)
    return conn.execute(
        """SELECT * FROM breakouts WHERE niche=? AND score >= ?
           ORDER BY score DESC LIMIT ?""",
        (niche, score_min, limite),
    ).fetchall()


# Palavras que aparecem em qualquer título do nicho e não ensinam nada.
_STOP = set("""para por com sem uma que voce você deus dios your you the and for with from
into music musica música mix hora horas hour hours playlist completa full best top new
nova novo 2025 2026 canciones songs song alabanzas louvores""".split())


def padroes_de_titulo(conn, niche, *, limite=12, score_min=20.0):
    """Palavras recorrentes entre os breakouts — a embalagem a copiar.

    Só olha os títulos que passaram do corte: copiar o vocabulário de vídeo
    que não estourou não serve de nada.
    """
    linhas = listar_breakouts(conn, niche, score_min=score_min, limite=60)
    freq = {}
    for r in linhas:
        vistas_neste = set()
        for w in re.findall(r"[\wÀ-ÿ]{4,}", (r["titulo"] or "").lower()):
            if w in _STOP or w.isdigit() or w in vistas_neste:
                continue
            vistas_neste.add(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(
        ((w, c) for w, c in freq.items() if c >= 2),
        key=lambda x: (-x[1], x[0]),
    )[:limite]


def format_breakout_report(conn, niche):
    init(conn)
    tot = conn.execute(
        "SELECT COUNT(*) c, MAX(coletado_em) u FROM breakouts WHERE niche=?", (niche,)
    ).fetchone()
    L = [f"🚀 COMEÇANDO A VIRALIZAR — {niche}", ""]
    if not tot or tot["c"] == 0:
        L += ["  Nenhum candidato coletado.",
              f"  Colete com: cli.py breakout-ingest --niche {niche} --file <json>",
              "  (JSON de vidiq_outliers / vidiq_trending_videos)"]
        return "\n".join(L)

    L.append(f"  {tot['c']} vídeo(s) avaliado(s) · última coleta {tot['u'][:10]}")
    L += ["",
          "  Score = multiplicador (views÷inscritos) + velocidade + volume,",
          f"  com peso de recência (cheio até {JANELA_QUENTE_DIAS}d, zero após "
          f"{JANELA_MAX_DIAS}d) e de porte do canal.",
          "", f"  {'score':>5} {'mult':>6} {'views':>10}  título / canal",
          "  " + "-" * 72]

    linhas = listar_breakouts(conn, niche, score_min=1.0)
    if not linhas:
        L.append("  nenhum vídeo passou do corte — nada começando a viralizar agora")
    for r in linhas:
        views = f"{r['views']:,}".replace(",", ".") if r["views"] else "—"
        mult = f"{r['multiplicador']:.1f}x" if r["multiplicador"] else "—"
        L.append(f"  {r['score']:>5.0f} {mult:>6} {views:>10}  {r['titulo'][:52]}")
        L.append(f"  {'':>23}  ↳ {r['canal'] or '?'} · {r['motivo'] or ''}")

    pad = padroes_de_titulo(conn, niche)
    if pad:
        L += ["", "  EMBALAGEM A COPIAR (palavras recorrentes nos que estouraram)",
              "  " + ", ".join(f"{w} ({c}x)" for w, c in pad)]
    return "\n".join(L)
