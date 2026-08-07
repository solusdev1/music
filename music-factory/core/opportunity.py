"""Oportunidade: escolher o tema do dia por demanda real, não por rodízio.

Restrição de projeto — a conta VIDIQ tem teto de 150 créditos/semana e cada
consulta custa 5. São ~30 consultas por semana no total. Um job diário que
consultasse a API queimaria a cota em dois dias.

Por isso: a coleta é SEMANAL e vai para cache; a pauta diária lê só o cache
e nunca gasta crédito. Sem cache válido, o sistema cai no rodízio simples
e diz isso em voz alta, em vez de fingir que tem dado.
"""

from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS keyword_cache (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    niche        TEXT NOT NULL,
    keyword      TEXT NOT NULL,
    volume       INTEGER,
    competition  INTEGER,
    score        INTEGER,
    country      TEXT,
    collected_at TEXT NOT NULL,
    UNIQUE(niche, keyword, country)
);

CREATE TABLE IF NOT EXISTS theme_opportunity (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    niche        TEXT NOT NULL,
    theme        TEXT NOT NULL,
    keyword      TEXT,
    score        REAL NOT NULL,
    fonte        TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    UNIQUE(niche, theme)
);
"""

CACHE_VALIDO_DIAS = 14


def init(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def save_keyword(conn, niche, keyword, *, volume=None, competition=None,
                 score=None, country=None):
    """Grava resultado de pesquisa de keyword no cache (idempotente)."""
    init(conn)
    conn.execute(
        """INSERT INTO keyword_cache (niche, keyword, volume, competition, score,
               country, collected_at)
           VALUES (?,?,?,?,?,?,?)
           ON CONFLICT(niche, keyword, country) DO UPDATE SET
               volume=excluded.volume, competition=excluded.competition,
               score=excluded.score, collected_at=excluded.collected_at""",
        (niche, keyword, volume, competition, score, country,
         datetime.now(timezone.utc).isoformat(timespec="microseconds")),
    )
    conn.commit()


def save_theme_score(conn, niche, theme, score, *, keyword=None, fonte="vidiq"):
    init(conn)
    conn.execute(
        """INSERT INTO theme_opportunity (niche, theme, keyword, score, fonte, collected_at)
           VALUES (?,?,?,?,?,?)
           ON CONFLICT(niche, theme) DO UPDATE SET
               score=excluded.score, keyword=excluded.keyword,
               fonte=excluded.fonte, collected_at=excluded.collected_at""",
        (niche, theme, keyword, float(score), fonte,
         datetime.now(timezone.utc).isoformat(timespec="microseconds")),
    )
    conn.commit()


def cache_status(conn, niche):
    """Idade e tamanho do cache. É o que decide se dá para usar oportunidade."""
    init(conn)
    row = conn.execute(
        "SELECT COUNT(*) n, MAX(collected_at) ultimo FROM theme_opportunity WHERE niche=?",
        (niche,),
    ).fetchone()
    if not row or row["n"] == 0:
        return {"valido": False, "n": 0, "idade_dias": None,
                "motivo": "nenhuma coleta de oportunidade registrada"}

    ultimo = datetime.fromisoformat(row["ultimo"])
    idade = (datetime.now(timezone.utc) - ultimo).days
    if idade > CACHE_VALIDO_DIAS:
        return {"valido": False, "n": row["n"], "idade_dias": idade,
                "motivo": f"cache com {idade} dias (limite {CACHE_VALIDO_DIAS})"}
    return {"valido": True, "n": row["n"], "idade_dias": idade, "motivo": None}


def rank_themes(conn, niche, theme_bank):
    """Ordena o banco de temas por score de oportunidade.

    Só reordena temas que TÊM score coletado; os demais mantêm a ordem
    original do config, no fim da fila. Nunca inventa score.
    """
    init(conn)
    scores = {
        r["theme"]: r["score"]
        for r in conn.execute(
            "SELECT theme, score FROM theme_opportunity WHERE niche=?", (niche,)
        )
    }
    com_score = [t for t in theme_bank if t in scores]
    sem_score = [t for t in theme_bank if t not in scores]
    com_score.sort(key=lambda t: scores[t], reverse=True)
    return com_score + sem_score, scores


def pick_theme_by_opportunity(conn, niche, theme_bank, *, cooldown_days=60,
                              grupo_niches=None, cooldown_grupo_days=14):
    """Tema do dia = maior oportunidade FORA do período de descanso.

    Combina os dois eixos: demanda (score) e anti-repetição (cooldown).
    Sem cache válido, devolve None para o chamador cair no rodízio simples.
    """
    from . import catalog  # import tardio evita ciclo

    st = cache_status(conn, niche)
    if not st["valido"]:
        return None, st["motivo"]

    ranked, scores = rank_themes(conn, niche, theme_bank)
    livres = set(catalog.theme_filter(
        conn, niche, theme_bank, cooldown_days=cooldown_days,
        grupo_niches=grupo_niches, cooldown_grupo_days=cooldown_grupo_days))
    for t in ranked:
        if t in livres:
            return t, (f"score {scores[t]:.0f} (coleta de {st['idade_dias']}d atrás)"
                       if t in scores else "sem score; ordem do config")
    return None, "todos os temas com oportunidade estão em período de descanso"


def format_report(conn, niche, theme_bank):
    st = cache_status(conn, niche)
    L = [f"📈 OPORTUNIDADE — {niche}", ""]
    if not st["valido"]:
        L += [f"  ⚠️  Cache indisponível: {st['motivo']}",
              "",
              "  A pauta diária segue funcionando por rodízio simples de temas.",
              "  Para coletar (consome créditos VIDIQ, rode SEMANALMENTE):",
              "      1. Peça ao agente para consultar o MCP VIDIQ (vidiq_keyword_research)",
              f"      2. python3 cli.py vidiq-ingest --niche {niche} --file <json> --tipo keywords",
              f"      3. python3 cli.py set-theme-score --niche {niche} --theme \"...\" --score N"]
        return "\n".join(L)

    ranked, scores = rank_themes(conn, niche, theme_bank)
    L.append(f"  Cache: {st['n']} tema(s) pontuado(s), coletado há {st['idade_dias']} dia(s)")
    L.append("")
    for t in ranked[:15]:
        s = scores.get(t)
        L.append(f"  {s:>5.0f}  {t}" if s is not None else f"      —  {t}")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# RADAR — ideias novas de música
#
# O radar não serve para ranquear o que já existe: serve para DESCOBRIR tema
# que ainda não está no banco. É a única coisa além da criação que precisa
# rodar continuamente, porque o banco de temas se esgota com 5 músicas/dia.
# ═══════════════════════════════════════════════════════════════════════════

SCHEMA_IDEIAS = """
CREATE TABLE IF NOT EXISTS ideias (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    niche        TEXT NOT NULL,
    ideia        TEXT NOT NULL,
    origem       TEXT,
    score        REAL,
    status       TEXT DEFAULT 'nova',
    descoberta_em TEXT NOT NULL,
    UNIQUE(niche, ideia)
);
"""


def init_ideias(conn):
    conn.executescript(SCHEMA_IDEIAS)
    conn.commit()


def add_ideia(conn, niche, ideia, *, origem="radar", score=None):
    """Registra tema descoberto pelo radar, ainda fora do banco do nicho."""
    init_ideias(conn)
    conn.execute(
        """INSERT INTO ideias (niche, ideia, origem, score, descoberta_em)
           VALUES (?,?,?,?,?)
           ON CONFLICT(niche, ideia) DO UPDATE SET
               score=COALESCE(excluded.score, ideias.score), origem=excluded.origem""",
        (niche, ideia, origem, score,
         datetime.now(timezone.utc).isoformat(timespec="microseconds")),
    )
    conn.commit()


def listar_ideias(conn, niche, *, status="nova"):
    init_ideias(conn)
    return conn.execute(
        "SELECT * FROM ideias WHERE niche=? AND status=? ORDER BY COALESCE(score,0) DESC",
        (niche, status),
    ).fetchall()


def aprovar_ideia(conn, niche, ideia):
    """Marca a ideia como aprovada — daí ela entra no `temas` do config."""
    init_ideias(conn)
    cur = conn.execute(
        "UPDATE ideias SET status='aprovada' WHERE niche=? AND ideia=?", (niche, ideia))
    conn.commit()
    if cur.rowcount == 0:
        raise LookupError(f"ideia não encontrada em {niche!r}: {ideia!r}")


def radar_report(conn, niche, temas_atuais, *, completo=True):
    """Radar do nicho em quatro blocos.

    Ordem intencional — do que é acionável hoje para o que é contexto:
      1. saúde do banco de temas (se esgotar, a pauta diária quebra)
      2. o que está começando a viralizar (formato a copiar)
      3. canais replicáveis (quem já provou o formato no tamanho certo)
      4. ideias soltas aguardando aprovação

    `completo=False` corta os blocos 2 e 3 — útil quando o chamador só quer
    a fila de ideias sem tocar nas tabelas de canais.
    """
    from . import channels  # import tardio evita ciclo

    init_ideias(conn)
    novas = listar_ideias(conn, niche)
    L = [f"🛰️  RADAR — {niche}", "",
         f"  banco atual: {len(temas_atuais)} tema(s)"]
    # com 5 músicas/dia e descanso de 60d, o banco precisa cobrir a janela
    minimo = 30
    if len(temas_atuais) < minimo:
        L.append(f"  ⚠️  abaixo de {minimo}: o rodízio esgota e passa a reaproveitar tema antigo")

    if completo:
        L += ["", channels.format_breakout_report(conn, niche),
              "", channels.format_channels_report(conn, niche)]

    L += ["", f"💡 IDEIAS PENDENTES — {niche}", ""]
    if not novas:
        L += ["  Nenhuma ideia nova pendente.",
              f"  Registre com: cli.py radar-add --niche {niche} --ideia \"...\""]
    else:
        L.append(f"  {len(novas)} ideia(s) aguardando aprovação:")
        for r in novas:
            sc = f"{r['score']:.0f}" if r["score"] is not None else "—"
            L.append(f"    [{sc:>4}] {r['ideia']}  ({r['origem']})")
        L += ["", f"  Aprovar: cli.py radar-approve --niche {niche} --ideia \"...\"",
              "  Depois copie a ideia para o campo `temas` do config do nicho."]
    return "\n".join(L)
