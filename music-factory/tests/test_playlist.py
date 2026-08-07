import pytest

from core import catalog, playlist


def _seed_acervo(conn, niche, n, *, mood="retain", dur=300, prefix="f"):
    ids = []
    for i in range(n):
        row = catalog.add_track(
            conn, niche, f"Faixa {prefix}{i}", slug=f"{niche}-{prefix}{i}",
            status="audio_ok", duration_sec=dur, mood=mood,
        )
        ids.append(row["id"])
    return ids


def test_build_raises_without_any_track(conn):
    with pytest.raises(ValueError):
        playlist.build(conn, "vazio")


def test_build_opens_with_highest_vph_archive_track(conn):
    _seed_acervo(conn, "n1", 3)
    conn.execute("UPDATE tracks SET vph=10 WHERE slug='n1-f0'")
    conn.execute("UPDATE tracks SET vph=99 WHERE slug='n1-f1'")
    conn.execute("UPDATE tracks SET vph=5 WHERE slug='n1-f2'")
    conn.commit()

    plano = playlist.build(conn, "n1", target_sec=10 ** 6, tolerance_sec=0)
    assert plano["sequence"][0]["title"] == "Faixa f1"


def test_build_closes_with_calm_tracks(conn):
    _seed_acervo(conn, "n1", 3, mood="retain", prefix="r")
    _seed_acervo(conn, "n1", 2, mood="calm", prefix="c")
    plano = playlist.build(conn, "n1", target_sec=10 ** 6, tolerance_sec=0, n_closers=2)
    closers = plano["sequence"][-2:]
    assert all(c["mood"] == "calm" for c in closers)


def test_build_warns_when_acervo_insufficient(conn):
    _seed_acervo(conn, "n1", 1, dur=100)
    plano = playlist.build(conn, "n1", target_sec=3600, tolerance_sec=0)
    assert plano["deficit_sec"] > 0
    assert any("insuficiente" in w for w in plano["warnings"])


def test_save_then_ignorar_playlist_allows_rebuild(conn):
    _seed_acervo(conn, "n1", 3)
    plano1 = playlist.build(conn, "n1", target_sec=10 ** 6, tolerance_sec=0)
    assert len(plano1["sequence"]) == 3
    pid = playlist.save(conn, plano1, slug="pl-n1")

    # sem ignorar_playlist, tudo entrou em cooldown -> não há faixa livre
    with pytest.raises(ValueError):
        playlist.build(conn, "n1", target_sec=10 ** 6, tolerance_sec=0)

    # ignorando a própria playlist, remontagem funciona
    plano2 = playlist.build(conn, "n1", target_sec=10 ** 6, tolerance_sec=0,
                             ignorar_playlist=pid)
    assert len(plano2["sequence"]) == 3


def test_render_chapters_marks_new_tracks(conn):
    ids = _seed_acervo(conn, "n1", 2)
    plano = playlist.build(conn, "n1", new_track_ids=[ids[0]], target_sec=10 ** 6,
                            tolerance_sec=0)
    out = playlist.render_chapters(plano)
    assert "🆕" in out
