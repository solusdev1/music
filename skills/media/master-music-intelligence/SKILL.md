---
name: master-music-intelligence
description: "Radar operacional de música no YouTube: busca de canais, detecção do que está COMEÇANDO a viralizar (multiplicador views÷inscritos, não views absolutas) e ingestão no music-factory. Inclui também material histórico com dados sintéticos, explicitamente marcado."
version: 2.0.0
author: Claude Code Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [youtube, music, trends, analytics, suno, production, intelligence, radar, breakout]
    related_skills: [youtube-music-production, country-blues-fe-channel-analysis, dark-music-youtube-niche-strategy]
    integration: consolidated
---

# Master Music Intelligence (v2.0)

Radar de oportunidade para os canais de música do projeto. A v2 troca o radar
antigo — que ranqueava por views absolutas e por uma tabela de gêneros
inventada — por um que responde à pergunta certa:

> **O que está começando a viralizar num canal do meu tamanho, que eu consiga
> replicar esta semana?**

---

## O princípio: multiplicador, não views

Ordenar por views coloca no topo o vídeo de 4M de views de um canal de 3M de
inscritos. Isso é uma gravadora com catálogo, verba e marca — não é replicável.

O sinal que importa é o **multiplicador**: views ÷ inscritos. Um canal de 2.100
inscritos com 62k views em 5 dias fez 29x o próprio tamanho. **Esse** formato é
copiável, e é ele que o radar coloca em primeiro.

O score (0–100) combina três eixos, com peso de recência e de porte do canal:

| Eixo | Peso | Por quê |
|------|-----:|---------|
| Multiplicador (views ÷ inscritos) | 45 | o eixo que decide replicabilidade |
| Velocidade (views/dia) | 35 | separa "pegando agora" de "acumulou devagar" |
| Volume absoluto | 20 | evita premiar 3k views num canal de 300 |

Multiplicadores: **recência** cheia até 14 dias, zerando aos 90 (passou disso,
o formato não está "começando"); **porte** de 1.0 para canal pequeno a 0.15
para canal gigante.

Efeito prático, com números reais do pipeline:

```
  score   mult      views  título / canal
     89  29.5x     62.000  Deus Viu Suas Lágrimas | 1 Hora de Country Gospel
                           ↳ Estrada de Fé · 12.400 views/dia · 5d · pequeno
     75  20.7x    310.000  Quando Você Não Aguenta Mais — Louvores Country
                           ↳ Voz do Sertão Gospel · 28.182 views/dia · 11d · medio
      7   1.4x  4.200.000  As Melhores Canções Gospel 2026
                           ↳ Gravadora Som Maior · 123.529 views/dia · 34d · gigante
```

A gravadora tem 68x mais views e fica em último — corretamente.

---

## Rodar o radar

### 1. Coleta ampla (grátis, diária)

```bash
python3 youtube_music_ops/scripts/run_daily_opportunity_radar.py
```

Varre as queries de `config/daily_opportunity_radar_queries.json` e grava em
`radar/daily_opportunity/<data>/`:

| Arquivo | Conteúdo |
|---------|----------|
| `daily_opportunity_summary.md` | relatório, com seções "Começando a viralizar" e "Canais do nicho" |
| `channels_by_niche.json` | canais agregados: em quantas queries recorrem, mediana de views |
| `breakouts.json` | candidatos, já no formato que o music-factory ingere |
| `daily_opportunity_rows.csv` | todas as linhas |

Esta fonte **não expõe inscritos**. O multiplicador aqui usa como base a mediana
do próprio canal na amostra, e só quando há 3+ vídeos dele — com menos, o campo
fica nulo em vez de inventar número.

### 2. Ingestão e repontuação

```bash
python3 music-factory/cli.py breakout-ingest \
  --niche country_blues_fe \
  --file youtube_music_ops/radar/daily_opportunity/<data>/breakouts.json
```

### 3. Enriquecer com inscritos (VIDIQ, semanal)

Sem inscritos o score fica limitado (peso de porte 0.5, multiplicador nulo).
Para fechar a conta, o agente consulta o MCP VIDIQ, salva o JSON e ingere:

| Objetivo | Ferramenta MCP | Ingerir com |
|----------|----------------|-------------|
| Vídeos em alta no nicho | `vidiq_outliers`, `vidiq_trending_videos` | `breakout-ingest` |
| Canais do nicho | `vidiq_channel_search` | `channels-ingest` |
| Vizinhança de um canal | `vidiq_similar_channels` | `channels-ingest` |
| Keywords / espaço aberto | `vidiq_keyword_research` | `vidiq-ingest --tipo keywords` |

