import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import db  # noqa: E402


@pytest.fixture
def conn():
    """Banco SQLite em memória com o schema real, isolado por teste."""
    c = db.connect(":memory:")
    yield c
    c.close()


@pytest.fixture
def niche_cfg():
    """Config mínima de nicho, com os campos que brief/songbrief/opportunity leem."""
    return {
        "niche": "test_niche",
        "nome_exibicao": "Test Niche",
        "canal": "Test Channel",
        "idioma": "pt-BR",
        "pais": "BR",
        "songs_per_day": 3,
        "target_sec": 1200,
        "cooldown_faixa_dias": 21,
        "cooldown_tema_dias": 60,
        "cooldown_gancho_dias": 30,
        "duracao_media_faixa_sec": 270,
        "style_prompt": "estilo base de teste",
        "exclude_styles": "eletronico, trap",
        "formula_titulo": "{GANCHO} | {DURACAO} de Teste Para {BENEFICIO}",
        "formula_alt": [],
        "ganchos": ["GANCHO UM", "GANCHO DOIS", "GANCHO TRES"],
        "beneficios": ["Descansar", "Renovar"],
        "temas": ["Tema A", "Tema B", "Tema C"],
        "hashtags": ["#Teste"],
        "tags_youtube": ["teste"],
        "comentario_fixado": "Comente aqui.",
        "prompt_thumbnail": "thumb de teste",
        "palavras_protegidas": ["deus"],
        "papeis": ["retencao", "narrativa", "descanso"],
        "angulos": ["angulo 1", "angulo 2", "angulo 3"],
        "variacoes_estilo": ["variacao 1", "variacao 2"],
        "regras_extra": ["Regra de teste."],
    }
