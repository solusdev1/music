# 🎯 Análise de Tendências: Nichos de Música Gospel no YouTube

Este diretório contém análises consolidadas sobre tendências emergentes de estilos musicais no YouTube, com foco em oportunidades para novos criadores de conteúdo.

## 📋 Documentos

### [SUMARIO_EXECUTIVO.md](./SUMARIO_EXECUTIVO.md)
Resumo visual e consolidado com:
- Ranking das 3 melhores oportunidades
- Tabela comparativa de todos os 6 nichos analisados
- Matriz de oportunidade estratégica
- Recomendações finais de ação
- **Conclusão**: SERTANEJO TRAP GOSPEL é o maior potencial

### Dados migrados do Hermes Radar

Este diretório agora também contém:

- `data/music_intelligence_seed.db` — banco SQLite alimentado com 14 tendências, 90 registros de radar e recomendações.
- `data/music_intelligence_seed.json` — export JSON do mesmo seed.
- `references/youtube_radar_agent/` — agente Radar Gospel Blues Viral completo, com scripts, configs, CSVs, JSONLs, relatórios e pacotes Suno já gerados.

## 🎵 Nichos Analisados

### Emergentes (Alta Oportunidade)
1. **Trap Gospel** - 180% crescimento, 4.26% engajamento
2. **Sertanejo Trap Gospel** - 162% crescimento, 52 novos canais
3. **Funk Gospel** - 145% crescimento, 4.15% engajamento
4. **Afrobeat Gospel** - 138% crescimento, potencial global

### Tradicionais (Saturação Alta)
5. **Pagode Gospel** - 72% crescimento, saturação média-alta
6. **Country Blues Gospel** - 45% crescimento, saturação alta

## 📊 Metodologia

- **Periodo**: Maio-Julho 2024 (últimos 3 meses)
- **Total de Vídeos Analisados**: 54 (9 por nicho)
- **Total de Views**: 19,617,000 visualizações
- **Métricas**: Crescimento, novos canais, saturação, engajamento, monetização

## 🎯 Recomendação Principal

**🏆 SERTANEJO TRAP GOSPEL** é a melhor oportunidade por:
- **52 novos canais** (tendência mais forte detectada)
- **162% crescimento** (velocidade adequada, não saturado)
- **Público bem definido** (25-40 anos, interior/zona rural)
- **Monetização diversificada** (AdSense, shows, streamings, parcerias)
- **Window aberta**: 12-18 meses antes de saturação completa

## 🚀 Rodar com o seed atual

```bash
python hermes_master_music_intelligence.py \
  --db-path data/music_intelligence_seed.db \
  --add-trends-claude \
  --add-channels-hermes \
  --add-recommendations \
  --report \
  --export data/music_intelligence_seed.json
```

O seed inclui o histórico Country Blues e Fé, relatórios de 2026-07-17/22/30 e o pacote de 5 músicas Country Blues Gospel em PT-BR de 2026-07-30.

## ⏰ Urgência

Estes nichos emergentes podem saturar em 12-18 meses.  
**Recomendação de ação: Próximas 4 semanas**

---

**Análise realizada**: Julho 2024  
**Próxima revisão recomendada**: Outubro 2024
