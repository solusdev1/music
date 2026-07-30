# Análise da v1 + Proposta v2 — Music Factory

**Data:** 2026-07-30
**Escopo:** canais de música (Gospel Blues PT/EN + demais nichos), operação diária em VPS

---

## Parte 1 — Diagnóstico da v1 (`hermes_master_music_intelligence.py`)

Tudo abaixo foi **testado contra o commit `4acfd97`** (versão atual do repo), não inferido.

### 1.0 Já corrigido pelo commit `4acfd97`

Três problemas graves da versão original foram resolvidos e não constam mais como pendência:

- ✅ **CLI real.** `argparse` implementado: `--db-path`, `--init`, `--add-trends-claude`, `--add-channels-hermes`, `--add-recommendations`, `--report`, `--guide`, `--export`, `--demo`.
- ✅ **Idempotência.** Rodando o pipeline 3× seguidas: `trend_analysis` fica em 14, `channel_analysis` em 90, `recommendations` em 4. Não duplica mais — pode ir para o cron sem inflar o banco.
- ✅ **Dados reais.** As 90 linhas de `channel_analysis` são snapshots de vídeos/canais reais do radar (Country Blues e Fé, Raízes da Fé Country, Outlaw Gospel Music), não números inventados.

### 1.1 Defeitos que permanecem

| # | Defeito | Evidência |
|---|---------|-----------|
| 1 | **`generate_report()` quebra com dado parcial.** Qualquer estilo sem `avg_engagement` derruba com `TypeError: unsupported format string passed to NoneType.__format__`. Dado incompleto é a norma em coleta real — isso mata um job de cron. | crash reproduzido na versão atual |
| 2 | **4 dos 8 gêneros documentados não têm guia.** Emo Rap, Amapiano, Hyperpunk e Synthwave caem num stub genérico sem BPM/elementos/monetização — silenciosamente, sem aviso. | `get_creation_guide()` por gênero |
| 3 | **`decision_history` nunca é escrita.** 0 linhas. A tabela que supostamente sustenta o "aprendizado" continua sendo código morto. | `COUNT(*) = 0` após pipeline completo |
| 4 | **O motor de conflito nunca dispara.** `conflicts` = 0 linhas no caminho do CLI. `detect_conflict()` só é exercitado pelo `--demo`, e compara com a string fixa `"country blues gospel"`. | `COUNT(*) = 0` |
| 5 | **"Auto-updates: YES" continua falso.** `skill_metadata` = 0 linhas: `auto_update()` não é chamado por nenhuma flag do CLI. A versão `1.1.0` no `SKILL.md` foi incrementada à mão, não pelo código. | `SELECT * FROM skill_metadata` → vazio |

### 1.2 O desalinhamento ficou explícito

O commit `4acfd97` alimentou a skill com **dados reais — todos de Country Blues / Gospel**. Ao mesmo tempo, o eixo declarado da skill (`SKILL.md`, `README.md`, tabela de recomendações) continua sendo os **8 gêneros genéricos** (Phonk, Hyperpop, Amapiano…), para os quais não existe um único dado coletado.

Ou seja: o repositório agora contém, lado a lado, o que funciona (radar real dos canais operados) e o que é decorativo (ranking de gêneros que ninguém mede). A pergunta certa não é "qual dos 8 gêneros tem maior score" — é "qual fórmula de título rende mais VPH nos meus canais".

### 1.2 O problema real (mais grave que os bugs)

A v1 é **um painel de tendências sobre gêneros que vocês não operam**, enquanto o negócio é **produção diária para os canais que vocês operam**.

Dois agravantes:

**(a) A camada de análise já existe — e muito melhor.** As skills `youtube-channel-analyst` v4 e `gospel-blues-channel` já entregam, com dados reais via VIDIQ: channel IDs reais, tabela de CPM por nicho, fórmula de título validada, benchmark de 6 concorrentes, score de viralidade, módulo de receita estimada e modo radar. A v1 duplica os 10% mais fracos disso com números fabricados.

**(b) A recomendação da v1 é ativamente ruim para vocês.** "Pivotar para Phonk/Hyperpop/Amapiano" descartaria um canal cuja keyword principal tem **220k buscas/mês com 83% do volume no Brasil** — vantagem de descoberta orgânica que levaria anos para reconstruir em outro nicho. E o canal EN tem CPM 3x maior ($12–15 vs $4–6). A alavanca não é trocar de nicho; é **volume e consistência dentro do nicho que já funciona** (os vencedores do nicho publicam 1,5–2 vídeos/dia).

### 1.3 Veredito

**Manter o que virou dado real; aposentar a camada de tendências genéricas.** Com a idempotência e o CLI resolvidos, o módulo já serve como *ingestor de radar* — esse pedaço vale a pena preservar e apontar para a v2.

