import json

import pytest

from core import brief


def test_load_niche_missing_lists_available(tmp_path):
    (tmp_path / "existe.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FileNotFoundError) as exc:
        brief.load_niche(tmp_path, "nao-existe")
    assert "existe" in str(exc.value)


def test_load_group_returns_self_when_no_group(tmp_path, niche_cfg):
    irmaos, nomes = brief.load_group(tmp_path, niche_cfg)
    assert irmaos == ["test_niche"]
    assert nomes == []


def test_load_group_finds_siblings(tmp_path, niche_cfg):
    a = dict(niche_cfg, niche="a", grupo="familia", nome_exibicao="A")
    b = dict(niche_cfg, niche="b", grupo="familia", nome_exibicao="B")
    (tmp_path / "a.json").write_text(json.dumps(a), encoding="utf-8")
    (tmp_path / "b.json").write_text(json.dumps(b), encoding="utf-8")

    irmaos, nomes = brief.load_group(tmp_path, a)
    assert set(irmaos) == {"a", "b"}
    assert nomes == ["B"]


def test_rotulo_duracao_never_overpromises():
    # 25:48 não pode virar "1 Hora" — é a promessa que retenção paga caro
    assert brief._rotulo_duracao(25 * 60 + 48) == "20 Minutos"
    assert brief._rotulo_duracao(56 * 60) == "1 Hora"
    assert brief._rotulo_duracao(56 * 60, idioma="en-US") == "1 Hour"
    assert brief._rotulo_duracao(0) == ""


def test_make_titles_fills_placeholders(conn, niche_cfg):
    titulos = brief.make_titles(conn, niche_cfg, n=2, total_sec=1500)
    assert len(titulos) == 2
    assert "{GANCHO}" not in titulos[0]["titulo"]
    assert "20 Minutos" in titulos[0]["titulo"]


def test_generate_writes_pauta_and_registers_theme(conn, tmp_path, niche_cfg):
    niches_dir = tmp_path / "niches"
    niches_dir.mkdir()
    (niches_dir / "test_niche.json").write_text(json.dumps(niche_cfg), encoding="utf-8")
    out_root = tmp_path / "out"

    result = brief.generate(conn, niche_cfg, out_root, today="2026-08-06",
                             n_songs=2, niches_dir=niches_dir)

    assert result["tema"] in niche_cfg["temas"]
    assert len(result["faixas"]) == 2
    pauta = result["out_dir"] / "00-PAUTA-DO-DIA.md"
    assert pauta.exists()
    assert result["tema"] in pauta.read_text(encoding="utf-8")

    # tema registrado -> segunda chamada não deveria reescolher o mesmo tema
    # dentro do cooldown, a menos que o banco de temas se esgote
    used = conn.execute(
        "SELECT COUNT(*) c FROM theme_usage WHERE niche='test_niche'"
    ).fetchone()["c"]
    assert used == 1


def test_generate_is_language_aware_for_description(conn, tmp_path, niche_cfg):
    en_cfg = dict(niche_cfg, niche="en_niche", idioma="en-US", pais="US")
    niches_dir = tmp_path / "niches"
    niches_dir.mkdir()
    (niches_dir / "en_niche.json").write_text(json.dumps(en_cfg), encoding="utf-8")

    result = brief.generate(conn, en_cfg, tmp_path / "out", today="2026-08-06",
                             n_songs=1, niches_dir=niches_dir, com_playlist=True)
    desc = (result["out_dir"] / "playlist" / "descricao.txt").read_text(encoding="utf-8")
    assert "Press play" in desc


def test_titulo_sem_duracao_nao_deixa_conector_orfao(conn, niche_cfg):
    """Sem áudio ainda não há duração honesta — o slot sai inteiro."""
    cfg = dict(niche_cfg, formula_titulo="{GANCHO} 🙏 | {DURACAO} de Teste Para {BENEFICIO}")
    titulo = brief.make_titles(conn, cfg, n=1)[0]["titulo"]
    assert " de Teste" not in titulo
    assert "  " not in titulo
    assert titulo.startswith("GANCHO UM 🙏 | Teste Para")


def test_make_titles_ignora_gancho_aposentado(conn, niche_cfg):
    cfg = dict(niche_cfg, ganchos_aposentados=["GANCHO UM"])
    ganchos = [t["gancho"] for t in brief.make_titles(conn, cfg, n=3)]
    assert "GANCHO UM" not in ganchos


def test_hashtags_da_playlist_variam_com_o_tema(conn, tmp_path, niche_cfg):
    """A lista fixa em todo vídeo reforçava sinal de duplicata no YouTube."""
    cfg = dict(niche_cfg, hashtags=[f"#Tag{i}" for i in range(10)])
    niches_dir = tmp_path / "niches"
    niches_dir.mkdir()
    (niches_dir / "test_niche.json").write_text(json.dumps(cfg), encoding="utf-8")

    r1 = brief.generate(conn, cfg, tmp_path / "out", today="2026-08-06", n_songs=1,
                        niches_dir=niches_dir, com_playlist=True)
    r2 = brief.generate(conn, cfg, tmp_path / "out", today="2026-08-07", n_songs=1,
                        niches_dir=niches_dir, com_playlist=True)
    assert r1["tema"] != r2["tema"]
    tags1 = (r1["out_dir"] / "playlist" / "hashtags.txt").read_text(encoding="utf-8")
    tags2 = (r2["out_dir"] / "playlist" / "hashtags.txt").read_text(encoding="utf-8")
    assert tags1 != tags2


def test_pauta_avisa_style_prompt_sem_voz(conn, tmp_path, niche_cfg):
    niches_dir = tmp_path / "niches"
    niches_dir.mkdir()
    (niches_dir / "test_niche.json").write_text(json.dumps(niche_cfg), encoding="utf-8")
    r = brief.generate(conn, niche_cfg, tmp_path / "out", today="2026-08-06",
                       n_songs=1, niches_dir=niches_dir)
    assert any("`voz`" in a for a in r["avisos"])


def test_prompt_do_dia_carrega_o_oficio_da_letra(conn, tmp_path, niche_cfg):
    niches_dir = tmp_path / "niches"
    niches_dir.mkdir()
    (niches_dir / "test_niche.json").write_text(json.dumps(niche_cfg), encoding="utf-8")
    r = brief.generate(conn, niche_cfg, tmp_path / "out", today="2026-08-06",
                       n_songs=1, niches_dir=niches_dir)
    prompt = (r["out_dir"] / "01-PROMPT-LETRAS.md").read_text(encoding="utf-8")
    assert "Gancho nos 3 primeiros segundos" in prompt
    assert "Refrão cantável" in prompt


def test_faixa_instrumental_recebe_oficio_proprio(conn, tmp_path, niche_cfg):
    cfg = dict(niche_cfg, niche="inst", formato="instrumental")
    niches_dir = tmp_path / "niches"
    niches_dir.mkdir()
    (niches_dir / "inst.json").write_text(json.dumps(cfg), encoding="utf-8")
    r = brief.generate(conn, cfg, tmp_path / "out", today="2026-08-06",
                       n_songs=1, niches_dir=niches_dir)
    prompt = (r["out_dir"] / "01-PROMPT-LETRAS.md").read_text(encoding="utf-8")
    assert "nunca resolve num clímax" in prompt.lower()
    assert "Refrão cantável" not in prompt
