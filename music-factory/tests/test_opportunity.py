from datetime import datetime, timedelta, timezone

from core import catalog, opportunity


def test_cache_status_invalid_without_data(conn):
    st = opportunity.cache_status(conn, "n1")
    assert st["valido"] is False
    assert st["n"] == 0


def test_cache_status_invalid_when_stale(conn):
    opportunity.init(conn)
    old = (datetime.now(timezone.utc) - timedelta(days=opportunity.CACHE_VALIDO_DIAS + 5)).isoformat()
    conn.execute(
        "INSERT INTO theme_opportunity (niche, theme, score, fonte, collected_at) VALUES (?,?,?,?,?)",
        ("n1", "Tema A", 80, "vidiq", old),
    )
    conn.commit()
    st = opportunity.cache_status(conn, "n1")
    assert st["valido"] is False
    assert "dias" in st["motivo"]


def test_save_theme_score_and_rank_themes(conn):
    opportunity.save_theme_score(conn, "n1", "Tema A", 90)
    opportunity.save_theme_score(conn, "n1", "Tema B", 10)
    ranked, scores = opportunity.rank_themes(conn, "n1", ["Tema A", "Tema B", "Tema C"])
    # com score: ordenados por score desc; sem score: no fim, ordem original
    assert ranked == ["Tema A", "Tema B", "Tema C"]
    assert scores["Tema A"] == 90


def test_pick_theme_by_opportunity_returns_none_without_valid_cache(conn):
    tema, motivo = opportunity.pick_theme_by_opportunity(conn, "n1", ["Tema A"])
    assert tema is None
    assert "coleta" in motivo or "cache" in motivo


def test_pick_theme_by_opportunity_skips_themes_in_cooldown(conn):
    opportunity.save_theme_score(conn, "n1", "Tema A", 90)
    opportunity.save_theme_score(conn, "n1", "Tema B", 50)
    catalog.register_theme(conn, "n1", "Tema A")

    tema, motivo = opportunity.pick_theme_by_opportunity(
        conn, "n1", ["Tema A", "Tema B"], cooldown_days=9999
    )
    assert tema == "Tema B"
    assert "score 50" in motivo


def test_add_and_approve_ideia(conn):
    opportunity.add_ideia(conn, "n1", "Nova ideia de tema", origem="radar", score=42)
    pendentes = opportunity.listar_ideias(conn, "n1")
    assert len(pendentes) == 1
    assert pendentes[0]["ideia"] == "Nova ideia de tema"

    opportunity.aprovar_ideia(conn, "n1", "Nova ideia de tema")
    assert opportunity.listar_ideias(conn, "n1") == []
    aprovadas = opportunity.listar_ideias(conn, "n1", status="aprovada")
    assert len(aprovadas) == 1


def test_aprovar_ideia_unknown_raises(conn):
    import pytest
    with pytest.raises(LookupError):
        opportunity.aprovar_ideia(conn, "n1", "não existe")
