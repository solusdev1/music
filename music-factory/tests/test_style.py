from core import style


def test_voz_vem_antes_da_identidade(niche_cfg):
    cfg = dict(niche_cfg, voz="Male deep baritone vocals",
               style_base="Country blues gospel brasileiro")
    prompt = style.build(cfg)
    assert prompt.index("Male deep baritone") < prompt.index("Country blues")


def test_ancoras_fecham_o_prompt_de_cancao(niche_cfg):
    prompt = style.build(dict(niche_cfg, voz="Male baritone vocals"))
    assert prompt.endswith("vocals lead the mix")


def test_variacao_entra_entre_identidade_e_ancoras(niche_cfg):
    cfg = dict(niche_cfg, voz="Male baritone vocals", style_base="base do canal")
    prompt = style.build(cfg, "slide guitar em primeiro plano")
    assert prompt.index("base do canal") < prompt.index("slide guitar")
    assert prompt.index("slide guitar") < prompt.index("vocals lead the mix")


def test_instrumental_nunca_recebe_ancora_vocal(niche_cfg):
    cfg = dict(niche_cfg, formato="instrumental",
               style_base="[Instrumental] ambient sleep music")
    prompt = style.build(cfg, "soft felt piano")
    assert "vocal" not in prompt.lower()
    assert prompt == "[Instrumental] ambient sleep music, soft felt piano"


def test_nao_repete_ancora_ja_presente_na_base(niche_cfg):
    cfg = dict(niche_cfg, voz="Male baritone vocals",
               style_base="warm blues, vocals lead the mix")
    assert style.build(cfg).lower().count("vocals lead the mix") == 1


def test_exclude_ganha_guardas_anti_instrumental(niche_cfg):
    excl = style.exclude(dict(niche_cfg, exclude_styles="EDM, trap"))
    assert "instrumental only" in excl
    assert "no lead vocals" in excl


def test_exclude_de_canal_instrumental_fica_intacto(niche_cfg):
    cfg = dict(niche_cfg, formato="instrumental",
               exclude_styles="vocals, choir, spoken words")
    assert style.exclude(cfg) == "vocals, choir, spoken words"


def test_diagnostico_aponta_nicho_sem_voz(niche_cfg):
    avisos = style.diagnostico(niche_cfg)
    assert any("`voz`" in a for a in avisos)


def test_diagnostico_pega_termo_ambiguo_em_canal_de_cancao(niche_cfg):
    cfg = dict(niche_cfg, voz="Male baritone vocals",
               style_base="minimalist ambient country blues")
    assert any("ambíguo" in a for a in style.diagnostico(cfg))


def test_diagnostico_limpo_quando_config_esta_correto(niche_cfg):
    cfg = dict(niche_cfg, voz="Male baritone vocals",
               style_base="country blues gospel",
               exclude_styles="EDM, instrumental only, backing vocals only")
    assert style.diagnostico(cfg) == []
