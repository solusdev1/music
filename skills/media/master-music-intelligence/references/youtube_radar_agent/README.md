# Radar Gospel Blues Viral

Agente local para mapear vídeos/canais no YouTube em estilos dark country/gospel/blues, calcular score de oportunidade e gerar relatório com ideias originais para produção musical.

## Rodar agora

Use este comando na pasta do agente:

```bash
uv run --with yt-dlp python scripts/radar_gospel_blues_viral.py --max-results 5
```

## Saídas

- data_raw/videos_raw_YYYY-MM-DD.jsonl
- data_processed/videos_ranked_YYYY-MM-DD.csv
- reports/trend_report_YYYY-MM-DD.md
- generated_songs/production_ideas_YYYY-MM-DD.md

## Configuração

Edite:
- config/search_queries.txt para mudar buscas
- config/seed_channels.csv para adicionar canais conhecidos

## Interpretação do score

- 80-100: tendência forte
- 60-79: tendência promissora
- 40-59: observar
- abaixo de 40: referência fraca

## Cuidados de monetização

Não copie letras, melodias, thumbnails, vozes ou identidade de outros canais. O agente usa tendências como referência para criar conteúdo original.
