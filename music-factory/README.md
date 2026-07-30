# Music Factory

**Foco: qualidade da música e oportunidade.** Renderização e upload de vídeo
ficam fora — são feitos manualmente.

Motor de produção diária para canais de música. Resolve o que faltava: **estado**.

O gargalo era visível no pacote anterior — a playlist de 1h trazia
`"Acrescente aqui uma música antiga sua com tema de força/renovação"` nas
posições 6 a 9, porque nada sabia o que já existia no acervo. Agora sabe.

Zero dependências externas: Python 3 puro (`sqlite3`, `json`, `argparse`).

---

## O que a Fase 1 entrega

| Recurso | O que faz |
|---|---|
| **Catálogo** | Toda faixa já criada, com tema, mood, duração, status e VPH |
| **Anti-repetição** | Bloqueia faixa reusada em <21d, tema em <60d, gancho de título em <30d |
| **Montador de playlist** | Sequência de 1h com regras + chapters com timestamps |
| **Pauta diária** | Pasta pronta por nicho: tema do dia, títulos, prompt de letras, metadados |
| **Rodar sozinho** | `systemd` timer diário às 06:00, um nicho quebrado não derruba os outros |
| **Qualidade** | Lê TODAS as letras do acervo e acusa imagens, rimas e títulos gastos |
| **Oportunidade** | Tema do dia escolhido por demanda real (cache semanal), não por rodízio |

### Regras do montador

1. **Posição 1 = faixa do acervo com maior VPH.** Nunca abrir com faixa nova — os primeiros 30s decidem a sessão.
2. **Novas em posições pares**, nunca abrindo nem fechando.
3. **Nenhuma faixa reutilizada em menos de 21 dias.**
4. **Fecho com 2 faixas `calm`** (sono/oração).
5. **Chapters automáticos** a partir das durações acumuladas.

Quando o acervo não dá conta, a playlist sai mais curta **com aviso explícito
do déficit** — nunca quebra e nunca finge que está completa.

---

## Uso

### Backfill do acervo existente (uma vez)

```bash
python3 cli.py import-acervo --niche country_blues_fe \
  --folder ../skills/media/master-music-intelligence/references/youtube_radar_agent/generated_songs/country_blues_ptbr_5_songs_new_prompt_2026-07-30
```

### Ciclo diário

```bash
# 1. pauta do dia (é o que o systemd chama)
python3 cli.py daily-brief --niche country_blues_fe

# 2. cole out/AAAA-MM-DD/<nicho>/01-PROMPT-PARA-CLAUDE-LETRAS.md no Claude
#    → recebe as 5 letras do tema escolhido

# 3. registre cada letra
python3 cli.py add-song --niche country_blues_fe \
  --title "Deus Ouviu Seu Choro" --mood calm --lyrics letras/01.txt

# 4. gere no Suno, baixe o áudio e registre a duração REAL
python3 cli.py set-audio --slug country_blues_fe-deus-ouviu-seu-choro \
  --file /audio/01.mp3 --duration 265

# 5. remonte a playlist com timestamps corretos
python3 cli.py build-playlist --niche country_blues_fe --save minha-playlist
```

### Inspeção

```bash
python3 cli.py status                      # visão geral por nicho
python3 cli.py catalog --niche country_blues_fe
```

---

## Saída da pauta diária

```
out/2026-07-31/country_blues_fe/
├── 00-RESUMO-DO-DIA.md              tema, playlist planejada, avisos, próximos passos
├── 01-PROMPT-PARA-CLAUDE-LETRAS.md  pronto para colar → gera as 5 letras
└── playlist/
    ├── titulo-variacoes.txt         3 variações para A/B (ganchos não repetidos)
    ├── descricao.txt                com tracklist e AI disclosure
    ├── tracklist-chapters.txt       timestamps para os chapters
    ├── hashtags.txt
    ├── tags-youtube.txt
    ├── comentario-fixado.txt
    └── prompt-thumbnail.txt
```

**Divisão de responsabilidade:** o Python cuida de estado e montagem (o que já
foi usado, o que entra hoje, em que ordem, com que timestamp). A escrita das
letras continua sendo do modelo — o job entrega o prompt pronto em vez de
fingir que gera letra boa em template.

---

## Instalação no VPS

```bash
sudo cp -r music-factory /opt/
sudo mkdir -p /var/music-factory
sudo cp systemd/music-factory-brief.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now music-factory-brief.timer
systemctl list-timers music-factory-brief.timer   # confirmar
```

Ajuste `User=` no `.service` e as variáveis `MUSIC_FACTORY_*` conforme o VPS.
Para usar cron em vez de systemd:

```cron
0 6 * * * /usr/bin/env bash /opt/music-factory/jobs/run_all_niches.sh
```

---

## Os 5 canais

| Canal | Idioma | País | Formato | Grupo |
|---|---|---|---|---|
| Country Blues e Fé | pt-BR | BR | canção | country_blues_gospel |
| Blues & Praises | en-US | US | canção | country_blues_gospel |
| Blues & Alabanzas | es-419 | MX | canção | country_blues_gospel |
| Southern Country Blues Gospel | en-US | US | canção | country_blues_gospel |
| Peaceful Deep Sleep Music | en-US | US | **instrumental** | — |

### Como os canais ficam diferentes entre si

Três mecanismos, porque só traduzir não resolve:

