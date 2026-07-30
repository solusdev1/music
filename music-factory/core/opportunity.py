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


def pick_theme_by_opportunity(conn, niche, theme_bank, *, cooldown_days=60):
    """Tema do dia = maior oportunidade FORA do período de descanso.

    Combina os dois eixos: demanda (score) e anti-repetição (cooldown).
    Sem cache válido, devolve None para o chamador cair no rodízio simples.
    """
    from . import catalog  # import tardio evita ciclo

    st = cache_status(conn, niche)
    if not st["valido"]:
        return None, st["motivo"]

    ranked, scores = rank_themes(conn, niche, theme_bank)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=cooldown_days)).isoformat()
    usados = {
        r["theme"]: r["last"]
        for r in conn.execute(
            "SELECT theme, MAX(used_at) AS last FROM theme_usage WHERE niche=? GROUP BY theme",
            (niche,),
        )
    }
    for t in ranked:
        if usados.get(t, "") <= cutoff:
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
              f"      python3 cli.py collect-opportunity --niche {niche}"]
        return "\n".join(L)

    ranked, scores = rank_themes(conn, niche, theme_bank)
    L.append(f"  Cache: {st['n']} tema(s) pontuado(s), coletado há {st['idade_dias']} dia(s)")
    L.append("")
    for t in ranked[:15]:
        s = scores.get(t)
        L.append(f"  {s:>5.0f}  {t}" if s is not None else f"      —  {t}")
    return "\n".join(L)
