"""Montador de playlist long-form (novas + acervo) com chapters automáticos.

Regras (derivadas dos padrões validados em gospel-blues-channel):
  1. Posição 1 = faixa do ACERVO com maior VPH — segura os primeiros 30s,
     que decidem a sessão. Nunca abrir com faixa nova/não testada.
  2. Faixas novas nas posições pares — nunca abrindo nem fechando.
  3. Nenhuma faixa reutilizada dentro do período de descanso (padrão 21 dias).
  4. Fecho com até 2 faixas 'calm' (sono/oração).
  5. Alvo de 60 min; chapters gerados a partir das durações acumuladas.
"""

from datetime import datetime, timezone

from . import catalog


def _fmt_ts(seconds: int) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def build(conn, niche, *, new_track_ids=(), target_sec=3600, cooldown_days=21,
          tolerance_sec=180, n_closers=2):
    """Monta a sequência da playlist. NÃO grava — devolve o plano para inspeção.

    Retorna dict com: sequence (faixas + position/start_sec), total_sec,
    deficit_sec e warnings. Degrada com aviso em vez de estourar quando o
    acervo é insuficiente.
    """
    warnings = []
    new_ids = list(new_track_ids)

    novas = []
    for tid in new_ids:
        row = conn.execute("SELECT * FROM tracks WHERE id=?", (tid,)).fetchone()
        if row is None:
            raise LookupError(f"faixa nova inexistente: id={tid}")
        novas.append(row)

    acervo = catalog.eligible_tracks(
        conn, niche, cooldown_days=cooldown_days, exclude_ids=set(new_ids)
    )

    if not acervo and not novas:
        raise ValueError(
            f"nicho {niche!r} não tem nenhuma faixa elegível nem faixa nova. "
            "Rode 'import-acervo' ou 'daily-brief' primeiro."
        )

    # Reserva de fecho: faixas calmas do acervo (as menos prioritárias por VPH)
    calmas = [t for t in acervo if t["mood"] == "calm"]
    closers = calmas[-n_closers:] if calmas else []
    if len(closers) < n_closers:
        warnings.append(
            f"apenas {len(closers)} faixa(s) 'calm' disponível(is) para o fecho "
            f"(ideal: {n_closers}). Marque faixas com mood='calm'."
        )
    closer_ids = {t["id"] for t in closers}

    # Abertura: maior VPH do acervo (acervo já vem ordenado por vph desc)
    restante = [t for t in acervo if t["id"] not in closer_ids]
    if restante:
        opener = restante.pop(0)
    else:
        opener = novas.pop(0) if novas else closers.pop(0)
        warnings.append(
            "sem faixa de acervo para abrir; abrindo com faixa nova (não testada). "
            "O ideal é abrir com a de maior VPH."
        )

    sequence = [opener]
    reservado = sum(_dur(t) for t in closers)

    # Miolo: novas nas posições pares, acervo nas ímpares
    while restante or novas:
        total = sum(_dur(t) for t in sequence)
        if total + reservado >= target_sec - tolerance_sec:
            break
        proxima_pos = len(sequence) + 1
        if proxima_pos % 2 == 0 and novas:
            sequence.append(novas.pop(0))
        elif restante:
            sequence.append(restante.pop(0))
        elif novas:
            sequence.append(novas.pop(0))
        else:
            break

    sequence.extend(closers)

    total_sec = sum(_dur(t) for t in sequence)
    deficit = max(0, target_sec - tolerance_sec - total_sec)
    if deficit:
        faltam = -(-deficit // 270)  # ceil, ~4min30 por faixa
        warnings.append(
            f"acervo insuficiente: faltam {_fmt_ts(deficit)} para o alvo de "
            f"{_fmt_ts(target_sec)} (~{faltam} faixa(s)). A playlist sai mais curta."
        )

    if any(t["duration_estimated"] for t in sequence):
        n_est = sum(1 for t in sequence if t["duration_estimated"])
        warnings.append(
            f"{n_est} de {len(sequence)} faixas com duração ESTIMADA. "
            "Os timestamps só ficam corretos após 'set-audio' com a duração real."
        )

    itens, cursor = [], 0
    for i, t in enumerate(sequence, start=1):
        itens.append({
            "position": i, "track_id": t["id"], "title": t["title"],
            "mood": t["mood"], "duration_sec": _dur(t), "start_sec": cursor,
            "timestamp": _fmt_ts(cursor), "is_new": t["id"] in set(new_ids),
            "estimated": bool(t["duration_estimated"]),
        })
        cursor += _dur(t)

    return {"niche": niche, "sequence": itens, "total_sec": total_sec,
            "target_sec": target_sec, "deficit_sec": deficit, "warnings": warnings}


def _dur(track, fallback=270):
    return int(track["duration_sec"] or fallback)


def save(conn, plan, *, slug, title=None):
    """Persiste o plano e registra o uso das faixas (alimenta a anti-repetição)."""
    ts = catalog.now()
    cur = conn.execute(
        """INSERT INTO playlists (slug, niche, title, target_sec, total_sec, created_at)
           VALUES (?,?,?,?,?,?)
           ON CONFLICT(slug) DO UPDATE SET
               title=excluded.title, total_sec=excluded.total_sec""",
        (slug, plan["niche"], title, plan["target_sec"], plan["total_sec"], ts),
    )
    pid = conn.execute("SELECT id FROM playlists WHERE slug=?", (slug,)).fetchone()["id"]

    # Recriar do zero permite reconstruir a playlist com durações reais
    conn.execute("DELETE FROM playlist_tracks WHERE playlist_id=?", (pid,))
    conn.execute("DELETE FROM usage WHERE playlist_id=?", (pid,))
    for item in plan["sequence"]:
        conn.execute(
            "INSERT INTO playlist_tracks (playlist_id, track_id, position, start_sec) VALUES (?,?,?,?)",
            (pid, item["track_id"], item["position"], item["start_sec"]),
        )
        conn.execute(
            "INSERT INTO usage (track_id, playlist_id, used_at) VALUES (?,?,?)",
            (item["track_id"], pid, ts),
        )
    conn.commit()
    return pid


def render_chapters(plan) -> str:
    """Tracklist com timestamps, pronta para colar na descrição do YouTube."""
    linhas = []
    for item in plan["sequence"]:
        marca = " 🆕" if item["is_new"] else ""
        linhas.append(f"{item['timestamp']} — {item['title']}{marca}")
    return "\n".join(linhas)
