from core import vidiq


def test_ingest_keywords_stores_seed_and_related(conn):
    payload = {
        "seedKeyword": {"keyword": "gospel blues", "volume": 50, "competition": 20, "overall": 70,
                         "estimatedMonthlySearch": 12000, "countryVolume": 8000},
        "relatedKeywords": [
            {"keyword": "louvor country", "volume": 30, "competition": 10, "overall": 60,
             "estimatedMonthlySearch": 4000},
        ],
        "country": "BR",
    }
    n = vidiq.ingest_keywords(conn, "n1", payload)
    assert n == 2
    rows = conn.execute("SELECT * FROM vidiq_keywords WHERE niche='n1'").fetchall()
    assert {r["keyword"] for r in rows} == {"gospel blues", "louvor country"}
    assert all(r["pais"] == "BR" for r in rows)


def test_ingest_keywords_skips_entries_without_keyword(conn):
    payload = {"relatedKeywords": [{"volume": 10}]}
    n = vidiq.ingest_keywords(conn, "n1", payload)
    assert n == 0


def test_ingest_outliers_filters_by_breakout_score(conn):
    payload = {"videos": [
        {"videoTitle": "Video forte", "breakoutScore": 8.0, "channelTitle": "X", "subscriberCount": 100},
        {"videoTitle": "Video fraco", "breakoutScore": 2.0, "channelTitle": "Y", "subscriberCount": 50},
    ]}
    n = vidiq.ingest_outliers(conn, "n1", payload, min_breakout=5.0)
    assert n == 1
    ideias = conn.execute("SELECT ideia FROM ideias WHERE niche='n1'").fetchall()
    assert ideias[0]["ideia"] == "Video forte"


def test_oportunidades_filters_by_competition_and_volume(conn):
    vidiq.ingest_keywords(conn, "n1", {
        "relatedKeywords": [
            {"keyword": "espaco aberto", "competition": 10, "overall": 80, "estimatedMonthlySearch": 5000},
            {"keyword": "muito concorrido", "competition": 90, "overall": 95, "estimatedMonthlySearch": 50000},
            {"keyword": "pouco buscado", "competition": 5, "overall": 50, "estimatedMonthlySearch": 100},
        ],
    })
    linhas = vidiq.oportunidades(conn, "n1", max_competition=30, min_buscas=3000)
    assert [r["keyword"] for r in linhas] == ["espaco aberto"]
