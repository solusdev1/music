from core import catalog, quality


def _add_lyrics(conn, tmp_path, niche, name, text):
    p = tmp_path / f"{name}.txt"
    p.write_text(text, encoding="utf-8")
    catalog.add_track(conn, niche, name, slug=f"{niche}-{name}", lyrics_path=str(p))


def test_extract_lyric_text_strips_metatags():
    raw = "[Verse 1]\nSó a noite sabe\n[Chorus]\nSó a noite sabe"
    out = quality.extract_lyric_text(raw)
    assert "[Verse" not in out and "[Chorus" not in out
    assert "noite" in out


def test_vocabulary_report_empty_without_lyrics(conn):
    rep = quality.vocabulary_report(conn, "n1")
    assert rep["n_musicas"] == 0
    assert rep["saturadas"] == []


def test_vocabulary_report_flags_saturated_image_across_songs(conn, tmp_path):
    for i in range(4):
        _add_lyrics(conn, tmp_path, "n1", f"m{i}",
                    "[Verse]\nA noite cai sobre a estrada\nA noite guarda o meu segredo")
    rep = quality.vocabulary_report(conn, "n1", threshold=0.4)
    palavras = {r["palavra"] for r in rep["saturadas"]}
    assert "noite" in palavras


def test_vocabulary_report_protected_words_are_never_saturated(conn, tmp_path):
    for i in range(4):
        _add_lyrics(conn, tmp_path, "n1", f"m{i}", "[Verse]\nDeus está aqui, Deus cuida de mim")
    rep = quality.vocabulary_report(conn, "n1", threshold=0.4, protegidas=["deus"])
    palavras = {r["palavra"] for r in rep["saturadas"]}
    assert "deus" not in palavras


def test_vocabulary_report_routes_stopwords_by_language(conn, tmp_path):
    for i in range(4):
        _add_lyrics(conn, tmp_path, "n1", f"m{i}", "[Verse]\nI know that more than this is still real")
    rep_en = quality.vocabulary_report(conn, "n1", idioma="en-US")
    palavras_en = {r["palavra"] for r in rep_en["frequentes"]}
    assert "more" not in palavras_en and "still" not in palavras_en


def test_avoid_list_requires_minimum_song_count(conn, tmp_path):
    # só 2 músicas repetindo a imagem: não deve contar como vício (min_musicas=3)
    for i in range(2):
        _add_lyrics(conn, tmp_path, "n1", f"m{i}", "[Verse]\nO cheiro de café na cozinha")
    aviso = quality.avoid_list(conn, "n1", min_musicas=3)
    assert aviso["palavras"] == []


def test_title_collisions_detects_shared_content_words(conn):
    catalog.add_track(conn, "n1", "Deus Ouviu Meu Choro", slug="n1-a", status="suno_ready")
    catalog.add_track(conn, "n1", "Deus Ouviu Minha Prece", slug="n1-b", status="suno_ready")
    catalog.add_track(conn, "n1", "Totalmente Diferente Aqui", slug="n1-c", status="suno_ready")
    col = quality.title_collisions(conn, "n1", min_overlap=2)
    assert len(col) == 1
    assert {col[0]["a"], col[0]["b"]} == {"Deus Ouviu Meu Choro", "Deus Ouviu Minha Prece"}
