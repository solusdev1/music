"""Integração VIDIQ → radar de ideias e oportunidade.

O MCP do VIDIQ não é chamado daqui: quem consulta é o agente, que passa o
JSON bruto para estas funções normalizarem e gravarem. Isso mantém o módulo
testável sem rede e sem gastar crédito.

Orçamento: cada consulta custa 5 créditos. Por isso a coleta é semanal e vai
para cache — a pauta diária lê só o banco.
"""

from datetime import datetime, timezone

from . import opportunity

CUSTO_POR_CONSULTA = 5

SCHEMA = """
CREATE TABLE IF NOT EXISTS vidiq_keywords (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    niche         TEXT NOT NULL,
    keyword       TEXT NOT NULL,
    volume        REAL,
    competition   REAL,
    overall       REAL,
    buscas_mes    INTEGER,
    buscas_pais   INTEGER,
    pais          TEXT,
    coletado_em   TEXT NOT NULL,
    UNIQUE(niche, keyword, pais)
);
"""


def init(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def _agora():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def ingest_keywords(conn, niche, payload, *, pais=None):
    """Grava o resultado de `vidiq_keyword_research`.

    Aceita o JSON do MCP como veio: seedKeyword + relatedKeywords.
    """
    init(conn)
    pais = pais or payload.get("country")
    linhas = []
    seed = payload.get("seedKeyword")
    if seed:
        linhas.append(seed)
    linhas.extend(payload.get("relatedKeywords") or [])

    gravadas = 0
    for k in linhas:
        kw = k.get("keyword")
        if not kw:
            continue
        conn.execute(
            """INSERT INTO vidiq_keywords (niche, keyword, volume, competition,
                   overall, buscas_mes, buscas_pais, pais, coletado_em)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(niche, keyword, pais) DO UPDATE SET
                   volume=excluded.volume, competition=excluded.competition,
                   overall=excluded.overall, buscas_mes=excluded.buscas_mes,
                   buscas_pais=excluded.buscas_pais, coletado_em=excluded.coletado_em""",
            (niche, kw, k.get("volume"), k.get("competition"), k.get("overall"),
             k.get("estimatedMonthlySearch"), k.get("countryVolume"), pais, _agora()),
        )
        gravadas += 1
    conn.commit()
    return gravadas


def ingest_outliers(conn, niche, payload, *, min_breakout=5.0):
    """Transforma vídeos em alta em ideias de música.

    Guarda o título como ideia bruta — quem decide se vira tema é o operador,
    via `radar-approve`. O sistema não inventa tema sozinho.
    """
    ideias = 0
    for v in payload.get("videos") or []:
        if (v.get("breakoutScore") or 0) < min_breakout:
            continue
        titulo = (v.get("videoTitle") or "").strip()
        if not titulo:
            continue
        opportunity.add_ideia(
            conn, niche, titulo,
            origem=f"outlier·{v.get('channelTitle','?')}·{v.get('subscriberCount',0)}subs",
            score=v.get("breakoutScore"),
        )
        ideias += 1
    return ideias


def oportunidades(conn, niche, *, max_competition=30, min_buscas=3000, limite=15):
    """Keywords de alta demanda e baixa concorrência — onde há espaço."""
    init(conn)
    return conn.execute(
        """SELECT keyword, overall, competition, buscas_mes, buscas_pais
           FROM vidiq_keywords
           WHERE niche=? AND competition IS NOT NULL AND competition <= ?
             AND COALESCE(buscas_mes,0) >= ?
           ORDER BY overall DESC LIMIT ?""",
        (niche, max_competition, min_buscas, limite),
    ).fetchall()


def format_report(conn, niche):
    init(conn)
    tot = conn.execute(
        "SELECT COUNT(*) c, MAX(coletado_em) u FROM vidiq_keywords WHERE niche=?", (niche,)
    ).fetchone()
    L = [f"🔎 VIDIQ — {niche}", ""]
    if not tot or tot["c"] == 0:
        L.append("  Nenhuma coleta. Rode a pesquisa de keyword e ingira o resultado.")
        return "\n".join(L)

    L.append(f"  {tot['c']} keyword(s) em cache · última coleta {tot['u'][:10]}")
    L += ["", "  ESPAÇO ABERTO (concorrência ≤30 e ≥3k buscas/mês)",
          f"  {'score':>6} {'conc':>5} {'buscas/mês':>11}  keyword", "  " + "-" * 60]
    linhas = oportunidades(conn, niche)
    if not linhas:
        L.append("  nenhuma keyword com esse perfil no cache")
    for r in linhas:
        L.append(f"  {r['overall'] or 0:>6.1f} {r['competition']:>5.1f} "
                 f"{r['buscas_mes'] or 0:>11,}  {r['keyword']}")

    L += ["", "  MAIOR VOLUME (independente de concorrência)",
          f"  {'score':>6} {'conc':>5} {'buscas/mês':>11}  keyword", "  " + "-" * 60]
    for r in conn.execute(
        """SELECT keyword, overall, competition, buscas_mes FROM vidiq_keywords
           WHERE niche=? ORDER BY COALESCE(buscas_mes,0) DESC LIMIT 8""", (niche,)):
        L.append(f"  {r['overall'] or 0:>6.1f} {r['competition'] or 0:>5.1f} "
                 f"{r['buscas_mes'] or 0:>11,}  {r['keyword']}")
    return "\n".join(L)