**Aproveitar:** persistência SQLite, o CLI, o ingestor de snapshots do radar, e o conceito de conflito entre fontes (que vira "dado próprio vence dado de mercado").
**Descartar:** tabela dos 8 gêneros, ranking de oportunidade, contador de versão.
**Corrigir de imediato (barato):** o crash do `generate_report()` com `None` — é o único defeito que impede colocar no cron hoje.

### 1.4 Reproduzir os testes

```bash
cd skills/media/master-music-intelligence
DB=/tmp/t.db

# idempotência (3 runs, contagens estáveis)
for i in 1 2 3; do python3 hermes_master_music_intelligence.py --db-path $DB \
  --add-trends-claude --add-channels-hermes --add-recommendations >/dev/null; done
python3 -c "import sqlite3;c=sqlite3.connect('$DB');[print(t,c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]) for t in ['trend_analysis','channel_analysis','recommendations','decision_history','conflicts','skill_metadata']]"

# crash com dado parcial
python3 -c "
import sys;sys.path.insert(0,'.')
from hermes_master_music_intelligence import HermesmasterMusicIntelligence as H
h=H(db_path='/tmp/t2.db')
h.add_trend_analysis('X',{'growth_percentage':120,'saturation_level':'Low'})
h.generate_report()"
```

---

## Parte 2 — O que falta de verdade

O fluxo real de vocês é:

> 1 playlist/dia por nicho · ~5 músicas novas + faixas do acervo · monta a playlist · sobe

Nenhuma skill atual cobre a parte difícil disso, que é **estado**:

| Necessidade | Existe hoje? |
|---|---|
| Saber o que já foi criado (acervo pesquisável) | ❌ |
| Saber qual faixa entrou em qual playlist e quando | ❌ |
| Não repetir versículo / tema / gancho de título | ❌ |
| Montar playlist de 1h com regra (novas + acervo) | ⚠️ manual, sob demanda |
| Gerar tracklist + chapters com timestamps | ❌ |
| Rodar sozinho todo dia no VPS | ❌ |
| Aprender qual fórmula de título vence **com dados próprios** | ❌ |

Sem catálogo e sem anti-repetição, na faixa dos 300–400 vídeos vocês vão repetir Salmo 23 e o gancho "QUANDO TUDO PARECER ACABADO" a cada poucas semanas — canibalizando as próprias posições de busca.

---

## Parte 3 — Proposta v2: Music Factory

Motor de produção com estado, rodando como serviço no VPS.

### 3.1 Estrutura

```
music-factory/
├── core/
│   ├── db.py           # schema + migrations
│   ├── catalog.py      # acervo de faixas, status, busca
│   ├── playlist.py     # montagem 1h (novas + acervo) + chapters
│   ├── metrics.py      # ingestão VIDIQ / yt-dlp → snapshots
│   └── learn.py        # ranking de fórmulas por VPH real
├── niches/
│   ├── gospel_blues_pt.yaml     # canal, CPM, fórmula de título, cadência
│   ├── gospel_blues_en.yaml
│   └── vintage_soul.yaml
├── jobs/
│   ├── daily_brief.py  # 06:00 — pauta do dia por nicho
│   ├── render.py       # ffmpeg: concat áudio + loop → mp4 de 1h
│   └── snapshot.py     # 03:00 — métricas diárias
└── systemd/*.timer
```

### 3.2 Schema — a peça central

```sql
tracks(
  id, niche, channel_id, title, theme,        -- versículo/tema, usado no anti-repeat
  style_prompt, exclude_styles, lyrics_path,
  bpm, duration_sec, mood,                    -- open | retain | calm
  status,                                     -- draft|suno_ready|audio_ok|published
  audio_path, created_at, published_at, video_url
);
playlists(id, niche, channel_id, title, target_sec, status, published_at, video_url);
playlist_tracks(playlist_id, track_id, position, start_sec);   -- gera os chapters
usage(track_id, playlist_id, used_at);                          -- anti-repetição
title_experiments(video_url, formula, hook, duration_bucket, posted_hour, v7d, v30d);
channel_snapshots(channel_id, date, subs, views_total, videos);
```

`usage` + `theme` são o que impedem a canibalização. `title_experiments` é o que substitui o "auto-versionamento" por aprendizado de verdade.

### 3.3 Regras do montador de playlist

Derivadas dos padrões já validados na skill `gospel-blues-channel`:

