from datetime import date, timedelta

import pytest

from core import catalog


def test_add_track_is_idempotent_by_slug(conn):
    a = catalog.add_track(conn, "n1", "Minha Faixa", slug="n1-faixa")
    b = catalog.add_track(conn, "n1", "Minha Faixa Editada", slug="n1-faixa")
    assert a["id"] == b["id"]
    row = conn.execute("SELECT title FROM tracks WHERE slug='n1-faixa'").fetchone()
    assert row["title"] == "Minha Faixa Editada"


def test_add_track_rejects_invalid_mood(conn):
    with pytest.raises(ValueError):
        catalog.add_track(conn, "n1", "X", mood="furioso")


def test_set_audio_clears_estimated_flag(conn):
    catalog.add_track(conn, "n1", "Faixa", slug="n1-f", duration_sec=270, estimated=True)
    catalog.set_audio(conn, "n1-f", "/tmp/f.mp3", 301)
    row = conn.execute("SELECT * FROM tracks WHERE slug='n1-f'").fetchone()
    assert row["duration_sec"] == 301
    assert row["duration_estimated"] == 0
    assert row["status"] == "audio_ok"


def test_set_audio_unknown_slug_raises(conn):
    with pytest.raises(LookupError):
        catalog.set_audio(conn, "nope", "/tmp/x.mp3", 100)


def test_eligible_tracks_excludes_draft_and_respects_cooldown(conn):
    catalog.add_track(conn, "n1", "Rascunho", slug="n1-a", status="draft")
    catalog.add_track(conn, "n1", "Pronta", slug="n1-b", status="audio_ok", duration_sec=200)
    elig = catalog.eligible_tracks(conn, "n1")
    assert [t["slug"] for t in elig] == ["n1-b"]

    # marcar uso agora -> some do elegível
    tid = elig[0]["id"]
    conn.execute("INSERT INTO usage (track_id, used_at) VALUES (?, ?)",
                 (tid, catalog.now()))
    conn.commit()
    assert catalog.eligible_tracks(conn, "n1") == []


def test_eligible_tracks_ignorar_playlist_allows_rebuild(conn):
    catalog.add_track(conn, "n1", "Pronta", slug="n1-b", status="audio_ok", duration_sec=200)
    tid = conn.execute("SELECT id FROM tracks WHERE slug='n1-b'").fetchone()["id"]
    conn.execute("INSERT INTO playlists (slug, niche, created_at) VALUES ('pl1','n1',?)", (catalog.now(),))
    pid = conn.execute("SELECT id FROM playlists WHERE slug='pl1'").fetchone()["id"]
    conn.execute("INSERT INTO usage (track_id, playlist_id, used_at) VALUES (?,?,?)",
                 (tid, pid, catalog.now()))
    conn.commit()

    assert catalog.eligible_tracks(conn, "n1") == []
    assert len(catalog.eligible_tracks(conn, "n1", ignorar_playlist=pid)) == 1


def test_theme_filter_respects_self_and_group_cooldown(conn):
    bank = ["Tema A", "Tema B", "Tema C"]
    catalog.register_theme(conn, "n1", "Tema A")
    livres = catalog.theme_filter(conn, "n1", bank, cooldown_days=60)
    assert "Tema A" not in livres
    assert set(livres) == {"Tema B", "Tema C"}

    # tema usado no canal irmão recentemente também sai da lista, na janela de grupo
    catalog.register_theme(conn, "n2", "Tema B")
    livres_grupo = catalog.theme_filter(
        conn, "n1", bank, cooldown_days=60, grupo_niches=["n1", "n2"], cooldown_grupo_days=14
    )
    assert livres_grupo == ["Tema C"]


def test_pick_theme_degrades_to_oldest_when_all_resting(conn):
    bank = ["Tema A", "Tema B"]
    catalog.register_theme(conn, "n1", "Tema A")
    catalog.register_theme(conn, "n1", "Tema B")
    tema, aviso = catalog.pick_theme(conn, "n1", bank, cooldown_days=9999)
    assert tema in bank
    assert aviso is not None and "descanso" in aviso


def test_pick_theme_empty_bank_raises(conn):
    with pytest.raises(ValueError):
        catalog.pick_theme(conn, "n1", [])


def test_pick_hook_cooldown(conn):
    hooks = ["H1", "H2"]
    catalog.register_hook(conn, "n1", "H1")
    livres = catalog.pick_hook(conn, "n1", hooks, cooldown_days=30)
    assert livres == ["H2"]


def test_migrate_tracks_resets_usage_by_default(conn):
    catalog.add_track(conn, "origem", "Faixa 1", slug="origem-f1", status="audio_ok", duration_sec=200)
    migradas = catalog.migrate_tracks(conn, "origem", "destino")
    assert migradas == ["Faixa 1"]
    nova = conn.execute("SELECT * FROM tracks WHERE slug='destino-f1'").fetchone()
    assert nova["vph"] == 0
    assert nova["niche"] == "destino"
    # original não é afetada
    original = conn.execute("SELECT * FROM tracks WHERE slug='origem-f1'").fetchone()
    assert original is not None


def test_migrate_tracks_no_eligible_raises(conn):
    catalog.add_track(conn, "origem", "Rascunho", slug="origem-r", status="draft")
    with pytest.raises(LookupError):
        catalog.migrate_tracks(conn, "origem", "destino")


def test_import_suno_folder_missing_dir_raises(conn, tmp_path):
    with pytest.raises(NotADirectoryError):
        catalog.import_suno_folder(conn, tmp_path / "nao-existe", "n1")


def test_import_suno_folder_reads_style_and_lyrics(conn, tmp_path):
    pasta = tmp_path / "01-minha-musica"
    pasta.mkdir()
    (pasta / "01-style-prompt-suno.txt").write_text("estilo x")
    (pasta / "02-exclude-styles-suno.txt").write_text("nada")
    (pasta / "03-lyrics-suno.txt").write_text("[Verse]\nla la la")

    importadas = catalog.import_suno_folder(conn, tmp_path, "n1")
    assert len(importadas) == 1
    t = importadas[0]
    assert t["title"] == "Minha Musica"
    assert t["style_prompt"] == "estilo x"
    assert t["status"] == "suno_ready"
