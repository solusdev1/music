# Music Factory — Fase 1

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

## Próximas fases

| Fase | Entrega |
|---|---|
| 2 | `render.py` — ffmpeg concatena áudios + loop de fundo → MP4 de 1h |
| 3 | `snapshot.py` (VIDIQ/yt-dlp) + `learn.py` — ranking de fórmulas por VPH real |
| 4 | Upload automático via YouTube Data API v3 (OAuth uma vez) |