```bash
python3 music-factory/cli.py channels-ingest --niche country_blues_fe --file canais.json
```

> **Orçamento VIDIQ**: 150 créditos/semana, 5 por consulta — ~30 consultas.
> Por isso a coleta VIDIQ é **semanal**; a diária é a do passo 1, que é grátis.

### 4. Ler

```bash
python3 music-factory/cli.py radar    --niche country_blues_fe   # tudo
python3 music-factory/cli.py breakout --niche country_blues_fe   # só o que está pegando
python3 music-factory/cli.py channels --niche country_blues_fe   # só os canais
```

`radar` mostra, nesta ordem: saúde do banco de temas → o que está começando a
viralizar → canais replicáveis → ideias pendentes de aprovação.

---

## Busca de canais

Canal agora é entidade de primeira classe, não um campo de texto no vídeo.

- **Identidade reconciliada.** O mesmo canal chega como nome solto (via
  breakout) e como `channelId` (via busca de canais). Sem reconciliar, cada
  fonte criava uma linha e o mapa virava lista de duplicatas. A busca é por ID,
  depois handle, depois nome normalizado (sem acento/pontuação).
- **Recorrência é sinal.** `vezes_visto` conta em quantas coletas o canal
  reapareceu. Recorrer em várias queries indica canal estrutural do nicho, não
  acaso do ranking daquele dia.
- **Porte decide a leitura.** `semente` (<1k) · `pequeno` (<10k) ·
  `medio` (<100k) · `grande` (<1M) · `gigante` (≥1M). Até 100k inscritos o
  formato é considerado replicável e o canal entra na lista de modelos.

---

## Embalagem a copiar

Detectar o vídeo não basta — é preciso saber **o que** copiar. O relatório de
breakout extrai as palavras recorrentes entre os títulos que passaram do corte,
descartando o vocabulário genérico do nicho (deus, louvores, música, playlist,
hora…) que aparece em qualquer título e não ensina nada.

Só entram títulos que efetivamente estouraram: copiar o vocabulário de vídeo que
não performou seria copiar ruído.

---

## Aprovação continua sendo humana

O radar **não** cria tema sozinho. Ideias descobertas entram como pendentes:

```bash
python3 music-factory/cli.py radar-add     --niche <n> --ideia "..."
python3 music-factory/cli.py radar-approve --niche <n> --ideia "..."
```

Depois de aprovada, copie para o campo `temas` do config do nicho.

---

## ⚠️ Material histórico com dados sintéticos

`hermes_master_music_intelligence.py` e os documentos abaixo são de **2024** e
contêm uma tabela de 8 gêneros (Phonk 234%, Hyperpop 245%…) que é **dado
sintético de exemplo — inventado, não medido**. Não use como base de decisão.

O caso mais claro: aqueles documentos classificam "Country Blues Gospel" como
saturado e recomendam evitá-lo, enquanto **Country Blues e Fé é o canal de
melhor desempenho medido do projeto** e nenhum canal Sertanejo Trap Gospel
jamais foi lançado.

| Documento | Status |
|-----------|--------|
| `hermes_master_music_intelligence.py` | tabela `CLAUDE_TRENDS` sintética; `auto_update()` é código morto |
| `SUMARIO_EXECUTIVO.md` | artefato histórico (2024) |
| `ANALISE_ABRANGENTE_ESTILOS_MUSICAIS.md` | artefato histórico (2024) |
| `COMPARATIVO_E_CONSOLIDACAO.md` | artefato histórico (2024) |
| `HERMES_MASTER_SKILL_INTEGRATED.md` | artefato histórico (2024) |

Para desempenho real dos canais: `music-factory/data/*.db` e
`ANALISE-2026-07-30.md`.

Dados **reais** preservados: `references/youtube_radar_agent/` (radar Country
Blues e Fé, relatórios de 2026-07-17/22/30, pacotes Suno) e
`data/music_intelligence_seed.db`.

---

## Onde está o código

| Arquivo | Papel |
|---------|-------|
| `music-factory/core/channels.py` | busca de canais + score de breakout |
| `music-factory/core/opportunity.py` | radar, ideias, ranking de temas |
| `music-factory/core/vidiq.py` | ingestão de keywords e outliers |
| `youtube_music_ops/scripts/run_daily_opportunity_radar.py` | coleta ampla diária |
| `music-factory/tests/test_channels.py` | 24 testes do score e da identidade de canal |
