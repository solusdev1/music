"""Aprendizado com o desempenho real dos canais.

Substitui o "auto-versionamento" decorativo da v1 por algo que responde à
única pergunta que importa: **o que funcionou nos SEUS canais**.

O primeiro achado ao carregar os dados reais já justificou o módulo: o mesmo
gancho de título reaproveitado poucos dias depois derruba o segundo vídeo —
84% de perda no Country Blues e Fé (1 dia de intervalo) e 48% no Estrada da
Fé (3 dias). Dois canais, mesmo padrão.
"""

import re
from datetime import date, datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS published (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    niche         TEXT NOT NULL,
    title         TEXT NOT NULL,
    hook          TEXT,
    published_at  TEXT NOT NULL,
    views         INTEGER NOT NULL,
    comments      INTEGER DEFAULT 0,
    duration_sec  INTEGER,
    video_url     TEXT,
    formato       TEXT DEFAULT 'long',
    collected_at  TEXT NOT NULL,
    UNIQUE(niche, title, published_at)
);
"""

# Shorts (<=3min) e longos disputam audiências diferentes. Misturar os dois
# na mesma média esconde exatamente o efeito que se quer medir.
LIMITE_SHORT_SEC = 180


def init(conn):
    conn.executescript(SCHEMA)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(published)")}
    if "formato" not in cols:  # migração de bancos criados antes
        conn.execute("ALTER TABLE published ADD COLUMN formato TEXT DEFAULT 'long'")
    conn.commit()


def classify(duration_sec, formato=None):
    """Short ou long. Duração decide, salvo se informado explicitamente."""
    if formato in ("short", "long"):
        return formato
    if duration_sec is not None and duration_sec <= LIMITE_SHORT_SEC:
        return "short"
    return "long"


def parse_duration(txt):
    """'1:54:49' ou '4:34' -> segundos. None se não der para ler."""
    if not txt:
        return None
    partes = [p for p in str(txt).strip().split(":") if p.isdigit()]
    if not partes:
        return None
    seg = 0
    for p in partes:
        seg = seg * 60 + int(p)
    return seg


def extract_hook(title):
    """Gancho = trecho emocional antes do separador.

    Os títulos do projeto seguem '[GANCHO] 🙏 | [formato/benefício]'.
    Corta no primeiro '|' ou emoji e normaliza para comparação.
    """
    t = re.split(r"[|🙏😴🌙✨🎵]", title)[0]
    t = re.sub(r"\s+", " ", t).strip(" -–—:").upper()
    return t or title.strip().upper()


def add_published(conn, niche, title, published_at, views, *, comments=0,
                  duration=None, video_url=None, hook=None, formato=None):
    """Registra um vídeo publicado. Idempotente por (nicho, título, data)."""
    init(conn)
    if isinstance(published_at, date):
        published_at = published_at.isoformat()
    dur = parse_duration(duration) if not isinstance(duration, int) else duration
    conn.execute(
        """INSERT INTO published (niche, title, hook, published_at, views, comments,
               duration_sec, video_url, formato, collected_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(niche, title, published_at) DO UPDATE SET
               views=excluded.views, comments=excluded.comments,
               duration_sec=COALESCE(excluded.duration_sec, published.duration_sec),
               video_url=COALESCE(excluded.video_url, published.video_url),
               formato=excluded.formato, collected_at=excluded.collected_at""",
        (niche, title, hook or extract_hook(title), published_at, int(views),
         int(comments or 0), dur, video_url, classify(dur, formato),
         datetime.now(timezone.utc).isoformat(timespec="microseconds")),
    )
    conn.commit()


def _views_per_day(row, hoje=None):
    hoje = hoje or date.today()
    pub = date.fromisoformat(row["published_at"][:10])
    dias = max(1, (hoje - pub).days)
    return row["views"] / dias


def performance(conn, niche, *, hoje=None, formato=None):
    """Vídeos do nicho ordenados por views/dia (normaliza idade)."""
    init(conn)
    q = "SELECT * FROM published WHERE niche=?"
    params = [niche]
    if formato:
        q += " AND formato=?"
        params.append(formato)
    rows = conn.execute(q + " ORDER BY published_at DESC", params).fetchall()
    out = []
    for r in rows:
        out.append({
            "title": r["title"], "hook": r["hook"], "views": r["views"],
            "comments": r["comments"], "published_at": r["published_at"][:10],
            "duration_sec": r["duration_sec"], "formato": r["formato"] or "long",
            "vpd": _views_per_day(r, hoje),
        })
    out.sort(key=lambda x: x["vpd"], reverse=True)
    return out


def hook_collisions(conn, niche, *, hoje=None, janela_dias=30):
    """Ganchos reaproveitados dentro da janela, com a perda medida.

    É a evidência que sustenta o cooldown de gancho: quando o mesmo gancho
    volta rápido, o segundo vídeo fica com uma fração do primeiro.
    """
    perf = performance(conn, niche, hoje=hoje, formato="long")
    por_gancho = {}
    for p in perf:
        por_gancho.setdefault(p["hook"], []).append(p)

    colisoes = []
    for hook, vids in por_gancho.items():
        if len(vids) < 2:
            continue
        vids = sorted(vids, key=lambda v: v["published_at"])
        for anterior, atual in zip(vids, vids[1:]):
            gap = (date.fromisoformat(atual["published_at"])
                   - date.fromisoformat(anterior["published_at"])).days
            if gap > janela_dias or anterior["vpd"] <= 0:
                continue
            colisoes.append({
                "hook": hook, "gap_dias": gap,
                "primeiro": anterior, "segundo": atual,
                "retencao_pct": 100 * atual["vpd"] / anterior["vpd"],
            })
    return sorted(colisoes, key=lambda c: c["retencao_pct"])


def sync_vph(conn, niche, *, hoje=None):
    """Copia views/dia para as faixas do catálogo cujo título casa.

    É o que faz a regra "abrir a playlist pela faixa de maior VPH" usar
    desempenho real em vez de zero.
    """
    perf = performance(conn, niche, hoje=hoje)
    casados = 0
    for p in perf:
        cur = conn.execute(
            "UPDATE tracks SET vph=? WHERE niche=? AND LOWER(title)=LOWER(?)",
            (p["vpd"], niche, p["title"]),
        )
        casados += cur.rowcount
    conn.commit()
    return casados, len(perf)


def format_report(conn, niche, *, hoje=None):
    perf = performance(conn, niche, hoje=hoje)
    if not perf:
        return (f"Nenhum vídeo publicado registrado para {niche!r}.\n"
                "Registre com: cli.py add-published --niche ... --title ... "
                "--date AAAA-MM-DD --views N")

    L = [f"📊 DESEMPENHO REAL — {niche} ({len(perf)} vídeo(s))", ""]
    L.append(f"  {'v/dia':>7} {'views':>7} {'com':>4}  {'duração':>8}  título")
    L.append("  " + "-" * 72)
    for p in perf:
        dur = ""
        if p["duration_sec"]:
            h, rem = divmod(p["duration_sec"], 3600)
            m, s = divmod(rem, 60)
            dur = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        L.append(f"  {p['vpd']:>7.0f} {p['views']:>7} {p['comments']:>4}  {dur:>8}  {p['title'][:40]}")

    media = sum(p["vpd"] for p in perf) / len(perf)
    L += ["", f"  melhor: {perf[0]['vpd']:.0f} v/dia · média: {media:.0f} v/dia"]

    col = hook_collisions(conn, niche, hoje=hoje)
    if col:
        L += ["", "⚠️  GANCHOS REAPROVEITADOS CEDO DEMAIS"]
        for c in col:
            L.append(
                f"  «{c['hook'][:38]}» — {c['gap_dias']}d de intervalo: "
                f"{c['primeiro']['vpd']:.0f} → {c['segundo']['vpd']:.0f} v/dia "
                f"({c['retencao_pct']:.0f}% do primeiro)"
            )
        L.append("  → o cooldown de gancho do nicho impede que isso se repita.")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# CADÊNCIA DE SHORTS × ENTREGA DO LONGO
#
# Hipótese do operador: interromper os Shorts derruba a entrega dos vídeos
# longos, e em algum canal os Shorts passaram a canibalizar o longo por
# completo. É plausível — Shorts e long-form recrutam audiências diferentes,
# e o público condicionado a Short costuma abandonar cedo um vídeo de 1h,
# o que devolve sinal ruim de retenção.
#
# Este módulo NÃO decide se a hipótese é verdadeira. Ele organiza os dados
# semana a semana para que ela fique verificável com o histórico do próprio
# canal, em vez de ser aceita ou descartada por intuição.
# ═══════════════════════════════════════════════════════════════════════════

MIN_SEMANAS_SINAL = 6


def _segunda(d):
    return d - timedelta(days=d.weekday())


def weekly_cadence(conn, niche, *, hoje=None):
    """Por semana: quantos Shorts saíram e como os longos entregaram."""
    init(conn)
    perf = performance(conn, niche, hoje=hoje)
    if not perf:
        return []

    semanas = {}
    for p in perf:
        wk = _segunda(date.fromisoformat(p["published_at"]))
        s = semanas.setdefault(wk, {"shorts": 0, "longos": [], "views_short": 0})
        if p["formato"] == "short":
            s["shorts"] += 1
            s["views_short"] += p["views"]
        else:
            s["longos"].append(p["vpd"])

    out = []
    for wk in sorted(semanas):
        s = semanas[wk]
        longos = sorted(s["longos"])
        mediana = longos[len(longos) // 2] if longos else None
        out.append({
            "semana": wk.isoformat(), "shorts": s["shorts"],
            "n_longos": len(longos), "vpd_mediano": mediana,
            "views_short": s["views_short"],
        })
    return out


def shorts_gap(conn, niche, *, hoje=None):
    """Dias desde o último Short. None se o canal nunca publicou Short."""
    init(conn)
    row = conn.execute(
        "SELECT MAX(published_at) AS ultimo FROM published WHERE niche=? AND formato='short'",
        (niche,),
    ).fetchone()
    if not row or not row["ultimo"]:
        return None
    return ((hoje or date.today()) - date.fromisoformat(row["ultimo"][:10])).days


def cadence_report(conn, niche, *, hoje=None, shorts_por_semana=None):
    linhas = weekly_cadence(conn, niche, hoje=hoje)
    if not linhas:
        return f"Sem histórico publicado para {niche!r}."

    L = [f"📅 CADÊNCIA DE SHORTS × ENTREGA DO LONGO — {niche}", "",
         f"  {'semana':<12} {'shorts':>7} {'longos':>7} {'v/dia longo (mediana)':>23}",
         "  " + "-" * 52]
    for r in linhas:
        vpd = f"{r['vpd_mediano']:.0f}" if r["vpd_mediano"] is not None else "—"
        L.append(f"  {r['semana']:<12} {r['shorts']:>7} {r['n_longos']:>7} {vpd:>23}")

    com_short = [r for r in linhas if r["shorts"] > 0 and r["vpd_mediano"] is not None]
    sem_short = [r for r in linhas if r["shorts"] == 0 and r["vpd_mediano"] is not None]

    L.append("")
    if len(linhas) < MIN_SEMANAS_SINAL:
        L += [f"  ℹ️  Só {len(linhas)} semana(s) de histórico. São necessárias ao menos",
              f"     {MIN_SEMANAS_SINAL} para que a comparação signifique alguma coisa.",
              "     Registre os Shorts com --formato short para o sinal aparecer."]
    elif com_short and sem_short:
        a = sum(r["vpd_mediano"] for r in com_short) / len(com_short)
        b = sum(r["vpd_mediano"] for r in sem_short) / len(sem_short)
        L += [f"  semanas COM Short: {a:>7.0f} v/dia mediano ({len(com_short)} semanas)",
              f"  semanas SEM Short: {b:>7.0f} v/dia mediano ({len(sem_short)} semanas)"]
        if b > 0:
            dif = (a / b - 1) * 100
            L.append(f"  → diferença de {dif:+.0f}% a favor das semanas {'com' if dif > 0 else 'sem'} Short")
        L.append("  ⚠️  Correlação, não causa: sazonalidade e tema também mudam entre semanas.")
    else:
        falta = "sem Short" if not sem_short else "com Short"
        L.append(f"  ℹ️  Ainda não há semanas {falta} para comparar.")

    gap = shorts_gap(conn, niche, hoje=hoje)
    if gap is not None:
        L.append("")
        if shorts_por_semana and gap > 7:
            L.append(f"  ⚠️  Último Short há {gap} dias — a política deste canal é "
                     f"{shorts_por_semana}/semana.")
        else:
            L.append(f"  Último Short há {gap} dia(s).")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# SAÚDE DO CANAL E DECISÃO DE ABANDONO
#
# Estratégia do operador: canal que não entrega é abandonado, cria-se outro.
# O papel do sistema é tornar essa decisão DATADA e comparável, em vez de
# deixá-la à sensação — e evitar que se abandone cedo demais um canal que
# ainda não teve janela, ou tarde demais um que já não responde.
#
# Cuidado metodológico: views/dia decai com a idade do vídeo (views são
# front-loaded). Comparar um vídeo de 6 dias com um de 33 favorece o novo.
# Por isso toda comparação aqui é feita dentro da MESMA faixa de idade.
# ═══════════════════════════════════════════════════════════════════════════

FAIXAS_IDADE = [(0, 7), (8, 15), (16, 30), (31, 60), (61, 10**6)]


def _faixa(idade_dias):
    for lo, hi in FAIXAS_IDADE:
        if lo <= idade_dias <= hi:
            return f"{lo}-{hi if hi < 10**6 else '+'}d"
    return "?"


def by_age_band(conn, niche, *, hoje=None):
    """Mediana de v/dia por faixa de idade — única comparação honesta."""
    hoje = hoje or date.today()
    perf = performance(conn, niche, hoje=hoje, formato="long")
    bandas = {}
    for p in perf:
        idade = max(1, (hoje - date.fromisoformat(p["published_at"])).days)
        bandas.setdefault(_faixa(idade), []).append(p["vpd"])
    return {b: sorted(v)[len(v) // 2] for b, v in bandas.items()}


def channel_health(conn, niche, *, hoje=None, janela_decisao_dias=60,
                   piso_vpd=None, referencia=None):
    """Diagnóstico datado do canal.

    NÃO calcula tendência a partir de um único snapshot. views/dia decai com
    a idade do vídeo, então comparar "vídeos antigos vs recentes" faria todo
    canal ativo parecer em crescimento — inclusive um que está caindo. Só o
    que é apurável de um snapshot entra no veredito: dias sem postar e
    desempenho relativo dentro da mesma faixa de idade.
    """
    hoje = hoje or date.today()
    perf = performance(conn, niche, hoje=hoje, formato="long")
    if not perf:
        return {"niche": niche, "veredito": "SEM DADOS", "n_videos": 0,
                "bandas": {}, "detalhe": "nenhum vídeo longo registrado"}

    datas = sorted(date.fromisoformat(p["published_at"]) for p in perf)
    idade_canal = (hoje - datas[0]).days
    dias_sem_postar = (hoje - datas[-1]).days
    bandas = by_age_band(conn, niche, hoje=hoje)
    decidir_em = date.fromordinal(datas[0].toordinal() + janela_decisao_dias)

    # desempenho relativo: só contra canal de referência NA MESMA faixa
    rel = None
    if referencia:
        comuns = [b for b in bandas if b in referencia]
        if comuns:
            razoes = [bandas[b] / referencia[b] for b in comuns if referencia[b] > 0]
            if razoes:
                rel = sum(razoes) / len(razoes)

    if dias_sem_postar > 30:
        veredito = "PARADO"
    elif piso_vpd and max(bandas.values()) < piso_vpd and idade_canal >= janela_decisao_dias:
        veredito = "ABAIXO DO PISO"
    elif rel is not None and rel < 0.25 and idade_canal >= janela_decisao_dias:
        veredito = "MUITO ABAIXO"
    elif rel is not None and rel < 0.6:
        veredito = "ABAIXO"
    elif idade_canal < janela_decisao_dias:
        veredito = "EM JANELA"
    else:
        veredito = "ATIVO"

    return {
        "niche": niche, "veredito": veredito, "n_videos": len(perf),
        "idade_canal_dias": idade_canal, "dias_sem_postar": dias_sem_postar,
        "decidir_em": decidir_em.isoformat(),
        "janela_vencida": idade_canal >= janela_decisao_dias,
        "relativo": rel, "bandas": bandas,
    }


def health_report(conn, niches, *, hoje=None, janela=60, piso_vpd=None):
    L = ["🩺 SAÚDE DOS CANAIS", ""]
    L.append(f"  {'canal':<30} {'vídeos':>6} {'idade':>6} {'s/ postar':>10} "
             f"{'vs melhor':>7} {'veredito':>15}")
    L.append("  " + "-" * 82)
    # canal de referência = melhor mediana por faixa entre todos
    referencia = {}
    for n in niches:
        for b, v in by_age_band(conn, n, hoje=hoje).items():
            referencia[b] = max(referencia.get(b, 0), v)

    dados = []
    for n in niches:
        h = channel_health(conn, n, hoje=hoje, janela_decisao_dias=janela,
                           piso_vpd=piso_vpd, referencia=referencia)
        dados.append(h)
        if h["veredito"] == "SEM DADOS":
            L.append(f"  {n:<30} {'—':>6} {'—':>6} {'—':>10} {'—':>7} {'SEM DADOS':>15}")
        else:
            rel = f"{h['relativo']*100:.0f}%" if h["relativo"] is not None else "—"
            L.append(f"  {n:<30} {h['n_videos']:>6} {h['idade_canal_dias']:>5}d "
                     f"{h['dias_sem_postar']:>9}d {rel:>7} {h['veredito']:>15}")

    # comparação entre canais só dentro da mesma faixa de idade
    bandas = {}
    for h in dados:
        for b, v in h.get("bandas", {}).items():
            bandas.setdefault(b, []).append((h["niche"], v))
    comparaveis = {b: v for b, v in bandas.items() if len(v) > 1}
    if comparaveis:
        L += ["", "  COMPARAÇÃO POR FAIXA DE IDADE (v/dia mediano)",
              "  views/dia decai com a idade do vídeo; só a mesma faixa é comparável"]
        for b in sorted(comparaveis):
            itens = sorted(comparaveis[b], key=lambda x: -x[1])
            L.append(f"    {b:<8} " + " · ".join(f"{n}: {v:.0f}" for n, v in itens))
    else:
        L += ["", "  ℹ️  Nenhuma faixa de idade tem dois canais — sem comparação honesta ainda."]

    L += ["", "  ℹ️  Tendência (subindo/caindo) exige snapshots ao longo do tempo:",
          "     um retrato único não distingue queda de decaimento natural de v/dia.",
          "     Rode `add-published` periodicamente para construir a série."]

    acao = [h for h in dados if h["veredito"] in ("PARADO", "MUITO ABAIXO", "ABAIXO DO PISO")
            and h.get("janela_vencida")]
    if acao:
        L += ["", "  ⚠️  DECISÃO VENCIDA (janela de avaliação já passou)"]
        for h in acao:
            L.append(f"    {h['niche']}: {h['veredito']} — janela venceu em {h['decidir_em']}")
    return "\n".join(L)
