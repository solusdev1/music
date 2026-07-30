"""Aprendizado com o desempenho real dos canais.

Substitui o "auto-versionamento" decorativo da v1 por algo que responde à
única pergunta que importa: **o que funcionou nos SEUS canais**.

O primeiro achado ao carregar os dados reais já justificou o módulo: o mesmo
gancho de título reaproveitado poucos dias depois derruba o segundo vídeo —
84% de perda no Country Blues e Fé (1 dia de intervalo) e 48% no Estrada da
Fé (3 dias). Dois canais, mesmo padrão.
"""

import re
from datetime import date, datetime, timezone

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
    collected_at  TEXT NOT NULL,
    UNIQUE(niche, title, published_at)
);
"""


def init(conn):
    conn.executescript(SCHEMA)
    conn.commit()


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
                  duration=None, video_url=None, hook=None):
    """Registra um vídeo publicado. Idempotente por (nicho, título, data)."""
    init(conn)
    if isinstance(published_at, date):
        published_at = published_at.isoformat()
    dur = parse_duration(duration) if not isinstance(duration, int) else duration
    conn.execute(
        """INSERT INTO published (niche, title, hook, published_at, views, comments,
               duration_sec, video_url, collected_at)
           VALUES (?,?,?,?,?,?,?,?,?)
           ON CONFLICT(niche, title, published_at) DO UPDATE SET
               views=excluded.views, comments=excluded.comments,
               duration_sec=COALESCE(excluded.duration_sec, published.duration_sec),
               video_url=COALESCE(excluded.video_url, published.video_url),
               collected_at=excluded.collected_at""",
        (niche, title, hook or extract_hook(title), published_at, int(views),
         int(comments or 0), dur, video_url,
         datetime.now(timezone.utc).isoformat(timespec="microseconds")),
    )
    conn.commit()


def _views_per_day(row, hoje=None):
    hoje = hoje or date.today()
    pub = date.fromisoformat(row["published_at"][:10])
    dias = max(1, (hoje - pub).days)
    return row["views"] / dias


def performance(conn, niche, *, hoje=None):
    """Vídeos do nicho ordenados por views/dia (normaliza idade)."""
    init(conn)
    rows = conn.execute(
        "SELECT * FROM published WHERE niche=? ORDER BY published_at DESC", (niche,)
    ).fetchall()
    out = []
    for r in rows:
        out.append({
            "title": r["title"], "hook": r["hook"], "views": r["views"],
            "comments": r["comments"], "published_at": r["published_at"][:10],
            "duration_sec": r["duration_sec"], "vpd": _views_per_day(r, hoje),
        })
    out.sort(key=lambda x: x["vpd"], reverse=True)
    return out


def hook_collisions(conn, niche, *, hoje=None, janela_dias=30):
    """Ganchos reaproveitados dentro da janela, com a perda medida.

    É a evidência que sustenta o cooldown de gancho: quando o mesmo gancho
    volta rápido, o segundo vídeo fica com uma fração do primeiro.
    """
    perf = performance(conn, niche, hoje=hoje)
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