- Alvo **60 min (±3)** — retenção long-form devocional 0.35–0.45 ⇒ ~24 min de watch time por view
- **Posição 1 = faixa do acervo com maior VPH** (segura os primeiros 30s, que decidem a sessão)
- **5 novas nas posições 2, 4, 6, 8, 10** — nunca abrindo nem fechando
- **Nenhuma faixa reutilizada em < 21 dias** (via `usage`)
- **Fecho com 2 faixas `calm`** (sono/oração — "Salmos para dormir" tem 57k buscas/mês no BR)
- **Chapters automáticos** a partir das durações acumuladas
- Título gerado pela fórmula validada `[EMOÇÃO] 🙏 | [formato] | [versículo]`, com 3 variações para A/B e checagem de gancho não usado nos últimos N dias

### 3.4 O que o job das 06:00 cospe

```
/var/music-factory/out/2026-07-31/gospel_blues_pt/
├── 00-RESUMO-DO-DIA.md              # tema, por que foi escolhido, o que fazer
├── musicas/0{1..5}/
│   ├── 01-style-prompt-suno.txt     # copy-paste direto
│   ├── 02-exclude-styles.txt
│   ├── 03-lyrics-suno.txt
│   └── 04-video-loop-prompt.txt
├── playlist/
│   ├── titulo-3-variacoes.txt
│   ├── descricao.txt                # com AI disclosure obrigatório
│   ├── hashtags.txt
│   └── tracklist-chapters.txt
└── render.sh                        # ffmpeg pronto p/ rodar quando os áudios chegarem
```

### 3.5 Automação no VPS — o que dá e o que não dá

| Etapa | Automatizável | Como |
|---|---|---|
| Métricas diárias por canal | ✅ 100% | `snapshot.py` 03:00 (VIDIQ/yt-dlp) |
| Escolha do tema do dia (sem repetir) | ✅ 100% | `daily_brief.py` consulta `usage`+`theme` |
| Letras + prompts Suno | ✅ 100% | templates por nicho |
| Título / descrição / hashtags / chapters | ✅ 100% | fórmula + `title_experiments` |
| **Render do vídeo de 1h** | ✅ 100% | **ffmpeg: concat de áudio + loop de fundo** |
| Geração do áudio no Suno | ⚠️ semi | sem API oficial → humano cola os `.txt`. Com conta/API, automatizável |
| **Upload no YouTube** | ✅ possível | **YouTube Data API v3, upload resumable — OAuth uma vez só** |

O render por ffmpeg e o upload por API são o verdadeiro payoff do "deixar rodando direto no VPS": o dia inteiro fica automático exceto colar 5 prompts no Suno e baixar os áudios.

**Dependências a instalar no VPS** (ausentes neste ambiente): `ffmpeg`, `yt-dlp`. Credenciais: OAuth do YouTube Data API v3 (nenhuma chave de API está exposta no ambiente hoje).

### 3.6 O loop de aprendizado que substitui o contador de versão

A cada publicação, grava em `title_experiments`: fórmula usada, gancho, faixa de duração, horário. Aos 7 e 30 dias, `snapshot.py` preenche `v7d`/`v30d`. Mensalmente, `learn.py` ranqueia as fórmulas por **VPH mediano nos dados de vocês**.

É isso que responde "qual título funciona" — não benchmark de terceiros, não número inventado. É também a versão honesta da "resolução de conflito" da v1: **dado próprio vence dado de mercado quando os dois discordam.**

---

## Parte 4 — Roadmap

| Fase | Entrega | Destrava |
|---|---|---|
| **1** | Catálogo + anti-repetição + montador de playlist + `daily_brief.py` | "1 playlist/dia por nicho" com 5 novas + acervo |
| **2** | `render.py` (ffmpeg) + chapters | vídeo de 1h montado sozinho |
| **3** | `snapshot.py` (VIDIQ/yt-dlp) + `learn.py` | fórmulas ranqueadas por dado próprio |
| **4** | Upload automático (YouTube API) + systemd timers | pipeline diário sem intervenção |

Migração da v1: importar o acervo existente para `tracks` (backfill via yt-dlp nos canais atuais), aposentar `hermes_master_music_intelligence.py`.

---

## Resumo

O commit `4acfd97` resolveu os três problemas mais graves (CLI, idempotência, dados reais) — a v1 já é utilizável como ingestor de radar. Sobram 5 defeitos, sendo um bloqueante para cron (crash com dado parcial).

Mas o problema central nunca foram os bugs: a skill declara como eixo 8 gêneros que vocês não operam e ninguém mediu, enquanto os dados reais que entraram são todos dos canais de Country Blues / Gospel que vocês de fato rodam.

O que falta é **estado**: catálogo, anti-repetição, montagem de playlist e cadência automática. É isso que a v2 entrega — e é o que transforma o VPS de máquina parada em linha de produção.
