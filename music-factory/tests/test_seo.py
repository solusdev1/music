from core import seo


def test_tags_do_tema_fecham_a_referencia(niche_cfg):
    tags = seo.tags_do_tema("Salmo 91 — proteção na estrada escura")
    assert tags[0] == "#Salmo91"
    assert any("Prote" in t for t in tags[1:])


def test_tags_do_tema_ignoram_palavras_vazias():
    tags = seo.tags_do_tema("Psalm 23 — the Lord is my shepherd")
    assert "#The" not in tags
    assert "#Shepherd" in tags


def test_hashtags_mantem_a_marca_em_todo_video(niche_cfg):
    cfg = dict(niche_cfg, hashtags=[f"#Tag{i}" for i in range(10)])
    a = seo.hashtags(cfg, "Tema A — uma coisa")
    b = seo.hashtags(cfg, "Tema B — outra coisa")
    assert a[:seo.N_MARCA] == b[:seo.N_MARCA] == ["#Tag0", "#Tag1", "#Tag2"]


def test_hashtags_variam_entre_temas(niche_cfg):
    """O sinal de duplicata vinha de repetir as mesmas 11 tags em todo vídeo."""
    cfg = dict(niche_cfg, hashtags=[f"#Tag{i}" for i in range(10)])
    a = seo.hashtags(cfg, "Salmo 91 — proteção na estrada")
    b = seo.hashtags(cfg, "Salmo 23 — o pastor que conduz")
    assert a != b


def test_hashtags_sao_estaveis_para_o_mesmo_tema(niche_cfg):
    cfg = dict(niche_cfg, hashtags=[f"#Tag{i}" for i in range(10)])
    tema = "Salmo 91 — proteção na estrada"
    assert seo.hashtags(cfg, tema) == seo.hashtags(cfg, tema)


def test_hashtags_nao_repetem_dentro_do_conjunto(niche_cfg):
    cfg = dict(niche_cfg, hashtags=["#Gospel", "#Gospel", "#Blues", "#Fe"])
    tags = seo.hashtags(cfg, "Salmo 91 — proteção")
    assert len(tags) == len({t.lower() for t in tags})


def test_hashtags_respeitam_o_limite(niche_cfg):
    cfg = dict(niche_cfg, hashtags=[f"#Tag{i}" for i in range(30)])
    assert len(seo.hashtags(cfg, "Tema — algo", n=8)) == 8


def test_linha_keywords_junta_nicho_e_tema(niche_cfg):
    cfg = dict(niche_cfg, tags_youtube=["gospel blues", "louvores", "country gospel"])
    linha = seo.linha_keywords(cfg, "Salmo 91 — proteção na estrada escura")
    assert "gospel blues" in linha
    assert "Salmo 91" in linha


def test_checklist_segue_o_idioma_do_canal(niche_cfg):
    assert "Aviso de IA" in seo.checklist(niche_cfg)
    assert "AI disclosure" in seo.checklist(dict(niche_cfg, idioma="en-US"))
