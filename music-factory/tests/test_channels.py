from core import channels


# ─── normalização de números ─────────────────────────────────────────────

def test_int_aceita_formatos_de_contagem():
    assert channels._int(12345) == 12345
    assert channels._int("12.345") == 12345      # milhar pt-BR
    assert channels._int("12,345") == 12345      # milhar en
    assert channels._int("1.2K") == 1200
    assert channels._int("3.4M") == 3_400_000
    assert channels._int("1,2 mi") == 1_200_000
    assert channels._int("50k views") == 50_000
    assert channels._int("1 milhão") == 1_000_000


def test_int_devolve_none_no_que_nao_e_numero():
    for v in (None, "", "abc", True):
        assert channels._int(v) is None


# ─── porte do canal ──────────────────────────────────────────────────────

def test_porte_classifica_por_inscritos():
    assert channels.porte(300) == "semente"
    assert channels.porte(5_000) == "pequeno"
    assert channels.porte(50_000) == "medio"
    assert channels.porte(500_000) == "grande"
    assert channels.porte(3_000_000) == "gigante"
    assert channels.porte(None) == "desconhecido"


def test_peso_porte_penaliza_canal_grande():
    assert channels.peso_porte(2_000) > channels.peso_porte(500_000)
    assert channels.peso_porte(500_000) > channels.peso_porte(3_000_000)


# ─── score de breakout ───────────────────────────────────────────────────

def test_canal_pequeno_e_recente_ganha_da_gravadora():
    """O ponto do módulo: 4M de views de uma gravadora não é replicável."""
    pequeno = channels.score_breakout(60_000, 2_000, 5)
    gravadora = channels.score_breakout(4_000_000, 3_000_000, 34)
    assert pequeno["score"] > gravadora["score"]


def test_video_velho_nao_conta_como_breakout():
    novo = channels.score_breakout(300_000, 15_000, 10)
    velho = channels.score_breakout(300_000, 15_000, 200)
    assert novo["score"] > 0
    assert velho["score"] == 0


def test_score_nao_empata_no_teto():
    """Teto duro empatava os melhores candidatos e perdia a ordem no topo."""
    forte = channels.score_breakout(62_000, 2_000, 5)     # 31x
    menos_forte = channels.score_breakout(88_000, 6_400, 8)  # 13.8x
    assert forte["score"] != menos_forte["score"]
    assert forte["score"] <= 100


def test_sem_views_nao_pontua():
    r = channels.score_breakout(None, 1_000, 3)
    assert r["score"] == 0.0
    assert "sem contagem" in r["motivo"]


def test_multiplicador_e_none_quando_inscritos_desconhecidos():
    """Sem inscritos o cálculo usa um piso — expor isso como 'x' seria mentira."""
    r = channels.score_breakout(90_000, None, 6)
    assert r["multiplicador"] is None
    assert "desconhecidos" in r["motivo"]
    assert r["score"] > 0


def test_peso_recencia_decai_entre_as_janelas():
    assert channels.peso_recencia(5) == 1.0
    assert channels.peso_recencia(14) == 1.0
    assert 0 < channels.peso_recencia(50) < 1.0
    assert channels.peso_recencia(90) == 0.0
    assert channels.peso_recencia(None) == 0.5


# ─── identidade de canal ─────────────────────────────────────────────────

def test_mesmo_canal_por_nome_e_por_id_nao_duplica(conn):
    """Breakout traz só o nome; a busca de canais traz o channelId."""
    channels.save_channel(conn, "n", "Estrada de Fé", subs=2_100)
    channels.save_channel(conn, "n", "Estrada de Fé", channel_id="UC001", subs=2_400)

    linhas = channels.listar_channels(conn, "n")
    assert len(linhas) == 1
    assert linhas[0]["channel_id"] == "UC001"
    assert linhas[0]["subs"] == 2_400
    assert linhas[0]["vezes_visto"] == 2


def test_save_channel_nao_apaga_dado_com_none(conn):
    channels.save_channel(conn, "n", "Canal", channel_id="UC9", subs=5_000, pais="BR")
    channels.save_channel(conn, "n", "Canal", channel_id="UC9")
    r = channels.listar_channels(conn, "n")[0]
    assert r["subs"] == 5_000
    assert r["pais"] == "BR"


def test_canais_de_niches_diferentes_nao_se_misturam(conn):
    channels.save_channel(conn, "a", "Mesmo Canal", channel_id="UC1")
    channels.save_channel(conn, "b", "Mesmo Canal", channel_id="UC1")
    assert len(channels.listar_channels(conn, "a")) == 1
    assert len(channels.listar_channels(conn, "b")) == 1


def test_replicaveis_exclui_canal_grande(conn):
    channels.save_channel(conn, "n", "Pequeno", channel_id="U1", subs=3_000)
    channels.save_channel(conn, "n", "Gravadora", channel_id="U2", subs=3_000_000)
    nomes = [r["nome"] for r in channels.concorrentes_replicaveis(conn, "n")]
    assert nomes == ["Pequeno"]


