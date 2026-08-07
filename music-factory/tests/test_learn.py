from datetime import date, timedelta

from core import learn


def _hoje():
    return date(2026, 8, 6)


def test_classify_by_duration_and_override():
    assert learn.classify(120) == "short"
    assert learn.classify(181) == "long"
    assert learn.classify(9999, formato="short") == "short"
    assert learn.classify(None) == "long"


def test_parse_duration_variants():
    assert learn.parse_duration("4:34") == 274
    assert learn.parse_duration("1:54:49") == 6889
    assert learn.parse_duration(None) is None
    assert learn.parse_duration("") is None


def test_extract_hook_cuts_on_separator_and_normalizes():
    assert learn.extract_hook("Deus Conhece Sua Dor 🙏 | 1 Hora de Gospel") == "DEUS CONHECE SUA DOR"
    assert learn.extract_hook("sem separador") == "SEM SEPARADOR"


def test_add_published_is_idempotent_and_updates_views(conn):
    learn.add_published(conn, "n1", "Video A", "2026-08-01", 100)
    learn.add_published(conn, "n1", "Video A", "2026-08-01", 250)
    rows = conn.execute("SELECT * FROM published WHERE niche='n1'").fetchall()
    assert len(rows) == 1
    assert rows[0]["views"] == 250


def test_performance_orders_by_views_per_day_not_raw_views(conn):
    hoje = _hoje()
    # vídeo antigo com muitas views totais, mas taxa diária baixa
    learn.add_published(conn, "n1", "Antigo Grande", "2026-07-01", 3500)
    # vídeo novo com poucas views totais, mas taxa diária alta
    learn.add_published(conn, "n1", "Novo Pequeno", "2026-08-05", 200)

    perf = learn.performance(conn, "n1", hoje=hoje)
    assert perf[0]["title"] == "Novo Pequeno"


def test_hook_collisions_measures_retention_drop(conn):
    hoje = _hoje()
    learn.add_published(conn, "n1", "GANCHO X | primeira", "2026-08-01", 1000, formato="long")
    learn.add_published(conn, "n1", "GANCHO X | segunda", "2026-08-02", 100, formato="long")

    colisoes = learn.hook_collisions(conn, "n1", hoje=hoje, janela_dias=30)
    assert len(colisoes) == 1
    c = colisoes[0]
    assert c["gap_dias"] == 1
    assert c["retencao_pct"] < 100


def test_hook_collisions_ignores_far_apart_reuse(conn):
    hoje = _hoje()
    learn.add_published(conn, "n1", "GANCHO Y | primeira", "2026-01-01", 1000, formato="long")
    learn.add_published(conn, "n1", "GANCHO Y | segunda", "2026-08-01", 100, formato="long")
    colisoes = learn.hook_collisions(conn, "n1", hoje=hoje, janela_dias=30)
    assert colisoes == []


def test_channel_health_parado_when_no_post_for_30_days(conn):
    hoje = _hoje()
    learn.add_published(conn, "n1", "Antigo", "2026-06-01", 100, formato="long")
    h = learn.channel_health(conn, "n1", hoje=hoje)
    assert h["veredito"] == "PARADO"


def test_channel_health_em_janela_when_too_young_to_judge(conn):
    hoje = _hoje()
    learn.add_published(conn, "n1", "Recente", "2026-08-01", 100, formato="long")
    h = learn.channel_health(conn, "n1", hoje=hoje, janela_decisao_dias=60)
    assert h["veredito"] == "EM JANELA"


def test_channel_health_sem_dados(conn):
    h = learn.channel_health(conn, "vazio")
    assert h["veredito"] == "SEM DADOS"


def test_sync_vph_matches_by_title_case_insensitive(conn):
    from core import catalog
    catalog.add_track(conn, "n1", "Minha Faixa", slug="n1-a", status="audio_ok", duration_sec=200)
    learn.add_published(conn, "n1", "minha faixa", "2026-08-01", 500)

    casados, total = learn.sync_vph(conn, "n1", hoje=_hoje())
    assert casados == 1
    row = conn.execute("SELECT vph FROM tracks WHERE slug='n1-a'").fetchone()
    assert row["vph"] > 0


def test_extract_hook_ignora_emoji_no_inicio():
    """Metade dos títulos do projeto começa com 🙏 — o gancho é o mesmo.

    Cortar no primeiro separador devolvia string vazia nesse caso, e o
    fallback entregava o título inteiro: os dois formatos nunca casavam e
    hook_collisions ficava cego para a repetição.
    """
    a = learn.extract_hook("DEUS CONHECE SUA DOR 🙏 1H55 Os Melhores Louvores")
    b = learn.extract_hook("🙏 DEUS CONHECE SUA DOR | Os Melhores Louvores")
    assert a == b == "DEUS CONHECE SUA DOR"


def test_hook_collisions_enxerga_repeticao_com_emoji_no_inicio(conn):
    learn.add_published(conn, "n1", "DEUS CONHECE SUA DOR 🙏 1H55 Louvores",
                        "2026-07-15", 8000, duration=6889, formato="long")
    learn.add_published(conn, "n1", "🙏 DEUS CONHECE SUA DOR | Louvores (1 Hora)",
                        "2026-07-20", 186, duration=3644, formato="long")
    colisoes = learn.hook_collisions(conn, "n1", hoje=date(2026, 7, 25), janela_dias=30)
    assert len(colisoes) == 1
    assert colisoes[0]["hook"] == "DEUS CONHECE SUA DOR"
    assert colisoes[0]["retencao_pct"] < 50   # o segundo ficou com uma fração
