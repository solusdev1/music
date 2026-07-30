# Como usar o agente Radar Gospel Blues Viral

Pasta do agente:
C:\Users\suporteti\Music\youtube_radar_agent

## Teste rápido

No terminal Git Bash:

```bash
cd /c/Users/suporteti/Music/youtube_radar_agent
bash run_radar.sh 2 3
```

Isso busca 2 resultados por query nas 3 primeiras queries.

## Rodada completa

```bash
cd /c/Users/suporteti/Music/youtube_radar_agent
bash run_radar.sh 5
```

Isso busca 5 resultados para todas as queries de config/search_queries.txt.

## Onde ver os resultados

Relatório de tendências:
reports/trend_report_YYYY-MM-DD.md

Ranking CSV:
data_processed/videos_ranked_YYYY-MM-DD.csv

Ideias e pacotes de produção:
generated_songs/production_ideas_YYYY-MM-DD.md

Dados brutos:
data_raw/videos_raw_YYYY-MM-DD.jsonl

## Analisar URLs escolhidas por você

Cole links de vídeos do YouTube, um por linha, neste arquivo:

inputs/input_urls.txt

Depois rode:

```bash
cd /c/Users/suporteti/Music/youtube_radar_agent
bash run_radar.sh 3 0
```

O agente vai analisar as URLs do arquivo e também fazer as buscas normais.

Para analisar somente suas URLs, sem busca automática:

```bash
cd /c/Users/suporteti/Music/youtube_radar_agent
bash run_radar.sh 1 0 --skip-search
```

## Usar conteúdo do NotebookLM

O NotebookLM normalmente não oferece uma API simples para “pegar tudo” automaticamente. Então o fluxo prático é:

1. Abra seu NotebookLM.
2. Copie a lista de fontes, briefing, notas ou resumo onde estão os canais/vídeos.
3. Cole tudo neste arquivo:

inputs/notebooklm_export.md

4. Rode:

```bash
cd /c/Users/suporteti/Music/youtube_radar_agent
bash run_radar.sh 3 0
```

O agente extrai automaticamente links youtube.com e youtu.be que estiverem no texto do NotebookLM.

## Ajustar buscas

Edite:
config/search_queries.txt

Adicione termos como:
- oração de madrugada country gospel
- louvor country para dormir
- dark gospel blues português
- gospel blues estrada de fé

## Observação sobre aviso do yt-dlp

Se aparecer aviso sobre JavaScript runtime, mas o agente concluir e gerar relatório, pode ignorar no MVP.
Se no futuro o YouTube bloquear extrações, instale/configure um runtime JS para yt-dlp ou migre para YouTube Data API v3.

## Próxima evolução recomendada

1. Adicionar YouTube Data API v3 para dados mais consistentes.
2. Adicionar análise automática de thumbnails com visão.
3. Adicionar transcrição quando disponível.
4. Criar cron semanal no Hermes.
5. Conectar com o agente de música para gerar 7 músicas completas por tendência.
