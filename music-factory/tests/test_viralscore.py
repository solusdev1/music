import pytest

from core import catalog, viralscore

LETRA_BOA = """[Intro]
Eu chamei no escuro

[Verse 1]
A estrada sumiu na neblina
E o medo veio me rondar
Mas eu lembrei do abrigo
Que ninguém pode tirar

[Chorus]
Eu chamei no escuro
E o abrigo respondeu

[Verse 2]
O rádio chiava baixinho
E a noite não tinha fim

[Bridge]
Debaixo das asas
O medo não entra aqui

[Final Chorus]
Eu chamei no escuro
E o abrigo respondeu

[Outro]
E o abrigo respondeu
"""

LETRA_FRACA = """[Verse 1]
Numa noite dessas em que a cidade inteira parecia dormir sem mim
Eu fiquei olhando a janela sem saber o que dizer para ninguém

[Chorus]
Eu queria muito que alguém me dissesse que tudo isso ainda vai passar
"""


def test_letra_completa_pontua_alto(conn, niche_cfg):
    r = viralscore.score(conn, niche_cfg, LETRA_BOA,
                         titulo="GANCHO UM | Teste Para Descansar")
    assert r["total"] >= 90
    assert "viral" in r["banda"]


def test_letra_sem_estrutura_e_com_refrao_longo_pontua_baixo(conn, niche_cfg):
    r = viralscore.score(conn, niche_cfg, LETRA_FRACA, titulo="um título qualquer")
    assert r["total"] < 60
    assert r["acao"].startswith("reescrever")


def test_estrutura_lista_o_que_falta(conn, niche_cfg):
    r = viralscore.score(conn, niche_cfg, LETRA_FRACA, titulo="x")
    estrutura = next(c for c in r["criterios"] if c["criterio"] == "estrutura")
    assert "intro" in estrutura["nota"] and "ponte" in estrutura["nota"]


def test_refrao_longo_perde_ponto(conn, niche_cfg):
    r = viralscore.score(conn, niche_cfg, LETRA_FRACA, titulo="x")
    refrao = next(c for c in r["criterios"] if c["criterio"] == "refrão")
    assert refrao["pontos"] < 20


def test_titulo_fora_do_banco_nao_pontua(conn, niche_cfg):
    r = viralscore.score(conn, niche_cfg, LETRA_BOA, titulo="TÍTULO INVENTADO NA MÃO")
    titulo = next(c for c in r["criterios"] if c["criterio"] == "título")
    assert titulo["pontos"] == 0
    assert "cooldown" in titulo["nota"]


def test_gancho_em_descanso_e_sinalizado(conn, niche_cfg):
    catalog.register_hook(conn, niche_cfg["niche"], "GANCHO UM")
    r = viralscore.score(conn, niche_cfg, LETRA_BOA,
                         titulo="GANCHO UM | Teste Para Descansar")
    titulo = next(c for c in r["criterios"] if c["criterio"] == "título")
    assert "descanso" in titulo["nota"]
    assert titulo["pontos"] == 15  # gancho + benefício, sem o ponto de disponibilidade


def test_canal_instrumental_recusa_score_de_letra(conn, niche_cfg):
    cfg = dict(niche_cfg, formato="instrumental")
    with pytest.raises(ValueError, match="instrumental"):
        viralscore.score(conn, cfg, LETRA_BOA)


def test_parse_reconhece_secao_em_ingles_e_portugues():
    secoes = viralscore.parse_secoes("[Verso 1]\na\n[Final Chorus]\nb\n")
    assert [t for t, _ in secoes] == ["verso", "refrao"]


def test_originalidade_penaliza_imagem_saturada(conn, niche_cfg, tmp_path):
    """Com o acervo carregado, reusar a imagem gasta custa ponto."""
    for i in range(4):
        p = tmp_path / f"{i}.txt"
        p.write_text("[Chorus]\nO abrigo na neblina\n", encoding="utf-8")
        catalog.add_track(conn, niche_cfg["niche"], f"Faixa {i}",
                          lyrics_path=str(p), status="suno_ready")

    r = viralscore.score(conn, niche_cfg, LETRA_BOA, titulo="x")
    orig = next(c for c in r["criterios"] if c["criterio"] == "originalidade")
    assert orig["pontos"] < 20
    assert "neblina" in orig["nota"] or "abrigo" in orig["nota"]


def test_format_report_mostra_total_e_criterios(conn, niche_cfg):
    saida = viralscore.format_report(conn, niche_cfg, LETRA_BOA, titulo="GANCHO UM")
    assert "/100" in saida
    assert "estrutura" in saida and "gancho em 3s" in saida