**1. Duas janelas de descanso de tema.** Dentro do canal, 60 dias (o mesmo
público voltaria a ver o mesmo assunto). Entre canais irmãos, 14 dias — basta
não saírem na mesma semana. Com janela única, 4 canais consumindo 1 tema/dia
esgotariam qualquer banco em dias.

**2. Bloco de cultura por canal.** Cada config declara o repertório de imagens
nativas e o que é **transposição proibida**. Os dois canais em inglês não
compartilham nenhuma imagem:

- *Blues & Praises* → revival tent, church pew, choir loft, river baptism
- *Southern* → Appalachian hollow, tobacco barn, coal town, grandmother's hymnbook

E cada um proíbe explicitamente o repertório do outro. O PT proíbe "front
porch"; o ES proíbe "sertão" e "front porch"; o Southern proíbe "church pew".

**3. Aviso de canal irmão no prompt.** Quando o tema pode ter saído noutro
idioma, o prompt manda mudar ângulo narrativo, cenário e personagem —
"mesma verdade, outra história" — em vez de traduzir.

A identidade sonora também separa: *Blues & Praises* é órgão Hammond de
igreja; *Southern* é dobro, pedal steel e fiddle de varanda, com
`Hammond organ church gospel` na lista de exclude.

### Canal instrumental

`peaceful_deep_sleep` usa `"formato": "instrumental"`. O prompt muda sozinho:
pede **direção sonora** (instrumentação, andamento, arco dinâmico) em vez de
letra, o banco de temas é sensorial em vez de bíblico, as faixas são longas
(15 min) e há regra explícita de **nunca prometer efeito médico**.

## Novo nicho

Copie `niches/country_blues_fe.json` e ajuste. Campos que importam:

- `ganchos` / `beneficios` — alimentam a fórmula de título (rotacionados por uso)
- `temas` — banco de temas do dia. **Mantenha ≥ 30 itens**: com poucos temas o
  rodízio esgota e o sistema passa a reaproveitar o mais antigo, avisando.
- `cooldown_*_dias` — janelas de descanso de faixa, tema e gancho
- `style_prompt` / `exclude_styles` — idênticos aos que já funcionam no Suno

O `daily-brief` roda para todo `.json` em `niches/`, sem alterar código.

---

## Testado

Todos os cenários abaixo foram executados, incluindo os de borda:

- catálogo vazio → erro com instrução, sem stack trace
- import do acervo real (5 músicas) → idempotente por slug
- acervo sem áudio → 4 avisos precisos, playlist ainda sai
- dia 2 → tema e gancho rotacionam, abertura pega a de maior VPH
- cooldown 21d → 0 elegíveis; 0d → 5 elegíveis
- banco de temas esgotado → rodízio justo do menos-recentemente-usado
- `mood` inválido → rejeitado com a lista de valores válidos
- `run_all_niches.sh` → ponta a ponta, exit 0, 9 arquivos entregues

---

## Qualidade — o que só é possível tendo o catálogo

Com 5 músicas/dia, a ameaça à qualidade não é a letra isolada sair ruim: é o
acervo inteiro convergir para as mesmas imagens e as mesmas rimas. Nas 5
primeiras letras do canal, **"cheiro" aparece em 5 de 5** e as terminações
`-nho` e `-rar` em 4 de 5.

```bash
python3 cli.py quality --niche country_blues_fe
```

Detecta:
- **Imagens saturadas** — por presença por música, não contagem bruta (uma
  palavra 20x numa letra é estilo; em 8 de 10 letras é vício)
- **Terminações de verso viciadas** — rimas que fecham todo verso igual
- **Colisão de títulos** — músicas que canibalizam a busca uma da outra

Três filtros evitam ruído: `palavras_protegidas` do nicho (num canal gospel,
repetir "Deus" é o assunto, não defeito), stopwords com verbos conjugados
("quis", "veio" são gramática, não cenário) e mínimo de 3 músicas para entrar
na lista (2 de 5 é coincidência). Abaixo de 8 letras o relatório se declara
indicativo em vez de diagnóstico.

**O resultado entra sozinho no prompt do dia**, como bloco de anti-repetição.

## Oportunidade — tema por demanda, não por rodízio

A conta VIDIQ tem teto de **150 créditos/semana** e cada consulta custa 5 —
cerca de 30 consultas semanais no total. Um job diário que consultasse a API
queimaria a cota em dois dias.

Por isso a coleta é **semanal e vai para cache**; a pauta diária lê só o cache
e **nunca gasta crédito**. Sem cache válido (>14 dias ou vazio), o sistema cai
no rodízio simples e **diz isso em voz alta** em vez de fingir que tem dado.

```bash
python3 cli.py opportunity --niche country_blues_fe        # ranking atual
python3 cli.py set-theme-score --niche country_blues_fe \
    --theme "Salmo 91 — proteção na estrada escura" --score 87
```

O tema do dia passa a ser **o de maior score que esteja fora do descanso** —
demanda e anti-repetição combinadas. O `00-RESUMO-DO-DIA.md` sempre declara
qual critério foi usado.

## Próximas fases

| Fase | Entrega |
|---|---|
| 3 | Coleta automática de oportunidade (VIDIQ semanal dentro da cota) |
| 4 | `learn.py` — ranking de fórmulas de título por VPH real dos canais |

Renderização de vídeo e upload **não estão no roadmap** — feitos manualmente.
