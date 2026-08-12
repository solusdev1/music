"""Montagem do style prompt do Suno — a ordem dos elementos decide o resultado.

O acervo tinha um problema silencioso: prompts que descreviam o gênero e a
instrumentação primeiro e a voz por último ("Country blues gospel BR, slide
guitar, órgão suave, barítono rouco") faziam o Suno devolver faixa quase
instrumental, com a voz recuada na mistura. Num canal de canção, isso é a
música inteira perdida.

`STYLE-PROMPTS-MELHORADOS.md` diagnosticou isso em 2026-07-31 e escreveu a
fórmula correta, mas ela nunca chegou aos configs. Este módulo é essa fórmula
em código, aplicada a todos os canais de uma vez:

    [VOZ] + [identidade do canal] + [instrumentação da faixa] + [âncoras]

A voz vem primeiro porque é o que o Suno pesa mais; os instrumentos chegam
como acompanhamento; e as âncoras ("vocals lead the mix") fecham fixando a
voz à frente. Canal instrumental não recebe nada disso — lá a ausência de voz
é a identidade, e uma âncora vocal destruiria a faixa.
"""

# Fecham o prompt fixando a voz à frente. Em inglês mesmo em canal PT/ES:
# style tag do Suno é sempre inglês, só a letra é no idioma do canal.
ANCORAS_VOCAL = (
    "clear lead vocal in front",
    "memorable sing-along chorus hook",
    "vocals lead the mix",
)

# Sem estes o Suno entrega faixa sem voz — o modo de falha que originou o módulo.
GUARDAS_EXCLUDE_CANCAO = (
    "instrumental only",
    "backing vocals only",
    "no lead vocals",
)

# Palavras que empurram o Suno para o instrumental quando o canal quer canção.
AMBIGUAS_CANCAO = ("ambient", "instrumental", "minimalist", "soundscape", "no vocals")


def _ja_contem(texto: str, trecho: str) -> bool:
    return trecho.lower() in texto.lower()


def _juntar(partes):
    """Concatena sem repetir o que já foi dito antes na mesma frase."""
    out = []
    for p in partes:
        p = (p or "").strip().strip(",")
        if p and not _ja_contem(", ".join(out), p):
            out.append(p)
    return ", ".join(out)


def is_instrumental(cfg) -> bool:
    return cfg.get("formato") == "instrumental"


def ancoras(cfg):
    return tuple(cfg.get("ancoras_vocal") or ANCORAS_VOCAL)


def build(cfg, variacao="", *, com_ancoras=True):
    """Style prompt de uma faixa, na ordem que o Suno respeita.

    `style_base` continua carregando só a identidade que nunca muda; a
    variação entra como instrumentação da faixa. A novidade é o campo `voz`
    do nicho, que passa à frente de tudo.
    """
    base = cfg.get("style_base") or cfg["style_prompt"]

    if is_instrumental(cfg):
        # Canal instrumental: nenhuma âncora vocal, nenhum campo `voz`.
        return _juntar([base, variacao])

    return _juntar(
        [cfg.get("voz", ""), base, variacao]
        + (list(ancoras(cfg)) if com_ancoras else [])
    )


def exclude(cfg):
    """Exclude do nicho + as guardas que impedem o Suno de tirar a voz.

    Só para canal de canção: no instrumental o exclude já pede o oposto
    ("vocals, choir, spoken words") e acrescentar guardas o contradiria.
    """
    atual = cfg["exclude_styles"]
    if is_instrumental(cfg):
        return atual
    faltando = [g for g in GUARDAS_EXCLUDE_CANCAO if not _ja_contem(atual, g)]
    return ", ".join([atual] + faltando) if faltando else atual


def diagnostico(cfg):
    """Avisos sobre o style prompt do nicho, para a pauta do dia mostrar.

    Diagnóstico em vez de correção automática: mexer no timbre de um canal
    que já entrega é decisão do operador, não do script.
    """
    avisos = []
    if is_instrumental(cfg):
        if not _ja_contem(cfg["exclude_styles"], "vocal"):
            avisos.append(
                "canal instrumental sem 'vocals' no exclude_styles — o Suno pode "
                "devolver faixa cantada")
        return avisos

    if not (cfg.get("voz") or "").strip():
        avisos.append(
            "nicho sem campo `voz`: o style prompt não declara quem canta e o "
            "Suno tende a devolver faixa instrumental "
            "(ver STYLE-PROMPTS-MELHORADOS.md)")

    base = cfg.get("style_base") or cfg["style_prompt"]
    ambiguas = [p for p in AMBIGUAS_CANCAO if _ja_contem(base, p)]
    if ambiguas:
        avisos.append(
            f"style_base de canal de canção contém termo ambíguo: "
            f"{', '.join(ambiguas)} — empurra o Suno para o instrumental")

    if not _ja_contem(cfg["exclude_styles"], "instrumental only"):
        avisos.append(
            "exclude_styles sem 'instrumental only' — a guarda é adicionada "
            "automaticamente na pauta, mas vale gravar no config")
    return avisos
