"""Catálogo de faixas: cadastro, importação do acervo e anti-repetição."""

import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

MOODS = ("open", "retain", "calm")
STATUSES = ("draft", "suno_ready", "audio_ok", "published")


def now() -> str:
    # microssegundos: com precisão de segundos, dois registros no mesmo segundo
    # empatam e o desempate do "menos recentemente usado" vira ordem de lista.
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    norm = re.sub(r"[^a-zA-Z0-9]+", "-", norm).strip("-").lower()
    return norm or "faixa"


def add_track(conn, niche, title, *, theme=None, mood="retain", style_prompt=None,
              exclude_styles=None, lyrics_path=None, duration_sec=None,
              status="draft", slug=None, estimated=True):
    """Insere faixa. Idempotente por slug: reinserir atualiza em vez de duplicar."""
    if mood not in MOODS:
        raise ValueError(f"mood inválido: {mood!r} (use {MOODS})")
    if status not in STATUSES:
        raise ValueError(f"status inválido: {status!r} (use {STATUSES})")

    slug = slug or f"{niche}-{slugify(title)}"
    conn.execute(
        """INSERT INTO tracks (slug, niche, title, theme, mood, style_prompt,
               exclude_styles, lyrics_path, duration_sec, duration_estimated,
               status, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(slug) DO UPDATE SET
               title=excluded.title, theme=excluded.theme, mood=excluded.mood,
               style_prompt=excluded.style_prompt,
               exclude_styles=excluded.exclude_styles,
               lyrics_path=excluded.lyrics_path,
               duration_sec=COALESCE(excluded.duration_sec, tracks.duration_sec),
               status=excluded.status""",
        (slug, niche, title, theme, mood, style_prompt, exclude_styles,
         lyrics_path, duration_sec, 1 if estimated else 0, status, now()),
    )
    conn.commit()
    return conn.execute("SELECT * FROM tracks WHERE slug=?", (slug,)).fetchone()


def set_audio(conn, slug, audio_path, duration_sec):
    """Marca faixa como audio_ok com duração REAL (deixa de ser estimada)."""
    cur = conn.execute(
        """UPDATE tracks SET audio_path=?, duration_sec=?, duration_estimated=0,
               status='audio_ok' WHERE slug=?""",
        (audio_path, int(duration_sec), slug),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise LookupError(f"faixa não encontrada: {slug!r}")


def eligible_tracks(conn, niche, *, cooldown_days=21, exclude_ids=()):
    """Faixas do acervo liberadas para playlist (fora do período de descanso).

    Só entram faixas com áudio pronto ou já publicadas — draft não tem som.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=cooldown_days)).isoformat()
    rows = conn.execute(
        """SELECT t.*, (SELECT MAX(used_at) FROM usage u WHERE u.track_id=t.id) AS last_used
           FROM tracks t
           WHERE t.niche=? AND t.status IN ('audio_ok','published')
           ORDER BY t.vph DESC, t.created_at ASC""",
        (niche,),
    ).fetchall()
    out = []
    for r in rows:
        if r["id"] in exclude_ids:
            continue
        if r["last_used"] and r["last_used"] > cutoff:
            continue  # ainda em descanso
        out.append(r)
    return out


def pick_theme(conn, niche, theme_bank, *, cooldown_days=60):
    """Escolhe tema do dia evitando os usados recentemente.

    Se todos estiverem em descanso, devolve o menos-recentemente-usado
    (degrada em vez de travar) junto com um aviso.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=cooldown_days)).isoformat()
    used = {
        r["theme"]: r["last"]
        for r in conn.execute(
            "SELECT theme, MAX(used_at) AS last FROM theme_usage WHERE niche=? GROUP BY theme",
            (niche,),
        )
    }
    livres = [t for t in theme_bank if used.get(t, "") <= cutoff]
    if livres:
        return livres[0], None
    if not theme_bank:
        raise ValueError(f"banco de temas vazio para o nicho {niche!r}")
    antigo = min(theme_bank, key=lambda t: used.get(t, ""))
    return antigo, (
        f"todos os {len(theme_bank)} temas usados nos últimos {cooldown_days} dias; "
        f"reaproveitando o mais antigo. Amplie o theme_bank do nicho."
    )


def register_theme(conn, niche, theme):
    conn.execute("INSERT INTO theme_usage (niche, theme, used_at) VALUES (?,?,?)",
                 (niche, theme, now()))
    conn.commit()


def pick_hook(conn, niche, hook_bank, *, cooldown_days=30):
    """Mesma lógica do tema, para ganchos de título."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=cooldown_days)).isoformat()
    used = {
        r["hook"]: r["last"]
        for r in conn.execute(
            "SELECT hook, MAX(used_at) AS last FROM hook_usage WHERE niche=? GROUP BY hook",
            (niche,),
        )
    }
    livres = [h for h in hook_bank if used.get(h, "") <= cutoff]
    if livres:
        return livres
    return sorted(hook_bank, key=lambda h: used.get(h, ""))


def register_hook(conn, niche, hook):
    conn.execute("INSERT INTO hook_usage (niche, hook, used_at) VALUES (?,?,?)",
                 (niche, hook, now()))
    conn.commit()


def import_suno_folder(conn, folder, niche, *, default_duration=270):
    """Importa um lote já gerado (formato 0X-slug/{01,02,03}-*.txt) para o catálogo.

    Usado para backfill do acervo existente. Idempotente: rodar duas vezes
    não duplica, porque o slug é derivado do nome da pasta.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(folder)

    importadas = []
    for sub in sorted(p for p in folder.iterdir() if p.is_dir()):
        style = sub / "01-style-prompt-suno.txt"
        excl = sub / "02-exclude-styles-suno.txt"
        lyr = sub / "03-lyrics-suno.txt"
        if not lyr.exists():
            continue

        # "01-deus-viu-o-que-voce-chorou" -> "Deus Viu O Que Voce Chorou"
        nome = re.sub(r"^\d+-", "", sub.name)
        title = nome.replace("-", " ").title()

        importadas.append(add_track(
            conn, niche, title,
            slug=f"{niche}-{nome}",
            theme=None,
            mood="retain",
            style_prompt=style.read_text(encoding="utf-8").strip() if style.exists() else None,
            exclude_styles=excl.read_text(encoding="utf-8").strip() if excl.exists() else None,
            lyrics_path=str(lyr),
            duration_sec=default_duration,
            status="suno_ready",
            estimated=True,
        ))
    return importadas