# ─── ingestão ────────────────────────────────────────────────────────────

def test_ingest_channels_aceita_as_formas_do_payload(conn):
    assert channels.ingest_channels(
        conn, "n", {"channels": [{"channelTitle": "A", "channelId": "U1"}]}) == 1
    assert channels.ingest_channels(
        conn, "n", {"results": [{"title": "B", "id": "U2"}]}) == 1
    assert channels.ingest_channels(conn, "n", [{"name": "C", "channel_id": "U3"}]) == 1
    assert len(channels.listar_channels(conn, "n")) == 3


def test_ingest_channels_ignora_item_sem_identidade(conn):
    assert channels.ingest_channels(conn, "n", {"channels": [{"subscriberCount": 10}]}) == 0


def test_ingest_outliers_pontua_e_mapeia_o_canal(conn):
    payload = {"videos": [{
        "videoTitle": "Deus Viu Suas Lágrimas", "viewCount": 62_000,
        "channelTitle": "Estrada de Fé", "subscriberCount": 2_100,
        "ageDays": 5, "videoId": "aaa",
    }]}
    assert channels.ingest_outliers(conn, "n", payload) == 1

    b = channels.listar_breakouts(conn, "n")[0]
    assert b["titulo"] == "Deus Viu Suas Lágrimas"
    assert b["score"] > 50
    # o canal do vídeo entra no mapa junto, sem coleta separada
    assert [r["nome"] for r in channels.listar_channels(conn, "n")] == ["Estrada de Fé"]


def test_ingest_outliers_e_idempotente(conn):
    payload = {"videos": [{"videoTitle": "T", "viewCount": 1_000,
                           "channelTitle": "C", "subscriberCount": 100,
                           "ageDays": 2, "videoId": "x1"}]}
    channels.ingest_outliers(conn, "n", payload)
    channels.ingest_outliers(conn, "n", payload)
    assert len(channels.listar_breakouts(conn, "n")) == 1


def test_breakouts_ordenam_por_score(conn):
    channels.save_breakout(conn, "n", "gravadora", views=4_000_000,
                           canal="G", canal_subs=3_000_000, idade_dias=34)
    channels.save_breakout(conn, "n", "pequeno", views=60_000,
                           canal="P", canal_subs=2_000, idade_dias=5)
    assert [r["titulo"] for r in channels.listar_breakouts(conn, "n")] == \
        ["pequeno", "gravadora"]


# ─── padrões de título ───────────────────────────────────────────────────

def test_padroes_ignoram_palavra_generica_do_nicho(conn):
    titulos = ["Deus Viu Suas Lagrimas Louvores Country",
               "Deus Guardou Suas Lagrimas Louvores Country"]
    for i, t in enumerate(titulos):
        channels.save_breakout(conn, "n", t, views=60_000, canal=f"C{i}",
                               canal_subs=2_000, idade_dias=5)
    palavras = dict(channels.padroes_de_titulo(conn, "n"))
    # o que distingue estes títulos sobrevive...
    assert palavras["lagrimas"] == 2
    assert palavras["country"] == 2
    # ...e o que aparece em qualquer título do nicho, não
    assert "deus" not in palavras
    assert "louvores" not in palavras
    assert "viu" not in palavras          # menos de 4 letras


def test_padroes_so_olham_quem_passou_do_corte(conn):
    channels.save_breakout(conn, "n", "formato campeao alfa", views=60_000,
                           canal="A", canal_subs=2_000, idade_dias=5)
    channels.save_breakout(conn, "n", "formato campeao beta", views=60_000,
                           canal="B", canal_subs=2_000, idade_dias=5)
    # este é velho: score 0, não deve contaminar o vocabulário
    channels.save_breakout(conn, "n", "fracasso obsoleto zumbi", views=900_000,
                           canal="C", canal_subs=40_000, idade_dias=420)
    palavras = dict(channels.padroes_de_titulo(conn, "n"))
    assert "formato" in palavras and "campeao" in palavras
    assert "fracasso" not in palavras


def test_padroes_exigem_repeticao(conn):
    channels.save_breakout(conn, "n", "termo unico irrepetivel", views=60_000,
                           canal="A", canal_subs=2_000, idade_dias=5)
    assert channels.padroes_de_titulo(conn, "n") == []


# ─── relatórios ──────────────────────────────────────────────────────────

def test_relatorios_dizem_como_coletar_quando_vazios(conn):
    assert "breakout-ingest" in channels.format_breakout_report(conn, "n")
    assert "channels-ingest" in channels.format_channels_report(conn, "n")


def test_relatorio_de_breakout_nao_quebra_com_campo_faltando(conn):
    channels.save_breakout(conn, "n", "só o título")
    channels.save_breakout(conn, "n", "sem canal", views=50_000, idade_dias=3)
    saida = channels.format_breakout_report(conn, "n")
    assert "sem canal" in saida
