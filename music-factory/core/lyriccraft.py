"""Ofício da letra — as regras de escrita que valem para todo canal de canção.

`regras_extra` do nicho diz o que é *daquele canal* ("nada de ambiente de culto
formal", "vocabulário de trabalho rural"). Faltava o outro lado: o que vale
para qualquer letra que vai virar áudio no Suno e disputar retenção no YouTube.

Estas regras vêm das skills de conteúdo do operador (gospel-blues-channel,
musica-ia) e do que o próprio portfólio mediu — a retenção morre na abertura
longa, e refrão que não cabe na boca do público não é cantado junto.

Ficam aqui, em um lugar só, porque repetir isso em seis configs garantiria
que os seis divergissem na primeira edição.
"""

REGRAS_CANCAO = [
    "**Gancho nos 3 primeiros segundos:** a primeira linha cantada já carrega a "
    "emoção da música — no máximo 8 palavras. Nada de abertura de cenário antes "
    "de alguém falar.",
    "**Refrão cantável:** no máximo 8 palavras por linha, repetível, e contém a "
    "frase-âncora do tema. Se o público não consegue cantar junto na segunda "
    "vez que ouve, está longo demais.",
    "**Call & response no refrão:** marque a resposta do coro com metatag "
    "`(backing vocals: ...)` ecoando a última frase — é o que dá o efeito de "
    "congregação sem precisar de outra gravação.",
    "**Acentuação emocional com moderação:** alongue a vogal tônica onde a "
    "emoção pede (`nãããoo`, `Loooord`), no máximo 2 por verso. Mais que isso o "
    "Suno arrasta a dicção e a letra fica ininteligível.",
    "**A ponte traz o tema de forma reconhecível** — é onde quem chegou no meio "
    "entende do que a música fala.",
    "**A última linha do refrão final é a frase que fica.** Escreva-a como se "
    "fosse a única que o ouvinte vai lembrar amanhã.",
]

REGRAS_INSTRUMENTAL = [
    "**Os primeiros 15 segundos definem a textura** e não mudam depois: quem "
    "põe para dormir não quer surpresa no minuto 4.",
    "**Arco dinâmico sem pico:** a faixa cresce e volta, nunca resolve num "
    "clímax — clímax acorda.",
    "**Sem melodia que exija atenção:** motivo simples, repetido, sem gancho "
    "que fixe na memória e puxe o ouvinte de volta à consciência.",
    "**Nunca prometa efeito médico** no título, na descrição ou na direção "
    "sonora.",
]


def regras(cfg):
    base = (REGRAS_INSTRUMENTAL if cfg.get("formato") == "instrumental"
            else REGRAS_CANCAO)
    return list(cfg.get("regras_letra") or base)


def bloco(cfg):
    """Trecho pronto para o prompt do dia."""
    titulo = ("### Ofício da faixa instrumental"
              if cfg.get("formato") == "instrumental" else "### Ofício da letra")
    return "\n".join([f"\n{titulo}"] + [f"- {r}" for r in regras(cfg)])
